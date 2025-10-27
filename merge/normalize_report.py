#!/usr/bin/env python3
import re, sys

if len(sys.argv) != 2:
    print("Usage: normalize_report.py <path-to-md>")
    sys.exit(2)

path = sys.argv[1]
text = open(path, encoding="utf-8").read()

# ---------- utils (slug + parsing) ----------
HEADING_RE = re.compile(r'^(#{1,6})\s+(.+?)\s*$', re.UNICODE)
LIST_RE    = re.compile(r'^\s*-\s+\*\*')  # bullet that starts a maturity item

def slugify(s: str) -> str:
    s = s.strip()
    # drop leading "A. ", "B. ", etc and surrounding ** if any
    s = re.sub(r'^[A-Z]\.\s*', '', s)
    s = s.replace('**','')
    s = s.lower()
    s = re.sub(r'`.+?`', '', s)
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def parse_sections(md: str):
    lines = md.splitlines()
    heads = []
    for i, ln in enumerate(lines):
        m = HEADING_RE.match(ln)
        if m:
            level = len(m.group(1))
            title = m.group(2).strip()
            heads.append((level, title, slugify(title), i))
    sections = []
    for j, (lvl, title, slug, start) in enumerate(heads):
        end = len(lines) if j+1 == len(heads) else heads[j+1][3]
        sections.append({
            "level": lvl, "title": title, "slug": slug,
            "start": start, "end": end
        })
    return lines, sections

def get_body_by_slug(md: str, want_slug: str):
    lines, sections = parse_sections(md)
    for s in sections:
        if s["slug"] == want_slug:
            return lines[s["start"]+1:s["end"]]
    return None

def replace_body_by_slug(md: str, want_slug: str, new_body_lines):
    lines, sections = parse_sections(md)
    for s in sections:
        if s["slug"] == want_slug:
            start, end = s["start"], s["end"]
            return "\n".join(lines[:start+1] + new_body_lines + lines[end:])
    return md

# ---------- 1) Collapse blank line between Findings and Resolution ----------
def collapse_findings_resolution(md: str) -> str:
    L = md.splitlines()
    out = []
    i = 0
    while i < len(L):
        out.append(L[i])
        if re.match(r'^\s*\*Findings:\*', L[i]):
            if i + 2 < len(L) and L[i+1].strip() == "" and re.match(r'^\s*\*Resolution:\*', L[i+2]):
                i += 1  # skip the blank line
        i += 1
    return "\n".join(out)

text = collapse_findings_resolution(text)

# ---------- 2) Ensure maturity subsections have bullets ----------
def bullet(name: str):
    return [
        f"- **{name} (Score: ) (Priority level: ) (Personas: )**  ",
        "  *Findings:* ...  ",
        "  *Resolution:* ...",
        ""
    ]

NEEDED = {
    "enterprise platform viability": [
        "Production-Ready Environment",
        "Roles and Responsibilities (RACI)",
        "Leadership Commitment",
        "Security Integration",
        "Engagement and Communication",
        "Workload Understanding (App Workloads)",
    ],
    "platform success": [
        "DevOps Skills",
        "Automated Deployments (Automation)",
        "Release Engineering (Change Management)",
        "Site Reliability Engineering (Reliability)",
        "User Access (Access)",
    ],
    "platform upkeep": [
        "Upgrades",
        "Operational Excellence (Day-2 Ops)",
        "Monitoring (Logging, Metrics, Alerts)",
        "Capacity Planning and Management",
        "Business Continuity and Disaster Recovery (BCDR)",
    ],
    "platform support": [
        "Proactive Support",
        "Compliance Coverage",
        "Escalation Processes",
        "Third-Party Services Integration",
    ],
}

for slug, items in NEEDED.items():
    body = get_body_by_slug(text, slug)
    if body is None:
        # Section missing entirely: skip (validator will fail for a different reason)
        continue
    has_bullets = any(LIST_RE.match(ln) for ln in body)
    if not has_bullets:
        new_body = []
        for n in items:
            new_body += bullet(n)
        text = replace_body_by_slug(text, slug, new_body)

# ---------- 3) Ensure Final Maturity Score table is filled ----------
def fill_maturity_table(md: str) -> str:
    pat = re.compile(
        r'(\|\s*Rubric\s*\|\s*Current %\s*\|\s*Target %\s*\|\s*\n'
        r'\|[-\s|]+\|\s*\n'
        r'(?P<body>(?:\|\s*.*\s*\|\s*.*\s*\|\s*.*\s*\|\s*\n)+))',
        re.IGNORECASE
    )
    def fmt_pct(p):
        p = p.replace('%','').strip()
        try:
            v = float(p)
        except:
            return "0.00 %"
        return f"{v:.2f} %"
    def repl(m):
        body = m.group('body')
        out = []
        for row in body.splitlines(True):
            if not row.strip().startswith("|") or set(row.strip()) <= set("|-"):
                out.append(row); continue
            cols = [c.strip() for c in row.strip().split("|")]
            if len(cols) < 5:
                out.append(row); continue
            rubric, curr, targ = cols[1], cols[2], cols[3]
            key = rubric.lower()
            if key in ("viability","success","upkeep","support","overall"):
                curr = fmt_pct(curr) if curr else "0.00 %"
                targ = fmt_pct(targ) if targ else "0.00 %"
                row = f"| {rubric} | {curr} | {targ} |\n"
            out.append(row)
        return m.group(1).replace(body, "".join(out))
    return pat.sub(repl, md)

text = fill_maturity_table(text)

# ---------- 4) Ensure Technical Focus table cells are filled ----------
def fill_tech_table(md: str) -> str:
    L = md.splitlines()
    out = []
    in_table = False
    for ln in L:
        if ln.strip().startswith("| Area") and "Score (0–2)" in ln:
            in_table = True
            out.append(ln); continue
        if in_table and re.match(r'^\|\s*-+\s*\|', ln):
            out.append(ln); continue
        if in_table:
            if not ln.strip().startswith("|"):
                in_table = False
                out.append(ln); continue
            parts = [p.strip() for p in ln.strip().split("|")]
            if len(parts) >= 4:
                area = parts[1] or ""
                score = parts[2] or "0"
                just  = parts[3] or "TBD"
                try:
                    s = int(float(score))
                    if s not in (0,1,2): s = 0
                    score = str(s)
                except:
                    score = "0"
                ln = f"| {area} | {score} | {just} |"
        out.append(ln)
    return "\n".join(out)

text = fill_tech_table(text)

# ---------- write back ----------
with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("normalize_report.py: normalization completed (slug-aware).")
