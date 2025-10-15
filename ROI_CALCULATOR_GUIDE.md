# ROI Calculator - Feature Guide

## Overview

The enhanced ROI Calculator helps prospects quickly understand the business value of the Claims Risk Analyzer by providing:
- **Industry-researched preset scenarios**
- **One-click reset functionality**
- **Customizable presets** for different client situations
- **Annual savings projection** alongside monthly

---

## Features

### 1. Quick Scenario Buttons

**Four one-click options:**

| Button | Use Case | Values | Monthly ROI |
|--------|----------|--------|-------------|
| 🟢 **Conservative** | Mature fraud detection programs | 3% fraud, $5K claims, 15% improvement, 1K volume | ~$2,250 |
| 🟡 **Moderate** | Typical ML implementation | 5% fraud, $8.5K claims, 25% improvement, 2.5K volume | ~$26,500 |
| 🔴 **Optimistic** | High-fraud environments | 8% fraud, $12K claims, 35% improvement, 5K volume | ~$168,000 |
| ↺ **Reset** | Back to default values | 2% fraud, data-derived avg, 25% improvement, 500 volume | Varies |

### 2. Editable Presets (Advanced)

Click "⚙️ Preset Settings" expander to customize scenarios:
- Adjust fraud rates, claim amounts, improvement percentages, volumes
- Changes persist during the session
- Great for adapting to specific client situations

### 3. Annual Savings Display

Now shows **both** monthly and annual projections:
- Makes impact more tangible ("$300K/year" > "$25K/month")
- Better for C-suite conversations

---

## Research Behind the Presets

### Fraud Rate Values (3%, 5%, 8%)

**Sources:**
- National Health Care Anti-Fraud Association (NHCAA): 3-10% of health care expenditures
- FBI estimates: Up to 10% in high-risk categories
- Industry consensus: 3-5% typical, 8-10% in problematic areas

**Conservative (3%)**: Lower bound, well-documented fraud programs
**Moderate (5%)**: Industry average across health insurance
**Optimistic (8%)**: Higher-risk populations or regions with known fraud issues

### Detection Improvement (15%, 25%, 35%)

**Sources:**
- Academic research: ML models show 20-45% improvement over rule-based baselines
- Baseline (manual/rules): 54-68% accuracy
- Basic ML: 79% accuracy (~20% improvement)
- Advanced ML: 92-95% accuracy (~40% improvement)

**Conservative (15%)**: Early implementation, limited training data
**Moderate (25%)**: Typical ML deployment with decent historical data
**Optimistic (35%)**: Advanced models with extensive training, ensemble methods

### Claim Amounts ($5K, $8.5K, $12K)

**Sources:**
- Healthcare fraud studies: $3K-$25K range depending on fraud type
- Simple billing errors: $2K-$5K
- Coordinated fraud schemes: $10K-$25K+

**Conservative ($5K)**: Minor billing errors, incorrect codes
**Moderate ($8.5K)**: Mix of errors and intentional fraud
**Optimistic ($12K)**: More complex fraud schemes, higher-value claims

### Volume (1K, 2.5K, 5K claims/month)

**Based on insurer size:**
- Small regional insurer: 500-1,500 claims/month
- Mid-size insurer: 2,000-5,000 claims/month
- Large national insurer: 10,000+ claims/month

---

## Demo Talking Points

### Opening the ROI Calculator

> "Now let's talk ROI. I've built in three scenarios based on industry research - conservative, moderate, and optimistic. These are grounded in real data from NHCAA and academic ML research."

### Conservative Scenario

> "Conservative assumes a 3% fraud rate - that's the low end of industry estimates - with a mature detection program improving by 15%. For a small insurer processing 1,000 claims monthly, that's $2,250 in monthly savings, or about $27,000 annually."

### Moderate Scenario

> "Moderate is more typical: 5% fraud rate - right in the industry average - with ML improving detection by 25%. For a mid-size insurer at 2,500 claims per month, we're looking at $26,500 monthly savings, over $300,000 per year."

### Optimistic Scenario

> "Optimistic represents a high-fraud environment - maybe you're in a region with known issues, or a line of business that's fraud-prone. 8% fraud rate, and with advanced ML we can see 35% improvement. At 5,000 claims monthly, that's $168,000 per month - over $2 million annually."

### Using Reset

> "And if at any point you want to go back to baseline assumptions, just click Reset. Or better yet, let's customize this for YOUR organization..."

### Showing Preset Settings

> "I can also customize these scenarios if your situation is different. Click Preset Settings here - maybe your average fraudulent claim is $20,000 instead of $12,000. We adjust that, save it, and now when I click the preset button, it uses your numbers."

