from .models import UserCredit
import random
import qrcode
import os
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
from decimal import Decimal

def get_bet_amount(level):
    return max(1, min(level, 5))

def manage_risk(user_id, bet_amount, possible_payouts):
    user_credit = UserCredit.objects.get(user=user_id)

    # Definir probabilidades fixas: 8% de chance de ganhar, 8% de chance de perder
    if random.random() <= 0.02:  # 8% de chance de ganhar
        # Escolher um símbolo vencedor com base no nível do usuário
        level_weights = {
            1: [70, 25, 3, 1, 0.5, 0.4, 0.1],  # Pesos para cada símbolo no nível 1
            2: [70, 20, 5, 3, 1, 0.5, 0.5],   # Pesos para cada símbolo no nível 2
            3: [50, 30, 10, 5, 3, 1.5, 0.5],  # Pesos para cada símbolo no nível 3
            4: [30, 30, 20, 10, 5, 3, 2.5],   # Pesos para cada símbolo no nível 4
            5: [15, 15, 20, 20, 10, 10, 10]    # Pesos para cada símbolo no nível 5
        }
        base_weights = level_weights.get(user_credit.level, level_weights[1])  # Usar nível 1 como padrão
        total_weight = sum(base_weights)
        normalized_weights = [w / total_weight for w in base_weights]

        # Escolher um símbolo vencedor
        winning_symbol = random.choices(
            list(possible_payouts[user_credit.level]),
            weights=normalized_weights,
            k=1
        )[0]

        # Gerar resultados com base no símbolo vencedor
        result = [winning_symbol] * 3  # Todos os 3 símbolos iguais (vitória)
    else:  # 8% de chance de perder
        # Escolher símbolos aleatórios diferentes (derrota)
        result = random.choices(
            list(possible_payouts[user_credit.level]),
            k=3
        )

    return result


def gerar_qrcode(chave_pix):
    """Gera um QR Code a partir da string chave_pix e retorna o caminho do arquivo salvo."""

    # Diretório onde os QR Codes serão salvos
    qr_dir = os.path.join(settings.MEDIA_ROOT, "qrcodes")
    os.makedirs(qr_dir, exist_ok=True)  # Garante que o diretório existe

    # Define o caminho do arquivo (usando um nome único baseado na chave PIX)
    qr_filename = f"qrcode_{hash(chave_pix)}.png"
    qr_path = os.path.join(qr_dir, qr_filename)

    # Gera o QR Code e salva no caminho definido
    qr = qrcode.make(chave_pix)
    qr.save(qr_path, format="PNG")

    # Retorna o caminho relativo ao MEDIA_URL para ser usado no template
    return f"/media/qrcodes/{qr_filename}"



def generate_multiplier():
    import random
    return round(random.uniform(1.0, 2.5), 2)

@csrf_exempt
@login_required
def get_multiplier(request):
    if request.method == 'GET':
        multiplier = generate_multiplier()  # Função que gera o multiplicador

        return JsonResponse({
            'multiplier': multiplier,
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
@login_required
def lose_bet(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            bet_amount = Decimal(data.get('bet_amount', 0)).quantize(Decimal('0.00'))  # Converte para Decimal com 2 casas decimais

            # Obtém o saldo atual do usuário
            user_credit = UserCredit.objects.get(user=request.user)

            # Subtrai o valor apostado do saldo
            user_credit.balance -= bet_amount
            user_credit.save()

            return JsonResponse({
                'success': True,
                'new_balance': float(user_credit.balance)  # Converte para float
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
@login_required
def update_credits(request):
    if request.method == 'POST':
        try:
            # Obtém o valor ganho a partir do corpo da requisição
            data = json.loads(request.body)
            winnings = Decimal(data.get('winnings', 0)).quantize(Decimal('0.00'))

            # Obtém o saldo atual do usuário
            user_credit = UserCredit.objects.get(user=request.user)

            # Atualiza o saldo do usuário
            user_credit.balance += winnings
            user_credit.save()

            return JsonResponse({
                'success': True,
                'new_balance': float(user_credit.balance)
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)