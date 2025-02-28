import numpy as np
import plotly.graph_objects as go
import networkx as nx
from dash import Input, Output


def register_network_callbacks(app, network_analysis, scored_data):
    """
    Register callbacks related to risk metrics.

    Args:
        app (Dash): The Dash app instance
        risk_analyser (SanctionsRiskAnalyser): The risk analyser instance
    """

    # Callback to generate network graph
    @app.callback(
        Output("network-graph", "figure"),
        Input(
            "tabs", "active_tab"
        ),  # This is just a dummy input to trigger the callback
    )
    def generate_network_graph(active_tab):
        G = network_analysis["graph"]

        # Create node positions using a layout algorithm
        pos = nx.spring_layout(G)

        # Extract node and edge information
        edge_x = []
        edge_y = []
        edge_colors = []

        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

            # Edge color based on risk ratio
            risk_ratio = G[edge[0]][edge[1]]["risk_ratio"]
            edge_colors.append(risk_ratio)

        # Create edges trace
        edges_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            line=dict(width=1, color="gray"),
            hoverinfo="none",
            mode="lines",
        )

        # Create nodes trace
        node_x = []
        node_y = []
        node_text = []
        node_colors = []
        node_sizes = []

        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(node)

            # Node color based on centrality and size based on transaction volume
            centrality = network_analysis["risk_centrality"][node]
            node_colors.append(centrality)

            # Calculate total transaction volume for this country
            country_volume = scored_data[
                (scored_data["sender_country"] == node)
                | (scored_data["receiver_country"] == node)
            ]["amount"].sum()

            node_sizes.append(
                np.log1p(country_volume) * 2
            )  # Log scale for better visualization

        nodes_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers",
            hoverinfo="text",
            text=node_text,
            marker=dict(
                showscale=True,
                colorscale="Reds",
                color=node_colors,
                size=node_sizes,
                line=dict(width=2, color="white"),
            ),
        )

        # Create the figure
        fig = go.Figure(
            data=[edges_trace, nodes_trace],
            layout=go.Layout(
                title="Transaction Network (Node Size = Volume, Color = Risk Centrality)",
                showlegend=False,
                hovermode="closest",
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            ),
        )

        return fig
