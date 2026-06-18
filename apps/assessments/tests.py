from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from apps.patients.models import Patient
from apps.professionals.models import Professional

from .models import AssessmentMetric, AssessmentTemplate, ClinicalAssessment


class ClinicalAssessmentTests(TestCase):
    def setUp(self):
        self.patient = Patient.objects.create(full_name="Paciente Avaliacao", cpf="700.000.000-00")
        self.professional = Professional.objects.create(full_name="Profissional Avaliacao", cpf="800.000.000-00")
        self.template = AssessmentTemplate.objects.create(
            name="Avaliacao Ortopedica",
            specialty=AssessmentTemplate.Specialty.ORTHOPEDIC,
        )

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
