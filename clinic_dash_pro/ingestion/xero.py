# xero.py

import pandas as pd
import hashlib
from io import BytesIO

from clinic_dash_pro.helper.helper import (
    normalize_columns,
    auto_numeric_columns,
)
from clinic_dash_pro.ingestion.database import load_xero_to_db


def make_xero_hash(row):
    """
    Stable hash for Xero transactions.
    Identical rows inside the same file are treated as distinct.
    Identical rows across different uploads are deduped.
    """

    def norm(v):
        if v is None or pd.isna(v):
            return ""
        v = str(v).strip().lower()
        v = v.replace("\xa0", " ")
        v = " ".join(v.split())
        return v

    key_fields = [
        norm(row.get("date")),
        norm(row.get("account_type")),
        norm(row.get("related_account")),
        norm(row.get("contact")),
        norm(row.get("description")),
        norm(row.get("gross")),
        norm(row.get("_row_id")),   # synthetic unique row ID
    ]

    key = "|".join(key_fields)
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


# ---------------------------------------------------------
# 18. Xero category classification
# ---------------------------------------------------------
def classify_xero_category(row):
    """
    Classify Xero accounts by numeric prefix:
    - 1000–1999 Asset
    - 2000–2999 Liability
    - 3000–3999 Equity
    - 4000–4999 Revenue
    - 5000–5999 COGS
    - 6450, 6360 Payroll
    - 6000–6999 Expense
    - 7000–7999 Other Income
    """

    acct = str(row["related_account"]).strip()
    prefix = acct.split(" ")[0]

    if prefix.isdigit():
        acct_num = int(prefix)

        if 1000 <= acct_num <= 1999:
            return "Asset"
        if 2000 <= acct_num <= 2999:
            return "Liability"
        if 3000 <= acct_num <= 3999:
            return "Equity"
        if 4000 <= acct_num <= 4999:
            return "Revenue"
        if 5000 <= acct_num <= 5999:
            return "COGS"
        if acct_num in [6450, 6360]:
            return "Payroll"
        if 6000 <= acct_num <= 6999:
            return "Expense"
        if 7000 <= acct_num <= 7999:
            return "Other Income"

    return "Other Accounts"


def xero_ingest(uploaded_file):
    """
    Ingest a raw Xero Excel file uploaded via Django.
    """

    try:
        # Read Excel directly from Django InMemoryUploadedFile
        df = pd.read_excel(uploaded_file, skiprows=5)
    except Exception as e:
        print(f"❌ Error reading Xero file: {e}")
        return 0, 0

    xero_df = df.copy()

    # Normalize column names
    xero_df = normalize_columns(xero_df)

    # Convert date column
    xero_df["date"] = pd.to_datetime(xero_df["date"], errors="coerce").dt.date

    xero_df = xero_df[xero_df["date"].notna()]

    # Drop empty rows
    xero_df = xero_df.dropna(how="all").reset_index(drop=True)

    # Convert numeric columns
    numeric_cols = auto_numeric_columns(xero_df)
    xero_df[numeric_cols] = xero_df[numeric_cols].apply(
        pd.to_numeric, errors="coerce"
    )

    # Classify Xero categories (Revenue, Expense, Asset, Payroll, etc.)
    xero_df["category"] = xero_df.apply(classify_xero_category, axis=1)

    xero_df["_row_id"] = xero_df.index

    # Generate hash keys
    xero_df["hash_key"] = xero_df.apply(make_xero_hash, axis=1)

    # Load into DB
    inserted, skipped = load_xero_to_db(xero_df)

    return inserted, skipped
