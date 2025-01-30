from django.shortcuts import render
from django.http import JsonResponse
import random
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .models import UserCredit

def index(request):
    if not request.user.is_authenticated:
        return render(request, 'slot_machine/index.html', {'credits': 0})  # Usuário não autenticado

    # Obter ou criar o saldo de créditos do usuário
    user_credit = UserCredit.objects.get(user=request.user)
    return render(request, 'slot_machine/index.html', {'credits': user_credit.credits})

def spin(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Usuário não autenticado.'}, status=401)

    user_credit, created = UserCredit.objects.get_or_create(user=request.user)

    # Verificar se o usuário tem créditos suficientes
    if user_credit.credits < 1:
        return JsonResponse({'error': 'Créditos insuficientes.'}, status=400)

    # Consumir 1 crédito
    user_credit.credits -= 1
    user_credit.save()

    # Lógica do Caça-Níquel
    emojis = ['🍒', '🍋', '🍊', '🍇', '🔔', '⭐', '7️⃣']
    weights = [40, 30, 20, 15, 10, 5, 1]  # Pesos personalizados
    results = random.choices(emojis, weights=weights, k=3)

    print(results)
    # Verificar se há um ganhador
    if len(set(results)) == 1:
        message = "Você ganhou!"
        user_credit.credits += 10
        user_credit.save()
    else:
        message = "Tente novamente!"

    return JsonResponse({'results': results, 'message': message, 'credits': user_credit.credits})

def creditos(request):
    return render(request, 'vendas.html')