"""
Components for displaying headers in the Sanctions Dashboard.
"""

from dash import html
from config import COLOURS, HEADER_STYLE


def create_header():
    """
    Create the dashboard header.

    Returns:
        dash component: The confidence level controls
    """
    return html.Div(
        [
            html.H1("Sanctions Risk Management Dashboard", style=HEADER_STYLE),
            html.P(
                "Analysis of transaction risk exposure to sanctioned countries",
                style={"textAlign": "center", "color": COLOURS["subheader_text"]},
            ),
        ]
    )
