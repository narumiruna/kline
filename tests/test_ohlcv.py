import ccxt
import pandas as pd
import pytest

from cryptodataset import MAXOHLCVFetcher
from cryptodataset import OHLCVFetcher


@pytest.fixture
def exchange() -> ccxt.Exchange:
    return ccxt.binance()


@pytest.fixture
def ohlcv_fetcher(exchange: ccxt.Exchange) -> OHLCVFetcher:
    return OHLCVFetcher(exchange)


@pytest.fixture
def max_ohlcv_fetcher() -> MAXOHLCVFetcher:
    return MAXOHLCVFetcher()


def test_ohlcv_fetch_all_ohlcv(ohlcv_fetcher: OHLCVFetcher) -> None:
    symbol = 'BTC/USDT'
    timeframe = '1d'
    df = ohlcv_fetcher.fetch_all_ohlcv(symbol, timeframe)

    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0


def test_max_ohlcv_fetch_all(max_ohlcv_fetcher: MAXOHLCVFetcher) -> None:
    symbol = 'BTCUSDT'
    timeframe = '1d'

    df = max_ohlcv_fetcher.fetch_all(symbol, timeframe)
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
