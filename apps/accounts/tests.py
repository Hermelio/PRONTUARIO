from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.access_control.models import AccessProfile


class AccountsFlowTests(TestCase):
    def test_login_page_renders(self):
        response = self.client.get(reverse("accounts:login"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Login")

    def test_portal_requires_login(self):
        response = self.client.get(reverse("accounts:portal"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])

    def test_portal_shows_modules_by_profile(self):
        user = get_user_model().objects.create_user(username="financeiro", password="senha-forte")
        profile = user.access_profile
        profile.role = AccessProfile.Role.FINANCIAL
        profile.save()
        self.client.login(username="financeiro", password="senha-forte")

        response = self.client.get(reverse("accounts:portal"))

        self.assertContains(response, "Financeiro")
        self.assertNotContains(response, "Prontuario")
