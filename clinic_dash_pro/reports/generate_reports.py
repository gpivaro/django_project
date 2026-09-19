# clinic_dash_pro\reports\generate_reports
import pandas as pd
from .xero_reports import report_operational_expenses
from .accrual_reports import build_accrual_payroll
from .revenue_report import merge_claims_sessions
from .unified_reports import build_unified_financials


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

        return monthly_operational_expenses_assets.to_dict(orient="records")

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

        return unified_financials.to_dict(orient="records")
