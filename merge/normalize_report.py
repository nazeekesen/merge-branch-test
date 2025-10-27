#!/usr/bin/env python3
import re, sys

if len(sys.argv) != 2:
    print("Usage: normalize_report.py <path-to-md>")
    sys.exit(2)

path = sys.argv[1]
text = open(path, encoding="utf-8").read()

# ---------------- 1) Collapse blank line between Findings and Resolution ----------------
lines = text.splitlines()
out = []
i = 0
while i < len(lines):
    out.append(lines[i])
    if re.match(r'^\s*\*Findings:\*', lines[i]):
        # drop a single blank line if immediately followed by Resolution
        if i + 2 < len(lines) and lines[i+1].strip() == "" and re.match(r'^\s*\*Resolution:\*', lines[i+2]):
            i += 1
    i += 1
text = "\n".join(out)

# ---------------- helpers to find/replace section bodies by exact heading ----------------
HEADING_RE = re.compile(r'^(#{1,6})\s+(.+?)\s*$', re.UNICODE)

def find_sections(md):
    L = md.splitlines()
    heads = []
    for idx, ln in enumerate(L):
        m = HEADING_RE.match(ln)
        if m:
            level = len(m.group(1))
            title = m.group(2).strip()
            heads.append((level, title, idx))
    ranges = []
    for j, (lvl, title, start) in enumerate(heads):
        end = len(L) if j+1 == len(heads) else heads[j+1][2]
        ranges.append((lvl, title, start, end))
    return L, ranges

def get_section_body(md, exact_title):
    L, ranges = find_sections(md)
    for lvl, title, start, end in ranges:
        if title == exact_title:
            return L[start+1:end]
    return None

def replace_section_body(md, exact_title, new_body_lines):
    L, ranges = find_sections(md)
    for lvl, title, start, end in ranges:
        if title == exact_title:
            return "\n".join(L[:start+1] + new_body_lines + L[end:])
    return md

# ---------------- 2) Ensure maturity subsections have bullets ----------------
def bullet(name):
    return [
        f"- **{name} (Score: ) (Priority level: ) (Personas: )**  ",
        "  *Findings:* ...  ",
        "  *Resolution:* ...",
        ""  # blank line between items is OK
    ]

SECTIONS_TO_ENSURE = {
    "#### **Enterprise Platform Viability**": [
        "Production-Ready Environment",
        "Roles and Responsibilities (RACI)",
        "Leadership Commitment",
        "Security Integration",
        "Engagement and Communication",
        "Workload Understanding (App Workloads)",
    ],
    "### B. Platform Success": [
        "DevOps Skills",
        "Automated Deployments (Automation)",
        "Release Engineering (Change Management)",
        "Site Reliability Engineering (Reliability)",
        "User Access (Access)",
    ],
    "### C. Platform Upkeep": [
        "Upgrades",
        "Operational Excellence (Day-2 Ops)",
        "Monitoring (Logging, Metrics, Alerts)",
        "Capacity Planning and Management",
        "Business Continuity and Disaster Recovery (BCDR)",
    ],
    "### D. Platform Support": [
        "Proactive Support",
        "Compliance Coverage",
        "Escalation Processes",
        "Third-Party Services Integration",
    ],
}

# Inject bullets if there are no list items under the section
for heading, items in SECTIONS_TO_ENSURE.items():
    body = get_section_body(text, heading)
    if body is None:
        continue  # heading not found (should not happen if template is fixed)
    has_bullets = any(re.match(r'^\s*-\s*\*\*', ln) for ln in body)
    if not has_bullets:
        new_body = []
        for n in items:
            new_body += bullet(n)
        text = replace_section_body(text, heading, new_body)

# ---------------- 3) Ensure Final Maturity Score table is filled ----------------
def fill_maturity_table(md: str) -> str:
    pat = re.compile(
        r'(\|\s*Rubric\s*\|\s*Current %\s*\|\s*Target %\s*\|\s*\n'
        r'\|[-\s|]+\|\s*\n'
        r'(?P<body>(?:\|\s*.*\s*\|\s*.*\s*\|\s*.*\s*\|\s*\n)+))',
        re.IGNORECASE
    )
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
            def fmt(p):
                p = p.replace("%","").strip()
                try:
                    v = float(p)
                except:
                    return "0.00 %"
                return f"{v:.2f} %"
            if rubric.lower() in ("viability","success","upkeep","support","overall"):
                curr = fmt(curr) if curr else "0.00 %"
                targ = fmt(targ) if targ else "0.00 %"
                row = f"| {rubric} | {curr} | {targ} |\n"
            out.append(row)
        return m.group(1).replace(body, "".join(out))
    return pat.sub(repl, md)

text = fill_maturity_table(text)

# ---------------- 4) Ensure Technical Focus table values are filled ----------------
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

# ---------------- write back ----------------
with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("normalize_report.py: normalization completed.")
