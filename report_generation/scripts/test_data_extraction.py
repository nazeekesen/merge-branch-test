from src.data_extraction import extract_platform_entries, extract_technical_scores, extract_critical_risks, extract_compliance_posture, extract_final_maturity_scores, write_entry, write_final_maturity_entry
from src.utils import read_file
from src.config import COMBINED_REPORT_PATH, REPORT_PATH

def test_data_extraction():
    # Read input files
    combined_text = read_file(COMBINED_REPORT_PATH)
    if not combined_text:
        return

    # Extract data
    maturity_entries = extract_platform_entries(combined_text)
    technical_scores = extract_technical_scores(combined_text)
    critical_risks = extract_critical_risks(combined_text)
    compliance_posture = extract_compliance_posture(combined_text)
    final_maturity_scores = extract_final_maturity_scores(combined_text)

    # Write to report.txt
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("## Platform Maturity Results\n\n")
        for entry in maturity_entries:
            write_entry(f, entry)

        f.write("## Technical Focus Area Scores\n\n")
        for entry in technical_scores:
            write_entry(f, entry, is_tech=True)

        f.write("## Critical Risks\n\n")
        for risk in critical_risks:
            f.write(f"Title: {risk['title']}\n")
            f.write(f"Business Impact: {risk['business_impact']}\n")
            f.write("Solution:\n")
            f.write(f"- Immediate: {risk['solution']['immediate']}\n")
            f.write(f"- Short-term: {risk['solution']['short_term']}\n")
            f.write(f"- Long-term: {risk['solution']['long_term']}\n\n")

        if compliance_posture:
            f.write("## Compliance Posture\n\n")
            f.write(f"Overall Compliance Score: {compliance_posture['score']}\n")
            f.write(f"Description: {compliance_posture['description']}\n\n")

        if final_maturity_scores:
            f.write("## Final Maturity Scores\n\n")
            for entry in final_maturity_scores:
                write_final_maturity_entry(f, entry)

    print(f"✅ Generated report.txt with {len(maturity_entries)} platform entries, {len(technical_scores)} technical scores, {len(critical_risks)} critical risks, compliance posture, and {len(final_maturity_scores)} final maturity scores.")

if __name__ == "__main__":
    test_data_extraction()
