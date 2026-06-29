from django import forms

from .models import Patient


class PatientSearchForm(forms.Form):
    q = forms.CharField(
        label="Buscar paciente",
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control form-control-lg",
            "placeholder": "Nome, CPF, telefone, cidade ou diagnóstico",
        }),
    )
    status = forms.ChoiceField(
        label="Status",
        required=False,
        choices=[("", "Todos")] + list(Patient.Status.choices),
        widget=forms.Select(attrs={"class": "form-select form-select-lg"}),
    )


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = (
            "full_name",
            "cpf",
            "birth_date",
            "sex",
            "phone",
            "email",
            "status",
            "zip_code",
            "street",
            "number",
            "complement",
            "neighborhood",
            "city",
            "state",
            "latitude",
            "longitude",
            "primary_diagnosis",
            "secondary_diagnoses",
            "comorbidities",
            "allergies",
            "current_medications",
            "clinical_notes",
            "responsible_name",
            "responsible_relationship",
            "responsible_phone",
            "responsible_email",
            "assigned_professional",
            "referring_professional_name",
            "referring_professional_specialty",
            "referring_professional_council",
            "referring_professional_phone",
            "referring_professional_email",
        )
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control form-control-lg"}),
            "cpf": forms.TextInput(attrs={"class": "form-control"}),
            "birth_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "sex": forms.Select(attrs={"class": "form-select"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "zip_code": forms.TextInput(attrs={"class": "form-control"}),
            "street": forms.TextInput(attrs={"class": "form-control"}),
            "number": forms.TextInput(attrs={"class": "form-control"}),
            "complement": forms.TextInput(attrs={"class": "form-control"}),
            "neighborhood": forms.TextInput(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "state": forms.TextInput(attrs={"class": "form-control", "maxlength": "2"}),
            "latitude": forms.NumberInput(attrs={"class": "form-control", "step": "0.000001"}),
            "longitude": forms.NumberInput(attrs={"class": "form-control", "step": "0.000001"}),
            "primary_diagnosis": forms.TextInput(attrs={"class": "form-control"}),
            "secondary_diagnoses": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "comorbidities": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "allergies": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "current_medications": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "clinical_notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "responsible_name": forms.TextInput(attrs={"class": "form-control"}),
            "responsible_relationship": forms.TextInput(attrs={"class": "form-control"}),
            "responsible_phone": forms.TextInput(attrs={"class": "form-control"}),
            "responsible_email": forms.EmailInput(attrs={"class": "form-control"}),
            "assigned_professional": forms.Select(attrs={"class": "form-select"}),
            "referring_professional_name": forms.TextInput(attrs={"class": "form-control"}),
            "referring_professional_specialty": forms.TextInput(attrs={"class": "form-control"}),
            "referring_professional_council": forms.TextInput(attrs={"class": "form-control"}),
            "referring_professional_phone": forms.TextInput(attrs={"class": "form-control"}),
            "referring_professional_email": forms.EmailInput(attrs={"class": "form-control"}),
        }
