import os
import copy
import pickle
import roborally.config as config
import roborally.manager as manager

if config.save_replay:
  replay = []

def log_state(state):
  if config.interactive:
    print(state)
    input()
  if config.save_replay:
    replay.append(copy.deepcopy(state))

def log_results(state):
  if config.print_results:
    print('Final Results!')
    for brain in sorted(state.brains, key = lambda x: x.placement):
      print('{}. {}  with {} flags (scored: {})  surviving {} iterations ({} robots left)'.format(brain.placement,
            brain.name, brain.max_flag, brain.total_flags, brain.iterations_survived, brain.robots_alive))

state = manager.create_start_state()
while not manager.end_state(state):
  log_state(state)
  manager.next_iteration(state)
log_state(state)
log_results(state)

if config.save_replay:
  filename = 'roborally/replays/{}.pickle'.format(config.replay_name)
  os.makedirs(os.path.dirname(filename), exist_ok=True)
  with open(filename, 'wb') as replay_file:
    pickle.dump(replay, replay_file)
