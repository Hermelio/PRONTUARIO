from django.contrib import admin

from .models import AccessProfile


@admin.register(AccessProfile)
class AccessProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "professional", "created_at")
    list_filter = ("role",)
    search_fields = ("user__username", "user__email", "professional__full_name")
    autocomplete_fields = ("professional",)
