from modules.riskanalysis import SanctionsRiskAnalyser
from modules.data import generate_transaction_data
from modules.utils import export_data


def main():
    # 1. Generate or load transaction data
    print("Generating transaction data...")
    transactions = generate_transaction_data(5000)

    # 2. Initialize risk analyser
    print("Analysing risk metrics...")
    risk_analyser = SanctionsRiskAnalyser(transactions)
    risk_report = risk_analyser.generate_risk_report()

    # 3. Prepare data for visualisation
    print("Preparing data for dashboard...")
    tableau_data = export_data(transactions, risk_report)

    print("Analysis complete. Data files have been exported for Tableau.")

    # 4. Display key risk metrics
    print("\nKey Risk Metrics:")
    print(f"Historical VaR (95%): ${risk_report['VaR_Historical']:,.2f}")
    print(f"Expected Shortfall (95%): ${risk_report['Expected_Shortfall']:,.2f}")

    # 5. Display top countries by exposure
    print("\nTop Countries by Exposure:")
    top_exposure = (
        risk_report["Country_Exposure"].sort_values("Total", ascending=False).head(5)
    )
    print(top_exposure)


if __name__ == "__main__":
    main()
