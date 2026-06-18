from datetime import date, time

from django.test import TestCase
from django.urls import reverse

from apps.patients.models import Patient
from apps.professionals.models import Professional

from .models import ClinicalEvolution


class ClinicalEvolutionTests(TestCase):
    def setUp(self):
        self.patient = Patient.objects.create(full_name="Paciente Prontuario", cpf="500.000.000-00")
        self.professional = Professional.objects.create(full_name="Profissional Prontuario", cpf="600.000.000-00")

    def test_evolution_string_representation(self):
        evolution = ClinicalEvolution.objects.create(
            patient=self.patient,
            professional=self.professional,
            date=date(2026, 6, 17),
            time=time(8, 30),
            service_description="Atendimento domiciliar realizado.",
        )

        self.assertIn("Paciente Prontuario", str(evolution))

    def test_patient_record_lists_evolutions(self):
        ClinicalEvolution.objects.create(
            patient=self.patient,
            professional=self.professional,
            date=date(2026, 6, 17),
            time=time(8, 30),
            service_description="Treino de marcha e orientacoes.",
        )

        response = self.client.get(reverse("medical_records:patient_record", args=[self.patient.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Treino de marcha")
