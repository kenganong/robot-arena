# Directions
AHEAD = (-1, 0)
RIGHT = (0, 1)
BEHIND = (1, 0)
LEFT = (0, -1)

CLOCKWISE = [AHEAD, RIGHT, BEHIND, LEFT]

# Keys to cell.contents dict
TYPE = 'type'
POSITION = 'position'
LIFE = 'life'
FACING = 'facing'
NAME = 'name'
FLAGS_SCORED = 'scored'
CHARGES = 'charges'
MEMORY = 'memory'
FLAG_SENSE = 'sense'

# Floor elements
PIT = None
EMPTY = 'empty'
FLAG = 'flag'
LEFT_SPINNER = 'spin_left'
RIGHT_SPINNER = 'spin_right'

# Content types
WALL = 'wall'
MOUNTED_LASER = 'mounted'
CORPSE = 'corpse'
ROBOT = 'robot'

# Moves
LASER = 'laser'
FORWARD = 'forward'
FORWARD_TWO = 'forward2'
REVERSE = 'reverse'
SIDESTEP_LEFT = 'left_dodge'
SIDESTEP_RIGHT = 'right_dodge'
TURN_LEFT = 'left'
TURN_RIGHT = 'right'
U_TURN = 'uturn'

MOVES = [LASER, FORWARD, FORWARD_TWO, REVERSE, SIDESTEP_LEFT, SIDESTEP_RIGHT, TURN_LEFT, TURN_RIGHT, U_TURN]
NORMAL_MOVES = [FORWARD, REVERSE, TURN_LEFT, TURN_RIGHT, U_TURN]
ATTACK_MOVES = [LASER,]
PRIORITY_MOVES = [FORWARD_TWO, SIDESTEP_LEFT, SIDESTEP_RIGHT]

# Information available to robot
SIGHT = []

def myself():
  center = len(SIGHT) // 2
  return SIGHT[center][center].content

def sight():
  return SIGHT

def memory():
  return myself()[MEMORY]

def charges():
  return myself()[CHARGES]

def flags():
  return myself()[FLAGS_SCORED]

def life():
  return myself()[LIFE]

def sense_flag():
  return myself()[FLAG_SENSE]

def shooting(move=None):
  pass # TODO: implement, who am I shooting

def shot_by(move=None):
  pass # TODO: implement, who am I shot by

def position(move):
  pass # TODO: what position would I be in after move

def facing(move):
  pass # TODO: what direction would I be facing after move

def robots():
  pass # TODO: get all robots in sight

def walls():
  pass # TODO: get all walls in sight

def spinners():
  pass # TODO: get all spinners in sight

def flag():
  pass # TODO: get the flag if in sight

def mounted():
  pass # TODO: get all mounted lasers in sight

def pit():
  pass # TODO: get all pits in sight

def get_pos_in_direction(pos, direction, distance=1):
  return tuple(x + y for x, y in zip(pos, tuple(distance * z for z in direction)))

def opposite_direction(direction):
  return (-direction[0], -direction[1])

def convert_direction(ref_dir, direction):
  if ref_dir == AHEAD:
    return direction
  elif ref_dir == BEHIND:
    return opposite_direction(direction)
  elif ref_dir == RIGHT:
    return turn_direction(direction, False)
  elif ref_dir == LEFT:
    return turn_direction(direction, True)

def turn_direction(direction, clockwise):
  if clockwise:
    return CLOCKWISE[(CLOCKWISE.index(direction) + 1) % len(CLOCKWISE)]
  else:
    return CLOCKWISE[CLOCKWISE.index(direction) - 1]

def direction(start_pos, end_pos):
  directions = []
  if start_pos[0] == end_pos[0] and start_pos[1] == end_pos[1]:
    return directions
  row_diff = abs(start_pos[0] - end_pos[0])
  col_diff = abs(start_pos[1] - end_pos[1])
  if start_pos[0] < end_pos[0] and col_diff < row_diff * 4:
    directions.append(BEHIND)
  elif start_pos[0] > end_pos[0] and col_diff < row_diff * 4:
    directions.append(AHEAD)
  if start_pos[1] < end_pos[1] and row_diff < col_diff * 4:
    directions.append(RIGHT)
  elif start_pos[1] > end_pos[1] and row_diff < col_diff * 4:
    directions.append(LEFT)
  return directions
