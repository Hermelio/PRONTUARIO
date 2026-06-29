from django.urls import path

from . import views

app_name = "assessments"

urlpatterns = [
    path("", views.assessment_index_view, name="index"),
    path("pacientes/<int:patient_id>/avaliacoes/", views.patient_assessments_view, name="patient_assessments"),
    path("pacientes/<int:patient_id>/avaliacoes/nova/", views.assessment_create_view, name="assessment_create"),
    path("pacientes/<int:patient_id>/", views.patient_indicators_view, name="patient_indicators"),
]
