import json
from datetime import datetime
from numbers import Number
from typing import List
from typing import Optional

import pandas as pd
import requests
from loguru import logger

from .base import Base


class DeribitData(Base):
    base_url = 'https://www.deribit.com'
    timeframes = {
        '1s': '1',
        '1m': '60',
        '1h': '3600',
        '12h': '43200',
        '1d': '1D',
    }

    def _fetch(self,
               currency: str,
               timeframe: str = '1m',
               since: Optional[int] = None,
               until: Optional[int] = None) -> List[List[Number]]:
        url = f'{self.base_url}/api/v2/public/get_volatility_index_data'

        since = since or 0
        until = until or int(datetime.now().timestamp() * 1000)

        logger.info('fetch {} volatility from {} to {}', currency, pd.to_datetime(since, unit='ms'),
                    pd.to_datetime(until, unit='ms'))

        params = {
            'currency': currency,
            'start_timestamp': since,
            'end_timestamp': until,
            'resolution': self.timeframes[timeframe],  # 1, 60, 3600, 43200 or 1D
        }

        resp = requests.get(url, params=params)
        data = json.loads(resp.text)

        return data['result']['data']

    def get_ohlcv(self, currency: str, timeframe: str = '1m', limit: Optional[int] = None) -> pd.DataFrame:
        """Fetch all volatility index data from deribit

        https://docs.deribit.com/#public-get_volatility_index_data
        """

        until = int(datetime.now().timestamp() * 1000)

        data = []
        while True:
            if limit is not None and len(data) >= limit:
                data = data[-limit:]
                break

            new_data = self._fetch(currency, timeframe, since=0, until=until)

            # break the loop if there is no new data
            if not new_data:
                break

            if data and new_data and new_data[0][0] == data[0][0]:
                break

            data = new_data + data
            until = data[0][0] - 1

        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df = df.drop_duplicates('timestamp')
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')

        return df
