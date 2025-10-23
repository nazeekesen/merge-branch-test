from dash import html, dcc
from src.styles import CARD_STYLE
from src.chart_generation import generate_single_maturity_chart

def create_critical_risk_card(risk, index):
    """Create a card for Critical Risks with title, business impact, and solutions, using a table layout for consistent alignment."""
    return html.Div(style={**CARD_STYLE, "marginBottom": "30px"}, children=[
        # Title
        html.H4(f"{index + 1}. {risk['title']}", style={"color": "#2a4e85", "marginBottom": "10px", "borderBottom": "2px solid #000", "paddingBottom": "5px"}),
        # Table for Business Impact and Solution
        html.Table(style={"width": "100%", "borderCollapse": "collapse", "marginBottom": "15px"}, children=[
            # Business Impact Row
            html.Tr([
                html.Td(html.Strong("Business Impact:"), style={"width": "150px", "fontSize": "14px", "verticalAlign": "top"}),
                html.Td(risk["business_impact"], style={"fontSize": "14px"})
            ], style={"borderBottom": "2px solid #000"}),
            # Solution Row with Nested Table
            html.Tr([
                html.Td(html.Strong("Solution:"), style={"width": "150px", "fontSize": "14px", "verticalAlign": "top", "paddingTop": "10px"}),
                html.Td(
                    html.Table(style={"width": "100%", "borderCollapse": "collapse"}, children=[
                        html.Tr([
                            html.Td("- Immediate:", style={"width": "100px", "fontSize": "14px", "verticalAlign": "top", "paddingTop": "10px"}),
                            html.Td(risk["solution"]["immediate"], style={"fontSize": "14px", "paddingTop": "10px"})
                        ]),
                        html.Tr([
                            html.Td("- Short-term:", style={"width": "100px", "fontSize": "14px", "verticalAlign": "top"}),
                            html.Td(risk["solution"]["short_term"], style={"fontSize": "14px"})
                        ]),
                        html.Tr([
                            html.Td("- Long-term:", style={"width": "100px", "fontSize": "14px", "verticalAlign": "top"}),
                            html.Td(risk["solution"]["long_term"], style={"fontSize": "14px"})
                        ]),
                    ])
                )
            ]),
        ]),
    ])

def create_score_band(current_score):
    """Create a horizontal score band legend for the Overall Maturity Score."""
    bands = [
        {"label": "0-25\nCritical", "color": "#B22222", "range": (0, 25)},
        {"label": "25-50\nVery Low", "color": "#FF8C00", "range": (25, 50)},
        {"label": "50-75\nLow", "color": "#FFD700", "range": (50, 75)},
        {"label": "75+\nGood", "color": "#228B22", "range": (75, 100)}
    ]

    band_divs = []
    for band in bands:
        width = band["range"][1] - band["range"][0]
        band_divs.append(html.Div(className="score-band-label", style={
            "flexBasis": f"{width}%",
            "backgroundColor": band["color"],
            "textAlign": "center",
            "color": "white",
            "fontSize": "12px",
            "padding": "5px"
        }, children=band["label"]))

    score_text = html.Div([
        html.Div("Overall Maturity Score", style={
            "textAlign": "center",
            "fontWeight": "bold",
            "fontSize": "20px",
            "lineHeight": "1"
        }),
        html.Div(f"{current_score:.0f}%", style={
            "textAlign": "center",
            "fontWeight": "bold",
            "fontSize": "20px",
            "lineHeight": "1",
            "marginTop": "5px"
        })
    ], className="score-band-text", style={
        "marginBottom": "5px"
    })

    return html.Div([
        score_text,
        html.Div(style={"display": "flex", "position": "relative"}, children=band_divs)
    ], style={"marginBottom": "10px"})

def create_point_legend():
    """Create a legend for the Overall Maturity Score line chart points."""
    legend_items = [
        ("Current Score", "#2a4e85"),  # Dark blue for Current
        ("Target Score", "#6b9ad9"),   # Lighter blue for Target
        ("Decline Score", "#FF0000")   # Red for Decline
    ]

    return html.Div(
        style={
            "display": "flex",
            "flexWrap": "nowrap",
            "gap": "20px",
            "justifyContent": "center",
            "marginTop": "10px"
        },
        children=[
            html.Div([
                html.Div(style={
                    "width": "12px",
                    "height": "12px",
                    "backgroundColor": color,
                    "border": "1px solid black",
                    "display": "inline-block",
                    "verticalAlign": "middle",
                    "borderRadius": "50%"
                }),
                html.Span(f" {label}", className="point-legend-label", style={"fontSize": "12px", "marginLeft": "8px"})
            ])
            for label, color in legend_items
        ]
    )

def create_business_overview(critical_risks, final_maturity_scores=None):
    """Generate the Business Overview section layout with Overall Maturity Score graph and score band."""
    # Find the Overall rubric data
    overall_data = next((score for score in final_maturity_scores if score["rubric"] == "Overall"), None) if final_maturity_scores else None

    # Create critical risk cards with spacing
    risk_elements = []
    for index, risk in enumerate(critical_risks):
        risk_elements.append(create_critical_risk_card(risk, index))
        if index < len(critical_risks) - 1:  # Add spacing instead of HR
            risk_elements.append(html.Div(style={"height": "20px"}))

    # Create the layout
    content = [
        html.H1("Business Overview", style={"color": "#2a4e85", "marginTop": "40px"}),
    ]

    if overall_data:
        content.append(
            html.Div(
                className="flex-container",
                style={"display": "flex", "gap": "20px", "marginTop": "20px", "flexWrap": "wrap"},
                children=[
                    # Overall Maturity Score graph and score band
                    html.Div(
                        className="graph-section",
                        style={"flex": "0 0 450px"},
                        children=[
                            html.H2("Maturity Score", style={"color": "#2a4e85", "marginBottom": "10px"}),
                            create_score_band(overall_data["current_percent"]),
                            dcc.Graph(
                                figure=generate_single_maturity_chart(overall_data, width=450),
                                config={"displayModeBar": False},
                                style={"pageBreakInside": "avoid"}
                            ),
                            create_point_legend()
                        ]
                    ),
                    # Risk cards with title above
                    html.Div(
                        className="risk-cards-section",
                        style={"flex": "1", "minWidth": "145px"},
                        children=[
                            html.H2("Issues and Business Impact", style={"color": "#2a4e85", "marginBottom": "10px"}),
                            html.Div(risk_elements)
                        ]
                    )
                ]
            )
        )
    else:
        content.append(
            html.Div(
                [
                    html.H2("Issues and Business Impact", style={"color": "#2a4e85", "marginTop": "20px"}),
                    html.Div(risk_elements)
                ]
            )
        )

    return content
