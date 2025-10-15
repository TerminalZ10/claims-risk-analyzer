# Demo Cheatsheet - Quick Reference

## Dataset Quick Facts

### insurance_dataset.csv
- **Size**: 13,000 rows, 7 columns
- **Data Quality Issues**: 650 age outliers (5%), 120 income outliers (~1%)
- **Best For**: Data quality validation demo
- **Key Talking Point**: "Real data has real issues - 650 ages over 90!"

### data_synthetic.csv
- **Size**: 53,503 rows, 30 columns
- **Data Quality**: Clean (no outliers in tested sample)
- **Best For**: Scalability and feature richness demo
- **Key Talking Point**: "53K rows, 30 fields, instant performance"

---

## Data Quality Demo Script (3 minutes)

**Load insurance_dataset.csv**

1. **Show the Problem** (30 sec)
   - "13,000 insurance claims loaded"
   - Open sidebar → Data Quality section
   - "Notice we detected 650 age outliers and 120 income outliers"

2. **Configure Validation** (30 sec)
   - Age Validation → set min=18, max=90
   - Income Validation → set min=$10K, max=$500K
   - Choose "Impute mean"

3. **Show Results** (60 sec)
   - Point to Data Quality Report card
   - "650 ages cleaned, imputed value: 49"
   - "120 incomes cleaned, imputed value: $163K"
   - "Zero rows removed - we kept all data for analysis"

4. **Business Value** (60 sec)
   - "Why does this matter?"
   - "Bad data leads to bad predictions"
   - "If ages over 100 feed into actuarial models, your premiums are wrong"
   - "Our system prevents garbage-in-garbage-out"
   - "Your analysts save hours of manual cleaning"

---

## Schema Integration Demo (2 minutes)

**Switch between datasets**

1. **Load insurance_dataset.csv** (30 sec)
   - Show it works
   - Note columns: Age, Income, Claim_Amount (underscores)

2. **Load data_synthetic.csv** (30 sec)
   - Show it also works
   - Note columns: Coverage Amount, Income Level (spaces)

3. **The Point** (60 sec)
   - "These have completely different schemas"
   - "7 columns vs 30 columns"
   - "Underscores vs spaces"
   - "Different field names: 'Income' vs 'Income Level'"
   - "Our normalization layer maps everything automatically"
   - "In production, this handles Snowflake, BigQuery, S3 - any source"

---

## Q&A Cheat Sheet

### Security Questions

**Q: How do you handle sensitive data?**
- "This demo runs locally - data never leaves your machine"
- "Production: TLS in transit, KMS encryption at rest"
- "Field-level masking for PII"
- "SSO via SAML/OIDC, RBAC for access control"

**Q: What about audit logs?**
- "All data transformations are logged"
- "Every cleaning operation tracked: what changed, when, why"
- "Export to SIEM (Splunk, Datadog)"
- "Immutable audit trail for compliance"

### Performance Questions

**Q: How does this scale?**
- "This demo: pandas, works up to millions of rows"
- "Production: PySpark for distributed processing"
- "Same logic, different engine - scales horizontally"
- "We'd benchmark your data volumes during pilot"

**Q: What about real-time scoring?**
- "This is batch mode - great for daily analysis"
- "For real-time: deploy as microservice API"
- "Sub-second response for single claims"
- "Kafka + stream processing for high-volume"

### Integration Questions

**Q: How do we connect our data warehouse?**
- "Built-in connectors: Snowflake, BigQuery, Redshift, S3"
- "Standard SQL queries - you control the data selection"
- "Scheduled jobs via Airflow or Step Functions"
- "Or push data to us via REST API"

**Q: Can we customize the cleaning rules?**
- "Absolutely - everything is configurable"
- "Rules stored in config files, version-controlled"
- "Your team reviews and approves changes"
- "No code deployment needed for rule updates"

**Q: What about existing tools? Jira, ServiceNow?**
- "We push flagged claims to your case management"
- "Webhooks for Slack/Teams alerts"
- "Email notifications with configurable thresholds"
- "Two-way sync: updates flow back to our system"

### Feature Questions

**Q: Can we add custom risk factors?**
- "Yes - the model is extensible"
- "You provide features, we integrate them"
- "A/B testing to validate improvements"
- "Model registry tracks all versions"

