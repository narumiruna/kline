import itertools
from pathlib import Path

from loguru import logger

from cryptodata import fetch_all_ohlcv
from cryptodata.utils import build_filename
from cryptodata.utils import create_exchange_from_env


def main():
    exchange = create_exchange_from_env('binance')
    symbols = [
        'BTC/USDT',
        'ETH/USDT',
        'BNB/USDT',
        'USDC/USDT',
        'XRP/USDT',
        'SOL/USDT',
        'DOGE/USDT',
        'DOT/USDT',
        'MATIC/USDT',
    ]
    timeframes = [
        '1d',
        '1h',
    ]

    for symbol, timeframe in itertools.product(symbols, timeframes):
        df = fetch_all_ohlcv(exchange, symbol, timeframe)

        f = Path('data') / build_filename(exchange.name, symbol, timeframe)
        f.parent.mkdir(parents=True, exist_ok=True)
        logger.info('saving to {}', f)
        df.to_csv(f)


if __name__ == '__main__':
    main()
