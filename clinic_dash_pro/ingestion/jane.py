import pandas as pd
import hashlib

from clinic_dash_pro.helper.helper import normalize_columns, auto_numeric_columns, to_initials, build_staff_short_name
from clinic_dash_pro.ingestion.database import load_jane_sessions_to_db, load_jane_processed_claims_to_db

# ---------------------------------------------------------
# Utility: Count number of claims in applied_to column
# ---------------------------------------------------------


def count_claims(applied_to_value):
    """
    Count valid claim IDs in an applied_to cell.

    Handles:
    - NaN
    - blank strings
    - whitespace
    - 'nan'
    """
    if applied_to_value is None:
        return 0

    text = str(applied_to_value).strip()

    if text == "" or text.lower() == "nan":
        return 0

    # Split by comma → multiple claim IDs
    parts = text.split(',')

    # Remove empty entries
    cleaned = [p.strip() for p in parts if p.strip()]

    return len(cleaned)

# ---------------------------------------------------------
# Utility: Replace exact text values in a column
# ---------------------------------------------------------


def replace_entries(df, search_column, new_column, old_value, new_value):
    """
    Replace specific payer or payment_method values.

    Example:
        Replace "Texas Children's Health Plan - CHIP"
        with "Texas Children's Health Plan"

    This helps normalize payer names across Jane exports.
    """
    df.loc[df[search_column] == old_value, new_column] = new_value
    return df

# ---------------------------------------------------------
# Utility: Replace using regex
# ---------------------------------------------------------


def replace_with_regex(df, column, replace_text, new_text):
    """
    Replace text using a regex pattern.

    Example:
        Replace any "Jane Payments - XYZ" with "Jane Payments"
    """
    df[column] = df[column].str.replace(replace_text, new_text, regex=True)
    return df


def make_jane_sessions_hash(row):
    """
    Stable hash for Jane Sessions rows.
    Identical rows inside the same file are treated as distinct.
    Identical rows across uploads are deduped.
    """

    def norm(v):
        if v is None or pd.isna(v):
            return ""
        v = str(v).strip().lower()
        v = v.replace("\xa0", " ")
        v = " ".join(v.split())
        return v

    key_fields = [
        norm(row.get("purchase_date")),
        norm(row.get("invoice_date")),
        norm(row.get("item")),
        norm(row.get("staff_member")),
        norm(row.get("employee_initials")),
        norm(row.get("payer")),
        norm(row.get("invoice_number")),
        norm(row.get("status")),
        norm(row.get("subtotal")),
        norm(row.get("total")),
        norm(row.get("collected")),
        norm(row.get("balance")),
        # synthetic row ID for uniqueness inside file
        norm(row.get("_row_id")),
    ]

    key = "|".join(key_fields)
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def jane_sessions_ingest(uploaded_file):
    """
    Ingest Jane 'Sessions by Staff Member' CSV file.
    """

    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        print(f"❌ Error reading Jane Sessions file: {e}")
        return 0, 0

    jane_df = df.copy()

    # Normalize column names
    jane_df = normalize_columns(jane_df)

    # Drop columns not needed for merging
    jane_df.drop(columns=['location', 'patient_guid', 'patient',
                 'payer', 'income_category', 'details'], inplace=True)

    # Convert dates
    jane_df["purchase_date"] = pd.to_datetime(
        jane_df["purchase_date"], errors="coerce").dt.date
    jane_df["invoice_date"] = pd.to_datetime(
        jane_df["invoice_date"], errors="coerce").dt.date

    # Drop empty rows
    jane_df = jane_df.dropna(how="all").reset_index(drop=True)

    # Convert numeric columns
    numeric_cols = auto_numeric_columns(jane_df)
    jane_df[numeric_cols] = jane_df[numeric_cols].apply(
        pd.to_numeric, errors="coerce")

    # Drop Last Name
    jane_df["staff_member"] = jane_df.apply(
        lambda row: build_staff_short_name(full_name=row["staff_member"]),
        axis=1
    )

    # Add initials column
    jane_df["employee_initials"] = jane_df["staff_member"].apply(
        to_initials)

    # Add synthetic row ID
    jane_df["_row_id"] = jane_df.index

    # Generate hash keys
    jane_df["hash_key"] = jane_df.apply(make_jane_sessions_hash, axis=1)

    # Load into DB
    inserted, skipped = load_jane_sessions_to_db(jane_df)

    return inserted, skipped


