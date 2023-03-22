import pandas as pd
import pytest

from cryptodataset import CCXTData


@pytest.fixture
def ccxt_data() -> CCXTData:
    return CCXTData('KuCoin')


def test_ohlcv_get_ohlcv(ccxt_data: CCXTData) -> None:
    symbol = 'BTC/USDT'
    timeframe = '1d'
    df = ccxt_data.get_ohlcv(symbol, timeframe)

    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0


def test_ohlcv_get_ohlcv_limit(ccxt_data: CCXTData) -> None:
    symbol = 'BTC/USDT'
    timeframe = '1d'
    limit = 30
    df = ccxt_data.get_ohlcv(symbol, timeframe, limit)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == limit