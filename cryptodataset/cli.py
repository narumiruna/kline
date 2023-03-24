from itertools import product
from pathlib import Path
from typing import List

import click
from loguru import logger

from . import CCXTData
from . import MAXData


@click.group()
def cli():
    pass


@cli.command()
@click.option('-e', '--exchange', type=click.STRING, default='binance', help='exchange name')
@click.option('-s', '--symbol', type=click.STRING, default=['BTC/USDT'], multiple=True, help='symbol to download')
@click.option('-t', '--timeframe', type=click.STRING, default=['1d'], multiple=True, help='timeframe')
@click.option('-o', '--output-dir', type=click.STRING, default='data', help='output directory')
@click.option('--all-symbols', is_flag=True, help='download all symbols')
@click.option('--all-timeframes', is_flag=True, help='download all timeframes')
@click.option('--skip', is_flag=True, help='skip existing files')
def ccxt(exchange: str, symbol: List[str], timeframe: List[str], output_dir: str, all_symbols: bool,
         all_timeframes: bool, skip: bool) -> None:
    """Download OHLCV data from cryptocurrency exchange"""
    ccxt_data = CCXTData(exchange)

    if all_symbols:
        symbol = ccxt_data.get_market_symbols()

    if all_timeframes:
        timeframe = list(ccxt_data.exchange.timeframes.keys())

    for s, tf in product(symbol, timeframe):
        try:
            ccxt_data.download_ohlcv(s, tf, output_dir=output_dir, skip=skip)
        except Exception as e:
            logger.error(e)


@cli.command()
@click.option('-s', '--symbol', type=click.STRING, default=['BTC/USDT'], multiple=True, help='symbol to download')
@click.option('-t', '--timeframe', type=click.STRING, default=['1d'], multiple=True, help='timeframe')
@click.option('-o', '--output-dir', type=click.STRING, default='data', help='output directory')
@click.option('--all-symbols', is_flag=True, help='download all symbols')
@click.option('--skip', is_flag=True, help='skip existing files')
def max(symbol: List[str], timeframe: List[str], output_dir: str, all_symbols: bool, skip: bool) -> None:
    output_dir = Path(output_dir)

    max_data = MAXData()

    if all_symbols:
        symbol = max_data.get_market_symbols()

    for s, tf in product(symbol, timeframe):
        try:
            max_data.download_ohlcv(s, tf, output_dir=output_dir, skip=skip)
        except Exception as e:
            logger.error(e)


if __name__ == '__main__':
    cli()
