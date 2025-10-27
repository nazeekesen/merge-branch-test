#!/usr/bin/env python3
import re
import sys
from typing import List

path = sys.argv[1]
text = open(path, encoding="utf-8").read()

lines = text.splitlines()

# --- 1) Collapse blank line between Findings and Resolution
out: List[str] = []
i = 0
while i < len(lines):
    out.append(lines[i])
    # detect Findings line
    if re.match(r'^\s*\*Findings:\*', lines[i]):
        # if next line is blank and the one after is Resolution -> drop the blank
        if i + 2 < len(lines) and lines[i+1].strip() == "" and re.match(r'^\s*\*Resolution:\*', lines[i+2]):
            # skip the blank line
            i += 1  # this increments again at loop end, net effect: drop one blank
    i += 1

text = "\n".join(out)

# --- 2) Ensure Final Maturity Score table cells are populated
def fill_maturity_table(markdown: str) -> str:
    # Find the maturity table block
    pattern = re.compile(
        r'(\|\s*Rubric\s*\|\s*Current %\s*\|\s*Target %\s*\|\s*\n'
        r'\|[-\s|]+\|\s*\n'  # separator row
        r'(?P<body>(?:\|\s*.*\s*\|\s*.*\s*\|\s*.*\s*\|\s*\n)+))',
        re.IGNORECASE
    )

    def repl(m):
        body = m.group('body')
        def fix_row(row):
            # | Viability | ... | ... |
            cols = [c.strip() for c in row.strip().split('|')]
            if len(cols) < 5:
                return row  # not a proper row
            rubric = cols[1]
            curr = cols[2] or "0.00 %"
            targ = cols[3] or "0.00 %"
            # force format NN.NN %
            def fmt(p):
                p = p.replace('%','').strip()
                try:
                    val = float(p)
                except:
                    return "0.00 %"
                return f"{val:.2f} %"
            if rubric.lower() in ("viability","success","upkeep","support","overall"):
                curr = fmt(curr)
                targ = fmt(targ)
            return f"| {rubric} | {curr} | {targ} |\n"

        new_body = ""
        for row in body.splitlines(True):
            if row.strip().startswith("|") and not set(row.strip()) <= set("|-"):
                new_body += fix_row(row)
            else:
                new_body += row
        return m.group(1).replace(body, new_body)

    return pattern.sub(repl, markdown)

text = fill_maturity_table(text)

# --- 3) Ensure Technical Focus table cells are populated
def fill_tech_table(markdown: str) -> str:
    # Find the table under "## 6. Technical Focus Area Scores"
    # We’ll fill empty score with 0 and empty justification with "TBD".
    in_table = False
    out = []
    for line in markdown.splitlines():
        if line.strip().startswith("| Area") and "Score (0–2)" in line:
            in_table = True
            out.append(line)
            continue
        if in_table and re.match(r'^\|\s*-+\s*\|', line):
            out.append(line); continue
        if in_table:
            if not line.strip().startswith("|"):
                in_table = False
                out.append(line)
                continue
            # process row
            parts = [p.strip() for p in line.strip().split("|")]
            # ['', Area, Score, Justification, '']
            if len(parts) >= 4:
                area = parts[1]
                score = parts[2] or "0"
                just = parts[3] or "TBD"
                # sanitize score to 0/1/2
                try:
                    s = int(float(score))
                    if s not in (0,1,2):
                        s = 0
                    score = str(s)
                except:
                    score = "0"
                line = f"| {area} | {score} | {just} |"
        out.append(line)
    return "\n".join(out)

text = fill_tech_table(text)

# Write back
with open(path, "w", encoding="utf-8") as f:
    f.write(text)
print("normalize_report.py: normalization completed.")
