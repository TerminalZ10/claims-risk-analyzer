# Claims Risk Analyzer

A machine learning-powered web application for insurance companies to identify high-risk claims, validate data quality, and quantify business impact.

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Overview

Claims Risk Analyzer helps insurance teams surface potentially fraudulent or risky claims from large datasets using machine learning and statistical analysis. The tool combines IsolationForest anomaly detection with Z-score analysis to flag suspicious claims while providing transparent reason codes for every flagged case.

**Key Capabilities:**
- Smart anomaly detection using ML and statistics
- Automated data quality validation and cleaning
- Interactive visualizations for pattern recognition
- ROI calculator with industry-backed estimates
- Configurable thresholds for sensitivity tuning

---

## Features

### 🎯 Anomaly Detection
- **IsolationForest**: Unsupervised ML to detect unusual patterns
- **Z-Score Analysis**: Statistical outlier detection within categories
- **Risk Scoring**: 0-1 scale with transparent methodology
- **Reason Codes**: Explainable flags for audit compliance

### 📊 Data Quality Management
- **Age Validation**: Detect and handle values outside normal ranges
- **Income Validation**: Flag suspicious salary/income entries
- **Duplicate Detection**: Identify suspiciously repetitive values with high precision
- **Configurable Handling**: Choose to flag, exclude, or ignore issues

### 📈 Interactive Visualizations
- **Risk Landscape**: Scatter plots showing claim patterns by amount and age/income
- **Distribution Analysis**: Histograms with threshold indicators and risk zones
- **Real-time Updates**: Visualizations respond instantly to threshold adjustments

### 💰 ROI Calculator
- Industry-backed fraud rate estimates (3-10% from NHCAA)
- ML detection improvement projections (20-45%)
- Preset scenarios: Conservative, Moderate, Optimistic
- Auto-populated from actual dataset statistics

---

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

```bash
# Clone the repository
git clone https://github.com/TerminalZ10/claims-risk-analyzer.git
cd claims-risk-analyzer

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## Usage

### Quick Start
1. Click **"Use minimal sample data"** to explore with demo data
2. Or upload your own CSV file with claims data
3. Adjust anomaly detection thresholds in the sidebar
4. Review flagged claims in the Investigation Shortlist
5. Export results as CSV for further investigation

### Data Format
The app automatically normalizes column names. Supported column variations:

| Your Column | Normalized To |
|------------|---------------|
| Income, Salary, Income_Level | annual_income |
| Coverage_Amount, Claim_Amount | claim_amount |
| Premium_Amount, Policy_Premium | policy_premium |
| Location, Geographic_Information | state/region |

---

## Architecture

### Technology Stack
- **Frontend**: Streamlit (Python web framework)
- **ML**: Scikit-learn (IsolationForest)
- **Statistics**: Scipy (Z-scores)
- **Visualization**: Plotly (interactive charts)
- **Data Processing**: Pandas, NumPy

### Project Structure
```
claims-risk-analyzer/
├── app.py              # Main Streamlit application
├── helpers.py          # Data processing utilities
├── requirements.txt    # Python dependencies
└── data/              # Sample datasets
    ├── insurance_dataset.csv
    └── data_synthetic.csv
```

### Key Components
- **Data Ingestion**: CSV upload with automatic schema detection
- **Data Cleaning**: Configurable validation for age, income, duplicates
- **Anomaly Detection**: Dual-method approach (ML + statistics)
- **Visualization**: Real-time interactive charts
- **Export**: Flagged claims downloadable as CSV

---

## Configuration

### Anomaly Detection Settings
Adjust thresholds in the sidebar:
- **Z-score threshold**: Typically 2.5-3.5 (higher = fewer flags)
- **IsolationForest score**: 0-1 scale (0.6-0.7 recommended)

### Data Quality Settings
Configure validation rules:
- **Age range**: Default 18-90 years
- **Income range**: Default $10K-$500K
- **Duplicate threshold**: Flag values appearing 10+ times

Each validation has three handling options:
- **Flag only**: Highlight issues without removing data
- **Exclude rows**: Remove problematic records from analysis
- **Ignore**: Skip validation for performance

---

## Performance

| Dataset Size | Load Time | Analysis Time |
|--------------|-----------|---------------|
| 1K rows | < 1 second | < 1 second |
| 13K rows | < 2 seconds | < 2 seconds |
| 50K+ rows | ~5 seconds | ~10-15 seconds |

**Recommendation**: For datasets over 50K rows, consider sampling or batch processing.

---

## Production Considerations

### Security
This application runs locally and processes data in-memory. For production deployment:
- Implement authentication (SSO via SAML/OIDC)
- Add role-based access control (RBAC)
- Enable encryption at rest and in transit
- Implement audit logging for compliance
- Use secrets management for configuration

### Scalability
For enterprise-scale deployments:
- Deploy to cloud infrastructure (AWS, Azure, GCP)
- Use containerization (Docker/Kubernetes)
- Implement batch processing for large datasets
- Add database backend for persistence
- Enable distributed computing for ML training

### Integration
API endpoints can be added for:
- Real-time claim scoring during submission
- Batch processing via scheduled jobs
- Webhook callbacks to case management systems
- Export to BI tools (Tableau, Power BI)

---

## Troubleshooting

### Common Issues

**"Command not found: streamlit"**
- Ensure virtual environment is activated: `source .venv/bin/activate`

**"Port already in use"**
- Use a different port: `streamlit run app.py --server.port 8502`

**Slow performance with large datasets**
- Use the 13K row sample dataset instead of 53K row dataset
- Consider implementing sampling for datasets over 50K rows

**Data not loading**
- Check CSV format and encoding (UTF-8 recommended)
- Ensure required columns exist (claim_amount minimum)

---

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

---

## License

MIT License - Free to use, modify, and distribute.

---

## Acknowledgments

- **Dataset**: Insurance Claims and Policy Data (Kaggle)
- **Fraud Statistics**: National Health Care Anti-Fraud Association (NHCAA)
- **ML Frameworks**: Scikit-learn, Scipy, Plotly

---

## Contact

For questions or support, please open an issue on GitHub.
