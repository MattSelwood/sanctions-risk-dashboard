"""
Components for displaying charts in the Sanctions Dashboard.
"""

from dash import html, dcc
import plotly.express as px
from config import SECTION_HEADER_STYLE


def create_country_exposure_chart(country_exposure_data):
    """
    Create the country exposure chart.

    Args:
        country_exposure_data (DataFrame): DataFrame containing country exposure data
        
    Returns:
        dash component: The country exposure chart
    """
    return html.Div(
        [
            html.H3("Country Exposure Analysis", style=SECTION_HEADER_STYLE),
            dcc.Graph(
                id="country-exposure-chart",
                figure=px.bar(
                    country_exposure_data.sort_values("Total", ascending=False),
                    x="Country",
                    y=["Incoming", "Outgoing"],
                    title="Exposure by Country",
                    labels={"value": "Transaction Amount ($)", "variable": "Direction"},
                    barmode="group",
                    color_discrete_map={"Incoming": "#2ecc71", "Outgoing": "#e74c3c"},
                ),
            ),
        ],
        className="six columns",
    )


def create_time_series_chart(time_series_data):
    """
    Create the time series chart.

    Args:
        time_series_data (DataFrame): DataFrame containing time series data
        
    Returns:
        dash component: The time series chart
    """
    return html.Div(
        [
            html.H3("Transaction Volume Over Time", style=SECTION_HEADER_STYLE),
            dcc.Graph(
                id="time-series-chart",
                figure=px.line(
                    time_series_data,
                    x="date",
                    y=["amount", "sanctions_exposure"],
                    title="Daily Transaction Volume",
                    labels={"value": "Amount ($)", "variable": "Type"},
                    color_discrete_map={
                        "amount": "#2ecc71",
                        "sanctions_exposure": "#e74c3c",
                    },
                ),
            ),
        ],
        className="six columns",
    )


def create_charts_section(initial_report):
    """Create the charts section with country exposure and time series"""
    return html.Div(
        [
            create_country_exposure_chart(initial_report["country_exposure"]),
            create_time_series_chart(initial_report["time_series"]),
        ],
        className="row section",
    )
