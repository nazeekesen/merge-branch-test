# scripts/main.py
import argparse
from typing import Dict, Any, List

from src.data_extraction import (
    extract_platform_entries,
    extract_technical_scores,
    extract_critical_risks,
    extract_compliance_posture,
    extract_final_maturity_scores,
    write_entry,
    write_final_maturity_entry,
)
from src.utils import read_file, parse_report_file
from src.document_creation import create_dash_app
from src.config import COMBINED_REPORT_PATH, REPORT_PATH


def _map_by_key(items: List[Dict[str, Any]], key: str) -> Dict[str, Dict[str, Any]]:
    """Build a dict keyed by `key` (e.g., title/area) for quick lookups."""
    out = {}
    for it in items:
        k = it.get(key)
        if k:
            out[k] = it
    return out


def main():
    parser = argparse.ArgumentParser(description="Render Dash report from combined markdown.")
    parser.add_argument(
        "-c", "--current",
        default=COMBINED_REPORT_PATH,
        help=f"Path to CURRENT combined_report.md (default: {COMBINED_REPORT_PATH})"
    )
    parser.add_argument(
        "-p", "--previous",
        default=None,
        help="Path to PREVIOUS combined_report.md (optional). When provided, 'Previous' values in report.txt will be populated."
    )
    args = parser.parse_args()

    # Load CURRENT combined report
    combined_text = read_file(args.current)
    if not combined_text:
        return

    # Always extract CURRENT
    cur_maturity = extract_platform_entries(combined_text)
    cur_tech = extract_technical_scores(combined_text)
    cur_risks = extract_critical_risks(combined_text)
    cur_compliance = extract_compliance_posture(combined_text)
    cur_final = extract_final_maturity_scores(combined_text)

    # Optionally extract PREVIOUS to populate "Previous" values
    prev_maturity_map = {}
    prev_tech_map = {}
    if args.previous:
        prev_text = read_file(args.previous)
        if prev_text:
            prev_maturity = extract_platform_entries(prev_text)
            prev_tech = extract_technical_scores(prev_text)
            # Map by title / area for quick lookups
            prev_maturity_map = _map_by_key(prev_maturity, "title")
            prev_tech_map = _map_by_key(prev_tech, "area")

    # Write normalized report.txt with optional previous values filled
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        # --- Technical Overview (per-rubric maturity cards)
        f.write("## Technical Overview\n\n")
        for entry in cur_maturity:
            # If we have a previous version, use its CURRENT score as the "Previous Score" for this title
            if prev_maturity_map:
                prev = prev_maturity_map.get(entry["title"])
                if prev:
                    # entry fields are from extract_platform_entries:
                    #   previous_score, current_score, target_score
                    entry = dict(entry)  # shallow copy
                    entry["previous_score"] = prev["current_score"]
            print(f"Main: Writing entry: {entry['title']}")
            write_entry(f, entry)

        # --- Technical Focus Area Scores (0–2)
        f.write("## Technical Focus Area Scores\n\n")
        for entry in cur_tech:
            if prev_tech_map:
                prev = prev_tech_map.get(entry["area"])
                if prev:
                    entry = dict(entry)
                    entry["previous"] = prev["score"]
            write_entry(f, entry, is_tech=True)

        # --- Critical Risks (unchanged)
        f.write("## Critical Risks\n\n")
        for risk in cur_risks:
            f.write(f"Title: {risk['title']}\n")
            f.write(f"Business Impact: {risk['business_impact']}\n")
            f.write("Solution:\n")
            f.write(f"- Immediate: {risk['solution']['immediate']}\n")
            f.write(f"- Short-term: {risk['solution']['short_term']}\n")
            f.write(f"- Long-term: {risk['solution']['long_term']}\n\n")

        # --- Compliance Posture (unchanged)
        if cur_compliance:
            f.write("## Compliance Posture\n\n")
            f.write(f"Overall Compliance Score: {cur_compliance['score']}\n")
            f.write(f"Description: {cur_compliance['description']}\n\n")

        # --- Final Maturity Scores (unchanged; "Overall" line chart uses quarters dynamically)
        if cur_final:
            f.write("## Final Maturity Scores\n\n")
            for entry in cur_final:
                write_final_maturity_entry(f, entry)

    print(
        f"✅ Generated report.txt with {len(cur_maturity)} technical overview entries, "
        f"{len(cur_tech)} technical scores, {len(cur_risks)} critical risks, "
        f"{'compliance posture, ' if cur_compliance else ''}"
        f"and {len(cur_final)} final maturity scores."
    )

    # Re-parse normalized file and run the Dash app
    maturity_data, technical_data, _, final_maturity_scores = parse_report_file(REPORT_PATH)
    app = create_dash_app(maturity_data, technical_data, cur_risks, final_maturity_scores)
    app.run_server(debug=True, dev_tools_ui=False)


if __name__ == "__main__":
    main()

