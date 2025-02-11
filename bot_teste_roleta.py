import requests
from collections import Counter
import threading
import time

# URL real da API
URL = "http://0.0.0.0:5000/spin_roulette/"  # Substitua pela URL correta

# Tabela de resultados esperados
outcomes = [
    {'label': 'Perde Tudo', 'multiplier': -1},
    {'label': 'x2', 'multiplier': 2},
    {'label': 'x5', 'multiplier': 5},
    {'label': 'Perde Tudo', 'multiplier': -1},
    {'label': 'x20', 'multiplier': 20},
    {'label': 'Perde Tudo', 'multiplier': -1},
    {'label': 'x2', 'multiplier': 2},
    {'label': 'x5', 'multiplier': 5},
    {'label': 'Perde Tudo', 'multiplier': -1},
    {'label': 'Passa a Vez', 'multiplier': 0}
]

# Número de requisições a serem feitas
NUM_REQUISICOES = 500

# Contador para armazenar os resultados
contador_resultados = Counter()

# Lock para garantir que o contador seja atualizado corretamente
lock = threading.Lock()

# Criar uma sessão para reutilizar conexões (melhora o desempenho)
session = requests.Session()

# Função para fazer a requisição à API
def fazer_requisicao():
    try:
        resposta = session.post(URL, timeout=5)  # Faz a requisição à API
        resposta.raise_for_status()  # Lança erro se o status for ruim (ex: 500, 404)
        data = resposta.json()  # Converte a resposta para JSON

        # Valida se o índice retornado está dentro da tabela esperada
        index = data.get("index")
        if index is not None and 0 <= index < len(outcomes):
            return outcomes[index]["label"]  # Retorna o rótulo correto do índice
        else:
            return "Erro na resposta"

    except requests.exceptions.RequestException as e:
        return f"Erro de conexão: {e}"
    except ValueError:
        return "Erro ao converter resposta para JSON"

# Função que cada thread executará
def worker():
    global contador_resultados
    resultado = fazer_requisicao()
    
    # Usar o lock para atualizar o contador de forma segura
    with lock:
        contador_resultados[resultado] += 1

# Criar e iniciar as threads
threads = []
for _ in range(NUM_REQUISICOES):
    thread = threading.Thread(target=worker)
    threads.append(thread)
    thread.start()

    # Pequeno delay para evitar sobrecarregar o servidor
    time.sleep(0.05)

# Aguardar todas as threads terminarem
for thread in threads:
    thread.join()

# Exibir os resultados
print("Quantidade de vezes que cada resultado apareceu:")
for resultado, quantidade in contador_resultados.items():
    print(f"{resultado}: {quantidade} vezes")

# Exibir a porcentagem de cada resultado
print("\nPorcentagem de cada resultado:")
total_requisicoes = sum(contador_resultados.values())
for resultado, quantidade in contador_resultados.items():
    porcentagem = (quantidade / total_requisicoes) * 100
    print(f"{resultado}: {porcentagem:.2f}%")