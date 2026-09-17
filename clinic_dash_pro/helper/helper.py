# helper.py

from datetime import date, timedelta
import math
from dateutil import parser
from datetime import datetime
from rapidfuzz import process, fuzz
import re
import os
import pandas as pd
from openpyxl.styles import Alignment
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import hashlib

# Load credentials list from environment variable
# Used to strip credentials (CCC-SLP, MS, etc.) from therapist names
raw = os.getenv("CREDENTIALS", "")
CREDENTIALS = [c.strip().lower() for c in raw.split(",") if c.strip()]


# ---------------------------------------------------------
# 1. Date parsing utilities
# ---------------------------------------------------------
def try_parse_date(x):
    """
    Safely parse a date string into a Python date.
    Returns original value if:
    - not a string
    - contains letters (payer names, descriptions)
    - contains ranges ("12/22/2025 - 01/04/2026")
    - contains fewer than 6 digits (not a real date)
    """
    if not isinstance(x, str):
        return x

    s = x.strip()

    # Reject strings containing letters
    if any(c.isalpha() for c in s):
        return x

    # Reject date ranges
    if " - " in s or " to " in s or "–" in s:
        return x

    # Must contain at least 6 digits
    digits = sum(c.isdigit() for c in s)
    if digits < 6:
        return x

    # Try parsing safely
    try:
        return parser.parse(s).date()
    except Exception:
        return x


# ---------------------------------------------------------
# 2. DataFrame sanitization
# ---------------------------------------------------------
def sanitize_df(df):
    """
    Normalize column names, remove duplicate columns,
    convert NaN → None, convert timestamps → Python dates,
    and parse valid date strings.
    """

    # Normalize column names
    df.columns = (
        df.columns
        .str.strip()
        .str.replace("\xa0", " ", regex=False)
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("#", "")
        .str.replace("(", "_")
        .str.replace(")", "")
        .str.replace("-", "_")
        .str.replace("/", "_")
        .str.replace(".", "")
        .str.replace("__", "_")
        .str.rstrip("_")
    )

    # Remove duplicate columns
    df = df.loc[:, ~df.columns.duplicated()]

    # Convert NaN → None
    df = df.where(pd.notnull(df), None)

    # Convert Timestamp → Python date
    for col in df.columns:
        df[col] = df[col].apply(
            lambda x: x.date() if isinstance(x, pd.Timestamp) else x
        )

    # Convert valid date strings → Python date
    for col in df.columns:
        df[col] = df[col].apply(try_parse_date)

    return df


# ---------------------------------------------------------
# 3. Excel export utility
# ---------------------------------------------------------
def export_df_to_excel(df, filename="jane_transactions_merged.xlsx", output_dir='output', tableName='Data', padding=5):
    """
    Export a DataFrame to Excel with:
    - auto-sized columns
    - table formatting
    - alignment
    """

    # Convert Period columns to strings
    for col in df.columns:
        if isinstance(df[col].dtype, pd.PeriodDtype):
            df[col] = df[col].astype(str)

    wb = Workbook()
    ws = wb.active
    ws.title = "Merged Transactions"

    # Write DataFrame rows
    for r in dataframe_to_rows(df, index=False, header=True):
        ws.append(r)

    # Create Excel table
    last_row = ws.max_row
    last_col = ws.max_column
    table_ref = f"A1:{ws.cell(row=last_row, column=last_col).coordinate}"
    table = Table(displayName=tableName, ref=table_ref)

    # Table style
    style = TableStyleInfo(
        name="TableStyleNone",
        showFirstColumn=False,
        showLastColumn=False,
        showRowStripes=True,
        showColumnStripes=False
    )
    table.tableStyleInfo = style
    ws.add_table(table)

    # Auto-size columns
    for col in ws.columns:
        max_length = 0
        col_letter = col[0].column_letter

        for cell in col:
            try:
                cell_value = str(cell.value)
                max_length = max(max_length, len(cell_value))
            except:
                pass

        ws.column_dimensions[col_letter].width = max_length + padding

    # Alignment
    for row in ws.iter_rows():
        for cell in row:
            cell.alignment = Alignment(vertical="center", wrap_text=False)

    # Save file
    wb.save(os.path.join(output_dir, filename))
    print("\n==============================")
    print(f"Excel file created: {filename}.\n")


