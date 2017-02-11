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
TURN_MOVES = [TURN_LEFT, TURN_RIGHT, U_TURN]
PROGRESS_MOVES = [FORWARD, FORWARD_TWO, REVERSE, SIDESTEP_LEFT, SIDESTEP_RIGHT]

# Information available to robot
SIGHT = []

def sight():
  """Returns everything your robot knows.
     11x11 list of lists filled with cell objects.
     Each cell object has a floor attribute and a content attribute.
     Floor is one of PIT, EMPTY, FLAG, LEFT_SPINNER, RIGHT_SPINNER.
     Content is a dict with the keys TYPE, POSITION, LIFE, FACING, and NAME.
     For your robot (located at (5, 5)), the content dict also contains FLAGS_SCORED, CHARGES, MEMORY, and FLAG_SENSE.
  """
  return SIGHT

def myself():
  """Returns the dict representing your robot.
     This dict contains the keys TYPE, POSITION, LIFE, FACING, NAME, FLAGS_SCORED, CHARGES, MEMORY, and FLAG_SENSE.
  """
  center = len(sight()) // 2
  return sight()[center][center].content

def memory():
  """Returns your robot's memory, which is a dict.
     Your memory is not automatically populated with anything. Your AI can populate it when deciding a move."""
  return myself()[MEMORY]

def charges():
  """Returns the number of charges your robot has.
     Charges allow your robot to use priority moves without taking damage.
  """
  return myself()[CHARGES]

def flags():
  """Returns the number of flags your robot has scored."""
  return myself()[FLAGS_SCORED]

def life():
  """Returns the amount of life your robot has left."""
  return myself()[LIFE]

def sense_flag():
  """Returns a list of directions toward the next flag.
     This will contain one or two elements from AHEAD, RIGHT, BEHIND, LEFT."""
  return myself()[FLAG_SENSE]

def get_cell_in_sight(pos):
  """Returns the cell object at the given position within your sight.
     If the cell is beyond your sight, this returns None."""
  if pos[0] < 0 or pos[1] < 0 or pos[0] >= len(sight()) or pos[1] >= len(sight()):
    return None
  return sight()[pos[0]][pos[1]]

def flag_in_sight():
  """Returns the position of the flag if it is within your sight. Otherwise returns None."""
  my_sight = sight()
  for row in range(len(my_sight)):
    for col in range(len(my_sight[row])):
      if my_sight[row][col].floor == FLAG:
        return (row, col)
  return None

# This is a python recipe which allows functions to initialize static variables at the function scope.
def _static_vars(**kwargs):
  def decorate(func):
    for k in kwargs:
      setattr(func, k, kwargs[k])
    return func
  return decorate

@_static_vars(move_map = {LASER: LASER, FORWARD: REVERSE, FORWARD_TWO: REVERSE, REVERSE: FORWARD,
                         SIDESTEP_LEFT: SIDESTEP_RIGHT, SIDESTEP_RIGHT: SIDESTEP_LEFT,
                         TURN_LEFT: TURN_RIGHT, TURN_RIGHT: TURN_LEFT, U_TURN: U_TURN})
def opposite_move(move):
  """Returns the move opposite to the given move.
     Since their is no REVERSE_TWO move, FORWARD_TWO will return REVERSE."""
  if move not in opposite_move.move_map:
    return None
  return opposite_move.move_map[move]

@_static_vars(direction_map = {AHEAD: [FORWARD, FORWARD_TWO], BEHIND: [U_TURN, REVERSE], LEFT: [TURN_LEFT, SIDESTEP_LEFT], RIGHT: [TURN_RIGHT, SIDESTEP_RIGHT]})
def moves_in_direction(direction, potential_moves=None):
  """Returns a list of possible first moves that will move your robot in the given direction.
     If potential_moves is given, moves will be considered from that list. Otherwise, all moves will be considered.
  """
  if not potential_moves:
    potential_moves = MOVES
  if direction not in moves_in_direction.direction_map:
    return []
  return [move for move in potential_moves if move in moves_in_direction.direction_map[direction]]

def moves_in_directions(directions, potential_moves=None):
  """Returns a list of possible first moves that will move your robot in one of the given directions.
     If potential_moves is given, moves will be considered from that list. Otherwise, all moves will be considered.
  """
  moves_toward = []
  for direction in directions:
    moves_toward.extend(moves_in_direction(direction, potential_moves))
  return moves_toward

@_static_vars(direction_map = {FORWARD: AHEAD, FORWARD_TWO: AHEAD, REVERSE: BEHIND,
                              SIDESTEP_LEFT: LEFT, SIDESTEP_RIGHT: RIGHT})
def direction_of_move(move):
  """Returns which direction the given move will take your robot.
     If the move given is not a progress move, None will be returned."""
  if move not in direction_of_move.direction_map:
    return None
  return direction_of_move.direction_map[move]

