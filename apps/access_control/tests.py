from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.patients.models import Patient
from apps.professionals.models import Professional

from .models import AccessProfile


class AccessProfileTests(TestCase):
    def test_profile_is_created_for_new_user(self):
        user = get_user_model().objects.create_user(username="profissional")

        self.assertTrue(hasattr(user, "access_profile"))

    def test_professional_access_only_own_patients(self):
        user = get_user_model().objects.create_user(username="fisio")
        professional = Professional.objects.create(full_name="Fisio", cpf="930.000.000-00")
        own_patient = Patient.objects.create(full_name="Paciente Proprio", cpf="931.000.000-00", assigned_professional=professional)
        other_patient = Patient.objects.create(full_name="Paciente Outro", cpf="932.000.000-00")
        profile = user.access_profile
        profile.role = AccessProfile.Role.PROFESSIONAL
        profile.professional = professional
        profile.save()

        self.assertTrue(profile.can_access_patient(own_patient))
        self.assertFalse(profile.can_access_patient(other_patient))

    def test_financial_role_accesses_finance_only(self):
        user = get_user_model().objects.create_user(username="financeiro")
        profile = user.access_profile
        profile.role = AccessProfile.Role.FINANCIAL

        self.assertTrue(profile.can_access_module("finance"))
        self.assertFalse(profile.can_access_module("medical_records"))
