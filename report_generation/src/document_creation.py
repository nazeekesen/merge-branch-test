import dash
from dash import html
from src.styles import TABLE_STYLE, CELL_STYLE, HEADER_STYLE, BOLD_CELL_STYLE, CARD_STYLE
from src.business_overview import create_business_overview
from src.operational_overview import create_operational_overview
from src.technical_overview import create_technical_overview
from src.utils import read_file

def create_dash_app(maturity_data, technical_data, critical_risks, final_maturity_scores):
    app = dash.Dash(__name__, use_pages=False)
    app.index_string = '''
    <!DOCTYPE html>
    <html>
        <head>
            {%metas%}
            <title>{%title%}</title>
            {%favicon%}
            {%css%}
            <style>
                .dash-pages-nav-button { display: none !important; }
                @media print {
                    @page {
                        margin-top: 20px;
                        margin-bottom: 20px;
                        margin-left: 20px;
                        margin-right: 20px;
                    }
                    hr { display: none; }
                    div { page-break-inside: avoid; }
                    .graph-container { page-break-inside: avoid; page-break-after: auto; }
                    h1, h2 { page-break-before: auto; page-break-after: avoid; }
                    .section-break { page-break-before: always; }
                    body {
                        margin: 0;
                        width: 100%;
                    }
                    /* Adjust flexbox layout for A4 width */
                    .flex-container {
                        display: flex;
                        flex-wrap: wrap;
                        width: 100%;
                        gap: 10px;
                    }
                    .graph-section {
                        flex: 0 0 450px !important;  /* Match web width */
                        min-width: 450px !important;
                    }
                    .risk-cards-section {
                        flex: 1;
                        min-width: 145px !important;
                    }
                    dcc-graph {
                        width: 100% !important;
                        max-width: 100% !important;
                    }
                    /* Ensure Plotly graph container scales */
                    .js-plotly-plot .plotly {
                        width: 100% !important;
                        max-width: 100% !important;
                        height: auto !important;
                    }
                    .js-plotly-plot .plot-container {
                        width: 100% !important;
                        max-width: 100% !important;
                    }
                    .js-plotly-plot .main-svg {
                        width: 100% !important;
                        max-width: 100% !important;
                    }
                    /* Reduce font sizes for better fit */
                    h2 {
                        font-size: 14px !important;
                    }
                    .score-band-text {
                        font-size: 12px !important;
                    }
                    .score-band-label {
                        font-size: 8px !important;
                    }
                    .point-legend-label {
                        font-size: 8px !important;
                    }
                }
            </style>
        </head>
        <body>
            {%app_entry%}
            <footer>
                {%config%}
                {%scripts%}
                {%renderer%}
            </footer>
        </body>
    </html>
    '''

    app.layout = html.Div(style={"fontFamily": "Arial", "padding": "20px"}, children=[
        *create_business_overview(critical_risks, final_maturity_scores),
        *create_operational_overview(technical_data, final_maturity_scores),
        *create_technical_overview(maturity_data)
    ])
    return app
