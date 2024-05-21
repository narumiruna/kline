import pytest

from kline.base import OHLCV
from kline.max import MAXFetcher


@pytest.fixture
def max_data() -> MAXFetcher:
    return MAXFetcher()


def test_max_ohlcv_get_ohlcv_limit(max_data: MAXFetcher) -> None:
    symbol = "BTCUSDT"
    timeframe = "1d"
    limit = 30

    ohlcvs = max_data.fetch_ohlcv(symbol, timeframe, limit)

    assert all(isinstance(ohlcv, OHLCV) for ohlcv in ohlcvs)
    assert len(ohlcvs) == limit
