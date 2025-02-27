import dash
from dash import html
import dash_bootstrap_components as dbc


from data.loader import initialise_data


from components.header import create_header
from components.kpi_cards import create_kpi_cards
from components.transaction_analysis_tab import create_transaction_analysis_tab
from components.network_analysis_tab import create_network_analysis_tab
from components.anomaly_detection_tab import create_anomaly_detection_tab
from components.compliance_report_tab import create_compliance_report_tab
from components.risk_overview_tab import create_risk_overview_tab

from callbacks.network_callbacks import register_network_callbacks



# Initialize the Dash app
def create_layout(
    transactions, compliance_report, country_exposure, scored_data, anomaly_data
):
    """
    Create the main app layout.

    Args:
        transactions (DataFrame): Transaction data
        compliance_report (dict): Compliance report data
        country_exposure (DataFrame): Country exposure data
        scored_data (DataFrame): Scored transaction data
        anomaly_data (DataFrame): Anomaly detection

    Returns:
        dbc.Container: Main app layout
    """
    return dbc.Container(
        [
            create_header(),
            create_kpi_cards(compliance_report),
            # Tabs for different views
            dbc.Tabs(
                [
                    create_risk_overview_tab(compliance_report, country_exposure, transactions),
                    create_transaction_analysis_tab(scored_data),
                    # create_network_analysis_tab(network_analysis),
                    create_anomaly_detection_tab(anomaly_data),
                    create_compliance_report_tab(compliance_report, scored_data),
                ],
                className="mt-4",
            ),
            html.Footer(
                [
                    html.P(
                        "Sanctions Risk Analysis Dashboard - Created by Matthew Selwood with Plotly Dash",
                        className="text-center text-muted my-4",
                    )
                ]
            ),
        ],
        fluid=True,
    )


def initialise_app():
    """
    Initialise the Dash application.

    Returns:
        tuple: (dash.Dash, DataFrame, SanctionsRiskAnalyser, dict)
    """
    # Initialise data
    (
        transactions,
        analyser,
        scored_data,
        exposure_metrics,
        country_exposure,
        penalty_exposure,
        anomaly_data,
        network_analysis,
        compliance_report,
    ) = initialise_data()

    # Initialise app
    app = dash.Dash(
        __name__,
        external_stylesheets=[dbc.themes.FLATLY],
        suppress_callback_exceptions=True,
    )

    # Set app layout
    app.layout = create_layout(
        transactions, compliance_report, country_exposure, scored_data, anomaly_data
    )

    # Register callbacks
    # register_network_callbacks(app, network_analysis, scored_data)

    return app, transactions, analyser, compliance_report


# Run the app
if __name__ == "__main__":
    app, _, _, _ = initialise_app()
    app.run_server(debug=True)
