import pandas as pd
from typing import Dict, Any

class ExposureMetricsCalculator:
    def __init__(self, transaction_data: pd.DataFrame):
        """
        Initialize the ExposureMetricsCalculator with transaction data.

        :param transaction_data: DataFrame containing transaction data
        """
        self.data = transaction_data

    def calculate_exposure_metrics(self) -> Dict[str, Any]:
        """
        Calculate exposure metrics related to sanctions risk.

        :return: Dictionary containing total volume, sanctioned volume, percent sanctioned, and risk by sender and receiver countries
        """
        total_volume = self.data["amount"].sum()
        sanctioned_volume = self.data[self.data["sanctions_flag"] == 1]["amount"].sum()
        percent_sanctioned = (sanctioned_volume / total_volume) * 100 if total_volume else 0

        sender_risk = self.data.groupby("sender_country").agg({"amount": "sum", "sanctions_flag": "sum"})
        sender_risk["flag_rate"] = sender_risk["sanctions_flag"] / sender_risk.index.map(
            lambda x: len(self.data[self.data["sender_country"] == x])
        )

        receiver_risk = self.data.groupby("receiver_country").agg({"amount": "sum", "sanctions_flag": "sum"})
        receiver_risk["flag_rate"] = receiver_risk["sanctions_flag"] / receiver_risk.index.map(
            lambda x: len(self.data[self.data["receiver_country"] == x])
        )

        return {
            "total_volume": total_volume,
            "sanctioned_volume": sanctioned_volume,
            "percent_sanctioned": percent_sanctioned,
            "sender_country_risk": sender_risk.sort_values("flag_rate", ascending=False),
            "receiver_country_risk": receiver_risk.sort_values("flag_rate", ascending=False),
        }

    def sanction_exposure_by_country(self) -> pd.DataFrame:
        """
        Calculate exposure to sanctioned countries.

        :return: DataFrame containing total exposure by country
        """
        sender_exposure = self.data.groupby("sender_country")["amount"].sum()
        receiver_exposure = self.data.groupby("receiver_country")["amount"].sum()

        total_exposure = pd.concat([sender_exposure, receiver_exposure], axis=1)
        total_exposure.columns = ["Outgoing", "Incoming"]
        total_exposure["Total"] = total_exposure["Outgoing"].fillna(0) + total_exposure["Incoming"].fillna(0)

        return total_exposure.reset_index().rename(columns={"index": "Country"})