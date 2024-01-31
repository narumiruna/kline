import pytest

from cryptodata.base import OHLCV
from cryptodata.deribit import DeribitFetecher


@pytest.fixture
def deribit_data() -> DeribitFetecher:
    return DeribitFetecher()


def test_ohlcv_fetch_all_ohlcv(deribit_data: DeribitFetecher) -> None:
    currency = "BTC"
    timeframe = "1d"
    ohlcvs = deribit_data.fetch_ohlcv(currency, timeframe)

    assert all([isinstance(ohlcv, OHLCV) for ohlcv in ohlcvs])
    assert len(ohlcvs) > 0
