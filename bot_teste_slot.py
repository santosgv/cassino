import requests
import threading
from collections import Counter
import time



# Função para fazer requisição e armazenar resultados
def check_results(url, results_tracker, lock):
    try:
        response = requests.get(url)
        data = response.json()

        with lock:
            results_tracker['total_requests'] += 1
            
            if "results" in data:
                results = data["results"]
                for result in results:
                    results_tracker['results_count'][result] += 1
                
                # Verifica se todos os valores são iguais (vitória)
                if len(set(results)) == 1:
                    results_tracker['victories'] += 1
            
    except Exception as e:
        print(f"Erro ao acessar a URL: {e}")

# Função para executar testes com múltiplas threads
def run_tests(url, num_requests):
    results_tracker = {
        'total_requests': 0,
        'victories': 0,
        'results_count': Counter()
    }
    
    lock = threading.Lock()  # Lock para evitar condições de corrida
    threads = []
    
    for _ in range(num_requests):
        thread = threading.Thread(target=check_results, args=(url, results_tracker, lock))
        threads.append(thread)
        thread.start()
        time.sleep(0.10)  # Pequeno delay para evitar sobrecarga
    
    for thread in threads:
        thread.join()
    
    # Exibir os resultados
    print(f"\n🔹 Total de requisições: {results_tracker['total_requests']}")
    print(f"🏆 Total de vitórias (todos iguais): {results_tracker['victories']}")
    
    # Calcular e exibir a porcentagem de vitórias
    if results_tracker['total_requests'] > 0:
        victory_percentage = (results_tracker['victories'] / results_tracker['total_requests']) * 100
        print(f"📈 Porcentagem de vitórias: {victory_percentage:.2f}%\n")
    else:
        print("📈 Porcentagem de vitórias: 0.00% (nenhuma requisição foi feita)\n")
    
    # Exibir quantas vezes cada resultado apareceu
    print("📊 Quantidade de vezes que cada resultado apareceu:")
    for resultado, quantidade in results_tracker['results_count'].items():
        print(f"   {resultado}: {quantidade} vezes")

    # Exibir a porcentagem de cada resultado
    print("\n📊 Porcentagem de cada resultado:")
    total_requisicoes = results_tracker['total_requests']
    for resultado, quantidade in results_tracker['results_count'].items():
        porcentagem = (quantidade / total_requisicoes) * 100
        print(f"   {resultado}: {porcentagem:.2f}%")

# Exemplo de uso
url = "http://0.0.0.0:5000/spin/"  # Substitua pela URL real
num_requests = 20  # Defina o número de requisições desejadas
run_tests(url, num_requests)