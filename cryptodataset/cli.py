import itertools
from pathlib import Path
from typing import List

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
    csv_path = output_dir / '{}_{}_{}.csv'.format(output_dir, exchange.name, symbol.replace('/', '').upper(), timeframe)

    logger.info('saving ohlcv to {}', csv_path)
    df.to_csv(csv_path, index=False)


@click.group()
def cli():
    pass


@cli.command()
@click.option('-e', '--exchange-name', type=click.STRING, default='binance', help='exchange name')
@click.option('-s', '--symbol', type=click.STRING, default=['BTC/USDT'], multiple=True, help='symbol to download')
@click.option('-t', '--timeframe', type=click.STRING, default=['1d'], multiple=True, help='timeframe')
@click.option('-o', '--output-dir', type=click.STRING, default='data', help='output directory')
@click.option('--all-symbols', is_flag=True, help='download all symbols')
@click.option('--all-timeframes', is_flag=True, help='download all timeframes')
def ohlcv(exchange_name: str, symbol: List[str], timeframe: List[str], output_dir: str, all_symbols: bool,
          all_timeframes: bool) -> None:
    """Download OHLCV data from cryptocurrency exchange"""

    exchange = create_exchange_from_env(exchange_name=exchange_name)

    if all_symbols:
        symbol = [market['symbol'] for market in exchange.fetch_markets()]

    if all_timeframes:
        timeframe = list(exchange.timeframes.keys())

    for s, tf in itertools.product(symbol, timeframe):
        download_ohlcv(exchange, s, tf, output_dir)


if __name__ == '__main__':
    cli()
