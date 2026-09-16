# database.py

from clinic_dash_pro.models import JaneProcessedClaim
from clinic_dash_pro.models import GustoPayroll, XeroTransaction, JaneStaffSale, JaneProcessedClaim


def load_gusto_to_db(gusto_df):
    """
    Load cleaned Gusto payroll rows into the database.

    This function:
    - Iterates through each row in the cleaned DataFrame.
    - Converts the row into a dictionary.
    - Performs deduplication using the hash_key column.
    - Inserts new rows into the GustoPayroll model.
    - Tracks how many rows were inserted vs skipped.
    - Prints a load report.
    - Returns (inserted_count, skipped_count) to the caller.

    Parameters
    ----------
    gusto_df : pandas.DataFrame
        Cleaned payroll data with normalized fields and a hash_key column.

    Returns
    -------
    tuple
        (inserted, skipped)
        inserted : int — number of new rows added to the database
        skipped  : int — number of duplicate rows ignored
    """

    inserted = 0
    skipped = 0

    # Iterate through each row in the DataFrame
    for idx, row in gusto_df.iterrows():
        row_dict = row.to_dict()

        # ---------------------------------------------------------
        # Deduplication: skip rows whose hash_key already exists
        # ---------------------------------------------------------
        exists = GustoPayroll.objects.filter(
            hash_key=row_dict["hash_key"]
        ).exists()

        if exists:
            skipped += 1
            continue

        # ---------------------------------------------------------
        # Insert new payroll row
        # ---------------------------------------------------------
        GustoPayroll.objects.create(
            staff_member=row_dict.get("Staff Member"),
            employee_initials=row_dict.get("employee_initials"),

            payroll_period=row_dict.get("Payroll Period"),
            department=row_dict.get("Department"),

            regular_hours=row_dict.get("Regular Hours"),
            regular_amount=row_dict.get("Regular Amount"),
            regular_rate=row_dict.get("Regular Rate"),

            time_off_hours=row_dict.get("Time Off Hours"),
            time_off_amount=row_dict.get("Time Off Amount"),
            time_off_rate=row_dict.get("Time Off Rate"),

            additional_earnings=row_dict.get("Additional Earnings"),
            gross_earnings=row_dict.get("Gross Earnings"),

            employee_taxes=row_dict.get("Employee Taxes"),
            federal_income_tax_employee=row_dict.get(
                "Federal Income Tax Employee"),
            social_security_employee=row_dict.get("Social Security Employee"),
            medicare_employee=row_dict.get("Medicare Employee"),
            additional_medicare_employee=row_dict.get(
                "Additional Medicare Employee"),

            employer_taxes=row_dict.get("Employer Taxes"),
            social_security_employer=row_dict.get("Social Security Employer"),
            medicare_employer=row_dict.get("Medicare Employer"),
            tx_suta_employer=row_dict.get("TX SUTA Employer"),
            futa_employer=row_dict.get("FUTA Employer"),

            net_pay=row_dict.get("Net Pay"),
            reimbursements=row_dict.get("Reimbursements"),
            donations=row_dict.get("Donations"),
            check_amount=row_dict.get("Check Amount"),

            employer_cost=row_dict.get("Employer Cost"),

            employee_type=row_dict.get("Employee Type"),
            payment=row_dict.get("Payment"),

            payroll_period_start=row_dict.get("Payroll Period Start"),
            payroll_period_end=row_dict.get("Payroll Period End"),

            hash_key=row_dict.get("hash_key"),
        )

        inserted += 1

        if idx % 500 == 0:
            print(
                f"[Jane Claims] Row {idx:,} — Inserted: {inserted:,}, Skipped: {skipped:,}, Total: {len(gusto_df):,}")

    # ---------------------------------------------------------
    # Load Report
    # ---------------------------------------------------------
    print("\n=== GUSTO LOAD REPORT ===")
    print(f"Inserted new rows: {inserted}")
    print(f"Skipped duplicates: {skipped}")
    print("==========================\n")

    return inserted, skipped


