from django.urls import path

from . import views

app_name = "assessments"

urlpatterns = [
    path("pacientes/<int:patient_id>/", views.patient_indicators_view, name="patient_indicators"),
]
