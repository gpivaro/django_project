import pandas as pd
import numpy as np
from clinic_dash_pro.helper.helper import ty_ly_py

# ---------------------------------------------------------
# Main Jane ingestion function
# ---------------------------------------------------------


def merge_claims_sessions(claims_processed_df, sessions_df):
    """
    Ingests:
    - Jane Transactions Report (payments)
    - Jane Sales Report (appointments/invoices)

    Steps:
    1. Load both CSVs
    2. Normalize columns
    3. Normalize payer names
    4. Count claims
    5. Merge transactions with sales
    6. Validate financial totals
    7. Export cleaned dataset
    8. Load into DB
    """

    claims_processed_df = claims_processed_df.copy()
    sessions_df = sessions_df.copy()

    columns_to_drop = [
        "id",
        "hash_key",
        "insert_date",
        "updated_date",
        "period_month",
        "period_quarter",
        "period_year",
        "ty_ly_py",
    ]

    claims_processed_df = claims_processed_df.drop(
        columns=columns_to_drop, errors="ignore")
    sessions_df = sessions_df.drop(
        columns=columns_to_drop, errors="ignore")

    sessions_df = sessions_df.drop(columns="payer", errors="ignore")

    # ---------------------------------------------------------
    # Step 3: Merge transactions with sales (attach therapist)
    # ---------------------------------------------------------
    jane_merged_df = attach_therapist_to_transactions(
        claims_processed_df, sessions_df)

    # Drop rows missing purchase_date
    jane_merged_df = jane_merged_df[
        jane_merged_df["purchase_date"].notna() &
        (jane_merged_df["purchase_date"].astype(str).str.strip() != "")
    ]

    # Sort by payment_date
    jane_merged_df.sort_values(by='payment_date', inplace=True)
    jane_merged_df = jane_merged_df.reset_index(drop=True)

    return jane_merged_df


# ---------------------------------------------------------
# Core: Attach therapist data to Jane transactions
# ---------------------------------------------------------
def attach_therapist_to_transactions(claims_processed_df, sessions_df):
    """
    Steps:
    1. Normalize applied_to column → list of claim IDs
    2. Explode multi-claim rows
    3. Merge with Jane sales report (therapist + invoice data)
    4. Recompute Actual Collected
    5. Recompute dates
    6. Validate financial totals remain unchanged

    This ensures:
    - Each claim is linked to the correct therapist
    - Multi-claim payments are properly exploded
    - Financial totals remain identical to original
    """

    # --- Step 1: Keep original financial totals for validation ---
    original_financials = claims_processed_df[
        ['amount', 'processing_fee', 'amount_paid_to_clinic']
    ].copy()

    # Add unique payment ID for grouping later
    claims_processed_df['payment_id'] = claims_processed_df.index

    # --- Step 2: Normalize applied_to column ---
    claims_processed_df['applied_to'] = claims_processed_df['applied_to'].fillna(
        '')

    claims_processed_df['applied_to'] = claims_processed_df['applied_to'].apply(
        lambda x: [item.strip() for item in str(x).split(',') if item.strip()]
    )

    # --- Step 3: Explode multi-claim rows ---
    exploded = claims_processed_df.explode('applied_to')

    exploded['applied_to'] = exploded['applied_to'].apply(
        lambda x: x.replace("[", "").replace("]", "").replace("'", ""))

    # --- Step 4: Merge with therapist data from sales report ---
    merged = exploded.merge(
        sessions_df,
        left_on='applied_to',
        right_on='invoice_number',
        how='left'
    )

    # Recompute Actual Collected/revenue accrual per claim
    merged['revenue_accrual'] = round(
        merged['collected'] + merged['processing_fee'] /
        merged['claim_count'].replace(0, np.nan), 2
    )
    merged['revenue_accrual'] = merged['revenue_accrual'].fillna(0)
    merged.loc[merged['status'] == 'no_charge', 'revenue_accrual'] = 0

    # Calculate the processing fee per claim
    merged['processing_fee_invoice'] = round(
        merged['processing_fee'] /
        merged['claim_count'].replace(0, np.nan), 2
    )
    merged['processing_fee_invoice'] = merged['processing_fee_invoice'].fillna(
        0)

    # --- Step 5: Re-convert dates after merge ---
    merged["payment_date"] = pd.to_datetime(
        merged["payment_date"], errors="coerce")
    merged["invoice_date"] = pd.to_datetime(
        merged["invoice_date"], errors="coerce")

    merged["Days Until Paid"] = (
        merged["payment_date"] - merged["invoice_date"]
    ).apply(lambda x: x.days if pd.notnull(x) else None).fillna(0).astype("int")

    # Convert date columns to datetime.date
    date_cols = ["payment_date", "invoice_date", "purchase_date"]
    for col in date_cols:
        if col in merged.columns:
            merged[col] = pd.to_datetime(merged[col], errors="coerce").dt.date

    merged["purchase_date"] = pd.to_datetime(
        merged["purchase_date"], errors="coerce")
    merged["period_month"] = merged["purchase_date"].dt.to_period("M")
    merged["period_quarter"] = merged["purchase_date"].dt.to_period("Q")
    merged["period_year"] = merged["purchase_date"].dt.to_period("Y")
    # Add ty_ly_py to the data
    merged = ty_ly_py(merged, "period_year")

    # --- Step 6: Validate financial integrity ---
    key_cols = ['amount', 'processing_fee', 'amount_paid_to_clinic']

    merged_totals = merged.groupby('payment_id')[key_cols].first()

    comparison = merged_totals.compare(original_financials)

    if not comparison.empty:
        print("⚠️ Financial Integrity Warning: Totals changed after merge!")
        print("Differences:")
        print(comparison)
    else:
        print("\n✅ Financial validation passed — merged totals match original.\n")

    return merged


