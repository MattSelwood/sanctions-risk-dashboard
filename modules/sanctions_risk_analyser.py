import pandas as pd
from typing import Dict, Any

from config import RISK_CATEGORIES, RISK_SCORE_WEIGHTS, PENALTY_RATES
from modules.exposure_metrics_calculator import ExposureMetricsCalculator
from modules.risk_scorer import RiskScorer
from modules.network_analyser import NetworkAnalyser
from modules.anomaly_detector import AnomalyDetector

class SanctionsRiskAnalyser:
    def __init__(self, transaction_data: pd.DataFrame):
        """
        Initialize the SanctionsRiskAnalyser with transaction data.

        :param transaction_data: DataFrame containing transaction data
        """
        self.data = transaction_data
        self.risk_categories = RISK_CATEGORIES
        self.exposure_calculator = ExposureMetricsCalculator(transaction_data)
        self.risk_scorer = RiskScorer(transaction_data)
        self.network_analyser = NetworkAnalyser(transaction_data)
        self.anomaly_detector = AnomalyDetector(transaction_data)

    def calculate_exposure_metrics(self) -> Dict[str, Any]:
        """
        Calculate exposure metrics related to sanctions risk.

        :return: Dictionary containing exposure metrics
        """
        return self.exposure_calculator.calculate_exposure_metrics()

    def sanction_exposure_by_country(self) -> pd.DataFrame:
        """
        Calculate exposure to sanctioned countries.

        :return: DataFrame containing total exposure by country
        """
        return self.exposure_calculator.sanction_exposure_by_country()

    def transaction_risk_scoring(self, weights: Dict[str, float] = RISK_SCORE_WEIGHTS) -> pd.DataFrame:
        """
        Score each transaction based on risk factors.

        :param weights: Optional custom weights for risk factors
        :return: DataFrame with risk scores and categories
        """
        return self.risk_scorer.transaction_risk_scoring(weights)

    def calculate_potential_penalty_exposure(self, penalty_rates: Dict[str, float] = PENALTY_RATES) -> Dict[str, Any]:
        """
        Estimate potential penalties from sanctions violations.

        :param penalty_rates: Penalty rates by violation severity
        :return: Dictionary containing penalty exposure details
        """
        return self.risk_scorer.calculate_potential_penalty_exposure(penalty_rates)

    def network_risk_analysis(self) -> Dict[str, Any]:
        """
        Perform network analysis to identify risky transaction patterns.

        :return: Dictionary containing network risk analysis results
        """
        return self.network_analyser.network_risk_analysis()

    def anomaly_detection(self) -> Dict[str, Any]:
        """
        Detect anomalous transactions that may indicate sanctions evasion.

        :return: Dictionary containing anomaly detection results
        """
        return self.anomaly_detector.anomaly_detection()

    def compliance_risk_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive compliance risk report.

        :return: Dictionary containing the compliance risk report
        """
        exposure_metrics = self.calculate_exposure_metrics()
        scored_transactions = self.transaction_risk_scoring()
        penalty_exposure = self.calculate_potential_penalty_exposure()

        high_risk_volume = scored_transactions[scored_transactions["risk_category"] == "high"]["amount"].sum()
        percent_high_risk = (high_risk_volume / exposure_metrics["total_volume"]) * 100 if exposure_metrics["total_volume"] else 0

        combined_country_risk = {}
        for country in set(self.data["sender_country"].tolist() + self.data["receiver_country"].tolist()):
            country_data = self.data[(self.data["sender_country"] == country) | (self.data["receiver_country"] == country)]
            combined_country_risk[country] = {
                "transaction_count": len(country_data),
                "total_amount": country_data["amount"].sum(),
                "flagged_count": country_data["sanctions_flag"].sum(),
                "flag_rate": country_data["sanctions_flag"].sum() / len(country_data) if len(country_data) > 0 else 0,
            }

        country_risk_df = pd.DataFrame.from_dict(combined_country_risk, orient="index")
        country_risk_df.sort_values("flag_rate", ascending=False, inplace=True)

        time_trend = self.data.groupby(self.data["date"].dt.date).agg({"amount": "sum", "sanctions_flag": "sum"})
        time_trend["flag_ratio"] = time_trend["sanctions_flag"] / time_trend.index.map(
            lambda x: len(self.data[self.data["date"].dt.date == x])
        )

        report = {
            "summary_metrics": {
                "total_transaction_volume": exposure_metrics["total_volume"],
                "sanctioned_volume": exposure_metrics["sanctioned_volume"],
                "percent_sanctioned": exposure_metrics["percent_sanctioned"],
                "high_risk_volume": high_risk_volume,
                "percent_high_risk": percent_high_risk,
                "potential_penalty_exposure": penalty_exposure["total_potential_penalty"],
                "penalty_at_risk": penalty_exposure["penalty_at_risk"],
            },
            "risk_by_category": {
                "high": {
                    "transaction_count": len(scored_transactions[scored_transactions["risk_category"] == "high"]),
                    "volume": scored_transactions[scored_transactions["risk_category"] == "high"]["amount"].sum(),
                    "potential_penalty": penalty_exposure["penalty_by_category"].get("high", 0),
                },
                "medium": {
                    "transaction_count": len(scored_transactions[scored_transactions["risk_category"] == "medium"]),
                    "volume": scored_transactions[scored_transactions["risk_category"] == "medium"]["amount"].sum(),
                    "potential_penalty": penalty_exposure["penalty_by_category"].get("medium", 0),
                },
                "low": {
                    "transaction_count": len(scored_transactions[scored_transactions["risk_category"] == "low"]),
                    "volume": scored_transactions[scored_transactions["risk_category"] == "low"]["amount"].sum(),
                    "potential_penalty": penalty_exposure["penalty_by_category"].get("low", 0),
                },
            },
            "highest_risk_countries": country_risk_df.head(10).to_dict("index"),
            "time_trend": time_trend.to_dict("index"),
            "top_risky_transactions": scored_transactions.sort_values("risk_score", ascending=False).head(20),
        }

        return report
