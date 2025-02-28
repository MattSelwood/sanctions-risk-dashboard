import pandas as pd
import networkx as nx

class NetworkAnalyser:
    def __init__(self, transaction_data: pd.DataFrame):
        self.data = transaction_data

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