def distance_between(pos, other_pos=None):
  """Return the distance between the two given positions.
     If one position is given, the second will be the position of your robot."""
  if other_pos == None:
    other_pos = myself()[POSITION]
  return abs(pos[0] - other_pos[0]) + abs(pos[1] - other_pos[1])

def get_pos_in_direction(pos, direction, distance=1):
  """Returns the position (a tuple of the form (row, col)) in the given direction from the given position.
     If distance is not given, the position returned will be adjacent to the given position."""
  return tuple(x + y for x, y in zip(pos, tuple(distance * z for z in direction)))

def opposite_direction(direction):
  """Returns the direction opposite the given direction."""
  return (-direction[0], -direction[1])

def convert_direction(ref_dir, direction):
  """Converts a direction based an a different frame of reference.
     Answers the question, if I were facing ref_dir which way would direction be facing?"""
  if ref_dir == AHEAD:
    return direction
  elif ref_dir == BEHIND:
    return opposite_direction(direction)
  elif ref_dir == RIGHT:
    return turn_direction(direction, False)
  elif ref_dir == LEFT:
    return turn_direction(direction, True)

def turn_direction(direction, clockwise):
  """Returns a new direction based on turning the given direction clockwise or counter-clockwise."""
  if clockwise:
    return CLOCKWISE[(CLOCKWISE.index(direction) + 1) % len(CLOCKWISE)]
  else:
    return CLOCKWISE[CLOCKWISE.index(direction) - 1]

def direction_toward(start_pos, end_pos):
  """Returns which direction to move to go from start_pos to end_pos
     This returns a list containing one or two elements.
     For example if the end_pos is in front and to the left of start_pos this would return [AHEAD, LEFT]
     If one direction is significantly farther than the other direction, only the major direction will be returned.
     For example, if end_pos is 20 tiles AHEAD and 2 tiles LEFT from start_pos, this would return [AHEAD]"""
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

@_static_vars(move_map = {LASER: AHEAD, FORWARD: AHEAD, FORWARD_TWO: AHEAD, REVERSE: AHEAD, SIDESTEP_LEFT: AHEAD,
                         SIDESTEP_RIGHT: AHEAD, TURN_LEFT: LEFT, TURN_RIGHT: RIGHT, U_TURN: BEHIND})
def direction_after_move(move):
  """Returns which direction you will be facing after the given move (in relation to your current facing).
     This is speculative and could be changed due to other robots' moves"""
  if move not in direction_after_move.move_map:
    direction = AHEAD
  direction = direction_after_move.move_map[move]
  pos = position_after_move(move)
  cell = get_cell_in_sight(pos)
  if cell and cell.floor == LEFT_SPINNER:
    return turn_direction(direction, False)
  elif cell and cell.floor == RIGHT_SPINNER:
    return turn_direction(direction, True)
  else:
    return direction

def position_after_move(move):
  """Returns the position you will be in after the given move.
     If you would fall into a pit, this returns None.
     This is speculative and could be changed due to other robots' moves"""
  center = len(sight()) // 2
  start_pos = (center, center)
  if move not in PROGRESS_MOVES:
    return start_pos
  else:
    move_direction = direction_of_move(move)
    new_pos = get_pos_in_direction(start_pos, move_direction)
    new_cell = get_cell_in_sight(new_pos)
    # If you fall into a pit
    if not new_cell or new_cell.floor == PIT:
      return None
    # If you or something you tried to push bumped into a wall
    elif _wall_bump(start_pos, move_direction):
      return start_pos
    # If you only moved 0 or 1 tile
    elif move != FORWARD_TWO:
      return new_pos
    else:
      two_pos = get_pos_in_direction(new_pos, move_direction)
      new_cell = get_cell_in_sight(two_pos)
      # If your second move dropped you into a pit
      if not new_cell or new_cell.floor == PIT:
        return None
      # If your second move caused a bump into a wall
      elif _wall_bump(start_pos, move_direction, 2):
        return new_pos
      else:
        return two_pos

def bumps_into_wall(move):
  """Whether making the given move would cause you to stop prematurely due to a wall.
     This is speculative and could be changed due to other robots' moves"""
  if move not in PROGRESS_MOVES:
    return False
  center = len(sight()) // 2
  start_pos = (center, center)
  move_direction = direction_of_move(move)
  num_movement = 2 if move == FORWARD_TWO else 1
  return _wall_bump(start_pos, move_direction, num_movement)

def _wall_bump(pos, move_direction, num_movement=1):
  num_empty = 0
  while num_empty < num_movement:
    pos = get_pos_in_direction(pos, move_direction)
    cell = get_cell_in_sight(pos)
    if not cell or cell.floor == PIT:
      break
    # If the cell is empty, no wall bump, unless you moved more in that direction.
    elif not cell.content:
      num_empty += 1
    elif cell.content[TYPE] in [WALL, MOUNTED_LASER]:
      return True
  return False

