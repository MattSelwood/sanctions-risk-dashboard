# filepath: /D:/GitRepos/sanctions-risk-dashboard/components/compliance_report_tab.py
import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.express as px

def create_compliance_report_tab(compliance_report, scored_data):
    return dbc.Tab(label="Compliance Report", children=[
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Risk Summary by Category"),
                    dbc.CardBody([
                        html.Table([
                            html.Tr([html.Th('Category'), html.Th('Count'), html.Th('Volume'), html.Th('Potential Penalty')]),
                            html.Tr([
                                html.Td('High Risk', style={'color': '#dc3545', 'fontWeight': 'bold'}),
                                html.Td(f"{compliance_report['risk_by_category']['high']['transaction_count']:,}"),
                                html.Td(f"${compliance_report['risk_by_category']['high']['volume']:,.2f}"),
                                html.Td(f"${compliance_report['risk_by_category']['high']['potential_penalty']:,.2f}")
                            ]),
                            html.Tr([
                                html.Td('Medium Risk', style={'color': '#ffc107', 'fontWeight': 'bold'}),
                                html.Td(f"{compliance_report['risk_by_category']['medium']['transaction_count']:,}"),
                                html.Td(f"${compliance_report['risk_by_category']['medium']['volume']:,.2f}"),
                                html.Td(f"${compliance_report['risk_by_category']['medium']['potential_penalty']:,.2f}")
                            ]),
                            html.Tr([
                                html.Td('Low Risk', style={'color': '#28a745', 'fontWeight': 'bold'}),
                                html.Td(f"{compliance_report['risk_by_category']['low']['transaction_count']:,}"),
                                html.Td(f"${compliance_report['risk_by_category']['low']['volume']:,.2f}"),
                                html.Td(f"${compliance_report['risk_by_category']['low']['potential_penalty']:,.2f}")
                            ])
                        ], className="table table-striped table-bordered", style={'width': '100%'})
                    ])
                ], className="mb-4 shadow")
            ], width=12)
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Potential Penalty Distribution"),
                    dbc.CardBody([
                        dcc.Graph(
                            figure=px.bar(
                                x=['High Risk', 'Medium Risk', 'Low Risk'],
                                y=[
                                    compliance_report['risk_by_category']['high']['potential_penalty'],
                                    compliance_report['risk_by_category']['medium']['potential_penalty'],
                                    compliance_report['risk_by_category']['low']['potential_penalty']
                                ],
                                color=['High Risk', 'Medium Risk', 'Low Risk'],
                                color_discrete_map={
                                    'High Risk': '#dc3545',
                                    'Medium Risk': '#ffc107',
                                    'Low Risk': '#28a745'
                                },
                                labels={'x': 'Risk Category', 'y': 'Potential Penalty ($)'}
                            )
                        )
                    ])
                ], className="mb-4 shadow")
            ], width=8),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Additional Risk Metrics"),
                    dbc.CardBody([
                        html.Ul([
                            html.Li(f"Penalty at Risk (95% VaR): ${compliance_report['summary_metrics']['penalty_at_risk']:,.2f}"),
                            html.Li(f"Total Transaction Count: {len(scored_data):,}"),
                            html.Li(f"Average Transaction Amount: ${scored_data['amount'].mean():,.2f}"),
                            html.Li(f"Highest Single Transaction Risk: {scored_data['risk_score'].max():.4f}"),
                            html.Li(f"Average Risk Score: {scored_data['risk_score'].mean():.4f}")
                        ], className="list-group")
                    ])
                ], className="mb-4 shadow")
            ], width=4)
        ])
    ])