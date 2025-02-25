"""
Data loading functions for the Sanctions Dashboard.
"""

import pandas as pd
from modules.riskanalysis import SanctionsRiskAnalyser
from modules.data import generate_transaction_data
from config import DEFAULT_CONFIDENCE, DEFAULT_SAMPLE_SIZE


def load_transaction_data(sample_size=DEFAULT_SAMPLE_SIZE):
    """
    Load transaction data for the dashboard.

    Args:
        sample_size (int): Number of transactions to generate

    Returns:
        DataFrame: Generated transaction data
    """
    return generate_transaction_data(sample_size)


def initialise_data(
    sample_size=DEFAULT_SAMPLE_SIZE, confidence_level=DEFAULT_CONFIDENCE
):
    """
    Initialize all data needed for the dashboard.

    Args:
        sample_size (int): Number of transactions to generate
        confidence_level (float): Confidence level for risk calculations

    Returns:
        tuple: (transactions DataFrame, risk_analyser object, initial_report dict)
    """
    # Generate transaction data
    transactions = load_transaction_data(sample_size)

    # Initialize risk analyser
    risk_analyser = SanctionsRiskAnalyser(transactions)

    # Generate initial risk report
    initial_report = risk_analyser.generate_risk_report(
        confidence_level=confidence_level
    )

    return transactions, risk_analyser, initial_report


def get_unique_countries(transactions):
    """
    Get list of unique countries from transaction data.

    Args:
        transactions (DataFrame): Transaction data

    Returns:
        list: List of unique countries
    """
    sender_countries = set(transactions["sender_country"].unique())
    receiver_countries = set(transactions["receiver_country"].unique())

    # Combine and sort
    all_countries = sorted(list(sender_countries.union(receiver_countries)))

    return all_countries
