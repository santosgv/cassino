from django.db import models
from django.contrib.auth.models import User

class UserCredit(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    credits = models.IntegerField(default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    level = models.IntegerField(default=1)  # Adicionando um nível inicial

    def __str__(self):
        return f"{self.user.username} - {self.credits} créditos - R$ {self.balance} - Nível {self.level}"