from itertools import product
from pathlib import Path
from typing import List

import ccxt
import click
from loguru import logger

from . import CCXTOHLCVFetcher
from . import MAXOHLCVFetcher
from .max import get_markets
from .utils import create_exchange_from_env


def download_ohlcv(exchange: ccxt.Exchange, symbol: str, timeframe: str, output_dir: Path) -> None:
    ohlcv_fetcher = CCXTOHLCVFetcher(exchange.name)
    df = ohlcv_fetcher.fetch_all(symbol, timeframe)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / '{}_{}_{}.csv'.format(exchange.name, symbol.replace('/', '').upper(), timeframe)

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

    for s, tf in product(symbol, timeframe):
        download_ohlcv(exchange, s, tf, output_dir)


def download_max_ohlcv(symbol: str, timeframe: str, output_dir: Path) -> None:
    df = MAXOHLCVFetcher().fetch_all(symbol, timeframe)

    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / 'MAX_{}_{}.csv'.format(symbol.replace('/', '').upper(), timeframe)

    logger.info('saving ohlcv to {}', csv_path)
    df.to_csv(csv_path, index=False)


@cli.command()
@click.option('-s', '--symbol', type=click.STRING, default=['BTC/USDT'], multiple=True, help='symbol to download')
@click.option('-t', '--timeframe', type=click.STRING, default=['1d'], multiple=True, help='timeframe')
@click.option('-o', '--output-dir', type=click.STRING, default='data', help='output directory')
@click.option('--all-symbols', is_flag=True, help='download all symbols')
def max(symbol: List[str], timeframe: List[str], output_dir: str, all_symbols: bool) -> None:
    output_dir = Path(output_dir)

    if all_symbols:
        symbol = get_markets()

    for s, tf in product(symbol, timeframe):
        download_max_ohlcv(s, tf, output_dir)


if __name__ == '__main__':
    cli()
