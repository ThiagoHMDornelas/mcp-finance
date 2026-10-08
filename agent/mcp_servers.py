import os
import sys
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

DEFAULT_SERVER_PATH = Path(__file__).resolve().parent.parent / 'server' / 'main.py'


def build_server_config() -> dict:
    if os.getenv('MCP_TRANSPORT', 'stdio') == 'http':
        return {
            'url': os.getenv('MCP_SERVER_URL', 'http://localhost:8001/mcp'),
            'transport': 'streamable_http',
        }
    return {
        'command': os.getenv('MCP_SERVER_COMMAND', sys.executable),
        'args': [os.getenv('MCP_SERVER_PATH', str(DEFAULT_SERVER_PATH))],
        'transport': 'stdio',
    }


MCP_SERVERS_CONFIG = {
    'yfinance': build_server_config(),
}
