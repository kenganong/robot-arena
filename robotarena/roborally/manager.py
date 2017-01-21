import random
from roborally.api import *
from roborally.game_state import *

ROBOT_SIGHT_RANGE = 5

def create_start_state():
  import roborally.random_bot as random_bot
  class Stand:
    def move(self):
      return LASER
  class RandomBot:
    def move(self):
      return random.choice(MOVES)
  brains = [Brain('Thomas', RandomBot()), Brain('Wendy', RandomBot()), Brain('Steve', Stand())]
  with open('roborally/example_board.txt') as board_file:
    state = create_state(board_file, brains)
  return state

def next_iteration(state):
  record_moves_for_robots(state)
  perform_priority_moves(state)
  handle_destroyed(state)
  perform_laser_moves(state)
  handle_destroyed(state)
  perform_moves(state)
  perform_spinners(state)
  perform_lasers(state)
  handle_destroyed(state)
  handle_flags(state)
  charge_up(state)
  state.iteration += 1

def record_moves_for_robots(state):
  import roborally.api as api
  for cell, pos in state.board.traverse():
    if cell.content and cell.content[TYPE] == ROBOT:
      robot = cell.content
      api.SIGHT = get_robot_sight(state, pos, robot)
      try:
        robot['move'] = robot['brain'].ai.move() # TODO: send information to robot
      except:
        robot[LIFE] -= 1
        if robot[LIFE] == 0:
          record_death(robot, 'overheating')
        robot['move'] = LASER
      if robot['move'] not in MOVES:
        robot['move'] = LASER

def get_robot_sight(state, pos, robot):
  surroundings = state.board.get_surroundings(pos, ROBOT_SIGHT_RANGE)
  sight = []
  for row in range(len(surroundings)):
    sight_row = []
    for col in range(len(surroundings[row])):
      cell = surroundings[row][col]
      sight_cell= Cell()
      if cell:
        if cell.floor and cell.floor.startswith(FLAG):
          if robot[FLAGS_SCORED] == int(cell.floor[len(FLAG):]) - 1:
            sight_cell.floor = FLAG
          else:
            sight_cell.floor = EMPTY
        else:
          sight_cell.floor = cell.floor
        if not cell.content:
          sight_cell.content == None
        else:
          sight_cell.content = dict()
          sight_cell.content[TYPE] = cell.content[TYPE]
          sight_cell.content[POSITION] = (row, col)
          sight_cell.content[LIFE] = cell.content[LIFE]
          if FACING in cell.content:
            sight_cell.content[FACING] = convert_direction(cell.content[FACING], robot[FACING])
          else:
            sight_cell.content[FACING] = NORTH
          if cell.content[TYPE] == ROBOT:
            sight_cell.content[NAME] = cell.content['brain'].name
          else:
            sight_cell.content[NAME] = cell.content[TYPE]
          if row == ROBOT_SIGHT_RANGE and col == ROBOT_SIGHT_RANGE:
            sight_cell.content[FLAGS_SCORED] = cell.content[FLAGS_SCORED]
            sight_cell.content[CHARGES] = cell.content[CHARGES]
            sight_cell.content[MEMORY] = cell.content[MEMORY]
            sight_cell.content[FLAG_SENSE] = direction(pos, state.flags[cell.content[FLAGS_SCORED]])
      else:
        sight_cell.floor = None
        sight_cell.content = None
      sight_row.append(sight_cell)
    sight.append(sight_row)
  return sight

def perform_priority_moves(state):
  to_move = [pos for cell, pos in state.board.traverse() if cell.content and cell.content[TYPE] == ROBOT
                and cell.content['move'] in PRIORITY_MOVES]
  random.shuffle(to_move)
  while len(to_move) > 0:
    pos = to_move.pop()
    robot = state.board.get_item(pos).content
    if robot['move'] == FORWARD_TWO:
      direction = robot[FACING]
    elif robot['move'] == SIDESTEP_LEFT:
      direction = turn_direction(robot[FACING], False)
    elif robot['move'] == SIDESTEP_RIGHT:
      direction = turn_direction(robot[FACING], True)
    pos = perform_move_in_direction(state, pos, direction, to_move)
    if pos != None and robot['move'] == FORWARD_TWO:
      pos = perform_move_in_direction(state, pos, direction, to_move)
    if pos != None:
      if robot[CHARGES] > 0:
        robot[CHARGES] -= 1
      else:
        robot[LIFE] -= 1
        if robot[LIFE] == 0:
          record_death(robot, 'malfunction')

def perform_moves(state):
  to_move = [cell.content for cell, pos in state.board.traverse() if cell.content and cell.content[TYPE] == ROBOT
                and cell.content['move'] in [TURN_LEFT, TURN_RIGHT, U_TURN]]
  for robot in to_move:
    perform_turn(robot, robot['move'])
  to_move = [pos for cell, pos in state.board.traverse() if cell.content and cell.content[TYPE] == ROBOT
                and cell.content['move'] in [FORWARD, REVERSE]]
  random.shuffle(to_move)
  while len(to_move) > 0:
    pos = to_move.pop()
    robot = state.board.get_item(pos).content
    if robot['move'] == FORWARD:
      direction = robot[FACING]
    elif robot['move'] == REVERSE:
      direction = opposite_direction(robot[FACING])
    perform_move_in_direction(state, pos, direction, to_move)

