from django.db import models

from apps.patients.models import Patient
from apps.professionals.models import Professional
from apps.scheduling.models import Appointment


class Incident(models.Model):
    class Classification(models.TextChoices):
        MILD = "mild", "Leve"
        MODERATE = "moderate", "Moderada"
        SEVERE = "severe", "Grave"
        CRITICAL = "critical", "Critica"

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="incidents",
        verbose_name="paciente",
    )
    professional = models.ForeignKey(
        Professional,
        on_delete=models.PROTECT,
        related_name="incidents",
        verbose_name="profissional",
    )
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="incidents",
        verbose_name="agendamento",
    )
    date = models.DateField("data")
    time = models.TimeField("hora")
    description = models.TextField("descricao da intercorrencia")
    severity = models.CharField("gravidade", max_length=20, choices=Classification.choices)
    conduct_performed = models.TextField("conduta realizada", blank=True)
    classification = models.CharField("classificacao", max_length=20, choices=Classification.choices)
    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        ordering = ["-date", "-time"]
        verbose_name = "intercorrencia"
        verbose_name_plural = "intercorrencias"
        indexes = [
            models.Index(fields=["patient", "date"]),
            models.Index(fields=["professional", "date"]),
            models.Index(fields=["classification"]),
        ]

    def __str__(self):
        return f"{self.get_classification_display()} - {self.patient} em {self.date:%d/%m/%Y}"
