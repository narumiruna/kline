import pytest

from .base import OHLCV
from .max import MAXData


@pytest.fixture
def max_data() -> MAXData:
    return MAXData()


def test_max_ohlcv_get_ohlcv_limit(max_data: MAXData) -> None:
    symbol = "BTCUSDT"
    timeframe = "1d"
    limit = 30

    ohlcvs = max_data.fetch_ohlcv(symbol, timeframe, limit)

    assert all([isinstance(ohlcv, OHLCV) for ohlcv in ohlcvs])
    assert len(ohlcvs) == limit
