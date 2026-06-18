from django.db import models

from apps.patients.models import Patient
from apps.professionals.models import Professional
from apps.scheduling.models import Appointment


class ClinicalEvolution(models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="clinical_evolutions",
        verbose_name="paciente",
    )
    professional = models.ForeignKey(
        Professional,
        on_delete=models.PROTECT,
        related_name="clinical_evolutions",
        verbose_name="profissional",
    )
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="clinical_evolutions",
        verbose_name="agendamento",
    )
    date = models.DateField("data")
    time = models.TimeField("hora")
    service_description = models.TextField("descricao do atendimento")
    procedures_performed = models.TextField("procedimentos realizados", blank=True)
    conduct = models.TextField("conduta", blank=True)
    notes = models.TextField("observacoes", blank=True)
    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        ordering = ["-date", "-time"]
        verbose_name = "evolucao clinica"
        verbose_name_plural = "evolucoes clinicas"
        indexes = [
            models.Index(fields=["patient", "date", "time"]),
            models.Index(fields=["professional", "date"]),
        ]

    def __str__(self):
        return f"Evolucao de {self.patient} em {self.date:%d/%m/%Y} {self.time:%H:%M}"
