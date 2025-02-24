from django.shortcuts import render,redirect
from django.http import JsonResponse
import random
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import UserCredit
from django.contrib.auth.models import User
from accounts.models import Withdrawal
from django.contrib import messages
import json
from decimal import Decimal
from django.conf import settings
from django.core.paginator import Paginator
from .utils import  manage_risk,get_bet_amount,gerar_qrcode
from django.views.decorators.csrf import csrf_exempt


import logging

logger = logging.getLogger(__name__)

MIN_WITHDRAWAL = 100

# Lista dos pacotes disponíveis
PACKAGES = {
    "starter": {"name": "🟢 Starter", "credits": 20, "price": 10.00, "bonus": 0, "color": "success", "qr_code": "00020101021126580014br.gov.bcb.pix01362fc8fd02-fa45-4ff3-80a4-1c2f3439231b520400005303986540510.005802BR5907LIVEPIX6009SAO PAULO6228052467b9fbfc42b640c5100daf0563047B46"},
    "pro": {"name": "🔵 Pro Player", "credits": 90, "price": 20.00, "bonus": 40, "color": "primary", "qr_code": "00020101021126580014br.gov.bcb.pix01362fc8fd02-fa45-4ff3-80a4-1c2f3439231b520400005303986540520.005802BR5907LIVEPIX6009SAO PAULO6228052467b9eb50bb22c246c60fc50d63045EA3"},
    "high_roller": {"name": "🔴 High Roller", "credits": 180, "price": 75.00, "bonus": 80, "color": "danger", "qr_code": "00020101021126580014br.gov.bcb.pix01362fc8fd02-fa45-4ff3-80a4-1c2f3439231b520400005303986540575.005802BR5907LIVEPIX6009SAO PAULO6228052467b9fafdff9fe5429d0f002a6304DC02"},
    "vip": {"name": "🔥 VIP", "credits": 450, "price": 100.00, "bonus": 150, "color": "warning", "qr_code": "00020101021126580014br.gov.bcb.pix01362fc8fd02-fa45-4ff3-80a4-1c2f3439231b5204000053039865406100.005802BR5907LIVEPIX6009SAO PAULO6228052467b9fb4e449826beb7019c2563040DDA"},
}

CREDIT_PACKAGES = {
    10.00: 20,
    20.00: 90,
    75.00: 180,
    100.00: 450
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
        credits_won = user_credit.credits * multiplier
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

@login_required
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

def aviator(request):
    return render(request, 'aviator/index.html')

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
    if package_name not in PACKAGES:
        messages.error(request, "Pacote inválido!")
        return redirect("creditos")

    package = PACKAGES[package_name]

    qrcode = gerar_qrcode(package["qr_code"])

    print(qrcode)

    return render(request, "checkout.html", {
            "qr_code": qrcode,
            "package": package,
        })

@csrf_exempt
def livepix_webhook(request):
    if request.method == 'POST':
        try:
            event = json.loads(request.body)
            logger.debug(f"Payload recebido: {event}")

            if event.get('event') == 'new':  # Confirma que é um pagamento recebido
                payment_data = event.get('resource', {})
                amount = float(payment_data.get('amount', 0))
                reference = payment_data.get('reference', '')  # Aqui deve ser o email do usuário
                
                logger.debug(f"Pagamento recebido: {amount} | Referência: {reference}")

                # Valida se o valor pago está nos pacotes disponíveis
                if amount not in CREDIT_PACKAGES:
                    logger.warning(f"Valor pago inválido: {amount}")
                    return JsonResponse({'error': 'Valor de pagamento não reconhecido'}, status=400)

                # Busca o usuário pelo email de referência
                try:
                    user = User.objects.get(email=reference)
                    user_credit, created = UserCredit.objects.get_or_create(user=user)

                    # Atualiza os créditos do usuário
                    credits_to_add = CREDIT_PACKAGES[amount]
                    user_credit.credits += credits_to_add
                    user_credit.save()

                    logger.info(f"Créditos adicionados: {credits_to_add} para {user.email}")

                    return JsonResponse({'status': 'success', 'credits_added': credits_to_add}, status=200)
                
                except User.DoesNotExist:
                    logger.error(f"Usuário não encontrado para o email: {reference}")
                    return JsonResponse({'error': 'Usuário não encontrado'}, status=404)

            else:
                logger.warning("Evento não suportado recebido no webhook")
                return JsonResponse({'error': 'Evento não suportado'}, status=400)

        except json.JSONDecodeError:
            logger.error("Erro ao decodificar JSON recebido no webhook")
            return JsonResponse({'error': 'JSON inválido'}, status=400)

    return JsonResponse({'error': 'Método não permitido'}, status=405)

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
