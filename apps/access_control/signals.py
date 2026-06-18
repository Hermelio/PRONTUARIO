from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import AccessProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_access_profile(sender, instance, created, **kwargs):
    if created:
        AccessProfile.objects.get_or_create(user=instance)
