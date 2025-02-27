"""
Components for displaying headers in the Sanctions Dashboard.
"""

from dash import html
import dash_bootstrap_components as dbc
from config import COLOURS, HEADER_STYLE


def create_header():
    """
    Create the dashboard header.

    Returns:
        dash component: The confidence level controls
    """
    return dbc.Row(
        [
            dbc.Col([
            html.H1("Sanctions Risk Analysis Dashboard", className="text-center my-4"),
            html.Hr(),
            html.P(
                "Analysis of transaction risk exposure to sanctioned countries",
                style={"textAlign": "center", "color": COLOURS["subheader_text"]},
            ),
        ], width=12)
        ]
    )
