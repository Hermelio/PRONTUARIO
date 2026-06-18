from django.contrib import admin

from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "cpf",
        "birth_date",
        "display_age",
        "phone",
        "city",
        "state",
        "assigned_professional",
    )
    list_filter = ("sex", "state", "city", "assigned_professional")
    search_fields = (
        "full_name",
        "cpf",
        "phone",
        "email",
        "responsible_name",
        "assigned_professional__full_name",
    )
    readonly_fields = ("display_age", "google_maps_link", "route_link")
    fieldsets = (
        ("Dados cadastrais", {
            "fields": ("full_name", "cpf", "birth_date", "display_age", "sex", "phone", "email"),
        }),
        ("Endereco e geolocalizacao", {
            "fields": (
                "zip_code",
                "street",
                "number",
                "complement",
                "neighborhood",
                "city",
                "state",
                "latitude",
                "longitude",
                "google_maps_link",
                "route_link",
            ),
        }),
        ("Dados clinicos", {
            "fields": (
                "primary_diagnosis",
                "secondary_diagnoses",
                "comorbidities",
                "allergies",
                "current_medications",
                "clinical_notes",
            ),
        }),
        ("Responsavel", {
            "fields": (
                "responsible_name",
                "responsible_relationship",
                "responsible_phone",
                "responsible_email",
            ),
        }),
        ("Profissionais responsaveis", {
            "fields": (
                "assigned_professional",
                "referring_professional_name",
                "referring_professional_specialty",
                "referring_professional_council",
                "referring_professional_phone",
                "referring_professional_email",
            ),
        }),
    )

    @admin.display(description="idade")
    def display_age(self, obj):
        return obj.age if obj.age is not None else "-"

    @admin.display(description="Google Maps")
    def google_maps_link(self, obj):
        return obj.google_maps_url or "-"

    @admin.display(description="Rota")
    def route_link(self, obj):
        return obj.route_url or "-"
