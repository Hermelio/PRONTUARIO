from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from apps.patients.models import Patient

from .forms import ClinicalEvolutionForm, ClinicalEvolutionSearchForm
from .models import ClinicalEvolution


def patient_record_view(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
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
        "new_evolution_url": reverse("medical_records:evolution_create", args=[patient.pk]),
    }
    return render(request, "medical_records/patient_record.html", context)


def clinical_evolution_create_view(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    if request.method == "POST":
        form = ClinicalEvolutionForm(request.POST)
        form.fields["appointment"].queryset = patient.appointments.all()
        if form.is_valid():
            evolution = form.save(commit=False)
            evolution.patient = patient
            evolution.save()
            return redirect("medical_records:patient_record", patient_id=patient.pk)
    else:
        form = ClinicalEvolutionForm()
        form.fields["appointment"].queryset = patient.appointments.all()

    return render(request, "medical_records/evolution_form.html", {"patient": patient, "form": form})
