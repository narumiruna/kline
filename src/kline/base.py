from __future__ import annotations

import pandas as pd
from pydantic import BaseModel


class BaseFetcher:
    def fetch_ohlcv() -> list[OHLCV]:
        raise NotImplementedError

    def download_ohlcv() -> pd.DataFrame:
        raise NotImplementedError


class OHLCV(BaseModel):
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float | None = None
