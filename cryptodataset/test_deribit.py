import pytest

from .base import OHLCV
from .deribit import DeribitData


@pytest.fixture
def deribit_data() -> DeribitData:
    return DeribitData()


def test_ohlcv_fetch_all_ohlcv(deribit_data: DeribitData) -> None:
    currency = "BTC"
    timeframe = "1d"
    ohlcvs = deribit_data.fetch_ohlcv(currency, timeframe)

    assert all([isinstance(ohlcv, OHLCV) for ohlcv in ohlcvs])
    assert len(ohlcvs) > 0
