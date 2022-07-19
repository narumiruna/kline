from pathlib import Path

import click
from loguru import logger

from .ohlcv import OHLCVFetcher
from .utils import create_exchange_from_env


@click.group()
def cli():
    pass


@cli.command()
@click.option('-e', '--exchange-name', type=click.STRING, default='binance')
@click.option('-s', '--symbol', type=click.STRING, default='BTC/USDT')
@click.option('-t', '--timeframe', type=click.STRING, default='1h')
@click.option('-f', '--filename', type=click.STRING, default=None)
def download(exchange_name: str, symbol: str, timeframe: str, filename: str) -> None:
    exchange = create_exchange_from_env(exchange_name=exchange_name)
    df = OHLCVFetcher(exchange).fetch_all_ohlcv(symbol, timeframe)

    if filename is None:
        filename = 'data/{}_{}_{}.csv'.format(exchange.name, symbol.replace('/', '').upper(), timeframe.lower())

    Path(filename).parent.mkdir(parents=True, exist_ok=True)

    logger.info('saving all ohlcv to {}', filename)
    df.to_csv(filename, index=False)
