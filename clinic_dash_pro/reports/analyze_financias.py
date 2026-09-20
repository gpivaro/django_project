import pandas as pd
import numpy as np


def analyze_unified_financials(
    unified: pd.DataFrame,
    monthly_payroll_by_staff: pd.DataFrame,
    jane_df: pd.DataFrame,
):
    """
    Deep‑dive analysis on unified accrual financials.
    Expects unified to have:
        period_month, revenue, payroll, operational_total,
        real_profit, ty_ly_py, period_year, period_quarter
    """

    unified = unified.sort_values("period_month").reset_index(drop=True)

    for col in ["revenue", "payroll", "operational_total", "real_profit"]:
        unified[col] = pd.to_numeric(unified[col], errors="coerce")

    print("\n=== 1) Month‑over‑Month Revenue & Profit ===")
    df_mom = compute_mom_trends(unified)
    print(df_mom.tail(12))

    print("\n=== 2) Payroll & Operational Efficiency Ratios ===")
    df_eff = compute_efficiency_ratios(unified)
    print(df_eff.tail(12))

    print("\n=== 3) Quarterly Summary (Revenue, Payroll, Ops, Profit) ===")
    df_q = compute_quarterly_summary(unified)
    print(df_q)

    print("\n=== 4) TY vs LY Year‑over‑Year Comparison ===")
    df_yearly, df_yoy = compute_ty_ly_comparison(unified)
    print(df_yearly)
    print("\n--- TY - LY ---")
    print(df_yoy)

    print("\n=== 5) Therapist Profitability (Revenue vs Payroll) ===")
    df_tp = compute_therapist_profitability(monthly_payroll_by_staff, jane_df)
    print(df_tp.sort_values(
        ["period_month", "therapist_profit"], ascending=[True, False]).tail(20))

    print("\n=== 6) Quarter‑over‑Quarter (QoQ) Profit & Revenue ===")
    df_qoq = compute_qoq(unified)
    print(df_qoq)

    return df_tp


def compute_mom_trends(unified: pd.DataFrame) -> pd.DataFrame:
    df = unified.copy()

    df["revenue_mom_pct"] = df["revenue"].pct_change().round(4)
    df["profit_mom_pct"] = df["real_profit"].pct_change().round(4)

    df["revenue_3m_avg"] = df["revenue"].rolling(3).mean().round(2)
    df["profit_3m_avg"] = df["real_profit"].rolling(3).mean().round(2)

    return df[[
        "period_month", "revenue", "real_profit",
        "revenue_mom_pct", "profit_mom_pct",
        "revenue_3m_avg", "profit_3m_avg"
    ]]


def compute_efficiency_ratios(unified: pd.DataFrame) -> pd.DataFrame:
    df = unified.copy()

    df["payroll_ratio"] = (df["payroll"] / df["revenue"]
                           ).replace([np.inf, -np.inf], np.nan).round(4)
    df["ops_ratio"] = (df["operational_total"] / df["revenue"]
                       ).replace([np.inf, -np.inf], np.nan).round(4)
    df["profit_margin"] = (df["real_profit"] / df["revenue"]
                           ).replace([np.inf, -np.inf], np.nan).round(4)

    return df[[
        "period_month", "revenue", "payroll", "operational_total", "real_profit",
        "payroll_ratio", "ops_ratio", "profit_margin"
    ]]


def compute_quarterly_summary(unified: pd.DataFrame) -> pd.DataFrame:
    q = (
        unified.groupby("period_quarter")[
            ["revenue", "payroll", "operational_total", "real_profit"]]
        .sum()
        .reset_index()
    )

    q["payroll_ratio"] = (q["payroll"] / q["revenue"]).round(4)
    q["ops_ratio"] = (q["operational_total"] / q["revenue"]).round(4)
    q["profit_margin"] = (q["real_profit"] / q["revenue"]).round(4)

    return q


def compute_ty_ly_comparison(unified: pd.DataFrame):

    # Yearly summary (unchanged)
    yearly = (
        unified.groupby(["period_year", "ty_ly_py"])[
            ["revenue", "payroll", "operational_total", "real_profit"]
        ]
        .sum()
        .reset_index()
    )

    # Extract TY and LY rows
    ty = unified[unified["ty_ly_py"] == "TY"].copy()
    ly = unified[unified["ty_ly_py"] == "LY"].copy()

    # Extract month number from YYYY-MM
    ty["month_num"] = ty["period_month"].str[-2:].astype(int)
    ly["month_num"] = ly["period_month"].str[-2:].astype(int)

    # Align on month number (1–12)
    common_months = sorted(
        set(ty["month_num"]).intersection(set(ly["month_num"])))

    if not common_months:
        # No matching months → no YoY possible
        yoy = pd.DataFrame(columns=[
            "month_num", "revenue", "payroll",
            "operational_total", "real_profit"
        ])
        return yearly, yoy

    # FIX: convert set → list for indexing
    ty2 = ty.set_index("month_num").loc[common_months]
    ly2 = ly.set_index("month_num").loc[common_months]

    cols = ["revenue", "payroll", "operational_total", "real_profit"]

    # Compute YoY deltas
    yoy = ty2[cols] - ly2[cols]
    yoy["month_num"] = common_months

    return yearly, yoy.reset_index(drop=True)


def compute_therapist_profitability(
    monthly_payroll_by_staff: pd.DataFrame,
    jane_df: pd.DataFrame,
) -> pd.DataFrame:

    # Therapist revenue per month (from Jane accrual)
    therapist_rev = (
        jane_df.groupby(["period_month", "employee_initials"])[
            "revenue_accrual"]
        .sum()
        .reset_index()
        .rename(columns={"revenue_accrual": "therapist_revenue"})
    )

    # Therapist payroll per month (accrual)
    therapist_payroll = monthly_payroll_by_staff.rename(
        columns={"payroll_accrual": "therapist_payroll"}
    )

    # Merge
    tp = therapist_rev.merge(
        therapist_payroll,
        on=["period_month", "employee_initials"],
        how="left"
    )

    tp["therapist_payroll"] = tp["therapist_payroll"].fillna(0)
    tp["therapist_profit"] = (
        tp["therapist_revenue"] - tp["therapist_payroll"]).round(2)

    # Optional: profit margin per therapist
    tp["therapist_margin"] = (
        tp["therapist_profit"] / tp["therapist_revenue"]
    ).replace([np.inf, -np.inf], np.nan).round(4)

    return tp


def compute_qoq(unified: pd.DataFrame) -> pd.DataFrame:
    q = (
        unified.groupby("period_quarter")[
            ["revenue", "payroll", "operational_total", "real_profit"]]
        .sum()
        .reset_index()
        .sort_values("period_quarter")
    )

    q["revenue_qoq_pct"] = q["revenue"].pct_change().round(4)
    q["profit_qoq_pct"] = q["real_profit"].pct_change().round(4)

    return q
