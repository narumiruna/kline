import os
from datetime import datetime

import ccxt
from loguru import logger


def to_timestamp(dt: datetime) -> int:
    return int(dt.timestamp() * 1000)


def to_datetime(ts: int) -> datetime:
    return datetime.fromtimestamp(ts / 1000)


def create_exchange_from_env(exchange_name: str) -> ccxt.Exchange:
    logger.info('creating exchange from env')

    config = {
        'apiKey': os.environ.get(f'{exchange_name.upper()}_API_KEY'),
        'secret': os.environ.get(f'{exchange_name.upper()}_API_SECRET'),
    }
    return getattr(ccxt, exchange_name.lower())(config)
