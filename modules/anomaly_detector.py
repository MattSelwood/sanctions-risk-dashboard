import pandas as pd
from scipy.stats import percentileofscore
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from typing import Dict, Any

class AnomalyDetector:
    def __init__(self, transaction_data: pd.DataFrame):
        """
        Initialize the AnomalyDetector with transaction data.

        :param transaction_data: DataFrame containing transaction data
        """
        self.data = transaction_data

    def _feature_engineering(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Perform feature engineering on the transaction data.

        :param data: DataFrame containing transaction data
        :return: DataFrame with new features
        """
        data["day_of_week"] = data["date"].dt.dayofweek
        data["hour"] = data["date"].dt.hour
        data["month"] = data["date"].dt.month
        return data

    def _calculate_pair_stats(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate statistics for sender-receiver pairs.

        :param data: DataFrame containing transaction data
        :return: DataFrame with pair statistics
        """
        pair_stats = data.groupby(["sender_country", "receiver_country"]).agg(
            {"amount": ["mean", "std", "count"], "sanctions_flag": "sum"}
        )
        pair_stats.columns = ["_".join(col).strip() for col in pair_stats.columns.values]
        pair_stats.reset_index(inplace=True)
        return pair_stats

    def _calculate_anomalies(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate anomalies in the transaction data.

        :param data: DataFrame containing transaction data
        :return: DataFrame with anomaly scores
        """
        data["amount_zscore"] = (data["amount"] - data["amount_mean"]) / data["amount_std"].replace(0, 1)
        data["freq_percentile"] = data.apply(
            lambda x: percentileofscore(
                data[(data["sender_country"] == x["sender_country"]) & (data["receiver_country"] == x["receiver_country"])]["amount"],
                x["amount"],
            ),
            axis=1,
        )
        data["amount_anomaly"] = (data["amount_zscore"].abs() > 3) | (data["freq_percentile"] > 95)
        return data

    def _prepare_features_for_clustering(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare features for clustering.

        :param data: DataFrame containing transaction data
        :return: DataFrame with standardized features
        """
        features = ["amount", "amount_zscore", "amount_count", "sanctions_flag_sum", "day_of_week", "hour", "month"]
        data = data.fillna(0)
        scaler = StandardScaler()
        data[features] = scaler.fit_transform(data[features])
        return data

    def _apply_clustering(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Apply K-means clustering to the transaction data.

        :param data: DataFrame containing transaction data
        :return: DataFrame with cluster labels
        """
        kmeans = KMeans(n_clusters=3, random_state=42)
        data["cluster"] = kmeans.fit_predict(data[["amount", "amount_zscore", "amount_count", "sanctions_flag_sum", "day_of_week", "hour", "month"]])
        return data

    def _identify_high_risk_cluster(self, data: pd.DataFrame) -> int:
        """
        Identify the high-risk cluster based on sanctions flags.

        :param data: DataFrame containing transaction data
        :return: Cluster label of the high-risk cluster
        """
        cluster_risk = data.groupby("cluster")["sanctions_flag"].mean()
        return cluster_risk.idxmax()

    def anomaly_detection(self) -> Dict[str, Any]:
        """
        Detect anomalous transactions that may indicate sanctions evasion.

        :return: Dictionary containing anomaly data, top anomalies, high-risk cluster, and cluster profiles
        """
        data = self.data.copy()
        data = self._feature_engineering(data)
        pair_stats = self._calculate_pair_stats(data)
        data = pd.merge(data, pair_stats, on=["sender_country", "receiver_country"], how="left")
        data = self._calculate_anomalies(data)
        cluster_data = self._prepare_features_for_clustering(data)
        cluster_data = self._apply_clustering(cluster_data)
        high_risk_cluster = self._identify_high_risk_cluster(cluster_data)
        data["cluster"] = cluster_data["cluster"]
        data["high_risk_pattern"] = cluster_data["cluster"] == high_risk_cluster
        data["anomaly_score"] = (
            data["amount_zscore"].abs() * 0.3
            + (data["freq_percentile"] / 100) * 0.3
            + data["high_risk_pattern"].astype(int) * 0.4
        )
        top_anomalies = data.sort_values("anomaly_score", ascending=False).head(20)
        return {
            "anomaly_data": data[
                [
                    "date",
                    "sender_country",
                    "receiver_country",
                    "amount",
                    "sanctions_flag",
                    "amount_zscore",
                    "freq_percentile",
                    "high_risk_pattern",
                    "anomaly_score",
                ]
            ],
            "top_anomalies": top_anomalies,
            "high_risk_cluster": high_risk_cluster,
            "cluster_profiles": data.groupby("cluster")[["amount", "amount_zscore", "amount_count", "sanctions_flag_sum", "day_of_week", "hour", "month"]].mean(),
        }