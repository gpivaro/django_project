# clinic_dash_pro\tests\test_auth.py

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class AuthProtectionTests(TestCase):

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )

        # Every URL in clinic_dash_pro that should require login
        self.protected_urls = [
            # Home
            reverse("clinicdashpro_home"),

            # Upload pages
            reverse("upload_gusto"),
            reverse("upload_xero"),
            reverse("upload_jane_sessions"),
            reverse("upload_jane_processed_claims"),

            # Success pages
            reverse("gusto_upload_success"),
            reverse("xero_upload_success"),
            reverse("jane_sessions_upload_success"),
            reverse("jane_processed_claims_upload_success"),

            # List views
            reverse("gusto_list"),
            reverse("xero_list"),
            reverse("jane_sessions_list"),
            reverse("jane_claims_list"),
            reverse("revenue_details_view"),

            # Reports
            reverse("reports_home"),

            # Export routes (need kwargs)
            reverse("export_csv", kwargs={"model_name": "XeroTransaction"}),
            reverse("export_excel", kwargs={"model_name": "XeroTransaction"}),
            reverse("export_df_csv"),
            reverse("export_df_excel"),
        ]

    def test_pages_require_login(self):
        for url in self.protected_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertIn("/login", response.url)

    def test_pages_load_after_login(self):
        self.client.login(username="testuser", password="testpass123")

        for url in self.protected_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
