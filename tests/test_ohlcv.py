import pandas as pd
import pytest

from cryptodataset import CCXTOHLCVFetcher
from cryptodataset import MAXOHLCVFetcher


@pytest.fixture
def ohlcv_fetcher() -> CCXTOHLCVFetcher:
    return CCXTOHLCVFetcher('Binance')


@pytest.fixture
def max_ohlcv_fetcher() -> MAXOHLCVFetcher:
    return MAXOHLCVFetcher()


def test_ohlcv_fetch_all_ohlcv(ohlcv_fetcher: CCXTOHLCVFetcher) -> None:
    symbol = 'BTC/USDT'
    timeframe = '1d'
    df = ohlcv_fetcher.fetch_all(symbol, timeframe)

    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0


def test_max_ohlcv_fetch_all(max_ohlcv_fetcher: MAXOHLCVFetcher) -> None:
    symbol = 'BTCUSDT'
    timeframe = '1d'

    df = max_ohlcv_fetcher.fetch_all(symbol, timeframe)
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
