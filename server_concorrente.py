import socket
import threading
import hashlib

# Configurações básicas
HOST = "0.0.0.0"
PORT = 80

# Identificação do aluno
MATRICULA = "20219041293"
NOME = "Camila Moura"

# --- Lógica de Negócios (Idêntica à do servidor sequencial) ---

def gerar_custom_id():
    data = f"{MATRICULA} {NOME}".encode("utf-8")
    return hashlib.md5(data).hexdigest()

X_CUSTOM_ID_ESPERADO = gerar_custom_id()

def gerar_resposta_http(status_code, status_msg, mensagem):
    """Gera uma resposta HTTP completa."""
    resposta = (
        f"HTTP/1.1 {status_code} {status_msg}\r\n"
        f"Content-Type: text/plain\r\n"
        f"X-Custom-ID: {X_CUSTOM_ID_ESPERADO}\r\n"
        f"Content-Length: {len(mensagem)}\r\n"
        "Connection: close\r\n"
        "\r\n"
        f"{mensagem}"
    )
    return resposta.encode("utf-8")

def processar_requisicao(dados_requisicao):
    """Analisa a requisição e retorna a resposta HTTP adequada."""
    headers = {}
    metodo = ""
    try:
        linhas = dados_requisicao.split('\r\n')
        if not linhas:
            return gerar_resposta_http(400, "Bad Request", "Requisição vazia")
        metodo = linhas[0].split(' ')[0]
        for linha in linhas[1:]:
            if linha == "": break
            if ":" in linha:
                chave, valor = linha.split(":", 1)
                headers[chave.strip().lower()] = valor.strip()
    except Exception as e:
        return gerar_resposta_http(400, "Bad Request", f"Erro ao processar requisição: {e}")

    if metodo != "GET":
        return gerar_resposta_http(405, "Method Not Allowed", "Método não permitido. Use GET.")

    custom_id_recebido = headers.get('x-custom-id')
    if not custom_id_recebido or custom_id_recebido != X_CUSTOM_ID_ESPERADO:
        return gerar_resposta_http(403, "Forbidden", "X-Custom-ID ausente ou inválido.")
        
    return gerar_resposta_http(200, "OK", "Servidor Concorrente: Requisição válida recebida com sucesso!\n")

# --- Lógica de Concorrência ---

def atender_cliente(conexao, endereco):
    """Função executada por cada thread para atender um cliente."""
    print(f"Nova thread iniciada para atender {endereco}")
    try:
        dados = conexao.recv(1024).decode("utf-8")
        if dados:
            print(f"\nRequisição recebida de {endereco} na sua thread.")
            resposta = processar_requisicao(dados)
            conexao.sendall(resposta)
            print(f"Resposta enviada para {endereco} e conexão da thread encerrada.\n")
    except Exception as e:
        print(f"Erro na thread para {endereco}: {e}")
    finally:
        conexao.close()

def iniciar_servidor_concorrente():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((HOST, PORT))
        servidor.listen(5) # O backlog pode ser maior para um servidor concorrente
        print(f"Servidor CONCORRENTE iniciado em {HOST}:{PORT}")
        print(f"X-Custom-ID Esperado: {X_CUSTOM_ID_ESPERADO}\n")

        while True:
            conexao, endereco = servidor.accept()
            # Cria e inicia uma nova thread para cada cliente
            thread = threading.Thread(target=atender_cliente, args=(conexao, endereco))
            thread.start()

if __name__ == "__main__":
    iniciar_servidor_concorrente()
