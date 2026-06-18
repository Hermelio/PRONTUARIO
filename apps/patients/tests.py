from datetime import date
from decimal import Decimal

from django.test import TestCase

from .models import Patient


class PatientModelTests(TestCase):
    def test_patient_age(self):
        patient = Patient.objects.create(
            full_name="Joao Silva",
            cpf="987.654.321-00",
            birth_date=date(2000, 1, 1),
        )

        self.assertGreaterEqual(patient.age, 26)

    def test_patient_maps_url_prefers_coordinates(self):
        patient = Patient.objects.create(
            full_name="Maria Lima",
            cpf="111.222.333-44",
            latitude=Decimal("-23.550520"),
            longitude=Decimal("-46.633308"),
        )

        self.assertIn("-23.550520,-46.633308", patient.google_maps_url)
