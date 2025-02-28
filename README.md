# **Sanctions Risk Analysis Dashboard**

A Python-based toy analytics dashboard for monitoring and analysing economic sanctions risk exposure in financial transactions.


## **Overview**

This project provides a complete end-to-end solution for analysing transaction data to identify, quantify, and visualise financial risks associated with potential sanctions violations. It applies **risk scoring, penalty exposure estimation, and anomaly detection** to transactions, providing a comprehensive compliance risk report.It demonstrates key skills relevant to a Junior Risk Analyst position in economic sanctions compliance at a financial institution.



 ## **Features/Components**

 ### Transaction Data Simulation
- Synthetic transaction data creation
- **Sanctions screening** simulation
- Data cleaning and preparation

### Risk Scoring System  
- Assigns each transaction a **risk score** based on multiple factors  
- Considers **transaction amount, sanctions flags, country risk, and frequency anomalies**  
- Categorises transactions into **high, medium, and low risk groups**  

### Potential Penalty Exposure  
- Estimates **financial exposure** from potential sanctions violations  
- Inspired by **Value at Risk (VaR), but tailored for compliance risk**  
- Calculates a **Penalty at Risk (PaR)** metric, estimating the penalty amount that won’t be exceeded with 95% confidence  

<!-- ### Network Risk Analysis  
- Uses **graph theory** to detect **high-risk transaction pathways**  
- Identifies **sanctions evasion patterns** and **high-risk jurisdictions**  
- Highlights **key countries** that pose the highest network risk   -->

### Anomaly Detection  
- Uses **statistical and machine learning techniques** to identify **unusual transactions**  
- Combines **z-scores, percentiles, and clustering** for comprehensive anomaly detection  
- Flags **suspicious transactions** for further investigation  

### Comprehensive Risk Reporting  
- Generates a **detailed compliance risk report**  
- Includes **summary metrics, risk by category, country risk profiles, and time trends**  
- Identifies **highest-risk transactions** for further review 

## **Screenshots**  

![image](https://github.com/user-attachments/assets/fadb4a71-683e-4824-a516-7788da6c8dc0)

![image](https://github.com/user-attachments/assets/29ddd069-1110-491a-9c58-ac3c55490d6e)

![image](https://github.com/user-attachments/assets/f3c96dad-9855-407b-9360-64fc118d9a3f)

![image](https://github.com/user-attachments/assets/960895f0-086b-4489-aa78-53f1acd4c8a3)


## **Technology Stack**

- **Python:** Core programming language
- **Pandas & NumPy:** Data manipulation and numerical analysis
- **SciPy:** Statistical calculations
- **Plotly Dash:** Interactive dashboard framework
- **Plotly Express:** Data visualization

## **Getting Started**

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


## **Future Enhancements**
- Network Risk Analysis: use **graph theory** to detect **high-risk transaction pathways** and identify **sanctions evasion patterns**.
- Enhance **machine learning anomaly detection models**.
- Incorporate **real transaction data**.
- Integrate **real sanctions list and name screening algorithm**: Implement fuzzy matching for counterparty names against real sanctions lists.
- Implement different sanctions **scenario analysis**.

## **License**

This project is licensed under the MIT License - see the LICENSE file for details.


## **Contact**  
👤 **Matt Selwood**  
📧 https://www.linkedin.com/in/matthew-selwood/  

---

*Note/Disclaimer: This project is for educational and demonstration purposes only. It should not be used as the sole basis for sanctions compliance without proper validation and customisation to meet specific regulatory requirements.*
