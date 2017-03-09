import random
from roborally.api import *

name = 'Leeroy'

def move():
  vision = sight()

  in_front = [vision[4][5], vision[3][5], vision[2][5], vision[1][5], vision[0][5]]
  if any(space.content and space.content[TYPE] == ROBOT for space in in_front):
    return FORWARD

  to_the_right = [vision[5][6], vision[5][7], vision[5][8], vision[5][9], vision[5][10]]
  if any(space.content and space.content[TYPE] == ROBOT for space in to_the_right):
    return TURN_RIGHT

  to_the_left = [vision[5][0], vision[5][1], vision[5][2], vision[5][3], vision[5][4]]
  if any(space.content and space.content[TYPE] == ROBOT for space in to_the_left):
    return TURN_LEFT

  return FORWARD
