from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PatientForm, PatientSearchForm
from .models import Patient


def _access_profile(user):
    return getattr(user, "access_profile", None)


def _can_access_patients(user):
    profile = _access_profile(user)
    return user.is_superuser or (profile and profile.can_access_module("patients"))


def _patient_queryset_for_user(user):
    queryset = Patient.objects.select_related("assigned_professional").annotate(
        appointment_count=Count("appointments", distinct=True),
        evolution_count=Count("clinical_evolutions", distinct=True),
        document_count=Count("documents", distinct=True),
        incident_count=Count("incidents", distinct=True),
    )
    profile = _access_profile(user)
    if user.is_superuser or not profile:
        return queryset
    if profile.role == profile.Role.PROFESSIONAL and profile.professional_id:
        return queryset.filter(assigned_professional=profile.professional)
    if profile.can_access_module("patients"):
        return queryset
    return queryset.none()


def _ensure_patient_access(user, patient):
    profile = _access_profile(user)
    if user.is_superuser:
        return
    if not profile or not profile.can_access_patient(patient):
        raise PermissionDenied("Você não tem acesso a este paciente.")


@login_required
def patient_list_view(request):
    if not _can_access_patients(request.user):
        raise PermissionDenied("Você não tem acesso ao módulo de pacientes.")

    form = PatientSearchForm(request.GET or None)
    patients = _patient_queryset_for_user(request.user)

    if form.is_valid():
        query = form.cleaned_data.get("q")
        status = form.cleaned_data.get("status")
        if query:
            patients = patients.filter(
                Q(full_name__icontains=query)
                | Q(cpf__icontains=query)
                | Q(phone__icontains=query)
                | Q(city__icontains=query)
                | Q(primary_diagnosis__icontains=query)
                | Q(responsible_name__icontains=query)
            )
        if status:
            patients = patients.filter(status=status)

    summary_queryset = _patient_queryset_for_user(request.user)
    context = {
        "form": form,
        "patients": patients,
        "total_patients": summary_queryset.count(),
        "active_patients": summary_queryset.filter(status=Patient.Status.ACTIVE).count(),
        "inactive_patients": summary_queryset.filter(status=Patient.Status.INACTIVE).count(),
        "mapped_patients": summary_queryset.filter(latitude__isnull=False, longitude__isnull=False).count(),
    }
    return render(request, "patients/patient_list.html", context)


@login_required
def patient_create_view(request):
    if not _can_access_patients(request.user):
        raise PermissionDenied("Você não tem acesso ao módulo de pacientes.")

    if request.method == "POST":
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save()
            return redirect("patients:detail", pk=patient.pk)
    else:
        form = PatientForm()

    return render(request, "patients/patient_form.html", {"form": form, "title": "Novo paciente"})


@login_required
def patient_update_view(request, pk):
    patient = get_object_or_404(_patient_queryset_for_user(request.user), pk=pk)
    _ensure_patient_access(request.user, patient)

    if request.method == "POST":
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            patient = form.save()
            return redirect("patients:detail", pk=patient.pk)
    else:
        form = PatientForm(instance=patient)

    return render(request, "patients/patient_form.html", {"form": form, "patient": patient, "title": "Editar paciente"})


@login_required
def patient_detail_view(request, pk):
    patient = get_object_or_404(_patient_queryset_for_user(request.user), pk=pk)
    _ensure_patient_access(request.user, patient)

    context = {
        "patient": patient,
        "appointments": patient.appointments.select_related("professional").order_by("-date", "-starts_at")[:8],
        "evolutions": patient.clinical_evolutions.select_related("professional").order_by("-date", "-time")[:6],
        "documents": patient.documents.select_related("uploaded_by").order_by("-created_at")[:6],
        "incidents": patient.incidents.select_related("professional").order_by("-date", "-time")[:6],
        "assessments": patient.clinical_assessments.select_related("template", "professional").order_by("-performed_at")[:6],
    }
    return render(request, "patients/patient_detail.html", context)
