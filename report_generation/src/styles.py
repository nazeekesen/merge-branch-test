# Shared styles for reusability
TABLE_STYLE = {"width": "100%", "borderCollapse": "collapse", "marginBottom": "20px"}
CELL_STYLE = {"border": "1px solid #ddd", "padding": "8px"}
HEADER_STYLE = {"border": "1px solid #ddd", "padding": "8px", "backgroundColor": "#f0f0f0"}
BOLD_CELL_STYLE = {**CELL_STYLE, "fontWeight": "bold"}
CARD_STYLE = {
    "marginBottom": "20px",
    "border": "2px solid #000",  # Solid border around each risk entry
    "padding": "10px",
    "pageBreakInside": "avoid",  # Prevent page breaks inside cards
}
