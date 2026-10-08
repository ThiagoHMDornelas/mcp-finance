# mcp-finance — Agente financeiro com MCP (Servidor + Agente)

![Testes](https://github.com/ThiagoHMDornelas/mcp-finance/actions/workflows/tests.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![FastMCP](https://img.shields.io/badge/fastmcp-3.1-8A2BE2)
![LangGraph](https://img.shields.io/badge/LangGraph-1.1-1C3C3C)
![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-000000)
![License](https://img.shields.io/badge/license-MIT-green)

Projeto de referência que mostra, de ponta a ponta, como construir um **servidor MCP** (Model Context Protocol) com **FastMCP** e consumi-lo em um **agente de IA** (LangGraph + OpenAI). O servidor expõe ferramentas de consulta de ações (preços, histórico e dados da empresa, via `yfinance`) e o agente as utiliza para responder perguntas do usuário.

O projeto reúne as duas partes em um **monorepo** — `server/` e `agent/` — com **testes, CI e Docker**.

## Sumário

- [Visão geral](#visão-geral)
- [Arquitetura](#arquitetura)
- [Componentes](#componentes)
- [Tecnologias](#tecnologias)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Pré-requisitos](#pré-requisitos)
- [Instalação e execução](#instalação-e-execução)
- [Executar com Docker](#executar-com-docker)
- [Variáveis de ambiente](#variáveis-de-ambiente)
- [Exemplos](#exemplos)
- [Testes](#testes)
- [Licença](#licença)

## Visão geral

O **Model Context Protocol (MCP)** é um padrão aberto que permite que modelos e agentes descubram e executem ferramentas de forma padronizada. Este projeto demonstra o fluxo completo:

1. O **servidor MCP** (`server/`) registra ferramentas de ações usando o decorador `@mcp.tool` do FastMCP.
2. O **agente** (`agent/`) conecta no servidor com `langchain-mcp-adapters`, descobre as ferramentas e as usa em um loop **ReAct**.

O servidor pode rodar em dois modos:

- **stdio** — o agente inicia o processo do servidor e conversa por entrada/saída padrão.
- **HTTP (streamable-http)** — o servidor roda como serviço independente, em uma porta.

O agente escolhe o transporte por variável de ambiente (`MCP_TRANSPORT`), sem alterar o código.

## Arquitetura

```
Usuário
   │  (terminal)
   ▼
Agente ReAct (LangGraph + gpt-4o-mini)          [agent/]
   │  langchain-mcp-adapters (MultiServerMCPClient)
   │        ┌────────── stdio ──────────┐
   │        └────────── http ───────────┘
   ▼
Servidor MCP (FastMCP)                          [server/]
   │
   ▼
yfinance (Yahoo Finance)
```

## Componentes

### Servidor MCP (`server/`)

Servidor **FastMCP** que expõe três ferramentas para análise de ações:

| Ferramenta | Descrição | Parâmetros |
|---|---|---|
| `get_current_stock_price` | Retorna o preço atual da ação | `ticker` (ex.: `AAPL`) |
| `get_history_stock_price` | Retorna o histórico de preços no período | `ticker`, `period` (ex.: `1d`, `1mo`, `1y`, `max`) |
| `get_company_info` | Retorna dados completos da empresa | `ticker` |

O servidor é **reutilizável**: por seguir o protocolo MCP, pode ser plugado em qualquer cliente compatível (Claude Desktop, Cursor, etc.).

### Agente (`agent/`)

Agente **ReAct** construído com `create_react_agent` (LangGraph) e `ChatOpenAI`. Ele **não** implementa as ferramentas: descobre-as no servidor MCP. Mantém o histórico da conversa em memória (`MemorySaver`) e imprime cada passo no terminal.

> **Nota sobre o aviso `create_react_agent`**: ao rodar o agente, o console exibe um aviso de depreciação do LangGraph (`create_react_agent` foi movido para `langchain.agents.create_agent` na V1.0). É apenas um alerta de versão futura — com as versões fixadas em `agent/requirements.txt`, tudo funciona normalmente.

## Tecnologias

- Python 3.11+
- FastMCP 3.1 e MCP (servidor)
- LangGraph e LangChain + `langchain-mcp-adapters` + OpenAI (agente)
- yfinance (dados do Yahoo Finance)
- python-dotenv (variáveis de ambiente)
- flake8 e pytest (desenvolvimento)
- Docker e Docker Compose
- GitHub Actions (CI)

## Estrutura do projeto

```
mcp-finance/
├── server/                # servidor MCP (FastMCP + yfinance)
│   ├── main.py            # definição das ferramentas
│   ├── tests/             # testes do servidor
│   ├── requirements.txt
│   ├── requirements_dev.txt
│   ├── pytest.ini
│   ├── Dockerfile
│   └── .dockerignore
├── agent/                 # agente (LangGraph + MCP)
│   ├── mcp_agent.py       # agente que consome as ferramentas via MCP
│   ├── mcp_servers.py     # configuração do transporte (stdio/http)
│   ├── examples/          # versão de referência com ferramentas locais
│   ├── tests/             # testes do agente
│   ├── requirements.txt
│   ├── requirements_dev.txt
│   ├── pytest.ini
│   ├── Dockerfile
│   └── .dockerignore
├── .github/workflows/     # pipeline de CI (GitHub Actions)
├── docker-compose.yml
├── .env.example           # exemplo de variáveis de ambiente
├── .flake8
├── .gitignore
├── .gitattributes
├── LICENSE
└── README.md
```

## Pré-requisitos

- Python 3.11 ou superior
- Docker Desktop (opcional, para rodar via containers)
- Uma chave de API da OpenAI (`OPENAI_API_KEY`)

## Instalação e execução

Há **duas formas de rodar localmente**, sem Docker. Escolha conforme o objetivo:

| Modo | Como funciona | Quando usar | Terminais |
|---|---|---|---|
| **1 — stdio** | O agente inicia o servidor como subprocesso; a conversa é por entrada/saída padrão | Desenvolvimento rápido; uso mais simples | 1 |
| **2 — http** | O servidor roda como serviço HTTP em uma porta; o agente conecta pela rede | Simular cliente/servidor separados; depurar o servidor isolado | 2 |

### Preparação (comum aos dois modos)

**1. Clone o repositório e entre na pasta do projeto:**

```powershell
git clone https://github.com/ThiagoHMDornelas/mcp-finance.git
cd mcp-finance
```

> O `git clone` cria a pasta **`mcp-finance`** e o `cd mcp-finance` entra nela. Se você **já tem** o projeto baixado, pule o clone e apenas entre na pasta do projeto.

**2. Crie o arquivo de ambiente e preencha a chave da OpenAI:**

```powershell
copy .env.example .env
```

> Abra o `.env` no editor e preencha `OPENAI_API_KEY=sk-...`. O `.env` **não** é versionado (está no `.gitignore`).

**3. Crie o ambiente virtual e instale as dependências (do agente e do servidor):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r agent\requirements.txt -r server\requirements.txt
pip install -r agent\requirements_dev.txt -r server\requirements_dev.txt
```

### Modo 1 — stdio (mais simples)

**Como funciona:** o agente inicia o processo do servidor sozinho e conversa com ele por **entrada/saída padrão** (`stdio`). Não é preciso subir nenhum servidor nem se preocupar com portas.

- **Quando usar:** desenvolvimento e testes rápidos, no dia a dia.
- **Configuração:** nenhuma — `MCP_TRANSPORT=stdio` já é o padrão.

Com o ambiente virtual ativado, rode:

```powershell
python agent\mcp_agent.py
```

**O que esperar:** o agente carrega as ferramentas do servidor, exibe `Digite:` e responde às perguntas. Exemplo:

    Digite: Qual o preço atual da ação da Apple?
    ... get_current_stock_price(ticker=AAPL) ...
    O preço atual da ação da Apple (AAPL) é de aproximadamente $338,20.

**Encerrar:** `Ctrl+C`.

**Problemas comuns**

- **`Activate.ps1` bloqueado** ("a execução de scripts foi desabilitada neste sistema"): rode uma vez `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` e ative de novo.
- **`ModuleNotFoundError: No module named 'fastmcp'`**: faltou instalar as dependências do servidor; repita `pip install -r server\requirements.txt` com o ambiente ativado.
- **`SSL: CERTIFICATE_VERIFY_FAILED` / "Connection error"**: é a inspeção HTTPS de antivírus/proxy; tente novamente ou exclua o `python.exe`/`api.openai.com` da varredura HTTPS.

### Modo 2 — http (servidor como serviço local)

**Como funciona:** o servidor roda como um serviço **HTTP** em uma porta (`8001`) e o agente se conecta pela rede (`http://localhost:8001/mcp`). Isso simula dois processos separados.

- **Quando usar:** testar/observar o servidor isoladamente ou reproduzir o cenário cliente/servidor real.
- **Requer dois terminais** (os dois na pasta do projeto).

**Terminal A — servidor** (deixe rodando):

```powershell
cd mcp-finance
.\.venv\Scripts\Activate.ps1
fastmcp run server\main.py --transport streamable-http --host 127.0.0.1 --port 8001
```

Espere o banner do **FastMCP** (`yfinance MCP Server`).

**Terminal B — agente:**

```powershell
cd mcp-finance
.\.venv\Scripts\Activate.ps1
$env:MCP_TRANSPORT="http"
$env:MCP_SERVER_URL="http://localhost:8001/mcp"
python agent\mcp_agent.py
```

**O que esperar:** no Terminal A aparecem os logs de requisição do servidor; no Terminal B o agente responde normalmente, agora consumindo as ferramentas **por HTTP**.

**Encerrar:** `Ctrl+C` no Terminal B (agente) e depois no Terminal A (servidor).

> Usei `$env:...` **no terminal** em vez de editar o `.env` — assim volta ao **Modo 1** naturalmente (basta abrir um terminal novo, sem essas variáveis; o `MCP_TRANSPORT` cai no padrão `stdio`).

**Problemas comuns**

- **Porta `8001` ocupada** (`Address already in use`): pare o processo que usa a porta ou um container antigo (`docker compose down`).
- **O agente não conecta no servidor**: confirme que o Terminal A está rodando e exibiu o banner do FastMCP.
- **`SSL: CERTIFICATE_VERIFY_FAILED` / "Connection error"**: é a inspeção HTTPS de antivírus/proxy; tente novamente.

## Executar com Docker

Também é possível rodar **sem instalar Python localmente** (o **Modo 3**). O `docker-compose.yml` define dois serviços:

- **`mcp_server`** — o servidor MCP em modo **HTTP** (porta `8001`).
- **`mcp_agent`** — o agente. É **interativo** e usa a sua `OPENAI_API_KEY`, então roda **sob demanda** (não sobe junto com o `up`) e fica em um *profile* chamado `agent`.

### Pré-requisitos

- **Docker Desktop** instalado e **em execução** (engine ligado).
- Git instalado (para clonar o projeto).
- A porta `8001` livre.

### Passo a passo

**1. Clone o repositório e entre na pasta do projeto** (se ainda não fez):

```powershell
git clone https://github.com/ThiagoHMDornelas/mcp-finance.git
cd mcp-finance
```

**2. Crie o `.env` e preencha a chave da OpenAI.** O Docker lê esse arquivo automaticamente:

```powershell
copy .env.example .env
```

> Abra o `.env` no editor e preencha `OPENAI_API_KEY=sk-...`. Sem a chave, o servidor sobe normalmente, mas o agente não consegue responder.

**3. Suba o servidor.** Na primeira vez ele **compila a imagem** — pode levar alguns minutos:

```powershell
docker compose up -d mcp_server
```

**4. Confira se subiu.** Espere o `mcp_server` aparecer como `Up`:

```powershell
docker compose ps
```

| Serviço | Porta | Descrição |
|---|---|---|
| `mcp_server` | 8001 | Servidor MCP (streamable-http) em `http://localhost:8001/mcp` |

**5. Rode o agente** (interativo, em primeiro plano). O `--profile agent` é **obrigatório** porque o serviço está em um profile; o `--rm` remove o container do agente quando você sai:

```powershell
docker compose --profile agent run --rm mcp_agent
```

> O agente se conecta ao servidor pela rede interna do Docker (`http://mcp_server:8001/mcp`) — você **não** precisa instalar nada de Python.

**O que esperar:** o agente exibe `Digite:`; pergunte algo como *"Qual o preço atual da ação da Apple?"* e ele responde usando as ferramentas do servidor. Para acompanhar as requisições chegando no servidor, abra outro terminal e rode `docker compose logs -f mcp_server`.

**Encerrar:** `Ctrl+C` no agente e depois:

```powershell
docker compose down
```

### Comandos úteis

```powershell
docker compose logs -f mcp_server                # logs do servidor
docker compose --profile agent build             # (re)constrói as duas imagens
docker compose down                              # para e remove os containers
docker compose down --rmi local                  # remove também as imagens do projeto
```

### Problemas comuns

- **Nada sobe / erro de conexão**: confirme que o **Docker Desktop está aberto** (engine em execução).
- **Erro de porta em uso (`8001`)**: pare o serviço que ocupa a porta ou ajuste o mapeamento no `docker-compose.yml` (ex.: `8002:8001`).
- **O agente não conecta**: verifique se o `mcp_server` está `Up` (`docker compose ps`).
- **Sem resposta da OpenAI**: confira a `OPENAI_API_KEY` no `.env`.

## Variáveis de ambiente

| Variável | Padrão | Descrição |
|---|---|---|
| `OPENAI_API_KEY` | — | Chave da OpenAI (obrigatória para o agente) |
| `OPENAI_MODEL` | `gpt-4o-mini` | Modelo usado pelo agente |
| `MCP_TRANSPORT` | `stdio` | Transporte do agente até o servidor: `stdio` ou `http` |
| `MCP_SERVER_URL` | `http://localhost:8001/mcp` | URL do servidor (quando `MCP_TRANSPORT=http`) |
| `MCP_SERVER_PATH` | `../server/main.py` | Caminho do `main.py` do servidor (modo stdio) |
| `MCP_SERVER_COMMAND` | interpretador atual | Interpretador que inicia o servidor (modo stdio) |

## Exemplos

A pasta `agent/examples/` traz uma versão equivalente do agente (`sample_agent.py`) em que as ferramentas são definidas **localmente** (`tools.py`), sem MCP — útil para comparar as duas abordagens:

```powershell
python agent/examples/sample_agent.py
```

## Testes

As dependências de desenvolvimento foram instaladas na [preparação](#preparação-comum-aos-dois-modos). Execute os testes de cada componente a partir da sua pasta:

    cd server && pytest -q
    cd agent  && pytest -q

A suíte do agente inclui um **teste de integração** que sobe o servidor MCP (via `stdio`) e confirma que as 3 ferramentas são carregadas. Ele é pulado automaticamente se o `server/main.py` ou o `fastmcp` não estiverem disponíveis no ambiente.

O **lint** do código é feito com `flake8` (configuração em `.flake8`), a partir da raiz:

    flake8

A suíte e o lint também rodam automaticamente a cada `push` e `pull request` via **GitHub Actions** (`.github/workflows/tests.yml`). O resultado é exibido no badge no topo deste README.

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
