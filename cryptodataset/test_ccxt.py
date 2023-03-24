import pandas as pd
import pytest

from .ccxt import CCXTData


@pytest.fixture
def ccxt_data() -> CCXTData:
    return CCXTData('KuCoin')


def test_ohlcv_get_ohlcv_limit(ccxt_data: CCXTData) -> None:
    symbol = 'BTC/USDT'
    timeframe = '1d'
    limit = 30
    df = ccxt_data.get_ohlcv(symbol, timeframe, limit=limit)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == limit
