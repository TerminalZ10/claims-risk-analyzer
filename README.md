# Claims Risk Analyzer — InsureTech AI

A production-ready Streamlit application that helps insurance companies **surface risky claims**, understand **loss drivers**, and **quantify ROI** using machine learning and statistical analysis.

![Claims Risk Analyzer](https://img.shields.io/badge/Status-Interview%20Ready-success)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🎯 What It Does

- **Upload Claims/Policy Data** - Works with any CSV schema, auto-detects columns
- **Smart Anomaly Detection** - IsolationForest ML + Z-score statistics
- **Data Quality Validation** - Age, income, and duplicate detection with configurable handling
- **Interactive Visualizations** - Risk landscapes and distribution charts
- **ROI Calculator** - Industry-backed estimates with preset scenarios
- **Investigation Shortlist** - Prioritized claims with transparent reason codes
- **CSV Export** - Download flagged claims for handoff to investigation teams

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

```bash
# 1. Clone or navigate to the project
cd /path/to/claims-risk-analyzer

# 2. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`

### One-Command Quick Start

```bash
cd /path/to/claims-risk-analyzer && source .venv/bin/activate && streamlit run app.py
```

---

## 📊 Features

### 1. **Smart Anomaly Detection**
- **IsolationForest**: Unsupervised ML to detect unusual claim patterns
- **Z-Score Analysis**: Statistical outliers based on claim type/region
- **Risk Scoring**: 0-1 scale with transparent methodology
- **Reason Codes**: Every flagged claim includes explanation

### 2. **Data Quality Management**
- **Age Validation**: Detect values outside 18-90 range
- **Income Validation**: Flag incomes below $10K or above $500K
- **Suspicious Duplicates**: Identify identical values appearing 10+ times
- **Three Handling Options**:
  - **Flag only**: Highlight issues without removing data
  - **Exclude rows**: Remove problematic records from analysis
  - **Ignore**: Skip validation for performance

### 3. **Interactive Visualizations**
- **Risk Landscape**: Scatter plot showing claim amount vs. age/income, color-coded by risk
- **Distribution Analysis**: Histogram with threshold lines and risk zones
- **Real-time Updates**: Adjust sliders and watch charts update instantly

### 4. **ROI Calculator**
- **Preset Scenarios**:
  - **Conservative**: 3% fraud rate, 15% improvement → ~$318K annual savings
  - **Moderate**: 5% fraud rate, 25% improvement → ~$636K annual savings
  - **Optimistic**: 8% fraud rate, 35% improvement → ~$1.68M annual savings
- **Auto-Update**: Pulls from actual dataset (volume, avg claim amount)
- **Industry-Backed**: Metrics from NHCAA research and ML benchmarks

### 5. **Enterprise-Ready Features**
- **Collapsible UI**: Organize complex workflows without overwhelm
- **RBAC Demo**: Lock/unlock toggle for access control preview
- **CSV Export**: Download flagged claims for Jira/ServiceNow integration
- **Session State**: Fast, responsive UI with minimal recomputation

---

## 📂 Project Structure

```
claims-risk-analyzer/
├── app.py                      # Main Streamlit application (850 lines)
├── helpers.py                  # Data processing utilities (324 lines)
├── requirements.txt            # Python dependencies
├── .venv/                      # Virtual environment (not in git)
├── data/                       # Sample datasets
│   ├── insurance_dataset.csv  # 13K rows, good for demo
│   └── data_synthetic.csv     # 53K rows, slower
└── docs/
    ├── INTERVIEW_GUIDE.md     # Comprehensive demo prep guide
    ├── DEMO_CHEATSHEET.md     # Quick reference for presentation
    ├── PITCH.md               # 2-3 minute pitch script
    └── FINAL_ASSESSMENT.md    # UI/UX and code quality analysis
```

---

## 🎓 For Interview Preparation

### Essential Reading (15 minutes)
1. **[INTERVIEW_GUIDE.md](./INTERVIEW_GUIDE.md)** - Comprehensive guide with demo flow, talking points, Q&A
2. **[DEMO_CHEATSHEET.md](./DEMO_CHEATSHEET.md)** - 1-page quick reference
3. **[PITCH.md](./PITCH.md)** - 2-3 minute pitch structure

### Practice Demo (2-3 minutes)
1. **Opening (15s)**: Show landing page, explain value prop
2. **Data Load (20s)**: Click "Use minimal sample data"
3. **Investigation Shortlist (45s)**: Show flagged claims, adjust thresholds, enable highlighting
4. **Visualizations (30s)**: Show Risk Landscape and Distribution charts
5. **ROI Calculator (35s)**: Click "Moderate" preset, adjust slider
6. **Closing (15s)**: Export CSV, mention integrations

### Key Metrics to Memorize
- Industry fraud rate: **3-10%** (NHCAA)
- ML improvement: **20-45%** (detection rate increase)
- Moderate scenario ROI: **~$636K annual savings**
- Processing time: **< 2 seconds** for 13K rows

---

## 🛠️ Technical Stack

- **Framework**: Streamlit 1.28+
- **ML**: Scikit-learn (IsolationForest)
- **Stats**: Scipy (Z-scores)
- **Visualization**: Plotly Express + Plotly Graph Objects
- **Data**: Pandas, NumPy

---

## 📈 Performance

| Dataset Size | Load Time | Visualization Time |
|--------------|-----------|-------------------|
| 1K rows | < 1 second | < 1 second |
| 13K rows | < 2 seconds | < 2 seconds |
| 53K rows | ~5 seconds | ~10-15 seconds |

**Recommendation**: Use `insurance_dataset.csv` (13K rows) for demos.

---

## 🔒 Security

### This Demo (Local)
- No PII required
- Data stays on your machine
- No external API calls
- Runs entirely offline

### Production Roadmap
- **Authentication**: SSO (Okta, Azure AD) via SAML/OIDC
- **Authorization**: Role-based access control (RBAC)
- **Encryption**: At rest (AES-256) and in transit (TLS 1.3)
- **Audit Logs**: Track all threshold changes and data access
- **Secrets Management**: AWS Secrets Manager / HashiCorp Vault
- **Network**: VPC/private subnets, no public exposure

---

## 🔌 Integration Roadmap

### Today (Demo)
- ✅ CSV upload
- ✅ CSV export

### Phase 1 (4-6 weeks)
- REST API for programmatic access
- Snowflake connector for live data
- S3 batch processing

### Phase 2 (8-12 weeks)
- Webhooks to Jira/ServiceNow
- BigQuery, Redshift connectors
- Slack/Teams alerting
- Scheduled scoring jobs

---

## 📖 Data Compatibility

The app automatically normalizes column names. Works with:

| Your Column Name | Normalized To |
|-----------------|---------------|
| Income, Salary, Income_Level | annual_income |
| Coverage_Amount, Claim_Amount | claim_amount |
| Premium_Amount, Policy_Premium | policy_premium |
| Location, Geographic_Information | state/region |
| Customer_ID, Claim_ID | claim_id |

See [DATASET_COMPATIBILITY.md](./docs/DATASET_COMPATIBILITY.md) for full mapping.

---

## 🐛 Troubleshooting

### "Command not found: streamlit"
**Fix**: Activate virtual environment first:
```bash
source .venv/bin/activate  # You should see (.venv) in prompt
```

### "Port already in use"
**Fix**: Use a different port:
```bash
streamlit run app.py --server.port 8502
```

### App won't open in browser
**Fix**: Manually navigate to the URL shown in terminal (usually `http://localhost:8501`)

### Large dataset is slow
**Fix**: Use `insurance_dataset.csv` (13K rows) instead of `data_synthetic.csv` (53K rows)

---

## 🎯 Next Steps After Demo

1. **Hosted Demo**: Deploy to Streamlit Cloud for remote access
2. **Custom Schema**: Adjust column mapping for client's data
3. **Pilot Proposal**: 2-week POC → 6-week pilot → production
4. **Integration Planning**: Identify priority connectors (Snowflake, Jira, etc.)

---

## 📧 Support

For questions or issues:
- Review **[INTERVIEW_GUIDE.md](./INTERVIEW_GUIDE.md)** for comprehensive Q&A
- Check **[docs/QandA.md](./docs/QandA.md)** for technical deep-dives

---

## 📝 License

MIT License - Free to use, modify, and distribute.

---

## 🙏 Acknowledgments

- **Dataset**: Insurance Claims and Policy Data by Smit Raval (Kaggle)
- **Fraud Statistics**: National Health Care Anti-Fraud Association (NHCAA)
- **ML Benchmarks**: Industry research on fraud detection improvement rates

---

**Built for Sales Engineer interview at InsureTech AI** | [View Demo Guide](./INTERVIEW_GUIDE.md)
