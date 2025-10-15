import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO
from helpers import (
    coalesce_columns, compute_kpis, flag_anomalies, safe_float,
    handle_numeric_outliers, get_data_quality_summary,
    detect_suspicious_duplicates,
    AGE_MIN_DEFAULT, AGE_MAX_DEFAULT,
    INCOME_MIN_DEFAULT, INCOME_MAX_DEFAULT
)

st.set_page_config(page_title="Claims Risk Analyzer — InsureTech AI", layout="wide")

st.title("🛡️ Claims Risk Analyzer — InsureTech AI")
st.caption("Surface risky claims, understand loss drivers, and quantify ROI from day one.")

with st.expander("About this tool"):
    st.write("""
    **What this shows**
    - Upload a CSV or use a sample to explore claims/policy data.
    - KPI summary + interactive filters.
    - Outlier detection with transparent reason codes.
    - ROI calculator to translate findings into business impact.
    - Export flagged claims to CSV for investigation.

    **Notes**
    - In this instance: No PII required. Runs locally.
    - Available for implementation: SSO, encryption, audit logs, connectors, and RBAC.
    """)

# Data input - prominent upload section
st.subheader("📂 Upload CSV for Analysis (Claims/Policy Data)")

# Initialize uploader key in session state
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0

# Add clear/reset button
col_upload, col_reset = st.columns([4, 1])
with col_upload:
    uploaded = st.file_uploader(
        "Choose a file to begin analysis",
        type=["csv"],
        label_visibility="collapsed",
        key=f"uploader_{st.session_state.uploader_key}"
    )
with col_reset:
    if st.button("🔄 Clear Data"):
        # Increment key to reset file uploader
        st.session_state.uploader_key += 1
        # Clear all other session state
        for key in list(st.session_state.keys()):
            if key != 'uploader_key':
                del st.session_state[key]
        st.rerun()

sample_btn = st.button("Use minimal sample data")

def load_sample_df():
    data = {
        "claim_id": range(1, 31),
        "claim_amount": np.random.lognormal(mean=8.5, sigma=0.6, size=30).round(2),
        "policy_premium": np.random.uniform(500, 2500, size=30).round(2),
        "policy_type": np.random.choice(["Auto", "Home", "Health"], size=30, p=[0.3, 0.2, 0.5]),
        "claim_type": np.random.choice(["Injury", "Property", "Theft", "Other"], size=30),
        "region": np.random.choice(["Northeast", "Midwest", "South", "West"], size=30),
        "state": np.random.choice(["NY", "CA", "TX", "FL", "IL", "PA"], size=30),
        "age": np.random.randint(18, 85, size=30),
        "tenure_months": np.random.randint(1, 120, size=30),
    }
    df = pd.DataFrame(data)
    # Add a few synthetic outliers
    df.loc[np.random.choice(df.index, 2, replace=False), "claim_amount"] *= 6
    return df

# Use session state to persist data across reruns
if 'df' not in st.session_state:
    st.session_state.df = None

df = None
if uploaded is not None:
    try:
        df = pd.read_csv(uploaded)
        st.session_state.df = df  # Store in session state
    except Exception as e:
        st.error(f"Failed to read CSV: {e}")
elif sample_btn:
    df = load_sample_df()
    st.session_state.df = df  # Store in session state
elif st.session_state.df is not None:
    df = st.session_state.df  # Retrieve from session state

