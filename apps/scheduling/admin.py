from django.contrib import admin

from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "date",
        "starts_at",
        "ends_at",
        "patient",
        "professional",
        "appointment_type",
        "status",
        "recurrence_frequency",
    )
    list_filter = ("status", "appointment_type", "recurrence_frequency", "date")
    search_fields = ("patient__full_name", "patient__cpf", "professional__full_name", "professional__cpf")
    autocomplete_fields = ("patient", "professional")
    date_hierarchy = "date"
    fieldsets = (
        ("Agendamento", {
            "fields": (
                "patient",
                "professional",
                "date",
                "starts_at",
                "ends_at",
                "appointment_type",
                "status",
                "notes",
            ),
        }),
        ("Recorrencia", {
            "fields": (
                "recurrence_frequency",
                "recurrence_interval",
                "recurrence_weekdays",
                "recurrence_until",
                "recurrence_count",
            ),
        }),
    )
