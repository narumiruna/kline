import pandas as pd
import pytest

from .max import MAXData


@pytest.fixture
def max_data() -> MAXData:
    return MAXData()


def test_max_ohlcv_get_ohlcv_limit(max_data: MAXData) -> None:
    symbol = 'BTCUSDT'
    timeframe = '1d'
    limit = 30

    df = max_data.get_ohlcv(symbol, timeframe, limit)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == limit
