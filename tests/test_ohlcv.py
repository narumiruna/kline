import pandas as pd
import pytest

from cryptodataset import CCXTData
from cryptodataset import MAXData


@pytest.fixture
def ccxt_data() -> CCXTData:
    return CCXTData('Binance')


@pytest.fixture
def max_data() -> MAXData:
    return MAXData()


def test_ohlcv_fetch_all_ohlcv(ccxt_data: CCXTData) -> None:
    symbol = 'BTC/USDT'
    timeframe = '1d'
    df = ccxt_data.get_ohlcv(symbol, timeframe)

    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0


def test_max_ohlcv_fetch_all(max_data: MAXData) -> None:
    symbol = 'BTCUSDT'
    timeframe = '1d'

    df = max_data.get_ohlcv(symbol, timeframe)
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
