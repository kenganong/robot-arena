#!/usr/bin/env python3
import sys
import os
import importlib.util
import copy
import pickle
import roborally.manager as manager

# Load the config file
if len(sys.argv) < 2:
  import roborally.config as config
else:
  spec = importlib.util.spec_from_file_location('config', sys.argv[1])
  config = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(config)

if config.save_replay:
  replay = {}
  replay['name'] = config.replay_name
  replay['type'] = 'RoboRally'
  replay['states'] = []

def log_state(state):
  if config.interactive:
    print(state)
    input()
  if config.save_replay:
    replay['states'].append(copy.deepcopy(state))

def log_results(state):
  if config.print_results:
    print('Final Results!')
    for brain in sorted(state.brains, key = lambda x: x.placement):
      print('{}. {}  with {} flags (scored: {})  surviving {} iterations ({} robots left)'.format(brain.placement,
            brain.name, brain.max_flag, brain.total_flags, brain.iterations_survived, brain.robots_alive))
  if config.save_replay:
    filename = 'roborally/replays/{}.pickle'.format(replay['name'])
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'wb') as replay_file:
      pickle.dump(replay, replay_file)

state = manager.create_start_state(config.map_file, getattr(config, 'robots', None))
while not manager.end_state(state):
  log_state(state)
  manager.next_iteration(state, config.debug_robots, config.interactive)
log_state(state)
log_results(state)
