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
from django.core.paginator import Paginator
from .utils import  manage_risk,get_bet_amount
from django.views.decorators.csrf import csrf_exempt

MIN_WITHDRAWAL = 100

# Lista dos pacotes disponíveis
PACKAGES = {
    "starter": {"name": "🟢 Starter Pack", "credits": 20, "price": 10.00, "bonus": 0, "color": "success"},
    "pro": {"name": "🔵 Pro Player", "credits": 90, "price": 50.00, "bonus": 40, "color": "primary"},
    "high_roller": {"name": "🔴 High Roller", "credits": 180, "price": 100.00, "bonus": 80, "color": "danger"},
    "vip": {"name": "🔥 VIP Pack", "credits": 450, "price": 250.00, "bonus": 150, "color": "warning"},
    "super_vip": {"name": " 💎Super VIP", "credits": 900, "price": 500.00, "bonus": 200, "color": "info"},
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

    # teste
    #user_credit = UserCredit.objects.get(user=1)

    # Verificar se o usuário tem créditos suficientes
    if user_credit.credits < 1:
        return JsonResponse({'error': 'Créditos insuficientes.'}, status=400)
    
    bet_amount = get_bet_amount(user_credit.level)
    

    # Consumir  crédito
    user_credit.credits -= bet_amount
    user_credit.save()

    results = manage_risk(
        user_id=user_credit.user.id, 
        bet_amount=bet_amount, 
        possible_payouts={
            1: ['🍒', '🍋', '🍊', '🍇', '🔔', '⭐', '7️⃣'],
            2: ['🍒', '🍋', '🍊', '🍇', '🔔', '⭐', '7️⃣'],
            3: ['🍒', '🍋', '🍊', '🍇', '🔔', '⭐', '7️⃣'],
            4: ['🍒', '🍋', '🍊', '🍇', '🔔', '⭐', '7️⃣'],
            5: ['🍒', '🍋', '🍊', '🍇', '🔔', '⭐', '7️⃣']
        }
    )


    print(results)
    print(bet_amount)

    # Verificar se há um ganhador e aplicar o multiplicador
    if len(set(results)) == 1:  # Se todos os símbolos forem iguais
        symbol = results[0]  # Símbolo que foi acertado
        multipliers = {
            '🍒': 1.2,
            '🍋': 1.4,
            '🍊': 1.6,
            '🍇': 1.8,
            '🔔': 2,
            '⭐': 2,
            '7️⃣': 2,
        }
        
        multiplier = multipliers.get(symbol, 0) 
        credits_won = bet_amount * multiplier
        user_credit.credits += credits_won  
        user_credit.update_stats(1, 1)

        
        # Aumentar o nível se ganhou
        if user_credit.level < 5:
            user_credit.level += 1

        user_credit.save()
        message = f"Você ganhou x{multiplier}"
    else:
        user_credit.update_stats(1, -1)
        message = "Tente novamente!"

    return JsonResponse({'results': results, 'message': message, 'credits': user_credit.credits})

@login_required(login_url='/login/')  
def roleta(request):
    user_credit,created = UserCredit.objects.get_or_create(user=request.user)
    return render(request, 'roleta/index.html', {'credits': user_credit.credits})

#@login_required
@csrf_exempt 
def spin_roulette(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Usuário não autenticado.'}, status=401)

    # Simulação de créditos do usuário (substitua por seu modelo real)
    #user_credit = UserCredit.objects.get(user=1)
    user_credit,created = UserCredit.objects.get_or_create(user=request.user)

    # Verificar se o usuário tem créditos suficientes
    if user_credit.credits < 1:
        return JsonResponse({'error': 'Créditos insuficientes.'}, status=400)

    # Aplicar margem de lucro do cassino (10%)
    bet_amount = 5


    # Consumir 5 créditos
    user_credit.credits -= bet_amount
    user_credit.save()

    # Definir as opções da roleta e suas probabilidades
    outcomes = [
        {'label': 'Perde Tudo', 'multiplier': -1},
        {'label': 'x2', 'multiplier': 2},
        {'label': 'x5', 'multiplier': 5},
        {'label': 'Perde Tudo', 'multiplier': -1},
        {'label': 'x20', 'multiplier': 20},
        {'label': 'Perde Tudo', 'multiplier': -1},
        {'label': 'x2', 'multiplier': 2},
        {'label': 'x5', 'multiplier': 5},
    ]
    weights = [40, 3, 1, 40, 0.05, 40, 3, 1]

    # Sortear um resultado
    result_index = random.choices(range(len(outcomes)), weights=weights, k=1)[0]
    result = outcomes[result_index]

    # Atualizar créditos do usuário com base no resultado
    if result['multiplier'] == -1:
        user_credit.credits = 0  # Perde tudo
        
    elif result['multiplier'] > 0:
        user_credit.credits *= result['multiplier']  # Multiplica créditos

    # Salvar créditos (substitua por sua lógica de salvamento)

    user_credit.update_stats(bet_amount, user_credit.credits)
    user_credit.save()

    print(result_index,result['label'])

    # Retornar o resultado e o índice
    return JsonResponse({
        'result': result['label'],
        'index': result_index,  # Índice do resultado
        'credits': user_credit.credits
    })

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
    amount = Decimal(user_credit.credits)  # Quantidade de créditos para converter
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
    print(payment_link)

    return redirect(payment_link)


@csrf_exempt
def mercado_pago_webhook(request):
    """ Webhook para ouvir notificações de pagamento do Mercado Pago """
    
    if request.method == "POST":
        try:
            # Obtendo os dados enviados pelo Mercado Pago
            data = json.loads(request.body)
            payment_id = data.get("data", {}).get("id")

            if not payment_id:
                return JsonResponse({"error": "ID de pagamento não encontrado"}, status=400)

            # Conectando à API do Mercado Pago
            mp = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
            payment_info = mp.payment().get(payment_id)

            if "response" not in payment_info or payment_info["response"].get("status") != "approved":
                return JsonResponse({"error": "Pagamento não aprovado"}, status=400)

            # Pegando os detalhes do pagamento
            payment_data = payment_info["response"]
            email = payment_data["payer"]["email"]
            amount_paid = payment_data["transaction_amount"]

            # Encontrando o usuário pelo email
            user = User.objects.filter(email=email).first()
            if not user:
                return JsonResponse({"error": "Usuário não encontrado"}, status=400)

            # Verificando qual pacote foi comprado
            purchased_credits = None
            for package_name, package in PACKAGES.items():
                if float(package["price"]) == amount_paid:
                    purchased_credits = package["credits"]
                    break

            if purchased_credits is None:
                return JsonResponse({"error": "Pacote não encontrado"}, status=400)

            # Atualizando os créditos do usuário
            user_credit, created = UserCredit.objects.get_or_create(user=user)
            user_credit.credits += purchased_credits
            user_credit.save()

            return JsonResponse({"message": "Pagamento processado com sucesso"}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Método inválido"}, status=405)


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
    withdrawals_all = Withdrawal.objects.filter(user=request.user).order_by('-id')

    pagina = Paginator(withdrawals_all, 10)
    page = request.GET.get('page')
    withdrawals = pagina.get_page(page)

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

        user_credit.balance -= amount
        user_credit.save()

        messages.success(request, "Solicitação de saque enviada para aprovação.")
        withdrawal.save()
        return redirect("request_pix_withdrawal")

    return render(request, "withdraw_pix.html",{'withdrawals':withdrawals})
