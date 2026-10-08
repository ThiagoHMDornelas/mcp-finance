import sys
from pathlib import Path

import mcp_servers


def test_transporte_stdio_por_padrao(monkeypatch):
    monkeypatch.delenv('MCP_TRANSPORT', raising=False)
    config = mcp_servers.build_server_config()
    assert config['transport'] == 'stdio'
    assert config['command'] == sys.executable
    assert Path(config['args'][0]).name == 'main.py'
    assert Path(config['args'][0]).parent.name == 'server'


def test_transporte_http(monkeypatch):
    monkeypatch.setenv('MCP_TRANSPORT', 'http')
    monkeypatch.setenv('MCP_SERVER_URL', 'http://localhost:8001/mcp')
    config = mcp_servers.build_server_config()
    assert config['transport'] == 'streamable_http'
    assert config['url'] == 'http://localhost:8001/mcp'


def test_config_do_modulo_tem_yfinance():
    assert 'yfinance' in mcp_servers.MCP_SERVERS_CONFIG
    assert 'transport' in mcp_servers.MCP_SERVERS_CONFIG['yfinance']
