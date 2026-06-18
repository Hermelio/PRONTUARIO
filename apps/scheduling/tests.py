from datetime import date, time

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.patients.models import Patient
from apps.professionals.models import Professional

from .models import Appointment


class AppointmentModelTests(TestCase):
    def setUp(self):
        self.patient = Patient.objects.create(full_name="Paciente A", cpf="100.000.000-00")
        self.professional = Professional.objects.create(full_name="Profissional A", cpf="200.000.000-00")

    def test_appointment_requires_end_after_start(self):
        appointment = Appointment(
            patient=self.patient,
            professional=self.professional,
            date=date(2026, 6, 17),
            starts_at=time(10, 0),
            ends_at=time(9, 0),
        )

        with self.assertRaises(ValidationError):
            appointment.clean()

    def test_detects_professional_time_overlap(self):
        Appointment.objects.create(
            patient=self.patient,
            professional=self.professional,
            date=date(2026, 6, 17),
            starts_at=time(9, 0),
            ends_at=time(10, 0),
        )
        overlapping = Appointment(
            patient=self.patient,
            professional=self.professional,
            date=date(2026, 6, 17),
            starts_at=time(9, 30),
            ends_at=time(10, 30),
        )

        with self.assertRaises(ValidationError):
            overlapping.clean()

    def test_weekly_recurrence_requires_weekdays(self):
        appointment = Appointment(
            patient=self.patient,
            professional=self.professional,
            date=date(2026, 6, 17),
            starts_at=time(9, 0),
            ends_at=time(10, 0),
            recurrence_frequency=Appointment.RecurrenceFrequency.WEEKLY,
        )

        with self.assertRaises(ValidationError):
            appointment.clean()