if df is not None:
    df = coalesce_columns(df)

    # Sidebar filters
    with st.sidebar:
        with st.expander("🔍 Filters", expanded=True):
            filter_cols = []
            for col in ["policy_type", "claim_type", "region", "state"]:
                if col in df.columns:
                    vals = sorted(df[col].dropna().unique().tolist())
                    sel = st.multiselect(col.replace("_", " ").title(), vals, default=vals)
                    filter_cols.append((col, sel))

            # Note: We'll apply these filters AFTER data quality cleaning
            # (filters are stored in filter_cols list)

        st.divider()
        st.subheader("Anomaly Detection Settings")
        z_threshold = safe_float(st.number_input("Z-score threshold", value=2.5, step=0.1))
        score_threshold = safe_float(st.number_input("IsolationForest score threshold (0-1)", value=0.65, step=0.05))
        if z_threshold is None: z_threshold = 2.5

        if score_threshold is None: score_threshold = 0.65

        # Quick preview of how many claims will be flagged
        # (We'll calculate full details later, this is just for immediate feedback)
        preview_scored = flag_anomalies(df, z_threshold=z_threshold, score_threshold=score_threshold)
        preview_flagged = preview_scored[preview_scored["flagged"]]
        num_flagged = len(preview_flagged)
        pct_flagged = (num_flagged / len(df) * 100) if len(df) > 0 else 0

        # Show immediate feedback
        st.markdown("**📊 Detection Preview:**")
        feedback_col1, feedback_col2 = st.columns(2)
        feedback_col1.metric("Claims Flagged", f"{num_flagged:,}", help="Claims requiring investigation")
        feedback_col2.metric("Flag Rate", f"{pct_flagged:.1f}%", help="Percentage of total dataset")

        if num_flagged > 0:
            high_risk = len(preview_flagged[preview_flagged["risk_score"] >= 0.8])
            medium_risk = len(preview_flagged[(preview_flagged["risk_score"] >= 0.6) & (preview_flagged["risk_score"] < 0.8)])
            low_risk = len(preview_flagged[preview_flagged["risk_score"] < 0.6])
            st.caption(f"🔴 High risk: {high_risk} | 🟡 Medium: {medium_risk} | 🟢 Low: {low_risk}")

        st.divider()
        st.subheader("Data Quality")

        with st.expander("Age Validation", expanded=False):
            st.markdown("Configure how to handle age values outside the valid range.")
            age_method = st.radio(
                "Age handling method",
                options=["Impute mean", "Exclude rows", "Leave as-is"],
                index=1,
                help="Impute: replace invalid with mean | Exclude: remove rows | Leave: keep data unchanged"
            )
            col1, col2 = st.columns(2)
            age_min = col1.number_input("Min valid age", value=AGE_MIN_DEFAULT, step=1, min_value=0, max_value=120)
            age_max = col2.number_input("Max valid age", value=AGE_MAX_DEFAULT, step=1, min_value=0, max_value=120)

            if age_min >= age_max:
                st.error("⚠️ Min age must be less than max age")

        with st.expander("Income Validation", expanded=False):
            st.markdown("Configure how to handle income/salary values outside the valid range.")
            income_method = st.radio(
                "Income handling method",
                options=["Impute mean", "Exclude rows", "Leave as-is"],
                index=1,
                help="Impute: replace invalid with mean | Exclude: remove rows | Leave: keep data unchanged"
            )
            col1, col2 = st.columns(2)
            income_min = col1.number_input(
                "Min valid income ($)",
                value=INCOME_MIN_DEFAULT,
                step=5000,
                min_value=0,
                format="%d"
            )
            income_max = col2.number_input(
                "Max valid income ($)",
                value=INCOME_MAX_DEFAULT,
                step=10000,
                min_value=0,
                format="%d"
            )

            if income_min >= income_max:
                st.error("⚠️ Min income must be less than max income")

        with st.expander("Suspicious Duplicates", expanded=False):
            st.markdown("Detect and handle values that appear suspiciously often with unusual precision.")

            duplicates_method = st.radio(
                "Duplicate handling method",
                options=["Flag only", "Exclude rows", "Ignore"],
                index=1,
                help="Flag only: highlight in table | Exclude: remove from analysis | Ignore: no duplicate detection"
            )

            if duplicates_method != "Ignore":
                dup_threshold = st.slider(
                    "Minimum occurrences to flag",
                    min_value=5,
                    max_value=50,
                    value=10,
                    step=5,
                    help="Flag values appearing this many times or more"
                )
            else:
                dup_threshold = 10  # Default value when ignored

    # ========================================================================
    # DATA QUALITY CLEANING (now that sidebar variables are defined)
    # ========================================================================

    # Map UI labels to method keys
    method_map = {
        'Impute mean': 'impute_mean',
        'Exclude rows': 'exclude',
        'Leave as-is': 'leave'
    }

    age_method_key = method_map.get(age_method, 'impute_mean')
    income_method_key = method_map.get(income_method, 'impute_mean')

    # Store original count for reporting
    original_row_count = len(df)

    # Track which rows had quality issues BEFORE cleaning (for highlighting later)
    original_age_issues = pd.Series(False, index=df.index)
    if 'age' in df.columns:
        age_series = pd.to_numeric(df['age'], errors='coerce')
        original_age_issues = (age_series < age_min) | (age_series > age_max) | age_series.isna()

    # Clean AGE column
    df, affected_age, age_imputed_value = handle_numeric_outliers(
        df,
        column="age",
        method=age_method_key,
        min_val=age_min,
        max_val=age_max,
        round_to_int=True
    )

    # Clean INCOME/SALARY column (use coalesced name)
    income_col = None
    if "annual_income" in df.columns:
        income_col = "annual_income"
    elif "salary" in df.columns:
        income_col = "salary"

    # Track which rows had income issues BEFORE cleaning
    original_income_issues = pd.Series(False, index=df.index)
    if income_col:
        income_series = pd.to_numeric(df[income_col], errors='coerce')
        original_income_issues = (income_series < income_min) | (income_series > income_max) | income_series.isna()

        df, affected_income, income_imputed_value = handle_numeric_outliers(
            df,
            column=income_col,
            method=income_method_key,
            min_val=income_min,
            max_val=income_max,
            round_to_int=True
        )
    else:
        affected_income, income_imputed_value = 0, None

    # Clean SUSPICIOUS DUPLICATES
    affected_duplicates = 0
    if duplicates_method != "Ignore" and income_col:
        # Detect duplicates
        has_duplicates = detect_suspicious_duplicates(df, income_col, min_occurrences=dup_threshold)
        affected_duplicates = has_duplicates.sum()
        # Exclude rows with duplicates if method is "Exclude rows"
        if duplicates_method == "Exclude rows":
            df = df[~has_duplicates].copy()

    rows_removed = original_row_count - len(df)

    # ========================================================================
    # APPLY FILTERS (now that data is cleaned)
    # ========================================================================

    if filter_cols:
        mask = pd.Series([True] * len(df))
        for col, sel in filter_cols:
            if col in df.columns:  # Make sure column still exists after cleaning
                mask &= df[col].isin(sel)
        df_f = df[mask].copy()
    else:
        df_f = df.copy()

    # ========================================================================
    # DATA QUALITY FEEDBACK
    # ========================================================================

    quality_messages = []

    # Age cleaning feedback
    if affected_age > 0:
        if age_method_key == 'impute_mean' and age_imputed_value is not None:
            quality_messages.append(
                f"🔧 **Age**: {affected_age} out-of-range value(s) imputed to mean = **{age_imputed_value}**"
            )
        elif age_method_key == 'exclude':
            quality_messages.append(
                f"🗑️ **Age**: {affected_age} row(s) excluded (out-of-range ages)"
            )
        else:
            quality_messages.append(
                f"ℹ️ **Age**: {affected_age} out-of-range value(s) detected (no changes applied)"
            )

    # Income cleaning feedback
    if affected_income > 0:
        if income_method_key == 'impute_mean' and income_imputed_value is not None:
            quality_messages.append(
                f"🔧 **Income**: {affected_income} out-of-range value(s) imputed to mean = **${income_imputed_value:,}**"
            )
        elif income_method_key == 'exclude':
            quality_messages.append(
                f"🗑️ **Income**: {affected_income} row(s) excluded (out-of-range income)"
            )
        else:
            quality_messages.append(
                f"ℹ️ **Income**: {affected_income} out-of-range value(s) detected (no changes applied)"
            )

    # Duplicates cleaning feedback
    if affected_duplicates > 0:
        if duplicates_method == 'Exclude rows':
            quality_messages.append(
                f"🗑️ **Duplicates**: {affected_duplicates} row(s) excluded (suspicious duplicate values)"
            )
        elif duplicates_method == 'Flag only':
            quality_messages.append(
                f"⚠️ **Duplicates**: {affected_duplicates} suspicious duplicate value(s) detected (highlighted in table)"
            )

    # Display quality summary if any issues found
    if quality_messages:
        with st.expander("📊 Data Quality Report", expanded=True):
            for msg in quality_messages:
                st.markdown(msg)
            if rows_removed > 0:
                st.info(f"**Total rows removed**: {rows_removed} of {original_row_count} ({rows_removed/original_row_count*100:.1f}%)")
            st.caption("💡 Adjust settings in the sidebar to change how data quality issues are handled.")

    # Dataset summary (shows impact of cleaning)
    summary_cols = st.columns([1, 1, 1, 1])
    summary_cols[0].metric(
        "Original Dataset",
        f"{original_row_count:,}",
        help="Row count before any data quality cleaning"
    )
    summary_cols[1].metric(
        "After Cleaning",
        f"{len(df):,}",
        delta=f"-{rows_removed}" if rows_removed > 0 else "✓ Clean",
        delta_color="inverse" if rows_removed > 0 else "off",
        help="Rows remaining after data quality cleaning"
    )
    summary_cols[2].metric(
        "Available for Analysis",
        f"{len(df_f):,}",
        help="After data cleaning and filters applied"
    )
    if rows_removed > 0:
        summary_cols[3].metric(
            "Data Quality",
            f"{((len(df)/original_row_count)*100):.1f}%",
            help="Percentage of rows retained after cleaning"
        )

    # KPIs
    kpis = compute_kpis(df_f)
    kcols = st.columns(4)
    kcols[0].metric("Claims (rows)", f"{kpis.get('num_claims', 0):,}")
    if "avg_claim_amount" in kpis:
        kcols[1].metric("Avg Claim Amount", f"${kpis['avg_claim_amount']:,.0f}")
    if "total_claims_amount" in kpis:
        kcols[2].metric("Total Claim Amount", f"${kpis['total_claims_amount']:,.0f}")
    if kpis.get("loss_ratio_proxy") is not None:
        kcols[3].metric("Loss Ratio (proxy)", f"{kpis['loss_ratio_proxy']:.2f}")

    # =====================================================================
    # INTERACTIVE VISUALIZATION: Risk Analysis
    # =====================================================================
    with st.expander("📊 Claims Analysis Visualization", expanded=True):
        st.caption("Interactive visualizations that respond to anomaly detection and data quality settings")

        # Run anomaly detection on the filtered dataset
        scored_for_viz = flag_anomalies(df_f, z_threshold=z_threshold, score_threshold=score_threshold)

        # Create tabs for different visualizations
        viz_tab1, viz_tab2 = st.tabs(["🎯 Risk Landscape", "📈 Distribution Analysis"])

        with viz_tab1:
            # ============ SCATTER PLOT: Risk Score Landscape ============
            st.markdown("**Claims Risk Landscape** - Each point represents a claim, colored by risk level")

            if len(scored_for_viz) > 0 and "claim_amount" in scored_for_viz.columns:
                # Determine Y-axis column (prefer age, fallback to income)
                y_axis_col = None
                y_axis_label = ""

                if "age" in scored_for_viz.columns:
                    y_axis_col = "age"
                    y_axis_label = "Age"
                elif "annual_income" in scored_for_viz.columns:
                    y_axis_col = "annual_income"
                    y_axis_label = "Annual Income"
                elif "salary" in scored_for_viz.columns:
                    y_axis_col = "salary"
                    y_axis_label = "Salary"

                if y_axis_col:
                    # Create scatter plot
                    fig_scatter = px.scatter(
                        scored_for_viz,
                        x="claim_amount",
                        y=y_axis_col,
                        color="risk_score",
                        size="anomaly_iforest",
                        hover_data={
                            "claim_amount": ":,.0f",
                            y_axis_col: ":,.0f",
                            "risk_score": ":.3f",
                            "anomaly_iforest": ":.3f",
                            "anomaly_z": ":.3f",
                            "flagged": True
                        },
                        color_continuous_scale=[
                            [0.0, "#2ecc71"],    # Green (low risk)
                            [0.5, "#f39c12"],    # Yellow (medium risk)
                            [1.0, "#e74c3c"]     # Red (high risk)
                        ],
                        title=f"Risk Landscape: Claim Amount vs. {y_axis_label}",
                        labels={
                            "claim_amount": "Claim Amount ($)",
                            y_axis_col: y_axis_label,
                            "risk_score": "Risk Score",
                            "anomaly_iforest": "IsolationForest Score",
                            "anomaly_z": "Z-Score"
                        }
                    )

                    # Update layout for better appearance
                    fig_scatter.update_layout(
                        height=500,
                        coloraxis_colorbar=dict(
                            title="Risk<br>Score",
                            tickformat=".2f"
                        ),
                        hovermode='closest'
                    )

                    # Add threshold line annotations
                    flagged_count = scored_for_viz["flagged"].sum()
                    fig_scatter.add_annotation(
                        text=f"🚩 {flagged_count:,} claims flagged ({(flagged_count/len(scored_for_viz)*100):.1f}%)",
                        xref="paper", yref="paper",
                        x=0.02, y=0.98,
                        showarrow=False,
                        bgcolor="rgba(255, 255, 255, 0.8)",
                        bordercolor="#e74c3c",
                        borderwidth=2,
                        borderpad=8,
                        font=dict(size=12, color="#e74c3c")
                    )

                    st.plotly_chart(fig_scatter, use_container_width=True)

                    # Add insight
                    high_risk_count = len(scored_for_viz[scored_for_viz["risk_score"] >= 0.8])
                    if high_risk_count > 0:
                        st.info(f"🔴 **{high_risk_count} high-risk claims** (risk score ≥ 0.8) - prioritize these for investigation")
                else:
                    st.warning("⚠️ No suitable Y-axis column found (age, annual_income, or salary)")
            else:
                st.warning("⚠️ Not enough data for scatter plot visualization")

        with viz_tab2:
            # ============ HISTOGRAM: Risk Score Distribution ============
            st.markdown("**Risk Score Distribution** - Shows how claims are distributed across risk levels")

            if len(scored_for_viz) > 0:
                # Create histogram of risk scores
                fig_hist = go.Figure()

                # Separate flagged and non-flagged for different colors
                flagged_scores = scored_for_viz[scored_for_viz["flagged"]]["risk_score"]
                non_flagged_scores = scored_for_viz[~scored_for_viz["flagged"]]["risk_score"]

                # Add non-flagged claims (gray)
                fig_hist.add_trace(go.Histogram(
                    x=non_flagged_scores,
                    name="Not Flagged",
                    marker_color="#95a5a6",
                    opacity=0.7,
                    nbinsx=50
                ))

                # Add flagged claims (red)
                fig_hist.add_trace(go.Histogram(
                    x=flagged_scores,
                    name="Flagged for Review",
                    marker_color="#e74c3c",
                    opacity=0.8,
                    nbinsx=50
                ))

                # Add vertical threshold line
                fig_hist.add_vline(
                    x=score_threshold,
                    line_dash="dash",
                    line_color="#2c3e50",
                    line_width=3,
                    annotation_text=f"Threshold: {score_threshold}",
                    annotation_position="top"
                )

                # Add risk zone shading
                fig_hist.add_vrect(
                    x0=0.8, x1=1.0,
                    fillcolor="red", opacity=0.1,
                    layer="below", line_width=0,
                    annotation_text="High Risk", annotation_position="top right"
                )
                fig_hist.add_vrect(
                    x0=0.6, x1=0.8,
                    fillcolor="orange", opacity=0.1,
                    layer="below", line_width=0,
                    annotation_text="Medium Risk", annotation_position="top right"
                )

                # Update layout
                fig_hist.update_layout(
                    title="Risk Score Distribution with Threshold",
                    xaxis_title="Risk Score",
                    yaxis_title="Number of Claims",
                    height=500,
                    barmode='stack',
                    showlegend=True,
                    legend=dict(
                        yanchor="top",
                        y=0.99,
                        xanchor="right",
                        x=0.99
                    )
                )

                st.plotly_chart(fig_hist, use_container_width=True)

                # Add statistics
                stat_cols = st.columns(4)
                stat_cols[0].metric(
                    "Mean Risk Score",
                    f"{scored_for_viz['risk_score'].mean():.3f}"
                )
                stat_cols[1].metric(
                    "Median Risk Score",
                    f"{scored_for_viz['risk_score'].median():.3f}"
                )
                stat_cols[2].metric(
                    "High Risk (≥0.8)",
                    f"{len(scored_for_viz[scored_for_viz['risk_score'] >= 0.8]):,}"
                )
                stat_cols[3].metric(
                    "Above Threshold",
                    f"{len(scored_for_viz[scored_for_viz['risk_score'] >= score_threshold]):,}"
                )
            else:
                st.warning("⚠️ Not enough data for distribution visualization")

    # Charts
    st.subheader("Insights")
    c1, c2 = st.columns(2)
    if "claim_amount" in df_f.columns and "claim_type" in df_f.columns:
        fig = px.box(df_f, x="claim_type", y="claim_amount", points="all", title="Claim Amount by Claim Type")
        c1.plotly_chart(fig, use_container_width=True)

    if "claim_amount" in df_f.columns and "policy_type" in df_f.columns:
        fig2 = px.violin(df_f, x="policy_type", y="claim_amount", box=True, points="all", title="Claim Amount by Policy Type")
        c2.plotly_chart(fig2, use_container_width=True)

    # Anomalies
    scored = flag_anomalies(df_f, z_threshold=z_threshold, score_threshold=score_threshold)
    flagged = scored[scored["flagged"]].copy().sort_values("risk_score", ascending=False)

    # Header with count
    num_flagged_final = len(flagged)
    pct_flagged_final = (num_flagged_final / len(df_f) * 100) if len(df_f) > 0 else 0
    st.subheader(f"Investigation Shortlist ({num_flagged_final:,} claims flagged - {pct_flagged_final:.1f}%)")
    st.write("**Flagged records** are displayed below with **risk scores** and **reason codes**.")

    # Toggle to highlight data quality issues
    if not flagged.empty:
        highlight_toggle = st.toggle(
            "🔍 Highlight rows with data quality issues",
            value=False,
            help="Shows which flagged claims have age/income out of range or suspicious duplicate values"
        )

        if highlight_toggle:
            st.caption("**Legend:** 🟡 Out of range | 🟠 Suspicious duplicate | 🔴 Both issues")

        # Identify rows with data quality issues
        if highlight_toggle and not flagged.empty:
            # Use original issues tracked BEFORE cleaning
            # This way imputed values still show as having had issues
            has_age_issue = pd.Series(False, index=flagged.index)
            for idx in flagged.index:
                if idx in original_age_issues.index:
                    has_age_issue.loc[idx] = original_age_issues.loc[idx]

            has_income_issue = pd.Series(False, index=flagged.index)
            income_col = None
            if 'annual_income' in flagged.columns:
                income_col = 'annual_income'
            elif 'salary' in flagged.columns:
                income_col = 'salary'

            if income_col:
                for idx in flagged.index:
                    if idx in original_income_issues.index:
                        has_income_issue.loc[idx] = original_income_issues.loc[idx]

            # Check for suspicious duplicates
            has_duplicate_issue = pd.Series(False, index=flagged.index)
            if duplicates_method != "Ignore" and income_col:
                # Detect duplicates in the full dataset (df_f), then check which flagged rows have them
                duplicates_in_full = detect_suspicious_duplicates(df_f, income_col, min_occurrences=dup_threshold)
                # Map back to flagged rows - convert to Series with proper index
                has_duplicate_issue = pd.Series(flagged.index.isin(df_f[duplicates_in_full].index), index=flagged.index)

            # Combine: any data quality issue
            has_data_issue = has_age_issue | has_income_issue | has_duplicate_issue
            num_with_issues = has_data_issue.sum()
            num_with_duplicates = has_duplicate_issue.sum()

            if num_with_issues > 0:
                issue_types = []
                if (has_age_issue | has_income_issue).sum() > 0:
                    issue_types.append("out of range")
                if num_with_duplicates > 0:
                    issue_types.append(f"{num_with_duplicates} suspicious duplicates")
                st.info(f"⚠️ {num_with_issues} of {len(flagged)} flagged claims have data quality issues ({', '.join(issue_types)})")

            # Style the dataframe to highlight problematic rows
            def highlight_quality_issues(row):
                row_idx = row.name

                # Check what type of issue this row has (use .loc with fallback)
                has_range_issue = (has_age_issue.loc[row_idx] if row_idx in has_age_issue.index else False) or \
                                  (has_income_issue.loc[row_idx] if row_idx in has_income_issue.index else False)
                has_dup_issue = has_duplicate_issue.loc[row_idx] if row_idx in has_duplicate_issue.index else False

                if has_range_issue and has_dup_issue:
                    # Both issues - darker amber with border
                    return ['background-color: rgba(255, 152, 0, 0.35); font-weight: 600; border-left: 3px solid #ff6b6b'] * len(row)
                elif has_range_issue:
                    # Out of range - amber
                    return ['background-color: rgba(255, 193, 7, 0.25); font-weight: 500'] * len(row)
                elif has_dup_issue:
                    # Suspicious duplicate - light orange
                    return ['background-color: rgba(255, 152, 0, 0.2); font-weight: 500; font-style: italic'] * len(row)
                return [''] * len(row)

            styled_df = flagged.head(100).style.apply(highlight_quality_issues, axis=1)
            st.dataframe(styled_df, use_container_width=True)
        else:
            st.dataframe(flagged.head(100))

        csv = flagged.to_csv(index=False).encode("utf-8")
        st.download_button("Download flagged CSV", csv, "flagged_claims.csv", "text/csv")
    else:
        st.info("No records flagged at current thresholds. Try lowering thresholds or inspecting box/violin plots.")

    # ========================================================================
    # ROI CALCULATOR WITH PRESETS
    # ========================================================================

    st.subheader("ROI Calculator")

    # Initialize presets in session state (editable via settings)
    if 'roi_presets' not in st.session_state:
        st.session_state.roi_presets = {
            'Conservative': {
                'fraud_rate': 3.0,
                'claim_amount': 5000.0,
                'improvement': 15.0,
                'volume': 1000
            },
            'Moderate': {
                'fraud_rate': 5.0,
                'claim_amount': 8500.0,
                'improvement': 25.0,
                'volume': 2500
            },
            'Optimistic': {
                'fraud_rate': 8.0,
                'claim_amount': 12000.0,
                'improvement': 35.0,
                'volume': 5000
            }
        }

    # Initialize default values (use actual dataset metrics)
    # Note: We recalculate this each time to reflect data cleaning changes
    actual_row_count = len(df_f)  # Use filtered dataset count
    actual_avg_claim = float(kpis.get('avg_claim_amount', 5000.0))

    if 'roi_defaults' not in st.session_state:
        st.session_state.roi_defaults = {
            'fraud_rate': 2.0,
            'claim_amount': actual_avg_claim,
            'improvement': 25.0,
            'volume': actual_row_count
        }
    else:
        # Update defaults with current dataset values (but don't override if user changed them)
        st.session_state.roi_defaults['claim_amount'] = actual_avg_claim
        st.session_state.roi_defaults['volume'] = actual_row_count

    # Current values (use session state to persist across reruns)
    if 'roi_current' not in st.session_state:
        st.session_state.roi_current = st.session_state.roi_defaults.copy()
        st.session_state.roi_using_defaults = True  # Track if using defaults or custom values

    # Auto-update volume and claim amount if user is still using defaults (not a preset)
    # This makes the ROI calculator responsive to data quality changes
    if st.session_state.get('roi_using_defaults', True):
        st.session_state.roi_current['volume'] = actual_row_count
        st.session_state.roi_current['claim_amount'] = actual_avg_claim

    # Preset buttons
    st.markdown("**Quick Scenarios:**")
    preset_cols = st.columns([1, 1, 1, 1, 2])

    if preset_cols[0].button("🟢 Conservative", help="Mature fraud detection program"):
        st.session_state.roi_current = st.session_state.roi_presets['Conservative'].copy()
        st.session_state.roi_using_defaults = False  # User clicked preset
        st.rerun()

    if preset_cols[1].button("🟡 Moderate", help="Typical ML implementation"):
        st.session_state.roi_current = st.session_state.roi_presets['Moderate'].copy()
        st.session_state.roi_using_defaults = False  # User clicked preset
        st.rerun()

    if preset_cols[2].button("🔴 Optimistic", help="High-fraud environment"):
        st.session_state.roi_current = st.session_state.roi_presets['Optimistic'].copy()
        st.session_state.roi_using_defaults = False  # User clicked preset
        st.rerun()

    if preset_cols[3].button("↺ Reset", help="Reset to default values (uses actual dataset)"):
        st.session_state.roi_current = st.session_state.roi_defaults.copy()
        st.session_state.roi_using_defaults = True  # Back to auto-updating
        st.rerun()

    # Input fields (use current values from session state)
    col_a, col_b, col_c, col_d = st.columns(4)

    avg_fraud_rate = col_a.number_input(
        "Est. suspicious rate (%)",
        value=st.session_state.roi_current['fraud_rate'],
        min_value=0.0,
        max_value=100.0,
        step=0.5,
        key="fraud_rate_input"
    )

    avg_claim_amt = col_b.number_input(
        "Avg suspicious claim amount ($)",
        value=st.session_state.roi_current['claim_amount'],
        step=100.0,
        key="claim_amt_input"
    )

    detection_improvement = col_c.number_input(
        "Detection improvement (%)",
        value=st.session_state.roi_current['improvement'],
        min_value=0.0,
        max_value=100.0,
        step=1.0,
        key="improvement_input",
        help="Improvement vs. baseline detection rate"
    )

    monthly_claim_volume = col_d.number_input(
        "Monthly claim volume",
        value=st.session_state.roi_current['volume'],
        step=10,
        key="volume_input",
        help=f"Using actual dataset size: {actual_row_count:,} rows (updates when you exclude data)"
    )

    # Update session state with current values
    st.session_state.roi_current = {
        'fraud_rate': avg_fraud_rate,
        'claim_amount': avg_claim_amt,
        'improvement': detection_improvement,
        'volume': monthly_claim_volume
    }

    # Calculate ROI
    suspicious_claims = monthly_claim_volume * (avg_fraud_rate / 100.0)
    improved_catches = suspicious_claims * (detection_improvement / 100.0)
    savings = improved_catches * avg_claim_amt

    # Display results
    result_cols = st.columns([2, 1])
    result_cols[0].metric("Estimated Monthly Savings", f"${savings:,.0f}")
    result_cols[1].metric("Annual Savings", f"${savings * 12:,.0f}")

    st.caption("💡 Adjust assumptions to match your environment. We can calibrate with historicals during pilot.")

    # Settings expander for editing presets
    with st.expander("⚙️ Preset Settings (Edit Scenarios)", expanded=False):
        st.markdown("**Customize preset scenarios:**")

        # Lock/Unlock toggle for security demo
        if 'presets_unlocked' not in st.session_state:
            st.session_state.presets_unlocked = True  # Default to unlocked for demo

        lock_col1, lock_col2 = st.columns([3, 1])
        lock_col1.markdown("🔒 **Access Control** (Production Feature)")

        is_unlocked = lock_col2.toggle(
            "🔓 Unlocked" if st.session_state.presets_unlocked else "🔒 Locked",
            value=st.session_state.presets_unlocked,
            key="preset_lock_toggle",
            help="In production, only admins can modify presets"
        )
        st.session_state.presets_unlocked = is_unlocked

        if not is_unlocked:
            st.warning("🔒 Preset editing is locked. In production, this would require admin privileges (role-based access control).")
        else:
            st.info("🔓 Preset editing is unlocked. Admins can customize scenarios for different use cases.")

        st.divider()

        # Only show preset editing if unlocked
        if is_unlocked:
            for preset_name in ['Conservative', 'Moderate', 'Optimistic']:
                st.markdown(f"**{preset_name} Scenario:**")
                preset_cols = st.columns(4)

                new_fraud = preset_cols[0].number_input(
                    "Fraud %",
                    value=st.session_state.roi_presets[preset_name]['fraud_rate'],
                    min_value=0.0,
                    max_value=100.0,
                    step=0.5,
                    key=f"preset_{preset_name}_fraud"
                )

                new_claim = preset_cols[1].number_input(
                    "Claim $",
                    value=st.session_state.roi_presets[preset_name]['claim_amount'],
                    step=100.0,
                    key=f"preset_{preset_name}_claim"
                )

                new_improvement = preset_cols[2].number_input(
                    "Improve %",
                    value=st.session_state.roi_presets[preset_name]['improvement'],
                    min_value=0.0,
                    max_value=100.0,
                    step=1.0,
                    key=f"preset_{preset_name}_improvement"
                )

                new_volume = preset_cols[3].number_input(
                    "Volume",
                    value=st.session_state.roi_presets[preset_name]['volume'],
                    step=100,
                    key=f"preset_{preset_name}_volume"
                )

                # Update preset values
                st.session_state.roi_presets[preset_name] = {
                    'fraud_rate': new_fraud,
                    'claim_amount': new_claim,
                    'improvement': new_improvement,
                    'volume': new_volume
                }

            st.caption("💡 Changes to presets are saved for this session. Click preset buttons above to use them.")

