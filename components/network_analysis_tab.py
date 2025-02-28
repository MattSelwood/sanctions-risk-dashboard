# filepath: /D:/GitRepos/sanctions-risk-dashboard/components/network_analysis_tab.py
import dash_bootstrap_components as dbc
from dash.dash_table.Format import Format, Scheme
from dash import dcc, dash_table, html
import plotly.graph_objects as go
import networkx as nx
import numpy as np


def create_network_analysis_tab(network_analysis, scored_data):
    return dbc.Tab(
        label="Network Analysis",
        children=[
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader("Transaction Network Graph"),
                                    dbc.CardBody([dcc.Graph(id="network-graph")]),
                                ],
                                className="mb-4 shadow",
                            )
                        ],
                        width=12,
                    ),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader("Country Risk Centrality Metrics"),
                                    dbc.CardBody(
                                        [
                                            dash_table.DataTable(
                                                columns=[
                                                    {
                                                        "name": "Country",
                                                        "id": "country",
                                                    },
                                                    {
                                                        "name": "Centrality Score",
                                                        "id": "centrality",
                                                        "type": "numeric",
                                                        "format": Format(
                                                            precision=4,
                                                            scheme=Scheme.fixed,
                                                        ),
                                                    },
                                                ],
                                                data=[
                                                    {"country": k, "centrality": v}
                                                    for k, v in network_analysis[
                                                        "risk_centrality"
                                                    ].items()
                                                ],
                                                sort_action="native",
                                                style_cell={
                                                    "textAlign": "left",
                                                    "padding": "10px",
                                                },
                                                style_header={
                                                    "backgroundColor": "#f8f9fa",
                                                    "fontWeight": "bold",
                                                },
                                                style_data_conditional=[
                                                    {
                                                        "if": {
                                                            "column_id": "centrality",
                                                            "filter_query": "{centrality} >= 0.05",
                                                        },
                                                        "backgroundColor": "rgba(220, 53, 69, 0.2)",
                                                        "color": "#dc3545",
                                                    }
                                                ],
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
                                    dbc.CardHeader("High Risk Transaction Paths"),
                                    dbc.CardBody(
                                        [
                                            (
                                                html.Ul(
                                                    [
                                                        html.Li(
                                                            " → ".join(path),
                                                            style={
                                                                "marginBottom": "10px"
                                                            },
                                                        )
                                                        for path in network_analysis[
                                                            "high_risk_paths"
                                                        ][:10]
                                                    ]
                                                )
                                                if network_analysis["high_risk_paths"]
                                                else html.P(
                                                    "No high risk paths detected"
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
        ],
    )
