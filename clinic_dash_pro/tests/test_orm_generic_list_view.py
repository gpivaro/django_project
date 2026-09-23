# clinic_dash_pro\tests\test_orm_generic_list_view.py
import pandas as pd
from io import BytesIO

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from clinic_dash_pro.models import JaneSessions


class GenericListViewORMTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("gabriel", password="pass")
        self.client.login(username="gabriel", password="pass")

        # Base record
        self.base = JaneSessions.objects.create(
            staff_member='June S',
            employee_initials='J.S',
            purchase_date='2026-09-10',
            invoice_date='2026-09-10',
            invoice_number='2631-C01',
            item='Speech Therapy',
            payer='BlueCross Texas',
            status='paid',
            subtotal=55.14,
            total=55.14,
            collected=55.14,
            balance=0,
            hash_key='17d2',
        )

    def test_orm_filtering(self):
        url = reverse("jane_sessions_list") + "?q=2631-C01"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        filtered_ids = self.client.session["filtered_ids"]

        # ORM filtering is broad — ensure at least one match
        self.assertTrue(len(filtered_ids) > 0)

    def test_orm_export_filtered_ids(self):
        """ORM export must store filtered IDs correctly."""
        url = reverse("jane_sessions_list") + "?q=2631-C01"
        self.client.get(url)

        # After Option 2, filtered_ids = visible page IDs
        filtered_ids = self.client.session["filtered_ids"]

        # Should contain the base record
        self.assertIn(self.base.id, filtered_ids)

    def test_orm_sorting_does_not_break_export(self):
        url = reverse("jane_sessions_list") + "?q=2631-C01&sort=-purchase_date"
        self.client.get(url)

        filtered_ids = self.client.session["filtered_ids"]

        # Sorting should not break export
        self.assertTrue(len(filtered_ids) > 0)

    def test_orm_pagination(self):
        """Pagination must return a page object."""
        response = self.client.get(reverse("jane_sessions_list"))
        items = response.context["items"]
        self.assertTrue(hasattr(items, "paginator"))
        self.assertTrue(hasattr(items, "object_list"))

    def test_orm_export_uses_filtered_ids(self):
        # Remove base record created in setUp
        JaneSessions.objects.all().delete()

        # Seed ORM data with unique hash_keys
        match = JaneSessions.objects.create(
            invoice_number="2631-C01", hash_key="hk1")
        JaneSessions.objects.create(invoice_number="9999-X01", hash_key="hk2")

        # Filter list view
        self.client.get(reverse("jane_sessions_list") + "?q=2631-C01")

        # Export
        response = self.client.get(
            reverse("export_excel", args=["JaneSessions"]))

        # Load exported Excel into a DataFrame
        df = pd.read_excel(BytesIO(response.content))

        # Should only export the filtered record
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]["invoice_number"], "2631-C01")
