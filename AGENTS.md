# AGENTS.md — mcp-finance

> Gerado automaticamente na clonagem para a VPS (21/10/2026). **Revisar**: ajuste o que não bater com a realidade do projeto.

## Visão geral
Projeto de referência **MCP**: servidor de ferramentas financeiras (FastMCP + yfinance) consumido por um agente ReAct (LangGraph + OpenAI). Monorepo com duas partes independentes.

**Stack:** FastMCP 3.1 · yfinance · LangGraph 1.1 · langchain-mcp-adapters · OpenAI · pytest · flake8 · Python 3.11 · Docker

## Contexto em camadas
`~/.hermes/SOUL.md` (regras globais) → `~/projetos/python/AGENTS.md` (regras da linguagem) → este arquivo (particularidades do projeto).
Em conflito, vale o mais específico (este arquivo), exceto em regras de segurança/global.

## Estrutura
- `server/` — servidor MCP (`main.py`), `requirements.txt`, `pytest.ini`, `tests/`, `Dockerfile`
- `agent/` — agente LangGraph (`mcp_agent.py`, `mcp_servers.py`), `examples/`, `tests/`, `Dockerfile`
- `.flake8` na raiz vale para o monorepo

## Como rodar
```bash
# servidor (uma vez)
cd server && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements_dev.txt && python main.py

# agente
cd ../agent && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements_dev.txt && python mcp_agent.py
```

## Testes e lint
```bash
cd server && pytest -q
cd agent  && pytest -q
flake8
```
Cada pasta tem seu próprio `pytest.ini` — rodar da raiz não coleta os dois.

## Particularidades
- `MCP_TRANSPORT=stdio` (padrão) ou `http`; em `http` usar `MCP_SERVER_URL`, em `stdio` os caminhos/comando do servidor.
- `OPENAI_API_KEY` é obrigatória só para o agente.
- Dados vêm do Yahoo Finance (`yfinance`) — chamadas externas, sujeitas a rate limit; testes não devem depender da rede.

## Convenções
- Secrets **sempre** em `.env` (nunca hardcode); mantenha o `.env.example` atualizado e o `.env` fora do versionamento.
- Migrações que apagam ou tornam campo obrigatório sem `default` precisam de aviso antes de rodar em produção.
- Mensagens de UI/validação em português do Brasil, revisadas (acentuação e concordância).
- Não commitar/pushar por conta própria: as alterações ficam prontas para o usuário revisar e commitar.
- Preservar encoding dos arquivos ao editar (não converter ANSI ↔ UTF-8 sem pedido explícito).
