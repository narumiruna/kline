from dataclasses import dataclass

import ccxt
import pandas as pd
from loguru import logger


@dataclass
class OHLCV:
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float

    def __str__(self):
        return f"OHLCV(timestamp={self.timestamp}, open={self.open}, high={self.high}, low={self.low}, close={self.close}, volume={self.volume})"

    def to_dict(self) -> dict:
        return dict(
            timestamp=self.timestamp,
            open=self.open,
            high=self.high,
            low=self.low,
            close=self.close,
            volume=self.volume,
        )


def fetch_all_ohlcv(exchange: ccxt.Exchange, symbol: str, timeframe: str, since: int = 0) -> pd.DataFrame:
    logger.info('fetching {} ohlcv form {} with timeframe {}', symbol, exchange.name, timeframe)

    all_ohlcv = []
    while True:
        batch_ohlcv = [OHLCV(*kline) for kline in exchange.fetch_ohlcv(symbol=symbol, timeframe=timeframe, since=since)]
        batch_ohlcv.sort(key=lambda k: k.timestamp)

        if len(batch_ohlcv) == 0:
            break

        all_ohlcv += batch_ohlcv
        since = batch_ohlcv[-1].timestamp + 1

    df = pd.DataFrame([ohlcv.to_dict() for ohlcv in all_ohlcv])
    df.set_index('timestamp', inplace=True)

    return df
