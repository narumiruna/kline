import gym

from .evaluation import evaluate_model


class RandomPredictor:

    def __init__(self, env):
        self.action_space = env.action_space

    def predict(self, observation, deterministic=False):
        return self.action_space.sample()


def test_evaluation_model():
    env = gym.make('CartPole-v1')
    model = RandomPredictor(env)
    mean_reward, std_reward = evaluate_model(model, env)
