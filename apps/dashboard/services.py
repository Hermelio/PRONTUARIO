from datetime import timedelta
from decimal import Decimal

from django.db.models import Avg, Sum
from django.utils import timezone

from apps.assessments.models import AssessmentMetric
from apps.attendance.models import AttendanceRecord
from apps.finance.models import FinancialEntry
from apps.patients.models import Patient
from apps.professionals.models import Professional
from apps.scheduling.models import Appointment


def _money(value):
    return value or Decimal("0.00")


def build_dashboard_summary(today=None):
    today = today or timezone.localdate()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    year_start = today.replace(month=1, day=1)

    monthly_entries = FinancialEntry.objects.filter(reference_date__gte=month_start).exclude(
        status=FinancialEntry.Status.CANCELED
    )
    annual_entries = FinancialEntry.objects.filter(reference_date__gte=year_start).exclude(
        status=FinancialEntry.Status.CANCELED
    )
    pending_entries = FinancialEntry.objects.filter(status=FinancialEntry.Status.PENDING)
    paid_entries = FinancialEntry.objects.filter(status=FinancialEntry.Status.PAID)

    assessment_average = AssessmentMetric.objects.filter(numeric_value__isnull=False).aggregate(
        average=Avg("numeric_value")
    )["average"]

    return {
        "patients": {
            "total": Patient.objects.count(),
            "active": Patient.objects.filter(status=Patient.Status.ACTIVE).count(),
            "inactive": Patient.objects.filter(status=Patient.Status.INACTIVE).count(),
            "new": Patient.objects.filter(created_at__date__gte=month_start).count(),
            "mapped": Patient.objects.filter(latitude__isnull=False, longitude__isnull=False).count(),
        },
        "professionals": {
            "total": Professional.objects.count(),
            "active": Professional.objects.filter(status=Professional.Status.ACTIVE).count(),
            "inactive": Professional.objects.filter(status=Professional.Status.INACTIVE).count(),
            "in_attendance": AttendanceRecord.objects.filter(
                check_in_at__date=today,
                check_out_at__isnull=True,
                check_in_allowed=True,
            ).count(),
        },
        "appointments": {
            "today": Appointment.objects.filter(date=today).count(),
            "week": Appointment.objects.filter(date__gte=week_start, date__lte=today + timedelta(days=6)).count(),
            "month": Appointment.objects.filter(date__gte=month_start).count(),
            "pending": Appointment.objects.filter(
                status__in=[Appointment.Status.SCHEDULED, Appointment.Status.CONFIRMED]
            ).count(),
            "completed": Appointment.objects.filter(status=Appointment.Status.COMPLETED).count(),
        },
        "finance": {
            "monthly_revenue": _money(monthly_entries.aggregate(total=Sum("total_amount"))["total"]),
            "annual_revenue": _money(annual_entries.aggregate(total=Sum("total_amount"))["total"]),
            "receivable": _money(pending_entries.aggregate(total=Sum("total_amount"))["total"]),
            "paid": _money(paid_entries.aggregate(total=Sum("professional_amount"))["total"]),
        },
        "assessments": {
            "average_evolution": assessment_average or Decimal("0.00"),
            "clinical_indicators": AssessmentMetric.objects.values("name").distinct().count(),
        },
        "map": {
            "patients": Patient.objects.filter(latitude__isnull=False, longitude__isnull=False).count(),
            "appointments_today": Appointment.objects.filter(date=today).count(),
            "professionals_in_attendance": AttendanceRecord.objects.filter(
                check_in_at__date=today,
                check_out_at__isnull=True,
                check_in_allowed=True,
            ).count(),
        },
    }
