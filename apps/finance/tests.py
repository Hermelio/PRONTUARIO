from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.patients.models import Patient
from apps.professionals.models import Professional

from .models import FinancialEntry, MonthlyClosing


class FinancialEntryTests(TestCase):
    def setUp(self):
        self.patient = Patient.objects.create(full_name="Paciente Financeiro", cpf="910.000.000-00")
        self.professional = Professional.objects.create(
            full_name="Profissional Financeiro",
            cpf="911.000.000-00",
            primary_specialty="Fisioterapia",
        )

    def test_financial_entry_calculates_split(self):
        entry = FinancialEntry.objects.create(
            patient=self.patient,
            professional=self.professional,
            reference_date=date(2026, 6, 17),
            appointment_quantity=2,
            appointment_value=Decimal("150.00"),
            payer_type=FinancialEntry.PayerType.PRIVATE,
            company_percentage=Decimal("30.00"),
            professional_percentage=Decimal("70.00"),
        )

        self.assertEqual(entry.total_amount, Decimal("300.00"))
        self.assertEqual(entry.company_amount, Decimal("90.00"))
        self.assertEqual(entry.professional_amount, Decimal("210.00"))
        self.assertEqual(entry.professional_specialty, "Fisioterapia")

    def test_insurance_entry_requires_insurance_name(self):
        entry = FinancialEntry(
            patient=self.patient,
            professional=self.professional,
            reference_date=date(2026, 6, 17),
            appointment_quantity=1,
            appointment_value=Decimal("100.00"),
            payer_type=FinancialEntry.PayerType.INSURANCE,
        )

        with self.assertRaises(ValidationError):
            entry.clean()

    def test_monthly_closing_calculates_totals(self):
        FinancialEntry.objects.create(
            patient=self.patient,
            professional=self.professional,
            reference_date=date(2026, 6, 10),
            appointment_quantity=3,
            appointment_value=Decimal("100.00"),
            payer_type=FinancialEntry.PayerType.PRIVATE,
        )
        FinancialEntry.objects.create(
            patient=self.patient,
            professional=self.professional,
            reference_date=date(2026, 6, 20),
            appointment_quantity=1,
            appointment_value=Decimal("200.00"),
            payer_type=FinancialEntry.PayerType.PRIVATE,
            status=FinancialEntry.Status.RECEIVED,
        )

        closing = MonthlyClosing.objects.create(start_date=date(2026, 6, 1), end_date=date(2026, 6, 30))

        self.assertEqual(closing.appointment_quantity, 4)
        self.assertEqual(closing.total_billed, Decimal("500.00"))
        self.assertEqual(closing.company_receivable, Decimal("150.00"))
        self.assertEqual(closing.professional_payable, Decimal("350.00"))
        self.assertEqual(closing.pending_amount, Decimal("300.00"))
