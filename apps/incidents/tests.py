from datetime import date, time

from django.test import TestCase

from apps.patients.models import Patient
from apps.professionals.models import Professional

from .models import Incident


class IncidentModelTests(TestCase):
    def test_incident_string_representation(self):
        patient = Patient.objects.create(full_name="Paciente Intercorrencia", cpf="900.000.000-00")
        professional = Professional.objects.create(full_name="Profissional Intercorrencia", cpf="901.000.000-00")

        incident = Incident.objects.create(
            patient=patient,
            professional=professional,
            date=date(2026, 6, 17),
            time=time(10, 15),
            description="Paciente apresentou tontura durante o atendimento.",
            severity=Incident.Classification.MODERATE,
            classification=Incident.Classification.MODERATE,
            conduct_performed="Atendimento pausado e sinais vitais monitorados.",
        )

        self.assertIn("Moderada", str(incident))
