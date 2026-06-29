from .views import build_app_navigation, role_label


def app_navigation(request):
    if not request.user.is_authenticated:
        return {}
    return {
        "app_nav_items": build_app_navigation(request.user),
        "app_role_label": role_label(request.user),
    }
