from django.contrib import admin

from .models import AttendanceRecord


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = (
        "appointment",
        "patient_name",
        "professional_name",
        "check_in_at",
        "check_in_allowed",
        "check_in_distance_meters",
        "check_out_at",
        "duration_minutes",
    )
    list_filter = ("check_in_allowed", "check_in_radius_meters", "check_in_at", "check_out_at")
    search_fields = (
        "appointment__patient__full_name",
        "appointment__patient__cpf",
        "appointment__professional__full_name",
        "appointment__professional__cpf",
    )
    autocomplete_fields = ("appointment",)
    readonly_fields = (
        "check_in_distance_meters",
        "check_in_allowed",
        "check_out_distance_meters",
        "duration_minutes",
    )

    @admin.display(description="paciente")
    def patient_name(self, obj):
        return obj.patient

    @admin.display(description="profissional")
    def professional_name(self, obj):
        return obj.professional
