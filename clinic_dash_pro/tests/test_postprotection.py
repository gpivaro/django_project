# clinic_dash_pro\tests\test_postprotection.py

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class PostProtectionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("test", password="pass")

        self.post_urls = [
            reverse("upload_gusto"),
            reverse("upload_xero"),
            reverse("upload_jane_sessions"),
            reverse("upload_jane_processed_claims"),
            reverse("export_csv", kwargs={"model_name": "XeroTransaction"}),
            reverse("export_excel", kwargs={"model_name": "XeroTransaction"}),
        ]

    def test_post_requires_login(self):
        for url in self.post_urls:
            response = self.client.post(url, {})
            self.assertEqual(response.status_code, 302)

    def test_post_after_login(self):
        self.client.login(username="test", password="pass")
        for url in self.post_urls:
            response = self.client.post(url, {})
            self.assertNotEqual(response.status_code, 302)
