from django.db import models


class Professional(models.Model):
    class Sex(models.TextChoices):
        FEMALE = "F", "Feminino"
        MALE = "M", "Masculino"
        OTHER = "O", "Outro"
        NOT_INFORMED = "N", "Nao informado"

    class Status(models.TextChoices):
        ACTIVE = "active", "Ativo"
        INACTIVE = "inactive", "Inativo"

    full_name = models.CharField("nome completo", max_length=255)
    cpf = models.CharField("CPF", max_length=14, unique=True)
    rg = models.CharField("RG", max_length=30, blank=True)
    birth_date = models.DateField("data de nascimento", null=True, blank=True)
    sex = models.CharField("sexo", max_length=1, choices=Sex.choices, default=Sex.NOT_INFORMED)
    phone = models.CharField("telefone", max_length=30, blank=True)
    email = models.EmailField("e-mail", blank=True)

    zip_code = models.CharField("CEP", max_length=12, blank=True)
    street = models.CharField("logradouro", max_length=255, blank=True)
    number = models.CharField("numero", max_length=20, blank=True)
    complement = models.CharField("complemento", max_length=120, blank=True)
    neighborhood = models.CharField("bairro", max_length=120, blank=True)
    city = models.CharField("cidade", max_length=120, blank=True)
    state = models.CharField("UF", max_length=2, blank=True)

    professional_council = models.CharField("conselho profissional", max_length=30, blank=True)
    council_number = models.CharField("numero do conselho", max_length=50, blank=True)
    council_state = models.CharField("UF do conselho", max_length=2, blank=True)
    primary_specialty = models.CharField("especialidade principal", max_length=120, blank=True)
    secondary_specialties = models.TextField("especialidades secundarias", blank=True)
    hired_at = models.DateField("data de contratacao", null=True, blank=True)
    status = models.CharField("status", max_length=20, choices=Status.choices, default=Status.ACTIVE)

    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        ordering = ["full_name"]
        verbose_name = "profissional"
        verbose_name_plural = "profissionais"

    def __str__(self):
        return self.full_name


class ProfessionalDocument(models.Model):
    class DocumentType(models.TextChoices):
        DIPLOMA = "diploma", "Diploma"
        CERTIFICATE = "certificate", "Certificado"
        COUNCIL_REGISTRATION = "council_registration", "Registro do conselho"
        PERSONAL_DOCUMENT = "personal_document", "Documento pessoal"
        PROOF = "proof", "Comprovante"
        OTHER = "other", "Outro arquivo"

    professional = models.ForeignKey(
        Professional,
        on_delete=models.CASCADE,
        related_name="documents",
        verbose_name="profissional",
    )
    title = models.CharField("titulo", max_length=180)
    document_type = models.CharField(
        "tipo",
        max_length=40,
        choices=DocumentType.choices,
        default=DocumentType.OTHER,
    )
    file = models.FileField("arquivo", upload_to="professionals/documents/%Y/%m/")
    notes = models.TextField("observacoes", blank=True)
    uploaded_at = models.DateTimeField("enviado em", auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "documento do profissional"
        verbose_name_plural = "documentos dos profissionais"

    def __str__(self):
        return f"{self.professional} - {self.title}"
