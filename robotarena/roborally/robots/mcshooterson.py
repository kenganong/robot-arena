import random
from roborally.api import *

def move():
  hits_robot = []
  hits_non_robot = []
  for move in MOVES:
    target = shooting(move)
    if target and target[TYPE] == ROBOT:
      hits_robot.append(move)
    elif target:
      hits_non_robot.append(move)
  if LASER in hits_robot:
    return LASER
  elif hits_robot:
    return random.choice(hits_robot)
  elif hits_non_robot:
    return random.choice(hits_non_robot)
  else:
    return FORWARD # Find something to shoot!
