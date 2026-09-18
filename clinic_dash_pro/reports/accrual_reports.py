# accrual_reports.py

import pandas as pd


def build_accrual_payroll(gusto_df: pd.DataFrame, jane_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build monthly accrual payroll:

    - Therapists: payroll allocated only to days they had appointments.
    - Admin: payroll allocated evenly across all days in the payroll period.

    Returns:
        DataFrame with:
            period_month
            staff_member
            payroll_accrual
    """

    # -----------------------------
    # 1. Normalize Gusto dates
    # -----------------------------
    gusto = gusto_df.copy()
    gusto["payroll_period_start"] = pd.to_datetime(
        gusto["payroll_period_start"], errors="coerce")
    gusto["payroll_period_end"] = pd.to_datetime(
        gusto["payroll_period_end"], errors="coerce")

    # -----------------------------
    # 2. Normalize Jane dates
    # -----------------------------
    jane = jane_df.copy()
    jane["purchase_date"] = pd.to_datetime(
        jane["purchase_date"], errors="coerce")

    # Assume jane_df has a column "staff_member" (therapist name)
    # and gusto_df has "staff_member" + "department" (e.g., "Therapy" / "Admin")

    # -----------------------------
    # 3. Expand payroll periods into daily rows
    # -----------------------------
    rows = []

    for idx, row in gusto.iterrows():
        staff = row["staff_member"]
        # default to Therapist if missing
        role = row.get("department", "Therapy")
        start = row["payroll_period_start"]
        end = row["payroll_period_end"]
        employer_cost = row["employer_cost"]
        payroll_period = row["payroll_period"]

        if pd.isna(start) or pd.isna(end):
            continue

        days = pd.date_range(start, end, freq="D")
        n_days = len(days)
        if n_days == 0:
            continue

        daily_cost = employer_cost / n_days

        for day in days:
            rows.append({
                "idx": idx,
                "purchase_date": day,
                "staff_member": staff,
                "role": role,
                "daily_cost_base": daily_cost,
                "payroll_period": payroll_period
            })

    daily_payroll = pd.DataFrame(rows)

    # -----------------------------
    # 4. Count therapist appointments per day
    # -----------------------------
    # Therapist work days from Jane
    therapist_days = (
        jane.groupby(["purchase_date", "staff_member"])
        .size()
        .reset_index(name="appointments_count")
    )

    # Merge with daily payroll
    daily = daily_payroll.merge(
        therapist_days,
        on=["purchase_date", "staff_member"],
        how="left"
    ).fillna(0)

    # -----------------------------
    # 5. Correct Hybrid Accrual Logic (Option C)
    # -----------------------------

    # Count worked days per staff per payroll period
    worked_days = (
        daily[daily["appointments_count"] > 0]
        .groupby("idx")["purchase_date"]
        .nunique()
        .rename("worked_days")
    )

    daily = daily.merge(worked_days, on="idx", how="left")
    daily["worked_days"] = daily["worked_days"].fillna(0)

    # Total days in payroll period
    daily["total_days"] = daily.groupby(
        "idx")["purchase_date"].transform("nunique")

    def compute_daily_cost(row):
        # Admin: cost spread across all days
        if row["role"] == "Admin":
            return row["daily_cost_base"]

        # Therapist:
        # If no worked days → allocate evenly across all days
        if row["worked_days"] == 0:
            return row["daily_cost_base"]

        # Therapist daily cost = employer_cost / worked_days
        therapist_daily_cost = (
            row["daily_cost_base"] * row["total_days"]) / row["worked_days"]

        # Apply cost only to worked days
        if row["appointments_count"] > 0:
            return therapist_daily_cost

        return 0.0

    daily["daily_cost"] = daily.apply(compute_daily_cost, axis=1)

    # -----------------------------
    # 6. Convert date → period_month
    # -----------------------------
    daily["period_month"] = daily["purchase_date"].dt.to_period("M")

    # -----------------------------
    # 7. Aggregate to monthly payroll per staff_member
    # -----------------------------
    monthly_payroll_by_staff = (
        daily.groupby(["period_month", "staff_member"])["daily_cost"]
        .sum()
        .reset_index()
        .rename(columns={"daily_cost": "payroll_accrual"})
    )

    # Ensure period_month is Period[M]
    monthly_payroll_by_staff["period_month"] = monthly_payroll_by_staff["period_month"].astype(
        "period[M]")

    # -----------------------------
    # 8. Aggregate to monthly payroll
    # -----------------------------
    monthly_payroll = (
        daily.groupby(["period_month"])["daily_cost"]
        .sum()
        .reset_index()
        .rename(columns={"daily_cost": "payroll_accrual"})
    )

    # Ensure period_month is Period[M]
    monthly_payroll["period_month"] = monthly_payroll["period_month"].astype(
        "period[M]")

    return monthly_payroll_by_staff, monthly_payroll
