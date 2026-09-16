# gusto.py

from io import StringIO
import csv
import pandas as pd

# DB loader for Gusto payroll
from clinic_dash_pro.helper.helper import (
    auto_numeric_columns,
    generate_hash,
    to_initials,
    normalize_name,
    build_staff_short_name
)
from clinic_dash_pro.ingestion.database import load_gusto_to_db


# ---------------------------------------------------------
# Helper: Parse a single Gusto payroll table line
# ---------------------------------------------------------
def parse_table_line(line):
    """
    Robust CSV parser that respects quoted fields.
    Handles commas inside quotes (e.g., addresses).
    Uses Python's built-in CSV reader for correctness.
    """
    reader = csv.reader(StringIO(line), skipinitialspace=True)
    return next(reader)


# ---------------------------------------------------------
# Main Gusto Payroll Ingestion Function
# ---------------------------------------------------------
def gusto_payroll(uploaded_file):
    """
    Ingests a raw Gusto payroll CSV file uploaded via Django.

    Steps:
    1. Read uploaded CSV file into memory.
    2. Identify payroll period blocks.
    3. Extract each payroll table.
    4. Combine into a single DataFrame.
    5. Clean, normalize, convert numeric/date fields.
    6. Generate hash_key for deduplication.
    7. Load into database.
    8. Return (inserted_count, skipped_count).
    """

    # ---------------------------------------------------------
    # Step 1: Read file directly from Django InMemoryUploadedFile
    # ---------------------------------------------------------
    try:
        raw_text = uploaded_file.read().decode("utf-8")
        lines = raw_text.splitlines()
    except Exception as e:
        print(f"❌ Error reading uploaded Gusto file: {e}")
        return

    # ---------------------------------------------------------
    # Step 2: Identify payroll period blocks
    # ---------------------------------------------------------
    period_indices = []
    for i, line in enumerate(lines):
        if "Payroll period" in line:
            period_indices.append(i)

    if not period_indices:
        print("⚠️ No payroll periods found in Gusto report — skipping.")
        return

    # Add final line index to close last block
    period_indices.append(len(lines))

    tables = []  # will store each payroll period table

    # ---------------------------------------------------------
    # Step 3: Extract each payroll table block
    # ---------------------------------------------------------
    for idx in range(len(period_indices) - 1):
        start = period_indices[idx]
        end = period_indices[idx + 1]

        block = lines[start:end]

        # Find header line (contains "Last Name" and "First Name")
        header_line_index = None
        for j, line in enumerate(block):
            if "Last Name" in line and "First Name" in line:
                header_line_index = j
                break

        if header_line_index is None:
            continue

        # Extract table lines until a blank line
        table_lines = []
        for line in block[header_line_index:]:
            if line.strip() == "":
                break
            table_lines.append(line)

        # Parse header row
        header = parse_table_line(table_lines[0])
        header = [h.replace('"', '').strip() for h in header]

        # Extract payroll period from first line of block
        payroll_period_raw = block[0].strip().replace('"', '')
        payroll_period_clean = payroll_period_raw.replace(
            "Payroll period,", "").strip()

        # Add payroll period as a new column
        header.append("Payroll Period")

        # Parse all rows
        rows = []
        for line in table_lines[1:]:
            parsed = parse_table_line(line)
            parsed = [p.replace('"', '').strip() for p in parsed]

            if len(parsed) == len(header) - 1:
                parsed.append(payroll_period_clean)
                rows.append(parsed)

        # Build DataFrame for this payroll period
        df = pd.DataFrame(rows, columns=header)

        # Drop address column (not needed)
        df = df.drop(columns="Work Address")

        tables.append(df)

    # ---------------------------------------------------------
    # Step 4: Combine all payroll periods into one DataFrame
    # ---------------------------------------------------------
    payroll_df = pd.concat(tables, ignore_index=True)

    # Remove "Payroll Totals" rows
    payroll_df = payroll_df[~payroll_df["Last Name"].str.contains(
        "Payroll Totals", na=False)]

    # ---------------------------------------------------------
    # Step 4a: Build short staff member name (First + Last Initial)
    # ---------------------------------------------------------
    payroll_df["Staff Member"] = payroll_df.apply(
        lambda row: build_staff_short_name(
            row["First Name"], row["Last Name"]),
        axis=1
    )

    # Drop name columns now that Staff Member is created
    payroll_df = payroll_df.drop(columns=["First Name", "Last Name"])

    # Reorder columns: Staff Member, Payroll Period, then everything else
    cols = ["Staff Member", "Payroll Period"] + [
        c for c in payroll_df.columns if c not in ["Staff Member", "Payroll Period"]
    ]
    payroll_df = payroll_df[cols]

    # ---------------------------------------------------------
    # Step 4b: Split payroll period into start and end dates
    # ---------------------------------------------------------
    payroll_df['Payroll Period Start'] = payroll_df['Payroll Period'].apply(
        lambda x: x.split('-')[0])
    payroll_df['Payroll Period End'] = payroll_df['Payroll Period'].apply(
        lambda x: x.split('-')[1])

    # Convert numeric columns
    numeric_cols = auto_numeric_columns(payroll_df)
    payroll_df[numeric_cols] = payroll_df[numeric_cols].apply(
        pd.to_numeric, errors="coerce"
    )

    # Convert payroll period dates to datetime.date
    payroll_df["Payroll Period Start"] = pd.to_datetime(
        payroll_df["Payroll Period Start"], errors="coerce"
    ).dt.date

    payroll_df["Payroll Period End"] = pd.to_datetime(
        payroll_df["Payroll Period End"], errors="coerce"
    ).dt.date

    payroll_df = payroll_df.reset_index(drop=True)

    # ---------------------------------------------------------
    # Step 5: Clean DataFrame before hashing
    # ---------------------------------------------------------
    payroll_df = payroll_df.replace("", None)
    payroll_df = payroll_df.replace(" ", None)
    payroll_df = payroll_df.replace("nan", None)
    payroll_df = payroll_df.replace("NaN", None)

    # Add initials column
    payroll_df["employee_initials"] = payroll_df["Staff Member"].apply(
        to_initials)

    # ---------------------------------------------------------
    # Step 5b: Generate hash_key for deduplication
    # ---------------------------------------------------------
    KEY_COLUMNS = [
        "Staff Member",
        "Payroll Period",
        "Department"
    ]

    payroll_df["hash_key"] = payroll_df.apply(
        lambda row: generate_hash(row.to_dict(), KEY_COLUMNS), axis=1)

    # ---------------------------------------------------------
    # Step 6: Load cleaned payroll into DB
    # ---------------------------------------------------------
    inserted, skipped = load_gusto_to_db(payroll_df)

    # Return counts to Django view
    return inserted, skipped


# Allow running this file directly
if __name__ == "__main__":
    gusto_payroll()
