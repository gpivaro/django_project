# clinic_dash_pro\tests\test_staffonly.py


from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class StaffOnlyTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            "user", password="pass", is_staff=False)
        self.staff = User.objects.create_user(
            "staff", password="pass", is_staff=True)

    def test_non_staff_denied(self):
        self.client.login(username="user", password="pass")
        response = self.client.get(reverse("admin_only_view"))
        self.assertEqual(response.status_code, 302)

    def test_staff_allowed(self):
        self.client.login(username="staff", password="pass")
        response = self.client.get(reverse("admin_only_view"))
        self.assertEqual(response.status_code, 200)
