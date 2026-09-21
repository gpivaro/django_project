# clinic_dash_pro\reports\xero_reports.py

import pandas as pd
from clinic_dash_pro.helper.helper import ty_ly_py, get_periods


periods = get_periods()

latest_closed_month = periods["latest_closed_month"]
current_month = periods["current_month"]
current_year = periods["current_year"]
latest_closed_year = periods["latest_closed_year"]

# ---------------------------------------------------------
# 1. Operational Expense Report (Xero)
# ---------------------------------------------------------


def expenses_asset_data(xero_df):
    # Convert date → datetime
    xero_df["date"] = pd.to_datetime(xero_df["date"], errors="coerce")
    xero_df["period_month"] = xero_df["date"].dt.to_period("M")
    xero_df["period_quarter"] = xero_df["date"].dt.to_period("Q")
    xero_df["period_year"] = xero_df["date"].dt.to_period("Y")

    # Add ty_ly_py to the data
    xero_df = ty_ly_py(xero_df, "period_year")

    # Convert amount → positive
    xero_df["amount"] = xero_df["gross"].abs()

    columns = ["hash_key", "insert_date", "account_type", "id"]
    xero_df = xero_df.drop(columns=columns)

    # Separate expenses and assets
    category_dfs = {
        category: xero_df[xero_df["category"] == category].copy()
        for category in xero_df["category"].unique()
    }

    expenses = category_dfs["Expense"].reset_index(drop=True)
    assets = category_dfs["Asset"].reset_index(drop=True)

    return expenses, assets


def report_operational_expenses(xero_df):
    """
    Build operational expense report using:
        - Xero Expenses (6000–6999)
        - Xero Assets (1000–1999)
    """

    expenses, assets = expenses_asset_data(xero_df)

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

    return monthly_expenses_assets


def report_operational_expenses_ytd(monthly_expenses_assets):
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

    return ytd


def report_operational_expenses_lifetime(monthly, monthly_expenses_assets):
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

    return grand_total


def operating_expenses_breakdown(xero_df):

    expenses, assets = expenses_asset_data(xero_df)

    group_cols = [
        'period_year', 'ty_ly_py', 'period_quarter',
        'period_month', 'category', 'related_account'
    ]

    expenses_df = (
        expenses[group_cols + ['amount']]
        .groupby(group_cols)['amount']
        .sum()
        .reset_index()
    )

    assets_df = (
        assets[group_cols + ['amount']]
        .groupby(group_cols)['amount']
        .sum()
        .reset_index()
    )

    return expenses_df, assets_df
