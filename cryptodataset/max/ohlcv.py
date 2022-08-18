import pandas as pd
from loguru import logger

from ..fetcher import Fetcher
from .api import get_klines


class MAXOHLCVFetcher(Fetcher):

    def fetch_all(self, symbol: str, timeframe: str) -> pd.DataFrame:
        logger.info('fetching {} ohlcv form MaiCoin MAX with timeframe {}', symbol, timeframe)

        since = None
        limit = None

        all_ohlcv = []
        while True:
            logger.info('fetch {} ohlcv with timeframe {} from {}', symbol, timeframe, pd.to_datetime(since, unit='s'))
            ohlcv = get_klines(symbol, period=to_minutes(timeframe), timestamp=since)

            ohlcv.sort(key=lambda k: k[0])

            if limit is None:
                limit = len(ohlcv)

            if all_ohlcv and ohlcv[0][0] == all_ohlcv[0][0]:
                break

            all_ohlcv = ohlcv + all_ohlcv

            # a small amount of overlap to make sure the final data is continuous
            since = ohlcv[0][0] - to_seconds(timeframe) * (limit - 1)

        df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df = df.drop_duplicates('timestamp')
        df['timestamp'] = df['timestamp'] * 1000
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df


def to_seconds(timeframe: str) -> int:
    return {
        '1m': 60,
        '5m': 60 * 5,
        '15m': 60 * 15,
        '30m': 60 * 30,
        '1h': 60 * 60,
        '2h': 60 * 60 * 2,
        '4h': 60 * 60 * 4,
        '6h': 60 * 60 * 6,
        '12h': 60 * 60 * 12,
        '1d': 60 * 60 * 24,
        '3d': 60 * 60 * 24 * 3,
        '1w': 60 * 60 * 24 * 7,
    }[timeframe]


def to_minutes(timeframe: str) -> int:
    return {
        '1m': 1,
        '5m': 5,
        '15m': 15,
        '30m': 30,
        '1h': 60,
        '2h': 60 * 2,
        '4h': 60 * 4,
        '6h': 60 * 6,
        '12h': 60 * 12,
        '1d': 60 * 24,
        '3d': 60 * 24 * 3,
        '1w': 60 * 24 * 7,
    }[timeframe]


def to_milliseconds(timeframe: str) -> int:
    return {
        '1m': 1000 * 60,
        '5m': 1000 * 60 * 5,
        '15m': 1000 * 60 * 15,
        '30m': 1000 * 60 * 30,
        '1h': 1000 * 60 * 60,
        '2h': 1000 * 60 * 60 * 2,
        '4h': 1000 * 60 * 60 * 4,
        '6h': 1000 * 60 * 60 * 6,
        '12h': 1000 * 60 * 60 * 12,
        '1d': 1000 * 60 * 60 * 24,
        '3d': 1000 * 60 * 60 * 24 * 3,
        '1w': 1000 * 60 * 60 * 24 * 7,
    }[timeframe]
