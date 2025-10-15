import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

NUMERIC_CANDIDATES = [
    "claim_amount", "policy_premium", "annual_income", "age", "tenure_months"
]

CATEGORICAL_CANDIDATES = [
    "region", "state", "policy_type", "claim_type", "incident_severity",
    "vehicle_segment", "marital_status", "customer_education"
]

def coalesce_columns(df: pd.DataFrame):
    # Normalize column names
    df = df.copy()
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Friendly aliases (map common variants to a standard set)
    alias_map = {
        # Claim amount variations
        "total_claim_amount": "claim_amount",
        "total_claim_value": "claim_amount",
        "claim_value": "claim_amount",
        "amount": "claim_amount",
        "coverage_amount": "claim_amount",  # data_synthetic.csv

        # Premium variations
        "premium": "policy_premium",
        "policy_annual_premium": "policy_premium",
        "premium_amount": "policy_premium",  # data_synthetic.csv

        # Education variations
        "education": "customer_education",
        "education_level": "customer_education",

        # Income variations
        "salary": "annual_income",
        "income": "annual_income",  # insurance_dataset.csv
        "income_level": "annual_income",  # data_synthetic.csv

        # State/Location variations
        "state_code": "state",
        "location": "state",  # data_synthetic.csv
        "geographic_information": "region",  # data_synthetic.csv

        # ID variations
        "customer_id": "claim_id",  # data_synthetic.csv

        # Other mappings
        "customer_lifetime_value": "lifetime_value",
        "customer_value": "lifetime_value",
        "months_since_policy_inception": "tenure_months",
        "policy_tenure": "tenure_months",
        "marital_status": "marital_status",  # normalize both variants
        "claim_history": "previous_claims",  # data_synthetic.csv
        "previous_claims_history": "previous_claims",  # data_synthetic.csv
    }
    for old, new in alias_map.items():
        if old in df.columns and new not in df.columns:
            df.rename(columns={old: new}, inplace=True)

    return df

def compute_kpis(df: pd.DataFrame):
    kpis = {}
    if "claim_amount" in df.columns:
        kpis["total_claims_amount"] = float(df["claim_amount"].fillna(0).sum())
        kpis["avg_claim_amount"] = float(df["claim_amount"].dropna().mean())
    kpis["num_claims"] = int(len(df))
    if "policy_premium" in df.columns and "claim_amount" in df.columns:
        # crude proxy for loss ratio if premium exists
        premiums = df["policy_premium"].fillna(0).sum()
        claims = df["claim_amount"].fillna(0).sum()
        kpis["loss_ratio_proxy"] = float(claims / premiums) if premiums > 0 else None
    return kpis

def isolation_forest_scores(df: pd.DataFrame, random_state=42):
    # Build a simple numeric feature matrix
    num_cols = [c for c in NUMERIC_CANDIDATES if c in df.columns]
    if not num_cols:
        return pd.Series([0.0] * len(df), index=df.index)
    X = df[num_cols].fillna(0.0).astype(float).values
    model = IsolationForest(n_estimators=200, contamination="auto", random_state=random_state)
    scores = -model.fit_predict(X)  # 1 for normal, -1 for anomaly; invert to score-like
    # decision_function gives anomaly scores; lower = more abnormal
    decision = model.decision_function(X)
    # Normalize to 0..1 (higher = more anomalous)
    dec_min, dec_max = decision.min(), decision.max()
    if dec_max == dec_min:
        norm = np.zeros_like(decision)
    else:
        norm = (dec_max - decision) / (dec_max - dec_min)
    return pd.Series(norm, index=df.index)

def category_amount_zscores(df: pd.DataFrame, category_col: str, amount_col="claim_amount"):
    if amount_col not in df.columns or category_col not in df.columns:
        return pd.Series([np.nan]*len(df), index=df.index)
    def zscore(s):
        m = s.mean()
        sd = s.std(ddof=0)
        if sd == 0 or np.isnan(sd):
            return (s - m) * 0.0
        return (s - m) / sd
    z = df.groupby(category_col)[amount_col].transform(zscore)
    return z

def flag_anomalies(df: pd.DataFrame, iforest_weight=0.6, zscore_weight=0.4, z_threshold=2.5, score_threshold=0.65):
    out = df.copy()
    out["anomaly_iforest"] = isolation_forest_scores(out).fillna(0.0)

    # Try a couple of categorical pivots if present
    zcomponents = []
    for cat in ["claim_type", "policy_type", "state", "region"]:
        if cat in out.columns:
            z = category_amount_zscores(out, cat)
            zcomponents.append(z.abs())
    if zcomponents:
        out["anomaly_z"] = pd.concat(zcomponents, axis=1).mean(axis=1)
    else:
        out["anomaly_z"] = 0.0

    # Combine signals
    out["risk_score"] = (iforest_weight * out["anomaly_iforest"].fillna(0.0) +
                         zscore_weight * (out["anomaly_z"].fillna(0.0) / max(out["anomaly_z"].max(), 1.0)))

    # Reason codes
    reasons = []
    for _, row in out.iterrows():
        r = []
        if row.get("anomaly_iforest", 0) >= score_threshold:
            r.append("IsolationForest outlier")
        if row.get("anomaly_z", 0) >= z_threshold:
            r.append("Category z-score high")
        reasons.append(", ".join(r) if r else "—")
    out["risk_reason"] = reasons

    # Flag
    out["flagged"] = (out["anomaly_iforest"] >= score_threshold) | (out["anomaly_z"] >= z_threshold)
    return out

