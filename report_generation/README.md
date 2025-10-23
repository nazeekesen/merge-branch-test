# 📊 Report Generator

This project generates reports from markdown files, including **platform maturity**, **technical focus area scores**, **critical risks**, **compliance posture**, and **final maturity scores**, and displays the results in a web-based dashboard using [Dash](https://dash.plotly.com/). The pipeline extracts data from markdown files, generates a structured text report, and creates visualizations for business, operational, and technical overviews.

---
## Example run with Current report only
# ./run.sh

## Example run with a previous and current report
# ./run.sh -p data/combined_report.md -c data/combined_report.md

## 🚀 Project Overview

The project consists of two main steps:

### 1. Data Extraction & Text Report Generation
- Extracts platform maturity entries from `final_report.md`.
- Extracts technical focus area scores, critical risks, compliance posture, and final maturity scores from `combined_report.md`.
- Outputs a structured text report as `report.txt`, including platform maturity results, technical focus area scores, critical risks with business impact and solutions, compliance posture, and final maturity scores (Viability, Success, Upkeep, Support, Overall).

### 2. Web Dashboard Generation
- Parses `report.txt` to build a dashboard using Dash.
- Displays:
  - **Business Overview**: Critical risks with titles, business impact, and solutions (Immediate, Short-term, Long-term), alongside a line graph of the Overall Maturity Score (Current, Target, and Decline percentages) with a legend indicating Current Score, Target Score, and Decline Score.
  - **Operational Overview**: A table of technical focus area scores with summary statistics, compliance posture, and a bar graph of final maturity scores (Viability, Success, Upkeep, Support; excluding Overall).
  - **Technical Overview**: Platform maturity cards with bar charts, priority levels, personas, and findings.

> **Note:** A separate script (`export_pdf.py`) exists for exporting to PDF but is not part of the main pipeline and runs independently.

---

## 📁 Directory Structure

```
report_generator/
├── data/
│   ├── combined_report.md        # Technical scores, critical risks, compliance posture, final maturity scores
│   ├── final_report.md           # Platform maturity scores
│   └── output/
│       └── report.txt            # Generated text report
│
├── scripts/
│   ├── main.py                   # Main script for full pipeline
│   └── test_data_extraction.py   # Data extraction test script
│
├── src/
│   ├── __init__.py
│   ├── business_overview.py      # Business Overview section (critical risks and Overall Maturity Score)
│   ├── chart_generation.py       # Plotly bar charts
│   ├── config.py                 # File paths and settings
│   ├── data_extraction.py        # Markdown parsing and report writing
│   ├── document_creation.py      # Builds the Dash dashboard
│   ├── operational_overview.py   # Operational Overview section (technical scores, compliance, final maturity scores)
│   ├── pdf_export.py             # Optional PDF export script
│   ├── styles.py                 # Shared CSS styles for Dash components
│   ├── technical_overview.py     # Technical Overview section (platform maturity)
│   └── utils.py                  # Shared helpers
│
├── requirements.txt              # Project dependencies
├── run.sh                        # Runs full pipeline
├── run_test_data_extraction.sh   # Runs extraction only
└── README.md                     # This file
```

---

## 📂 File Descriptions

### Input Files
- `data/combined_report.md`  
  - Technical scores (Section 6)
  - Critical risks (Section 1) — with Business Impact and Solution subsections
  - Compliance posture (Section 4)
  - Final maturity scores (Section 3) — Viability, Success, Upkeep, Support, Overall percentages
- `data/final_report.md`  
  - Platform maturity scores (Section 2)

### Output File
- `data/output/report.txt`  
  - Contains platform maturity results, technical scores, critical risks, compliance posture, and final maturity scores in structured format

### Pipeline
- `scripts/main.py`  
  - Runs extraction, report generation, and dashboard
- `scripts/test_data_extraction.py`  
  - Runs extraction and report generation only (no dashboard)

### Core Modules
- `src/__init__.py`: Marks `src/` as a Python package
- `src/business_overview.py`  
  - `create_critical_risk_card`, `create_score_band`, `create_point_legend`, `create_business_overview`
  - Handles Critical Risks section and Overall Maturity Score line graph (Current, Target, and Decline percentages) with a legend below the graph. The Overall Maturity Score section is fixed at 450px wide for both web and PDF views, with the Critical Risks section taking the remaining space (wrapping to the next row in PDF if space is limited).
- `src/chart_generation.py`  
  - `get_technical_color`, `get_maturity_color`, `generate_chart`, `generate_final_maturity_chart`, `generate_single_maturity_chart`
  - `TECHNICAL_LEGEND`, `MATURITY_RISK_LEVELS`, `MULTILINE_LABELS`
  - `generate_single_maturity_chart` creates a line graph for the Overall Maturity Score, showing Current to Target and Current to Decline percentages, with dynamic x-axis labels based on the current date (e.g., Q2 2025 to Q2 2026).
- `src/config.py`  
  - Paths like `FINAL_REPORT_PATH`, `COMBINED_REPORT_PATH`, `REPORT_PATH`
- `src/data_extraction.py`  
  - `extract_platform_entries`, `extract_technical_scores`, `extract_critical_risks`, `extract_compliance_posture`, `extract_final_maturity_scores`
  - `write_entry`, `write_final_maturity_entry`, `platform_data`
- `src/document_creation.py`  
  - `read_file`, `create_dash_app`
  - Coordinates dashboard assembly
- `src/operational_overview.py`  
  - `create_technical_table`, `create_operational_overview`
  - Handles Technical Focus Area Scores, compliance posture, and Final Maturity Scores bar graph (excluding Overall)
- `src/pdf_export.py`: Placeholder (optional)
- `src/styles.py`  
  - Shared styles: `TABLE_STYLE`, `CELL_STYLE`, `HEADER_STYLE`, `BOLD_CELL_STYLE`, `CARD_STYLE`
- `src/technical_overview.py`  
  - `create_maturity_card`, `create_technical_overview`
  - Handles Platform Maturity Results
- `src/utils.py`  
  - `read_file`, `parse_report_file`, `build_legend`, `extract_compliance_posture_from_report`
  - Parses `report.txt` for dashboard data, including Final Maturity Scores

---

## ⚙️ Setup

### ✅ Prerequisites
- Python 3.6 or later
- Input files (`final_report.md`, `combined_report.md`) in `data/`

### 🧪 Installation

```bash
# Optional: create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Dependencies:**
```
dash==2.17.1
plotly==5.22.0
```

---

## 📥 Input Files

Ensure you’ve placed your markdown files correctly:

```bash
mkdir -p data/output
# Place final_report.md and combined_report.md in data/
```

---

## ▶️ Running the Pipeline

### Full Pipeline (with Dashboard)

```bash
./run.sh
```

- Reads input markdown
- Extracts platform maturity, technical scores, critical risks, compliance posture, and final maturity scores
- Writes `report.txt`
- Launches the Dash server

### Extraction Only (No Dashboard)

```bash
./run_test_data_extraction.sh
```

- Same as above, but only generates `report.txt`

---

## 🌐 Accessing the Dashboard

Once the server starts, go to:

```
http://127.0.0.1:8050
```

You will see:
- **Business Overview**: Critical risks with titles, business impact, and solutions (Immediate, Short-term, Long-term), alongside a line graph of the Overall Maturity Score (Current, Target, and Decline percentages) with a legend indicating Current Score, Target Score, and Decline Score. The Overall Maturity Score section is fixed at 450px wide, with the Critical Risks section displayed side by side in the web view and wrapping to the next row in the PDF export if space is limited.
- **Operational Overview**: A table of technical focus area scores with summary statistics, compliance posture, and a bar graph of Final Maturity Scores (Viability, Success, Upkeep, Support; excluding Overall).
- **Technical Overview**: Platform maturity bar charts with legends.

---

## 📤 Output

### `data/output/report.txt` – Example

```
## Platform Maturity Results

Production-Ready Environment
Priority Level: 2
Personas: Operator
Previous Score: N/A
Current Score: 2
Target Score: 3
Findings: The environment has foundational production capabilities but requires enhancements in infrastructure resilience and deployment automation to achieve full operational readiness.

...

## Technical Focus Area Scores

Installation
Previous Score: N/A
Score: 1
Target Score: 2
Justification: Installation processes are partially automated but still rely on manual steps that can be error-prone.

...

## Critical Risks

Title: Insufficient Business Continuity and Disaster Recovery (BCDR) Planning
Business Impact: The absence of comprehensive BCDR strategies exposes the organization to prolonged outages and data loss in the event of critical failures. This can disrupt operations, erode customer trust, and result in significant financial losses due to downtime and recovery efforts.
Solution:
- Immediate: Develop and document a detailed disaster recovery plan outlining step-by-step recovery procedures and clearly assigning team responsibilities.
- Short-term: Implement automated and frequent backup mechanisms for all persistent storage and databases, and conduct routine restore tests to ensure backup reliability.
- Long-term: Establish failover procedures with regular stress-testing under various failure scenarios and integrate BCDR processes into the overall infrastructure management framework.

...

## Compliance Posture

Overall Compliance Score: 85%
Description: The platform demonstrates strong alignment with compliance expectations, particularly in areas such as Role-Based Access Control (RBAC), audit logging, and backup practices. Compliance frameworks are well-established, ensuring adherence to relevant regulatory standards. To maintain and enhance this posture, it is recommended to conduct regular internal assessments and external compliance reviews, continuously update data protection and security policies, and stay abreast of evolving regulatory requirements and industry best practices.

...

## Final Maturity Scores

Rubric: Viability
Current Percent: 50.0%
Target Percent: 65.0%

Rubric: Success
Current Percent: 40.0%
Target Percent: 55.0%

Rubric: Upkeep
Current Percent: 60.0%
Target Percent: 75.0%

Rubric: Support
Current Percent: 50.0%
Target Percent: 65.0%

Rubric: Overall
Current Percent: 52.5%
Target Percent: 67.5%
Decline Percent: 32.5%
```

---

## 🔧 Extending the Project

### ➕ Add New Extraction Logic

In `src/data_extraction.py`:
```python
def extract_custom_section(text):
    # Add parsing logic
    ...
```

Then update:
- `write_entry()` or create a new write function
- `platform_data` (if needed)
- `scripts/main.py` and `scripts/test_data_extraction.py` to call your function

### ➕ Parse More Critical Risk Fields

Modify `extract_critical_risks()` in `src/data_extraction.py`:
```python
pattern = re.compile(
    r'### \d+\. (.+?)\n\n'  # Title
    r'\*\*Business Impact:\*\*\s*\n(.+?)\n\n'
    r'\*\*Solution:\*\*\s*\n'
    r'- \*\*Immediate:\*\*\s*(.+?)\n'
    r'- \*\*Short-term:\*\*\s*(.+?)\n'
    r'- \*\*Long-term:\*\*\s*(.+?)\n',
    re.DOTALL
)
```

---

## 📊 Modify Chart Generation

In `src/chart_generation.py`:
```python
# Adjust Final Maturity Scores graph size
fig.update_layout(height=400, width=700)

# Modify colors for Final Maturity Scores
go.Bar(name="Current Percent", marker_color="#123456")  # New color
```

Update color logic in:
- `get_technical_color`
- `get_maturity_color`

---

## 🧱 Customize the Dashboard

The dashboard is constructed using Dash components across multiple modules to display the **Business Overview**, **Operational Overview**, and **Technical Overview** sections. Below are the key functions and their locations, along with examples of how to customize the styling and structure.

---

### 🔧 Key Functions and Their Roles

---

#### `create_critical_risk_card(risk, index)` (in `src/business_overview.py`)
Creates a card for each **Critical Risk**, displaying title, business impact, and solutions.

- Uses `html.Table`, `html.Tr`, and nested tables for the solution section
- Includes `pageBreakInside: "avoid"`

**Example customization:** Add a column to the solution table:
```python
html.Table([
    html.Tr([
        html.Td("- Immediate:", style={"width": "100px", "fontSize": "14px", "verticalAlign": "top", "paddingTop": "10px"}),
        html.Td(risk["solution"]["immediate"], style={"fontSize": "14px", "paddingTop": "10px"}),
        html.Td("New Column", style={"fontSize": "14px", "paddingTop": "10px"})  # Add new column
    ]),
    ...
])
```

---

#### `create_business_overview(critical_risks, final_maturity_scores=None)` (in `src/business_overview.py`)
Constructs the **Business Overview** section, displaying critical risk cards and a line graph of the Overall Maturity Score (Current, Target, and Decline percentages) with a legend below the graph. The Overall Maturity Score section is fixed at 450px wide for both web and PDF views, with the Critical Risks section taking the remaining space (wrapping to the next row in PDF if space is limited).

- Uses a flexbox layout to position the Overall Maturity Score graph to the left of the critical risk cards

**Example customization:** Adjust the graph width or spacing:
```python
html.Div(
    style={"display": "flex", "gap": "30px", "marginTop": "20px", "flexWrap": "wrap"},  # Increase gap
    children=[
        html.Div(
            [
                html.H3("Overall Maturity Score", style={"color": "#2a4e85", "marginBottom": "10px"}),
                dcc.Graph(
                    figure=generate_single_maturity_chart(overall_data, width=500),  # Adjust width
                    config={"displayModeBar": False},
                    style={"pageBreakInside": "avoid"}
                )
            ],
            style={"flex": "0 0 500px"}  # Match adjusted width
        ),
        html.Div(risk_elements, style={"flex": "1", "minWidth": "300px"})
    ]
)
```

---

#### `create_technical_table(technical_data)` (in `src/operational_overview.py`)
Creates a table for the **Technical Focus Area Scores** section, displaying platform readiness scores across multiple years (2024, 2025, 2026). The table includes rows for each technical item, summary rows for totals and percentages, a legend, and compliance posture.

- Uses `html.Table`, `html.Tr`, and `html.Td` to structure the table

**Example customization:** Add a new column:
```python
header_row = html.Tr([
    html.Th("Platform Readiness (Day 1 Essentials)", style=HEADER_STYLE),
    *[html.Th(year, style=HEADER_STYLE) for year in ["2024", "2025", "2026"]],
    html.Th("New Column", style=HEADER_STYLE)  # Add new column header
])

rows = [html.Tr([
    html.Td(item["title"], style=CELL_STYLE),
    html.Td("N/A" if item["prev_score_missing"] else str(item["scores"][0]), style={...}),
    html.Td(str(item["scores"][1]), style={...}),
    html.Td(str(item["scores"][2]), style={...}),
    html.Td("New Data", style=CELL_STYLE)  # Add new column data
]) for item in technical_data]
```

---

#### `create_operational_overview(technical_data, final_maturity_scores=None)` (in `src/operational_overview.py`)
Constructs the **Operational Overview** section, including the technical table, compliance posture, and a bar graph of Final Maturity Scores (Viability, Success, Upkeep, Support; excluding Overall).

**Example customization:** Add a new paragraph below the Final Maturity Scores graph:
```python
return [
    html.H1("Operational Overview", style={"color": "#2a4e85", "marginTop": "40px"}),
    create_technical_table(technical_data),
    html.Div([
        html.P([...], style={"marginTop": "20px"}),
        html.P([...], style={"marginTop": "10px"}),
        html.P("New Paragraph", style={"marginTop": "20px"})  # Add new paragraph
    ]),
    html.H3("Final Maturity Scores", style={"color": "#2a4e85", "marginTop": "20px"}),
    dcc.Graph(figure=generate_final_maturity_chart(final_maturity_scores), ...)
]
```

---

#### `create_maturity_card(title, priority_level, personas, chart_figure, findings_text)` (in `src/technical_overview.py`)
Creates a card for each **Platform Maturity Result**, displaying a title, priority level, personas, a bar chart (`dcc.Graph`), and findings text.

- Uses `html.Div` and `dcc.Graph`
- Includes `pageBreakInside: "avoid"` to prevent PDF page breaks

**Example customization:** Add a new field below the findings:
```python
html.Div([
    html.Div([
        html.Strong("Priority Level"), html.Br(),
        html.Span(str(priority_level)),
        ...
    ], style={"minWidth": "120px", "fontSize": "14px"}),

    dcc.Graph(
        figure=chart_figure,
        config={"displayModeBar": False},
        style={"flexBasis": "160px", "flexShrink": "0", "pageBreakInside": "avoid"}
    ),

    html.Div([
        html.Div(findings_text, style={"flexGrow": "1", "fontSize": "14px", "minWidth": "0"}),
        html.Div("New Field", style={"fontSize": "14px", "marginTop": "10px"})  # Add new field
    ])
])
```

---

#### `build_legend(legend_items, is_horizontal=True)` (in `src/utils.py`)
Builds a legend for maturity or technical score sections with colored labels.

- Used by `operational_overview.py` (for `TECHNICAL_LEGEND`) and `technical_overview.py` (for `MATURITY_RISK_LEVELS`)
- Uses `html.Div` for layout

**Example customization:** Add a new label to each item:
```python
html.Div([
    html.Div([
        html.Div(style={
            "width": "20px", "height": "20px", "backgroundColor": color,
            "border": "1px solid black", "display": "inline-block", "verticalAlign": "middle"
        }),
        html.Span(f" {label}", style={"fontSize": "12px", "marginLeft": "5px"}),
        html.Span("New Field", style={"fontSize": "12px", "marginLeft": "5px"})  # Add new field
    ])
    for label, color in legend_items
])
```

---

#### `create_technical_overview(maturity_data)` (in `src/technical_overview.py`)
Constructs the **Technical Overview** section, including platform maturity cards and legend.

**Example customization:** Add a new description:
```python
return [
    html.H1("Technical Overview", style={"color": "#2a4e85", "marginTop": "40px", "pageBreakBefore": "always"}),
    html.P("New Description", style={"marginTop": "10px"}),  # Add new description
    html.P("Provides a detailed analysis..."),
    ...
]
```

---

#### `create_dash_app(maturity_data, technical_data, critical_risks, final_maturity_scores)` (in `src/document_creation.py`)
Coordinates the full dashboard layout by combining section layouts from `business_overview.py`, `operational_overview.py`, and `technical_overview.py`.

**Example customization:** Add a new section:
```python
app.layout = html.Div(style={"fontFamily": "Arial", "padding": "40px"}, children=[
    *create_business_overview(critical_risks, final_maturity_scores),
    *create_operational_overview(technical_data, final_maturity_scores),
    *create_technical_overview(maturity_data),
    html.H1("New Section", style={"color": "#2a4e85", "marginTop": "40px"}),
    html.Div("New Section Content", style={"fontSize": "14px"})
])
```

---

## 🛠 Change File Paths or Config

In `src/config.py`:
```python
FINAL_REPORT_PATH = "data/custom_final_report.md"
```

---

## 📦 Add New Dependencies

```bash
pip install new-package
pip freeze > requirements.txt
```

---

## 🧪 Pass CLI Args via Shell

Update `run.sh` or `run_test_data_extraction.sh`:
```bash
python3 -m scripts.main --arg1 value
```

---

## 🧩 Troubleshooting

| Error                  | Fix                                                                 |
|------------------------|----------------------------------------------------------------------|
| `ModuleNotFoundError`  | Run from root with `python3 -m scripts.main`                         |
| `ImportError`          | Clear `__pycache__` (`rm -rf src/__pycache__ scripts/__pycache__`)   |
| `FileNotFoundError`    | Ensure markdown files exist and `data/output/` is writable           |
| Dash won't start       | Check if `dash` and `plotly` are installed; verify port 8050 is free |
| No critical risks      | Ensure section headers are correct in markdown files                 |
| Missing report sections| Verify `combined_report.md` format; check console for extraction errors|
| PDF export issues      | Ensure the viewport in `export_pdf.py` is set to A4 dimensions (595x842 pixels); verify Plotly graph widths match container widths (e.g., 450px for Overall Maturity Score section).|

---

## 🔮 Future Enhancements

- Word Document Export (`python-docx`)
- Integrated PDF Export (`pdf_export.py`)
- Add Unit Tests (`tests/` directory)
- CLI Flags (e.g., `--port`, `--output-dir`)

---

## 🧑‍💻 Contributing

Pull requests and feature suggestions are welcome! Open an issue to discuss improvements.

