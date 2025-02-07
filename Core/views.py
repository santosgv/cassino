from django.shortcuts import render,redirect
from django.http import JsonResponse
import random
from django.contrib.auth.decorators import login_required
from .models import UserCredit


@login_required(login_url='/accounts/login/')  
def jogo(request):
    user_credit,created = UserCredit.objects.get_or_create(user=request.user)

    return render(request, 'slot_machine/index.html', {'credits': user_credit.credits})

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
    weights = [40, 25, 15, 5, 3, 2, 1]  # Pesos personalizados
    results = random.choices(emojis, weights=weights, k=3)

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
        credits_won = multiplier  # Créditos ganhos (baseado no multiplicador)
        user_credit.credits += credits_won  # Adiciona os créditos ganhos ao saldo
        user_credit.save()
        message = f"Você ganhou X{credits_won}"
    else:
        message = "Tente novamente!"

    return JsonResponse({'results': results, 'message': message, 'credits': user_credit.credits})

def creditos(request):
    user_credit,created = UserCredit.objects.get_or_create(user=request.user)
    return render(request, 'vendas.html',{'credits': user_credit.credits})

def convert_credits(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Usuário não autenticado.'}, status=401)

    user_credit, created = UserCredit.objects.get_or_create(user=request.user)

    # Verificar se o usuário tem créditos suficientes para converter
    if user_credit.credits < 1:
        return JsonResponse({'error': 'Créditos insuficientes para conversão.'}, status=400)

    # Converter créditos em dinheiro (1 crédito = R$ 1,00)
    amount = user_credit.credits  # Quantidade de créditos para converter
    user_credit.balance += amount  # Adiciona ao saldo em dinheiro
    user_credit.credits = 0  # Zera os créditos
    user_credit.save()

    return redirect('/jogo/')