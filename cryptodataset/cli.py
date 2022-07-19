from pathlib import Path

import ccxt
import click
from loguru import logger

from .ohlcv import OHLCVFetcher
from .utils import create_exchange_from_env


def download_ohlcv(exchange: ccxt.Exchange, symbol: str, timeframe: str, output_dir: str) -> None:
    ohlcv_fetcher = OHLCVFetcher(exchange)
    df = ohlcv_fetcher.fetch_all_ohlcv(symbol, timeframe)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / '{}_{}_{}.csv'.format(output_dir, exchange.name,
                                                  symbol.replace('/', '').upper(), timeframe.lower())

    logger.info('saving ohlcv to {}', csv_path)
    df.to_csv(csv_path, index=False)


@click.group()
def cli():
    pass


@cli.command()
@click.option('-e', '--exchange-name', type=click.STRING, default='binance')
@click.option('-s', '--symbol', type=click.STRING, default='BTC/USDT')
@click.option('-t', '--timeframe', type=click.STRING, default='1d')
@click.option('-o', '--output-dir', type=click.STRING, default='data')
def download(exchange_name: str, symbol: str, timeframe: str, output_dir: str) -> None:
    exchange = create_exchange_from_env(exchange_name=exchange_name)
    download_ohlcv(exchange, symbol, timeframe, output_dir)
