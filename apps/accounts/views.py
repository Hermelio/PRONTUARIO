from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def portal_view(request):
    profile = getattr(request.user, "access_profile", None)
    role = profile.role if profile else "admin" if request.user.is_superuser else "professional"

    cards = []
    if request.user.is_superuser or (profile and profile.can_access_module("dashboard")):
        cards.append({"title": "Dashboard", "description": "Indicadores gerais da operacao.", "url": "/dashboard/", "icon": "bi-speedometer2"})
    if request.user.is_superuser or (profile and profile.can_access_module("patients")):
        cards.append({"title": "Pacientes", "description": "Cadastro e acompanhamento de pacientes.", "url": "/pacientes/", "icon": "bi-person-heart"})
    if request.user.is_superuser or (profile and profile.can_access_module("scheduling")):
        cards.append({"title": "Agenda", "description": "Atendimentos, recorrencias, rotas e status.", "url": "/agenda/", "icon": "bi-calendar-week"})
    if request.user.is_superuser or (profile and profile.can_access_module("medical_records")):
        cards.append({"title": "Prontuario", "description": "Evolucoes clinicas e historico.", "url": "/prontuario/", "icon": "bi-file-earmark-medical"})
    if request.user.is_superuser or (profile and profile.can_access_module("assessments")):
        cards.append({"title": "Avaliacoes", "description": "Indicadores e comparativos clinicos.", "url": "/avaliacoes/", "icon": "bi-clipboard2-pulse"})
    if request.user.is_superuser or (profile and profile.can_access_module("finance")):
        cards.append({"title": "Financeiro", "description": "Recebimentos, repasses e fechamento.", "url": "/admin/finance/financialentry/", "icon": "bi-cash-coin"})

    return render(request, "accounts/portal.html", {"profile": profile, "role": role, "cards": cards})
