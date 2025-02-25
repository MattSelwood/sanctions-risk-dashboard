"""
Main application file for the Sanctions Dashboard.
"""

import dash
from dash import html

# Import configuration
from config import DEBUG, DEFAULT_CONFIDENCE

# Import data handling
from data.loader import initialise_data

# Import layout components
from components.header import create_header
from components.metrics import create_risk_metrics_section
from components.charts import create_charts_section
from components.transactions import create_transactions_section, create_risk_heatmap

# Import callbacks
from callbacks.metrics_callbacks import register_metrics_callbacks
from callbacks.filter_callbacks import register_filter_callbacks


def create_layout(transactions, initial_report):
    """
    Create the main app layout.

    Args:
        transactions (DataFrame): Transaction data
        initial_report (dict): Initial risk report data

    Returns:
        dash.html.Div: The complete dashboard layout
    """
    return html.Div(
        [
            create_header(),
            create_risk_metrics_section(initial_report, DEFAULT_CONFIDENCE),
            create_charts_section(initial_report),
            create_transactions_section(transactions, initial_report),
            create_risk_heatmap(transactions),
        ],
        style={"maxWidth": "1200px", "margin": "0 auto"},
    )


def initialise_app():
    """
    Initialise the Dash application.

    Returns:
        tuple: (app, transactions, risk_analyser, initial_report)
    """
    # Initialise data
    transactions, risk_analyser, initial_report = initialise_data()

    # Initialise app
    app = dash.Dash(__name__, suppress_callback_exceptions=True)

    # Set app layout
    app.layout = create_layout(transactions, initial_report)

    # Register callbacks
    register_metrics_callbacks(app, risk_analyser)
    register_filter_callbacks(app)

    return app, transactions, risk_analyser, initial_report


def main():
    """Main entry point for the application."""
    app, _, _, _ = initialise_app()
    app.run_server(debug=DEBUG)


if __name__ == "__main__":
    main()
