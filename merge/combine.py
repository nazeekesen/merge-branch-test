import openai
import os

def load_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def save_output(text, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

def merge_reports(api_key, ai_report, qa_report, prompt_path):
    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    prompt_template = load_file(prompt_path)
    merged_prompt = prompt_template.format(ai=ai_report, qa=qa_report)

    response = client.chat.completions.create(
        model="o1-mini-2024-09-12",
        messages=[
            {
                "role": "user",
                "content": (
                    """
You are a senior Kubernetes and DevOps consultant.

You are given two input documents:
1. A machine-generated assessment report.
2. A QA-reviewed assessment report.

Your task is to merge both sources into a **single, unified final Kubernetes assessment report**.

## STRUCTURE & FORMATTING RULES (CRITICAL):
- Reproduce **exactly** the structure, headings, formatting marks, and symbols of the template provided below.
- Keep **all** markdown symbols (`#`, `##`, `###`, `-`, `*`, `:`, `|`, etc.) exactly as they appear.
- Do not reorder, rename, or remove any headings.
- If a section has no content, leave it empty (only the heading remains). Do **not** insert placeholders or explanations such as “This section was missing”.
- Do not add any new sections, bullets, footers, or comments.
- Do not alter spacing, heading levels, or bullet formatting.
- Your output must match this structure **100%**, so it passes automated validation.
- Do not include any reference to the source documents.

## WRITING STYLE:
- Formal and executive tone (CISO/CTO level).
- Synthesized insights — speak as one unified expert, not two sources.
- Concise, factual, and structured.
- Use bullet points and subheadings where already in the template, nowhere else.

## TEMPLATE TO FOLLOW EXACTLY:

# Final Kubernetes Assessment Report

## Executive Summary

## 1. Critical Risks

### 1. **Insufficient Business Continuity and Disaster Recovery (BCDR) Planning**

**Business Impact:**  
...

**Solution:**  
- **Immediate:** ...
- **Short-term:** ...
- **Long-term:** ...

---

### 2. **Weak Container Image Management and Security**

**Business Impact:**  
...

**Solution:**  
- **Immediate:** ...
- **Short-term:** ...
- **Long-term:** ...

---

### 3. **Inadequate Infrastructure Automation and Configuration Management**

**Business Impact:**  
...

**Solution:**  
- **Immediate:** ...
- **Short-term:** ...
- **Long-term:** ...

---

### 4. **Deficient Security Controls and User Access Management**

**Business Impact:**  
...

**Solution:**  
- **Immediate:** ...
- **Short-term:** ...
- **Long-term:** ...

---

### 5. **Limited Monitoring, Logging, and Observability**

**Business Impact:**  
...

**Solution:**  
- **Immediate:** ...
- **Short-term:** ...
- **Long-term:** ...

## 2. Platform Maturity Scoring

#### **Enterprise Platform Viability**

- **Production-Ready Environment (Score: )**  
  *...*

- **Roles and Responsibilities (RACI) (Score: )**  
  *...*

- **Leadership Commitment (Score: )**  
  *...*

- **Security Integration (Score: )**  
  *...*

- **Engagement and Communication (Score: )**  
  *...*

- **Workload Understanding (App Workloads) (Score: )**  
  *...*

### B. Platform Success

- **DevOps Skills (Score: )**  
  *...*

- **Automated Deployments (Automation) (Score: )**  
  *...*

- **Release Engineering (Change Management) (Score: )**  
  *...*

- **Site Reliability Engineering (Reliability) (Score: )**  
  *...*

- **User Access (Access) (Score: )**  
  *...*

### C. Platform Upkeep

- **Upgrades (Score: )**  
  *...*

- **Operational Excellence (Day-2 Ops) (Score: )**  
  *...*

- **Monitoring (Logging, Metrics, Alerts) (Score: )**  
  *...*

- **Capacity Planning and Management (Score: )**  
  *...*

- **Business Continuity and Disaster Recovery (BCDR) (Score: )**  
  *...*

### D. Platform Support

- **Proactive Support (Score: )**  
  *...*

- **Compliance Coverage (Score: )**  
  *...*

- **Escalation Processes (Score: )**  
  *...*

- **Third-Party Services Integration (Score: )**  
  *...*

## 3. Final Maturity Score

| Rubric      | Current % | Target % |
|-------------|-----------|----------|
| Viability   |           |          |
| Success     |           |          |
| Upkeep      |           |          |
| Support     |           |          |
|-------------|-----------|----------|
| Overall     |           |          |

## 4. Compliance Posture

## 5. Recommendations Summary

- **Immediate (Next 2 Weeks):**
  - ...

- **Short-term (30–90 Days):**
  - ...

- **Strategic (6–12 Months):**
  - ...

## 6. Technical Focus Area Scores

| Area                 | Score (0–2) | Justification                                                                                      |
|----------------------|-------------|----------------------------------------------------------------------------------------------------|
| Installation         |             |                                                                                                    |
| Configuration        |             |                                                                                                    |
| Provisioning         |             |                                                                                                    |
| Deployment           |             |                                                                                                    |
| High Availability    |             |                                                                                                    |
| Scalability          |             |                                                                                                    |
| Performance          |             |                                                                                                    |
| Networking           |             |                                                                                                    |
| Security             |             |                                                                                                    |
| Metrics              |             |                                                                                                    |
| Logs                 |             |                                                                                                    |
| Backup and Restore   |             |                                                                                                    |
| Cost Optimization    |             |                                                                                                    |
| Documentation        |             |                                                                                                    |
| Tests                |             |                                                                                                    |

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
