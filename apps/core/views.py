from django.http import JsonResponse
from django.shortcuts import render


def home_view(request):
    return render(request, "core/home.html")


def healthcheck_view(request):
    return JsonResponse({"status": "ok"})
