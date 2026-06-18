from django.contrib import admin

from .models import Professional, ProfessionalDocument


class ProfessionalDocumentInline(admin.TabularInline):
    model = ProfessionalDocument
    extra = 0
    fields = ("title", "document_type", "file", "uploaded_at")
    readonly_fields = ("uploaded_at",)


@admin.register(Professional)
class ProfessionalAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "cpf",
        "professional_council",
        "council_number",
        "primary_specialty",
        "status",
    )
    list_filter = ("status", "sex", "state", "council_state", "primary_specialty")
    search_fields = ("full_name", "cpf", "rg", "email", "phone", "council_number")
    inlines = [ProfessionalDocumentInline]
    fieldsets = (
        ("Dados pessoais", {
            "fields": ("full_name", "cpf", "rg", "birth_date", "sex", "phone", "email"),
        }),
        ("Endereco", {
            "fields": (
                "zip_code",
                "street",
                "number",
                "complement",
                "neighborhood",
                "city",
                "state",
            ),
        }),
        ("Dados profissionais", {
            "fields": (
                "professional_council",
                "council_number",
                "council_state",
                "primary_specialty",
                "secondary_specialties",
                "hired_at",
                "status",
            ),
        }),
    )


@admin.register(ProfessionalDocument)
class ProfessionalDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "professional", "document_type", "uploaded_at")
    list_filter = ("document_type", "uploaded_at")
    search_fields = ("title", "professional__full_name", "professional__cpf")