# ---------------------------------------------------------
# 4. Column normalization
# ---------------------------------------------------------
def normalize_columns(df):
    """
    Normalize column names consistently across all ingestion modules.
    """
    df.columns = (
        df.columns
        .str.strip()
        .str.replace("\xa0", " ", regex=False)
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("#", "")
        .str.replace("(", "_")
        .str.replace(")", "")
        .str.replace("-", "_")
        .str.replace("/", "_")
        .str.replace(".", "")
        .str.replace("__", "_")
        .str.replace("___", "_")
        .str.rstrip("_")
    )
    return df


# ---------------------------------------------------------
# 5. Timestamp conversion
# ---------------------------------------------------------
def convert_timestamps(df):
    """
    Convert datetime64 columns → Python date.
    """
    for col in df.columns:
        if df[col].dtype == "datetime64[ns]":
            df[col] = df[col].dt.date
    return df


# ---------------------------------------------------------
# 6. Name normalization
# ---------------------------------------------------------
def normalize_name(name):
    """
    Normalize therapist names by:
    - lowercasing
    - removing punctuation
    - removing credentials
    - removing middle initials
    - collapsing spaces
    - converting to Title Case
    """
    if not isinstance(name, str):
        return ""

    name = name.lower().strip()
    name = re.sub(r"[.,\-_/]", " ", name)

    # Remove credentials (CCC-SLP, MS, etc.)
    for cred in CREDENTIALS:
        name = name.replace(cred, " ")

    # Remove middle initials
    name = re.sub(r"\b[a-z]\b", " ", name)

    name = " ".join(name.split())
    name = name.title()

    return name


# ---------------------------------------------------------
# 7. Fuzzy name matching
# ---------------------------------------------------------
def fuzzy_match_name(name, choices):
    """
    Fuzzy match a name against a list of choices.
    Returns match only if score >= 90.
    """
    match, score, _ = process.extractOne(name, choices, scorer=fuzz.WRatio)
    return match if score >= 90 else None


# ---------------------------------------------------------
# 8. Map Jane appointment → Gusto payroll period
# ---------------------------------------------------------
def find_payroll_period(date, payroll_df):
    """
    Given a Jane appointment date, find the matching Gusto payroll period.
    """
    if pd.isna(date):
        return None

    # Normalize Jane date
    if hasattr(date, "date"):
        date = date.date()

    for _, row in payroll_df.iterrows():
        start = row["payroll_period_start"]
        end = row["payroll_period_end"]

        # Normalize Gusto dates
        if hasattr(start, "date"):
            start = start.date()
        if hasattr(end, "date"):
            end = end.date()

        if start <= date <= end:
            return row["payroll_period"]

    return None


# ---------------------------------------------------------
# 9. CSV ingestion utilities
# ---------------------------------------------------------
def load_csv_to_dataframe(path):
    """
    Safely load a CSV file.
    - If file exists: load it and return DataFrame.
    - Do NOT delete the file.
    """
    if not os.path.exists(path):
        print(f"⚠️ File not found, skipping: {path}")
        return None

    try:
        df = pd.read_csv(path)
        print(f"📄 Loaded file: {path}")
        return df

    except Exception as e:
        print(f"❌ Error loading file {path}: {e}")
        return None


def load_and_delete_gusto_csv(path, skiprows=0):
    """
    Load a Gusto CSV file with optional skiprows.
    Delete file after ingestion.
    """
    if not os.path.exists(path):
        print(f"⚠️ Gusto file not found — skipping: {path}")
        return None

    try:
        df = pd.read_csv(path, skiprows=skiprows)
        print(f"📄 Loaded Gusto file: {path}")

        os.remove(path)
        print(f"🗑️ Deleted Gusto file after ingestion: {path}")

        return df

    except Exception as e:
        print(f"❌ Error loading Gusto file {path}: {e}")
        return None


