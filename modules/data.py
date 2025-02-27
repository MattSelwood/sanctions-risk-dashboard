import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta

from config import RANDOM_SEED

def get_ofac_data():
    # URL for OFAC SDN list (XML format)
    ofac_url = "https://www.treasury.gov/ofac/downloads/sdn.xml"

    try:
        # Download the data
        response = requests.get(ofac_url)

        if response.status_code == 200:
            # Parse XML data
            # Note: In a real project, you'd want to use a proper XML parser
            sdn_data = pd.read_xml(response.content)
            return sdn_data
        else:
            print(f"Failed to retrieve data: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None


# Generate synthetic transaction data
def generate_transaction_data(num_transactions=1000):
    np.random.seed(RANDOM_SEED)  # For reproducibility

    countries = [
        "USA",
        "UK",
        "France",
        "Germany",
        "Italy",
        "Japan",
        "China",
        "Russia",
        "Iran",
        "Venezuela",
        "Cuba",
        "Syria",
        "North Korea",
    ]
    high_risk_countries = [
        "Iran",
        "Russia",
        "Venezuela",
        "Cuba",
        "Syria",
        "North Korea",
    ]
    transaction_probabilities = [
        0.25,  # USA
        0.15,  # UK
        0.10,  # France
        0.10,  # Germany
        0.07,  # Italy
        0.08,  # Japan
        0.10,  # China
        0.05,  # Russia
        0.03,  # Iran
        0.02,  # Venezuela
        0.02,  # Cuba
        0.02,  # Syria
        0.01,  # North Korea
    ]

    # Generate dates over past year
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    dates = pd.date_range(start=start_date, end=end_date, periods=num_transactions)


    # Generate transaction data
    transactions = {
        "transaction_id": range(1, num_transactions + 1),
        "date": np.random.choice(dates, num_transactions),
        "amount": np.random.exponential(scale=10000, size=num_transactions),
        "sender_country": np.random.choice(
            countries,
            num_transactions,
            p=transaction_probabilities,
        ),
        "receiver_country": np.random.choice(
            countries,
            num_transactions,
            p=transaction_probabilities,
        ),
    }

    # Create DataFrame
    df = pd.DataFrame(transactions)

    # Flag high-risk transactions (those involving sanctioned countries)
    df["sanctions_flag"] = df.apply(
        lambda x: (
            1
            if x["sender_country"] in high_risk_countries
            or x["receiver_country"] in high_risk_countries
            else 0
        ),
        axis=1,
    )

    return df
