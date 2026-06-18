from datetime import date, time
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from apps.finance.models import FinancialEntry
from apps.patients.models import Patient
from apps.professionals.models import Professional
from apps.scheduling.models import Appointment

from .services import build_dashboard_summary


class DashboardTests(TestCase):
    def test_dashboard_summary_counts_core_indicators(self):
        patient = Patient.objects.create(full_name="Paciente Dashboard", cpf="920.000.000-00")
        professional = Professional.objects.create(full_name="Profissional Dashboard", cpf="921.000.000-00")
        Appointment.objects.create(
            patient=patient,
            professional=professional,
            date=date.today(),
            starts_at=time(9, 0),
            ends_at=time(10, 0),
            status=Appointment.Status.COMPLETED,
        )
        FinancialEntry.objects.create(
            patient=patient,
            professional=professional,
            reference_date=date.today(),
            appointment_quantity=1,
            appointment_value=Decimal("100.00"),
            payer_type=FinancialEntry.PayerType.PRIVATE,
        )

        summary = build_dashboard_summary(today=date.today())

        self.assertEqual(summary["patients"]["total"], 1)
        self.assertEqual(summary["professionals"]["total"], 1)
        self.assertEqual(summary["appointments"]["today"], 1)
        self.assertEqual(summary["finance"]["monthly_revenue"], Decimal("100.00"))

    def test_dashboard_view_renders(self):
        get_user_model().objects.create_user(username="gestor", password="senha-forte")
        self.client.login(username="gestor", password="senha-forte")

        response = self.client.get(reverse("dashboard:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dashboard executivo")

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard:index"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])