def falls_into_pit(move):
  """Whether you would fall into a pit after making the given move.
     This is speculative and could be changed due to other robots' moves"""
  if move not in PROGRESS_MOVES:
    return False
  center = len(sight()) // 2
  start_pos = (center, center)
  move_direction = direction_of_move(move)
  new_pos = get_pos_in_direction(start_pos, move_direction)
  new_cell = get_cell_in_sight(new_pos)
  if new_cell.floor == PIT:
    return True
  elif move != FORWARD_TWO:
    return False
  # If you moved twice, but a wall was between you and the pit
  elif new_cell.content and new_cell.content[TYPE] in [WALL, MOUNTED_LASER]:
    return False
  else:
    two_pos = get_pos_in_direction(new_pos, move_direction)
    two_cell = get_cell_in_sight(two_pos)
    return two_cell.floor == PIT

def shooting(move=LASER):
  """Returns what you are shooting after making the given move. This returns the content of a cell, which is a dict.
     If no move is given, the LASER move is used.
     If you do not hit anything or what you hit is beyond your sight range, this returns None.
     If you would fall into a pit due to your move, this returns None.
     Although this function does not speculate other robots' moves, it does handle your move pushing other robots.
     This is speculative and could be changed due to other robots' moves"""
  # Gather info
  pos = position_after_move(move)
  if pos == None:
    return None
  direction = direction_after_move(move)
  move_direction = direction_of_move(move)
  start_pos = myself()[POSITION]
  # Handle shooting something you pushed
  if move in PROGRESS_MOVES and pos != start_pos and direction == move_direction:
    cell = get_cell_in_sight(pos)
    if move == FORWARD_TWO:
      # If you moved twice, you could have pushed two things and we care about the first
      intermediate_pos = get_pos_in_direction(start_pos, move_direction)
      intermediate_cell = get_cell_in_sight(intermediate_pos)
      if intermediate_cell.content:
        cell = intermediate_cell
    # If you pushed something into a pit, you aren't shooting it.
    past_pos = get_pos_in_direction(pos, move_direction)
    past_cell = get_cell_in_sight(past_pos)
    if cell.content and past_cell.floor != PIT:
      return cell.content
  # Handle shooting something you didn't push
  next_pos = pos
  while True:
    next_pos = get_pos_in_direction(next_pos, direction)
    next_cell = get_cell_in_sight(next_pos)
    if not next_cell:
      return None # Shoots past your sight, may hit anything
    elif next_cell.content and next_cell.content != myself():
      return next_cell.content

def shot_by(move=LASER):
  """Returns what is shooting you after you make the given move.
     This returns a list of the contents of a cells, which are dicts.
     If no move is given, the LASER move is used.
     If nothing would shoot you or what shoots you is beyond your sight range, this returns an empty list.
     If you would fall into a pit due to your move, this returns an empty list.
     Although this function does not speculate other robots' moves, it does handle your move pushing other robots.
     This is speculative and could be changed due to other robots' moves"""
  pos = position_after_move(move)
  if pos == None:
    return []
  start_pos = myself()[POSITION]
  move_direction = direction_of_move(move)
  shooters = []
  # Only one thing can shoot you from each direction
  for direction in CLOCKWISE:
    opposite = opposite_direction(direction)
    # Handle getting shot by things you pushed
    if move in PROGRESS_MOVES and direction == move_direction and pos != start_pos:
      cell = get_cell_in_sight(pos)
      if move == FORWARD_TWO:
        # If you moved twice, you could have pushed two things and we care about the first
        intermediate_pos = get_pos_in_direction(start_pos, move_direction)
        intermediate_cell = get_cell_in_sight(intermediate_pos)
        if intermediate_cell.content:
          cell = intermediate_cell
      past_pos = get_pos_in_direction(pos, move_direction)
      past_cell = get_cell_in_sight(past_pos)
      # If you pushed something into a pit, it cannot shoot you
      if cell.content and past_cell.floor != PIT:
        if cell.content[TYPE] in [ROBOT, MOUNTED_LASER] and cell.content[FACING] == opposite:
          shooters.append(cell.content)
        else:
          continue # What you pushed will protect you
    # Handle getting shot by things you didn't push
    next_pos = pos
    while True:
      next_pos = get_pos_in_direction(next_pos, direction)
      next_cell = get_cell_in_sight(next_pos)
      if not next_cell:
        break # Past your sight, you cannot tell
      # You cannot get shot by yourself, and if you moved two, you cannot get shot by something you pushed facing AHEAD
      elif (next_cell.content and next_cell.content != myself() and
           (move != FORWARD_TWO or next_cell.content[POSITION] != get_pos_in_direction(start_pos, move_direction))):
        if next_cell.content[TYPE] in [ROBOT, MOUNTED_LASER] and next_cell.content[FACING] == opposite:
          shooters.append(next_cell.content)
        else:
          break
  return shooters
