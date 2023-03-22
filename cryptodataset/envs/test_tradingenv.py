import pytest

from .trading import TradingEnv


def test_tradingenv():
    init_cash = 25000
    init_quantity = 1.0

    env = TradingEnv(
        exchange='KuCoin',
        symbol='BTC/USDT',
        init_cash=init_cash,
        init_quantity=init_quantity,
    )

    _ = env.reset()
    for _ in range(5):
        state, reward, done, info = env.step(1.0)

    #  pytest assert close values
    assert env.cash == pytest.approx(init_cash, 0.01)
    assert env.quantity == pytest.approx(init_quantity, 0.01)
