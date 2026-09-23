# clinic_dash_pro\tests\test_reportmath.py

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from clinic_dash_pro.models import JaneSessions, JaneProcessedClaim
from clinic_dash_pro.reports.generate_reports import GenerateReport


class ReportMathTests(TestCase):
    def test_accrual_revenue_math(self):
        # Create mock Jane sessions
        JaneSessions.objects.create(
            staff_member='June S',
            employee_initials='J.S',
            purchase_date='2026-09-10',
            invoice_date='2026-09-10',
            invoice_number="2631-C01",
            item='Speech Therapy',
            payer='BlueCross Texas',
            status='paid',
            subtotal=55.14,
            total=55.14,
            collected=55.14,
            balance=0,
            hash_key='17d2',
        )

        # Create mock Jane claims
        JaneProcessedClaim.objects.create(
            payment_date='2026-09-17',
            payer='BlueCross Texas',
            payment_method='BCBSTX',
            reference_number='C26258E33541510',
            applied_to="['2631-C01']",
            claim_count=1.0,
            amount=55.14,
            processing_fee=0,
            amount_paid_to_clinic=55.14,
            hash_key='c05f4',
        )

        reports = GenerateReport(
            gusto_df=[],
            jane_sessions_df=JaneSessions.objects.all().values(),
            jane_claims_df=JaneProcessedClaim.objects.all().values(),
            xero_df=[],
        )

        df = reports.get_revenue_details()
        self.assertAlmostEqual(df.iloc[0]["revenue_accrual"], 55.14, places=2)
        self.assertEqual(df.iloc[0]["amount_paid_to_clinic"], 55.14)