# ---------------------------------------------------------
# 10. Safe division
# ---------------------------------------------------------
def safe_div(numerator, denominator):
    """
    Safe division:
    - returns 0 if denominator is None or zero
    """
    if denominator is None or denominator == 0:
        return 0
    return numerator / denominator


# ---------------------------------------------------------
# 11. Profitability metrics
# ---------------------------------------------------------
def add_profitability_metrics(merged):
    """
    Add profitability metrics to merged Gusto+Jane dataset:
    - revenue_per_hour
    - cost_per_hour
    - profit
    - profit_margin
    """

    merged["revenue_per_hour"] = merged.apply(
        lambda row: round(safe_div(row["revenue"], row["regular_hours"]), 2),
        axis=1,
    )

    merged["cost_per_hour"] = merged.apply(
        lambda row: round(
            safe_div(row["employer_cost"], row["regular_hours"]), 2),
        axis=1,
    )

    merged["profit"] = merged["revenue"] - merged["employer_cost"]

    merged["profit_margin"] = merged.apply(
        lambda row: round(safe_div(row["profit"], row["revenue"]), 3),
        axis=1,
    )

    return merged


def map_staff_names(gusto_df, jane_df):
    """
    Normalize therapist names and fuzzy-match Jane staff to Gusto staff.
    Adds diagnostics to detect:
        - therapists missing in Gusto
        - therapists missing in Jane
        - fuzzy-match collisions
        - fuzzy-match failures
        - ambiguous matches
        - normalization anomalies

    Returns:
        gusto_df, jane_df
    """

    issues = []

    # -----------------------------------------------------
    # Normalize names in both datasets
    # -----------------------------------------------------
    jane_df["staff_member_clean"] = jane_df["staff_member"].fillna(
        "N/A").apply(normalize_name)
    jane_df["employee_initials"] = jane_df["staff_member_clean"].apply(
        to_initials)

    gusto_df["staff_member_clean"] = gusto_df["staff_member"].apply(
        normalize_name)
    gusto_df["employee_initials"] = gusto_df["staff_member_clean"].apply(
        to_initials)

    unique_gusto = gusto_df["staff_member_clean"].unique()

    # -----------------------------------------------------
    # Admin Staff / Non Therapist
    # -----------------------------------------------------

    staff_department = gusto_df[[
        'staff_member_clean', 'employee_initials', 'department']].drop_duplicates()
    non_therapy_staff = staff_department[staff_department['department'] != 'Therapy']

    # -----------------------------------------------------
    # Fuzzy match Jane → Gusto
    # -----------------------------------------------------
    def match_name(n):
        match = fuzzy_match_name(n, unique_gusto)
        return match if match else n

    jane_df["matched_name"] = jane_df["staff_member_clean"].apply(match_name)

    # -----------------------------------------------------
    # DIAGNOSTICS
    # -----------------------------------------------------

    # Build sets
    jane_names = set(jane_df["staff_member_clean"])
    gusto_names = set(unique_gusto)

    # Identify non-therapy staff (admin, office, billing, etc.)
    staff_department = gusto_df[[
        'staff_member_clean', 'department']].drop_duplicates()
    non_therapy_staff = set(
        staff_department[staff_department['department']
                         != 'Therapy']['staff_member_clean']
    )

    # 1. Employees missing in Gusto (but ignore admin staff)
    missing_in_gusto = jane_names - gusto_names
    missing_in_gusto = missing_in_gusto - non_therapy_staff  # remove admin staff

    if missing_in_gusto:
        issues.append(
            f"Employees present in Jane but missing in Gusto (excluding admin staff): {missing_in_gusto}"
        )

    # 2. Employees missing in Jane (but ignore admin staff)
    missing_in_jane = gusto_names - jane_names
    missing_in_jane = missing_in_jane - non_therapy_staff  # remove admin staff

    if missing_in_jane:
        issues.append(
            f"Employees present in Gusto but missing in Jane (excluding admin staff): {missing_in_jane}"
        )

    # 3. Fuzzy-match failures (matched_name == original)
    failed_matches = jane_df[
        (jane_df["staff_member_clean"] != "N/A") &
        (jane_df["matched_name"] == jane_df["staff_member_clean"]) &
        (~jane_df["staff_member_clean"].isin(gusto_names))
    ]["staff_member_clean"].unique()

    if len(failed_matches) > 0:
        issues.append(
            f"Fuzzy-match failures (no close match found): {failed_matches}")

    # 4. Fuzzy-match collisions (multiple Jane names → same Gusto name)
    collision_df = (
        jane_df.groupby("matched_name")["staff_member_clean"]
        .nunique()
        .reset_index()
    )
    collisions = collision_df[collision_df["staff_member_clean"] > 1]

    if not collisions.empty:
        issues.append(
            "Fuzzy-match collisions detected (multiple Jane names mapped to same Gusto name):")
        issues.append(collisions.to_string(index=False))

    # 5. Ambiguous matches (low fuzzy score)
    ambiguous = []
    for n in jane_names:
        match, score, _ = process.extractOne(
            n, unique_gusto, scorer=fuzz.WRatio)
        if score < 90:
            ambiguous.append((n, match, score))

    if ambiguous:
        issues.append("Ambiguous fuzzy matches (score < 90):")
        for n, m, s in ambiguous:
            issues.append(f"  {n} → {m} (score={s})")

    # -----------------------------------------------------
    # Apply final matched names
    # -----------------------------------------------------
    jane_df["staff_member_clean"] = jane_df["matched_name"]
    jane_df.drop(columns=["matched_name"], inplace=True)

    # -----------------------------------------------------
    # Print diagnostics
    # -----------------------------------------------------
    print("\n==============================")
    print(" STAFF NAME MAPPING VALIDATION")
    print("==============================")
    if issues:
        for issue in issues:
            print("⚠️", issue)
    else:
        print("✅ All employees names mapped cleanly with no issues.")
    print("==============================\n")

    return gusto_df, jane_df, non_therapy_staff


