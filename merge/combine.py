import os

def load_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def save_output(text, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

def merge_reports(api_key, ai_report, qa_report, prompt_path):
    if not api_key or not api_key.strip():
        raise RuntimeError("OPENAI_API_KEY is not set. Provide it via env or workflow input/secret.")

    from openai import OpenAI

    # Support project-scoped keys (harmless if unset)
    client = OpenAI(
        api_key=api_key,
        organization=os.getenv("OPENAI_ORG_ID"),
        project=os.getenv("OPENAI_PROJECT"),
    )

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # <-- safe default

    prompt_template = load_file(prompt_path)
    merged_prompt = prompt_template.format(ai=ai_report, qa=qa_report)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": (
                    """
You are a senior Kubernetes and DevOps consultant.

You are given two input documents:
1) A machine-generated assessment report.
2) A QA-reviewed assessment report.

Your task: merge them into ONE final report.

CRITICAL STRUCTURE RULES:
- Reproduce EXACTLY the headings, symbols, and order shown in the TEMPLATE below.
- Do not add, remove, or rename headings. Do not add extra sections.
- Every section must be NON-EMPTY. Do not output “...”.
- For each critical risk section:
  - Output a **Business Impact** paragraph.
  - Then a **Solution** list with three bullets (Immediate, Short-term, Long-term).
  - Then add ONE closing sentence as a paragraph after the list (this satisfies validator shape: para → list → para).
- For each maturity item:
  - Output a list item line like: “- **Production-Ready Environment (Score: X) (Priority level: Y) (Personas: Z)**”
  - Immediately followed by two paragraphs on consecutive lines (no blank line between):
      *Findings:* ...
      *Resolution:* ...
- Fill ALL numeric cells in “Final Maturity Score” and “Technical Focus Area Scores”.
  - Percent format must be `NN.NN %` (e.g., `52.50 %`).
  - Technical scores must be integers 0, 1, or 2 with short justification text.
- Do NOT include any “Unmatched sections”, comments, placeholders, or tool names.
- Output MUST pass a strict validator that checks heading text, section order, and block types.

TEMPLATE TO FOLLOW EXACTLY (fill with content — no “...” anywhere):

# Final Kubernetes Assessment Report

## Executive Summary

## 1. Critical Risks

### 1. **Insufficient Business Continuity and Disaster Recovery (BCDR) Planning**

**Business Impact:**  
[Write a complete paragraph.]

**Solution:**  
- **Immediate:** [One action.]
- **Short-term:** [One action.]
- **Long-term:** [One action.]

[Write one closing sentence paragraph about why addressing this risk changes outcomes.]

---

### 2. **Weak Container Image Management and Security**

**Business Impact:**  
[Paragraph.]

**Solution:**  
- **Immediate:** [One action.]
- **Short-term:** [One action.]
- **Long-term:** [One action.]

[One closing sentence paragraph.]

---

### 3. **Inadequate Infrastructure Automation and Configuration Management**

**Business Impact:**  
[Paragraph.]

**Solution:**  
- **Immediate:** [One action.]
- **Short-term:** [One action.]
- **Long-term:** [One action.]

[One closing sentence paragraph.]

---

### 4. **Deficient Security Controls and User Access Management**

**Business Impact:**  
[Paragraph.]

**Solution:**  
- **Immediate:** [One action.]
- **Short-term:** [One action.]
- **Long-term:** [One action.]

[One closing sentence paragraph.]

---

### 5. **Limited Monitoring, Logging, and Observability**

**Business Impact:**  
[Paragraph.]

**Solution:**  
- **Immediate:** [One action.]
- **Short-term:** [One action.]
- **Long-term:** [One action.]

[One closing sentence paragraph.]

## 2. Platform Maturity Scoring

#### **Enterprise Platform Viability**

- **Production-Ready Environment (Score: X) (Priority level: Y) (Personas: Z)**  
  *Findings:* [One paragraph.]  
  *Resolution:* [One paragraph.]

- **Roles and Responsibilities (RACI) (Score: X) (Priority level: Y) (Personas: Z)**  
  *Findings:* [One paragraph.]  
  *Resolution:* [One paragraph.]

- **Leadership Commitment (Score: X) (Priority level: Y) (Personas: Z)**  
  *Findings:* [One paragraph.]  
  *Resolution:* [One paragraph.]

- **Security Integration (Score: X) (Priority level: Y) (Personas: Z)**  
  *Findings:* [One paragraph.]  
  *Resolution:* [One paragraph.]

- **Engagement and Communication (Score: X) (Priority level: Y) (Personas: Z)**  
  *Findings:* [One paragraph.]  
  *Resolution:* [One paragraph.]

- **Workload Understanding (App Workloads) (Score: X) (Priority level: Y) (Personas: Z)**  
  *Findings:* [One paragraph.]  
  *Resolution:* [One paragraph.]

### **Platform Success**

- **DevOps Skills (Score: X) (Priority level: Y) (Personas: Z)**  
  *Findings:* [One paragraph.]  
  *Resolution:* [One paragraph.]

- **Automated Deployments (Automation) (Score: X) (Priority level: Y) (Personas: Z)**  
  *Findings:* [One paragraph.]  
  *Resolution:* [One paragraph.]

- **Release Engineering (Change Management) (Score: X) (Priority level: Y) (Personas: Z)**  
  *Findings:* [One paragraph.]  
  *Resolution:* [One paragraph.]

- **Site Reliability Engineering (Reliability) (Score: X) (Priority level: Y) (Personas: Z)**  
  *Findings:* [One paragraph.]  
  *Resolution:* [One paragraph.]

- **User Access (Access) (Score: X) (Priority level: Y) (Personas: Z)**  
  *Findings:* [One paragraph.]  
  *Resolution:* [One paragraph.]

### **Platform Upkeep**

- **Upgrades (Score: X) (Priority level: Y) (Personas: Z)**  
  *Findings:* [One paragraph.]  
  *Resolution:* [One paragraph.]

- **Operational Excellence (Day-2 Ops) (Score: X) (Priority level: Y) (Personas: Z)**  
  *Findings:* [One paragraph.]  
  *Resolution:* [One paragraph.]

- **Monitoring (Logging, Metrics, Alerts) (Score: X) (Priority level: Y) (Personas: Z)**  
  *Findings:* [One paragraph.]  
  *Resolution:* [One paragraph.]

- **Capacity Planning and Management (Score: X) (Priority level: Y) (Personas: Z)**  
  *Findings:* [One paragraph.]  
  *Resolution:* [One paragraph.]

- **Business Continuity and Disaster Recovery (BCDR) (Score: X) (Priority level: Y) (Personas: Z)**  
  *Findings:* [One paragraph.]  
  *Resolution:* [One paragraph.]

### **Platform Support**

- **Proactive Support (Score: X) (Priority level: Y) (Personas: Z)**  
  *Findings:* [One paragraph.]  
  *Resolution:* [One paragraph.]

- **Compliance Coverage (Score: X) (Priority level: Y) (Personas: Z)**  
  *Findings:* [One paragraph.]  
  *Resolution:* [One paragraph.]

- **Escalation Processes (Score: X) (Priority level: Y) (Personas: Z)**  
  *Findings:* [One paragraph.]  
  *Resolution:* [One paragraph.]

- **Third-Party Services Integration (Score: X) (Priority level: Y) (Personas: Z)**  
  *Findings:* [One paragraph.]  
  *Resolution:* [One paragraph.]

## 3. Final Maturity Score

| Rubric      | Current % | Target % |
|-------------|-----------|----------|
| Viability   | NN.NN %   | NN.NN %  |
| Success     | NN.NN %   | NN.NN %  |
| Upkeep      | NN.NN %   | NN.NN %  |
| Support     | NN.NN %   | NN.NN %  |
|-------------|-----------|----------|
| Overall     | NN.NN %   | NN.NN %  |

## 4. Compliance Posture

[Write a full paragraph with an explicit overall compliance score like: “Overall Compliance: 85%.”]

## 5. Recommendations Summary

- **Immediate (Next 2 Weeks):**
  - [Bullet]
  - [Bullet]
  - [Bullet]

- **Short-term (30–90 Days):**
  - [Bullet]
  - [Bullet]
  - [Bullet]

- **Strategic (6–12 Months):**
  - [Bullet]
  - [Bullet]
  - [Bullet]

## 6. Technical Focus Area Scores

| Area                 | Score (0–2) | Justification                                                                                      |
|----------------------|-------------|----------------------------------------------------------------------------------------------------|
| Installation         | 0/1/2       | [Short justification.]                                                                             |
| Configuration        | 0/1/2       | [Short justification.]                                                                             |
| Provisioning         | 0/1/2       | [Short justification.]                                                                             |
| Deployment           | 0/1/2       | [Short justification.]                                                                             |
| High Availability    | 0/1/2       | [Short justification.]                                                                             |
| Scalability          | 0/1/2       | [Short justification.]                                                                             |
| Performance          | 0/1/2       | [Short justification.]                                                                             |
| Networking           | 0/1/2       | [Short justification.]                                                                             |
| Security             | 0/1/2       | [Short justification.]                                                                             |
| Metrics              | 0/1/2       | [Short justification.]                                                                             |
| Logs                 | 0/1/2       | [Short justification.]                                                                             |
| Backup and Restore   | 0/1/2       | [Short justification.]                                                                             |
| Cost Optimization    | 0/1/2       | [Short justification.]                                                                             |
| Documentation        | 0/1/2       | [Short justification.]                                                                             |
| Tests                | 0/1/2       | [Short justification.]                                                                             |

# Conclusion

---

Inputs:
AI Report:  
""" + ai_report + "\n\nQA Reviewed Report:\n" + qa_report
                )
            }
        ]
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    ai_report = load_file("merge/input/final_report.md")
    qa_report = load_file("merge/input/results.txt")
    prompt_path = "merge/prompts/combined_prompt.txt"

    result = merge_reports(
        api_key=os.getenv("OPENAI_API_KEY"),
        ai_report=ai_report,
        qa_report=qa_report,
        prompt_path=prompt_path
    )

    os.makedirs("merge/output", exist_ok=True)
    save_output(result, "merge/output/combined_report.md")
