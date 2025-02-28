# filepath: /D:/GitRepos/sanctions-risk-dashboard/components/anomaly_detection_tab.py
import dash_bootstrap_components as dbc
from dash.dash_table.Format import Format, Scheme
from dash import dcc, dash_table
import plotly.express as px


def create_anomaly_detection_tab(anomaly_data):
    return dbc.Tab(
        label="Anomaly Detection",
        children=[
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader("Anomaly Score Distribution"),
                                    dbc.CardBody(
                                        [
                                            dcc.Graph(
                                                figure=px.histogram(
                                                    anomaly_data["anomaly_data"],
                                                    x="anomaly_score",
                                                    nbins=30,
                                                    color_discrete_sequence=["#17a2b8"],
                                                    labels={
                                                        "anomaly_score": "Anomaly Score"
                                                    },
                                                )
                                            )
                                        ]
                                    ),
                                ],
                                className="mb-4 shadow",
                            )
                        ],
                        width=6,
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        "Amount Z-score vs Frequency Percentile"
                                    ),
                                    dbc.CardBody(
                                        [
                                            dcc.Graph(
                                                figure=px.scatter(
                                                    anomaly_data["anomaly_data"],
                                                    x="amount_zscore",
                                                    y="freq_percentile",
                                                    color="sanctions_flag",
                                                    color_discrete_map={
                                                        1: "#dc3545",
                                                        0: "#6c757d",
                                                    },
                                                    size="amount",
                                                    hover_data=[
                                                        "sender_country",
                                                        "receiver_country",
                                                        "amount",
                                                    ],
                                                    labels={
                                                        "amount_zscore": "Amount Z-Score",
                                                        "freq_percentile": "Frequency Percentile",
                                                        "sanctions_flag": "Sanctions Flag",
                                                    },
                                                )
                                            )
                                        ]
                                    ),
                                ],
                                className="mb-4 shadow",
                            )
                        ],
                        width=6,
                    ),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader("Top 10 Anomalous Transactions"),
                                    dbc.CardBody(
                                        [
                                            dash_table.DataTable(
                                                columns=[
                                                    {
                                                        "name": "Date",
                                                        "id": "date",
                                                        "type": "datetime",
                                                    },
                                                    {
                                                        "name": "Sender",
                                                        "id": "sender_country",
                                                    },
                                                    {
                                                        "name": "Receiver",
                                                        "id": "receiver_country",
                                                    },
                                                    {
                                                        "name": "Amount",
                                                        "id": "amount",
                                                        "type": "numeric",
                                                        "format": Format(
                                                            precision=2,
                                                            scheme=Scheme.fixed,
                                                        ),
                                                    },
                                                    {
                                                        "name": "Sanctions Flag",
                                                        "id": "sanctions_flag",
                                                    },
                                                    {
                                                        "name": "Amount Z-score",
                                                        "id": "amount_zscore",
                                                        "type": "numeric",
                                                        "format": Format(
                                                            precision=2,
                                                            scheme=Scheme.fixed,
                                                        ),
                                                    },
                                                    {
                                                        "name": "Freq. Percentile",
                                                        "id": "freq_percentile",
                                                        "type": "numeric",
                                                        "format": Format(
                                                            precision=2,
                                                            scheme=Scheme.fixed,
                                                        ),
                                                    },
                                                    {
                                                        "name": "Anomaly Score",
                                                        "id": "anomaly_score",
                                                        "type": "numeric",
                                                        "format": Format(
                                                            precision=4,
                                                            scheme=Scheme.fixed,
                                                        ),
                                                    },
                                                ],
                                                data=anomaly_data["top_anomalies"]
                                                .head(10)
                                                .to_dict("records"),
                                                style_data_conditional=[
                                                    {
                                                        "if": {
                                                            "filter_query": "{sanctions_flag} = 1"
                                                        },
                                                        "backgroundColor": "rgba(220, 53, 69, 0.2)",
                                                        "color": "#dc3545",
                                                    },
                                                    {
                                                        "if": {
                                                            "filter_query": "{amount_zscore} > 3"
                                                        },
                                                        "backgroundColor": "rgba(255, 193, 7, 0.2)",
                                                        "color": "#856404",
                                                    },
                                                ],
                                                style_cell={
                                                    "textAlign": "left",
                                                    "padding": "10px",
                                                },
                                                style_header={
                                                    "backgroundColor": "#f8f9fa",
                                                    "fontWeight": "bold",
                                                },
                                            )
                                        ]
                                    ),
                                ],
                                className="mb-4 shadow",
                            )
                        ],
                        width=12,
                    )
                ]
            ),
        ],
    )
