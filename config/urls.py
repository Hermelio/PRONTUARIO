"""URL configuration for PRONTUARIO."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from apps.assessments import views as assessment_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.accounts.urls")),
    path("dashboard/", include("apps.dashboard.urls")),
    path("pacientes/", include("apps.patients.urls")),
    path("agenda/", include("apps.scheduling.urls")),
    path("prontuario/", include("apps.medical_records.urls")),
    path("avaliacoes/", include("apps.assessments.urls")),
    path("indicadores/pacientes/<int:patient_id>/", assessment_views.patient_indicators_view, name="legacy_patient_indicators"),
    path("", include("apps.core.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
