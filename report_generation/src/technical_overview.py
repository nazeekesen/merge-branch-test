from dash import html, dcc
from src.utils import build_legend
from src.chart_generation import generate_chart, MATURITY_RISK_LEVELS
from src.styles import CARD_STYLE

def create_maturity_card(title, priority_level, personas, chart_figure, findings_text):
    """Create a card for Technical Overview with a bar chart."""
    return html.Div(style={**CARD_STYLE, "marginBottom": "30px"}, children=[
        html.H3(title, style={"color": "#2a4e85"}),
        html.Div(style={"display": "flex", "gap": "30px", "flexWrap": "nowrap"}, children=[
            html.Div([
                html.Strong("Priority Level"), html.Br(), html.Span(str(priority_level)), html.Br(), html.Br(),
                html.Strong("Personas"), html.Br(), html.Span(personas)
            ], style={"minWidth": "120px", "fontSize": "14px"}),
            dcc.Graph(figure=chart_figure, config={"displayModeBar": False}, style={"flexBasis": "160px", "flexShrink": "0", "pageBreakInside": "avoid"}),
            html.Div(findings_text, style={"flexGrow": "1", "fontSize": "14px", "minWidth": "0"})
        ])
    ])

def create_technical_overview(maturity_data):
    """Generate the Technical Overview section layout."""
    return [
        html.H1("Technical Overview", style={"color": "#2a4e85", "marginTop": "40px", "pageBreakBefore": "always"}),
        html.P("Provides a detailed analysis of the Kubernetes infrastructure’s maturity and security posture."),
        html.P("Priority Score (N/A or 1–3): Indicates urgency for each Persona, or N/A if not specified."),
        html.P("Bar Graph (1–5): Assesses core areas using 360 Cloud Platforms’ proprietary rubric to guide evaluation and action."),
        html.Div(style={"marginBottom": "20px"}),
        build_legend(MATURITY_RISK_LEVELS, is_horizontal=True),
        html.H2("Technical Overview Results", style={"marginTop": "40px"}),
        *[create_maturity_card(
            item["title"],
            item["priority"],
            item["personas"],
            generate_chart(item["scores"], item["prev_score_missing"]),
            item["findings"]
        ) for item in maturity_data]
    ]
