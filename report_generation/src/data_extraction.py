import re

def extract_platform_entries(text):
    start = text.find("## 2. Platform Maturity Scoring")
    if start == -1:
        print("❌ Error: 'Platform Maturity Scoring' section not found.")
        return []

    end = text.find("## 3. Final Maturity Score", start)
    if end == -1:
        end = len(text)
    section_text = text[start:end]
    # Filter out lines starting with ###
    section_text = "\n".join(line for line in section_text.splitlines() if not line.strip().startswith("###"))
    print(f"🔍 Platform Maturity Scoring section found. Length: {len(section_text)} chars")

    pattern = re.compile(
        r'- \*\*(.+?) \(Score: ([\d.]+)\) \(Priority level: (\d)\) \(Personas: ([^\)]+)\)\*\*\s*\n\s*([^\n-].+?)(?=\n\s*(?:- \*\*|\n\s*####|\n---|\Z))',
        re.DOTALL
    )
    matches = list(pattern.finditer(section_text))
    print(f"✅ Found {len(matches)} platform entries.")

    entries = []
    for match in matches:
        title, score_str, priority_level, personas, findings = match.groups()
        title = title.strip()
        score = float(score_str)
        priority_level = int(priority_level)
        personas = personas.strip()
        findings = findings.strip()
        entries.append({
            "title": title,
            "priority_level": priority_level,
            "personas": personas,
            "previous_score": "N/A",
            "current_score": score,
            "target_score": min(score + 1, 5.0),  # Cap at 5.0 for float scores
            "findings": findings
        })
        print(f"  - Extracted: Title='{title}', Score={score}, Priority={priority_level}, Personas='{personas}', Findings='{findings[:50]}...'")
    return entries

def extract_technical_scores(text):
    start = text.find("## 6. Technical Focus Area Scores")
    if start == -1:
        print("❌ Could not find 'Technical Focus Area Scores' section.")
        return []

    rows = []
    for line in text[start:].splitlines():
        if line.strip().startswith("| Area") or set(line.strip()) <= {"|", "-"} or not line.strip().startswith("|"):
            continue
        if line.strip() == "":
            break

        cells = [cell.strip() for cell in line.strip().strip('|').split('|')][:3]
        if len(cells) < 3:
            print(f"⚠️ Skipping malformed row: {line}")
            continue

        area, score_str, justification = cells
        area = area.replace("**", "").strip()
        try:
            score = min(int(score_str), 2)
            if int(score_str) > 2:
                print(f"⚠️ Score for '{area}' exceeds 2. Clamped to 2.")
            rows.append({
                "area": area,
                "previous": "N/A",
                "score": score,
                "target": min(score + 1, 2),
                "justification": justification
            })
        except ValueError:
            print(f"⚠️ Invalid score for '{area}': '{score_str}'")

    print(f"✅ Found {len(rows)} technical scores.")
    return rows

def extract_critical_risks(text):
    start = text.find("## 1. Critical Risks")
    if start == -1:
        print("❌ Could not find '1. Critical Risks' section.")
        return []

    end = text.find("## 2. Platform Maturity Scoring", start)
    if end == -1:
        end = len(text)
    section_text = text[start:end]

    pattern = re.compile(
        r'### \d+\.\s*(?:\*\*)?(.+?)(?:\*\*)?\n\n'
        r'\*\*Business Impact:\*\*\s*\n(.+?)\n\n'
        r'\*\*Solution:\*\*\s*\n'
        r'- \*\*Immediate:\*\*\s*(.+?)\n'
        r'- \*\*Short-term:\*\*\s*(.+?)\n'
        r'- \*\*Long-term:\*\*\s*(.+?)(?=\n\n### \d+\.\s*(?:\*\*)?|\n\n##|\Z)',
        re.DOTALL
    )
    matches = list(pattern.finditer(section_text))

    if not matches:
        print("⚠️ No critical risks matched. Section text:")
        print(section_text[:500] + "..." if len(section_text) > 500 else section_text)
        print("Pattern used:", pattern.pattern)

    print(f"✅ Found {len(matches)} critical risks.")

    risks = []
    for match in matches:
        title, business_impact, immediate, short_term, long_term = match.groups()
        clean_title = title.replace("**", "").strip()
        risks.append({
            "title": clean_title,
            "business_impact": business_impact.strip(),
            "solution": {
                "immediate": immediate.strip(),
                "short_term": short_term.strip(),
                "long_term": long_term.strip()
            }
        })
    return risks

