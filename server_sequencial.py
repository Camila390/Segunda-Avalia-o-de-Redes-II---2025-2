import socket
import hashlib

# Configurações básicas
HOST = "0.0.0.0"  
PORT = 80         

# Identificação do aluno
MATRICULA = "20219041293"
NOME = "Camila Moura"

# Calcula o hash para o cabeçalho X-Custom-ID
def gerar_custom_id():
    data = f"{MATRICULA} {NOME}".encode("utf-8")
    return hashlib.md5(data).hexdigest()

X_CUSTOM_ID_ESPERADO = gerar_custom_id()

# --- Funções de Resposta HTTP ---

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

# --- Lógica de Processamento ---

def processar_requisicao(dados_requisicao):
    """Analisa a requisição e retorna a resposta HTTP adequada."""
    
    print("\nRequisição recebida:\n", dados_requisicao)

    # 1. Parsing da Requisição
    headers = {}
    metodo = ""
    
    try:
        linhas = dados_requisicao.split('\r\n')
        if not linhas:
            return gerar_resposta_http(400, "Bad Request", "Requisição vazia")

        # Pega o método da primeira linha (ex: "GET / HTTP/1.1")
        linha_requisicao = linhas[0]
        metodo = linha_requisicao.split(' ')[0]

        # Pega os cabeçalhos
        for linha in linhas[1:]:
            if linha == "":
                break  # Fim dos cabeçalhos
            if ":" in linha:
                chave, valor = linha.split(":", 1)
                headers[chave.strip().lower()] = valor.strip()
    
    except Exception as e:
        print(f"Erro no parsing: {e}")
        return gerar_resposta_http(400, "Bad Request", f"Erro ao processar requisição: {e}")

    # 2. Validação do Método
    # O projeto pede para o aluno definir as primitivas. Vamos aceitar apenas GET.
    if metodo != "GET":
        print(f"Método não permitido: {metodo}")
        return gerar_resposta_http(405, "Method Not Allowed", "Método não permitido. Use GET.")

    # 3. Validação do X-Custom-ID
    custom_id_recebido = headers.get('x-custom-id')
    
    if not custom_id_recebido:
        print("Cabeçalho X-Custom-ID ausente.")
        return gerar_resposta_http(403, "Forbidden", "Cabeçalho X-Custom-ID ausente.")

    if custom_id_recebido != X_CUSTOM_ID_ESPERADO:
        print(f"X-Custom-ID inválido. Recebido: {custom_id_recebido}")
        return gerar_resposta_http(403, "Forbidden", "X-Custom-ID inválido.")

    # 4. Sucesso
    print("Requisição válida (GET e X-Custom-ID corretos).")
    return gerar_resposta_http(200, "OK", "Servidor Sequencial: Requisição válida recebida com sucesso!\n")


def iniciar_servidor():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((HOST, PORT))
        servidor.listen(1)

        print(f"Servidor sequencial iniciado em {HOST}:{PORT}")
        print(f"X-Custom-ID Esperado: {X_CUSTOM_ID_ESPERADO}\n")

        while True:
            conexao, endereco = servidor.accept()
            print(f"Conexão recebida de {endereco}")

            with conexao:
                dados = conexao.recv(1024).decode("utf-8")
                if not dados:
                    print("Conexão vazia, fechando.")
                    continue
                
                # Processa a requisição e obtém a resposta
                resposta = processar_requisicao(dados)
                
                # Envia a resposta
                conexao.sendall(resposta)
                print("Resposta enviada e conexão encerrada.\n")


if __name__ == "__main__":
    iniciar_servidor()