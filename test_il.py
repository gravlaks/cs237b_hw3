import numpy as np
from train_il import NN
import gym_carlo
import gym
import time
import argparse
import tensorflow as tf
from utils import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--scenario', type=str, help="intersection, circularroad, lanechange", default="intersection")
    parser.add_argument('--goal', type=str, help="left, straight, right, inner, outer, all", default="all")
    parser.add_argument("--visualize", action="store_true", default=False)
    args = parser.parse_args()
    scenario_name = args.scenario.lower()
    assert scenario_name in scenario_names, '--scenario argument is invalid!'

    if args.goal.lower() == 'all':
        env = gym.make(scenario_name + 'Scenario-v0', goal=len(goals[scenario_name]))
    else:
        env = gym.make(scenario_name + 'Scenario-v0', goal=np.argwhere(np.array(goals[scenario_name])==args.goal.lower())[0,0]) # hmm, unreadable
    
    nn_model = NN(obs_sizes[scenario_name],2)
    nn_model.load_weights('./policies/' + scenario_name + '_' + args.goal.lower() + '_IL')

    episode_number = 10 if args.visualize else 100
    success_counter = 0
    env.T = 200*env.dt - env.dt/2. # Run for at most 200dt = 20 seconds
    for _ in range(episode_number):
        env.seed(int(np.random.rand()*1e6))
        obs, done = env.reset(), False
        if args.visualize: env.render()
        while not done:
            t = time.time()
            obs = np.array(obs).reshape(1,-1)
            action = nn_model(obs).numpy().reshape(-1)
            obs,_,done,_ = env.step(action)
            if args.visualize: 
                env.render()
                while time.time() - t < env.dt/2: pass # runs 2x speed. This is not great, but time.sleep() causes problems with the interactive controller
            if done:
                env.close()
                if args.visualize: time.sleep(1)
                if env.target_reached: success_counter += 1
    print('Success Rate = ' + str(float(success_counter)/episode_number))
