import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import networkx as nx
from scipy.stats import percentileofscore


class SanctionsRiskAnalyser:
    def __init__(self, transaction_data):
        self.data = transaction_data
        self.risk_categories = {
            "high": 0.8,  # Risk score >= 0.8
            "medium": 0.5,  # Risk score >= 0.5
            "low": 0.0,  # Risk score >= 0
        }

    def calculate_exposure_metrics(self):
        """Calculate exposure metrics related to sanctions risk"""
        # Total transaction volume
        total_volume = self.data["amount"].sum()

        # Sanctioned transaction volume
        sanctioned_volume = self.data[self.data["sanctions_flag"] == 1]["amount"].sum()

        # Percent of volume with sanctions flags
        percent_sanctioned = (
            (sanctioned_volume / total_volume) * 100 if total_volume else 0
        )

        # Top risk countries (both sender and receiver)
        sender_risk = self.data.groupby("sender_country").agg(
            {"amount": "sum", "sanctions_flag": "sum"}
        )
        sender_risk["flag_rate"] = sender_risk[
            "sanctions_flag"
        ] / sender_risk.index.map(
            lambda x: len(self.data[self.data["sender_country"] == x])
        )

        receiver_risk = self.data.groupby("receiver_country").agg(
            {"amount": "sum", "sanctions_flag": "sum"}
        )
        receiver_risk["flag_rate"] = receiver_risk[
            "sanctions_flag"
        ] / receiver_risk.index.map(
            lambda x: len(self.data[self.data["receiver_country"] == x])
        )

        return {
            "total_volume": total_volume,
            "sanctioned_volume": sanctioned_volume,
            "percent_sanctioned": percent_sanctioned,
            "sender_country_risk": sender_risk.sort_values(
                "flag_rate", ascending=False
            ),
            "receiver_country_risk": receiver_risk.sort_values(
                "flag_rate", ascending=False
            ),
        }

    def sanction_exposure_by_country(self):
        """Calculate exposure to sanctioned countries"""
        # Group by country and calculate total exposure
        sender_exposure = self.data.groupby("sender_country")["amount"].sum()
        receiver_exposure = self.data.groupby("receiver_country")["amount"].sum()

        # Combine exposures (this is simplified)
        total_exposure = pd.concat([sender_exposure, receiver_exposure], axis=1)
        total_exposure.columns = ["Outgoing", "Incoming"]
        total_exposure["Total"] = total_exposure["Outgoing"].fillna(0) + total_exposure[
            "Incoming"
        ].fillna(0)

        return total_exposure.reset_index().rename(columns={"index": "Country"})

    def transaction_risk_scoring(self, weights=None):
        """
        Score each transaction based on risk factors

        Parameters:
        weights (dict): Optional custom weights for risk factors
        """
        # Default weights if not provided
        if weights is None:
            weights = {
                "amount": 0.3,  # Higher amounts = higher risk
                "sanctions_flag": 0.4,  # Direct sanctions flag
                "country_risk": 0.2,  # Country risk score
                "frequency_anomaly": 0.1,  # Unusual transaction patterns
            }

        # Create a copy to add risk scores
        scored_data = self.data.copy()

        # 1. Amount risk - normalize and scale the transaction amounts
        max_amount = scored_data["amount"].max()
        scored_data["amount_risk"] = (
            scored_data["amount"] / max_amount if max_amount else 0
        )

        # 2. Sanctions flag risk - direct binary score
        scored_data["sanctions_risk"] = scored_data["sanctions_flag"]

        # 3. Country risk - based on the proportion of flagged transactions per country
        country_risk = {}
        for country in set(
            scored_data["sender_country"].tolist()
            + scored_data["receiver_country"].tolist()
        ):
            country_txns = scored_data[
                (scored_data["sender_country"] == country)
                | (scored_data["receiver_country"] == country)
            ]
            if len(country_txns) > 0:
                country_risk[country] = country_txns["sanctions_flag"].sum() / len(
                    country_txns
                )
            else:
                country_risk[country] = 0

        scored_data["sender_country_risk"] = scored_data["sender_country"].map(
            country_risk
        )
        scored_data["receiver_country_risk"] = scored_data["receiver_country"].map(
            country_risk
        )
        scored_data["country_risk"] = scored_data[
            ["sender_country_risk", "receiver_country_risk"]
        ].max(axis=1)

        # 4. Frequency anomaly - identify unusual patterns
        # Group by sender/receiver pair and date to find frequency
        frequency_data = (
            scored_data.groupby(
                ["sender_country", "receiver_country", pd.Grouper(key="date", freq="D")]
            )
            .size()
            .reset_index(name="frequency")
        )

        # Calculate typical frequency for each country pair
        typical_freq = frequency_data.groupby(["sender_country", "receiver_country"])[
            "frequency"
        ].median()

        # Map back to each transaction
        scored_data["typical_freq"] = scored_data.apply(
            lambda x: typical_freq.get((x["sender_country"], x["receiver_country"]), 0),
            axis=1,
        )

        # Calculate daily frequency
        daily_freq = (
            scored_data.groupby(
                ["sender_country", "receiver_country", scored_data["date"].dt.date]
            )
            .size()
            .reset_index(name="daily_freq")
        )
        daily_freq_map = daily_freq.set_index(
            ["sender_country", "receiver_country", "date"]
        ).to_dict()["daily_freq"]

        # Calculate frequency anomaly score
        scored_data["daily_freq"] = scored_data.apply(
            lambda x: daily_freq_map.get(
                (x["sender_country"], x["receiver_country"], x["date"].date()), 0
            ),
            axis=1,
        )

        # Normalize anomaly score (higher anomaly = higher risk)
        scored_data["freq_diff"] = (
            scored_data["daily_freq"] - scored_data["typical_freq"]
        )
        max_diff = scored_data["freq_diff"].abs().max()
        scored_data["frequency_anomaly"] = (
            scored_data["freq_diff"].abs() / max_diff if max_diff else 0
        )

        # Calculate final risk score as weighted sum of risk factors
        scored_data["risk_score"] = (
            weights["amount"] * scored_data["amount_risk"]
            + weights["sanctions_flag"] * scored_data["sanctions_risk"]
            + weights["country_risk"] * scored_data["country_risk"]
            + weights["frequency_anomaly"] * scored_data["frequency_anomaly"]
        )

        # Classify into risk categories
        scored_data["risk_category"] = scored_data["risk_score"].apply(
            lambda score: (
                "high"
                if score >= self.risk_categories["high"]
                else ("medium" if score >= self.risk_categories["medium"] else "low")
            )
        )

        return scored_data

    def calculate_potential_penalty_exposure(self, penalty_rates=None):
        """
        Estimate potential penalties from sanctions violations

        Parameters:
        penalty_rates (dict): Penalty rates by violation severity
        """
        if penalty_rates is None:
            penalty_rates = {
                "high": 1.0,  # 100% of transaction amount
                "medium": 0.5,  # 50% of transaction amount
                "low": 0.1,  # 10% of transaction amount
            }

        # Score transactions if not already done
        if "risk_score" not in self.data.columns:
            scored_data = self.transaction_risk_scoring()
        else:
            scored_data = self.data

        # Calculate potential penalty for each transaction
        scored_data["potential_penalty"] = scored_data.apply(
            lambda x: (
                x["amount"] * penalty_rates[x["risk_category"]]
                if "risk_category" in scored_data.columns
                else 0
            ),
            axis=1,
        )

        # Summary statistics
        total_potential_penalty = scored_data["potential_penalty"].sum()
        penalty_by_category = scored_data.groupby("risk_category")[
            "potential_penalty"
        ].sum()
        worst_case_exposure = scored_data[
            scored_data["risk_score"] >= self.risk_categories["high"]
        ]["amount"].sum()

        # Calculate penalty at risk similar to VaR concept
        # This represents the potential penalty amount that won't be exceeded with 95% confidence
        penalty_at_risk = np.percentile(scored_data["potential_penalty"], 95)

        return {
            "total_potential_penalty": total_potential_penalty,
            "penalty_by_category": penalty_by_category,
            "worst_case_exposure": worst_case_exposure,
            "penalty_at_risk": penalty_at_risk,
            "detailed_data": scored_data,
        }

    def network_risk_analysis(self):
        """Perform network analysis to identify risky transaction patterns"""
        # Create a directed graph of transactions
        G = nx.DiGraph()

        # Add nodes (countries)
        countries = set(
            self.data["sender_country"].tolist()
            + self.data["receiver_country"].tolist()
        )
        for country in countries:
            G.add_node(country)

        # Add edges (transactions)
        for _, row in self.data.iterrows():
            sender = row["sender_country"]
            receiver = row["receiver_country"]
            amount = row["amount"]
            sanctions_flag = row["sanctions_flag"]

            # Check if edge already exists
            if G.has_edge(sender, receiver):
                # Update existing edge
                G[sender][receiver]["transactions"] += 1
                G[sender][receiver]["total_amount"] += amount
                G[sender][receiver]["flagged_transactions"] += sanctions_flag
            else:
                # Create new edge
                G.add_edge(
                    sender,
                    receiver,
                    transactions=1,
                    total_amount=amount,
                    flagged_transactions=sanctions_flag,
                )

        # Calculate risk metrics for each edge
        for u, v, data in G.edges(data=True):
            data["risk_ratio"] = (
                data["flagged_transactions"] / data["transactions"]
                if data["transactions"] > 0
                else 0
            )

        # Find high-risk paths (paths that involve multiple high-risk countries)
        high_risk_countries = [
            c
            for c in countries
            if self.data[self.data["sender_country"] == c]["sanctions_flag"].sum()
            / len(self.data[self.data["sender_country"] == c])
            > 0.5
        ]

        high_risk_paths = []
        for source in high_risk_countries:
            for target in countries:
                if source != target:
                    try:
                        paths = list(nx.all_simple_paths(G, source, target, cutoff=3))
                        if paths:
                            high_risk_paths.extend(paths)
                    except:
                        # Path may not exist
                        continue

        # Calculate centrality metrics to identify key risk nodes
        betweenness = nx.betweenness_centrality(G, weight="risk_ratio")

        return {
            "graph": G,
            "high_risk_countries": high_risk_countries,
            "high_risk_paths": high_risk_paths,
            "risk_centrality": betweenness,
        }

    def anomaly_detection(self):
        """Detect anomalous transactions that may indicate sanctions evasion"""
        # Create a copy of data for analysis
        data = self.data.copy()

        # Feature engineering
        data["day_of_week"] = data["date"].dt.dayofweek
        data["hour"] = data["date"].dt.hour
        data["month"] = data["date"].dt.month

        # Calculate statistics for sender-receiver pairs
        pair_stats = data.groupby(["sender_country", "receiver_country"]).agg(
            {"amount": ["mean", "std", "count"], "sanctions_flag": "sum"}
        )

        pair_stats.columns = [
            "_".join(col).strip() for col in pair_stats.columns.values
        ]
        pair_stats.reset_index(inplace=True)

        # Merge back to original data
        data = pd.merge(
            data, pair_stats, on=["sender_country", "receiver_country"], how="left"
        )

        # Calculate z-score for amount to identify unusual transaction amounts
        data["amount_zscore"] = (data["amount"] - data["amount_mean"]) / data[
            "amount_std"
        ].replace(0, 1)

        # Calculate transaction frequency anomaly
        data["freq_percentile"] = data.apply(
            lambda x: percentileofscore(
                data[
                    (data["sender_country"] == x["sender_country"])
                    & (data["receiver_country"] == x["receiver_country"])
                ]["amount"],
                x["amount"],
            ),
            axis=1,
        )

        # Flag anomalies
        data["amount_anomaly"] = (data["amount_zscore"].abs() > 3) | (
            data["freq_percentile"] > 95
        )

        # Prepare features for clustering
        features = [
            "amount",
            "amount_zscore",
            "amount_count",
            "sanctions_flag_sum",
            "day_of_week",
            "hour",
            "month",
        ]

        # Standardize features
        data = data.dropna()
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(data[features])

        # Apply K-means clustering
        kmeans = KMeans(n_clusters=3, random_state=42)
        data["cluster"] = kmeans.fit_predict(scaled_features)

        # Identify the high-risk cluster (most sanctions flags)
        cluster_risk = data.groupby("cluster")["sanctions_flag"].mean()
        high_risk_cluster = cluster_risk.idxmax()

        # Mark transactions in high-risk cluster
        data["high_risk_pattern"] = data["cluster"] == high_risk_cluster

        # Final anomaly score combining all factors
        data["anomaly_score"] = (
            data["amount_zscore"].abs() * 0.3
            + (data["freq_percentile"] / 100) * 0.3
            + data["high_risk_pattern"].astype(int) * 0.4
        )

        # Identify top anomalies
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
            "cluster_profiles": data.groupby("cluster")[features].mean(),
        }

    def scenario_analysis(self, scenarios=None):
        """
        Analyze impact of different sanctions scenarios

        Parameters:
        scenarios (dict): Dictionary of scenario descriptions and affected countries
        """
        if scenarios is None:
            scenarios = {
                "new_sanctions_scenario_1": ["CountryA", "CountryB"],
                "increased_scrutiny_scenario": ["CountryC", "CountryD", "CountryE"],
                "sanctions_lifting_scenario": ["CountryF"],
            }

        results = {}

        for scenario_name, affected_countries in scenarios.items():
            # Create a copy of data with modified sanctions flags based on scenario
            scenario_data = self.data.copy()

            if "new_sanctions" in scenario_name:
                # Add sanctions flags to transactions involving newly sanctioned countries
                scenario_data.loc[
                    (scenario_data["sender_country"].isin(affected_countries))
                    | (scenario_data["receiver_country"].isin(affected_countries)),
                    "sanctions_flag",
                ] = 1

            elif "increased_scrutiny" in scenario_name:
                # Weight transactions with these countries higher in risk calculations
                scenario_data["scrutiny_factor"] = scenario_data.apply(
                    lambda x: (
                        1.5
                        if x["sender_country"] in affected_countries
                        or x["receiver_country"] in affected_countries
                        else 1.0
                    ),
                    axis=1,
                )

            elif "sanctions_lifting" in scenario_name:
                # Remove sanctions flags from transactions with countries where sanctions were lifted
                scenario_data.loc[
                    (scenario_data["sender_country"].isin(affected_countries))
                    & (scenario_data["receiver_country"].isin(affected_countries)),
                    "sanctions_flag",
                ] = 0

            # Calculate impact metrics
            scenario_analyzer = SanctionsRiskAnalyser(scenario_data)
            exposure_metrics = scenario_analyzer.calculate_exposure_metrics()
            penalty_exposure = scenario_analyzer.calculate_potential_penalty_exposure()

            # Store results
            results[scenario_name] = {
                "affected_countries": affected_countries,
                "flagged_transaction_count": scenario_data["sanctions_flag"].sum(),
                "flagged_transaction_amount": scenario_data[
                    scenario_data["sanctions_flag"] == 1
                ]["amount"].sum(),
                "percent_sanctioned": exposure_metrics["percent_sanctioned"],
                "potential_penalty": penalty_exposure["total_potential_penalty"],
            }

        return results

    def compliance_risk_report(self):
        """Generate a comprehensive compliance risk report"""
        # Run all analyses
        exposure_metrics = self.calculate_exposure_metrics()
        scored_transactions = self.transaction_risk_scoring()
        penalty_exposure = self.calculate_potential_penalty_exposure()

        # Compliance metrics
        high_risk_volume = scored_transactions[
            scored_transactions["risk_category"] == "high"
        ]["amount"].sum()
        percent_high_risk = (
            (high_risk_volume / exposure_metrics["total_volume"]) * 100
            if exposure_metrics["total_volume"]
            else 0
        )

        # Country risk assessment
        combined_country_risk = {}
        for country in set(
            self.data["sender_country"].tolist()
            + self.data["receiver_country"].tolist()
        ):
            country_data = self.data[
                (self.data["sender_country"] == country)
                | (self.data["receiver_country"] == country)
            ]
            combined_country_risk[country] = {
                "transaction_count": len(country_data),
                "total_amount": country_data["amount"].sum(),
                "flagged_count": country_data["sanctions_flag"].sum(),
                "flag_rate": (
                    country_data["sanctions_flag"].sum() / len(country_data)
                    if len(country_data) > 0
                    else 0
                ),
            }

        # Convert to dataframe for easier handling
        country_risk_df = pd.DataFrame.from_dict(combined_country_risk, orient="index")
        country_risk_df.sort_values("flag_rate", ascending=False, inplace=True)

        # Time trend analysis
        time_trend = self.data.groupby(self.data["date"].dt.date).agg(
            {"amount": "sum", "sanctions_flag": "sum"}
        )
        time_trend["flag_ratio"] = time_trend["sanctions_flag"] / time_trend.index.map(
            lambda x: len(self.data[self.data["date"].dt.date == x])
        )

        # Generate final report
        report = {
            "summary_metrics": {
                "total_transaction_volume": exposure_metrics["total_volume"],
                "sanctioned_volume": exposure_metrics["sanctioned_volume"],
                "percent_sanctioned": exposure_metrics["percent_sanctioned"],
                "high_risk_volume": high_risk_volume,
                "percent_high_risk": percent_high_risk,
                "potential_penalty_exposure": penalty_exposure[
                    "total_potential_penalty"
                ],
                "penalty_at_risk": penalty_exposure["penalty_at_risk"],
            },
            "risk_by_category": {
                "high": {
                    "transaction_count": len(
                        scored_transactions[
                            scored_transactions["risk_category"] == "high"
                        ]
                    ),
                    "volume": scored_transactions[
                        scored_transactions["risk_category"] == "high"
                    ]["amount"].sum(),
                    "potential_penalty": penalty_exposure["penalty_by_category"].get(
                        "high", 0
                    ),
                },
                "medium": {
                    "transaction_count": len(
                        scored_transactions[
                            scored_transactions["risk_category"] == "medium"
                        ]
                    ),
                    "volume": scored_transactions[
                        scored_transactions["risk_category"] == "medium"
                    ]["amount"].sum(),
                    "potential_penalty": penalty_exposure["penalty_by_category"].get(
                        "medium", 0
                    ),
                },
                "low": {
                    "transaction_count": len(
                        scored_transactions[
                            scored_transactions["risk_category"] == "low"
                        ]
                    ),
                    "volume": scored_transactions[
                        scored_transactions["risk_category"] == "low"
                    ]["amount"].sum(),
                    "potential_penalty": penalty_exposure["penalty_by_category"].get(
                        "low", 0
                    ),
                },
            },
            "highest_risk_countries": country_risk_df.head(10).to_dict("index"),
            "time_trend": time_trend.to_dict("index"),
            "top_risky_transactions": scored_transactions.sort_values(
                "risk_score", ascending=False
            ).head(20),
        }

        return report
