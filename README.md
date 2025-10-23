
# Assessment Report Merger

This project automates the merging of two types of assessment reports—an AI-generated report and a QA-reviewed script-based report—into a single, polished summary using OpenAI’s language model.

## Features

- Combines insights from automated scans and manual rubric-based assessments
- Uses a customizable prompt template to guide the content structure
- Produces a cohesive, professional-quality final report

## Before You Begin

1. **Clone the repository on your code editor( VScode) or a terminal:**

```bash

git clone https://github.com/360-cloud-platforms/assessment_pipeline_automation.git
cd assessment_pipeline_automation
```

## Usage

1. Add your input files to the `merge/input/` directory:
   - `final_report.md` — the machine-generated assessment
   - `results.txt` — the manually reviewed QA report

2. (Optional) Add a prompt template to the `merge/prompts/` directory:
   - `combined_prompt.txt` — a custom prompt to shape the merged report 
   - Paste the same prompt on the "content" on 24 line. 

3. Push your changes to GitHub:

```bash
git init
git add .
git commit -m "your_message"
git push -u origin your_branch
```

## How to Run

1. Navigate to the **Actions** tab in your GitHub repository.
2. Select the **Merge Assessment Reports** workflow.
3. Click **Run workflow** and provide your **OpenAI API key** when prompted.
4. After the workflow completes, download the final merged report from the **Upload combined report** step.
5. The output will be available as `final_merged_report.zip`.