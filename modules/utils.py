import pandas as pd


def export_data(transactions_df, risk_report):
    """Exports data for use with Tableau etc."""
    # 1. Transaction Summary by Country
    country_summary = pd.DataFrame(
        {
            "Country": risk_report["Country_Exposure"].index,
            "Total_Exposure": risk_report["Country_Exposure"]["Total"],
            "Outgoing": risk_report["Country_Exposure"]["Outgoing"],
            "Incoming": risk_report["Country_Exposure"]["Incoming"],
        }
    )

    # 2. Risk Metrics Summary
    risk_metrics = pd.DataFrame(
        {
            "Metric": [
                "VaR (Historical)",
                "VaR (Parametric)",
                "VaR (Monte Carlo)",
                "Expected Shortfall",
            ],
            "Value": [
                risk_report["VaR_Historical"],
                risk_report["VaR_Parametric"],
                risk_report["VaR_MonteCarlo"],
                risk_report["Expected_Shortfall"],
            ],
        }
    )

    # 3. Time Series Data (Daily Risk Exposure)
    time_series = (
        transactions_df.groupby("date")
        .agg({"amount": "sum", "sanctions_flag": "sum"})
        .reset_index()
    )
    time_series["sanctions_exposure"] = time_series.apply(
        lambda x: x["amount"] if x["sanctions_flag"] > 0 else 0, axis=1
    )

    # 4. Transaction-level data for detailed view
    transaction_detail = transactions_df[
        [
            "transaction_id",
            "date",
            "amount",
            "sender_country",
            "receiver_country",
            "sanctions_flag",
        ]
    ]

    # Save to CSV for Tableau import
    country_summary.to_csv("country_summary.csv", index=False)
    risk_metrics.to_csv("risk_metrics.csv", index=False)
    time_series.to_csv("time_series.csv", index=False)
    transaction_detail.to_csv("transaction_detail.csv", index=False)

    return {
        "country_summary": country_summary,
        "risk_metrics": risk_metrics,
        "time_series": time_series,
        "transaction_detail": transaction_detail,
    }
