from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserCredit

@receiver(post_save, sender=User)
def create_user_credit(sender, instance, created, **kwargs):
    """Cria um registro na UserCredit para cada novo usuário."""
    if created:
        UserCredit.objects.create(user=instance)
