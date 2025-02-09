from django.db import models
from django.contrib.auth.models import User
import uuid

class Affiliate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    referral_code = models.UUIDField(default=uuid.uuid4, unique=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=5)  # Percentual de comissão
    total_commission = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    referral_link = models.URLField(blank=True)

    def save(self, *args, **kwargs):
        if not self.referral_link:  # Evita sobrescrever caso já tenha sido gerado
            self.referral_link = f"http://0.0.0.0:5000/register?ref={self.referral_code}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Afiliado: {self.user.username}"

class Referral(models.Model):
    affiliate = models.ForeignKey(Affiliate, on_delete=models.CASCADE,related_name="referrals")
    referred_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)  # Para rastrear acessos
    created_at = models.DateTimeField(auto_now_add=True)

class Withdrawal(models.Model):
    affiliate = models.ForeignKey(Affiliate, on_delete=models.CASCADE,null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,  
        choices=[("Pendente", "Pendente"), ("Aprovado", "Aprovado"), ("Recusado", "Recusado"), ('paid', 'Pago')],
        default="Pendente"
    )
    pix_key = models.CharField(max_length=150,null=True, blank=True)
    transaction_id = models.UUIDField(default=uuid.uuid4, unique=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

