from django.db.models.signals import post_save
from django.dispatch import receiver
from Core.models import UserCredit
from .models import Affiliate

@receiver(post_save, sender=Affiliate)
def update_user_credit(sender, instance, created, **kwargs):
    if created:
        user_credit, _ = UserCredit.objects.get_or_create(user=instance.user)
        user_credit.is_affiliate = True
        user_credit.save()