def make_jane_processed_claim_hash(row):
    """
    Stable hash for Jane Processed Claims rows.
    Identical rows inside the same file are treated as distinct.
    Identical rows across uploads are deduped.
    """

    def norm(v):
        if v is None or pd.isna(v):
            return ""
        v = str(v).strip().lower()
        v = v.replace("\xa0", " ")
        v = " ".join(v.split())
        return v

    key_fields = [
        norm(row.get("payment_date")),
        norm(row.get("payer")),
        norm(row.get("payment_method")),
        norm(row.get("reference_number")),
        norm(row.get("amount")),
        norm(row.get("processing_fee")),
        norm(row.get("amount_paid_to_clinic")),
        # synthetic row ID for uniqueness inside file
        norm(row.get("_row_id")),
    ]

    key = "|".join(key_fields)
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def jane_processed_claims_ingest(uploaded_file):
    """
    Ingest Jane Processed Claims CSV file.
    """

    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        print(f"❌ Error reading Jane Processed Claims file: {e}")
        return 0, 0

    jane_df = df.copy()

    # Normalize column names
    jane_df = normalize_columns(jane_df)

    # --- Step 2: Normalize applied_to column ---
    jane_df['applied_to'] = jane_df['applied_to'].fillna('')

    jane_df['applied_to'] = jane_df['applied_to'].apply(
        lambda x: [item.strip() for item in str(x).split(',') if item.strip()]
    )

    # ---------------------------------------------------------
    # Step 1: Normalize payer based on patient_guid
    # ---------------------------------------------------------
    if 'patient_guid' in jane_df.columns:
        jane_df.loc[
            jane_df['patient_guid'].notna(),
            'payer'
        ] = jane_df['payment_method']
    else:
        raise ValueError("Column 'patient_guid' not found in Jane report CSV")

    # Normalize payer names
    jane_df = replace_entries(
        jane_df, 'payer', 'payer',
        "Texas Children's Health Plan - CHIP",
        "Texas Children's Health Plan"
    )

    # Normalize payment_method names
    jane_df = replace_entries(
        jane_df, 'payment_method', 'payment_method',
        'Insurer Cheque', 'TCHP'
    )

    # Convert payment_date to datetime.date
    jane_df["payment_date"] = pd.to_datetime(
        jane_df["payment_date"],
        format="%B %d %Y, %I:%M %p",
        errors="coerce"
    ).dt.date

    # Normalize Jane Payments naming
    jane_df = replace_with_regex(
        jane_df, 'payment_method', r'^Jane Payments.*', 'Jane Payments'
    )

    jane_df = replace_with_regex(
        jane_df, 'payer', r'^Jane Payments.*', 'Jane Payments'
    )

    # Drop patient_guid now that payer is normalized
    jane_df.drop(columns=['patient_guid'], inplace=True)

    # Drop empty rows
    jane_df = jane_df.dropna(how="all").reset_index(drop=True)

    # Convert numeric columns
    numeric_cols = auto_numeric_columns(jane_df)
    jane_df[numeric_cols] = jane_df[numeric_cols].apply(
        pd.to_numeric, errors="coerce")

    # ---------------------------------------------------------
    # Step 2: Count number of claims per transaction
    # ---------------------------------------------------------
    jane_df["claim_count"] = jane_df["applied_to"].apply(
        count_claims)

    # Add synthetic row ID
    jane_df["_row_id"] = jane_df.index

    # Generate hash keys
    jane_df["hash_key"] = jane_df.apply(make_jane_processed_claim_hash, axis=1)

    # Load into DB
    inserted, skipped = load_jane_processed_claims_to_db(jane_df)

    return inserted, skipped
