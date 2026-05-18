from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.auth_system.models import User

from .services import ensure_user_subscription


@receiver(post_save, sender=User)
def create_default_subscription(sender, instance, created, **kwargs):
    if created:
        ensure_user_subscription(instance)
