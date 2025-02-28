
from sanctions_risk_analyser import SanctionsRiskAnalyser
import pandas as pd

class ScenarioAnalyser:
    def __init__(self, transaction_data: pd.DataFrame):
        self.data = transaction_data

    def scenario_analysis(self, scenarios=None):
        """
        Analyse impact of different sanctions scenarios

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