else:
    # Landing page - no data loaded yet
    st.markdown("---")

    # Key Features Section
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🎯 Smart Detection")
        st.markdown("""
        **Machine Learning + Statistics**
        - IsolationForest anomaly detection
        - Z-score statistical analysis
        - Transparent risk scoring
        - Automatic reason codes
        """)

    with col2:
        st.markdown("### 📊 Data Quality")
        st.markdown("""
        **Automated Validation**
        - Age/income range checking
        - Suspicious duplicate detection
        - Configurable handling rules
        - Real-time quality reports
        """)

    with col3:
        st.markdown("### 💰 Business Impact")
        st.markdown("""
        **ROI Calculator**
        - Industry-backed estimates
        - Preset scenarios
        - Live dataset integration
        - Monthly/annual projections
        """)

    st.markdown("---")

    # Value Proposition
    st.markdown("### Why This Matters")
    metric_cols = st.columns(4)
    metric_cols[0].metric("Industry Fraud Rate", "3-10%", help="NHCAA estimate")
    metric_cols[1].metric("ML Improvement", "20-45%", help="Detection rate increase")
    metric_cols[2].metric("Processing Time", "< 2 sec", help="For 10K+ claims")
    metric_cols[3].metric("False Positives", "Minimized", help="Tunable thresholds")

    st.markdown("---")

    # Call to Action
    st.info("👆 **Get Started:** Upload your CSV file above or click 'Use minimal sample data' to explore with demo data.")
