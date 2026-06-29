from django.conf import settings
from django.db import models

from apps.professionals.models import Professional


class AccessProfile(models.Model):
    class Role(models.TextChoices):
        ADMIN = "admin", "Administrador"
        COORDINATOR = "coordinator", "Coordenador"
        PROFESSIONAL = "professional", "Profissional"
        FINANCIAL = "financial", "Financeiro"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="access_profile")
    role = models.CharField("perfil", max_length=20, choices=Role.choices, default=Role.PROFESSIONAL)
    professional = models.OneToOneField(
        Professional,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="access_profile",
        verbose_name="profissional vinculado",
    )
    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        verbose_name = "perfil de acesso"
        verbose_name_plural = "perfis de acesso"

    def __str__(self):
        return f"{self.user} - {self.get_role_display()}"

    def can_access_module(self, module_name):
        if self.role == self.Role.ADMIN:
            return True
        modules_by_role = {
            self.Role.COORDINATOR: {"patients", "professionals", "scheduling", "dashboard", "medical_records", "assessments"},
            self.Role.PROFESSIONAL: {"patients", "scheduling", "attendance", "medical_records", "assessments"},
            self.Role.FINANCIAL: {"finance", "dashboard"},
        }
        return module_name in modules_by_role.get(self.role, set())

    def can_access_patient(self, patient):
        if self.role in {self.Role.ADMIN, self.Role.COORDINATOR}:
            return True
        if self.role == self.Role.PROFESSIONAL and self.professional_id:
            return patient.assigned_professional_id == self.professional_id
        return False
