import math
import random
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

import gym
import numpy as np
import pandas as pd
import pandas_ta as ta
import quantstats as qs
from gym.spaces import Box
from gym.spaces import Discrete
from loguru import logger

from ..ccxt import CCXTData

REWARD_TYPES = ('return', 'log_return')
ACTION_TYPES = ('discrete', 'continuous')

# calculated by scripts/calculate_close_prices_mean_and_std.py
CLOSE_PRICE_MEAN = {
    'ADAUSDT': 0.5011164426755376,
    'APEUSDT': 6.524456809487376,
    'BCHUSDT': 345.22541376228776,
    'BNBUSDT': 149.62331857422726,
    'BTCUSDT': 19459.3699594795,
    'DOGEUSDT': 0.08753216592086445,
    'DOTUSDT': 17.357185317496995,
    'ETCUSDT': 19.264128692045258,
    'ETHUSDT': 1100.951793763185,
    'LTCUSDT': 100.73259433543461,
    'MATICUSDT': 0.602782859471206,
    'SANDUSDT': 1.2599757235559235,
    'SHIBUSDT': 1.7320846892766127e-05,
    'SOLUSDT': 56.60217189662282,
    'XRPUSDT': 0.48026767259376574
}

CLOSE_PRICE_STD = {
    'ADAUSDT': 0.6399649011988369,
    'APEUSDT': 3.6092922412446757,
    'BCHUSDT': 216.88149140644657,
    'BNBUSDT': 182.3235804459624,
    'BTCUSDT': 16583.120717299495,
    'DOGEUSDT': 0.10756096898207089,
    'DOTUSDT': 12.621120000736905,
    'ETCUSDT': 18.72263875299633,
    'ETHUSDT': 1164.9444178121253,
    'LTCUSDT': 62.767330016212966,
    'MATICUSDT': 0.6804862610908117,
    'SANDUSDT': 1.5208289792620078,
    'SHIBUSDT': 1.2435966456449551e-05,
    'SOLUSDT': 61.04868090617073,
    'XRPUSDT': 0.2933438776594941
}


