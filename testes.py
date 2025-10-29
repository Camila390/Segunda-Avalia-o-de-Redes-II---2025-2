import socket
import threading
import time
import hashlib
import statistics

# --- CONFIGURAÇÕES DO TESTE ---
SERVER_IP = "12.93.0.2"   
SERVER_PORT = 80
TOTAL_REQUISICOES = 500   
CLIENTES_SIMULTANEOS = 25    

# --- DADOS DO ALUNO ---
MATRICULA = "20219041293"
NOME = "Camila Moura"

# --- VARIÁVEIS GLOBAIS PARA COLETA DE DADOS ---
# Lista para armazenar o tempo de latência de cada requisição bem-sucedida
tempos_de_latencia = []
# Contador para requisições que falharam
requisicoes_falhas = 0
# Lock para garantir que a escrita nas variáveis globais seja segura entre as threads
lock = threading.Lock()


def gerar_custom_id():
    data = f"{MATRICULA} {NOME}".encode("utf-8")
    return hashlib.md5(data).hexdigest()

X_CUSTOM_ID = gerar_custom_id()

def gerar_requisicao_http():
    return (
        "GET / HTTP/1.1\r\n"
        f"Host: {SERVER_IP}\r\n"
        f"X-Custom-ID: {X_CUSTOM_ID}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).encode("utf-8")

# --- FUNÇÃO DO "CLIENTE" (EXECUTADA POR CADA THREAD) ---

def cliente_worker():
    """Esta função é executada por cada thread. Ela faz uma requisição e registra o resultado."""
    global requisicoes_falhas
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(10) # Timeout de 10 segundos para evitar que uma thread prenda para sempre
            s.connect((SERVER_IP, SERVER_PORT))

            requisicao = gerar_requisicao_http()
            
            # Mede o tempo de latência (T_lat)
            inicio = time.perf_counter()
            s.sendall(requisicao)
            s.recv(4096) # Apenas esperamos a resposta, não a processamos para o teste
            fim = time.perf_counter()

            latencia_ms = (fim - inicio) * 1000

            # Usa um lock para adicionar o resultado à lista de forma segura
            with lock:
                tempos_de_latencia.append(latencia_ms)

    except (socket.timeout, ConnectionRefusedError, ConnectionResetError) as e:
        # Se a conexão falhar ou demorar demais, contamos como uma falha
        print(f"Erro em uma requisição: {e}")
        with lock:
            requisicoes_falhas += 1
    except Exception as e:
        print(f"Erro inesperado: {e}")
        with lock:
            requisicoes_falhas += 1

# --- FUNÇÃO PRINCIPAL PARA ORQUESTRAR O TESTE ---

def executar_teste():
    print("--- Iniciando Teste de Desempenho ---")
    print(f"Alvo: {SERVER_IP}:{SERVER_PORT}")
    print(f"Total de Requisições: {TOTAL_REQUISICOES}")
    print(f"Clientes Simultâneos: {CLIENTES_SIMULTANEOS}")
    print("--------------------------------------\n")
    
    # Mede o tempo total de execução
    tempo_inicio_total = time.perf_counter()

    # Cria e inicia as threads
    threads = []
    for _ in range(TOTAL_REQUISICOES):
        thread = threading.Thread(target=cliente_worker)
        threads.append(thread)
        thread.start()
        # Controla o número de threads ativas para não sobrecarregar a máquina cliente
        if len(threads) % CLIENTES_SIMULTANEOS == 0:
             # Espera o lote atual de threads terminar antes de iniciar o próximo
            for t in threads:
                t.join()
            threads = []
            
    # Espera as threads restantes terminarem
    for thread in threads:
        thread.join()

    tempo_fim_total = time.perf_counter()
    
    # --- CÁLCULO E APRESENTAÇÃO DOS RESULTADOS ---
    
    tempo_total_execucao = tempo_fim_total - tempo_inicio_total
    
    print("\n--- Resultados do Teste ---")
    
    if not tempos_de_latencia:
        print("Nenhuma requisição foi bem-sucedida.")
        return

    # Métricas Estatísticas (µ e σ)
    media_latencia = statistics.mean(tempos_de_latencia)
    if len(tempos_de_latencia) > 1:
        desvio_padrao_latencia = statistics.stdev(tempos_de_latencia)
    else:
        desvio_padrao_latencia = 0
        
    # Vazão (Throughput)
    requisicoes_sucesso = len(tempos_de_latencia)
    vazao = requisicoes_sucesso / tempo_total_execucao if tempo_total_execucao > 0 else 0
    
    print(f"Tempo Total de Execução: {tempo_total_execucao:.2f} s")
    print(f"Total de Requisições com Sucesso: {requisicoes_sucesso}")
    print(f"Total de Requisições com Falha: {requisicoes_falhas}")
    print("-" * 25)
    print(f"Média de Latência: {media_latencia:.2f} ms")
    print(f"Desvio Padrão da Latência: {desvio_padrao_latencia:.2f} ms")
    print(f"Vazão (Throughput): {vazao:.2f} req/s")
    print("---------------------------\n")

if __name__ == "__main__":
    executar_teste()