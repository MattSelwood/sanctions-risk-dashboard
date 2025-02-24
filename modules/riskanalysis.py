import pandas as pd
import numpy as np
from scipy import stats


class SanctionsRiskAnalyser:
    def __init__(self, transaction_data):
        self.data = transaction_data
        self.portfolio_values = None
        self.confidence_level = 0.95
        self.latest_value = None
        self.daily_returns = None

    def prepare_portfolio_data(self, lookback_days=252):
        """Prepare daily portfolio values based on transaction data"""
        # Group data by date to get daily totals
        daily_data = self.data.groupby("date")["amount"].sum().tail(lookback_days)

        # Create a series of daily returns
        daily_returns = daily_data.pct_change().dropna()

        # Store latest portfolio value
        self.latest_value = daily_data.iloc[-1]
        self.daily_returns = daily_returns

        return daily_returns

    def calculate_var(self, confidence_level=0.95, method="historical"):
        """Calculate Value at Risk"""
        if self.daily_returns is None:
            self.prepare_portfolio_data()

        if method == "historical":
            # Historical VaR
            var = np.percentile(self.daily_returns, 100 * (1 - confidence_level))

        elif method == "parametric":
            # Parametric VaR (assumes normal distribution)
            mean = self.daily_returns.mean()
            std = self.daily_returns.std()
            var = stats.norm.ppf(1 - confidence_level, mean, std)

        elif method == "monte_carlo":
            # Monte Carlo simulation (simplified)
            mean = self.daily_returns.mean()
            std = self.daily_returns.std()
            simulations = 10_000
            simulated_returns = np.random.normal(mean, std, simulations)
            var = np.percentile(simulated_returns, 100 * (1 - confidence_level))

        # Convert percentage to dollar amount based on latest portfolio value
        var_amount = abs(var * self.latest_value)

        return var_amount

    def calculate_expected_shortfall(self, confidence_level=0.95):
        """Calculate Expected Shortfall (Conditional VaR)"""
        if self.daily_returns is None:
            self.prepare_portfolio_data()

        # Find the cutoff point based on confidence level
        cutoff = np.percentile(self.daily_returns, 100 * (1 - confidence_level))

        # Filter for returns worse than VaR
        tail_returns = self.daily_returns[self.daily_returns <= cutoff]

        # Expected Shortfall is the average of these tail returns
        es = tail_returns.mean()

        # Convert to dollar amount
        es_amount = abs(es * self.latest_value)

        return es_amount

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

        return total_exposure.reset_index().rename(columns={'index': 'Country'})

    def generate_risk_report(self):
        """Generate a comprehensive risk report"""
        var_hist = self.calculate_var(method="historical")
        var_param = self.calculate_var(method="parametric")
        var_mc = self.calculate_var(method="monte_carlo")
        es = self.calculate_expected_shortfall()
        country_exposure = self.sanction_exposure_by_country()

        # Create risk metrics dataframe
        risk_metrics = pd.DataFrame(
            {
                "Metric": [
                    "VaR (Historical)",
                    "VaR (Parametric)",
                    "VaR (Monte Carlo)",
                    "Expected Shortfall",
                ],
                "Value": [var_hist, var_param, var_mc, es],
            }
        )

        # Create time series data
        time_series = (
            self.data.groupby(self.data["date"].dt.date)
            .agg({"amount": "sum", "sanctions_flag": "sum"})
            .reset_index()
        )

        time_series["sanctions_exposure"] = (
            self.data[self.data["sanctions_flag"] == 1]
            .groupby(self.data["date"].dt.date)["amount"]
            .sum()
            .reset_index()["amount"]
        )

        time_series["sanctions_exposure"] = time_series["sanctions_exposure"].fillna(0)

        # Transactions with sanctions flags
        flagged_transactions = self.data[self.data["sanctions_flag"] == 1].sort_values(
            "amount", ascending=False
        )

        return {
            "risk_metrics": risk_metrics,
            "country_exposure": country_exposure,
            "time_series": time_series,
            "flagged_transactions": flagged_transactions,
        }
