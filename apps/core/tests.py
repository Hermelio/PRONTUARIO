from django.test import SimpleTestCase
from django.urls import reverse


class CoreViewTests(SimpleTestCase):
    def test_home_returns_success(self):
        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 200)

    def test_healthcheck_returns_success(self):
        response = self.client.get(reverse("core:healthcheck"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