def safe_float(x):
    try:
        return float(x)
    except Exception:
        return None


# ============================================================================
# DATA QUALITY UTILITIES
# ============================================================================

AGE_MIN_DEFAULT = 18
AGE_MAX_DEFAULT = 90
INCOME_MIN_DEFAULT = 10000
INCOME_MAX_DEFAULT = 500000


def _to_float_series(s: pd.Series) -> pd.Series:
    """Safely convert series to float, coercing errors to NaN."""
    try:
        return pd.to_numeric(s, errors="coerce")
    except Exception:
        return pd.Series([np.nan] * len(s), index=s.index)


def handle_numeric_outliers(
    df: pd.DataFrame,
    column: str,
    method: str = "impute_mean",
    min_val: float | None = None,
    max_val: float | None = None,
    round_to_int: bool = True
) -> tuple[pd.DataFrame, int, float | None]:
    """
    Clean numeric column by handling out-of-range values.

    Args:
        df: Input DataFrame
        column: Column name to clean
        method: One of ["impute_mean", "exclude", "leave"]
            - "impute_mean": Replace out-of-range with mean of valid values
            - "exclude": Remove rows with out-of-range values
            - "leave": No changes, just report count
        min_val: Minimum valid value (inclusive)
        max_val: Maximum valid value (inclusive)
        round_to_int: If True, round imputed values to nearest integer

    Returns:
        (cleaned_df, affected_count, imputed_value_or_None)

    Examples:
        >>> df, count, value = handle_numeric_outliers(
        ...     df, "age", method="impute_mean", min_val=18, max_val=90
        ... )
        >>> print(f"Fixed {count} ages, imputed value: {value}")
    """
    if column not in df.columns:
        return df.copy(), 0, None

    out = df.copy()
    out[column] = _to_float_series(out[column])

    # Define valid range
    lo = -np.inf if min_val is None else float(min_val)
    hi = np.inf if max_val is None else float(max_val)

    # Identify valid and invalid rows
    valid_mask = (out[column] >= lo) & (out[column] <= hi) & out[column].notna()
    affected = int((~valid_mask & out[column].notna()).sum())

    if affected == 0:
        return out, 0, None

    if method == "leave":
        return out, affected, None

    if method == "exclude":
        return out[valid_mask | out[column].isna()].copy(), affected, None

    # method == "impute_mean"
    valid_values = out.loc[valid_mask, column]

    if len(valid_values) == 0:
        # No valid values, use midpoint of range
        if np.isfinite(lo) and np.isfinite(hi):
            imputed_value = (lo + hi) / 2.0
        else:
            imputed_value = 0.0
    else:
        imputed_value = float(valid_values.mean())

    if round_to_int:
        imputed_value = round(imputed_value)

    out.loc[~valid_mask, column] = imputed_value

    return out, affected, imputed_value


def get_data_quality_summary(df: pd.DataFrame) -> dict:
    """
    Generate data quality summary statistics for key columns.

    Returns dict with column names as keys and quality metrics as values.
    Useful for reporting and audit trails.
    """
    summary = {}

    for col in ["age", "annual_income", "claim_amount"]:
        if col not in df.columns:
            continue

        series = _to_float_series(df[col])
        summary[col] = {
            "missing_count": int(series.isna().sum()),
            "missing_pct": float(series.isna().sum() / len(series) * 100),
            "min": float(series.min()) if not series.isna().all() else None,
            "max": float(series.max()) if not series.isna().all() else None,
            "mean": float(series.mean()) if not series.isna().all() else None,
        }

    return summary


def detect_suspicious_duplicates(
    df: pd.DataFrame,
    column: str,
    min_occurrences: int = 10,
    precision_threshold: int = 4
) -> pd.Series:
    """
    Detect suspicious duplicate values in a numeric column.

    Returns a boolean Series indicating which rows have suspicious duplicate values.

    A value is considered "suspicious" if:
    1. It appears more than min_occurrences times in the dataset
    2. It has unusual precision (more than precision_threshold decimal places)

    Args:
        df: Input DataFrame
        column: Column name to check for duplicates
        min_occurrences: Minimum number of times a value must appear to be flagged (default: 10)
        precision_threshold: Number of decimal places that's considered suspicious (default: 4)

    Returns:
        Boolean Series with same index as df, True for suspicious duplicates

    Examples:
        >>> suspicious = detect_suspicious_duplicates(df, "annual_income", min_occurrences=10)
        >>> print(f"Found {suspicious.sum()} suspicious duplicate income values")
    """
    if column not in df.columns:
        return pd.Series(False, index=df.index)

    suspicious = pd.Series(False, index=df.index)

    # Convert to float for numeric analysis
    values = _to_float_series(df[column])

    # Count occurrences of each value
    value_counts = values.value_counts()

    # Find values that appear too frequently
    frequent_values = value_counts[value_counts >= min_occurrences].index.tolist()

    # Check if values have suspicious precision (many decimal places)
    for val in frequent_values:
        if pd.notna(val):
            # Convert to string and check decimal places
            val_str = f"{val:.10f}".rstrip('0')  # Remove trailing zeros
            if '.' in val_str:
                decimal_places = len(val_str.split('.')[1])
                if decimal_places >= precision_threshold:
                    # This value appears frequently AND has high precision - very suspicious
                    suspicious |= (values == val)
                else:
                    # Appears frequently but normal precision - might be legitimate (e.g., common salary tiers)
                    # Still flag it, but less suspicious
                    suspicious |= (values == val)

    return suspicious
