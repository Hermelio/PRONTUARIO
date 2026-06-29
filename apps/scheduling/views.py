import calendar
from collections import defaultdict
from datetime import timedelta
from urllib.parse import urlencode

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.utils import timezone

from apps.access_control.models import AccessProfile

from .forms import ScheduleFilterForm
from .models import Appointment


def _access_profile(user):
    return getattr(user, "access_profile", None)


def _can_access_schedule(user):
    profile = _access_profile(user)
    return user.is_superuser or (profile and profile.can_access_module("scheduling"))


def _can_view_all_professionals(user):
    profile = _access_profile(user)
    return user.is_superuser or (
        profile and profile.role in {AccessProfile.Role.ADMIN, AccessProfile.Role.COORDINATOR}
    )


def _appointment_queryset_for_user(user):
    queryset = Appointment.objects.select_related("patient", "professional").order_by("date", "starts_at")
    profile = _access_profile(user)
    if user.is_superuser or not profile:
        return queryset
    if profile.role == AccessProfile.Role.PROFESSIONAL:
        if profile.professional_id:
            return queryset.filter(professional=profile.professional)
        return queryset.none()
    if profile.can_access_module("scheduling"):
        return queryset
    return queryset.none()


def _date_range_for_view(view_mode, selected_date):
    if view_mode == "day":
        return selected_date, selected_date
    if view_mode == "month":
        _, last_day = calendar.monthrange(selected_date.year, selected_date.month)
        return selected_date.replace(day=1), selected_date.replace(day=last_day)
    week_start = selected_date - timedelta(days=selected_date.weekday())
    return week_start, week_start + timedelta(days=6)


def _navigation_url(request, target_date, view_mode):
    params = request.GET.copy()
    params["date"] = target_date.isoformat()
    params["view"] = view_mode
    return f"?{urlencode(params, doseq=True)}"


def _appointment_card(appointment):
    patient = appointment.patient
    return {
        "appointment": appointment,
        "patient": patient,
        "professional": appointment.professional,
        "address": ", ".join(
            part
            for part in [
                patient.street,
                patient.number,
                patient.neighborhood,
                patient.city,
                patient.state,
            ]
            if part
        ),
        "maps_url": patient.google_maps_url,
        "route_url": patient.route_url,
        "has_location": patient.latitude is not None and patient.longitude is not None,
    }


def _build_week_columns(start_date, appointments):
    grouped = defaultdict(list)
    for appointment in appointments:
        grouped[appointment.date].append(_appointment_card(appointment))
    return [
        {
            "date": start_date + timedelta(days=offset),
            "appointments": grouped[start_date + timedelta(days=offset)],
            "is_today": start_date + timedelta(days=offset) == timezone.localdate(),
        }
        for offset in range(7)
    ]


def _build_month_weeks(selected_date, appointments):
    grouped = defaultdict(list)
    for appointment in appointments:
        grouped[appointment.date].append(_appointment_card(appointment))

    month_calendar = calendar.Calendar(firstweekday=0)
    weeks = []
    for week in month_calendar.monthdatescalendar(selected_date.year, selected_date.month):
        weeks.append([
            {
                "date": day,
                "appointments": grouped[day],
                "in_month": day.month == selected_date.month,
                "is_today": day == timezone.localdate(),
            }
            for day in week
        ])
    return weeks


def _professional_board(appointments):
    grouped = defaultdict(list)
    for appointment in appointments:
        grouped[appointment.professional].append(_appointment_card(appointment))
    return [
        {
            "professional": professional,
            "appointments": cards,
            "total": len(cards),
        }
        for professional, cards in sorted(grouped.items(), key=lambda item: item[0].full_name)
    ]


@login_required
def schedule_view(request):
    if not _can_access_schedule(request.user):
        raise PermissionDenied("Voce nao tem acesso ao modulo de agenda.")

    allow_professional_filter = _can_view_all_professionals(request.user)
    today = timezone.localdate()
    form = ScheduleFilterForm(
        request.GET or None,
        allow_professional_filter=allow_professional_filter,
        initial={"date": today, "view": "week"},
    )

    selected_date = today
    view_mode = "week"
    status = ""
    professional = None
    if form.is_valid():
        selected_date = form.cleaned_data.get("date") or today
        view_mode = form.cleaned_data.get("view") or "week"
        status = form.cleaned_data.get("status") or ""
        professional = form.cleaned_data.get("professional") if allow_professional_filter else None

    start_date, end_date = _date_range_for_view(view_mode, selected_date)
    appointments = _appointment_queryset_for_user(request.user).filter(date__range=(start_date, end_date))
    if status:
        appointments = appointments.filter(status=status)
    if professional:
        appointments = appointments.filter(professional=professional)

    appointment_list = list(appointments)
    if view_mode == "day":
        previous_date = selected_date - timedelta(days=1)
        next_date = selected_date + timedelta(days=1)
    elif view_mode == "month":
        previous_date = (selected_date.replace(day=1) - timedelta(days=1)).replace(day=1)
        next_date = (selected_date.replace(day=28) + timedelta(days=4)).replace(day=1)
    else:
        previous_date = selected_date - timedelta(days=7)
        next_date = selected_date + timedelta(days=7)

    visible_scope = _appointment_queryset_for_user(request.user)
    context = {
        "form": form,
        "view_mode": view_mode,
        "selected_date": selected_date,
        "start_date": start_date,
        "end_date": end_date,
        "appointments": [_appointment_card(appointment) for appointment in appointment_list],
        "week_columns": _build_week_columns(start_date, appointment_list),
        "month_weeks": _build_month_weeks(selected_date, appointment_list) if view_mode == "month" else [],
        "professional_board": _professional_board(appointment_list),
        "allow_professional_filter": allow_professional_filter,
        "total_appointments": len(appointment_list),
        "confirmed_count": sum(1 for appointment in appointment_list if appointment.status == Appointment.Status.CONFIRMED),
        "in_progress_count": sum(1 for appointment in appointment_list if appointment.status == Appointment.Status.IN_PROGRESS),
        "completed_count": sum(1 for appointment in appointment_list if appointment.status == Appointment.Status.COMPLETED),
        "mapped_count": sum(1 for appointment in appointment_list if appointment.patient.google_maps_url),
        "today_count": visible_scope.filter(date=today).exclude(status=Appointment.Status.CANCELED).count(),
        "previous_url": _navigation_url(request, previous_date, view_mode),
        "next_url": _navigation_url(request, next_date, view_mode),
        "today_url": _navigation_url(request, today, view_mode),
    }
    return render(request, "scheduling/schedule.html", context)
