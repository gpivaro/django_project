# clinic_dash_pro\reports\generate_reports
import pandas as pd
from .xero_reports import report_operational_expenses


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
