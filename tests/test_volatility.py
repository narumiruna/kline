import pandas as pd
import pytest

from cryptodataset.volatility import VolatilityFetcher


@pytest.fixture
def volatility_fetcher() -> VolatilityFetcher:
    return VolatilityFetcher()


def test_ohlcv_fetch_all_ohlcv(volatility_fetcher: VolatilityFetcher) -> None:
    currency = 'BTC'
    timeframe = '1d'
    df = volatility_fetcher.fetch_all(currency, timeframe)

    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
