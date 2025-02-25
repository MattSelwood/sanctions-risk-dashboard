import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd

from modules.riskanalysis import SanctionsRiskAnalyser
from modules.data import generate_transaction_data

# ------- DASH APP -------

# Default confidence level
DEFAULT_CONFIDENCE = 0.95

# Generate data
transactions = generate_transaction_data(5000)
risk_analyzer = SanctionsRiskAnalyser(transactions)

# Get the initial risk report at default confidence level
initial_report = risk_analyzer.generate_risk_report(confidence_level=DEFAULT_CONFIDENCE)

# Initialise the app
app = dash.Dash(__name__, suppress_callback_exceptions=True)


# App layout
app.layout = html.Div(
    [
        # Header
        html.Div(
            [
                html.H1(
                    "Sanctions Risk Management Dashboard",
                    style={
                        "textAlign": "center",
                        "color": "#2c3e50",
                        "padding": "20px",
                    },
                ),
                html.P(
                    "Analysis of transaction risk exposure to sanctioned countries",
                    style={"textAlign": "center", "color": "#7f8c8d"},
                ),
            ]
        ),
        # Key Metrics with Threshold Settings
        html.Div(
            [
                html.Div(
                    [
                        html.H3(
                            "Key Risk Metrics",
                            style={"color": "#2c3e50", "padding": "10px"},
                        ),
                        html.Div(
                            [
                                html.Label("VaR Confidence Level:"),
                                dcc.Slider(
                                    id="var-confidence-slider",
                                    min=0.9,
                                    max=0.995,
                                    step=0.005,
                                    value=DEFAULT_CONFIDENCE,
                                    marks={i / 100: f"{i}%" for i in range(90, 100, 2)},
                                    tooltip={
                                        "placement": "bottom",
                                        "always_visible": True,
                                    },
                                ),
                            ],
                            style={"marginBottom": "20px", "padding": "10px"},
                        ),
                        html.Button(
                            "Update Risk Metrics",
                            id="update-metrics-button",
                            style={
                                "backgroundColor": "#3498db",
                                "color": "white",
                                "border": "none",
                                "padding": "10px 20px",
                                "borderRadius": "5px",
                                "cursor": "pointer",
                                "marginBottom": "20px",
                                "marginLeft": "10px",
                            },
                        ),
                    ],
                    className="row",
                ),
                html.Div(
                    id="metrics-container",
                    className="row",
                    children=[
                        # Initialize with default metrics
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H4(
                                            f"Historical VaR ({DEFAULT_CONFIDENCE*100:.0f}%)",
                                            style={"textAlign": "center"},
                                        ),
                                        html.H2(
                                            f"${initial_report['risk_metrics'].loc[0, 'Value']:,.2f}",
                                            style={
                                                "textAlign": "center",
                                                "color": "#e74c3c",
                                            },
                                        ),
                                    ],
                                    className="metric-box",
                                )
                            ],
                            className="three columns",
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H4(
                                            f"Parametric VaR ({DEFAULT_CONFIDENCE*100:.0f}%)",
                                            style={"textAlign": "center"},
                                        ),
                                        html.H2(
                                            f"${initial_report['risk_metrics'].loc[1, 'Value']:,.2f}",
                                            style={
                                                "textAlign": "center",
                                                "color": "#e67e22",
                                            },
                                        ),
                                    ],
                                    className="metric-box",
                                )
                            ],
                            className="three columns",
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H4(
                                            f"Monte Carlo VaR ({DEFAULT_CONFIDENCE*100:.0f}%)",
                                            style={"textAlign": "center"},
                                        ),
                                        html.H2(
                                            f"${initial_report['risk_metrics'].loc[2, 'Value']:,.2f}",
                                            style={
                                                "textAlign": "center",
                                                "color": "#f39c12",
                                            },
                                        ),
                                    ],
                                    className="metric-box",
                                )
                            ],
                            className="three columns",
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H4(
                                            f"Expected Shortfall ({DEFAULT_CONFIDENCE*100:.0f}%)",
                                            style={"textAlign": "center"},
                                        ),
                                        html.H2(
                                            f"${initial_report['risk_metrics'].loc[3, 'Value']:,.2f}",
                                            style={
                                                "textAlign": "center",
                                                "color": "#c0392b",
                                            },
                                        ),
                                    ],
                                    className="metric-box",
                                )
                            ],
                            className="three columns",
                        ),
                    ],
                ),
            ],
            className="row section",
        ),
        # Charts Row
        html.Div(
            [
                # Country Exposure
                html.Div(
                    [
                        html.H3(
                            "Country Exposure Analysis",
                            style={"color": "#2c3e50", "padding": "10px"},
                        ),
                        dcc.Graph(
                            id="country-exposure-chart",
                            figure=px.bar(
                                initial_report["country_exposure"].sort_values(
                                    "Total", ascending=False
                                ),
                                x="Country",
                                y=["Incoming", "Outgoing"],
                                title="Exposure by Country",
                                labels={
                                    "value": "Transaction Amount ($)",
                                    "variable": "Direction",
                                },
                                barmode="group",
                                color_discrete_map={
                                    "Incoming": "#2ecc71",
                                    "Outgoing": "#e74c3c",
                                },
                            ),
                        ),
                    ],
                    className="six columns",
                ),
                # Time Series
                html.Div(
                    [
                        html.H3(
                            "Transaction Volume Over Time",
                            style={"color": "#2c3e50", "padding": "10px"},
                        ),
                        dcc.Graph(
                            id="time-series-chart",
                            figure=px.line(
                                initial_report["time_series"],
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
                ),
            ],
            className="row section",
        ),
        # Filtered Transaction Table
        html.Div(
            [
                html.H3(
                    "Sanctioned Transactions",
                    style={"color": "#2c3e50", "padding": "10px"},
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Label("Filter by Country:"),
                                dcc.Dropdown(
                                    id="country-filter",
                                    options=[
                                        {"label": country, "value": country}
                                        for country in transactions[
                                            "sender_country"
                                        ].unique()
                                    ]
                                    + [
                                        {"label": country, "value": country}
                                        for country in transactions[
                                            "receiver_country"
                                        ].unique()
                                    ],
                                    multi=True,
                                    value=[],
                                ),
                            ],
                            className="four columns",
                        ),
                        html.Div(
                            [
                                html.Label("Min Amount:"),
                                dcc.Slider(
                                    id="amount-slider",
                                    min=0,
                                    max=50000,
                                    step=1000,
                                    value=5000,
                                    marks={
                                        i: f"${i:,}" for i in range(0, 50001, 10000)
                                    },
                                ),
                            ],
                            className="eight columns",
                        ),
                    ],
                    className="row",
                ),
                dash_table.DataTable(
                    id="transaction-table",
                    columns=[
                        {"name": "Transaction ID", "id": "transaction_id"},
                        {"name": "Date", "id": "date", "type": "datetime"},
                        {
                            "name": "Amount",
                            "id": "amount",
                            "type": "numeric",
                            "format": {"specifier": "$,.2f"},
                        },
                        {"name": "Sender Country", "id": "sender_country"},
                        {"name": "Receiver Country", "id": "receiver_country"},
                    ],
                    data=initial_report["flagged_transactions"].to_dict("records"),
                    page_size=10,
                    style_table={"overflowX": "auto"},
                    style_cell={
                        "minWidth": "100px",
                        "maxWidth": "200px",
                        "whiteSpace": "normal",
                        "textAlign": "left",
                    },
                    style_header={
                        "backgroundColor": "#2c3e50",
                        "color": "white",
                        "fontWeight": "bold",
                    },
                    style_data_conditional=[
                        {"if": {"row_index": "odd"}, "backgroundColor": "#f9f9f9"},
                        {
                            "if": {"filter_query": "{amount} > 30000"},
                            "backgroundColor": "#f8d7da",
                            "color": "#721c24",
                        },
                    ],
                ),
            ],
            className="row section",
        ),
        # Risk Heatmap
        html.Div(
            [
                html.H3(
                    "Sanctions Risk Heatmap",
                    style={"color": "#2c3e50", "padding": "10px"},
                ),
                dcc.Graph(
                    id="risk-heatmap",
                    figure=px.density_heatmap(
                        transactions[transactions["sanctions_flag"] == 1],
                        x="sender_country",
                        y="receiver_country",
                        z="amount",
                        title="Transaction Risk Heatmap",
                        labels={
                            "sender_country": "Sender Country",
                            "receiver_country": "Receiver Country",
                            "amount": "Transaction Amount ($)",
                        },
                        color_continuous_scale="Plasma",
                    ),
                ),
            ],
            className="row section",
        ),
        # Store the flagged transactions for filtering
        dcc.Store(
            id="flagged-transactions-store",
            data=initial_report["flagged_transactions"].to_dict("records"),
        ),
    ],
    style={"maxWidth": "1200px", "margin": "0 auto"},
)


