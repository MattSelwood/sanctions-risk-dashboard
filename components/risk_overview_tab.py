# filepath: /D:/GitRepos/sanctions-risk-dashboard/components/risk_overview_tab.py
import dash_bootstrap_components as dbc
from dash import dcc
import plotly.express as px

def create_risk_overview_tab(compliance_report, country_exposure_data, transactions):
    return dbc.Tab(label="Risk Overview", children=[
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Risk Distribution by Category"),
                    dbc.CardBody([
                        dcc.Graph(
                            figure=px.pie(
                                names=['High Risk', 'Medium Risk', 'Low Risk'],
                                values=[
                                    compliance_report['risk_by_category']['high']['volume'],
                                    compliance_report['risk_by_category']['medium']['volume'],
                                    compliance_report['risk_by_category']['low']['volume']
                                ],
                                color=['High Risk', 'Medium Risk', 'Low Risk'],
                                color_discrete_map={
                                    'High Risk': '#dc3545',
                                    'Medium Risk': '#ffc107',
                                    'Low Risk': '#28a745'
                                },
                                hole=0.4
                            )
                        )
                    ])
                ], className="mb-4 shadow")
            ], width=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Sanctions Flag Trend Over Time"),
                    dbc.CardBody([
                        dcc.Graph(
                            figure=px.line(
                                x=list(compliance_report['time_trend'].keys()),
                                y=[d['flag_ratio'] * 100 for d in compliance_report['time_trend'].values()],
                                labels={'x': 'Date', 'y': 'Flag Ratio (%)'},
                                title="Percentage of Flagged Transactions Over Time"
                            )
                        )
                    ])
                ], className="mb-4 shadow")
            ], width=6)
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Country Risk Analysis"),
                    dbc.CardBody([
                        dcc.Graph(
                            id="country-exposure-chart",
                            figure=px.bar(
                                country_exposure_data.sort_values("Total", ascending=False),
                                x="Country",
                                y=["Incoming", "Outgoing"],
                                title="Sanctions Exposure by Country",
                                labels={"value": "Transaction Amount ($)", "variable": "Direction"},
                                barmode="group",
                                color_discrete_map={"Incoming": "#2ecc71", "Outgoing": "#e74c3c"},
                            )
                        )
                    ])
                ], className="mb-4 shadow")
            ], width=6),

            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Transaction Risk Heatmap"),
                    dbc.CardBody([
                        dcc.Graph(
                            id="risk-heatmap",
                            figure=px.density_heatmap(
                                transactions[transactions["sanctions_flag"] == 1],
                                x="sender_country",
                                y="receiver_country",
                                z="amount",
                                title="Flagged Transaction Heatmap",
                                labels={
                                    "sender_country": "Sender Country",
                                    "receiver_country": "Receiver Country",
                                    "amount": "Transaction Amount ($)",
                                },
                                color_continuous_scale="Plasma",
                            ),
                        )
                    ])
                ], className="mb-4 shadow")
            ], width=6)
        ])

        
    ])