def perform_spinners(state):
  to_move = [cell for cell, pos in state.board.traverse() if cell.content and cell.content[TYPE] == ROBOT
                and cell.floor in [LEFT_SPINNER, RIGHT_SPINNER]]
  for cell in to_move:
    direction = TURN_LEFT if cell.floor == LEFT_SPINNER else TURN_RIGHT
    perform_turn(cell.content, direction)

def perform_turn(robot, turn):
  if turn == U_TURN:
    robot[FACING] = opposite_direction(robot[FACING])
  else:
    if turn == TURN_LEFT:
      robot[FACING] = turn_direction(robot[FACING], False)
    elif turn == TURN_RIGHT:
      robot[FACING] = turn_direction(robot[FACING], True)

def perform_move_in_direction(state, pos, direction, other_positions):
  pos_in_front = get_pos_in_direction(pos, direction)
  in_front = state.get_content(pos_in_front)
  # First push anything in front of this robot
  if in_front and (in_front[TYPE] == ROBOT or in_front[TYPE] == CORPSE):
    new_pos = perform_move_in_direction(state, pos_in_front, direction, other_positions)
    # Update the other_positions list with the new position
    if new_pos == None:
      try:
        other_positions.remove(pos_in_front)
      except ValueError:
        pass # It wasn't in the list
      in_front = None
    elif new_pos != pos_in_front:
      in_front = None
      try:
        other_positions[other_positions.index(pos_in_front)] = new_pos
      except ValueError:
        pass # It wasn't in the list
  # Now move the current robot
  if in_front:
    return pos
  else:
    robot = state.board.get_item(pos).content
    state.board.get_item(pos).content = None
    cell = state.board.get_item(pos_in_front)
    if cell:
      cell.content = robot
      return pos_in_front
    else:
      record_death(robot, 'falling')
      return None

def perform_laser_moves(state):
  for cell, pos in state.board.traverse():
    if cell.content and cell.content[TYPE] == ROBOT and cell.content['move'] == LASER:
      fire_laser(state, pos, cell.content[FACING])

def perform_lasers(state):
  for cell, pos in state.board.traverse():
    if cell.content and cell.content[TYPE] in [ROBOT, MOUNTED_LASER]:
      fire_laser(state, pos, cell.content[FACING])

def fire_laser(state, pos, direction):
  while True:
    pos = get_pos_in_direction(pos, direction)
    cell = state.board.get_item(pos)
    if not cell:
      break
    elif cell.content:
      cell.content[LIFE] -= 1
      if cell.content[LIFE] == 0:
        record_death(cell.content, 'lasers')
      break

def handle_destroyed(state):
  to_fill_with_corpses = []
  chain = []
  for cell, pos in state.board.traverse():
    perform_destruction(state, pos, cell, to_fill_with_corpses, chain)
  while len(chain) > 0:
    to_inspect = chain
    chain = []
    for pos, cell in to_inspect:
      perform_destruction(state, pos, cell, to_fill_with_corpses, chain)
  for cell in to_fill_with_corpses:
    cell.content = make_corpse()

def perform_destruction(state, pos, cell, to_fill_with_corpses, chain):
  if cell.content and cell.content[LIFE] <= 0:
    previous_content = cell.content
    cell.content = None
    if previous_content[TYPE] == CORPSE:
      for direction in [NORTH, EAST, SOUTH, WEST, (-1, -1), (-1, 1), (1, -1), (1, 1)]:
        adjacent_pos = get_pos_in_direction(pos, direction)
        adjacent_cell = state.board.get_item(adjacent_pos)
        if adjacent_cell and adjacent_cell.content:
          adjacent_cell.content[LIFE] -= 1
          if adjacent_cell.content[LIFE] == 0:
            record_death(adjacent_cell.content, 'explosions')
          chain.append((adjacent_pos, adjacent_cell))
    elif previous_content[TYPE] == ROBOT:
      to_fill_with_corpses.append(cell)

def handle_flags(state):
  for cell, pos in state.board.traverse():
    if cell.content and cell.content[TYPE] == ROBOT and cell.floor.startswith(FLAG):
      flag = int(cell.floor[len(FLAG):])
      if cell.content[FLAGS_SCORED] == flag - 1:
        cell.content[FLAGS_SCORED] += 1

def charge_up(state):
  if state.iteration % 10 == 9:
    for cell, pos in state.board.traverse():
      if cell.content and cell.content[TYPE] == ROBOT:
        cell.content[CHARGES] += 1

def record_death(content, method):
  # TODO: different implementation
  if content[TYPE] == ROBOT:
    print('{} died from {}'.format(content['brain'].name, method))
