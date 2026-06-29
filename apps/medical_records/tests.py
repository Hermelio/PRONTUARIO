from datetime import date, time

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.access_control.models import AccessProfile
from apps.patients.models import Patient
from apps.professionals.models import Professional

from .models import ClinicalEvolution


class ClinicalEvolutionTests(TestCase):
    def setUp(self):
        self.patient = Patient.objects.create(full_name="Paciente Prontuario", cpf="500.000.000-00")
        self.professional = Professional.objects.create(full_name="Profissional Prontuario", cpf="600.000.000-00")

    def _user_with_role(self, username, role, professional=None):
        user = get_user_model().objects.create_user(username=username, password="senha-forte")
        profile = user.access_profile
        profile.role = role
        profile.professional = professional
        profile.save()
        return user

    def test_evolution_string_representation(self):
        evolution = ClinicalEvolution.objects.create(
            patient=self.patient,
            professional=self.professional,
            date=date(2026, 6, 17),
            time=time(8, 30),
            service_description="Atendimento domiciliar realizado.",
        )

        self.assertIn("Paciente Prontuario", str(evolution))

    def test_patient_record_requires_login(self):
        response = self.client.get(reverse("medical_records:patient_record", args=[self.patient.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])

    def test_medical_record_index_lists_accessible_patients(self):
        self._user_with_role("coord-index", AccessProfile.Role.COORDINATOR)
        self.client.login(username="coord-index", password="senha-forte")

        response = self.client.get(reverse("medical_records:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Paciente Prontuario")
        self.assertContains(response, "Central de prontuarios")

    def test_patient_record_lists_evolutions_for_coordinator(self):
        ClinicalEvolution.objects.create(
            patient=self.patient,
            professional=self.professional,
            date=date(2026, 6, 17),
            time=time(8, 30),
            service_description="Treino de marcha e orientacoes.",
        )
        self._user_with_role("coord-prontuario", AccessProfile.Role.COORDINATOR)
        self.client.login(username="coord-prontuario", password="senha-forte")

        response = self.client.get(reverse("medical_records:patient_record", args=[self.patient.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Treino de marcha")

    def test_professional_sees_only_assigned_patient_record(self):
        assigned_patient = Patient.objects.create(
            full_name="Paciente Vinculado",
            cpf="501.000.000-00",
            assigned_professional=self.professional,
        )
        other_patient = Patient.objects.create(full_name="Paciente Bloqueado", cpf="502.000.000-00")
        self._user_with_role("prof-prontuario", AccessProfile.Role.PROFESSIONAL, self.professional)
        self.client.login(username="prof-prontuario", password="senha-forte")

        allowed = self.client.get(reverse("medical_records:patient_record", args=[assigned_patient.pk]))
        blocked = self.client.get(reverse("medical_records:patient_record", args=[other_patient.pk]))

        self.assertEqual(allowed.status_code, 200)
        self.assertEqual(blocked.status_code, 404)

    def test_financial_user_cannot_access_patient_record(self):
        self._user_with_role("fin-prontuario", AccessProfile.Role.FINANCIAL)
        self.client.login(username="fin-prontuario", password="senha-forte")

        response = self.client.get(reverse("medical_records:patient_record", args=[self.patient.pk]))

        self.assertEqual(response.status_code, 403)

    def test_financial_user_cannot_access_record_index(self):
        self._user_with_role("fin-index", AccessProfile.Role.FINANCIAL)
        self.client.login(username="fin-index", password="senha-forte")

        response = self.client.get(reverse("medical_records:index"))

        self.assertEqual(response.status_code, 403)

    def test_create_evolution_from_portal(self):
        self._user_with_role("coord-evolucao", AccessProfile.Role.COORDINATOR)
        self.client.login(username="coord-evolucao", password="senha-forte")

        response = self.client.post(reverse("medical_records:evolution_create", args=[self.patient.pk]), {
            "professional": self.professional.pk,
            "date": "2026-06-29",
            "time": "09:30",
            "service_description": "Evolucao registrada pela area operacional.",
            "procedures_performed": "Treino funcional.",
            "conduct": "Manter plano terapeutico.",
            "notes": "Paciente orientado.",
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            ClinicalEvolution.objects.filter(
                patient=self.patient,
                service_description__icontains="area operacional",
            ).exists()
        )
