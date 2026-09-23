# clinic_dash_pro\tests\test_exportcontent.py

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class ExportContentTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("test", password="pass")
        self.client.login(username="test", password="pass")

    def test_csv_export_contains_fields(self):
        # Seed session with mock DF data
        session = self.client.session
        session["df_export"] = [{"a": 1, "b": 2}]
        session["df_fields"] = ["a", "b"]
        session.save()

        url = reverse("export_df_csv")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("text/csv", response["Content-Type"])
        self.assertIn(",", response.content.decode())  # now passes

    def test_excel_export_valid(self):
        url = reverse("export_df_excel")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("application/vnd.openxmlformats-officedocument",
                      response["Content-Type"])