# ---------------------------------------------------------
# 16. Export merged Gusto+Jane dataset
# ---------------------------------------------------------
def export_merged(merged):
    """
    Export merged Gusto+Jane dataset to Excel.
    Filename includes payroll period range.
    """

    min_date = str(merged["payroll_period_start"].min()).replace("-", "")
    max_date = str(merged["payroll_period_end"].max()).replace("-", "")
    output_filename = f"gusto_jane_merged_{min_date}_{max_date}.xlsx"

    export_df_to_excel(
        merged,
        filename=output_filename,
        output_dir="output",
        tableName="GustoJane",
    )

    print("Gusto & Jane merged:\n", merged.drop(
        columns=['id', 'insert_date']).reset_index(drop=True))


# ---------------------------------------------------------
# 17. Merge Xero + Jane + Gusto into unified financial dataset
# ---------------------------------------------------------
def merge_xero_with_jane_gusto(xero_df, jane_df, gusto_df):
    """
    Build unified financial dataset:
    - Jane revenue (bank deposits)
    - Gusto payroll (accrual)
    - Xero operational expenses
    """

    records = []

    # 1. Jane revenue (bank deposits)
    jane_grouped = jane_df.groupby("payment_date")["actual_collected"].sum()

    for date, amt in jane_grouped.items():
        records.append({
            "date": date,
            "category": "Revenue",
            "subcategory": "Jane Payout",
            "source": "Jane",
            "amount": amt,
            "staff_member": None,
            "notes": "Jane payout (actual_collected)"
        })

    # 2. Gusto payroll (accrual)
    for _, row in gusto_df.iterrows():
        records.append({
            "date": row["payroll_period_end"],
            "category": "Payroll",
            "subcategory": "Employer Cost",
            "source": "Gusto",
            "amount": -abs(row["employer_cost"]),
            "staff_member": None,
            "notes": f"Gusto payroll for period ending {row['payroll_period_end']}"
        })

    # 3. Xero operational expenses
    for _, row in xero_df.iterrows():

        # Skip bank accounts
        if is_bank_account(row["related_account"]):
            continue

        category = classify_xero_category(row)

        if category not in ["Asset", "Expense", "Other Income"]:
            continue

        records.append({
            "date": row["date"],
            "category": category,
            "subcategory": row["related_account"],
            "source": "Xero",
            "amount": row["gross"],
            "staff_member": None,
            "notes": row["description"]
        })

    df_financials = pd.DataFrame(records)
    df_financials["date"] = pd.to_datetime(
        df_financials["date"], errors="coerce")
    df_financials.sort_values("date", inplace=True)
    df_financials.reset_index(drop=True, inplace=True)

    return df_financials


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


