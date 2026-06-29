from django import forms

from apps.professionals.models import Professional

from .models import Appointment


class ScheduleFilterForm(forms.Form):
    VIEW_CHOICES = (
        ("day", "Dia"),
        ("week", "Semana"),
        ("month", "Mes"),
    )

    date = forms.DateField(
        label="Data base",
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control form-control-lg", "type": "date"}),
    )
    view = forms.ChoiceField(
        label="Visualizacao",
        required=False,
        choices=VIEW_CHOICES,
        widget=forms.Select(attrs={"class": "form-select form-select-lg"}),
    )
    professional = forms.ModelChoiceField(
        label="Profissional",
        required=False,
        queryset=Professional.objects.filter(status=Professional.Status.ACTIVE),
        widget=forms.Select(attrs={"class": "form-select form-select-lg"}),
    )
    status = forms.ChoiceField(
        label="Status",
        required=False,
        choices=[("", "Todos")] + list(Appointment.Status.choices),
        widget=forms.Select(attrs={"class": "form-select form-select-lg"}),
    )

    def __init__(self, *args, allow_professional_filter=False, **kwargs):
        super().__init__(*args, **kwargs)
        if not allow_professional_filter:
            self.fields.pop("professional")
