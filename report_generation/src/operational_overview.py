from dash import html, dcc
from src.styles import TABLE_STYLE, CELL_STYLE, HEADER_STYLE, BOLD_CELL_STYLE
from src.utils import build_legend, extract_compliance_posture_from_report
from src.chart_generation import get_technical_color, TECHNICAL_LEGEND, generate_final_maturity_chart

def create_technical_table(technical_data):
    """Create a table for Technical Focus Area Scores with summary rows and compliance posture."""
    total_max = len(technical_data) * 2
    scores = [[item["scores"][i] for item in technical_data] for i in range(3)]
    totals = [sum(score) for score in scores]
    percents = [(total / total_max) * 100 if total_max > 0 else 0 for total in totals]
    # Calculate differences between consecutive years
    diffs = [0]  # 2024 has no previous year, so difference is 0
    for i in range(1, len(percents)):
        diff = percents[i] - percents[i-1]
        diffs.append(diff)

    header_row = html.Tr([
        html.Th("Platform Readiness (Day 1 Essentials)", style=HEADER_STYLE),
        *[html.Th(year, style=HEADER_STYLE) for year in ["2024", "2025", "2026"]]
    ])

    rows = [html.Tr([
        html.Td(item["title"], style=CELL_STYLE),
        html.Td("N/A" if item["prev_score_missing"] else str(item["scores"][0]), style={
            **CELL_STYLE, "backgroundColor": get_technical_color(item["scores"][0]) if not item["prev_score_missing"] else "white"}),
        html.Td(str(item["scores"][1]), style={**CELL_STYLE, "backgroundColor": get_technical_color(item["scores"][1])}),
        html.Td(str(item["scores"][2]), style={**CELL_STYLE, "backgroundColor": get_technical_color(item["scores"][2])})
    ]) for item in technical_data]

    summary_rows = [
        html.Tr([html.Td("TOTAL", style=BOLD_CELL_STYLE), *[html.Td(str(total), style=CELL_STYLE) for total in totals]]),
        html.Tr([html.Td("MAXIMUM", style=BOLD_CELL_STYLE), *[html.Td(str(total_max), style=CELL_STYLE) for _ in range(3)]]),
        html.Tr([
            html.Td("DIFFERENCE (PERCENTAGE)", style=BOLD_CELL_STYLE),
            html.Td("0", style=CELL_STYLE),  # 2024 difference
            html.Td(f"+{diffs[1]:.2f}" if diffs[1] > 0 else str(diffs[1]), style={**CELL_STYLE, "backgroundColor": "#CCFFCC" if diffs[1] > 0 else "white"}),
            html.Td(f"+{diffs[2]:.2f}" if diffs[2] > 0 else str(diffs[2]), style={**CELL_STYLE, "backgroundColor": "#CCFFCC" if diffs[2] > 0 else "white"})
        ]),
        html.Tr([
            html.Td("TOTAL (PERCENTAGE)", style={**BOLD_CELL_STYLE, "backgroundColor": "#FFFFCC"}),
            html.Td(f"{percents[0]:.0f}", style={**CELL_STYLE, "backgroundColor": "#FFFFCC"}),
            html.Td(f"{percents[1]:.1f}", style={**CELL_STYLE, "backgroundColor": "#FFFFCC"}),
            html.Td(f"{percents[2]:.0f}", style={**CELL_STYLE, "backgroundColor": "#FFFFCC"})
        ])
    ]

    # Extract compliance posture from report.txt
    compliance_posture = extract_compliance_posture_from_report()

    # Build the compliance posture display
    compliance_display = []
    if compliance_posture:
        compliance_display = [
            html.Div(style={"display": "flex", "alignItems": "center", "marginTop": "20px", "pageBreakInside": "avoid"}, children=[
                # Square box with the score
                html.Div(
                    html.Span(compliance_posture["score"], style={"fontSize": "24px", "fontWeight": "bold"}),
                    style={
                        "width": "150px",
                        "height": "100px",
                        "backgroundColor": "#c3e0e8",
                        "border": "1px solid #ddd",
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "center",
                        "marginRight": "20px"
                    }
                ),
                # Description next to the box
                html.Div([
                    html.Strong("Overall Compliance Score"),
                    html.Br(),
                    html.Span(compliance_posture["description"], style={"fontSize": "14px"})
                ], style={"flexGrow": "1"})
            ])
        ]

    return html.Div([
        html.Table(style=TABLE_STYLE, children=[header_row] + rows + summary_rows),
        build_legend(TECHNICAL_LEGEND, is_horizontal=True),
        *compliance_display  # Add the compliance posture display below the table and legend
    ])

def create_operational_overview(technical_data, final_maturity_scores=None):
    """Generate the Operational Overview section layout."""
    # Filter out the Overall rubric from final_maturity_scores
    filtered_maturity_scores = [score for score in final_maturity_scores if score["rubric"] != "Overall"] if final_maturity_scores else []

    final_maturity_graph = []
    if filtered_maturity_scores:
        final_maturity_graph = [
            html.H3("Final Maturity Scores", style={"color": "#2a4e85", "marginTop": "20px"}),
            dcc.Graph(
                figure=generate_final_maturity_chart(filtered_maturity_scores),
                config={"displayModeBar": False},
                style={"marginTop": "10px", "pageBreakInside": "avoid"}
            )
        ]

    return [
        html.H1("Operational Overview", style={"color": "#2a4e85", "marginTop": "40px"}),
        create_technical_table(technical_data),
        html.Div([
            html.P([
                html.Strong("Platform Maturity:"),
                html.Span(" Evaluates the maturity of each rubric criteria by assessing security, automation, and operational readiness.")
            ], style={"marginTop": "20px"}),
            html.P([
                html.Strong("Platform Readiness:"),
                html.Span(" Verifies essential components in production deployments are present, correctly configured, and optimized. Also ensures autoscaling, monitoring, and logging tools are in place before Kubernetes deployment go-live.")
            ], style={"marginTop": "10px"})
        ]),
        *final_maturity_graph  # Add the filtered final maturity scores graph
    ]
