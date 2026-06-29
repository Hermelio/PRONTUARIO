from django.http import JsonResponse
from django.shortcuts import redirect, render


def home_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:portal")
    return render(request, "core/home.html")


def healthcheck_view(request):
    return JsonResponse({"status": "ok"})
