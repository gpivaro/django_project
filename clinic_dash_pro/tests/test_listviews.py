# clinic_dash_pro\tests\test_listviews.py

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

import pandas as pd
from clinic_dash_pro.models import (
    XeroTransaction,
    GustoPayroll,
    JaneSessions,
    JaneProcessedClaim,
)


class RevenueDetailsViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("gabriel", password="pass")
        self.client.login(username="gabriel", password="pass")

        # Minimal Jane session + claim data to produce a DF
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

        JaneProcessedClaim.objects.create(
            payment_date='2026-09-17',
            payer='BlueCross Texas',
            payment_method='BCBSTX',
            reference_number='C26258E33541510',
            applied_to='2631-C01',
            claim_count=1.0,
            amount=55.14,
            processing_fee=0,
            amount_paid_to_clinic=55.14,
            hash_key='c05f4',
        )

    def test_revenue_details_view_renders(self):
        """View returns 200 and contains expected fields."""
        response = self.client.get(reverse("revenue_details_view"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Revenue Details")

    def test_df_export_session_is_populated(self):
        """DF export session keys must be created."""
        self.client.get(reverse("revenue_details_view"))
        self.assertIn("df_export", self.client.session)
        self.assertIn("df_fields", self.client.session)
        self.assertTrue(len(self.client.session["df_export"]) > 0)

    def test_df_filtering(self):
        """Filtering must reduce DF rows and update export session."""
        response = self.client.get(
            reverse("revenue_details_view") + "?q=2631-C01")
        self.assertEqual(response.status_code, 200)

        # Export session must reflect filtered DF
        export_rows = self.client.session["df_export"]
        self.assertEqual(len(export_rows), 1)
        self.assertIn("purchase_date", export_rows[0])

    def test_df_sorting(self):
        """Sorting must reorder DF and update export session."""
        response = self.client.get(
            reverse("revenue_details_view") + "?sort=purchase_date")
        self.assertEqual(response.status_code, 200)

        export_rows = self.client.session["df_export"]
        self.assertEqual(export_rows[0]["purchase_date"], "2026-09-10")

    def test_df_pagination(self):
        """Pagination must return a page object."""
        response = self.client.get(reverse("revenue_details_view"))
        items = response.context["items"]
        self.assertTrue(hasattr(items, "paginator"))
        self.assertTrue(hasattr(items, "object_list"))
