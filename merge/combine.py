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
You are a senior Kubernetes and DevOps consultant. You are given two separate assessment documents:

1. A machine-generated report created from automated scans and analysis.
2. A QA-reviewed report containing rubric-based scores, findings from interviews, and manual insights.

Your task is to analyze both of these **in full** and generate a new, unified assessment report. 

This should not be a side-by-side merge. Instead, **you must absorb and fully understand the insights from both sources**, then **rewrite the entire report from scratch**, combining the strongest, clearest, and most relevant findings from both.

**Instructions:**
- First, carefully read and comprehend both the AI-generated and QA-reviewed documents.
- Then, write a single **executive-level assessment** as if it were delivered by a consulting firm to a CISO, CTO, or VP of Engineering.
- The tone must be clear, formal, and professionally composed.
- The resulting report must **use the structure below**, and all sections should reflect **merged, synthesized insights**.

---

# Final Kubernetes Assessment Report

## Executive Summary

Summarize the most important conclusions. This includes:
- Platform maturity and readiness
- Major gaps or risks
- Positive trends or strengths
- What leadership should prioritize in the next 90 days

## 1. Critical Risks

List the 4–5 highest-impact risks across the platform.  
For each:
- Title  
- Business Impact  
- Solution (Immediate, Short-term, Long-term)

Do not mention scanner tools or source names. Write as if the risks were discovered through a full audit.

## 2. Platform Maturity Scoring

Group observations under the four main pillars:

### A. Enterprise Platform Viability
- Production-Ready Environment  
- Roles and Responsibilities  
- Leadership Commitment  
- Security Integration  
- Engagement and Communication  
- Workload Understanding  

### B. Platform Success
- DevOps Skills  
- Automated Deployments  
- Release Engineering  
- Site Reliability Engineering  
- User Access  

### C. Platform Upkeep
- Upgrades  
- Day-2 Operations  
- Monitoring and Alerts  
- Capacity Planning  
- Disaster Recovery  

### D. Platform Support
- Proactive Support  
- Compliance  
- Escalation Handling  
- Third-Party Tooling  

For each item:
- Give a score from 1 to 5
- Write a short paragraph explaining the evidence, strengths, and what to improve

## 3. Final Maturity Score

Estimate the overall maturity score using this formula:
Maturity = (Viability × 30 + Success × 25 + Upkeep × 25 + Support × 20) ÷ 100  
If exact numbers are not possible, estimate it based on the full review.

## 4. Compliance Posture

Summarize the platform's alignment with compliance expectations (e.g., RBAC, audit logging, backup practices, IAM).  
Estimate an overall compliance score in % if possible.

## 5. Recommendations Summary

Summarize key actions across three time horizons:
- Immediate (next 2 weeks)
- Short-term (30–90 days)
- Strategic (6–12 months)

## Formatting and Language Guidelines:
- Use bullet points only where it aids clarity — prefer paragraphs where possible.
- Do not repeat findings from both sources. Combine them into cohesive insights.
- Don’t say “in the AI report” or “according to QA”. Speak as one voice.
- Don’t use raw data, JSON, or scanner terminology.

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
