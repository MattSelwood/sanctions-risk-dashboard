"""
Components for displaying the transactions data table in the Sanctions Dashboard.
"""

from dash import html, dcc, dash_table
import plotly.express as px
from config import COLOURS, SECTION_HEADER_STYLE


def create_transaction_filters(transactions):
    """Create the transaction filtering controls"""
    unique_countries = set(transactions["sender_country"].unique()) | set(
        transactions["receiver_country"].unique()
    )
    country_options = [
        {"label": country, "value": country} for country in unique_countries
    ]

    return html.Div(
        [
            html.Div(
                [
                    html.Label("Filter by Country:"),
                    dcc.Dropdown(
                        id="country-filter",
                        options=country_options,
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
                        marks={i: f"${i:,}" for i in range(0, 50001, 10000)},
                    ),
                ],
                className="eight columns",
            ),
        ],
        className="row",
    )


def create_transaction_table(flagged_transactions):
    """Create the transaction data table"""
    return dash_table.DataTable(
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
        data=flagged_transactions.to_dict("records"),
        page_size=10,
        style_table={"overflowX": "auto"},
        style_cell={
            "minWidth": "100px",
            "maxWidth": "200px",
            "whiteSpace": "normal",
            "textAlign": "left",
        },
        style_header={
            "backgroundColor": COLOURS["header_bg"],
            "color": COLOURS["header_text_color"],
            "fontWeight": "bold",
        },
        style_data_conditional=[
            {"if": {"row_index": "odd"}, "backgroundColor": COLOURS["odd_row_bg"]},
            {
                "if": {"filter_query": "{amount} > 30000"},
                "backgroundColor": COLOURS["high_amount_bg"],
                "color": COLOURS["high_amount_text"],
            },
        ],
    )


def create_transactions_section(transactions, initial_report):
    """Create the transactions section with filters and table"""
    return html.Div(
        [
            html.H3("Sanctioned Transactions", style=SECTION_HEADER_STYLE),
            create_transaction_filters(transactions),
            create_transaction_table(initial_report["flagged_transactions"]),
            # Store for filtered transactions
            dcc.Store(
                id="flagged-transactions-store",
                data=initial_report["flagged_transactions"].to_dict("records"),
            ),
        ],
        className="row section",
    )


def create_risk_heatmap(transactions):
    """Create the risk heatmap visualization"""
    return html.Div(
        [
            html.H3("Sanctions Risk Heatmap", style=SECTION_HEADER_STYLE),
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
    )
