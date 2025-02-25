"""
Callbacks for risk metrics in the Sanctions Dashboard.
"""

from dash.dependencies import Input, Output, State
from components.metrics import create_metrics_display


def register_metrics_callbacks(app, risk_analyser):
    """
    Register callbacks related to risk metrics.

    Args:
        app (Dash): The Dash app instance
        risk_analyser (SanctionsRiskAnalyser): The risk analyser instance
    """

    @app.callback(
        Output("metrics-container", "children"),
        [Input("update-metrics-button", "n_clicks")],
        [State("var-confidence-slider", "value")],
        prevent_initial_call=True,
    )
    def update_risk_metrics(n_clicks, confidence_level):
        """
        Update risk metrics based on new confidence level.

        Args:
            n_clicks (int): Number of button clicks
            confidence_level (float): Selected confidence level

        Returns:
            dash component: Updated metrics display
        """
        try:
            # Generate risk report with custom confidence level
            risk_report = risk_analyser.generate_risk_report(
                confidence_level=confidence_level
            )
            metrics_df = risk_report["risk_metrics"]

            # Return updated metrics display
            return create_metrics_display(metrics_df, confidence_level)
        except Exception as e:
            from dash import html

            # Handle errors gracefully
            return html.Div(
                html.P(f"Error updating metrics: {str(e)}", style={"color": "red"})
            )
