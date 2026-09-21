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

    # Drop Unecessary columns
    claims_processed_df = claims_processed_df.drop(
        columns=["id", "hash_key", "insert_date"])

    sessions_df = sessions_df.drop(
        columns=["id", "hash_key", "insert_date", "payer"])

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

    # ---------------------------------------------------------
    # 2. Choose the revenue measure
    # ---------------------------------------------------------
    # If Jane provides billed_amount or charge_amount, use that.
    # Otherwise fall back to actual_collected (cash proxy).
    if "billed_amount" in jane_merged_df.columns:
        jane_merged_df["revenue_accrual"] = jane_merged_df["billed_amount"]
    else:
        jane_merged_df["revenue_accrual"] = jane_merged_df["Actual Collected"]

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

    # Recompute Actual Collected per claim
    merged['Actual Collected'] = round(
        merged['collected'] + merged['processing_fee'] /
        merged['claim_count'].replace(0, np.nan), 2
    )
    merged['Actual Collected'] = merged['Actual Collected'].fillna(0)
    merged.loc[merged['status'] == 'no_charge', 'Actual Collected'] = 0

    # --- Step 5: Re-convert dates after merge ---
    merged["payment_date"] = pd.to_datetime(
        merged["payment_date"], errors="coerce")
    merged["invoice_date"] = pd.to_datetime(
        merged["invoice_date"], errors="coerce")

    merged["Days Between invoice and Payment"] = (
        merged["payment_date"] - merged["invoice_date"]
    ).apply(lambda x: x.days if pd.notnull(x) else None)

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
               'purchase_date', 'payment_date', 'Days Between invoice and Payment',
               'payer', 'reference_number', 'employee_initials', 'item',
               'invoice_number',  'applied_to', 'claim_count', 'amount',
               'processing_fee', 'amount_paid_to_clinic', 'status', 'subtotal',
               'total', 'balance', 'revenue_accrual', 'Actual Collected']

    revenue_details = jane_claims_merged[columns]

    revenue_details['purchase_date'] = revenue_details['purchase_date'].dt.strftime(
        "%b. %d, %Y")

    return revenue_details
