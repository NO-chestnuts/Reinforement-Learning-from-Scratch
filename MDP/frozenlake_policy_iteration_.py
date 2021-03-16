import numpy as np
import gym
from gym import wrappers
from gym.envs.registration import register
import matplotlib.pylab as plt

evaluate_v = []

def run_episode(env, policy, gamma = 1.0, render = False):
    """ Runs an episode and return the total reward """
    obs = env.reset()
    total_reward = 0
    step_idx = 0
    while True:
        if render:
            env.render()
        obs, reward, done, _ = env.step(int(policy[obs]))
        total_reward += (gamma**step_idx * reward)
        step_idx += 1
        if done:
            break
    return total_reward

def evaluate_policy(env, policy, gamma = 1.0, n = 100):
    scores = [run_episode(env, policy, gamma, False) for _ in range(n)]
    return np.mean(scores)

def extract_policy(env, v, gamma = 1.0):
    """ Extract the policy given a value-function """
    policy = np.zeros(env.env.nS)
    for s in range(env.env.nS):
        q_sa = np.zeros(env.env.nA)
        for a in range(env.env.nA):
            q_sa[a] = sum([p * (r + gamma * v[s_]) for p, s_, r, _ in env.env.P[s][a]])
        policy[s] = np.argmax(q_sa)
    return policy

def compute_policy_v(env, policy, gamma=1.0):
    """ Iteratively evaluate the value-function under policy.
    Alternatively, we could formulate a set of linear equations in iterms of v[s]
    and solve them to find the value function.
    """
    v = np.zeros(env.env.nS)
    eps = 1e-10
    while True:
        # evaluate_v.append(evaluate_policy(env, policy, gamma, n=100))
        pre_v = v.copy()
        for s in range(env.env.nS):
            policy_a = policy[s]
            v[s] = sum([p * (r + gamma * pre_v[s_]) for p, s_, r, _ in env.env.P[s][policy_a]])
        if (np.sum((np.fabs(pre_v - v))) <= eps):
            break
    return v

def policy_iteration(env, gamma = 1.0):
    """ Policy-Iteration algorithm """
    policy = np.random.choice(env.env.nA, size=(env.env.nS))
    max_iterations = 200000
    gamma = 1.0
    for i in range(max_iterations):
        evaluate_v.append(evaluate_policy(env, policy, gamma, n=100))
        old_policy_v = compute_policy_v(env, policy, gamma)
        new_policy = extract_policy(env, old_policy_v, gamma)
        if (np.all(policy == new_policy)):
            print('Policy-Iteration converged at step %d.' % (i + 1))
            break
        policy = new_policy
    return policy

if __name__ == '__main__':

    env_name = 'FrozenLake-v0' # 'FrozenLake8x8-v0'
    env = gym.make(env_name)

    optimal_policy = policy_iteration(env, gamma = 1.0)
    scores = evaluate_policy(env, optimal_policy, gamma = 1.0)
    print('Average scores = ', np.mean(scores))

    for i in range(5):
        evaluate_v.append(evaluate_policy(env, optimal_policy, gamma = 1.0, n=100))
    time_step = [i+1 for i in range(len(evaluate_v))]
    plt.figure()
    plt.plot(time_step, evaluate_v)
    plt.show()
