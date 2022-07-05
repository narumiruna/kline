from dataclasses import dataclass
from typing import List

import ccxt
import pandas as pd
from loguru import logger

from .utils import to_datetime


@dataclass
class OHLCV:
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float

    def datetime(self):
        return to_datetime(self.timestamp)

    def __str__(self):
        return f'{self.datetime()} {self.open} {self.high} {self.low} {self.close} {self.volume}'

    def to_dict(self) -> dict:
        return dict(
            timestamp=self.timestamp,
            open=self.open,
            high=self.high,
            low=self.low,
            close=self.close,
            volume=self.volume,
        )


def fetch_all_ohlcv(exchange: ccxt.Exchange, symbol: str, timeframe: str, since: int = 0) -> List[OHLCV]:
    logger.info('fetching {} ohlcv form {} with timeframe {}', symbol, exchange.name, timeframe)

    all_ohlcv = []
    while True:
        batch_ohlcv = [OHLCV(*kline) for kline in exchange.fetch_ohlcv(symbol=symbol, timeframe=timeframe, since=since)]
        batch_ohlcv.sort(key=lambda k: k.timestamp)

        if len(batch_ohlcv) == 0:
            break

        all_ohlcv += batch_ohlcv
        since = batch_ohlcv[-1].timestamp + 1

    return all_ohlcv


def to_dataframe(all_ohlcv: List[OHLCV]) -> pd.DataFrame:
    df = pd.DataFrame([ohlcv.to_dict() for ohlcv in all_ohlcv])
    df.set_index('timestamp', inplace=True)
    return df
