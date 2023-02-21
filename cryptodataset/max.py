from numbers import Number
from pathlib import Path
from typing import List
from typing import Optional
from typing import Union

import pandas as pd
import requests
from loguru import logger

from .base import Base

BASE_URL = 'https://max-api.maicoin.com'


def get_klines(market: str, limit: int = 10000, period: int = 1, timestamp: int = None) -> List[List[Number]]:
    url = f'{BASE_URL}/api/v2/k'

    params = {'market': market.replace('/', '').lower(), 'limit': limit, 'period': period}
    if timestamp is not None:
        params['timestamp'] = timestamp

    resp = requests.get(url, params=params)
    return resp.json()


class MAXData(Base):

    def get_market_symbols(self) -> List[str]:
        url = f'{BASE_URL}/api/v2/markets'
        resp = requests.get(url)
        return [market['name'] for market in resp.json()]

    def get_ohlcv(self, symbol: str, timeframe: str, limit: int = None) -> pd.DataFrame:
        logger.info('fetching {} ohlcv form MaiCoin MAX with timeframe {}', symbol, timeframe)

        since = None

        all_ohlcv = []
        while True:
            if limit is not None and len(all_ohlcv) >= limit:
                all_ohlcv = all_ohlcv[-limit:]
                break

            logger.info('fetch {} ohlcv with timeframe {} from {}', symbol, timeframe, pd.to_datetime(since, unit='s'))
            ohlcv = get_klines(symbol, period=to_minutes(timeframe), timestamp=since)

            ohlcv.sort(key=lambda k: k[0])

            if all_ohlcv and ohlcv[0][0] == all_ohlcv[0][0]:
                break

            all_ohlcv = ohlcv + all_ohlcv

            # a small amount of overlap to make sure the final data is continuous
            since = ohlcv[0][0] - to_seconds(timeframe) * (len(ohlcv) - 1)

        df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df = df.drop_duplicates('timestamp')
        df['timestamp'] = df['timestamp'] * 1000
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df

    def download_ohlcv(self,
                       symbol: str,
                       timeframe: str,
                       limit: Optional[int] = None,
                       output_dir: Union[str, Path] = 'data',
                       skip: bool = False) -> None:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        csv_path = output_dir / 'MAX_{}_{}.csv'.format(symbol.replace('/', '').upper(), timeframe)

        if skip and csv_path.exists():
            logger.info('{} already exists, skip', csv_path)
            return

        df = self.get_ohlcv(symbol, timeframe, limit=limit)
        logger.info('saving ohlcv to {}', csv_path)
        df.to_csv(csv_path, index=False)


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
