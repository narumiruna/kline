from typing import Dict
from typing import Protocol
from typing import Tuple
from typing import Union

import gym
import numpy as np


class Predictor(Protocol):

    def predict(self, observation: Union[np.ndarray, Dict[str, np.ndarray]], deterministic: bool = False):
        pass


def evaluate_model(model: Predictor, env: gym.Env, num_episodes: int = 10, render: bool = False) -> Tuple[float, float]:
    episode_rewards = []

    for i_episode in range(num_episodes):
        obs = env.reset()

        episode_reward = 0
        done = False
        while not done:
            action = model.predict(obs, deterministic=True)
            obs, reward, done, info = env.step(action)
            episode_reward += reward
            if render:
                env.render()

        episode_rewards.append(episode_reward)

    env.close()

    return np.mean(episode_rewards), np.std(episode_rewards)
