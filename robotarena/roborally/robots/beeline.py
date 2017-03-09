import random
from roborally.api import *

name = 'Beeline'

def move():
  if charges() > 0:
    possible_moves = NORMAL_MOVES + PRIORITY_MOVES
  else:
    possible_moves = NORMAL_MOVES
  return random.choice(moves_in_directions(sense_flag(), possible_moves))
