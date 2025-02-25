"""
Components for displaying risk metrics in the Sanctions Dashboard.
"""

from dash import html, dcc
from config import COLOURS, SECTION_HEADER_STYLE, BUTTON_STYLE


def create_confidence_controls(default_confidence):
    """
    Create controls for adjusting VaR confidence level.

    Args:
        default_confidence (float): Default confidence level value

    Returns:
        dash component: The confidence level controls
    """
    return html.Div(
        [
            html.H3("Key Risk Metrics", style=SECTION_HEADER_STYLE),
            html.Div(
                [
                    html.Label("VaR Confidence Level:"),
                    dcc.Slider(
                        id="var-confidence-slider",
                        min=0.9,
                        max=0.995,
                        step=0.005,
                        value=default_confidence,
                        marks={i / 100: f"{i}%" for i in range(90, 100, 2)},
                        tooltip={"placement": "bottom", "always_visible": True},
                    ),
                ],
                style={"marginBottom": "20px", "padding": "10px"},
            ),
            html.Button(
                "Update Risk Metrics", id="update-metrics-button", style=BUTTON_STYLE
            ),
        ],
        className="row",
    )


def create_metric_box(title, value, color, confidence_level):
    """
    Create a single metric display box.

    Args:
        title (str): Title of the metric
        value (float): Value of the metric
        color (str): Color code for the value
        confidence_level (float): Confidence level for the metric

    Returns:
        dash component: The metric box component
    """
    return html.Div(
        [
            html.Div(
                [
                    html.H4(
                        f"{title} ({confidence_level*100:.0f}%)",
                        style={"textAlign": "center"},
                    ),
                    html.H2(
                        f"${value:,.2f}", style={"textAlign": "center", "color": color}
                    ),
                ],
                className="metric-box",
            )
        ],
        className="three columns",
    )


def create_metrics_display(risk_metrics, confidence_level):
    """
    Create the metrics display section with all metric boxes.

    Args:
        risk_metrics (DataFrame): DataFrame containing risk metrics
        confidence_level (float): Confidence level for the metrics

    Returns:
        dash component: The metrics display section
    """
    return html.Div(
        [
            create_metric_box(
                "Historical VaR",
                risk_metrics.loc[0, "Value"],
                COLOURS["historical_var"],
                confidence_level,
            ),
            create_metric_box(
                "Parametric VaR",
                risk_metrics.loc[1, "Value"],
                COLOURS["parametric_var"],
                confidence_level,
            ),
            create_metric_box(
                "Monte Carlo VaR",
                risk_metrics.loc[2, "Value"],
                COLOURS["monte_carlo_var"],
                confidence_level,
            ),
            create_metric_box(
                "Expected Shortfall",
                risk_metrics.loc[3, "Value"],
                COLOURS["expected_shortfall"],
                confidence_level,
            ),
        ],
        id="metrics-container",
        className="row",
    )


def create_risk_metrics_section(initial_report, default_confidence):
    """
    Create the complete risk metrics section.

    Args:
        initial_report (dict): Dictionary containing initial risk report data
        default_confidence (float): Default confidence level

    Returns:
        dash component: The complete risk metrics section
    """
    return html.Div(
        [
            create_confidence_controls(default_confidence),
            create_metrics_display(initial_report["risk_metrics"], default_confidence),
        ],
        className="row section",
    )
