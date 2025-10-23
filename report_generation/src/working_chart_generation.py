import plotly.graph_objects as go
from datetime import datetime
import math

# Chart labels
MULTILINE_LABELS = ["JULY<br>2024<br>(PREVIOUS)", "JAN<br>2025<br>(CURRENT)", "JAN<br>2026<br>(TARGET)"]

def get_technical_color(score):
    """Return color for Technical Focus Area Scores (0-2)."""
    return {0: "#FF9999", 1: "#CCFFCC", 2: "#99CC99"}.get(score, "grey")

def get_maturity_color(score):
    """Return color for Platform Maturity Scores (1-5), rounding floats to nearest integer."""
    rounded_score = min(max(round(float(score)), 1), 5)  # Round to nearest int, clamp to 1-5
    return {1: "#FF0000", 2: "#FF6200", 3: "#E0B020", 4: "#A9D6A9", 5: "#1E6B22"}.get(rounded_score, "grey")

# Legends
TECHNICAL_LEGEND = [
    ("2: Compliant/Completed", get_technical_color(2)),
    ("1: OK", get_technical_color(1)),
    ("0: Needs Improvement", get_technical_color(0))
]
MATURITY_RISK_LEVELS = [
    ("Critical Risk", get_maturity_color(1)),
    ("High Risk", get_maturity_color(2)),
    ("Moderate Risk", get_maturity_color(3)),
    ("Low Risk", get_maturity_color(4)),
    ("Minimal Risk", get_maturity_color(5))
]

def generate_chart(scores, prev_score_missing=False):
    """Generate a bar chart for Platform Maturity scores."""
    colors = ["#CCCCCC" if prev_score_missing else get_maturity_color(scores[0]), get_maturity_color(scores[1]), get_maturity_color(scores[2])]
    display_scores = ["N/A" if prev_score_missing else scores[0], scores[1], scores[2]]
    plotted_scores = [0 if prev_score_missing else scores[0], scores[1], scores[2]]

    x_vals = list(range(len(MULTILINE_LABELS)))
    fig = go.Figure(data=[
        go.Bar(x=x_vals, y=plotted_scores, marker_color=colors, text=display_scores,
               textposition="inside", textfont=dict(color="white", size=12), width=0.3)
    ])
    fig.update_layout(
        height=260, width=420, margin=dict(l=10, r=10, t=30, b=40),
        yaxis=dict(range=[0, 5], tick0=1, dtick=1, showgrid=False, fixedrange=True),
        xaxis=dict(tickangle=0, tickmode="array", tickvals=x_vals, ticktext=MULTILINE_LABELS),
        bargap=0.1, plot_bgcolor="white", paper_bgcolor="white"
    )
    return fig

def generate_final_maturity_chart(final_maturity_scores):
    """Generate a bar chart for Final Maturity Scores with Current and Target percentages."""
    rubrics = [score["rubric"] for score in final_maturity_scores]
    current_percents = [score["current_percent"] for score in final_maturity_scores]
    target_percents = [score["target_percent"] for score in final_maturity_scores]

    fig = go.Figure(data=[
        go.Bar(
            name="Current Percent",
            x=rubrics,
            y=current_percents,
            marker_color="#2a4e85",  # Dark blue for Current
            text=[f"{p:.1f}%" for p in current_percents],
            textposition="inside",
            textfont=dict(color="white", size=12)
        ),
        go.Bar(
            name="Target Percent",
            x=rubrics,
            y=target_percents,
            marker_color="#6b9ad9",  # Lighter blue for Target
            text=[f"{p:.1f}%" for p in target_percents],
            textposition="inside",
            textfont=dict(color="white", size=12)
        )
    ])

    fig.update_layout(
        height=300,
        width=600,
        margin=dict(l=20, r=20, t=50, b=100),
        yaxis=dict(
            title="Percentage (%)",
            range=[0, 100],
            tick0=0,
            dtick=10,
            showgrid=True,
            gridcolor="#ddd",
            fixedrange=True
        ),
        barmode="group",
        bargap=0.2,
        plot_bgcolor="white",
        paper_bgcolor="white",
        title="Final Maturity Scores",
        title_x=0.5,
        legend=dict(
            x=0.5,
            y=-0.3,
            xanchor="center",
            yanchor="top",
            orientation="h"
        )
    )

    return fig

