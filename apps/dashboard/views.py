from django.shortcuts import render

from .services import build_dashboard_summary


def dashboard_view(request):
    return render(request, "dashboard/index.html", {"summary": build_dashboard_summary()})
