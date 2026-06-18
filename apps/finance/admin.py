from django.contrib import admin

from .models import FinancialEntry, MonthlyClosing


@admin.register(FinancialEntry)
class FinancialEntryAdmin(admin.ModelAdmin):
    list_display = (
        "reference_date",
        "patient",
        "professional",
        "appointment_quantity",
        "total_amount",
        "company_amount",
        "professional_amount",
        "payer_type",
        "status",
    )
    list_filter = ("status", "payer_type", "insurance_name", "professional_specialty", "reference_date")
    search_fields = ("patient__full_name", "patient__cpf", "professional__full_name", "insurance_name")
    autocomplete_fields = ("appointment", "patient", "professional")
    readonly_fields = ("total_amount", "company_amount", "professional_amount")
    date_hierarchy = "reference_date"


@admin.register(MonthlyClosing)
class MonthlyClosingAdmin(admin.ModelAdmin):
    list_display = (
        "start_date",
        "end_date",
        "professional",
        "appointment_quantity",
        "total_billed",
        "company_receivable",
        "professional_payable",
        "pending_amount",
    )
    list_filter = ("start_date", "end_date", "professional")
    autocomplete_fields = ("professional",)
    readonly_fields = (
        "appointment_quantity",
        "total_billed",
        "company_receivable",
        "professional_payable",
        "pending_amount",
        "generated_at",
    )