def revenue_details(jane_claims_merged):

    columns = ['period_year', 'ty_ly_py', 'period_quarter', 'period_month',
               'purchase_date', 'payment_date', 'Days Until Paid',
               'payer', 'reference_number', 'employee_initials', 'item',
               'invoice_number', 'invoice_group', 'applied_to', 'refund', 'claim_count', 'amount',
               'processing_fee', 'amount_paid_to_clinic', 'status', 'subtotal',
               'total', 'balance', 'processing_fee_invoice', 'revenue_accrual']

    revenue_details = jane_claims_merged[columns]

    # Break view → make independent DataFrame
    revenue_details = revenue_details.copy()

    # Break dtype
    revenue_details['purchase_date'] = revenue_details['purchase_date'].astype(
        'object')

    # Assign formatted strings
    revenue_details['purchase_date'] = (
        revenue_details['purchase_date']
        .apply(lambda x: x.strftime('%Y-%m-%d') if hasattr(x, 'strftime') else x)
    )

    return revenue_details


def report_sessions_overview(jane_sessions):
    """
    Build a grouped overview of Jane Sessions:
    - Validates required columns
    - Cleans column names
    - Handles missing numeric columns
    - Groups by key fields
    - Sums numeric columns
    - Returns a safe, aggregated DataFrame
    """

    # --- 1. Clean column names (strip spaces, lower, etc.) ---
    jane_sessions = jane_sessions.copy()
    jane_sessions.columns = jane_sessions.columns.str.strip()

    # --- 2. Define grouping + numeric columns ---
    group_cols = [
        'period_year', 'ty_ly_py', 'period_quarter', 'period_month',
        'purchase_date', 'invoice_date', 'invoice_group',
        'item', 'status', 'employee_initials'
    ]

    numeric_cols = ['subtotal', 'total', 'collected', 'balance']

    # --- 3. Validate columns exist ---
    missing_group = [c for c in group_cols if c not in jane_sessions.columns]
    missing_numeric = [
        c for c in numeric_cols if c not in jane_sessions.columns]

    if missing_group:
        print(f"⚠️ Missing group columns: {missing_group}")

    if missing_numeric:
        print(f"⚠️ Missing numeric columns: {missing_numeric}")

    # Only use columns that exist
    group_cols = [c for c in group_cols if c in jane_sessions.columns]
    numeric_cols = [c for c in numeric_cols if c in jane_sessions.columns]

    if not group_cols:
        raise ValueError("❌ No valid grouping columns found.")

    if not numeric_cols:
        print("⚠️ No numeric columns found — returning ungrouped data.")
        return jane_sessions[group_cols].copy()

    # --- 4. Convert numeric columns safely ---
    for col in numeric_cols:
        jane_sessions[col] = pd.to_numeric(
            jane_sessions[col], errors="coerce").fillna(0)

    # --- 5. Group + aggregate ---
    try:
        sessions_overview = (
            jane_sessions[group_cols + numeric_cols]
            .groupby(group_cols, dropna=False)
            .agg({col: 'sum' for col in numeric_cols})
            .reset_index()
        )
    except Exception as e:
        print(f"❌ Error during grouping: {e}")
        return jane_sessions[group_cols + numeric_cols].copy()

    return sessions_overview
