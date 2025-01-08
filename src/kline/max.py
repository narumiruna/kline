from pathlib import Path
from typing import Any

import httpx
import pandas as pd
from loguru import logger

from .base import OHLCV
from .base import BaseFetcher

BASE_URL = "https://max-api.maicoin.com"


def parse_ohlcv(ohlcvs: list[OHLCV]) -> pd.DataFrame:
    df = pd.DataFrame(
        [ohlcv.dict() for ohlcv in ohlcvs],
        columns=["timestamp", "open", "high", "low", "close", "volume"],
    )
    df = df.drop_duplicates("timestamp")
    df["timestamp"] = df["timestamp"] * 1000
    df["datetime"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df


def get_klines(market: str, limit: int = 10000, period: int = 1, timestamp: int | None = None) -> Any:
    url = f"{BASE_URL}/api/v2/k"

    params = {
        "market": market.replace("/", "").lower(),
        "limit": str(limit),
        "period": str(period),
    }
    if timestamp is not None:
        params["timestamp"] = str(timestamp)

    resp = httpx.get(url, params=params)
    resp.raise_for_status()
    return resp.json()


class MAXFetcher(BaseFetcher):
    def get_market_symbols(self) -> list[Any]:
        url = f"{BASE_URL}/api/v2/markets"
        resp = httpx.get(url)
        resp.raise_for_status()
        return [market["name"] for market in resp.json()]

    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int | None = None) -> list[OHLCV]:
        logger.info("fetching {} ohlcv form MaiCoin MAX with timeframe {}", symbol, timeframe)

        since = None

        ohlcvs: list[list[int | float]] = []
        while True:
            if limit is not None and len(ohlcvs) >= limit:
                ohlcvs = ohlcvs[-limit:]
                break

            if since is not None:
                logger.info(
                    "fetch {} ohlcv with timeframe {} from {}", symbol, timeframe, pd.to_datetime(since, unit="s")
                )
            ohlcv = get_klines(symbol, period=to_minutes(timeframe), timestamp=since)

            ohlcv.sort(key=lambda k: k[0])

            if ohlcvs and ohlcv[0][0] == ohlcvs[0][0]:
                break

            ohlcvs = ohlcv + ohlcvs

            # a small amount of overlap to make sure the final data is continuous
            since = ohlcv[0][0] - to_seconds(timeframe) * (len(ohlcv) - 1)

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
        csv_path = output_dir / "MAX_{}_{}.csv".format(symbol.replace("/", "").upper(), timeframe)

        if skip and csv_path.exists():
            logger.info("{} already exists, skip", csv_path)
            df = pd.read_csv(csv_path)
            df["datetime"] = pd.to_datetime(df["timestamp"], unit="s")
            return df

        df = parse_ohlcv(self.fetch_ohlcv(symbol, timeframe, limit=limit))
        logger.info("saving ohlcv to {}", csv_path)
        df.to_csv(csv_path, index=False)

        return df


def to_seconds(timeframe: str) -> int:
    return {
        "1m": 60,
        "5m": 60 * 5,
        "15m": 60 * 15,
        "30m": 60 * 30,
        "1h": 60 * 60,
        "2h": 60 * 60 * 2,
        "4h": 60 * 60 * 4,
        "6h": 60 * 60 * 6,
        "12h": 60 * 60 * 12,
        "1d": 60 * 60 * 24,
        "3d": 60 * 60 * 24 * 3,
        "1w": 60 * 60 * 24 * 7,
    }[timeframe]


def to_minutes(timeframe: str) -> int:
    return {
        "1m": 1,
        "5m": 5,
        "15m": 15,
        "30m": 30,
        "1h": 60,
        "2h": 60 * 2,
        "4h": 60 * 4,
        "6h": 60 * 6,
        "12h": 60 * 12,
        "1d": 60 * 24,
        "3d": 60 * 24 * 3,
        "1w": 60 * 24 * 7,
    }[timeframe]


def to_milliseconds(timeframe: str) -> int:
    return {
        "1m": 1000 * 60,
        "5m": 1000 * 60 * 5,
        "15m": 1000 * 60 * 15,
        "30m": 1000 * 60 * 30,
        "1h": 1000 * 60 * 60,
        "2h": 1000 * 60 * 60 * 2,
        "4h": 1000 * 60 * 60 * 4,
        "6h": 1000 * 60 * 60 * 6,
        "12h": 1000 * 60 * 60 * 12,
        "1d": 1000 * 60 * 60 * 24,
        "3d": 1000 * 60 * 60 * 24 * 3,
        "1w": 1000 * 60 * 60 * 24 * 7,
    }[timeframe]
