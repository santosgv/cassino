from .models import UserCredit
import random


def get_bet_amount(level):
    return max(1, min(level, 5))

def manage_risk(user_id, bet_amount, possible_payouts):
    user_credit = UserCredit.objects.get(user=user_id)

    # 🎯 Definir retorno esperado para garantir lucro do cassino
    RETURN_EXPECTED = 0.85  # Jogador recebe no máximo 85% do que aposta no longo prazo

    # 🔢 Probabilidades iniciais baseadas no nível do usuário
    level_weights = {
        1: [70, 25, 3, 1, 0.5, 0.4, 0.1], 
        2: [70, 20, 5, 3, 1, 0.5, 0.5],  
        3: [50, 30, 10, 5, 3, 1.5, 0.5], 
        4: [30, 30, 20, 10, 5, 3, 2.5],  
        5: [15, 15, 20, 20, 10, 10, 10] 
    }
    
    base_weights = level_weights.get(user_credit.level, level_weights[1])  # Evita erro se nível for inválido

    # 🔄 Ajuste Dinâmico: Se jogador estiver ganhando muito, reduzir chance de vitória
    if user_credit.credits >= user_credit.max_credits * 0.5:
        base_weights = [w * 0.2 for w in base_weights]  # Reduz 80% das chances de ganhar

    if user_credit.credits >= user_credit.max_credits * 0.75:
        base_weights = [w * 0.05 for w in base_weights]  # Reduz 95% das chances

    # 📊 Ajuste para garantir lucro a longo prazo
    total_weight = sum(base_weights)
    normalized_weights = [w / total_weight for w in base_weights]

    # 🔢 Simulação de múltiplas rodadas para verificar retorno esperado
    simulated_wins = 0
    simulated_losses = 0
    for _ in range(2000):  # Simulação com 10.000 rodadas
        result = random.choices(
            list(possible_payouts[user_credit.level]),
            weights=normalized_weights,
            k=3
        )

        if len(set(result)) == 1:  # Se todos os símbolos forem iguais
            symbol = result[0]
            multipliers = {'🍒': 2, '🍋': 5, '🍊': 7, '🍇': 12, '🔔': 20, '⭐': 50, '7️⃣': 200}
            simulated_wins += bet_amount * multipliers.get(symbol, 0)
        else:
            simulated_losses += bet_amount

    actual_return = simulated_wins / max(simulated_losses, 1)  # Evita divisão por zero

    # 📉 Se retorno for maior do que esperado, reduz chances de vitória
    if actual_return > RETURN_EXPECTED:
        normalized_weights = [w * 0.8 for w in normalized_weights]

    # Escolher resultado final
    result = random.choices(
        list(possible_payouts[user_credit.level]),
        weights=normalized_weights,
        k=3
    )

    print(f' Possibilidade de vitoria {simulated_wins}')
    print(f' Possibilidade de perca {simulated_losses}')
    return result