**Q: What about explainability?**
- "Every flagged claim has reason codes"
- "Feature importance scores available"
- "SHAP values for model transparency"
- "No black box - you understand every decision"

**Q: Can we weight certain claim types higher?**
- "Yes - configurable risk weights by category"
- "Set thresholds per policy type, region, etc."
- "Different rules for different lines of business"
- "All managed through configuration UI"

---

## ROI Talking Points

### Time Savings
- "Manual triage: 5 minutes per claim × 500 claims/month = 42 hours"
- "With our tool: 10 minutes total for whole batch"
- "Save 41+ hours monthly = $2K+ at $50/hour"

### Improved Detection
- "Baseline: rules-only catches 60% of suspicious claims"
- "With ML: catch 85% (25% improvement)"
- "15-30% more fraud/leakage detected"
- "On $1M/month in claims, that's $150K-$300K saved annually"

### Faster Cycle Times
- "Reduce investigation backlog by 30%"
- "Faster resolution = better customer experience"
- "Fewer escalations to senior adjusters"

---

## Technical Credibility Boosters

Drop these naturally during demo:

- "We use IsolationForest plus category-aware z-scores"
- "Feature engineering happens in the pipeline, not ad-hoc"
- "Model drift monitoring with automated alerts"
- "CI/CD for model deployments - tested before production"
- "Containerized for easy deployment (Docker, K8s ready)"
- "Infrastructure as code (Terraform, CloudFormation)"

---

## What Not to Say

❌ "This is production-ready" → ✅ "This is production-track - we'd add X, Y, Z for enterprise"
❌ "We can do anything" → ✅ "We're focused on claims risk, with extensibility built in"
❌ "It just works" → ✅ "It works because we built proper normalization layers"
❌ "Trust the AI" → ✅ "Every decision is explainable with reason codes"

---

## Emergency Backup Plan

If demo breaks:

1. **App won't start**
   - Show code walkthrough instead
   - Focus on architecture discussion
   - "This is why thorough testing matters in production"

2. **Dataset won't load**
   - Use sample data (built into app)
   - "Sample data demonstrates core functionality"
   - Offer to troubleshoot their data format after demo

3. **Feature doesn't work**
   - Acknowledge it: "Good catch, that's a known edge case"
   - Explain how you'd fix it
   - "This is why we do pilots before full rollout"

**Key**: Show problem-solving skills, not just working features

---

## Closing Lines

### Strong Close
"We've built something that solves your immediate problem - surface risky claims fast. But more importantly, we've built it the right way: explainable, configurable, and integration-ready. This isn't just a demo - it's the foundation of a production system."

### Call to Action
"I'd love to run a pilot with your actual data. Two weeks, no commitment. We'll quantify the exact ROI for your organization. What's a good time to schedule a technical deep-dive with your team?"

### Confidence Builder
"You're evaluating other vendors too - that's smart. Ask them about schema normalization. Ask them about data quality handling. Ask them about explainability. Then compare the answers."

---

## Pre-Demo Checklist

- [ ] App runs: `streamlit run app.py`
- [ ] Both datasets load in UI
- [ ] Data quality report shows correct numbers
- [ ] Filters populate correctly
- [ ] Charts render properly
- [ ] Export buttons work
- [ ] Practiced the 3-minute data quality script
- [ ] Practiced the 2-minute schema integration story
- [ ] Prepared answers to top 3 expected questions
- [ ] Have backup plan if tech fails

---

## After Demo

### Follow-up Email Template

```
Subject: Claims Risk Analyzer - Demo Follow-up

Hi [Name],

Thanks for the great questions during today's demo! Here are the key points we discussed:

✅ Data Quality: Detected and cleaned 650 age outliers + 120 income outliers
✅ Schema Flexibility: Handled 2 different datasets with automatic normalization
✅ Business Impact: Estimated $150K-300K annual savings from improved detection

Next steps:
1. I'll send over the technical architecture doc
2. Let's schedule a 30-min call to discuss integration with your data sources
3. If interested, we can start a 2-week pilot with your actual claims data

Questions that came up:
- [Question 1]: [Your answer]
- [Question 2]: [Your answer]

Looking forward to exploring this further!

Best,
[Your name]
```

---

*Good luck! You've got this.* 🚀
