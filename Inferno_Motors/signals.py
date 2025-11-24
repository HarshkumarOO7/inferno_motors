# Inferno_Motors/signals.py
from django.db import IntegrityError
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from .models import userdetails

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_details(sender, instance, created, **kwargs):
    """
    Ensure a corresponding userdetails exists for each User.
    Use get_or_create to avoid UNIQUE constraint errors if a record already exists.
    Do NOT pass a 'password' kwarg here — AbstractBaseUser handles passwords.
    """
    email = getattr(instance, "email", None)
    if not email:
        return

    # Build a reasonable default name
    default_name = None
    try:
        default_name = instance.get_full_name() if callable(getattr(instance, "get_full_name", None)) else None
    except Exception:
        default_name = None
    if not default_name:
        default_name = getattr(instance, "username", "") or email

    try:
        userdetails.objects.get_or_create(
            email=email,
            defaults={
                "name": default_name,
                "contact": ""
            },
        )
    except IntegrityError:
        # Race condition or other DB issue — ignore or log as needed
        pass
