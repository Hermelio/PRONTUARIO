from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def build_app_navigation(user):
    profile = getattr(user, "access_profile", None)
    items = []
    if user.is_superuser or (profile and profile.can_access_module("dashboard")):
        items.append({"title": "Dashboard", "description": "Indicadores gerais da operacao.", "url": "/dashboard/", "icon": "bi-speedometer2"})
    if user.is_superuser or (profile and profile.can_access_module("patients")):
        items.append({"title": "Pacientes", "description": "Cadastro e acompanhamento de pacientes.", "url": "/pacientes/", "icon": "bi-person-heart"})
    if user.is_superuser or (profile and profile.can_access_module("scheduling")):
        items.append({"title": "Agenda", "description": "Atendimentos, recorrencias, rotas e status.", "url": "/agenda/", "icon": "bi-calendar-week"})
    if user.is_superuser or (profile and profile.can_access_module("medical_records")):
        items.append({"title": "Prontuario", "description": "Evolucoes clinicas e historico.", "url": "/prontuario/", "icon": "bi-file-earmark-medical"})
    if user.is_superuser or (profile and profile.can_access_module("assessments")):
        items.append({"title": "Avaliacoes", "description": "Indicadores e comparativos clinicos.", "url": "/avaliacoes/", "icon": "bi-clipboard2-pulse"})
    if user.is_superuser or (profile and profile.can_access_module("finance")):
        items.append({"title": "Financeiro", "description": "Recebimentos, repasses e fechamento.", "url": "/admin/finance/financialentry/", "icon": "bi-cash-coin"})
    return items


def role_label(user):
    profile = getattr(user, "access_profile", None)
    if user.is_superuser:
        return "Administrador"
    if profile:
        return profile.get_role_display()
    return "Profissional"


@login_required
def portal_view(request):
    profile = getattr(request.user, "access_profile", None)
    role = profile.role if profile else "admin" if request.user.is_superuser else "professional"
    cards = build_app_navigation(request.user)

    return render(request, "accounts/portal.html", {"profile": profile, "role": role, "cards": cards})
