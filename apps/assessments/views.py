from collections import defaultdict
from decimal import Decimal

from django.shortcuts import get_object_or_404, render

from apps.patients.models import Patient


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


def patient_indicators_view(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    context = build_patient_indicator_context(patient)
    context["patient"] = patient
    return render(request, "assessments/patient_indicators.html", context)
