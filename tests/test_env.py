from cryptodataset.envs import TradingEnv


def test_tradingenv():
    init_cash = 25000
    env = TradingEnv(exchange='KuCoin', init_cash=init_cash)

    _ = env.reset()
    done = False
    while not done:
        state, reward, done, info = env.step(0.0)

    assert env.values[-1] == init_cash
