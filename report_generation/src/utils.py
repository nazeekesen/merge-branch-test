from pathlib import Path
from dash import html
import re
from src.config import REPORT_PATH

def read_file(file_path):
    """Read the content of a file and return it as a string."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return None

def parse_report_file(path):
    """Parse report.txt into maturity, technical, critical risk, and final maturity score data sections."""
    if not Path(path).exists():
        print(f"❌ report.txt not found at {path}")
        return [], [], [], []

    with open(path, "r") as file:
        content = file.read()

    sections = content.strip().split("## ")
    maturity_part = ""
    technical_part = ""
    critical_risk_part = ""
    final_maturity_part = ""

    for section in sections[1:]:
        section_name = section.split("\n")[0].strip()
        if section_name == "Technical Overview":
            maturity_part = section
        elif section_name == "Technical Focus Area Scores":
            technical_part = section
        elif section_name == "Critical Risks":
            critical_risk_part = section
        elif section_name == "Final Maturity Scores":
            final_maturity_part = section

    maturity_blocks = maturity_part.split("\n\n")[1:]  # Skip header

    def parse_maturity_or_technical_blocks(blocks, cap_score_at=5, is_tech=False):
        parsed = []
        for block in blocks:
            lines = block.strip().split("\n")
            if not lines or len(lines) < 5:
                print(f"⚠️ Skipped block due to insufficient lines (expected at least 5, got {len(lines)}):\n{block}\n")
                continue

            try:
                title = lines[0].strip()
                if not title:
                    print(f"⚠️ Skipped block due to empty title:\n{block}\n")
                    continue

                is_maturity = "Priority Level" in lines[1] if not is_tech else False
                expected_lines = 7 if is_maturity else 5
                if len(lines) < expected_lines:
                    print(f"⚠️ Skipped block due to insufficient lines (expected {expected_lines}, got {len(lines)}):\n{block}\n")
                    continue

                priority = lines[1].split(":")[1].strip() if is_maturity else "N/A"
                personas = lines[2].split(":")[1].strip() if is_maturity else "N/A"
                prev_score_raw = lines[3 if is_maturity else 1].split(":")[1].strip()
                # Parse scores as float for maturity, int for technical
                if is_maturity:
                    current = float(lines[4].split(":")[1].strip())
                    target = float(lines[5].split(":")[1].strip())
                else:
                    current = int(lines[2].split(":")[1].strip())
                    target = int(lines[3].split(":")[1].strip())
                findings = lines[6 if is_maturity else 4].split(":", 1)[1].strip().strip("*")

                prev = None if prev_score_raw.upper() == "N/A" else float(prev_score_raw) if is_maturity else int(prev_score_raw)
                parsed.append({
                    "title": title,
                    "priority": priority,
                    "personas": personas,
                    "scores": [prev if prev is not None else 0, current, min(target, cap_score_at)],
                    "findings": findings,
                    "prev_score_missing": prev is None
                })
                print(f"Parsed entry: {title}")
            except Exception as e:
                print(f"⚠️ Skipped block due to error: {e}\nBlock:\n{block}\n")
        return parsed

    def parse_critical_risk_blocks(blocks):
        parsed = []
        for block in blocks:
            lines = block.strip().split("\n")
            if not lines or len(lines) < 5:
                print(f"⚠️ Skipped block due to insufficient lines (expected at least 5, got {len(lines)}):\n{block}\n")
                continue

            try:
                title = lines[0].split(":", 1)[1].strip() if lines[0].startswith("Title:") else None
                if not title:
                    print(f"⚠️ Skipped block due to empty title:\n{block}\n")
                    continue

                business_impact = lines[1].split(":", 1)[1].strip() if lines[1].startswith("Business Impact:") else ""
                solution_header = lines[2]
                immediate = lines[3].split(":", 1)[1].strip() if lines[3].startswith("- Immediate:") else ""
                short_term = lines[4].split(":", 1)[1].strip() if lines[4].startswith("- Short-term:") else ""
                long_term = lines[5].split(":", 1)[1].strip() if lines[5].startswith("- Long-term:") else ""

                parsed.append({
                    "title": title,
                    "business_impact": business_impact,
                    "solution": {
                        "immediate": immediate,
                        "short_term": short_term,
                        "long_term": long_term
                    }
                })
            except Exception as e:
                print(f"⚠️ Skipped block due to error: {e}\nBlock:\n{block}\n")
        return parsed

    def parse_final_maturity_blocks(blocks):
        parsed = []
        for block in blocks:
            lines = block.strip().split("\n")
            if not lines or len(lines) < 3:
                print(f"⚠️ Skipped final maturity block due to insufficient lines (expected at least 3, got {len(lines)}):\n{block}\n")
                continue

            try:
                rubric = lines[0].split(":", 1)[1].strip() if lines[0].startswith("Rubric:") else None
                if not rubric:
                    print(f"⚠️ Skipped final maturity block due to empty rubric:\n{block}\n")
                    continue

                current_percent = lines[1].split(":", 1)[1].strip().rstrip("%") if lines[1].startswith("Current Percent:") else ""
                target_percent = lines[2].split(":", 1)[1].strip().rstrip("%") if lines[2].startswith("Target Percent:") else ""

                decline_percent = None
                if rubric == "Overall" and len(lines) >= 4 and lines[3].startswith("Decline Percent:"):
                    decline_percent = lines[3].split(":", 1)[1].strip().rstrip("%")

                parsed.append({
                    "rubric": rubric,
                    "current_percent": float(current_percent),
                    "target_percent": float(target_percent),
                    "decline_percent": float(decline_percent) if decline_percent is not None else None
                })
            except Exception as e:
                print(f"⚠️ Skipped final maturity block due to error: {e}\nBlock:\n{block}\n")
        return parsed

    maturity = parse_maturity_or_technical_blocks(maturity_blocks, cap_score_at=5.0)
    technical = parse_maturity_or_technical_blocks(technical_part.split("\n\n"), cap_score_at=2, is_tech=True)
    critical_risks = parse_critical_risk_blocks(critical_risk_part.split("\n\n"))
    final_maturity_scores = parse_final_maturity_blocks(final_maturity_part.split("\n\n")[1:])

    print(f"✅ Loaded {len(maturity)} maturity, {len(technical)} technical, {len(critical_risks)} critical risks, and {len(final_maturity_scores)} final maturity scores from {path}")
    return maturity, technical, critical_risks, final_maturity_scores

def build_legend(legend_items, is_horizontal=True):
    """Build a legend for either maturity or technical sections."""
    if is_horizontal:
        return html.Div(
            style={"display": "flex", "flexWrap": "nowrap", "gap": "20px", "marginBottom": "20px", "justifyContent": "flex-start"},
            children=[
                html.Div([
                    html.Div(style={
                        "width": "20px", "height": "20px", "backgroundColor": color, "border": "1px solid black",
                        "display": "inline-block", "verticalAlign": "middle"
                    }),
                    html.Span(f" {label}", style={"fontSize": "12px", "marginLeft": "5px"})
                ])
                for label, color in legend_items
            ]
        )
    else:
        return html.Div(
            style={"marginTop": "20px"},
            children=[
                html.Div("Legend", style={"fontWeight": "bold"}),
                html.Div([
                    html.Div([
                        html.Div(style={
                            "width": "20px", "height": "20px", "backgroundColor": color, "border": "1px solid black",
                            "display": "inline-block", "verticalAlign": "middle"
                        }),
                        html.Span(f" {label}", style={"fontSize": "12px", "marginLeft": "5px"})
                    ], style={"marginBottom": "5px"})
                    for label, color in legend_items
                ])
            ]
        )

def extract_compliance_posture_from_report():
    """Extract the Overall Compliance Score and Description from report.txt."""
    text = read_file(REPORT_PATH)
    if not text:
        return None

    start = text.find("Compliance Posture\n")
    if start == -1:
        print("❌ Could not find 'Compliance Posture' section in report.txt.")
        return None

    pattern = re.compile(
        r'Overall Compliance Score: (.+?)\nDescription: (.+?)(?=\n##|\Z)',
        re.DOTALL
    )
    match = pattern.search(text[start:])

    if not match:
        print("⚠️ No compliance posture matched in report.txt.")
        return None

    score, description = match.groups()
    return {
        "score": score.strip(),
        "description": description.strip()
    }
