from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from django.urls import reverse


class CoreViewTests(SimpleTestCase):
    def test_home_returns_success(self):
        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 200)

    def test_healthcheck_returns_success(self):
        response = self.client.get(reverse("core:healthcheck"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")


class CoreAuthenticatedViewTests(TestCase):
    def test_authenticated_home_redirects_to_portal(self):
        get_user_model().objects.create_user(username="usuario", password="senha-forte")
        self.client.login(username="usuario", password="senha-forte")

        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("accounts:portal"))
