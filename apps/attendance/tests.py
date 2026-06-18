from datetime import date, time, timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from apps.patients.models import Patient
from apps.professionals.models import Professional
from apps.scheduling.models import Appointment

from .models import AttendanceRecord


class AttendanceRecordTests(TestCase):
    def setUp(self):
        self.patient = Patient.objects.create(
            full_name="Paciente com GPS",
            cpf="300.000.000-00",
            latitude=Decimal("-23.550520"),
            longitude=Decimal("-46.633308"),
        )
        self.professional = Professional.objects.create(full_name="Profissional GPS", cpf="400.000.000-00")
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            professional=self.professional,
            date=date(2026, 6, 17),
            starts_at=time(9, 0),
            ends_at=time(10, 0),
        )

    def test_check_in_is_allowed_inside_radius(self):
        record = AttendanceRecord(appointment=self.appointment)

        allowed = record.register_check_in("-23.550520", "-46.633308", radius_meters=50)

        self.assertTrue(allowed)
        self.assertEqual(record.check_in_distance_meters, 0)

    def test_check_in_is_blocked_outside_radius(self):
        record = AttendanceRecord(appointment=self.appointment)

        allowed = record.register_check_in("-23.560520", "-46.643308", radius_meters=50)

        self.assertFalse(allowed)
        self.assertGreater(record.check_in_distance_meters, 50)

    def test_check_out_calculates_duration(self):
        record = AttendanceRecord(appointment=self.appointment)
        checked_at = timezone.now()
        record.register_check_in("-23.550520", "-46.633308", checked_at=checked_at)

        duration = record.register_check_out(
            "-23.550520",
            "-46.633308",
            checked_at=checked_at + timedelta(minutes=75),
        )

        self.assertEqual(duration, 75)

    def test_check_out_before_check_in_is_invalid(self):
        record = AttendanceRecord(appointment=self.appointment)

        with self.assertRaises(ValidationError):
            record.register_check_out("-23.550520", "-46.633308")
