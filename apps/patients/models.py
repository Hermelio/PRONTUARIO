from django.db import models
from django.utils import timezone

from apps.professionals.models import Professional


class Patient(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Ativo"
        INACTIVE = "inactive", "Inativo"

    class Sex(models.TextChoices):
        FEMALE = "F", "Feminino"
        MALE = "M", "Masculino"
        OTHER = "O", "Outro"
        NOT_INFORMED = "N", "Nao informado"

    full_name = models.CharField("nome completo", max_length=255)
    cpf = models.CharField("CPF", max_length=14, unique=True)
    birth_date = models.DateField("data de nascimento", null=True, blank=True)
    sex = models.CharField("sexo", max_length=1, choices=Sex.choices, default=Sex.NOT_INFORMED)
    phone = models.CharField("telefone", max_length=30, blank=True)
    email = models.EmailField("e-mail", blank=True)
    status = models.CharField("status", max_length=20, choices=Status.choices, default=Status.ACTIVE)

    zip_code = models.CharField("CEP", max_length=12, blank=True)
    street = models.CharField("logradouro", max_length=255, blank=True)
    number = models.CharField("numero", max_length=20, blank=True)
    complement = models.CharField("complemento", max_length=120, blank=True)
    neighborhood = models.CharField("bairro", max_length=120, blank=True)
    city = models.CharField("cidade", max_length=120, blank=True)
    state = models.CharField("UF", max_length=2, blank=True)
    latitude = models.DecimalField("latitude", max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField("longitude", max_digits=9, decimal_places=6, null=True, blank=True)

    primary_diagnosis = models.CharField("diagnostico principal", max_length=255, blank=True)
    secondary_diagnoses = models.TextField("diagnosticos secundarios", blank=True)
    comorbidities = models.TextField("comorbidades", blank=True)
    allergies = models.TextField("alergias", blank=True)
    current_medications = models.TextField("medicamentos em uso", blank=True)
    clinical_notes = models.TextField("observacoes clinicas", blank=True)

    responsible_name = models.CharField("nome do responsavel", max_length=255, blank=True)
    responsible_relationship = models.CharField("grau de parentesco", max_length=80, blank=True)
    responsible_phone = models.CharField("telefone do responsavel", max_length=30, blank=True)
    responsible_email = models.EmailField("e-mail do responsavel", blank=True)

    assigned_professional = models.ForeignKey(
        Professional,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="patients",
        verbose_name="profissional interno responsavel",
    )
    referring_professional_name = models.CharField("medico/fisioterapeuta responsavel", max_length=255, blank=True)
    referring_professional_specialty = models.CharField("especialidade", max_length=120, blank=True)
    referring_professional_council = models.CharField("CRM/conselho", max_length=50, blank=True)
    referring_professional_phone = models.CharField("telefone", max_length=30, blank=True)
    referring_professional_email = models.EmailField("e-mail", blank=True)

    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        ordering = ["full_name"]
        verbose_name = "paciente"
        verbose_name_plural = "pacientes"

    def __str__(self):
        return self.full_name

    @property
    def age(self):
        if not self.birth_date:
            return None
        today = timezone.localdate()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )

    @property
    def google_maps_url(self):
        if self.latitude is not None and self.longitude is not None:
            return f"https://www.google.com/maps/search/?api=1&query={self.latitude},{self.longitude}"
        address_parts = [
            self.street,
            self.number,
            self.neighborhood,
            self.city,
            self.state,
            self.zip_code,
        ]
        query = ", ".join(part for part in address_parts if part)
        if not query:
            return ""
        return f"https://www.google.com/maps/search/?api=1&query={query.replace(' ', '+')}"

    @property
    def route_url(self):
        if not self.google_maps_url:
            return ""
        if self.latitude is not None and self.longitude is not None:
            return f"https://www.google.com/maps/dir/?api=1&destination={self.latitude},{self.longitude}"
        return self.google_maps_url.replace("/search/", "/dir/")
