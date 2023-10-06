from __future__ import annotations

from typing import List
from typing import Optional

import pandas as pd
from pydantic import BaseModel


class BaseFetcher:
    def fetch_ohlcv() -> List[OHLCV]:
        raise NotImplementedError

    def download_ohlcv() -> pd.DataFrame:
        raise NotImplementedError


class OHLCV(BaseModel):
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: Optional[float] = None
