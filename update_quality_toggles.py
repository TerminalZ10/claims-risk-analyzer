#!/usr/bin/env python3
"""
update_quality_toggles.py

Adds Data Quality controls to the Claims Risk Analyzer:
- Age validation and cleaning (impute mean, exclude, or leave as-is)
- Income/Salary validation and cleaning
- Visual feedback in UI showing what was cleaned
- Backups created automatically

Usage:
    python3 update_quality_toggles.py

Then run your app:
    streamlit run app.py
"""

import re
import shutil
from pathlib import Path
from datetime import datetime

# Configuration
PROJECT = Path(".")
HELPERS = PROJECT / "helpers.py"
APP = PROJECT / "app.py"

# Data quality defaults (conservative ranges for health insurance)
AGE_MIN = 18
AGE_MAX = 90
INCOME_MIN = 10000
INCOME_MAX = 500000

def validate_files():
    """Ensure we're in the right directory with required files."""
    if not HELPERS.exists() or not APP.exists():
        raise SystemExit(
            "❌ Error: Run this script from the project folder containing helpers.py and app.py\n"
            f"   Current directory: {PROJECT.absolute()}"
        )
    print(f"✓ Found helpers.py and app.py in {PROJECT.absolute()}")

def backup(p: Path):
    """Create timestamped backup of a file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = p.parent / f"{p.stem}_{timestamp}.bak"
    shutil.copyfile(p, bak)
    print(f"  ✓ Backup created: {bak.name}")
    return bak

# ============================================================================
# HELPERS.PY PATCHES
# ============================================================================

def patch_helpers_imports(src: str) -> str:
    """Ensure pandas and numpy are imported."""
    if "import pandas as pd" not in src:
        src = "import pandas as pd\n" + src
    if "import numpy as np" not in src:
        # Find first import and add after it
        lines = src.splitlines()
        for i, line in enumerate(lines):
            if "import pandas" in line:
                lines.insert(i + 1, "import numpy as np")
                break
        src = "\n".join(lines)
    return src

def add_salary_alias(src: str) -> str:
    """Add 'salary' -> 'annual_income' alias mapping."""
    # Find the alias_map dictionary
    pattern = r'(alias_map\s*=\s*\{[^}]*)'

    def add_alias(match):
        content = match.group(1)
        if '"salary"' in content or "'salary'" in content:
            return content  # already has it
        # Add before the closing brace
        return content + '\n        "salary": "annual_income",'

    if "alias_map" in src:
        src = re.sub(pattern, add_alias, src)

    return src

def add_data_quality_utils(src: str) -> str:
    """Append data quality utility functions to helpers.py."""

    if "def handle_numeric_outliers" in src:
        print("  ℹ️  Data quality utilities already present, skipping")
        return src

    utilities = f'''

# ============================================================================
# DATA QUALITY UTILITIES
# ============================================================================

AGE_MIN_DEFAULT = {AGE_MIN}
AGE_MAX_DEFAULT = {AGE_MAX}
INCOME_MIN_DEFAULT = {INCOME_MIN}
INCOME_MAX_DEFAULT = {INCOME_MAX}


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
        >>> print(f"Fixed {{count}} ages, imputed value: {{value}}")
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
    summary = {{}}

    for col in ["age", "annual_income", "claim_amount"]:
        if col not in df.columns:
            continue

        series = _to_float_series(df[col])
        summary[col] = {{
            "missing_count": int(series.isna().sum()),
            "missing_pct": float(series.isna().sum() / len(series) * 100),
            "min": float(series.min()) if not series.isna().all() else None,
            "max": float(series.max()) if not series.isna().all() else None,
            "mean": float(series.mean()) if not series.isna().all() else None,
        }}

    return summary
'''

    if not src.endswith("\n"):
        src += "\n"

    return src + utilities


def patch_helpers():
    """Apply all patches to helpers.py."""
    print("\n📝 Patching helpers.py...")
    src = HELPERS.read_text()

    src = patch_helpers_imports(src)
    src = add_salary_alias(src)
    src = add_data_quality_utils(src)

    return src


# ============================================================================
# APP.PY PATCHES
# ============================================================================

def patch_app_imports(src: str) -> str:
    """Update imports from helpers module."""
    # Find the existing import line
    pattern = r"from helpers import[^\n]+"

    new_import = """from helpers import (
    coalesce_columns, compute_kpis, flag_anomalies, safe_float,
    handle_numeric_outliers, get_data_quality_summary,
    AGE_MIN_DEFAULT, AGE_MAX_DEFAULT,
    INCOME_MIN_DEFAULT, INCOME_MAX_DEFAULT
)"""

    if re.search(pattern, src):
        return re.sub(pattern, new_import, src, count=1)

    # If not found, add after other imports
    lines = src.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("import streamlit"):
            lines.insert(i + 1, new_import)
            return "\n".join(lines)

    # Fallback: prepend
    return new_import + "\n\n" + src


def add_sidebar_quality_controls(src: str) -> str:
    """Add data quality controls to sidebar."""

    # Find where to insert (after anomaly detection settings)
    anchor = "if score_threshold is None: score_threshold = 0.65"

    if anchor not in src:
        print("  ⚠️  Warning: Could not find insertion point for sidebar controls")
        return src

    controls = '''
        if score_threshold is None: score_threshold = 0.65

        st.divider()
        st.subheader("Data Quality")

        with st.expander("Age Validation", expanded=False):
            st.markdown("Configure how to handle age values outside the valid range.")
            age_method = st.radio(
                "Age handling method",
                options=["Impute mean", "Exclude rows", "Leave as-is"],
                index=0,
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
                index=0,
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
'''

    return src.replace(anchor, controls, 1)


def add_data_cleaning_logic(src: str) -> str:
    """Add data cleaning logic after coalesce_columns call."""

    anchor = "df = coalesce_columns(df)"

    if anchor not in src:
        print("  ⚠️  Warning: Could not find insertion point for cleaning logic")
        return src

    cleaning_code = '''
    df = coalesce_columns(df)

    # ========================================================================
    # DATA QUALITY CLEANING (controlled by sidebar settings)
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

    if income_col:
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

    rows_removed = original_row_count - len(df)
'''

    return src.replace(anchor, cleaning_code, 1)


def add_quality_feedback_ui(src: str) -> str:
    """Add visual feedback about data quality cleaning."""

    # Insert before KPI metrics display
    anchor = "# KPIs"

    if anchor not in src:
        print("  ⚠️  Warning: Could not find insertion point for quality feedback")
        return src

    feedback_code = '''
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

    # Display quality summary if any issues found
    if quality_messages:
        with st.expander("📊 Data Quality Report", expanded=True):
            for msg in quality_messages:
                st.markdown(msg)
            if rows_removed > 0:
                st.info(f"**Total rows removed**: {rows_removed} of {original_row_count} ({rows_removed/original_row_count*100:.1f}%)")
            st.caption("💡 Adjust settings in the sidebar to change how data quality issues are handled.")

    # KPIs'''

    return src.replace(anchor, feedback_code, 1)


def patch_app():
    """Apply all patches to app.py."""
    print("\n📝 Patching app.py...")
    src = APP.read_text()

    src = patch_app_imports(src)
    src = add_sidebar_quality_controls(src)
    src = add_data_cleaning_logic(src)
    src = add_quality_feedback_ui(src)

    return src


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function."""
    print("\n" + "="*70)
    print("  Claims Risk Analyzer - Data Quality Toggle Installer")
    print("="*70)

    try:
        # Validate environment
        validate_files()

        # Create backups
        print("\n💾 Creating backups...")
        helpers_bak = backup(HELPERS)
        app_bak = backup(APP)

        # Apply patches
        patched_helpers = patch_helpers()
        patched_app = patch_app()

        # Write updated files
        print("\n✍️  Writing updated files...")
        HELPERS.write_text(patched_helpers)
        print(f"  ✓ Updated {HELPERS.name}")

        APP.write_text(patched_app)
        print(f"  ✓ Updated {APP.name}")

        # Success message
        print("\n" + "="*70)
        print("✅ SUCCESS! Data quality toggles installed.")
        print("="*70)
        print("\nNew features added:")
        print("  • Age validation with configurable min/max ranges")
        print("  • Income/salary validation with configurable ranges")
        print("  • Three handling modes: Impute mean, Exclude rows, Leave as-is")
        print("  • Visual feedback showing what was cleaned")
        print("  • Data quality summary in expandable section")
        print("\nBackups created:")
        print(f"  • {helpers_bak.name}")
        print(f"  • {app_bak.name}")
        print("\nNext steps:")
        print("  1. Run: streamlit run app.py")
        print("  2. Check sidebar for new 'Data Quality' section")
        print("  3. Test with sample data or upload your CSV")
        print("\n💡 Pro tip: Show this feature in your demo to demonstrate")
        print("   data validation and ETL capabilities!")
        print("="*70 + "\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nIf backups were created, you can restore them manually.")
        raise


if __name__ == "__main__":
    main()
