"""
Callbacks for transaction table filters in the Sanctions Dashboard.
"""

import pandas as pd
from dash.dependencies import Input, Output


def register_filter_callbacks(app):
    """
    Register callbacks related to risk metrics.

    Args:
        app (Dash): The Dash app instance
    """

    @app.callback(
        Output("transaction-table", "data"),
        [
            Input("country-filter", "value"),
            Input("amount-slider", "value"),
            Input("flagged-transactions-store", "data")
        ]
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