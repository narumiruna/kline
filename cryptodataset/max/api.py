from numbers import Number
from typing import List

import requests


def get_klines(market: str, limit: int = 10000, period: int = 1, timestamp: int = None)-> List[List[Number]]:
    url = 'https://max-api.maicoin.com/api/v2/k'

    params = {'market': market.lower(), 'limit': limit, 'period': period}
    if timestamp is not None:
        params['timestamp'] = timestamp

    resp = requests.get(url, params=params)
    return resp.json()

