from django.db import models
import uuid
from django.contrib.auth.models import User

class UserCredit(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_affiliate = models.BooleanField(default=False) 
    credits = models.IntegerField(default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    level = models.IntegerField(default=1)
    max_credits = models.IntegerField(default=0)
    total_bet = models.IntegerField(default=0)
    total_won = models.IntegerField(default=0)

    def update_stats(self, bet_amount, won_amount):
        self.total_bet += bet_amount
        self.total_won += won_amount
        self.credits = min(self.credits, self.max_credits)
        self.save()

    def apply_casino_margin(self, bet_amount):
        # Aplica a margem de lucro do cassino (10%)
        casino_margin = int(bet_amount * 0.10)
        self.credits -= casino_margin
        self.save()
        return casino_margin

    def __str__(self):
        return f"{self.user.username} - {self.credits} créditos - R$ {self.balance} - Nível {self.level}"

    class Meta:
        verbose_name_plural = "Creditos"


class TransactionHistory(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Depósito'),
        ('withdrawal', 'Saque'),
        ('bonus', 'Bônus'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    credits = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=[("Aprovado", "Aprovado"), ("Pendente", "Pendente"), ("Recusado", "Recusado")])
    created_at = models.DateTimeField(auto_now_add=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - R$ {self.amount}"

    class Meta:
        verbose_name_plural = "Historico de transaçoes"

