# database.py

from clinic_dash_pro.models import GustoPayroll


def load_gusto_to_db(gusto_df):
    inserted = 0
    skipped = 0

    for _, row in gusto_df.iterrows():
        row_dict = row.to_dict()

        # Deduplication
        exists = GustoPayroll.objects.filter(
            hash_key=row_dict["hash_key"]).exists()

        if exists:
            skipped += 1
            continue

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

    print("\n=== GUSTO LOAD REPORT ===")
    print(f"Inserted new rows: {inserted}")
    print(f"Skipped duplicates: {skipped}")
    print("==========================\n")

    return inserted, skipped
