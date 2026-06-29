from datetime import date, time

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from apps.access_control.models import AccessProfile
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


class SchedulePortalViewTests(TestCase):
    def setUp(self):
        self.professional = Professional.objects.create(full_name="Profissional Agenda", cpf="300.000.000-00")
        self.other_professional = Professional.objects.create(full_name="Profissional Outro", cpf="301.000.000-00")
        self.patient = Patient.objects.create(
            full_name="Paciente Agenda",
            cpf="400.000.000-00",
            assigned_professional=self.professional,
            street="Rua Teste",
            number="10",
            city="Sao Paulo",
            state="SP",
        )
        self.other_patient = Patient.objects.create(
            full_name="Paciente Outro",
            cpf="401.000.000-00",
            assigned_professional=self.other_professional,
        )
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            professional=self.professional,
            date=date(2026, 6, 29),
            starts_at=time(9, 0),
            ends_at=time(10, 0),
            status=Appointment.Status.CONFIRMED,
        )
        self.other_appointment = Appointment.objects.create(
            patient=self.other_patient,
            professional=self.other_professional,
            date=date(2026, 6, 29),
            starts_at=time(11, 0),
            ends_at=time(12, 0),
            status=Appointment.Status.SCHEDULED,
        )

    def _user_with_role(self, username, role, professional=None):
        user = get_user_model().objects.create_user(username=username, password="senha-forte")
        profile = user.access_profile
        profile.role = role
        profile.professional = professional
        profile.save()
        return user

    def test_schedule_requires_login(self):
        response = self.client.get(reverse("scheduling:schedule"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])

    def test_professional_sees_only_own_schedule(self):
        self._user_with_role("prof-agenda", AccessProfile.Role.PROFESSIONAL, self.professional)
        self.client.login(username="prof-agenda", password="senha-forte")

        response = self.client.get(reverse("scheduling:schedule"), {"date": "2026-06-29", "view": "day"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Paciente Agenda")
        self.assertNotContains(response, "Paciente Outro")

    def test_coordinator_sees_all_professionals(self):
        self._user_with_role("coord-agenda", AccessProfile.Role.COORDINATOR)
        self.client.login(username="coord-agenda", password="senha-forte")

        response = self.client.get(reverse("scheduling:schedule"), {"date": "2026-06-29", "view": "day"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Paciente Agenda")
        self.assertContains(response, "Paciente Outro")
        self.assertContains(response, "Profissional")

    def test_financial_user_cannot_access_schedule(self):
        self._user_with_role("fin-agenda", AccessProfile.Role.FINANCIAL)
        self.client.login(username="fin-agenda", password="senha-forte")

        response = self.client.get(reverse("scheduling:schedule"))

        self.assertEqual(response.status_code, 403)
