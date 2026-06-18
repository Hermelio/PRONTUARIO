from django.core.exceptions import ValidationError
from django.db import models

from apps.patients.models import Patient
from apps.professionals.models import Professional


class Appointment(models.Model):
    class AppointmentType(models.TextChoices):
        NURSING = "nursing", "Enfermagem"
        PHYSIOTHERAPY = "physiotherapy", "Fisioterapia"
        MEDICAL = "medical", "Atendimento medico"
        CAREGIVER = "caregiver", "Cuidador"
        SPEECH_THERAPY = "speech_therapy", "Fonoaudiologia"
        OCCUPATIONAL_THERAPY = "occupational_therapy", "Terapia ocupacional"
        OTHER = "other", "Outro"

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Agendado"
        CONFIRMED = "confirmed", "Confirmado"
        IN_PROGRESS = "in_progress", "Em atendimento"
        COMPLETED = "completed", "Finalizado"
        CANCELED = "canceled", "Cancelado"

    class RecurrenceFrequency(models.TextChoices):
        NONE = "none", "Nao repetir"
        DAILY = "daily", "Diario"
        WEEKLY = "weekly", "Semanal"
        MONTHLY = "monthly", "Mensal"

    patient = models.ForeignKey(
        Patient,
        on_delete=models.PROTECT,
        related_name="appointments",
        verbose_name="paciente",
    )
    professional = models.ForeignKey(
        Professional,
        on_delete=models.PROTECT,
        related_name="appointments",
        verbose_name="profissional",
    )
    date = models.DateField("data")
    starts_at = models.TimeField("hora inicial")
    ends_at = models.TimeField("hora final")
    appointment_type = models.CharField(
        "tipo de atendimento",
        max_length=40,
        choices=AppointmentType.choices,
        default=AppointmentType.OTHER,
    )
    notes = models.TextField("observacoes", blank=True)
    status = models.CharField(
        "status",
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED,
    )

    recurrence_frequency = models.CharField(
        "recorrencia",
        max_length=20,
        choices=RecurrenceFrequency.choices,
        default=RecurrenceFrequency.NONE,
    )
    recurrence_interval = models.PositiveSmallIntegerField("intervalo da recorrencia", default=1)
    recurrence_weekdays = models.CharField(
        "dias da semana",
        max_length=30,
        blank=True,
        help_text="Use numeros separados por virgula: 0=segunda, 1=terca, ..., 6=domingo.",
    )
    recurrence_until = models.DateField("repetir ate", null=True, blank=True)
    recurrence_count = models.PositiveIntegerField("quantidade de repeticoes", null=True, blank=True)

    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        ordering = ["date", "starts_at"]
        verbose_name = "agendamento"
        verbose_name_plural = "agendamentos"
        indexes = [
            models.Index(fields=["date", "starts_at"]),
            models.Index(fields=["professional", "date"]),
            models.Index(fields=["patient", "date"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.patient} com {self.professional} em {self.date:%d/%m/%Y} {self.starts_at:%H:%M}"

    @property
    def is_recurring(self):
        return self.recurrence_frequency != self.RecurrenceFrequency.NONE

    def clean(self):
        errors = {}
        if self.starts_at and self.ends_at and self.ends_at <= self.starts_at:
            errors["ends_at"] = "A hora final deve ser maior que a hora inicial."

        if self.recurrence_interval < 1:
            errors["recurrence_interval"] = "O intervalo da recorrencia deve ser maior que zero."

        if self.recurrence_frequency == self.RecurrenceFrequency.WEEKLY and not self.recurrence_weekdays:
            errors["recurrence_weekdays"] = "Informe os dias da semana para recorrencia semanal."

        if self.professional_id and self.date and self.starts_at and self.ends_at:
            overlapping = Appointment.objects.filter(
                professional=self.professional,
                date=self.date,
            ).exclude(status=self.Status.CANCELED)
            if self.pk:
                overlapping = overlapping.exclude(pk=self.pk)
            overlapping = overlapping.filter(starts_at__lt=self.ends_at, ends_at__gt=self.starts_at)
            if overlapping.exists():
                errors["professional"] = "O profissional ja possui atendimento nesse horario."

        if errors:
            raise ValidationError(errors)
