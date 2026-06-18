from django import forms

from .models import ClinicalEvolution


class ClinicalEvolutionSearchForm(forms.Form):
    q = forms.CharField(
        label="Pesquisa",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Buscar por texto, conduta ou observacao"}),
    )
    professional = forms.CharField(
        label="Profissional",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Nome do profissional"}),
    )
    start_date = forms.DateField(
        label="Data inicial",
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )
    end_date = forms.DateField(
        label="Data final",
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )


class ClinicalEvolutionForm(forms.ModelForm):
    class Meta:
        model = ClinicalEvolution
        fields = (
            "professional",
            "appointment",
            "date",
            "time",
            "service_description",
            "procedures_performed",
            "conduct",
            "notes",
        )
        widgets = {
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "professional": forms.Select(attrs={"class": "form-select"}),
            "appointment": forms.Select(attrs={"class": "form-select"}),
            "service_description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "procedures_performed": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "conduct": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
