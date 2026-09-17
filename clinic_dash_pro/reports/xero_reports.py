# clinic_dash_pro\reports\xero_reports.py

import pandas as pd
from clinic_dash_pro.helper.helper import ty_ly_py, get_periods


periods = get_periods()

latest_closed_month = periods["latest_closed_month"]
current_month = periods["current_month"]
current_year = periods["current_year"]
latest_closed_year = periods["latest_closed_year"]

# ---------------------------------------------------------
# 6. Operational Expense Report (Xero)
# ---------------------------------------------------------


def report_operational_expenses(xero_df):
    """
    Build operational expense report using:
        - Xero Expenses (6000–6999)
        - Xero Assets (1000–1999)
    """

    # Convert date → datetime
    xero_df["date"] = pd.to_datetime(xero_df["date"], errors="coerce")
    xero_df["period_month"] = xero_df["date"].dt.to_period("M")
    xero_df["period_quarter"] = xero_df["date"].dt.to_period("Q")
    xero_df["period_year"] = xero_df["date"].dt.to_period("Y")

    # Add ty_ly_py to the data
    xero_df = ty_ly_py(xero_df, "period_year")

    # Convert amount → positive
    xero_df["amount"] = xero_df["gross"].abs()

    # Separate expenses and assets
    category_dfs = {
        category: xero_df[xero_df["category"] == category].copy()
        for category in xero_df["category"].unique()
    }

    # -----------------------------
    # Categories
    # -----------------------------

    categories_totals = pd.DataFrame([
        {
            "category": category,
            "total_amount": df_cat[df_cat["period_month"] == latest_closed_month]["gross"].sum(),
            "total_amount_year": df_cat[df_cat["period_year"] == current_year]["gross"].sum(),
        }
        for category, df_cat in category_dfs.items()
    ]).sort_values("total_amount_year")

    print(categories_totals.reset_index(drop=True))

    expenses = category_dfs["Expense"]
    assets = category_dfs["Asset"]

    # -----------------------------
    # Monthly Expenses (cash-based)
    # -----------------------------
    monthly_expenses = (
        expenses.groupby(["period_month", "ty_ly_py"])["amount"]
        .sum()
        .rename("expense_amount")
    )

    # -----------------------------
    # Monthly Asset Expenses (simple mode)
    # -----------------------------
    # Full asset expensed in purchase month (no amortization)

    monthly_assets = (
        assets.groupby(["period_month", "ty_ly_py"])["amount"]
        .sum()
        .rename("asset_amount")
    )

    # -----------------------------
    # Combine Monthly Operational Costs
    # -----------------------------
    monthly = pd.concat([monthly_expenses, monthly_assets], axis=1).fillna(0)
    monthly["operational_total"] = round(
        monthly["expense_amount"] + monthly["asset_amount"], 2)

    monthly_expenses_assets = monthly.reset_index()

    # -----------------------------
    # YTD Summary
    # -----------------------------
    operational_current_year = monthly_expenses_assets[monthly_expenses_assets["ty_ly_py"] == 'TY']

    ytd = (
        operational_current_year[["expense_amount",
                                  "asset_amount", "operational_total"]]
        .sum()
        .to_frame()
        .T
    )
    ytd["period_month"] = str(operational_current_year["period_month"].min(
    )) + " / "+str(operational_current_year["period_month"].max())

    ytd["ty_ly_py"] = operational_current_year["ty_ly_py"].unique()

    # -----------------------------
    # GRAND TOTAL
    # -----------------------------
    grand_total = pd.DataFrame({
        "expense_amount": [monthly["expense_amount"].sum()],
        "asset_amount": [monthly["asset_amount"].sum()],
        "operational_total": [monthly["operational_total"].sum()]
    })
    grand_total["period_month"] = str(monthly_expenses_assets["period_month"].min(
    )) + " / "+str(monthly_expenses_assets["period_month"].max())

    grand_total["ty_ly_py"] = 'All Time'

    # Return combined dataset
    final = pd.concat([monthly_expenses_assets, ytd,
                      grand_total], ignore_index=True)

    # Print sections

    print("\n==============================")
    print(" Operational Expenses + Assets - Excluding Payroll ")
    print("===============================")
    print(final)

    # -----------------------------
    # Expenses Breakdown
    # -----------------------------

    expenses_assets_df = pd.concat([expenses, assets], axis=0)

    expenses_assets_agg = (
        expenses_assets_df.groupby(
            ["period_year", "period_quarter", "period_month",
             "category", "related_account"]
        )["amount"]
        .sum()
    ).reset_index()

    # Filter for latest CLOSED month
    exp_asset_lst = expenses_assets_agg[
        expenses_assets_agg["period_month"] == latest_closed_month
    ].reset_index(drop=True)

    # Category totals (for the new column)
    cat_tot = (
        exp_asset_lst.groupby("category")["amount"]
        .sum()
        .reset_index()
        .rename(columns={"amount": "category_total"})
    )

    # Merge category totals into the breakdown
    exp_asset_lst = exp_asset_lst.merge(cat_tot, on="category", how="left")

    # Build total row (overall total)
    overall_total = exp_asset_lst["amount"].sum()

    total_row = pd.DataFrame({
        "period_month": [latest_closed_month],
        "period_quarter": [latest_closed_month.asfreq("Q")],
        "period_year": [latest_closed_month.asfreq("Y")],
        "category": ["TOTAL"],
        "related_account": ["ALL ACCOUNTS"],
        "amount": [overall_total],
        "category_total": [overall_total]
    })

    # Append total row
    exp_asset_lst_final = pd.concat(
        [exp_asset_lst, total_row], ignore_index=True)

    print("\n==============================")
    print(
        f" Operational Expenses + Assets - Excluding Payroll ({latest_closed_month})")
    print("===============================")
    print(exp_asset_lst_final)

    return xero_df, final


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
