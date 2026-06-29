from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from apps.access_control.models import AccessProfile
from apps.patients.models import Patient
from apps.scheduling.models import Appointment

from .forms import ClinicalEvolutionForm, ClinicalEvolutionSearchForm


def _access_profile(user):
    return getattr(user, "access_profile", None)


def _can_access_medical_records(user):
    profile = _access_profile(user)
    return user.is_superuser or (profile and profile.can_access_module("medical_records"))


def _patient_queryset_for_user(user):
    queryset = Patient.objects.select_related("assigned_professional")
    profile = _access_profile(user)
    if user.is_superuser or not profile:
        return queryset
    if profile.role == AccessProfile.Role.PROFESSIONAL and profile.professional_id:
        return queryset.filter(assigned_professional=profile.professional)
    if profile.can_access_module("medical_records"):
        return queryset
    return queryset.none()


def _ensure_patient_access(user, patient):
    profile = _access_profile(user)
    if user.is_superuser:
        return
    if not profile or not profile.can_access_patient(patient):
        raise PermissionDenied("Voce nao tem acesso ao prontuario deste paciente.")


def _configure_evolution_form(form, patient, user):
    profile = _access_profile(user)
    form.fields["appointment"].queryset = patient.appointments.select_related("professional").order_by("-date", "-starts_at")
    if profile and profile.role == AccessProfile.Role.PROFESSIONAL and profile.professional_id:
        form.fields["professional"].queryset = form.fields["professional"].queryset.filter(pk=profile.professional_id)
        form.fields["professional"].initial = profile.professional
        form.fields["appointment"].queryset = form.fields["appointment"].queryset.filter(professional=profile.professional)


@login_required
def medical_record_index_view(request):
    if not _can_access_medical_records(request.user):
        raise PermissionDenied("Voce nao tem acesso ao modulo de prontuario.")

    query = request.GET.get("q", "").strip()
    patients = _patient_queryset_for_user(request.user).annotate(
        evolution_count=Count("clinical_evolutions", distinct=True),
        assessment_count=Count("clinical_assessments", distinct=True),
        incident_count=Count("incidents", distinct=True),
    )
    if query:
        patients = patients.filter(
            Q(full_name__icontains=query)
            | Q(cpf__icontains=query)
            | Q(primary_diagnosis__icontains=query)
            | Q(assigned_professional__full_name__icontains=query)
        )

    context = {
        "patients": patients,
        "query": query,
        "total_patients": patients.count(),
        "with_evolutions": patients.filter(evolution_count__gt=0).count(),
        "without_evolutions": patients.filter(evolution_count=0).count(),
    }
    return render(request, "medical_records/index.html", context)


@login_required
def patient_record_view(request, patient_id):
    if not _can_access_medical_records(request.user):
        raise PermissionDenied("Voce nao tem acesso ao modulo de prontuario.")

    patient = get_object_or_404(_patient_queryset_for_user(request.user), pk=patient_id)
    _ensure_patient_access(request.user, patient)
    form = ClinicalEvolutionSearchForm(request.GET or None)
    evolutions = patient.clinical_evolutions.select_related("professional", "appointment")

    if form.is_valid():
        query = form.cleaned_data.get("q")
        professional = form.cleaned_data.get("professional")
        start_date = form.cleaned_data.get("start_date")
        end_date = form.cleaned_data.get("end_date")

        if query:
            evolutions = evolutions.filter(
                Q(service_description__icontains=query)
                | Q(procedures_performed__icontains=query)
                | Q(conduct__icontains=query)
                | Q(notes__icontains=query)
            )
        if professional:
            evolutions = evolutions.filter(professional__full_name__icontains=professional)
        if start_date:
            evolutions = evolutions.filter(date__gte=start_date)
        if end_date:
            evolutions = evolutions.filter(date__lte=end_date)

    context = {
        "patient": patient,
        "form": form,
        "evolutions": evolutions,
        "evolution_count": patient.clinical_evolutions.count(),
        "assessment_count": patient.clinical_assessments.count(),
        "document_count": patient.documents.count(),
        "incident_count": patient.incidents.count(),
        "appointment_count": patient.appointments.count(),
        "last_evolution": patient.clinical_evolutions.select_related("professional").first(),
        "latest_assessment": patient.clinical_assessments.select_related("template", "professional").first(),
        "last_incident": patient.incidents.select_related("professional").first(),
        "next_appointment": (
            patient.appointments
            .select_related("professional")
            .filter(date__gte=timezone.localdate())
            .exclude(status=Appointment.Status.CANCELED)
            .order_by("date", "starts_at")
            .first()
        ),
        "new_evolution_url": reverse("medical_records:evolution_create", args=[patient.pk]),
    }
    return render(request, "medical_records/patient_record.html", context)


@login_required
def clinical_evolution_create_view(request, patient_id):
    if not _can_access_medical_records(request.user):
        raise PermissionDenied("Voce nao tem acesso ao modulo de prontuario.")

    patient = get_object_or_404(_patient_queryset_for_user(request.user), pk=patient_id)
    _ensure_patient_access(request.user, patient)
    if request.method == "POST":
        form = ClinicalEvolutionForm(request.POST)
        _configure_evolution_form(form, patient, request.user)
        if form.is_valid():
            evolution = form.save(commit=False)
            evolution.patient = patient
            evolution.save()
            return redirect("medical_records:patient_record", patient_id=patient.pk)
    else:
        form = ClinicalEvolutionForm(initial={"date": timezone.localdate(), "time": timezone.localtime().time()})
        _configure_evolution_form(form, patient, request.user)

    return render(request, "medical_records/evolution_form.html", {"patient": patient, "form": form})
