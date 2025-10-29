# Projeto de Servidores Web Sequencial vs Concorrente (Redes de Computadores II - UFPI)

Este projeto implementa e avalia o desempenho de um servidor web sequencial (síncrono) e um concorrente (assíncrono) usando sockets Python, TCP e Docker, conforme especificado na Segunda Avaliação de Redes de Computadores II.

**Aluno:** [Camila Moura]
**Matrícula:** [20219041293]

---

## 1. Links do Projeto

- **Link do GitHub:** [ ]
- **Link do Vídeo (YouTube):** [https://youtu.be/TXE8-8TR_0g]

---

## 2. Tecnologias Utilizadas

- **Linguagem:** Python
- **Protocolos:** TCP/IP e HTTP (mensagens customizadas)
- **Biblioteca de Criptografia:** [hashlib] (para o X-Custom-ID)
- **Concorrência:** [Threads ou Multiprocess]
- **Ambiente de Rede:** Docker (Containers Ubuntu)
- **Arquivos de Ambiente:** `Dockerfile` e `docker-compose.yml`

---

## 3. Estrutura do Projeto
O projeto está organizado da seguinte forma:

.
├── docker-compose.yml      # Orquestra os containers da rede
├── Dockerfile              # Imagem base para cliente e servidores
├── relatorio/
│   └── relatorio_final.pdf # Relatório no formato SBC
├── server_sequencial.py    # Implementação do servidor sequencial
├── server_concorrente.py   # Implementação do servidor concorrente
├── cliente.py              # Lógica do cliente para gerar requisições
├── testes.py               # Script para automatizar os testes e gerar métricas
└── README.md               # Este arquivo


## 4. Configuração do Ambiente

**4.1. Configuração de Rede (Docker)**

    Conforme a especificação do projeto, a rede Docker é customizada para usar uma sub-rede baseada nos quatro últimos dígitos da matrícula.

    Matrícula: 2021901293

    Sub-rede definida no docker-compose.yml: 12.93.0.0/24
    Os serviços (containers) terão IPs fixos nesta faixa para facilitar os testes (ex: 12.93.0.2, 12.93.0.3, ...).

**4.2. Cabeçalho HTTP X-Custom-ID**

    Todas as requisições feitas pelo cliente (cliente.py) incluem o cabeçalho obrigatório X-Custom-ID. O valor deste cabeçalho é o HASH (MD5 ou SHA-1) da string 20219041293 Camila Moura

## 5. Como Executar o Projeto

**Pré-requisitos:**

    Instalar Docker
    Instalar Docker Compose

**Passo 1: Construir e Iniciar os Containers**
    No diretório raiz do projeto, abra o terminal e execute:

        docker-compose up --build -d

**Passo 2: Verificar os Containers**
    Após a execução, verifique se todos os containers (ex: servidor_seq, servidor_conc, cliente) estão em execução:

        docker ps

**Passo 3: Executar os Testes**
    Para rodar a suíte de testes (que executa as 10+ execuções, coleta métricas, etc.), entre no container do cliente:

        docker exec -it [nome_container_cliente] bash

    Substitua [nome_container_cliente] pelo nome/ID do container cliente

    Dentro do container, execute o script de testes:
        python testes.py


**Passo 4: Parar o Ambiente**
    Para parar e remover todos os containers e a rede:
    
        docker-compose down
