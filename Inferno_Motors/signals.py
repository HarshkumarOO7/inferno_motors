from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import *

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_details(sender, instance, created, **kwargs):
    if created:
        # Save user details from Google OAuth
        userdetails.objects.create(
            name=instance.get_full_name() or instance.username,
            email=instance.email,
            password='',  # No password for Google OAuth users
            contact=''  # Optional
        )