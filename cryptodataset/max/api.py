from numbers import Number
from typing import List

import requests

BASE_URL = 'https://max-api.maicoin.com'


def get_klines(market: str, limit: int = 10000, period: int = 1, timestamp: int = None) -> List[List[Number]]:
    url = f'{BASE_URL}/api/v2/k'

    params = {'market': market.replace('/', '').lower(), 'limit': limit, 'period': period}
    if timestamp is not None:
        params['timestamp'] = timestamp

    resp = requests.get(url, params=params)
    return resp.json()


def get_markets() -> List[str]:
    url = f'{BASE_URL}/api/v2/markets'
    resp = requests.get(url)
    return [market['name'] for market in resp.json()]