# ---------------------------------------------------------
# 19. Detect bank accounts in Xero
# ---------------------------------------------------------
def is_bank_account(related_account: str) -> bool:
    """
    Determine if a Xero related_account is a bank account.

    Logic:
    - Numeric prefix 1000–1099 → bank account
    - Named accounts containing keywords → bank account
    """

    acct = str(related_account).strip()
    prefix = acct.split(" ")[0]

    if prefix.isdigit():
        acct_num = int(prefix)

        if 1000 <= acct_num <= 1099:
            return True

        return False

    lower = acct.lower()
    bank_keywords = ["checking", "savings", "bank", "cash", "account"]

    if any(word in lower for word in bank_keywords):
        return True

    return False


# ---------------------------------------------------------
# 20. Debugging utility
# ---------------------------------------------------------
def trace_rows(df, columns=None, label="TRACE"):
    """
    Print selected columns or the full DataFrame for debugging.

    Parameters:
        df (pd.DataFrame): The DataFrame to inspect.
        columns (list[str] or None): If provided, only these columns
                                     will be printed. If None, the
                                     entire DataFrame is printed.
        label (str): A header label to visually separate debug output.

    This function is used throughout the pipeline to inspect:
        - raw Gusto payroll rows
        - raw Jane rows
        - raw Xero rows
        - intermediate monthly payroll
        - operational totals
        - real profit breakdown

    It prints without index to keep output clean and readable.
    """
    print(f"\n========== {label} ==========")

    # If specific columns were requested, print only those
    if columns:
        print(df[columns].to_string(index=False))

    # Otherwise print the entire DataFrame
    else:
        print(df.to_string(index=False))

    print("================================\n")


def get_data_range(df, column):
    start_date = df[column].min()
    end_date = df[column].max()

    return start_date, end_date


# ---------------------------------------------------------
# 3. Convert full name → initials
# ---------------------------------------------------------
def to_initials(name: str) -> str:
    """
    Convert full therapist name into initials.
    Example: 'Karen Rocha Garcia' → 'K.R.G'
    """
    if not isinstance(name, str):
        return name

    parts = [p.strip() for p in name.split() if p.strip()]
    initials = ".".join([p[0].upper() for p in parts])
    return initials


def ty_ly_py(df, column):
    """
    Classify each row based on the year difference between df[column] and today:
        TY = This Year
        LY = Last Year
        PY = Prior Year (2 years ago)
        OY = Older Year (3+ years ago)

    Supports:
        - datetime64 columns
        - period dtype columns (e.g., period[Y-DEC])
    """

    current_year = datetime.now().year

    col = df[column]

    # ---------------------------------------------------------
    # Handle Period dtype (e.g., period[Y-DEC])
    # ---------------------------------------------------------
    if isinstance(col.dtype, pd.PeriodDtype):
        df["year_diff"] = current_year - col.dt.year

    # ---------------------------------------------------------
    # Handle datetime dtype
    # ---------------------------------------------------------
    elif pd.api.types.is_datetime64_any_dtype(col):
        df["year_diff"] = current_year - col.dt.year

    # ---------------------------------------------------------
    # Handle object/string dates
    # ---------------------------------------------------------
    else:
        # Convert to datetime safely
        col_dt = pd.to_datetime(col, errors="coerce")
        df["year_diff"] = current_year - col_dt.dt.year

    # ---------------------------------------------------------
    # Classification
    # ---------------------------------------------------------
    def classify(diff):
        if pd.isna(diff):
            return "OY"
        if diff == 0:
            return "TY"
        if diff == 1:
            return "LY"
        if diff == 2:
            return "PY"
        return "OY"

    df["ty_ly_py"] = df["year_diff"].apply(classify)

    df.drop(columns=["year_diff"], inplace=True)

    return df


