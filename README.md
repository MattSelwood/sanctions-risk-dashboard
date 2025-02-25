# Sanctions Risk Dashboard

A Python-based toy analytics dashboard for monitoring and analysing economic sanctions risk exposure in financial transactions.


## Overview

This project provides a complete end-to-end solution for analysing transaction data to identify, quantify, and visualize potential sanctions compliance risks. It demonstrates key skills relevant to a Junior Risk Analyst position in economic sanctions compliance at a financial institution.
 

 ## Features

 - **Transaction Risk Flagging:** Automatically identifies transactions involving sanctioned countries or entities
 - **Advanced Risk Metrics:** Calculates Value-at-Risk (VaR) and Expected Shortfall using multiple methodologies
 - **Interactive Data Visualization:** Provides a comprehensive dashboard with multiple views of risk exposure
 - **Filtering and Drill-Down:** Allows detailed analysis of specific countries, time periods, and transaction sizes
 - **Time-Series Analysis:** Tracks sanctions exposure trends over time


## Components

1. **Data Generation & Processing Module**
    - Synthetic transaction data creation
    - Sanctions screening simulation
    - Data cleaning and preparation


2. **Risk Analysis Engine**
    - Historical VaR calculation
    - Parametric VaR calculation
    - Monte Carlo VaR simulation
    - Expected Shortfall (Conditional VaR) analysis
    - Country exposure aggregation


3. **Dashboard Interface**
    - Key risk metrics display
    - Country exposure visualization
    - Transaction volume trends
    - Interactive transaction filtering
    - Risk heatmap generation


## Technology Stack

- **Python:** Core programming language
- **Pandas & NumPy:** Data manipulation and numerical analysis
- **SciPy:** Statistical calculations
- **Plotly Dash:** Interactive dashboard framework
- **Plotly Express:** Data visualization

## Getting Started

### Prerequisites

- Python 3.7+
- Pipenv package manager

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/MattSelwood/sanctions-risk-dashboard.git
   cd sanctions-risk-dashboard
   ```

2. Create a virtual environment and install required packages with pipenv (optional but recommended):
   ```bash
   pipenv install
   pipenv shell
   ```

### Running the Dashboard

Execute the main Python script:
```bash
python app.py
```

The dashboard will be accessible at http://127.0.0.1:8050/ in your web browser.

## Usage Guide

### Dashboard Navigation

The dashboard consists of several sections:

1. **Key Metrics Panel**: Shows VaR and Expected Shortfall values
2. **Country Exposure Chart**: Displays transaction volume by country
3. **Time Series Analysis**: Shows transaction trends over time
4. **Transaction Table**: Lists flagged transactions with filtering options
5. **Risk Heatmap**: Visualizes country-to-country risk patterns

### Filtering Data

- Use the country dropdown to focus on specific countries
- Adjust the amount slider to filter transactions by value
- Table will automatically update based on your selections

## Project Structure

```
sanctions_dashboard/
│
├── app.py                   # Main entry point that runs the server
├── config.py                # Configuration constants
├── offline_analysis.py      # Script to run an offline version of the analysis
│
├── assets/                  # CSS, images, and other static files
│   └── styles.css           # Custom styling
│
├── modules/                 # Main financial calculations
│   ├── data.py              # Data generation / pulling scripts
│   ├── riskanalysis.py      # Risk analysis engine class
│   └── utils.py             # Utilities
│
├── components/              # Reusable UI components
│   ├── header.py            # Header components
│   ├── metrics.py           # Risk metrics components
│   ├── charts.py            # Chart components
│   └── transactions.py      # Transaction table and filters
│
├── data/                    # Data handling
│   ├── loader.py            # Data loading functions
│   └── processor.py         # Data processing functions
│
├── callbacks/               # App callbacks
│   ├── metrics_callbacks.py # Callbacks for risk metrics
│   └── filter_callbacks.py  # Callbacks for data filtering
│
├── Pipfile                  # Pipfile for use with pipenv
├── Pipfile.lock             # Pipfile.lock for use with pipenv
├── README.md                # Project documentation
├── LICENSE                  # License information
├── .gitattributes           # Git attributes
└── .gitignore               # Git ignore
```


## Future Enhancements

- **Incorporate Actual Sanctions List and Name Screening Algorithm**: Implement fuzzy matching for counterparty names against real sanctions lists
- **Backtesting Module**: Add capability to validate VaR models against historical data
- **Stress Testing**: Implement scenarios to test portfolio resilience

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

*Note/Disclaimer: This project is for educational and demonstration purposes only. It should not be used as the sole basis for sanctions compliance without proper validation and customisation to meet specific regulatory requirements.*
