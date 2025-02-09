from django.shortcuts import render,redirect
from django.http import JsonResponse
import random
from django.contrib.auth.decorators import login_required
from .models import UserCredit,TransactionHistory
from accounts.models import Withdrawal
from django.contrib import messages
import mercadopago
from decimal import Decimal
from django.conf import settings


MIN_WITHDRAWAL = 5

# Lista dos pacotes disponíveis
PACKAGES = {
    "starter": {"name": "🟢 Starter Pack", "credits": 20, "price": 10.00, "bonus": 0, "color": "success"},
    "pro": {"name": "🔵 Pro Player", "credits": 100, "price": 50.00, "bonus": 50, "color": "primary"},
    "high_roller": {"name": "🔴 High Roller", "credits": 200, "price": 100.00, "bonus": 100, "color": "danger"},
    "vip": {"name": "🔥 VIP Pack", "credits": 500, "price": 250.00, "bonus": 250, "color": "warning"},
    "super_vip": {"name": " 💎Super VIP", "credits": 1000, "price": 500.00, "bonus": 300, "color": "info"},
}


@login_required(login_url='/login/')  
def jogo(request):
    user_credit,created = UserCredit.objects.get_or_create(user=request.user)

    return render(request, 'slot_machine/index.html', {'credits': user_credit.credits})