def extract_compliance_posture(text):
    start = text.find("## 4. Compliance Posture")
    if start == -1:
        print("❌ Could not find '4. Compliance Posture' section.")
        return None

    end = text.find("## 5. Recommendations Summary", start)
    if end == -1:
        end = len(text)
    section_text = text[start:end]

    pattern = re.compile(
        r'[\*]{1,2}Overall Compliance Score:\*+\s*\*+(\d+%)\*+\s*\n\n(.+?)(?=\n\n##|\Z)',
        re.DOTALL
    )
    match = pattern.search(section_text)

    if not match:
        print("⚠️ No compliance posture matched. Section text:")
        print(section_text[:500] + "..." if len(section_text) > 500 else section_text)
        print("Pattern used:", pattern.pattern)
        return None

    score, description = match.groups()
    print(f"✅ Extracted Overall Compliance Score: {score}")
    return {
        "score": score.strip(),
        "description": description.strip()
    }

def extract_final_maturity_scores(text):
    start = text.find("## 3. Final Maturity Score")
    if start == -1:
        print("❌ Could not find '3. Final Maturity Score' section in the provided text.")
        return []

    end = text.find("## 4. Compliance Posture", start)
    if end == -1:
        end = len(text)
    section_text = text[start:end]

    print(f"🔍 Extracting Final Maturity Scores. Section text (first 500 chars):")
    print(section_text[:500] + "..." if len(section_text) > 500 else section_text)

    pattern = re.compile(
        r'^\|\s*(?:\*\*)?([^\|]+?)(?:\*\*)?\s*\|\s*([\d.]+)\s*%?\s*\|\s*([\d.]+)\s*%?\s*\|$',
        re.MULTILINE
    )
    matches = list(pattern.finditer(section_text))

    if not matches:
        print("⚠️ No final maturity scores matched.")
        print("Pattern used:", pattern.pattern)
        return []

    print(f"✅ Found {len(matches)} final maturity scores.")

    scores = []
    for match in matches:
        rubric, current, target = match.groups()
        rubric = rubric.replace("**", "").strip()
        try:
            current = float(current)
            target = float(target)
            entry = {
                "rubric": rubric,
                "current_percent": current,
                "target_percent": target
            }
            if rubric == "Overall":
                decline = max(current - 20, 5)
                entry["decline_percent"] = decline
            scores.append(entry)
            print(f"  - Matched: Rubric='{rubric}', Current={current}%, Target={target}%"
                  + (f", Decline={decline}%" if rubric == "Overall" else ""))
        except ValueError:
            print(f"⚠️ Invalid percentages for '{rubric}': Current='{current}', Target='{target}'")

    return scores

def write_entry(f, entry, is_tech=False):
    f.write(f"{entry['area' if is_tech else 'title']}\n")
    if not is_tech:
        f.write(f"Priority Level: {entry['priority_level']}\n")
        f.write(f"Personas: {entry['personas']}\n")
    f.write(f"Previous Score: {entry['previous' if is_tech else 'previous_score']}\n")
    f.write(f"{'Score' if is_tech else 'Current Score'}: {entry['score' if is_tech else 'current_score']}\n")
    f.write(f"Target Score: {entry['target' if is_tech else 'target_score']}\n")
    f.write(f"{'Justification' if is_tech else 'Findings'}: {entry['justification' if is_tech else 'findings']}\n\n")

def write_final_maturity_entry(f, entry):
    f.write(f"Rubric: {entry['rubric']}\n")
    f.write(f"Current Percent: {entry['current_percent']}%\n")
    f.write(f"Target Percent: {entry['target_percent']}%\n")
    if "decline_percent" in entry:
        f.write(f"Decline Percent: {entry['decline_percent']}%\n")
    f.write("\n")

def write_report_file(text, output_path):
    print("🔍 Starting report generation...")
    platform_entries = extract_platform_entries(text)
    technical_scores = extract_technical_scores(text)
    critical_risks = extract_critical_risks(text)
    compliance_posture = extract_compliance_posture(text)
    final_maturity_scores = extract_final_maturity_scores(text)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("## Technical Overview\n\n")
        for entry in platform_entries:
            print(f"Writing entry: {entry['title']}")
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
        else:
            print("⚠️ No final maturity scores written to report.txt.")

    print(f"✅ Generated {output_path} with {len(platform_entries)} technical overview entries, {len(technical_scores)} technical scores, {len(critical_risks)} critical risks, and {len(final_maturity_scores)} final maturity scores.")
