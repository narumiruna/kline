import pandas as pd
import pytest

from .deribit import DeribitData


@pytest.fixture
def deribit_data() -> DeribitData:
    return DeribitData()


def test_ohlcv_fetch_all_ohlcv(deribit_data: DeribitData) -> None:
    currency = 'BTC'
    timeframe = '1d'
    df = deribit_data.get_ohlcv(currency, timeframe)

    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
