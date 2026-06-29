from collections import defaultdict
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.access_control.models import AccessProfile
from apps.patients.models import Patient

from .forms import AssessmentSearchForm, ClinicalAssessmentForm, MetricEntryForm, default_performed_at
from .models import AssessmentMetric, AssessmentTemplate


def _access_profile(user):
    return getattr(user, "access_profile", None)


def _can_access_assessments(user):
    profile = _access_profile(user)
    return user.is_superuser or (profile and profile.can_access_module("assessments"))


def _patient_queryset_for_user(user):
    queryset = Patient.objects.select_related("assigned_professional")
    profile = _access_profile(user)
    if user.is_superuser or not profile:
        return queryset
    if profile.role == AccessProfile.Role.PROFESSIONAL and profile.professional_id:
        return queryset.filter(assigned_professional=profile.professional)
    if profile.can_access_module("assessments"):
        return queryset
    return queryset.none()


def _ensure_patient_access(user, patient):
    profile = _access_profile(user)
    if user.is_superuser:
        return
    if not profile or not profile.can_access_patient(patient):
        raise PermissionDenied("Voce nao tem acesso as avaliacoes deste paciente.")


def _professional_for_user(user):
    profile = _access_profile(user)
    if profile and profile.role == AccessProfile.Role.PROFESSIONAL and profile.professional_id:
        return profile.professional
    return None


def _percent_variation(previous, current):
    if previous in (None, Decimal("0")) or current is None:
        return None
    return ((current - previous) / previous * Decimal("100")).quantize(Decimal("0.01"))


def build_patient_indicator_context(patient):
    assessments = (
        patient.clinical_assessments
        .select_related("template", "professional")
        .prefetch_related("metrics")
        .order_by("performed_at")
    )
    series = defaultdict(list)
    comparisons = []

    for assessment in assessments:
        for metric in assessment.metrics.all():
            if metric.numeric_value is None:
                continue
            series[metric.name].append({
                "date": assessment.performed_at.date().isoformat(),
                "value": float(metric.numeric_value),
                "unit": metric.unit,
                "higher_is_better": metric.higher_is_better,
                "assessment": str(assessment.template),
            })

    for metric_name, points in series.items():
        if len(points) < 2:
            continue
        previous = Decimal(str(points[-2]["value"]))
        current = Decimal(str(points[-1]["value"]))
        variation = _percent_variation(previous, current)
        if variation is None:
            continue
        higher_is_better = points[-1]["higher_is_better"]
        improved = variation >= 0 if higher_is_better else variation <= 0
        comparisons.append({
            "metric": metric_name,
            "previous": previous,
            "current": current,
            "variation_percent": variation,
            "improved": improved,
            "unit": points[-1]["unit"],
        })

    chart_labels = sorted({point["date"] for points in series.values() for point in points})
    chart_datasets = []
    for metric_name, points in series.items():
        values_by_date = {point["date"]: point["value"] for point in points}
        chart_datasets.append({
            "label": metric_name,
            "data": [values_by_date.get(label) for label in chart_labels],
        })

    return {
        "assessments": assessments,
        "series": dict(series),
        "comparisons": comparisons,
        "chart_data": {
            "labels": chart_labels,
            "datasets": chart_datasets,
        },
    }


@login_required
def assessment_index_view(request):
    if not _can_access_assessments(request.user):
        raise PermissionDenied("Voce nao tem acesso ao modulo de avaliacoes.")

    form = AssessmentSearchForm(request.GET or None)
    patients = _patient_queryset_for_user(request.user).annotate(
        assessment_count=Count("clinical_assessments", distinct=True),
        metric_count=Count("clinical_assessments__metrics", distinct=True),
        evolution_count=Count("clinical_evolutions", distinct=True),
    )
    if form.is_valid():
        query = form.cleaned_data.get("q")
        if query:
            patients = patients.filter(
                Q(full_name__icontains=query)
                | Q(cpf__icontains=query)
                | Q(primary_diagnosis__icontains=query)
                | Q(assigned_professional__full_name__icontains=query)
            )

    context = {
        "form": form,
        "patients": patients,
        "total_patients": patients.count(),
        "with_assessments": patients.filter(assessment_count__gt=0).count(),
        "without_assessments": patients.filter(assessment_count=0).count(),
        "template_count": AssessmentTemplate.objects.filter(is_active=True).count(),
    }
    return render(request, "assessments/index.html", context)


@login_required
def patient_assessments_view(request, patient_id):
    if not _can_access_assessments(request.user):
        raise PermissionDenied("Voce nao tem acesso ao modulo de avaliacoes.")

    patient = get_object_or_404(_patient_queryset_for_user(request.user), pk=patient_id)
    _ensure_patient_access(request.user, patient)
    context = build_patient_indicator_context(patient)
    context.update({
        "patient": patient,
        "latest_assessment": patient.clinical_assessments.select_related("template", "professional").first(),
        "template_count": AssessmentTemplate.objects.filter(is_active=True).count(),
    })
    return render(request, "assessments/patient_assessments.html", context)


@login_required
def assessment_create_view(request, patient_id):
    if not _can_access_assessments(request.user):
        raise PermissionDenied("Voce nao tem acesso ao modulo de avaliacoes.")

    patient = get_object_or_404(_patient_queryset_for_user(request.user), pk=patient_id)
    _ensure_patient_access(request.user, patient)
    professional = _professional_for_user(request.user)

    selected_template = None
    template_id = request.POST.get("template") or request.GET.get("template")
    if template_id:
        selected_template = get_object_or_404(AssessmentTemplate.objects.prefetch_related("fields"), pk=template_id, is_active=True)
    else:
        selected_template = AssessmentTemplate.objects.filter(is_active=True).prefetch_related("fields").first()

    form_kwargs = {"professional": professional}
    metric_kwargs = {"template": selected_template}
    if request.method == "POST":
        form = ClinicalAssessmentForm(request.POST, **form_kwargs)
        metric_form = MetricEntryForm(request.POST, **metric_kwargs)
        if form.is_valid() and metric_form.is_valid():
            assessment = form.save(commit=False)
            assessment.patient = patient
            assessment.save()
            metrics = [
                AssessmentMetric(assessment=assessment, **metric_data)
                for metric_data in metric_form.iter_metric_values()
            ]
            AssessmentMetric.objects.bulk_create(metrics)
            return redirect("assessments:patient_assessments", patient_id=patient.pk)
    else:
        form = ClinicalAssessmentForm(
            initial={"template": selected_template, "performed_at": default_performed_at()},
            **form_kwargs,
        )
        metric_form = MetricEntryForm(**metric_kwargs)

    return render(request, "assessments/assessment_form.html", {
        "patient": patient,
        "form": form,
        "metric_form": metric_form,
        "selected_template": selected_template,
    })


def patient_indicators_view(request, patient_id):
    return patient_assessments_view(request, patient_id)
