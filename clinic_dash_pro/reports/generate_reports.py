# clinic_dash_pro\reports\generate_reports
import pandas as pd
from .expenses_reports import report_operational_expenses, operating_expenses_breakdown
from .accrual_reports import build_accrual_payroll
from .revenue_report import merge_claims_sessions
from .unified_reports import build_unified_financials
from .analyze_financias import analyze_unified_financials


class GenerateReport:
    """
    Validation suite for data reports.

    This class checks:


    Inputs:
        gusto_df            → raw Gusto payroll data
        jane_sessions_df    → raw Jane sessions data
        jane_claims_df      → raw Jane claims data
        xero_df             → raw Xero data
    """

    def __init__(self, gusto_df, jane_sessions_df, jane_claims_df, xero_df):
        self.gusto_df = pd.DataFrame(gusto_df)
        self.jane_sessions_df = pd.DataFrame(jane_sessions_df)
        self.jane_claims_df = pd.DataFrame(jane_claims_df)
        self.xero_df = pd.DataFrame(xero_df)

    def get_operational_report(self):

        monthly_operational_expenses_assets = report_operational_expenses(
            self.xero_df)

        monthly_operational_expenses_assets['period_month'] = monthly_operational_expenses_assets['period_month'].astype(
            str)

        return monthly_operational_expenses_assets

    def get_accrual_payroll(self):
        monthly_payroll_by_staff, monthly_payroll = build_accrual_payroll(
            self.gusto_df, self.jane_sessions_df)

        return monthly_payroll_by_staff, monthly_payroll

    def get_accrual_revenue(self):

        claims_sessions_merged = merge_claims_sessions(
            self.jane_claims_df, self.jane_sessions_df)
        return claims_sessions_merged

    def get_unified_financials(self):

        # Call your own methods
        monthly_operational = pd.DataFrame(
            report_operational_expenses(self.xero_df))

        _, monthly_payroll = self.get_accrual_payroll()

        monthly_revenue = self.get_accrual_revenue()

        # Build unified report
        unified_financials = build_unified_financials(
            monthly_revenue=monthly_revenue,
            monthly_payroll=monthly_payroll,
            monthly_operational=monthly_operational
        )

        # FIX: Convert pandas Period → string
        for col in ["period_month", "period_year", "period_quarter"]:
            if col in unified_financials.columns:
                unified_financials[col] = unified_financials[col].astype(str)

        return unified_financials

    def get_analyze_unified_financials(self):

        monthly_payroll_by_staff, _ = self.get_accrual_payroll()

        unified_financials = self.get_unified_financials()

        monthly_revenue = self.get_accrual_revenue()

        therapist_profitability = analyze_unified_financials(
            unified_financials, monthly_payroll_by_staff, monthly_revenue)

        return therapist_profitability

    def get_operating_expenses_breakdown(self):

        expenses_monthly_df, assets_monthly_df = operating_expenses_breakdown(
            self.xero_df)

        return expenses_monthly_df, assets_monthly_df

    def get_income_statement(self):
        """
        Build a unified Income Statement dataset by stacking:
            - Monthly Revenue (Jane accrual)
            - Monthly Payroll (Gusto accrual)
            - Monthly Operating Expenses (Xero)
            - Monthly Assets (Xero)

        Ensures:
            - All DataFrames share the same period metadata:
                period_month, period_quarter, period_year, ty_ly_py
            - All DataFrames use the same column schema:
                period_month, category, related_account, amount
            - Final output is a single stacked DataFrame.
        """

        # ---------------------------------------------------------
        # 1. Get operating expenses + assets (already monthly)
        #    These contain full period metadata → authoritative
        # ---------------------------------------------------------
        expenses_monthly_df, assets_monthly_df = self.get_operating_expenses_breakdown()

        period_cols = ["period_month",
                       "period_quarter", "period_year", "ty_ly_py"]
        base_cols = ["period_month", "category", "related_account", "amount"]

        # Build lookup BEFORE trimming columns
        period_lookup = (
            expenses_monthly_df[period_cols]
            .drop_duplicates(subset=["period_month"])
            .set_index("period_month")
        )

        # ---------------------------------------------------------
        # 2. Get monthly revenue (Jane accrual)
        # ---------------------------------------------------------
        monthly_revenue = self.get_accrual_revenue()
        monthly_revenue["category"] = "Income"
        monthly_revenue["related_account"] = "4100 - Service Revenue"
        monthly_revenue = monthly_revenue.rename(
            columns={"amount": "tot_amount", "revenue_accrual": "amount"})

        print(monthly_revenue.iloc[0])

        # ---------------------------------------------------------
        # 3. Get monthly payroll (Gusto accrual)
        # ---------------------------------------------------------
        _, monthly_payroll = self.get_accrual_payroll()
        monthly_payroll["category"] = "Wages and Salaries Transactions/Taxes - Payroll"
        monthly_payroll["related_account"] = "6450 - Wages and Salaries / 6360 - Taxes - Payroll"
        monthly_payroll = monthly_payroll.rename(
            columns={"payroll_accrual": "amount"})

        # ---------------------------------------------------------
        # 4. Attach period metadata via lookup
        # ---------------------------------------------------------

        def attach_period_metadata(df):
            return df.merge(period_lookup, on="period_month", how="left")

        monthly_payroll = attach_period_metadata(monthly_payroll)

        # Now trim to common schema
        expenses_monthly_df = expenses_monthly_df[period_cols + base_cols[1:]]
        assets_monthly_df = assets_monthly_df[period_cols + base_cols[1:]]
        monthly_revenue = monthly_revenue[period_cols + base_cols[1:]]
        monthly_payroll = monthly_payroll[period_cols + base_cols[1:]]

        # -----------------------------------
        # 4A - Convert to Negative
        expenses_monthly_df["amount"] = -1*expenses_monthly_df["amount"]
        assets_monthly_df["amount"] = -1*assets_monthly_df["amount"]
        monthly_payroll["amount"] = -1*monthly_payroll["amount"]

        # ---------------------------------------------------------
        # 5. Stack all datasets into one unified Income Statement
        # ---------------------------------------------------------

        income_statement = pd.concat(
            [
                monthly_revenue,
                monthly_payroll,
                expenses_monthly_df,
                assets_monthly_df,
            ],
            ignore_index=True
        )

        income_statement = income_statement.groupby(
            ['period_month', 'period_quarter', 'period_year', 'ty_ly_py',
             'category', 'related_account'])['amount'].sum().reset_index()

        income_statement = income_statement.sort_values(
            ["period_year", "period_month", "category"]
        ).reset_index(drop=True)

        return income_statement
