from django.contrib import admin

from .models import Incident


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ("date", "time", "patient", "professional", "classification", "severity")
    list_filter = ("classification", "severity", "date")
    search_fields = (
        "patient__full_name",
        "patient__cpf",
        "professional__full_name",
        "description",
        "conduct_performed",
    )
    autocomplete_fields = ("patient", "professional", "appointment")
    date_hierarchy = "date"
    fieldsets = (
        ("Identificacao", {
            "fields": ("patient", "professional", "appointment", "date", "time"),
        }),
        ("Intercorrencia", {
            "fields": ("description", "severity", "classification", "conduct_performed"),
        }),
    )
