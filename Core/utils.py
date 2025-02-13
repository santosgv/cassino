from .models import UserCredit
from decimal import Decimal
import random


def get_bet_amount(level):
    return max(1, min(level, 5))

def manage_risk(user_id, bet_amount, possible_payouts):
    user_credit = UserCredit.objects.get(user=user_id)

    # 🔢 Probabilidades iniciais baseadas no nível do usuário
    level_weights = {
        1: [70, 25, 3, 1, 0.5, 0.4, 0.1], 
        2: [70, 20, 5, 3, 1, 0.5, 0.5],  
        3: [50, 30, 10, 5, 3, 1.5, 0.5], 
        4: [30, 30, 20, 10, 5, 3, 2.5],  
        5: [15, 15, 20, 20, 10, 10, 10] 
    }
    
    base_weights = level_weights.get(user_credit.level, level_weights[1])  # Evita erro se nível for inválido

    # 📊 Ajuste para garantir lucro a longo prazo
    total_weight = sum(base_weights)
    normalized_weights = [w / total_weight for w in base_weights]

    # Escolher resultado final
    result = random.choices(
        list(possible_payouts[user_credit.level]),
        weights=normalized_weights,
        k=3
    )

        # 🔄 Ajuste Dinâmico: Se jogador estiver ganhando muito, reduzir chance de vitória
    if user_credit.credits >= user_credit.max_credits * 0.5:
        base_weights = [w * 0.2 for w in base_weights]  # Reduz 80% das chances de ganhar
        result = random.choices(['🍒', '🍋', '🍊','🍇','🔔','⭐','7️⃣'],k=3)
        print('reduzido em 80')

    if user_credit.credits >= user_credit.max_credits * 0.75:
        base_weights = [w * 0.05 for w in base_weights]  # Reduz 95% das chances
        result = random.choices(['🍒', '🍋', '🍊','🍇','🔔','⭐','7️⃣'],k=3)
        print('reduzido em 95')

    return result