class TradingEnv(gym.Env):

    def __init__(
        self,
        root: str = 'data',
        exchange: str = 'Binance',
        symbol: str = 'BTCUSDT',
        timeframe: str = '1h',
        download: bool = False,
        fee: float = 0.0,
        start: Optional[str] = None,
        end: Optional[str] = None,
        init_cash: float = 25000,
        init_quantity: float = 0.0,
        max_amount: float = 0,
        random_length: int = 0,
        mean: Optional[List[float]] = None,
        std: Optional[List[float]] = None,
        reward_type: str = 'log_return',
        action_type: str = 'discrete',
        metric_currency: str = 'quote',
    ) -> None:
        """Initialize the trading environment.

        Args:
            root (str, optional): the root directory to store the downloaded data. Defaults to 'data'.
            exchange (str, optional): the exchange name. Defaults to 'Binance'.
            symbol (str, optional): the symbol. Defaults to 'BTCUSDT'.
            timeframe (str, optional): the timeframe. Defaults to '1h'.
            download (bool, optional): whether to download the data from exchange. Defaults to False.
            fee (float, optional): the trading fee. Defaults to 0.0.
            start (Optional[str], optional): the start date. Defaults to None.
            end (Optional[str], optional): the end date. Defaults to None.
            init_cash (float, optional): the initial cash. Defaults to 25000.
            init_quantity (float, optional): the initial quantity. Defaults to 0.0.
            max_amount (float, optional): the maximum amount of cash to use for each trade. Defaults to 2000.
            random_length (int, optional): the length of random data to use. Defaults to 0.
            reward_type (str, optional): the reward type. Defaults to 'log_return'.
            action_type (str, optional): the action type. Defaults to 'discrete'.
            metric_currency (str, optional): the currency to use for metrics. Defaults to 'quote'.
        """
        # validate the arguments
        if fee < 0:
            raise ValueError('fee must be non-negative, got {}'.format(fee))
        if random_length < 0:
            raise ValueError('random_length must be non-negative, got {}'.format(random_length))
        if reward_type not in REWARD_TYPES:
            raise ValueError(f'reward_type should be one of {REWARD_TYPES}, got {reward_type}')
        if action_type not in ACTION_TYPES:
            raise ValueError(f'action_type should be one of {ACTION_TYPES}, got {action_type}')

        self.root = root
        self.exchange = exchange
        self.symbol = symbol
        self.timeframe = timeframe
        self.download = download
        self.fee = fee
        self.start = pd.to_datetime(start)
        self.end = pd.to_datetime(end)
        self.init_cash = init_cash
        self.init_quantity = init_quantity
        self.max_amount = max_amount  # in quote currency
        self.random_length = random_length
        self.mean = np.array(mean or 0, dtype=np.float32)
        self.std = np.array(std or 1, dtype=np.float32)
        self.reward_type = reward_type
        self.action_type = action_type
        self.metric_currency = metric_currency

        self.df = self._load_data()

        self.cash = None
        self.quantity = None
        self.features = None
        self.prices = None

        self.step_index = 0
        self.values = []
        self.rewards = []
        self.actions = []
        self.datetimes = []

        self.action_space = self._get_action_space()
        self.observation_space = self._get_observation_space()

    def _load_data(self) -> pd.DataFrame:
        """Load data from local file or download from exchange by ccxt, and preprocess it.

        Returns:
            pd.DataFrame: the loaded and preprocessed data
        """
        df = CCXTData(self.exchange).download_ohlcv(self.symbol,
                                                    self.timeframe,
                                                    output_dir=self.root,
                                                    skip=not self.download)

        # preprocess the data
        df = preprocess(df, self.symbol)

        if self.start is not None:
            df = df.loc[self.start:]
        if self.end is not None:
            df = df.loc[:self.end]

        return df

    def _get_action_space(self):
        """Get the action space of the environment."""
        if self.action_type == 'continuous':
            return Box(low=-1, high=1, shape=(1,), dtype=np.float32)
        elif self.action_type == 'discrete':
            return Discrete(3)
        else:
            raise ValueError(f'unknown action_type {self.action_type}')

    def _get_observation_space(self):
        """Get the observation space of the environment."""
        array = self.df.drop(columns='close').values
        shape = (array.shape[1] + 2,)  # +2 for cash and quantity
        return Box(low=array.max(), high=array.min(), shape=shape, dtype=np.float32)

    def _random_sample_interval(self) -> None:
        """Randomly sample a sub-interval of the data"""
        data_length = len(self.features)

        if self.random_length == 0:
            return

        if self.random_length > data_length:
            logger.warning('random length {} is larger than the length of the data {}', self.random_length, data_length)
            return

        start = random.randint(0, data_length - self.random_length)
        self.features = self.features[start:start + self.random_length]
        self.prices = self.prices[start:start + self.random_length]

    def reset(self) -> np.ndarray:
        """Reset the environment."""
        self.cash = self.init_cash
        self.quantity = self.init_quantity

        self.features = self.df.drop(columns='close').values
        self.prices = self.df['close']

        self._random_sample_interval()

        # all in
        # TODO: add a parameter to control this
        # self.cash, self.quantity = 0, self.cash / self.get_price()

        self.step_index = 0
        self.values = [self.get_account_value()]
        self.rewards = [0.0]
        self.actions = []
        self.datetimes = [self.df.index[self.step_index]]

        return self.get_observation()

    def step(self, action: Union[int, float]) -> Tuple[np.ndarray, float, bool, dict]:
        """Take an action and return the next observation, reward, done flag and info.

        Args:
            action (Union[int, float]): the action to take

        Returns:
            Tuple[np.ndarray, float, bool, dict]: the next observation, reward, done flag and info
        """
        if self.action_type == 'discrete':
            self.take_discrete_action(action)
        elif self.action_type == 'continuous':
            self.take_continuous_action(action)
        else:
            raise ValueError(f'unknown action_type {self.action_type}')

        self.actions.append(action)

        self.step_index += 1

        self.values.append(self.get_account_value())
        self.datetimes.append(self.df.index[self.step_index])

        reward = self.calculate_reward()
        self.rewards.append(reward)

        done = False
        if not (self.step_index + 1 < len(self.prices)):
            done = True

        info = {}
        return self.get_observation(), reward, done, info

    def get_observation(self) -> np.ndarray:
        """Get the current observation of the environment."""
        # get current feature
        current_feature = self.features[self.step_index]

        obs = np.zeros((2 + current_feature.shape[0],))

        # get current price
        price = self.get_price()

        # calculate cash and quantity ratio
        value = self.quantity * price + self.cash
        obs[0] = self.quantity * price / value
        obs[1] = self.cash / value

        obs[2:] = current_feature

        return (obs - self.mean) / self.std

    def calculate_reward(self) -> float:
        """Calculate reward"""
        cur_value = self.values[self.step_index]
        pre_value = self.values[self.step_index - 1]

        if self.reward_type == 'return':
            return cur_value / pre_value - 1
        elif self.reward_type == 'log_return':
            return math.log(cur_value / pre_value)
        else:
            raise ValueError('Unknown reward type: {}'.format(self.reward_type))

    def get_account_value(self) -> float:
        if self.metric_currency == 'quote':
            return self.cash + self.quantity * self.get_price()
        else:
            return self.cash / self.get_price() + self.quantity

    def get_price(self, i: int = None) -> float:
        i = self.step_index if i is None else i
        return float(self.prices.iloc[i])

    def get_baseline_cumulative_return(self) -> float:
        return self.get_price() / self.get_price(0) - 1.0

    def take_discrete_action(self, action: int) -> None:
        if action == 2:  # buy
            amount = self.cash
            if self.max_amount > 0:
                amount = min(self.cash, self.max_amount)
            buy_qty = amount / self.get_price()

            self.quantity += buy_qty * (1 - self.fee)
            self.cash -= amount
        elif action == 0:  # sell
            sell_qty = self.quantity
            if self.max_amount > 0:
                sell_qty = min(self.max_amount / self.get_price(), self.quantity)

            self.quantity -= sell_qty
            self.cash += sell_qty * self.get_price() * (1 - self.fee)
        elif action == 1:  # hold
            pass
        else:
            raise ValueError('action should be 0, 1 or 2, got {}'.format(action))

    def take_continuous_action(self, action: float) -> None:
        action = float(action)

        if action > 1.0 or action < -1.0:
            raise ValueError(f'continuous action should be in [-1, 1], got {action}')

        # if action is 0, do nothing
        if action == 0:
            return

        # handle positive and negative action
        if action > 0:
            buy_amount = self.cash * action
            buy_qty = buy_amount / self.get_price()

            self.quantity += buy_qty * (1 - self.fee)
            self.cash -= buy_amount
        elif action < 0:
            sell_qty = self.quantity * abs(action)

            self.quantity -= sell_qty
            self.cash += sell_qty * self.get_price() * (1 - self.fee)

        # make sure cash and quantity are non-negative
        if self.cash < 0:
            logger.warning(f'cash is negative: {self.cash}, set to 0')
            self.cash = 0

        if self.quantity < 0:
            logger.warning(f'quantity is negative: {self.quantity}, set to 0')
            self.quantity = 0

    def get_metrics(self):
        values = pd.Series(self.values, index=self.datetimes)
        returns = values.pct_change().dropna()

        return {
            'compsum': qs.stats.compsum(returns).iloc[-1],
            'max_drawdown': qs.stats.max_drawdown(values),
            'sharpe': qs.stats.sharpe(returns),
        }


