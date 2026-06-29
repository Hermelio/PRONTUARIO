from decimal import Decimal

from django import forms
from django.utils import timezone

from apps.professionals.models import Professional

from .models import AssessmentField, AssessmentTemplate, ClinicalAssessment


class AssessmentSearchForm(forms.Form):
    q = forms.CharField(
        label="Buscar",
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control form-control-lg",
            "placeholder": "Paciente, CPF, diagnostico ou profissional",
        }),
    )


class ClinicalAssessmentForm(forms.ModelForm):
    class Meta:
        model = ClinicalAssessment
        fields = ("professional", "template", "performed_at", "summary")
        widgets = {
            "professional": forms.Select(attrs={"class": "form-select form-select-lg"}),
            "template": forms.Select(attrs={"class": "form-select form-select-lg"}),
            "performed_at": forms.DateTimeInput(attrs={"class": "form-control form-control-lg", "type": "datetime-local"}),
            "summary": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }

    def __init__(self, *args, professional=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["template"].queryset = AssessmentTemplate.objects.filter(is_active=True)
        if professional:
            self.fields["professional"].queryset = Professional.objects.filter(pk=professional.pk)
            self.fields["professional"].initial = professional


class MetricEntryForm(forms.Form):
    def __init__(self, *args, template=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.template = template
        if not template:
            return

        for field in template.fields.all():
            field_name = self._field_name(field)
            attrs = {"class": "form-control", "placeholder": field.unit}
            required = field.is_required
            if field.field_type in {AssessmentField.FieldType.NUMBER, AssessmentField.FieldType.SCALE}:
                self.fields[field_name] = forms.DecimalField(
                    label=field.label,
                    required=required,
                    decimal_places=2,
                    max_digits=10,
                    widget=forms.NumberInput(attrs={**attrs, "step": "0.01"}),
                    help_text=field.unit,
                )
            elif field.field_type == AssessmentField.FieldType.BOOLEAN:
                self.fields[field_name] = forms.BooleanField(label=field.label, required=False)
            elif field.field_type == AssessmentField.FieldType.DATE:
                self.fields[field_name] = forms.DateField(
                    label=field.label,
                    required=required,
                    widget=forms.DateInput(attrs={**attrs, "type": "date"}),
                    help_text=field.unit,
                )
            else:
                self.fields[field_name] = forms.CharField(
                    label=field.label,
                    required=required,
                    widget=forms.Textarea(attrs={**attrs, "rows": 2}),
                    help_text=field.unit,
                )

    @staticmethod
    def _field_name(field):
        return f"metric_{field.pk}"

    @staticmethod
    def higher_is_better_for(label):
        lower_is_better_terms = ("dor", "queda", "risco", "dispneia", "fadiga", "dependencia")
        normalized = label.lower()
        return not any(term in normalized for term in lower_is_better_terms)

    def iter_metric_values(self):
        if not self.template:
            return
        for field in self.template.fields.all():
            value = self.cleaned_data.get(self._field_name(field))
            if value in (None, ""):
                continue

            numeric_value = None
            text_value = ""
            if field.field_type in {AssessmentField.FieldType.NUMBER, AssessmentField.FieldType.SCALE}:
                numeric_value = Decimal(value)
            elif field.field_type == AssessmentField.FieldType.BOOLEAN:
                text_value = "Sim" if value else "Nao"
                numeric_value = Decimal("1.00") if value else Decimal("0.00")
            elif field.field_type == AssessmentField.FieldType.DATE:
                text_value = value.isoformat()
            else:
                text_value = str(value)

            yield {
                "field": field,
                "name": field.label,
                "numeric_value": numeric_value,
                "text_value": text_value,
                "unit": field.unit,
                "higher_is_better": self.higher_is_better_for(field.label),
            }


def default_performed_at():
    return timezone.localtime().strftime("%Y-%m-%dT%H:%M")
