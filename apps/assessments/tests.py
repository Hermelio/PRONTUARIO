from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.access_control.models import AccessProfile
from apps.patients.models import Patient
from apps.professionals.models import Professional

from .models import AssessmentField, AssessmentMetric, AssessmentTemplate, ClinicalAssessment


class ClinicalAssessmentTests(TestCase):
    def setUp(self):
        self.patient = Patient.objects.create(full_name="Paciente Avaliacao", cpf="700.000.000-00")
        self.professional = Professional.objects.create(full_name="Profissional Avaliacao", cpf="800.000.000-00")
        self.template = AssessmentTemplate.objects.create(
            name="Avaliacao Ortopedica",
            specialty=AssessmentTemplate.Specialty.ORTHOPEDIC,
        )
        self.field = AssessmentField.objects.create(
            template=self.template,
            label="Dor",
            field_type=AssessmentField.FieldType.SCALE,
            unit="0-10",
            is_required=True,
            order=1,
        )

    def _user_with_role(self, username, role, professional=None):
        user = get_user_model().objects.create_user(username=username, password="senha-forte")
        profile = user.access_profile
        profile.role = role
        profile.professional = professional
        profile.save()
        return user

    def test_assessment_comparison_identifies_improvement(self):
        previous = ClinicalAssessment.objects.create(
            patient=self.patient,
            professional=self.professional,
            template=self.template,
            performed_at=timezone.now() - timedelta(days=30),
        )
        current = ClinicalAssessment.objects.create(
            patient=self.patient,
            professional=self.professional,
            template=self.template,
            performed_at=timezone.now(),
        )
        AssessmentMetric.objects.create(
            assessment=previous,
            name="Forca muscular",
            numeric_value=Decimal("40.00"),
            unit="%",
            higher_is_better=True,
        )
        AssessmentMetric.objects.create(
            assessment=current,
            name="Forca muscular",
            numeric_value=Decimal("50.00"),
            unit="%",
            higher_is_better=True,
        )

        comparison = current.compare_with(previous)

        self.assertEqual(comparison[0]["metric"], "Forca muscular")
        self.assertEqual(comparison[0]["variation_percent"], Decimal("25.00"))
        self.assertTrue(comparison[0]["improved"])

    def test_assessment_comparison_handles_lower_is_better(self):
        previous = ClinicalAssessment.objects.create(
            patient=self.patient,
            professional=self.professional,
            template=self.template,
            performed_at=timezone.now() - timedelta(days=30),
        )
        current = ClinicalAssessment.objects.create(
            patient=self.patient,
            professional=self.professional,
            template=self.template,
            performed_at=timezone.now(),
        )
        AssessmentMetric.objects.create(
            assessment=previous,
            name="Dor",
            numeric_value=Decimal("8.00"),
            higher_is_better=False,
        )
        AssessmentMetric.objects.create(
            assessment=current,
            name="Dor",
            numeric_value=Decimal("5.00"),
            higher_is_better=False,
        )

        comparison = current.compare_with(previous)

        self.assertEqual(comparison[0]["variation_percent"], Decimal("-37.50"))
        self.assertTrue(comparison[0]["improved"])

    def test_assessment_index_requires_login(self):
        response = self.client.get(reverse("assessments:index"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])

    def test_professional_sees_only_assigned_patient_assessments(self):
        self.patient.assigned_professional = self.professional
        self.patient.save()
        other_patient = Patient.objects.create(full_name="Paciente Fora", cpf="701.000.000-00")
        self._user_with_role("prof-avaliacao", AccessProfile.Role.PROFESSIONAL, self.professional)
        self.client.login(username="prof-avaliacao", password="senha-forte")

        response = self.client.get(reverse("assessments:index"))
        allowed = self.client.get(reverse("assessments:patient_assessments", args=[self.patient.pk]))
        blocked = self.client.get(reverse("assessments:patient_assessments", args=[other_patient.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.patient.full_name)
        self.assertNotContains(response, other_patient.full_name)
        self.assertEqual(allowed.status_code, 200)
        self.assertEqual(blocked.status_code, 404)

    def test_financial_user_cannot_access_assessments(self):
        self._user_with_role("fin-avaliacao", AccessProfile.Role.FINANCIAL)
        self.client.login(username="fin-avaliacao", password="senha-forte")

        response = self.client.get(reverse("assessments:index"))

        self.assertEqual(response.status_code, 403)

    def test_create_assessment_from_operational_area(self):
        self._user_with_role("coord-avaliacao", AccessProfile.Role.COORDINATOR)
        self.client.login(username="coord-avaliacao", password="senha-forte")

        response = self.client.post(reverse("assessments:assessment_create", args=[self.patient.pk]), {
            "professional": self.professional.pk,
            "template": self.template.pk,
            "performed_at": "2026-06-29T09:30",
            "summary": "Avaliacao operacional registrada.",
            f"metric_{self.field.pk}": "4.00",
        })

        self.assertEqual(response.status_code, 302)
        assessment = ClinicalAssessment.objects.get(summary="Avaliacao operacional registrada.")
        self.assertEqual(assessment.metrics.count(), 1)
        self.assertEqual(assessment.metrics.first().numeric_value, Decimal("4.00"))