def preprocess(df: pd.DataFrame, symbol: str) -> pd.DataFrame:
    symbol = symbol.replace("/", "").upper()

    new_df = pd.DataFrame({'datetime': df['datetime']})

    # close price
    new_df['close'] = df['close']

    # normalized close price
    new_df['normalized_close'] = (df['close'] - CLOSE_PRICE_MEAN[symbol]) / CLOSE_PRICE_STD[symbol]

    # returns
    for n in [12, 24, 30, 60, 90]:
        new_df[f'pct_change_{n}'] = df['close'].pct_change(
            periods=n) / (df['close'].pct_change(periods=1).ewm(span=60).std() * math.sqrt(n))

    # macd
    for s, l in zip([8, 16, 32], [24, 48, 96]):
        s_ema = df['close'].ewm(span=s).mean()
        l_ema = df['close'].ewm(span=l).mean()
        q_t = (s_ema - l_ema) / df['close'].rolling(63).std()
        new_df[f'macd_{s}_{l}'] = q_t / q_t.ewm(span=s).std()

    # rsi
    for n in [12, 24, 30, 60, 90]:
        new_df[f'rsi_{n}'] = (ta.rsi(df['close'], length=n) - 50) / 100

    # drop na rows
    new_df.dropna(inplace=True)

    # set datetime as index
    new_df.set_index('datetime', inplace=True)

    return new_df
