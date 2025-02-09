from datetime import timezone
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .models import Affiliate, Referral, Withdrawal
from django.contrib.admin.views.decorators import staff_member_required
from decimal import Decimal



MIN_WITHDRAWAL = 10  # Valor mínimo para saque
WITHDRAWAL_FEE = 0.05  # Taxa de 5%


def home(request):
    return render(request, 'accounts/home.html')

# View para cadastro de usuário
def register(request):
    ip_address = request.META.get("REMOTE_ADDR")
    ref_code = request.GET.get("ref")
    affiliate = None
    if ref_code:
        affiliate = get_object_or_404(Affiliate, referral_code=ref_code)

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Cria o usuário
            username = form.cleaned_data.get('username')

            if affiliate:
                Referral.objects.create(affiliate=affiliate,ip_address=ip_address,referred_user=user)
                affiliate.total_commission += 10  # Exemplo de comissão fixa
                affiliate.save()

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


@login_required
def request_withdrawal(request):
    affiliate = Affiliate.objects.get(user=request.user)

    if request.method == "POST":
        amount = Decimal(request.POST["amount"])  # Convertendo para Decimal
        pix_key = request.POST["pix_key"]

        if amount < Decimal(MIN_WITHDRAWAL):  # Convertendo para Decimal
            messages.error(request, f"O valor mínimo para saque é R$ {MIN_WITHDRAWAL:.2f}")
            return redirect("Accounts:request_withdrawal")

        if amount > affiliate.total_commission:
            messages.error(request, "Saldo insuficiente para saque.")
            return redirect("Accounts:request_withdrawal")

        # Aplicar taxa de saque
        amount_after_fee = amount * (Decimal(1) - Decimal(WITHDRAWAL_FEE))

        # Criar solicitação de saque
        Withdrawal.objects.create(
            affiliate=affiliate,
            amount=amount_after_fee,
            pix_key=pix_key
        )

        # Deduzir saldo do afiliado
        affiliate.total_commission -= amount  # Agora os tipos são compatíveis
        affiliate.save()

        messages.success(request, f"Saque solicitado com sucesso! Valor líquido: R$ {amount_after_fee:.2f}")
        return redirect("Accounts:request_withdrawal")

    return render(request, "accounts/painel.html", {"affiliate": affiliate})


@staff_member_required
def manage_withdrawals(request):
    withdrawals = Withdrawal.objects.all().order_by("-requested_at")
    return render(request, "accounts/manage_withdrawals.html", {"withdrawals": withdrawals,
                                                                })


@staff_member_required
def approve_withdrawal(request, withdrawal_id):
    withdrawal = get_object_or_404(Withdrawal, id=withdrawal_id)

    if withdrawal.status == "Pendente":
        withdrawal.status = "Aprovado"
        withdrawal.processed_at = timezone.now()
        withdrawal.save()
        messages.success(request, "Saque aprovado com sucesso!")
    else:
        messages.error(request, "Este saque já foi processado.")

    return redirect("/manage_withdrawals")

@staff_member_required
def deny_withdrawal(request, withdrawal_id):
    withdrawal = get_object_or_404(Withdrawal, id=withdrawal_id)

    if withdrawal.status == "Pendente":
        withdrawal.status = "Recusado"
        withdrawal.processed_at = timezone.now()
        if withdrawal.affiliate:
            withdrawal.affiliate.total_commission += withdrawal.amount  # Devolve o saldo
            withdrawal.affiliate.save()
        withdrawal.save()
        messages.error(request, "Saque recusado.")
    else:
        messages.error(request, "Este saque já foi processado.")

    return redirect("/manage_withdrawals")