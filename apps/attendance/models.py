from decimal import Decimal
from math import asin, cos, radians, sin, sqrt

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.scheduling.models import Appointment


class AttendanceRecord(models.Model):
    class RadiusMeters(models.IntegerChoices):
        FIFTY = 50, "50 metros"
        ONE_HUNDRED = 100, "100 metros"
        TWO_HUNDRED = 200, "200 metros"

    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name="attendance_record",
        verbose_name="agendamento",
    )
    check_in_at = models.DateTimeField("horario do check-in", null=True, blank=True)
    check_in_latitude = models.DecimalField("latitude do check-in", max_digits=9, decimal_places=6, null=True, blank=True)
    check_in_longitude = models.DecimalField("longitude do check-in", max_digits=9, decimal_places=6, null=True, blank=True)
    check_in_distance_meters = models.PositiveIntegerField("distancia no check-in", null=True, blank=True)
    check_in_radius_meters = models.PositiveSmallIntegerField(
        "raio permitido",
        choices=RadiusMeters.choices,
        default=settings.CHECKIN_DEFAULT_RADIUS_METERS,
    )
    check_in_allowed = models.BooleanField("check-in permitido", default=False)

    check_out_at = models.DateTimeField("horario do check-out", null=True, blank=True)
    check_out_latitude = models.DecimalField("latitude do check-out", max_digits=9, decimal_places=6, null=True, blank=True)
    check_out_longitude = models.DecimalField("longitude do check-out", max_digits=9, decimal_places=6, null=True, blank=True)
    check_out_distance_meters = models.PositiveIntegerField("distancia no check-out", null=True, blank=True)
    duration_minutes = models.PositiveIntegerField("duracao em minutos", null=True, blank=True)

    notes = models.TextField("observacoes", blank=True)
    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        ordering = ["-check_in_at", "-created_at"]
        verbose_name = "registro de check-in/check-out"
        verbose_name_plural = "registros de check-in/check-out"
        indexes = [
            models.Index(fields=["check_in_at"]),
            models.Index(fields=["check_in_allowed"]),
        ]

    def __str__(self):
        return f"Check-in de {self.appointment}"

    @property
    def professional(self):
        return self.appointment.professional

    @property
    def patient(self):
        return self.appointment.patient

    @staticmethod
    def calculate_distance_meters(origin_latitude, origin_longitude, target_latitude, target_longitude):
        earth_radius_meters = 6371000
        origin_latitude = radians(float(origin_latitude))
        origin_longitude = radians(float(origin_longitude))
        target_latitude = radians(float(target_latitude))
        target_longitude = radians(float(target_longitude))

        delta_latitude = target_latitude - origin_latitude
        delta_longitude = target_longitude - origin_longitude

        haversine = (
            sin(delta_latitude / 2) ** 2
            + cos(origin_latitude) * cos(target_latitude) * sin(delta_longitude / 2) ** 2
        )
        distance = 2 * earth_radius_meters * asin(sqrt(haversine))
        return round(distance)

    def calculate_distance_from_patient(self, latitude, longitude):
        patient = self.patient
        if patient.latitude is None or patient.longitude is None:
            raise ValidationError("O paciente precisa ter latitude e longitude cadastradas.")

        return self.calculate_distance_meters(
            patient.latitude,
            patient.longitude,
            latitude,
            longitude,
        )

    def register_check_in(self, latitude, longitude, radius_meters=None, checked_at=None):
        radius = radius_meters or self.check_in_radius_meters
        distance = self.calculate_distance_from_patient(latitude, longitude)

        self.check_in_at = checked_at or timezone.now()
        self.check_in_latitude = Decimal(str(latitude))
        self.check_in_longitude = Decimal(str(longitude))
        self.check_in_distance_meters = distance
        self.check_in_radius_meters = radius
        self.check_in_allowed = distance <= radius
        return self.check_in_allowed

    def register_check_out(self, latitude, longitude, checked_at=None):
        if not self.check_in_at:
            raise ValidationError("Nao e possivel registrar check-out antes do check-in.")

        check_out_at = checked_at or timezone.now()
        if check_out_at < self.check_in_at:
            raise ValidationError("O check-out nao pode ser anterior ao check-in.")

        self.check_out_at = check_out_at
        self.check_out_latitude = Decimal(str(latitude))
        self.check_out_longitude = Decimal(str(longitude))
        self.check_out_distance_meters = self.calculate_distance_from_patient(latitude, longitude)
        self.duration_minutes = round((self.check_out_at - self.check_in_at).total_seconds() / 60)
        return self.duration_minutes

    def clean(self):
        if self.check_out_at and not self.check_in_at:
            raise ValidationError({"check_out_at": "Nao e possivel registrar check-out antes do check-in."})
        if self.check_in_at and self.check_out_at and self.check_out_at < self.check_in_at:
            raise ValidationError({"check_out_at": "O check-out nao pode ser anterior ao check-in."})
