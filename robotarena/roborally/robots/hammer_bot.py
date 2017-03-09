import random
from roborally.api import *

name = 'HammerBot'

def move():
  my_memory = memory()
  if 'move' not in my_memory:
    my_memory['num_moves'] = 0
    my_memory['move'] = random.choice([SIDESTEP_LEFT, SIDESTEP_RIGHT])
  my_memory['num_moves'] += 1
  if my_memory['num_moves'] % 3 == 0:
    my_memory['move'] = opposite_move(my_memory['move'])
  return my_memory['move']
