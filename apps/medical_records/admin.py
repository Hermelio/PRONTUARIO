from django.contrib import admin

from .models import ClinicalEvolution


@admin.register(ClinicalEvolution)
class ClinicalEvolutionAdmin(admin.ModelAdmin):
    list_display = ("date", "time", "patient", "professional", "short_description")
    list_filter = ("date", "professional")
    search_fields = (
        "patient__full_name",
        "patient__cpf",
        "professional__full_name",
        "service_description",
        "procedures_performed",
        "conduct",
        "notes",
    )
    autocomplete_fields = ("patient", "professional", "appointment")
    date_hierarchy = "date"
    fieldsets = (
        ("Identificacao", {
            "fields": ("patient", "professional", "appointment", "date", "time"),
        }),
        ("Evolucao", {
            "fields": ("service_description", "procedures_performed", "conduct", "notes"),
        }),
    )

    @admin.display(description="descricao")
    def short_description(self, obj):
        return obj.service_description[:90]
