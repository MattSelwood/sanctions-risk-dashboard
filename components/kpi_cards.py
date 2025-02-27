"""
Components for displaying KPI Card header in the Sanctions Dashboard.
"""

import dash_bootstrap_components as dbc
from dash import html

def create_kpi_cards(compliance_report):
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Total Transaction Volume", className="card-title text-center"),
                    html.H2(f"${compliance_report['summary_metrics']['total_transaction_volume']:,.2f}", 
                           className="card-text text-center text-primary")
                ])
            ], className="mb-4 shadow")
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Sanctioned Volume", className="card-title text-center"),
                    html.H2(f"${compliance_report['summary_metrics']['sanctioned_volume']:,.2f}", 
                           className="card-text text-center text-danger")
                ])
            ], className="mb-4 shadow")
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("% Sanctioned", className="card-title text-center"),
                    html.H2(f"{compliance_report['summary_metrics']['percent_sanctioned']:.2f}%", 
                           className="card-text text-center text-warning")
                ])
            ], className="mb-4 shadow")
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Potential Penalty Exposure", className="card-title text-center"),
                    html.H2(f"${compliance_report['summary_metrics']['potential_penalty_exposure']:,.2f}", 
                           className="card-text text-center text-danger")
                ])
            ], className="mb-4 shadow")
        ], width=3),
    ])