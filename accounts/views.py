from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from Core.models import UserCredit


def home(request):
    return render(request, 'accounts/home.html')

# View para cadastro de usuário
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()  # Cria o usuário
            username = form.cleaned_data.get('username')
            messages.success(request, f'Conta criada com sucesso para {username}!')
            return redirect('/')  # Redireciona para a página de login
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

# View para login de usuário
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)  # Faz o login
                messages.success(request, f'Bem-vindo, {username}!')
                return redirect('/')  # Redireciona para a página inicial
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

# View para logout de usuário
def user_logout(request):
    logout(request)  # Faz o logout
    messages.success(request, 'Você foi desconectado com sucesso.')
    return redirect('/')  # Redireciona para a página inicial