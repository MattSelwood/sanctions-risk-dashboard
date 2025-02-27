"""
Data loading functions for the Sanctions Dashboard.
"""

import pandas as pd
from modules.riskanalysis import SanctionsRiskAnalyser
from modules.data import generate_transaction_data
from config import DEFAULT_SAMPLE_SIZE


def load_transaction_data(sample_size=DEFAULT_SAMPLE_SIZE):
    """
    Load transaction data for the dashboard.

    Args:
        sample_size (int): Number of transactions to generate

    Returns:
        DataFrame: Generated transaction data
    """
    return generate_transaction_data(sample_size)


def initialise_data():
    """
    Initialize all data needed for the dashboard.

    Returns:
        tuple: (transactions DataFrame, risk_analyser object, initial_report dict)
    """
    # Generate transaction data
    # Initialize the sample data and analyzer
    transactions = load_transaction_data()
    analyser = SanctionsRiskAnalyser(transactions)

    # Run the analyses
    scored_data = analyser.transaction_risk_scoring()
    exposure_metrics = analyser.calculate_exposure_metrics()
    country_exposure = analyser.sanction_exposure_by_country()
    penalty_exposure = analyser.calculate_potential_penalty_exposure()
    anomaly_data = analyser.anomaly_detection()
    network_analysis = analyser.network_risk_analysis()
    compliance_report = analyser.compliance_risk_report()
    return (
        transactions,
        analyser,
        scored_data,
        exposure_metrics,
        country_exposure,
        penalty_exposure,
        anomaly_data,
        network_analysis,
        compliance_report,
    )