# Callback to update the risk metrics with custom confidence level
@app.callback(
    Output("metrics-container", "children"),
    [Input("update-metrics-button", "n_clicks")],
    [State("var-confidence-slider", "value")],
    prevent_initial_call=True,
)
def update_risk_metrics(n_clicks, confidence_level):
    # Generate risk report with custom confidence level
    # We only need the risk metrics part
    risk_report = risk_analyzer.generate_risk_report(confidence_level=confidence_level)
    metrics_df = risk_report["risk_metrics"]

    # Create the metrics display
    metrics_display = [
        html.Div(
            [
                html.Div(
                    [
                        html.H4(
                            f"Historical VaR ({confidence_level*100:.0f}%)",
                            style={"textAlign": "center"},
                        ),
                        html.H2(
                            f"${metrics_df.loc[0, 'Value']:,.2f}",
                            style={
                                "textAlign": "center",
                                "color": "#e74c3c",
                            },
                        ),
                    ],
                    className="metric-box",
                )
            ],
            className="three columns",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.H4(
                            f"Parametric VaR ({confidence_level*100:.0f}%)",
                            style={"textAlign": "center"},
                        ),
                        html.H2(
                            f"${metrics_df.loc[1, 'Value']:,.2f}",
                            style={
                                "textAlign": "center",
                                "color": "#e67e22",
                            },
                        ),
                    ],
                    className="metric-box",
                )
            ],
            className="three columns",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.H4(
                            f"Monte Carlo VaR ({confidence_level*100:.0f}%)",
                            style={"textAlign": "center"},
                        ),
                        html.H2(
                            f"${metrics_df.loc[2, 'Value']:,.2f}",
                            style={
                                "textAlign": "center",
                                "color": "#f39c12",
                            },
                        ),
                    ],
                    className="metric-box",
                )
            ],
            className="three columns",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.H4(
                            f"Expected Shortfall ({confidence_level*100:.0f}%)",
                            style={"textAlign": "center"},
                        ),
                        html.H2(
                            f"${metrics_df.loc[3, 'Value']:,.2f}",
                            style={
                                "textAlign": "center",
                                "color": "#c0392b",
                            },
                        ),
                    ],
                    className="metric-box",
                )
            ],
            className="three columns",
        ),
    ]

    return metrics_display


# Callback for filtering transactions
@app.callback(
    Output("transaction-table", "data"),
    [
        Input("country-filter", "value"),
        Input("amount-slider", "value"),
        Input("flagged-transactions-store", "data"),
    ],
)
def update_table(countries, min_amount, flagged_transactions_data):
    if not flagged_transactions_data:
        return []

    # Convert back to DataFrame
    flagged_transactions = pd.DataFrame(flagged_transactions_data)

    # Apply country filter if selected
    if countries and len(countries) > 0:
        filtered_data = flagged_transactions[
            (flagged_transactions["sender_country"].isin(countries))
            | (flagged_transactions["receiver_country"].isin(countries))
        ]
    else:
        filtered_data = flagged_transactions

    # Apply amount filter
    filtered_data = filtered_data[filtered_data["amount"] >= min_amount]

    return filtered_data.to_dict("records")


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
