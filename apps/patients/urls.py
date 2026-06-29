from django.urls import path

from . import views

app_name = "patients"

urlpatterns = [
    path("", views.patient_list_view, name="list"),
    path("novo/", views.patient_create_view, name="create"),
    path("<int:pk>/", views.patient_detail_view, name="detail"),
    path("<int:pk>/editar/", views.patient_update_view, name="update"),
]