---

## Q&A Preparation

### "Where did these numbers come from?"

**Answer**: "Great question. The fraud rates come from the National Health Care Anti-Fraud Association, which estimates 3-10% of healthcare spending is lost to fraud. The ML improvement numbers are from peer-reviewed research - studies show 20-45% improvement over rule-based systems. I can send you the specific papers if you'd like."

### "Our fraud rate is way higher/lower than these presets."

**Answer**: "That's exactly why I built the customization feature. Click 'Preset Settings' here, and we can adjust the assumptions to match your actual data. In a real engagement, we'd calibrate this with your historical claims data during the pilot phase."

### "These savings seem too optimistic."

**Answer**: "I appreciate the skepticism - that's smart. Notice I've labeled them Conservative, Moderate, and Optimistic for transparency. The Conservative scenario uses the low end of industry estimates. But you're right to push back - this is why we always recommend a pilot. Two weeks with your actual data, and we'll know the real ROI for your organization."

### "Can we add our own scenario?"

**Answer**: "Absolutely. Right now you can customize the three presets in the settings. If you wanted a fourth or fifth scenario - maybe one for each line of business - that's a simple config change. In production, we'd make these fully customizable through an admin panel."

### "What about false positives? Won't that eat into the ROI?"

**Answer**: "Excellent point. These calculations assume perfect precision, which isn't realistic. In production, we'd factor in your false positive tolerance. If you say 'we can handle 5% false positives,' we optimize for that threshold. The real ROI might be 80-90% of what's shown here, but it's still significant. And over time, as the model learns from your feedback, that improves."

---

## Technical Implementation Notes

### Session State Management

Uses Streamlit's `st.session_state` to persist:
- `roi_presets`: The three scenario configurations (editable)
- `roi_defaults`: Original default values for reset
- `roi_current`: Currently displayed values

**Why this matters**: Values persist across interactions, no database needed for demo

### Rerun on Preset Click

When user clicks a preset button:
1. Update `st.session_state.roi_current` with preset values
2. Call `st.rerun()` to refresh the app
3. Input fields now show preset values

### Editable Presets

The settings panel updates `st.session_state.roi_presets` in real-time. When user clicks a preset button later, it uses the updated values.

**Production enhancement**: Store presets in database or config file for persistence across sessions

---

## Future Enhancements

### Short-term (could add before demo):
- **Comparison view**: Show all three scenarios side-by-side
- **Sensitivity analysis**: "If fraud rate increases by 1%, savings increase by $X"
- **Break-even calculator**: "How many flagged claims to justify the investment?"

### Long-term (production features):
- **Historical ROI tracking**: "Here's your actual ROI over the past 6 months"
- **Export ROI report**: PDF with scenarios, assumptions, and references
- **Multi-currency support**: For international deployments
- **Custom scenario names**: Instead of Conservative/Moderate/Optimistic, use client-specific names
- **ROI confidence intervals**: "95% confidence: $20K-$35K monthly savings"

---

## Demo Script (30 seconds)

**Setup**: Insurance dataset loaded, ROI Calculator visible

**You**: "Let me show you the business value. I've built in three scenarios based on industry research."

**[Click Conservative]**

**You**: "Conservative: 3% fraud rate, 15% improvement - that's $27K annually."

**[Click Moderate]**

**You**: "Moderate: 5% fraud, 25% improvement - now we're at $300K per year."

**[Click Optimistic]**

**You**: "Optimistic: High-fraud environment - over $2 million annually."

**[Click Preset Settings]**

**You**: "And if your situation is different, I can customize these on the fly. Maybe your fraudulent claims average $20K instead of $12K..."

**[Adjust one value, click Optimistic again]**

**You**: "There - now it's using your numbers. This is how we'd calibrate it during a pilot with your actual data."

**Impact**: Shows research, flexibility, and customer-centric thinking in 30 seconds.

---

## Source Citations (for Q&A)

**Fraud Rates:**
- National Health Care Anti-Fraud Association (NHCAA): https://www.nhcaa.org/
- FBI Insurance Fraud statistics
- "The Challenge of Health Care Fraud" - NHCAA white paper

**ML Improvement:**
- "Insurance fraud detection using machine learning" - Scientific Reports (2025)
- "Fraud Detection in Healthcare Insurance Claims" - MDPI (2023)
- Deloitte: "Using AI to fight insurance fraud" (2025)

**Keep these links handy** in case someone asks for sources during or after the demo!

---

*Created: 2025-10-13*
*Research-backed, demo-ready, production-extensible* 🚀
