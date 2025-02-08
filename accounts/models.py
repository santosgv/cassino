from django.db import models
from django.contrib.auth.models import User
import uuid

class Affiliate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    referral_code = models.UUIDField(default=uuid.uuid4, unique=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=10)  # Percentual de comissão
    total_commission = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class Referral(models.Model):
    affiliate = models.ForeignKey(Affiliate, on_delete=models.CASCADE)
    referred_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="referred_users", null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)  # Para rastrear acessos
    created_at = models.DateTimeField(auto_now_add=True)


class Withdrawal(models.Model):
    affiliate = models.ForeignKey(Affiliate, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=[("Pendente", "Pendente"), ("Aprovado", "Aprovado"), ("Recusado", "Recusado")],
        default="Pendente"
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)