import asyncio
from pathlib import Path

import pytest

import mcp_servers

EXPECTED_TOOLS = {
    'get_current_stock_price',
    'get_history_stock_price',
    'get_company_info',
}


def _servidor_disponivel() -> bool:
    if not Path(mcp_servers.DEFAULT_SERVER_PATH).is_file():
        return False
    try:
        import fastmcp  # noqa: F401
    except ImportError:
        return False
    return True


@pytest.mark.skipif(
    not _servidor_disponivel(),
    reason='servidor MCP indisponivel (fastmcp ou server/main.py ausente)',
)
def test_agente_carrega_ferramentas_do_servidor_mcp(monkeypatch):
    from langchain_mcp_adapters.client import MultiServerMCPClient

    monkeypatch.delenv('MCP_TRANSPORT', raising=False)
    monkeypatch.delenv('MCP_SERVER_PATH', raising=False)
    config = {'yfinance': mcp_servers.build_server_config()}

    async def listar_ferramentas():
        client = MultiServerMCPClient(config)
        return await client.get_tools()

    tools = asyncio.run(listar_ferramentas())
    nomes = {tool.name for tool in tools}
    assert nomes == EXPECTED_TOOLS
