from django.contrib import admin

from .models import AssessmentField, AssessmentMetric, AssessmentTemplate, ClinicalAssessment


class AssessmentFieldInline(admin.TabularInline):
    model = AssessmentField
    extra = 1


@admin.register(AssessmentTemplate)
class AssessmentTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "specialty", "is_active", "created_at")
    list_filter = ("specialty", "is_active")
    search_fields = ("name", "description")
    inlines = [AssessmentFieldInline]


class AssessmentMetricInline(admin.TabularInline):
    model = AssessmentMetric
    extra = 1


@admin.register(ClinicalAssessment)
class ClinicalAssessmentAdmin(admin.ModelAdmin):
    list_display = ("performed_at", "patient", "professional", "template")
    list_filter = ("template__specialty", "template", "performed_at")
    search_fields = ("patient__full_name", "patient__cpf", "professional__full_name", "summary")
    autocomplete_fields = ("patient", "professional", "template")
    date_hierarchy = "performed_at"
    inlines = [AssessmentMetricInline]


@admin.register(AssessmentField)
class AssessmentFieldAdmin(admin.ModelAdmin):
    list_display = ("label", "template", "field_type", "unit", "is_required", "order")
    list_filter = ("field_type", "is_required", "template__specialty")
    search_fields = ("label", "template__name")


@admin.register(AssessmentMetric)
class AssessmentMetricAdmin(admin.ModelAdmin):
    list_display = ("name", "assessment", "numeric_value", "text_value", "unit", "higher_is_better")
    list_filter = ("name", "higher_is_better", "assessment__template__specialty")
    search_fields = ("name", "assessment__patient__full_name", "assessment__template__name")
