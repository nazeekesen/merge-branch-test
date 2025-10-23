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
                        margin-top: 40px; /* Add top margin to each page */
                        margin-bottom: 40px;
                        margin-left: 40px;
                        margin-right: 40px;
                    }
                    hr { display: none; } /* Hide horizontal lines in PDF */
                    div { page-break-inside: avoid; } /* Prevent page breaks inside divs */
                    .graph-container { page-break-inside: avoid; page-break-after: auto; } /* Prevent page breaks inside graphs */
                    h1, h2 { page-break-before: auto; page-break-after: avoid; } /* Control breaks around headings */
                    .section-break { page-break-before: always; } /* Force page break before major sections */
                    body {
                        margin: 0; /* Ensure no additional body margin overrides @page */
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

    app.layout = html.Div(style={"fontFamily": "Arial", "padding": "40px"}, children=[
        *create_business_overview(critical_risks),
        *create_operational_overview(technical_data, final_maturity_scores),
        *create_technical_overview(maturity_data)
    ])
    return app
