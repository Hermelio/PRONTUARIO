from django.db import models

from apps.patients.models import Patient
from apps.professionals.models import Professional


class PatientDocument(models.Model):
    class DocumentType(models.TextChoices):
        LAB_EXAM = "lab_exam", "Exame laboratorial"
        IMAGE_EXAM = "image_exam", "Exame de imagem"
        PRESCRIPTION = "prescription", "Receita medica"
        REPORT = "report", "Relatorio"
        MEDICAL_REPORT = "medical_report", "Laudo"
        PDF = "pdf", "PDF"
        PHOTO = "photo", "Foto"
        OTHER = "other", "Outro"

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="documents",
        verbose_name="paciente",
    )
    uploaded_by = models.ForeignKey(
        Professional,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_patient_documents",
        verbose_name="profissional responsavel",
    )
    title = models.CharField("titulo", max_length=180)
    document_type = models.CharField("tipo de documento", max_length=30, choices=DocumentType.choices)
    file = models.FileField("arquivo", upload_to="patients/documents/%Y/%m/")
    document_date = models.DateField("data do documento", null=True, blank=True)
    description = models.TextField("descricao", blank=True)
    created_at = models.DateTimeField("criado em", auto_now_add=True)

    class Meta:
        ordering = ["-document_date", "-created_at"]
        verbose_name = "exame/documento do paciente"
        verbose_name_plural = "exames e documentos dos pacientes"
        indexes = [
            models.Index(fields=["patient", "document_type"]),
            models.Index(fields=["document_date"]),
        ]

    def __str__(self):
        return f"{self.patient} - {self.title}"
