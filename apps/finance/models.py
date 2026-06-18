from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum

from apps.patients.models import Patient
from apps.professionals.models import Professional
from apps.scheduling.models import Appointment


class FinancialEntry(models.Model):
    class PayerType(models.TextChoices):
        PRIVATE = "private", "Particular"
        INSURANCE = "insurance", "Convenio"

    class Status(models.TextChoices):
        PENDING = "pending", "Pendente"
        RECEIVED = "received", "Recebido"
        PAID = "paid", "Pago ao profissional"
        CANCELED = "canceled", "Cancelado"

    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="financial_entry",
        verbose_name="agendamento",
    )
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="financial_entries", verbose_name="paciente")
    professional = models.ForeignKey(
        Professional,
        on_delete=models.PROTECT,
        related_name="financial_entries",
        verbose_name="profissional",
    )
    reference_date = models.DateField("data de referencia")
    appointment_quantity = models.PositiveIntegerField("quantidade de atendimentos", default=1)
    appointment_value = models.DecimalField("valor do atendimento", max_digits=10, decimal_places=2)
    payer_type = models.CharField("tipo de recebimento", max_length=20, choices=PayerType.choices)
    insurance_name = models.CharField("convenio", max_length=120, blank=True)
    professional_specialty = models.CharField("especialidade", max_length=120, blank=True)

    company_percentage = models.DecimalField("percentual da empresa", max_digits=5, decimal_places=2, default=Decimal("30.00"))
    professional_percentage = models.DecimalField(
        "percentual do profissional",
        max_digits=5,
        decimal_places=2,
        default=Decimal("70.00"),
    )
    total_amount = models.DecimalField("valor total faturado", max_digits=12, decimal_places=2, default=Decimal("0.00"))
    company_amount = models.DecimalField("valor da empresa", max_digits=12, decimal_places=2, default=Decimal("0.00"))
    professional_amount = models.DecimalField("valor do profissional", max_digits=12, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField("status", max_length=20, choices=Status.choices, default=Status.PENDING)
    notes = models.TextField("observacoes", blank=True)
    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        ordering = ["-reference_date", "professional", "patient"]
        verbose_name = "lancamento financeiro"
        verbose_name_plural = "lancamentos financeiros"
        indexes = [
            models.Index(fields=["reference_date"]),
            models.Index(fields=["professional", "reference_date"]),
            models.Index(fields=["patient", "reference_date"]),
            models.Index(fields=["payer_type"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.patient} - {self.reference_date:%d/%m/%Y} - R$ {self.total_amount}"

    def clean(self):
        errors = {}
        if self.appointment_value < 0:
            errors["appointment_value"] = "O valor do atendimento nao pode ser negativo."
        if self.company_percentage < 0 or self.professional_percentage < 0:
            errors["company_percentage"] = "Percentuais nao podem ser negativos."
        if (self.company_percentage + self.professional_percentage) != Decimal("100.00"):
            errors["professional_percentage"] = "A soma dos percentuais da empresa e do profissional deve ser 100%."
        if self.payer_type == self.PayerType.INSURANCE and not self.insurance_name:
            errors["insurance_name"] = "Informe o convenio para recebimentos por convenio."
        if errors:
            raise ValidationError(errors)

    def calculate_amounts(self):
        total = Decimal(self.appointment_quantity) * self.appointment_value
        self.total_amount = total.quantize(Decimal("0.01"))
        self.company_amount = (total * self.company_percentage / Decimal("100")).quantize(Decimal("0.01"))
        self.professional_amount = (total * self.professional_percentage / Decimal("100")).quantize(Decimal("0.01"))

    def save(self, *args, **kwargs):
        if not self.professional_specialty and self.professional_id:
            self.professional_specialty = self.professional.primary_specialty
        self.calculate_amounts()
        super().save(*args, **kwargs)


class MonthlyClosing(models.Model):
    start_date = models.DateField("data inicial")
    end_date = models.DateField("data final")
    professional = models.ForeignKey(
        Professional,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="monthly_closings",
        verbose_name="profissional",
    )
    appointment_quantity = models.PositiveIntegerField("quantidade de atendimentos realizados", default=0)
    total_billed = models.DecimalField("valor total faturado", max_digits=12, decimal_places=2, default=Decimal("0.00"))
    company_receivable = models.DecimalField("valor a receber pela empresa", max_digits=12, decimal_places=2, default=Decimal("0.00"))
    professional_payable = models.DecimalField("valor a receber pelo profissional", max_digits=12, decimal_places=2, default=Decimal("0.00"))
    pending_amount = models.DecimalField("valores pendentes", max_digits=12, decimal_places=2, default=Decimal("0.00"))
    generated_at = models.DateTimeField("gerado em", auto_now=True)

    class Meta:
        ordering = ["-start_date"]
        verbose_name = "fechamento mensal"
        verbose_name_plural = "fechamentos mensais"

    def __str__(self):
        target = self.professional or "Todos os profissionais"
        return f"{target} - {self.start_date:%d/%m/%Y} a {self.end_date:%d/%m/%Y}"

    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError({"end_date": "A data final deve ser maior ou igual a data inicial."})

    def calculate_totals(self):
        entries = FinancialEntry.objects.filter(reference_date__range=(self.start_date, self.end_date)).exclude(
            status=FinancialEntry.Status.CANCELED
        )
        if self.professional_id:
            entries = entries.filter(professional=self.professional)

        totals = entries.aggregate(
            appointment_quantity=Sum("appointment_quantity"),
            total_billed=Sum("total_amount"),
            company_receivable=Sum("company_amount"),
            professional_payable=Sum("professional_amount"),
        )
        pending = entries.filter(status=FinancialEntry.Status.PENDING).aggregate(total=Sum("total_amount"))["total"]

        self.appointment_quantity = totals["appointment_quantity"] or 0
        self.total_billed = totals["total_billed"] or Decimal("0.00")
        self.company_receivable = totals["company_receivable"] or Decimal("0.00")
        self.professional_payable = totals["professional_payable"] or Decimal("0.00")
        self.pending_amount = pending or Decimal("0.00")

    def save(self, *args, **kwargs):
        self.calculate_totals()
        super().save(*args, **kwargs)