def load_xero_to_db(xero_df):
    inserted = 0
    skipped = 0

    for idx, row in xero_df.iterrows():
        row_dict = row.to_dict()

        if idx % 100 == 0:
            print(
                f"[Xero] Row {idx:,} — Inserted: {inserted:,}, Skipped: {skipped:,}")

        # Deduplication
        if XeroTransaction.objects.filter(hash_key=row_dict["hash_key"]).exists():
            skipped += 1
            continue

        XeroTransaction.objects.create(
            date=row_dict.get("date"),
            account_type=row_dict.get("account_type"),
            related_account=row_dict.get("related_account"),
            contact=row_dict.get("contact"),
            description=row_dict.get("description"),
            debit=row_dict.get("debit"),
            credit=row_dict.get("credit"),
            gross=row_dict.get("gross"),
            category=row_dict.get("category"),
            hash_key=row_dict.get("hash_key"),
        )

        inserted += 1

        if idx % 500 == 0:
            print(
                f"[Jane Claims] Row {idx:,} — Inserted: {inserted:,}, Skipped: {skipped:,}, Total: {len(xero_df):,}")

    print("\n=== XERO LOAD REPORT ===")
    print(f"Inserted new rows: {inserted}")
    print(f"Skipped duplicates: {skipped}")
    print("==========================\n")

    return inserted, skipped


def load_jane_sales_to_db(jane_df):
    inserted = 0
    skipped = 0

    for idx, row in jane_df.iterrows():
        row_dict = row.to_dict()

        # Deduplication
        if JaneStaffSale.objects.filter(hash_key=row_dict["hash_key"]).exists():
            skipped += 1
            continue

        JaneStaffSale.objects.create(
            staff_member=row_dict.get("staff_member"),
            employee_initials=row_dict.get("employee_initials"),
            purchase_date=row_dict.get("purchase_date"),
            invoice_date=row_dict.get("invoice_date"),
            item=row_dict.get("item"),
            status=row_dict.get("status"),
            subtotal=row_dict.get("subtotal"),
            total=row_dict.get("total"),
            collected=row_dict.get("collected"),
            balance=row_dict.get("balance"),
            hash_key=row_dict.get("hash_key"),
        )

        inserted += 1

        if idx % 500 == 0:
            print(
                f"[Jane Staff Sales] Row {idx:,} — Inserted: {inserted:,}, Skipped: {skipped:,}, Total: {len(jane_df):,}")

    print("\n=== JANE SALES LOAD REPORT ===")
    print(f"Inserted new rows: {inserted}")
    print(f"Skipped duplicates: {skipped}")
    print("==============================\n")

    return inserted, skipped


def load_jane_processed_claims_to_db(jane_df):
    inserted = 0
    skipped = 0

    for idx, row in jane_df.iterrows():
        row_dict = row.to_dict()

        # Deduplication
        if JaneProcessedClaim.objects.filter(hash_key=row_dict["hash_key"]).exists():
            skipped += 1
            continue

        JaneProcessedClaim.objects.create(
            payment_date=row_dict.get("payment_date"),
            payer=row_dict.get("payer"),
            payment_method=row_dict.get("payment_method"),
            reference_number=row_dict.get("reference_number"),
            applied_to=row_dict.get("applied_to"),
            claim_count=row_dict.get("claim_count"),
            amount=row_dict.get("amount"),
            processing_fee=row_dict.get("processing_fee"),
            amount_paid_to_clinic=row_dict.get("amount_paid_to_clinic"),
            hash_key=row_dict.get("hash_key"),
        )

        inserted += 1

        if idx % 500 == 0:
            print(
                f"[Jane Claims] Row {idx:,} — Inserted: {inserted:,}, Skipped: {skipped:,}, Total: {len(jane_df):,}")

    print("\n=== JANE PROCESSED CLAIMS LOAD REPORT ===")
    print(f"Inserted new rows: {inserted}")
    print(f"Skipped duplicates: {skipped}")
    print("=========================================\n")

    return inserted, skipped
