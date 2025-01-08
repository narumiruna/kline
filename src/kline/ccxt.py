from pathlib import Path

import ccxt
import pandas as pd
from loguru import logger

from .base import OHLCV
from .base import BaseFetcher


def parse_ohlcv(all_ohlcv: list[OHLCV]) -> pd.DataFrame:
    df = pd.DataFrame(
        [ohlcv.model_dump() for ohlcv in all_ohlcv],
        columns=["timestamp", "open", "high", "low", "close", "volume"],
    )
    df = df.drop_duplicates("timestamp")
    df["datetime"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df


class CCXTFetcher(BaseFetcher):
    exchange: ccxt.Exchange

    def __init__(self, exchange: str) -> None:
        self.exchange = getattr(ccxt, exchange.lower())()

    def get_market_symbols(self) -> list[str]:
        return [market["symbol"] for market in self.exchange.fetch_markets()]

    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int | None = None) -> list[OHLCV]:
        logger.info(
            "fetching {} ohlcv form {} with timeframe {}",
            symbol,
            self.exchange.name,
            timeframe,
        )

        since = None

        ohlcvs: list[list[int | float]] = []
        while True:
            if limit is not None and len(ohlcvs) >= limit:
                ohlcvs = ohlcvs[-limit:]
                break

            if since is not None:
                logger.info(
                    "fetch {} ohlcv with timeframe {} from {}", symbol, timeframe, pd.to_datetime(since, unit="ms")
                )

            ohlcv: list[list[int | float]] = self.exchange.fetch_ohlcv(symbol=symbol, timeframe=timeframe, since=since)
            ohlcv.sort(key=lambda k: k[0])

            if not ohlcv:
                break

            if ohlcvs and ohlcv[0][0] == ohlcvs[0][0]:
                break

            ohlcvs = ohlcv + ohlcvs

            # a small amount of overlap to make sure the final data is continuous
            since = ohlcv[0][0] - to_milliseconds(timeframe) * (len(ohlcv) - 1)

        return [
            OHLCV(
                timestamp=int(ohlcv[0]),
                open=ohlcv[1],
                high=ohlcv[2],
                low=ohlcv[3],
                close=ohlcv[4],
                volume=ohlcv[5],
            )
            for ohlcv in ohlcvs
        ]

    def build_path(self, output_dir: str | Path, symbol: str, timeframe: str) -> Path:
        if isinstance(output_dir, str):
            output_dir = Path(output_dir)

        return output_dir / "{}_{}_{}.csv".format(self.exchange.name, symbol.replace("/", "").upper(), timeframe)

    def download_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        limit: int | None = None,
        output_dir: str | Path = "data",
        skip: bool = False,
    ) -> pd.DataFrame:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        csv_path = self.build_path(output_dir, symbol, timeframe)

        if skip and csv_path.exists():
            logger.info("{} already exists, reading data from file", csv_path)

            df = pd.read_csv(csv_path)
            df["datetime"] = pd.to_datetime(df["timestamp"], unit="ms")
            return df

        df = parse_ohlcv(self.fetch_ohlcv(symbol, timeframe, limit=limit))
        logger.info("saving ohlcv to {}", csv_path)
        df.to_csv(csv_path, index=False)

        return df


def to_milliseconds(timeframe: str) -> int:
    return {
        "1s": 1000,
        "15s": 1000 * 15,
        "1m": 1000 * 60,
        "5m": 1000 * 60 * 5,
        "15m": 1000 * 60 * 15,
        "1h": 1000 * 60 * 60,
        "4h": 1000 * 60 * 60 * 4,
        "1d": 1000 * 60 * 60 * 24,
        "3d": 1000 * 60 * 60 * 24 * 3,
        "1w": 1000 * 60 * 60 * 24 * 7,
        "2w": 1000 * 60 * 60 * 24 * 14,
        "1M": 1000 * 60 * 60 * 24 * 28,
    }[timeframe]
