#!/usr/bin/env python3
import re, sys

path = sys.argv[1]
text = open(path, encoding="utf-8").read()

# ---------- 1) Collapse blank line between Findings and Resolution ----------
lines = text.splitlines()
out = []
i = 0
while i < len(lines):
    out.append(lines[i])
    if re.match(r'^\s*\*Findings:\*', lines[i]):
        if i + 2 < len(lines) and lines[i+1].strip() == "" and re.match(r'^\s*\*Resolution:\*', lines[i+2]):
            i += 1  # skip single blank line
    i += 1
text = "\n".join(out)

# ---------- helpers to find/replace section bodies by heading ----------
HEADING_RE = re.compile(r'^(#{1,6})\s+(.+?)\s*$')
def find_section_ranges(md: str):
    """Return list of (level, title, start_line, end_line_exclusive)."""
    lines = md.splitlines()
    heads = []
    for idx, ln in enumerate(lines):
        m = HEADING_RE.match(ln)
        if m:
            level = len(m.group(1))
            title = m.group(2).strip()
            heads.append((level, title, idx))
    ranges = []
    for j, (lvl, title, start) in enumerate(heads):
        end = len(lines)
        if j + 1 < len(heads):
            end = heads[j+1][2]
        ranges.append((lvl, title, start, end))
    return ranges

def replace_section_body(md: str, heading_title_exact: str, new_body_lines):
    lines = md.splitlines()
    ranges = find_section_ranges(md)
    for lvl, title, start, end in ranges:
        if title == heading_title_exact:
            # keep the heading line, replace everything until next heading
            return "\n".join(lines[:start+1] + new_body_lines + lines[end:])
    return md  # heading not found; unchanged

# ---------- 2) Ensure maturity subsections have bullets ----------
# Each item will create one list line + two paragraph lines (Findings/Resolution).
def bullet(name: str):
    return [
        f"- **{name} (Score: ) (Priority level: ) (Personas: )**  ",
        "  *Findings:* ...  ",
        "  *Resolution:* ...",
        ""  # blank line between items is fine
    ]

SECTION_ITEMS = {
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

def body_is_empty(md: str, heading_title_exact: str) -> bool:
    lines = md.splitlines()
    ranges = find_section_ranges(md)
    for lvl, title, start, end in ranges:
        if title == heading_title_exact:
            body = [ln for ln in lines[start+1:end] if ln.strip() != ""]
            # Empty if no nonblank lines (or only comments/whitespace)
            return len(body) == 0
    return False

for heading, items in SECTION_ITEMS.items():
    if body_is_empty(text, heading):
        new_body = []
        for n in items:
            new_body += bullet(n)
        text = replace_section_body(text, heading, new_body)

# ---------- 3) Ensure Final Maturity Score table is filled ----------
def fill_maturity_table(md: str) -> str:
    pattern = re.compile(
        r'(\|\s*Rubric\s*\|\s*Current %\s*\|\s*Target %\s*\|\s*\n'
        r'\|[-\s|]+\|\s*\n'
        r'(?P<body>(?:\|\s*.*\s*\|\s*.*\s*\|\s*.*\s*\|\s*\n)+))',
        re.IGNORECASE
    )
    def repl(m):
        body = m.group('body')
        def fix_row(row):
            if not row.strip().startswith("|") or set(row.strip()) <= set("|-"):
                return row
            cols = [c.strip() for c in row.strip().split("|")]
            if len(cols) < 5:
                return row
            rubric, curr, targ = cols[1], cols[2], cols[3]
            def fmt(p):
                p = p.replace('%','').strip()
                try:
                    val = float(p)
                except:
                    return "0.00 %"
                return f"{val:.2f} %"
            if rubric.lower() in ("viability","success","upkeep","support","overall"):
                curr = fmt(curr) if curr else "0.00 %"
                targ = fmt(targ) if targ else "0.00 %"
            return f"| {rubric} | {curr} | {targ} |\n"
        new_body = "".join(fix_row(r) for r in body.splitlines(True))
        return m.group(1).replace(body, new_body)
    return pattern.sub(repl, md)

text = fill_maturity_table(text)

# ---------- 4) Ensure Technical Focus table cells are filled ----------
def fill_tech_table(md: str) -> str:
    lines = md.splitlines()
    out = []
    in_table = False
    for ln in lines:
        if ln.strip().startswith("| Area") and "Score (0–2)" in ln:
            in_table = True
            out.append(ln); continue
        if in_table and re.match(r'^\|\s*-+\s*\|', ln):
            out.append(ln); continue
        if in_table:
            if not ln.strip().startswith("|"):
                in_table = False
                out.append(ln)
                continue
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

# Write back
with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("normalize_report.py: normalization completed.")
