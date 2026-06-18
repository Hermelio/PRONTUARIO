from django.urls import path

from . import views

app_name = "medical_records"

urlpatterns = [
    path("pacientes/<int:patient_id>/", views.patient_record_view, name="patient_record"),
    path("pacientes/<int:patient_id>/evolucoes/nova/", views.clinical_evolution_create_view, name="evolution_create"),
]
