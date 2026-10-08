from unittest.mock import MagicMock

import pytest

from examples import tools


@pytest.fixture
def fake_ticker(monkeypatch):
    ticker = MagicMock()
    ticker.fast_info = {'lastPrice': 10.0}
    ticker.history.return_value.to_dict.return_value = {'Close': {0: 1.0}}
    ticker.info = {'shortName': 'Empresa X'}
    monkeypatch.setattr(tools.yf, 'Ticker', lambda symbol: ticker)
    return ticker


def test_get_current_stock_price(fake_ticker):
    assert tools.get_current_stock_price.func('AAPL') == 10.0


def test_get_history_stock_price(fake_ticker):
    resultado = tools.get_history_stock_price.func('AAPL', '1mo')
    assert resultado == {'Close': {0: 1.0}}


def test_get_company_info(fake_ticker):
    assert tools.get_company_info.func('AAPL') == {'shortName': 'Empresa X'}
