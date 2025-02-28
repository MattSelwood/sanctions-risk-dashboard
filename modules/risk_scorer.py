import numpy as np
import pandas as pd
from typing import Dict, Any

from config import RISK_CATEGORIES, PENALTY_RATES, RISK_SCORE_WEIGHTS, DEFAULT_CONFIDENCE

class RiskScorer:
    def __init__(self, transaction_data: pd.DataFrame):
        """
        Initialize the RiskScorer with transaction data.

        :param transaction_data: DataFrame containing transaction data
        """
        self.data = transaction_data
        self.risk_categories = RISK_CATEGORIES

    def _calculate_amount_risk(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate the amount risk for each transaction.

        :param data: DataFrame containing transaction data
        :return: DataFrame with amount risk scores
        """
        max_amount = data["amount"].max()
        data["amount_risk"] = data["amount"] / max_amount if max_amount else 0
        return data

    def _calculate_country_risk(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate the country risk for each transaction.

        :param data: DataFrame containing transaction data
        :return: DataFrame with country risk scores
        """
        country_risk = {}
        for country in set(data["sender_country"].tolist() + data["receiver_country"].tolist()):
            country_txns = data[(data["sender_country"] == country) | (data["receiver_country"] == country)]
            country_risk[country] = country_txns["sanctions_flag"].sum() / len(country_txns) if len(country_txns) > 0 else 0

        data["sender_country_risk"] = data["sender_country"].map(country_risk)
        data["receiver_country_risk"] = data["receiver_country"].map(country_risk)
        data["country_risk"] = data[["sender_country_risk", "receiver_country_risk"]].max(axis=1)
        return data

    def _calculate_frequency_anomaly(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate the frequency anomaly for each transaction.

        :param data: DataFrame containing transaction data
        :return: DataFrame with frequency anomaly scores
        """
        # Calculate typical frequency of transactions between sender-receiver pairs
        frequency_data = data.groupby(["sender_country", "receiver_country", pd.Grouper(key="date", freq="D")]).size().reset_index(name="frequency")
        typical_freq = frequency_data.groupby(["sender_country", "receiver_country"])["frequency"].median()

        data["typical_freq"] = data.apply(
            lambda x: typical_freq.get((x["sender_country"], x["receiver_country"]), 0),
            axis=1,
        )

        # Calculate daily frequency of transactions between sender-receiver pairs
        daily_freq = data.groupby(["sender_country", "receiver_country", data["date"].dt.date]).size().reset_index(name="daily_freq")
        daily_freq_map = daily_freq.set_index(["sender_country", "receiver_country", "date"]).to_dict()["daily_freq"]

        data["daily_freq"] = data.apply(
            lambda x: daily_freq_map.get((x["sender_country"], x["receiver_country"], x["date"].date()), 0),
            axis=1,
        )

        # Calculate frequency anomaly
        data["freq_diff"] = data["daily_freq"] - data["typical_freq"]
        max_diff = data["freq_diff"].abs().max()
        data["frequency_anomaly"] = data["freq_diff"].abs() / max_diff if max_diff else 0
        return data

    def _calculate_risk_score(self, data: pd.DataFrame, weights: Dict[str, float]) -> pd.DataFrame:
        """
        Calculate the final risk score for each transaction.

        :param data: DataFrame containing transaction data
        :param weights: Dictionary containing weights for risk factors
        :return: DataFrame with risk scores
        """
        data["risk_score"] = (
            weights["amount"] * data["amount_risk"]
            + weights["sanctions_flag"] * data["sanctions_risk"]
            + weights["country_risk"] * data["country_risk"]
            + weights["frequency_anomaly"] * data["frequency_anomaly"]
        )
        return data

    def _classify_risk_category(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Classify each transaction into a risk category.

        :param data: DataFrame containing transaction data
        :return: DataFrame with risk categories
        """
        data["risk_category"] = data["risk_score"].apply(
            lambda score: (
                "high"
                if score >= self.risk_categories["high"]
                else ("medium" if score >= self.risk_categories["medium"] else "low")
            )
        )
        return data

    def transaction_risk_scoring(self, weights: Dict[str, float] = RISK_SCORE_WEIGHTS) -> pd.DataFrame:
        """
        Score each transaction based on risk factors.

        :param weights: Optional custom weights for risk factors
        :return: DataFrame with risk scores and categories
        """
        scored_data = self.data.copy()
        scored_data = self._calculate_amount_risk(scored_data)
        scored_data["sanctions_risk"] = scored_data["sanctions_flag"]
        scored_data = self._calculate_country_risk(scored_data)
        scored_data = self._calculate_frequency_anomaly(scored_data)
        scored_data = self._calculate_risk_score(scored_data, weights)
        scored_data = self._classify_risk_category(scored_data)
        return scored_data

    def calculate_potential_penalty_exposure(self, penalty_rates: Dict[str, float] = PENALTY_RATES) -> Dict[str, Any]:
        """
        Estimate potential penalties from sanctions violations.

        :param penalty_rates: Penalty rates by violation severity
        :return: Dictionary containing penalty exposure details
        """
        if "risk_score" not in self.data.columns:
            scored_data = self.transaction_risk_scoring()
        else:
            scored_data = self.data

        scored_data["potential_penalty"] = scored_data.apply(
            lambda x: x["amount"] * penalty_rates[x["risk_category"]] if "risk_category" in scored_data.columns else 0,
            axis=1,
        )

        total_potential_penalty = scored_data["potential_penalty"].sum()
        penalty_by_category = scored_data.groupby("risk_category")["potential_penalty"].sum()
        worst_case_exposure = scored_data[scored_data["risk_score"] >= self.risk_categories["high"]]["amount"].sum()
        penalty_at_risk = np.percentile(scored_data["potential_penalty"], DEFAULT_CONFIDENCE * 100)

        return {
            "total_potential_penalty": total_potential_penalty,
            "penalty_by_category": penalty_by_category,
            "worst_case_exposure": worst_case_exposure,
            "penalty_at_risk": penalty_at_risk,
            "detailed_data": scored_data,
        }