def get_current_quarter_and_target():
    """Determine the current quarter and target quarter (one year later) based on the current date."""
    current_date = datetime.now()  # Current date: May 19, 2025
    year = current_date.year  # 2025
    month = current_date.month  # 5 (May)

    # Determine the current quarter based on the month
    if 1 <= month <= 3:
        current_quarter = "Q1"
    elif 4 <= month <= 6:
        current_quarter = "Q2"
    elif 7 <= month <= 9:
        current_quarter = "Q3"
    else:
        current_quarter = "Q4"

    # Current quarter label
    current_quarter_label = f"{current_quarter} {year}"  # e.g., "Q2 2025"

    # Target quarter is one year later, same quarter
    target_year = year + 1  # 2026
    target_quarter_label = f"{current_quarter} {target_year}"  # e.g., "Q2 2026"

    return current_quarter_label, target_quarter_label

def generate_single_maturity_chart(rubric_data, width=450):
    """Generate a line chart for a single Final Maturity Score rubric (e.g., Overall) with lines for Target and Decline."""
    rubric = rubric_data["rubric"]
    current_percent = rubric_data["current_percent"]
    target_percent = rubric_data["target_percent"]
    decline_percent = rubric_data.get("decline_percent")  # May be None for non-Overall rubrics

    # Get current and target quarters dynamically
    current_quarter, target_quarter = get_current_quarter_and_target()
    quarters = [current_quarter, target_quarter]  # e.g., ["Q2 2025", "Q2 2026"]

    fig = go.Figure()

    # Line from Current to Target
    fig.add_trace(go.Scatter(
        x=quarters,
        y=[current_percent, target_percent],
        mode='lines+markers+text',
        name='Target Score',
        line=dict(color='#2a4e85', width=2),
        marker=dict(
            size=6,
            color=['#2a4e85', '#6b9ad9'],  # Dark blue for Current, lighter blue for Target
            line=dict(width=1, color="black")
        ),
        text=[f"{current_percent:.1f}%", f"{target_percent:.1f}%"],
        textposition="top center",
        textfont=dict(size=10)
    ))

    # Line from Current to Decline (only for Overall rubric)
    if decline_percent is not None:
        fig.add_trace(go.Scatter(
            x=quarters,
            y=[current_percent, decline_percent],
            mode='lines+markers+text',
            name='Decline Score',
            line=dict(color='#FF0000', dash='dash', width=2),
            marker=dict(
                size=6,
                color=['#2a4e85', '#FF0000'],  # Dark blue for Current, red for Decline
                line=dict(width=1, color="black")
            ),
            text=["", f"{decline_percent:.1f}%"],  # Label only at the Decline point
            textposition="top center",
            textfont=dict(size=10)
        ))

    fig.update_layout(
        height=200,
        width=width,  # Fixed width for both web and PDF
        margin=dict(l=10, r=10, t=10, b=30),
        yaxis=dict(
            title="Percentage (%)",
            range=[0, 100],
            tick0=0,
            dtick=20,
            showgrid=True,
            gridcolor="#ddd",
            fixedrange=True,
            titlefont=dict(size=8),
            tickfont=dict(size=6)
        ),
        xaxis=dict(
            title="Time Period",
            showgrid=False,
            tickvals=quarters,
            ticktext=quarters,
            titlefont=dict(size=8),
            tickfont=dict(size=6)
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        title=f"{rubric} Maturity Score",
        title_x=0.5,
        titlefont=dict(size=10),
        showlegend=False  # Hide default legend; score band acts as legend
    )

    return fig
