import click
import pandas as pd
from loguru import logger

from .ohlcv import fetch_all_ohlcv
from .utils import build_filename
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
    df = fetch_all_ohlcv(exchange, symbol, timeframe)

    if filename is None:
        filename = build_filename(exchange.name, symbol, timeframe)

    logger.info('saving all ohlcv to {}', filename)
    df.to_csv(filename)
