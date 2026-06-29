from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.access_control.models import AccessProfile
from apps.professionals.models import Professional
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


class PatientPortalViewTests(TestCase):
    def setUp(self):
        self.professional = Professional.objects.create(full_name="Profissional Portal", cpf="111.111.111-11")
        self.patient = Patient.objects.create(
            full_name="Paciente Portal",
            cpf="222.222.222-22",
            assigned_professional=self.professional,
            primary_diagnosis="Reabilitacao motora",
        )

    def _user_with_role(self, username, role, professional=None):
        user = get_user_model().objects.create_user(username=username, password="senha-forte")
        profile = user.access_profile
        profile.role = role
        profile.professional = professional
        profile.save()
        return user

    def test_patient_list_requires_login(self):
        response = self.client.get(reverse("patients:list"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])

    def test_coordinator_can_list_patients(self):
        self._user_with_role("coord", AccessProfile.Role.COORDINATOR)
        self.client.login(username="coord", password="senha-forte")

        response = self.client.get(reverse("patients:list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Paciente Portal")

    def test_financial_user_cannot_access_patients(self):
        self._user_with_role("fin", AccessProfile.Role.FINANCIAL)
        self.client.login(username="fin", password="senha-forte")

        response = self.client.get(reverse("patients:list"))

        self.assertEqual(response.status_code, 403)

    def test_professional_sees_only_assigned_patients(self):
        other_patient = Patient.objects.create(full_name="Paciente Outro", cpf="333.333.333-33")
        self._user_with_role("prof", AccessProfile.Role.PROFESSIONAL, self.professional)
        self.client.login(username="prof", password="senha-forte")

        response = self.client.get(reverse("patients:list"))

        self.assertContains(response, self.patient.full_name)
        self.assertNotContains(response, other_patient.full_name)

    def test_create_patient_from_portal(self):
        self._user_with_role("coord-create", AccessProfile.Role.COORDINATOR)
        self.client.login(username="coord-create", password="senha-forte")

        response = self.client.post(reverse("patients:create"), {
            "full_name": "Novo Paciente",
            "cpf": "444.444.444-44",
            "sex": Patient.Sex.NOT_INFORMED,
            "status": Patient.Status.ACTIVE,
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Patient.objects.filter(cpf="444.444.444-44").exists())
