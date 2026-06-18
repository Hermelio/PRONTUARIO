from django.contrib import admin

from .models import PatientDocument


@admin.register(PatientDocument)
class PatientDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "patient", "document_type", "document_date", "uploaded_by", "created_at")
    list_filter = ("document_type", "document_date", "created_at")
    search_fields = ("title", "patient__full_name", "patient__cpf", "description")
    autocomplete_fields = ("patient", "uploaded_by")
    date_hierarchy = "document_date"
