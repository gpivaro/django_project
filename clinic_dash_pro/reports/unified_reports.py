import pandas as pd
from clinic_dash_pro.helper.helper import get_periods, ty_ly_py


periods = get_periods()

latest_closed_month = periods["latest_closed_month"]
current_month = periods["current_month"]
current_year = periods["current_year"]
latest_closed_year = periods["latest_closed_year"]


def build_unified_financials(
    monthly_revenue: pd.DataFrame,
    monthly_payroll: pd.DataFrame,
    monthly_operational: pd.DataFrame
):
    """
    Combine:
        - Jane accrual revenue
        - Gusto payroll (accrual)
        - Xero operational expenses + assets

    Output:
        Unified monthly accrual financial dataset:
            period_month
            revenue
            payroll
            operational_cost
            real_profit
            ty_ly_py
    """

    # ---------------------------------------------------------
    # 1. Prepare Jane Revenue (monthly)
    # ---------------------------------------------------------
    jane_rev = monthly_revenue.copy()
    # Convert date → datetime
    jane_rev["purchase_date"] = pd.to_datetime(
        jane_rev["purchase_date"], errors="coerce")

    jane_rev = jane_rev.groupby("period_month")[
        "revenue_accrual"].sum().reset_index()
    jane_rev = jane_rev.rename(columns={"revenue_accrual": "revenue"})

    # ---------------------------------------------------------
    # 2. Use Accrual Payroll (monthly)
    # ---------------------------------------------------------
    gusto_payroll = monthly_payroll.copy()
    gusto_payroll = gusto_payroll.rename(
        columns={"payroll_accrual": "payroll"})
    gusto_payroll["payroll"] = round(
        gusto_payroll["payroll"], 2)

    # ---------------------------------------------------------
    # 3. Prepare Xero Operational Costs (monthly)
    # ---------------------------------------------------------
    xero_ops = monthly_operational.copy()

    # Normalize period_month type
    xero_ops["period_month"] = xero_ops["period_month"].astype("period[M]")

    # Keep only the monthly rows
    xero_ops = xero_ops[["period_month", "operational_total", "ty_ly_py"]]

    # ---------------------------------------------------------
    # 4. Merge all three datasets
    # ---------------------------------------------------------
    unified = (
        jane_rev
        .merge(gusto_payroll, on="period_month", how="outer")
        .merge(xero_ops, on="period_month", how="outer")
    )

    # ---------------------------------------------------------
    # 5. Fill missing values
    # ---------------------------------------------------------
    unified["revenue"] = unified["revenue"].fillna(0)
    unified["payroll"] = unified["payroll"].fillna(0)
    unified["operational_total"] = unified["operational_total"].fillna(0)

    # ---------------------------------------------------------
    # 6. Compute Real Profit (Accrual Basis)
    # ---------------------------------------------------------
    unified["real_profit"] = (
        unified["revenue"]
        - unified["payroll"]
        - unified["operational_total"]
    ).round(2)

    # ---------------------------------------------------------
    # 7. Add year/quarter for reporting
    # ---------------------------------------------------------
    unified["period_year"] = unified["period_month"].astype("period[Y]")
    unified["period_quarter"] = unified["period_month"].astype("period[Q]")

    # ---------------------------------------------------------
    # 8. Add TY/LY/PY classification
    # ---------------------------------------------------------
    unified = ty_ly_py(unified, "period_year")

    # ---------------------------------------------------------
    # 9. Sort and return
    # ---------------------------------------------------------
    unified = unified.sort_values("period_month").reset_index(drop=True)

    # -----------------------------
    # YTD Summary (current year only)
    # -----------------------------
    monthly_current_year = unified[
        (unified["ty_ly_py"] == "TY") &
        (unified["period_month"] <= latest_closed_month)
    ]

    ytd = (
        monthly_current_year.groupby("period_year")[
            ["revenue", "payroll", "operational_total", "real_profit"]
        ]
        .sum()
    )

    ytd["period"] = "YTD"
    ytd_reset = ytd.reset_index()

    # -----------------------------
    # GRAND TOTAL ROW
    # -----------------------------
    grand_total = pd.DataFrame({
        "period_year": ["ALL"],
        "revenue": [unified["revenue"].sum()],
        "payroll": [unified["payroll"].sum()],
        "operational_total": [unified["operational_total"].sum()],
        "real_profit": [unified["real_profit"].sum()],
        "period": ["GRAND TOTAL"]
    })

    # -----------------------------
    # PRINT SECTIONS
    # -----------------------------
    print("\n==============================")
    print(" Unified Accrual Financials ")
    print("==============================")
    print(unified)

    print("\n==============================")
    print(" Unified YTD Totals")
    print("==============================")
    print(ytd_reset)

    print("\n==============================")
    print(" GRAND TOTAL (YTD)")
    print("==============================")
    print(grand_total)

    return unified
