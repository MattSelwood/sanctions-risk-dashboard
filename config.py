"""
Configuration settings for the Sanctions Dashboard.
"""

# Random seed
RANDOM_SEED = 1337

# Application settings
DEBUG = True
DEFAULT_CONFIDENCE = 0.95
DEFAULT_SAMPLE_SIZE = 5000

# Colour scheme
COLOURS = {
    "historical_var": "#e74c3c",
    "parametric_var": "#e67e22",
    "monte_carlo_var": "#f39c12",
    "expected_shortfall": "#c0392b",
    "header_text": "#2c3e50",
    "subheader_text": "#7f8c8d",
    "header_bg": "#2c3e50",
    "header_text_color": "white",
    "odd_row_bg": "#f9f9f9",
    "high_amount_bg": "#f8d7da",
    "high_amount_text": "#721c24",
    "button_bg": "#3498db",
    "incoming": "#2ecc71",
    "outgoing": "#e74c3c",
}

# Component styling
BUTTON_STYLE = {
    "backgroundColor": COLOURS["button_bg"],
    "color": "white",
    "border": "none",
    "padding": "10px 20px",
    "borderRadius": "5px",
    "cursor": "pointer",
    "marginBottom": "20px",
    "marginLeft": "10px",
}

HEADER_STYLE = {
    "textAlign": "center",
    "color": COLOURS["header_text"],
    "padding": "20px",
}

SECTION_HEADER_STYLE = {"color": COLOURS["header_text"], "padding": "10px"}