@login_required(login_url='/login/') 
def spin(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Usuário não autenticado.'}, status=401)

    user_credit,created = UserCredit.objects.get_or_create(user=request.user)

    # Verificar se o usuário tem créditos suficientes
    if user_credit.credits < 1:
        return JsonResponse({'error': 'Créditos insuficientes.'}, status=400)

    # Consumir 1 crédito
    user_credit.credits -= 1
    user_credit.save()

    # Lógica do Caça-Níquel
    emojis = ['🍒', '🍋', '🍊', '🍇', '🔔', '⭐', '7️⃣']
    

    # Probabilidades por nível (quanto maior o nível, maior a chance de ganhar os maiores prêmios)
    level_weights = {
        1: [80, 15, 3, 1, 0.5, 0.3, 0.2],      # Nível 1: Muitas chances de ganhar prêmios pequenos
        2: [70, 20, 5, 3, 1, 0.5, 0.5],          # Nível 2: 90% de chances de 5x, poucos prêmios maiores  
        3: [50, 30, 10, 5, 3, 1.5, 0.5],             # Nível 3: Equilibrado
        4: [30, 30, 20, 10, 5, 3, 2],          # Nível 4: Difícil ganhar qualquer coisa além de 2x e 5x  
        5: [25, 20, 15, 10, 10, 10, 10],          # Nível 5: Mais chances de ganhar os prêmios altos
    }


    # Ajustar nível de dificuldade baseado nos créditos e saldo
    if user_credit.credits > 100 or user_credit.balance > 100:
        user_level = random.choice([4, 5])  # Se tem mais de 100 créditos, joga nos níveis mais difíceis
    else:
        user_level = min(user_credit.level, 5)  # Máximo nível 5

    weights = level_weights[user_level]


    results = random.choices(emojis, weights=weights, k=3)

    print(results)
    print(user_level)

    # Verificar se há um ganhador e aplicar o multiplicador
    if len(set(results)) == 1:  # Se todos os símbolos forem iguais
        symbol = results[0]  # Símbolo que foi acertado
        multipliers = {
            '🍒': 2,
            '🍋': 5,
            '🍊': 10,
            '🍇': 20,
            '🔔': 50,
            '⭐': 100,
            '7️⃣': 500,
        }
        multiplier = multipliers.get(symbol, 0)  # Obtém o multiplicador ou 0 se não encontrado
        credits_won = (user_credit.credits + 1) * (multiplier)  # Créditos ganhos (baseado no multiplicador)
        user_credit.credits += credits_won  # Adiciona os créditos ganhos ao saldo

        print('creditos ganho', credits_won)
        
        # Aumentar o nível se ganhou
        if user_credit.level < 5:
            user_credit.level += 1

        user_credit.save()
        message = f"Você ganhou x{multiplier}"
    else:
        message = "Tente novamente!"

    return JsonResponse({'results': results, 'message': message, 'credits': user_credit.credits})

@login_required(login_url='/login/') 
def creditos(request):
    user_credit,created = UserCredit.objects.get_or_create(user=request.user)
    return render(request, 'vendas.html',{'credits': user_credit.credits,
                                            "packages": PACKAGES})

@login_required(login_url='/login/') 
def convert_credits(request):
    if not request.user.is_authenticated:
        messages.error(request,'Usuário não autenticado.')
        return redirect('/login/')

    user_credit, created = UserCredit.objects.get_or_create(user=request.user)

    # Verificar se o usuário tem créditos suficientes para converter
    if user_credit.credits < 1:
        messages.error(request,'Créditos insuficientes para conversão.')
        return redirect('/creditos/')

    # Converter créditos em dinheiro (1 crédito = R$ 1,00)
    amount = user_credit.credits  # Quantidade de créditos para converter
    user_credit.balance += amount  # Adiciona ao saldo em dinheiro
    user_credit.credits = 0  # Zera os créditos
    user_credit.save()

    return redirect('/creditos/')

@login_required(login_url='/login/') 
def purchase_credits(request, package_name):
    """ Gera um link de pagamento do Mercado Pago para a compra do pacote de créditos """
    
    if package_name not in PACKAGES:
        messages.error(request, "Pacote inválido!")
        return redirect("creditos")

    package = PACKAGES[package_name]
    mp = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

    # Criando a preferência de pagamento
    preference_data = {
        "items": [{
            "title": f"{package_name.replace('_', ' ').title()} - {package['credits']} Créditos",
            "quantity": 1,
            "currency_id": "BRL",
            "unit_price": float(package["price"]),
        }],
        "payer": {
            "email": request.user.email,
        },
        "back_urls": {
            "success": request.build_absolute_uri(f"/purchase/success/{package_name}/"),
            "failure": request.build_absolute_uri("/purchase/failure/"),
            "pending": request.build_absolute_uri("/purchase/pending/"),
        },
        "auto_return": "approved",
        "notification_url": request.build_absolute_uri("/mercadopago/webhook/"),
    }

    preference_response = mp.preference().create(preference_data)
    payment_link = preference_response["response"]["init_point"]

    return redirect(payment_link)

@login_required(login_url='/login/') 
def purchase_success(request, package_name):
    """ Processa a compra bem-sucedida e adiciona os créditos ao usuário """

    if package_name not in PACKAGES:
        messages.error(request, "Pacote inválido!")
        return redirect("creditos")

    package = PACKAGES[package_name]
    user_credit, created = UserCredit.objects.get_or_create(user=request.user)

    # Adicionando os créditos + bônus ao saldo do usuário
    total_credits = package["credits"] + package["bonus"]
    user_credit.credits += total_credits
    user_credit.save()

    # Criando um registro da transação
    TransactionHistory.objects.create(
        user=request.user,
        transaction_type="deposit",
        amount=Decimal(package["price"]),
        credits=total_credits,
        status="Aprovado"
    )

    messages.success(request, f"Compra bem-sucedida! Você recebeu {total_credits} créditos.")
    return redirect("creditos")

@login_required(login_url='/login/') 
def purchase_failure(request):
    """ Exibe uma mensagem de falha na compra """
    messages.error(request, "O pagamento não foi aprovado. Tente novamente.")
    return redirect("creditos")


@login_required(login_url='/login/') 
def purchase_pending(request):
    """ Exibe uma mensagem para pagamentos pendentes """
    messages.warning(request, "Seu pagamento está em análise. Assim que for aprovado, seus créditos serão adicionados.")
    return redirect("creditos")


@login_required
def request_pix_withdrawal(request):
    if request.method == "POST":
        amount = Decimal(request.POST["amount"])
        pix_key = request.POST["pix_key"]

        user_credit = UserCredit.objects.get(user=request.user)

        if amount > user_credit.balance:
            messages.error(request, "Saldo insuficiente.")
            return redirect("request_pix_withdrawal")

        if amount < MIN_WITHDRAWAL:
            messages.error(request, "Saldo insuficiente. Para saque, valor mínimo é R$ 100.")
            return redirect("request_pix_withdrawal")

        withdrawal = Withdrawal.objects.create(user=request.user, amount=amount, pix_key=pix_key)
        messages.success(request, "Solicitação de saque enviada para aprovação.")
        withdrawal.save()
        return redirect("request_pix_withdrawal")

    return render(request, "withdraw_pix.html")
