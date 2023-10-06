import pytest

from cryptodataset.base import OHLCV
from cryptodataset.ccxt import CCXTFetcher


@pytest.fixture
def ccxt_data() -> CCXTFetcher:
    return CCXTFetcher("KuCoin")


def test_ohlcv_get_ohlcv_limit(ccxt_data: CCXTFetcher) -> None:
    symbol = "BTC/USDT"
    timeframe = "1d"
    limit = 30
    ohlcvs = ccxt_data.fetch_ohlcv(symbol, timeframe, limit=limit)

    assert all([isinstance(ohlcv, OHLCV) for ohlcv in ohlcvs])
    assert len(ohlcvs) == limit