def get_periods():
    """
    Returns:
        - current_month: Period[M]
        - latest_closed_month: Period[M]
        - current_year: Period[Y]
        - latest_closed_year: Period[Y]
    """

    today = pd.Timestamp.today()   # <-- FIX: use pandas Timestamp

    # Current month
    current_month = today.to_period("M")

    # Latest closed month (previous month)
    latest_closed_month = (today.replace(
        day=1) - pd.Timedelta(days=1)).to_period("M")

    # Current year
    current_year = today.to_period("Y")

    # Latest closed year (previous year)
    latest_closed_year = (today.to_period("Y") - 1)

    return {
        "current_month": current_month,
        "latest_closed_month": latest_closed_month,
        "current_year": current_year,
        "latest_closed_year": latest_closed_year,
    }


def auto_numeric_columns(df):
    """
    Automatically detect numeric columns by attempting conversion.
    Returns a list of columns that can be safely converted to numeric.
    """

    numeric_cols = []

    for col in df.columns:
        # Try converting the column to numeric
        converted = pd.to_numeric(df[col], errors="coerce")

        # If at least 50% of values convert successfully, treat as numeric
        success_rate = converted.notna().mean()

        if success_rate >= 0.5:
            numeric_cols.append(col)

    return numeric_cols


def safe_value(v):
    """Convert any value to a safe string for hashing."""
    if v is None:
        return ""
    if isinstance(v, float) and math.isnan(v):
        return ""
    return str(v).strip()


def generate_hash(row, KEY_COLUMNS):
    raw = "|".join(str(row[col]).strip() for col in KEY_COLUMNS)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


# ---------------------------------------------------------
# 3. Convert full name → initials
# ---------------------------------------------------------
def to_initials(name: str) -> str:
    """
    Convert full therapist name into initials.
    Example: 'Karen Rocha Garcia' → 'K.R.G'
    """
    if not isinstance(name, str):
        return name

    parts = [p.strip() for p in name.split() if p.strip()]
    initials = ".".join([p[0].upper() for p in parts])
    return initials


def normalize_name(name):
    """
    Normalize therapist names by:
    - lowercasing
    - removing punctuation
    - removing credentials
    - removing middle initials
    - collapsing spaces
    - converting to Title Case
    """
    if not isinstance(name, str):
        return ""

    name = name.lower().strip()
    name = re.sub(r"[.,\-_/]", " ", name)

    # Remove credentials (CCC-SLP, MS, etc.)
    CREDENTIALS = [
        "rmt", "slp", "ccc-slp", "ccc slp", "cccslp",
        "ms", "m.s.", "m.s", "pt", "ot", "lmt", "lmft",
        "lpc", "ba"
    ]

    for cred in CREDENTIALS:
        name = name.replace(cred, " ")

    # Remove middle initials (single letters)
    name = re.sub(r"\b[a-z]\b", " ", name)

    # Collapse multiple spaces
    name = " ".join(name.split())

    # Convert to Title Case
    name = name.title()

    return name


def get_last_initial(last_name):
    if not isinstance(last_name, str) or last_name.strip() == "":
        return ""
    return last_name.strip()[0].upper()


def build_staff_short_name(first=None, last=None, full_name=None):
    """
    Builds a short staff name in the format:
        First L
    Works whether the caller provides:
        - first + last
        - full_name only
    """

    def clean(s):
        if not s:
            return ""
        return str(s).strip().title()

    def get_last_initial(name):
        if not name:
            return ""
        name = name.strip()
        return name[0].upper()

    # If full_name is provided, split it
    if full_name:
        full_name = clean(full_name)

        parts = full_name.split()

        if len(parts) == 1:
            # Only one name provided → treat as first name only
            first = parts[0]
            last = ""
        else:
            first = parts[0]
            last = parts[-1]  # last token is last name (handles middle names)

    # If first/last provided directly
    first = clean(first)
    last_initial = get_last_initial(last)

    return f"{first} {last_initial}".strip()


def is_stale(latest_date, days=15):
    if not latest_date:
        return True
    return latest_date < (date.today() - timedelta(days=days))
