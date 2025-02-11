from .models import UserCredit
import random



def manage_risk(user_id, bet_amount, possible_payouts):
    user_credit = UserCredit.objects.get(user=user_id)

    # Verificar o nível do usuário para ajustar as probabilidades
    user_level = min(user_credit.level, 5)

    # Definir a tabela de probabilidades baseada no nível do usuário
    level_weights = {
        1: [80, 15, 3, 1, 0.5, 0.4, 0.1], 
        2: [70, 20, 5, 3, 1, 0.5, 0.5],  
        3: [50, 30, 10, 5, 3, 1.5, 0.5], 
        4: [30, 30, 20, 10, 5, 3, 2.5],  
        5: [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]  
    }
    
    weights = level_weights[user_level]

    # Verifica se o jogador está ganhando muito e ajusta para reduzir os ganhos
    if user_credit.balance > 100:  
        weights = [w * 0.5 for w in weights]  # Reduz as chances de ganhos altos

    # Se o cassino estiver perdendo dinheiro, reduz ainda mais os prêmios
    if user_credit.balance > 500:  
        weights = [w * 0.3 for w in weights]

    # Normaliza para garantir que a soma das probabilidades seja 100%
    total_weight = sum(weights)
    normalized_weights = [w / total_weight for w in weights]

    # Escolhe o resultado com base nas probabilidades ajustadas
    result = random.choices(list(possible_payouts[user_level]), weights=normalized_weights, k=3)

    return result
