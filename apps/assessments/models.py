from decimal import Decimal

from django.db import models

from apps.patients.models import Patient
from apps.professionals.models import Professional


class AssessmentTemplate(models.Model):
    class Specialty(models.TextChoices):
        ORTHOPEDIC = "orthopedic", "Avaliacao Ortopedica"
        GERONTOLOGICAL = "gerontological", "Avaliacao Gerontologica"
        CARDIORESPIRATORY = "cardiorespiratory", "Avaliacao Cardiorrespiratoria"
        NEUROLOGICAL = "neurological", "Avaliacao Neurologica"
        CUSTOM = "custom", "Avaliacao Personalizada"

    name = models.CharField("nome", max_length=180)
    specialty = models.CharField("especialidade", max_length=40, choices=Specialty.choices)
    description = models.TextField("descricao", blank=True)
    is_active = models.BooleanField("ativo", default=True)
    created_at = models.DateTimeField("criado em", auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "modelo de avaliacao"
        verbose_name_plural = "modelos de avaliacao"

    def __str__(self):
        return self.name


class AssessmentField(models.Model):
    class FieldType(models.TextChoices):
        TEXT = "text", "Texto"
        NUMBER = "number", "Numero"
        SCALE = "scale", "Escala"
        BOOLEAN = "boolean", "Sim/Nao"
        DATE = "date", "Data"

    template = models.ForeignKey(
        AssessmentTemplate,
        on_delete=models.CASCADE,
        related_name="fields",
        verbose_name="modelo",
    )
    label = models.CharField("rotulo", max_length=180)
    field_type = models.CharField("tipo de campo", max_length=20, choices=FieldType.choices)
    unit = models.CharField("unidade", max_length=40, blank=True)
    is_required = models.BooleanField("obrigatorio", default=False)
    order = models.PositiveSmallIntegerField("ordem", default=0)

    class Meta:
        ordering = ["template", "order", "label"]
        verbose_name = "campo de avaliacao"
        verbose_name_plural = "campos de avaliacao"

    def __str__(self):
        return f"{self.template} - {self.label}"


class ClinicalAssessment(models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="clinical_assessments",
        verbose_name="paciente",
    )
    professional = models.ForeignKey(
        Professional,
        on_delete=models.PROTECT,
        related_name="clinical_assessments",
        verbose_name="profissional",
    )
    template = models.ForeignKey(
        AssessmentTemplate,
        on_delete=models.PROTECT,
        related_name="assessments",
        verbose_name="modelo",
    )
    performed_at = models.DateTimeField("data e hora da avaliacao")
    summary = models.TextField("resumo", blank=True)
    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        ordering = ["-performed_at"]
        verbose_name = "avaliacao clinica"
        verbose_name_plural = "avaliacoes clinicas"
        indexes = [
            models.Index(fields=["patient", "performed_at"]),
            models.Index(fields=["template", "performed_at"]),
        ]

    def __str__(self):
        return f"{self.template} - {self.patient} em {self.performed_at:%d/%m/%Y}"

    def compare_with(self, previous_assessment):
        current_metrics = {metric.name: metric for metric in self.metrics.filter(numeric_value__isnull=False)}
        previous_metrics = {
            metric.name: metric
            for metric in previous_assessment.metrics.filter(numeric_value__isnull=False)
        }
        comparisons = []

        for name, current in current_metrics.items():
            previous = previous_metrics.get(name)
            if not previous or previous.numeric_value in (None, Decimal("0")):
                continue

            variation = ((current.numeric_value - previous.numeric_value) / previous.numeric_value) * Decimal("100")
            improved = variation >= 0 if current.higher_is_better else variation <= 0
            comparisons.append({
                "metric": name,
                "previous": previous.numeric_value,
                "current": current.numeric_value,
                "variation_percent": variation.quantize(Decimal("0.01")),
                "improved": improved,
            })

        return comparisons


class AssessmentMetric(models.Model):
    assessment = models.ForeignKey(
        ClinicalAssessment,
        on_delete=models.CASCADE,
        related_name="metrics",
        verbose_name="avaliacao",
    )
    field = models.ForeignKey(
        AssessmentField,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="metrics",
        verbose_name="campo",
    )
    name = models.CharField("indicador", max_length=180)
    numeric_value = models.DecimalField("valor numerico", max_digits=10, decimal_places=2, null=True, blank=True)
    text_value = models.TextField("valor textual", blank=True)
    unit = models.CharField("unidade", max_length=40, blank=True)
    higher_is_better = models.BooleanField("maior e melhor", default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "metrica de avaliacao"
        verbose_name_plural = "metricas de avaliacao"
        indexes = [
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        value = self.numeric_value if self.numeric_value is not None else self.text_value
        return f"{self.name}: {value}"
