# filepath: /D:/GitRepos/sanctions-risk-dashboard/components/transaction_analysis_tab.py
import dash_bootstrap_components as dbc
from dash import dcc, dash_table
from dash.dash_table.Format import Format, Scheme
import plotly.express as px

def create_transaction_analysis_tab(scored_data):
    return dbc.Tab(label="Transaction Analysis", children=[
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Transaction Amount vs. Risk Score"),
                    dbc.CardBody([
                        dcc.Graph(
                            figure=px.scatter(
                                scored_data,
                                x='amount',
                                y='risk_score',
                                color='risk_category',
                                color_discrete_map={
                                    'high': '#dc3545',
                                    'medium': '#ffc107',
                                    'low': '#28a745'
                                },
                                size='amount',
                                hover_data=['sender_country', 'receiver_country', 'sanctions_flag'],
                                labels={'amount': 'Transaction Amount', 'risk_score': 'Risk Score'}
                            )
                        )
                    ])
                ], className="mb-4 shadow")
            ], width=12)
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Top 10 Highest Risk Transactions"),
                    dbc.CardBody([
                        dash_table.DataTable(
                            columns=[
                                {'name': 'Date', 'id': 'date', 'type': 'datetime'},
                                {'name': 'Sender', 'id': 'sender_country'},
                                {'name': 'Receiver', 'id': 'receiver_country'},
                                {'name': 'Amount', 'id': 'amount', 'type': 'numeric', 'format': Format(precision=2, scheme=Scheme.fixed)},
                                {'name': 'Sanctions Flag', 'id': 'sanctions_flag'},
                                {'name': 'Risk Score', 'id': 'risk_score', 'type': 'numeric', 'format': Format(precision=4, scheme=Scheme.fixed)},
                                {'name': 'Risk Category', 'id': 'risk_category'},
                            ],
                            data=scored_data.sort_values('risk_score', ascending=False).head(10).to_dict('records'),
                            style_data_conditional=[
                                {
                                    'if': {'filter_query': '{risk_category} = "high"'},
                                    'backgroundColor': 'rgba(220, 53, 69, 0.2)',
                                    'color': '#dc3545'
                                },
                                {
                                    'if': {'filter_query': '{risk_category} = "medium"'},
                                    'backgroundColor': 'rgba(255, 193, 7, 0.2)',
                                    'color': '#856404'
                                },
                                {
                                    'if': {'filter_query': '{risk_category} = "low"'},
                                    'backgroundColor': 'rgba(40, 167, 69, 0.2)',
                                    'color': '#155724'
                                }
                            ],
                            style_cell={
                                'textAlign': 'left',
                                'padding': '10px'
                            },
                            style_header={
                                'backgroundColor': '#f8f9fa',
                                'fontWeight': 'bold'
                            }
                        )
                    ])
                ], className="mb-4 shadow")
            ], width=12)
        ])
    ])