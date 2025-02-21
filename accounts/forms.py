from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Obrigatório. Insira um email válido.")

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]