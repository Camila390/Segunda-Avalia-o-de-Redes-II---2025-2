import socket
import time
import hashlib

# Configuração do servidor alvo
SERVER_IP = "12.93.0.2"   # IP do servidor dentro da rede Docker
SERVER_PORT = 80         

# Identificação do aluno
MATRICULA = "20219041293"
NOME = "Camila Moura"

# Gera o hash para o cabeçalho X-Custom-ID
def gerar_custom_id():
    data = f"{MATRICULA} {NOME}".encode("utf-8")
    return hashlib.md5(data).hexdigest()

X_CUSTOM_ID = gerar_custom_id()

# Monta a requisição HTTP padrão
def gerar_requisicao_http():
    return (
        "GET / HTTP/1.1\r\n"
        f"Host: {SERVER_IP}\r\n"
        f"X-Custom-ID: {X_CUSTOM_ID}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).encode("utf-8")

def enviar_requisicao():
    try:
        # Cria o socket TCP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVER_IP, SERVER_PORT))

            # Envia a requisição
            requisicao = gerar_requisicao_http()
            inicio = time.time()
            s.sendall(requisicao)

            # Recebe a resposta
            resposta = s.recv(4096)
            fim = time.time()

            tempo = (fim - inicio) * 1000  # tempo em ms
            print(f"\nRequisição enviada com sucesso.")
            print(f"Tempo de resposta: {tempo:.2f} ms")
            print(f"\nResposta recebida:\n{resposta.decode('utf-8')}")

    except ConnectionRefusedError:
        print("Erro: Não foi possível conectar ao servidor.")
    except Exception as e:
        print("Erro:", e)

if __name__ == "__main__":
    enviar_requisicao()
