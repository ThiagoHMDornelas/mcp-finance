# AGENTS.md — mcp-finance

Monorepo MCP: servidor de ferramentas financeiras (FastMCP + yfinance) consumido por um agente ReAct (LangGraph + OpenAI). FastMCP 3.1.1 · yfinance 1.2.0 · LangGraph 1.1.3 · langchain-mcp-adapters 0.2.2 · langchain-openai 1.1.11 · pytest 9.1.1 · flake8 7.3.0 · Python 3.11 (CI/Docker).

## Contexto em camadas
`SOUL.md` (regras globais do agente) → `AGENTS.md` da pasta da linguagem (regras comuns) → este arquivo (particularidades do projeto). Em conflito, vale o mais específico (este arquivo), exceto em regras de segurança/global.

## Arquitetura

Monorepo com **duas unidades independentes** (cada uma com requirements, Dockerfile e pytest.ini próprios), ligadas pelo transporte MCP:

| Pasta | Papel | Observações |
|---|---|---|
| `server/` | Servidor MCP (`main.py`) | 3 tools: `get_current_stock_price`, `get_history_stock_price` (parâmetro `period`: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max), `get_company_info` — todas via `yf.Ticker` |
| `server/tests/` | Testes pytest | Mockam `yf.Ticker` com `MagicMock` + `monkeypatch` (testes offline por natureza) |
| `agent/` | Agente ReAct (`mcp_agent.py`) | `create_react_agent` + `MemorySaver` em memória, loop REPL com `input()`; `thread_id` fixo `'1'` |
| `agent/mcp_servers.py` | Config do transporte | `build_server_config()`: `http` → `streamable_http` + `MCP_SERVER_URL` (default `http://localhost:8001/mcp`); `stdio` (padrão) → roda o `server/main.py` com `sys.executable` |
| `agent/tests/` | Unit + integração | `test_integration.py` tem `skipif` quando `fastmcp`/`server/main.py` não estão disponíveis |
| `agent/examples/` | Exemplos de uso direto das tools | `sample_agent.py`, `tools.py` |
| `.flake8` | Config compartilhada | Exclui `.venv`, `.git`; ignora `E501` |

## Contrato servidor ↔ agente

- O servidor **não conhece** o agente; o agente descobre as tools em runtime via `MultiServerMCPClient.get_tools()`. Renomear/assinar tools é breaking change: atualizar `agent/tests` (`EXPECTED_TOOLS`).
- Em `stdio` o próprio processo do agente **sobe o servidor como subprocesso** (command padrão = `sys.executable`, path padrão = `../server/main.py`) — não rodar dois servidores na mesma máquina sem ajustar variáveis.

O `.env` é lido **na raiz do monorepo** (o agente faz `load_dotenv()` a partir de `agent/`), não por pasta.

## Testes e lint

- Cada unidade tem sua suíte pytest e seu `pytest.ini` próprio (`pythonpath = .`, `testpaths = tests`): rodar pytest da **raiz não coleta os dois** — executar por pasta (`server/` e `agent/`).
- Lint com flake8 a partir da raiz (config única, compartilhada).
- CI (`.github/workflows/tests.yml`, Python 3.11): flake8 e depois `pytest -q` em `server/` e `agent/` com `working-directory` — exatamente a rotina acima.
- Testes do agente em modo stdio sobem o servidor real; a suíte é pensada para funcionar offline (`skipif` de integração).

## Variáveis de ambiente (.env.example, na raiz)

- `OPENAI_API_KEY` — obrigatória só para o agente
- `OPENAI_MODEL` — default `gpt-4o-mini`
- `MCP_TRANSPORT` — `stdio` (padrão) ou `http`
- `MCP_SERVER_URL` — só com `http`
- `MCP_SERVER_PATH` / `MCP_SERVER_COMMAND` — opcionais, só com `stdio` (default: `../server/main.py` e o mesmo interpretador do agente)

## Docker

- Serviço `mcp_server` (porta `8001`); o agente interativo exige `--profile agent` na chamada ao compose.
- O agente em Docker usa `MCP_TRANSPORT=http` e `MCP_SERVER_URL=http://mcp_server:8001/mcp`; `OPENAI_API_KEY` vem do `.env` raiz.
- Porta 8001 ocupada (`Address already in use`) → `docker compose down` e revisar mapeamento.

## Dados externos

Cotações vêm do Yahoo Finance (`yfinance`) — chamadas de rede sujeitas a rate limit: testes nunca devem chamá-lo sem mock.

## Convenções

- Secrets **sempre** em `.env` (nunca hardcode); mantenha o `.env.example` atualizado e o `.env` fora do versionamento.
- Mensagens de UI/validação em português do Brasil, revisadas (acentuação e concordância).
- Não commitar/pushar por conta própria: as alterações ficam prontas para o usuário revisar e commitar.
- Preservar encoding dos arquivos ao editar (não converter ANSI ↔ UTF-8 sem pedido explícito).
