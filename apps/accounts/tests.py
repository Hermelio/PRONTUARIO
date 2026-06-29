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

    def test_authenticated_login_redirects_to_portal(self):
        get_user_model().objects.create_user(username="logado", password="senha-forte")
        self.client.login(username="logado", password="senha-forte")

        response = self.client.get(reverse("accounts:login"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("accounts:portal"))

    def test_authenticated_navigation_hides_public_sales_links(self):
        user = get_user_model().objects.create_user(username="profissional", password="senha-forte")
        profile = user.access_profile
        profile.role = AccessProfile.Role.PROFESSIONAL
        profile.save()
        self.client.login(username="profissional", password="senha-forte")

        response = self.client.get(reverse("accounts:portal"))

        self.assertContains(response, "Ambiente operacional")
        self.assertContains(response, "Inicio")
        self.assertNotContains(response, "Modulos")
        self.assertNotContains(response, "Seguranca")

    def test_staff_professional_does_not_see_admin_shortcut(self):
        user = get_user_model().objects.create_user(username="staff-prof", password="senha-forte", is_staff=True)
        profile = user.access_profile
        profile.role = AccessProfile.Role.PROFESSIONAL
        profile.save()
        self.client.login(username="staff-prof", password="senha-forte")

        response = self.client.get(reverse("accounts:portal"))

        self.assertNotContains(response, 'href="/admin/"')
