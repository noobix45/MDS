from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Utilizator, AuthUser


@receiver(post_save, sender=User)
def create_utilizator(sender, instance, created, **kwargs):
    if created:
        Utilizator.objects.create(user=instance,email=instance.email)