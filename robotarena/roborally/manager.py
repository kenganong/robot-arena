import os
import importlib.util
import random
from roborally.api import *
from roborally.game_state import *

ROBOT_SIGHT_RANGE = 5
LIFE_GAIN_PER_FLAG = 10
RANDOM_DAMAGE_START = 300
RANDOM_DAMAGE_CYCLE = 30

def create_start_state(map_file, robots):
  brains = load_brains(robots)
  with open(map_file) as board_file:
    state = create_state(board_file, brains)
  return state

def load_brains(robots):
  brains = []
  brains_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'robots')
  if not robots:
    robots = [(file_name[:-3], file_name[:-3]) for file_name in os.listdir(brains_dir) if file_name.endswith('.py') and not file_name.startswith('__')]
  for bot in robots:
    module_path = os.path.join(brains_dir, bot[1] + '.py')
    spec = importlib.util.spec_from_file_location(bot[1], module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    brains.append(Brain(bot[0], module))
  return brains

def end_state(state):
  brains_alive = len([brain for brain in state.brains if brain.robots_alive > 0])
  most_flags = sorted(state.brains, reverse=True,
          key = lambda x: (x.max_flag, x.total_flags, x.iterations_survived, x.robots_alive))
  if brains_alive > 1 and most_flags[0].max_flag < NUM_FLAGS:
    return False
  # It is an end state! Record winner before returning
  most_survival = sorted(state.brains, reverse=True,
          key = lambda x: (x.iterations_survived, x.robots_alive, x.max_flag, x.total_flags))
  if brains_alive == 1:
    priority = (most_survival, most_flags)
  else:
    priority = (most_flags, most_survival)
  rank = 1
  for placement in range(2 * len(state.brains)):
    brain_list = priority[placement % 2]
    brain_index = placement // 2
    brain = brain_list[brain_index]
    if brain.placement == 0:
      brain.placement = rank
      rank += 1
      # If the next one in the list was not a tie-breaker, add it too
      for next_index in range(brain_index + 1, len(state.brains) - 1):
        next_brain = brain_list[brain_index]
        if (next_brain.max_flag == brain.max_flag and next_brain.iterations_survived == brain.iterations_survived and
            next_brain.total_flags == brain.total_flags and next_brain.robots_alive == brain.robots_alive):
          if next_brain.placement == 0:
            rank += 1
            next_brain.placement = brain.placement
        else:
          break
  return True

def next_iteration(state, debug_robots, interactive):
  record_moves_for_robots(state, debug_robots, interactive)
  perform_priority_moves(state, interactive)
  handle_destroyed(state, interactive)
  perform_laser_moves(state, interactive)
  handle_destroyed(state, interactive)
  perform_moves(state, interactive)
  perform_spinners(state)
  perform_lasers(state, interactive)
  handle_destroyed(state, interactive)
  perform_random_damage(state, interactive)
  handle_destroyed(state, interactive)
  handle_flags(state)
  charge_up(state)
  state.iteration += 1
  record_statistics(state)

def record_moves_for_robots(state, debug_robots, interactive):
  import roborally.api as api
  for cell, pos in state.board.traverse():
    if cell.content and cell.content[TYPE] == ROBOT:
      robot = cell.content
      api.SIGHT = get_robot_sight(state, pos, robot)
      try:
        robot['move'] = robot['brain'].ai.move()
      except Exception as error:
        if debug_robots:
          raise error
        robot[LIFE] -= 1
        if robot[LIFE] == 0:
          record_death(robot, 'overheating', interactive)
        robot['move'] = LASER
      if robot['move'] not in MOVES:
        robot['move'] = LASER

def get_robot_sight(state, pos, robot):
  surroundings = state.board.get_surroundings(pos, ROBOT_SIGHT_RANGE)
  size = len(surroundings)
  sight = []
  for row in range(size):
    sight_row = []
    for col in range(size):
      if robot[FACING] == NORTH:
        cell = surroundings[row][col]
      elif robot[FACING] == WEST:
        cell = surroundings[size - col - 1][row]
      if robot[FACING] == SOUTH:
        cell = surroundings[size - row - 1][size - col - 1]
      if robot[FACING] == EAST:
        cell = surroundings[col][size - row - 1]
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
            sight_cell.content[FACING] = convert_direction(robot[FACING], cell.content[FACING])
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
            sight_cell.content[FLAG_SENSE] = [convert_direction(robot[FACING], d)
                    for d in direction_toward(pos, state.flags[cell.content[FLAGS_SCORED]])]
      else:
        sight_cell.floor = None
        sight_cell.content = None
      sight_row.append(sight_cell)
    sight.append(sight_row)
  return sight

def perform_priority_moves(state, interactive):
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
    pos = perform_move_in_direction(state, pos, direction, to_move, interactive)
    if pos != None and robot['move'] == FORWARD_TWO:
      pos = perform_move_in_direction(state, pos, direction, to_move, interactive)
    if pos != None:
      if robot[CHARGES] > 0:
        robot[CHARGES] -= 1
      else:
        robot[LIFE] -= 1
        if robot[LIFE] == 0:
          record_death(robot, 'malfunction', interactive)

def perform_moves(state, interactive):
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
    perform_move_in_direction(state, pos, direction, to_move, interactive)

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

def perform_move_in_direction(state, pos, direction, other_positions, interactive):
  pos_in_front = get_pos_in_direction(pos, direction)
  in_front = state.get_content(pos_in_front)
  # First push anything in front of this robot
  if in_front and (in_front[TYPE] == ROBOT or in_front[TYPE] == CORPSE):
    new_pos = perform_move_in_direction(state, pos_in_front, direction, other_positions, interactive)
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
    if cell and cell.floor:
      cell.content = robot
      return pos_in_front
    else:
      record_death(robot, 'falling', interactive)
      return None

def perform_laser_moves(state, interactive):
  for cell, pos in state.board.traverse():
    if cell.content and cell.content[TYPE] == ROBOT and cell.content['move'] == LASER:
      fire_laser(state, pos, cell.content[FACING], interactive)

def perform_lasers(state, interactive):
  for cell, pos in state.board.traverse():
    if cell.content and cell.content[TYPE] in [ROBOT, MOUNTED_LASER]:
      fire_laser(state, pos, cell.content[FACING], interactive)

def fire_laser(state, pos, direction, interactive):
  while True:
    pos = get_pos_in_direction(pos, direction)
    cell = state.board.get_item(pos)
    if not cell:
      break
    elif cell.content:
      cell.content[LIFE] -= 1
      if cell.content[LIFE] == 0:
        record_death(cell.content, 'lasers', interactive)
      break

def perform_random_damage(state, interactive):
  if state.iteration >= RANDOM_DAMAGE_START and state.iteration % RANDOM_DAMAGE_CYCLE == 0:
    damage_amount = (state.iteration - RANDOM_DAMAGE_START) / RANDOM_DAMAGE_CYCLE
    living_bots = []
    for cell, pos in state.board.traverse():
      if cell.content and cell.content[TYPE] == ROBOT:
        # Random damage prefers robots who have scored less flags
        for i in range(6 - cell.content[FLAGS_SCORED]):
          living_bots.append(cell.content)
    if living_bots:
      robot = random.choice(living_bots)
      robot[LIFE] -= damage_amount
      if robot[LIFE] < 0:
        record_death(robot, 'random damage', interactive)

def handle_destroyed(state, interactive):
  to_fill_with_corpses = []
  chain = []
  for cell, pos in state.board.traverse():
    perform_destruction(state, pos, cell, to_fill_with_corpses, chain, interactive)
  while len(chain) > 0:
    to_inspect = chain
    chain = []
    for pos, cell in to_inspect:
      perform_destruction(state, pos, cell, to_fill_with_corpses, chain, interactive)
  for cell in to_fill_with_corpses:
    cell.content = make_corpse()

def perform_destruction(state, pos, cell, to_fill_with_corpses, chain, interactive):
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
            record_death(adjacent_cell.content, 'explosions', interactive)
          chain.append((adjacent_pos, adjacent_cell))
    elif previous_content[TYPE] == ROBOT:
      to_fill_with_corpses.append(cell)

def handle_flags(state):
  for cell, pos in state.board.traverse():
    if cell.content and cell.content[TYPE] == ROBOT and cell.floor.startswith(FLAG):
      flag = int(cell.floor[len(FLAG):])
      if cell.content[FLAGS_SCORED] == flag - 1:
        cell.content[FLAGS_SCORED] += 1
        cell.content[LIFE] += LIFE_GAIN_PER_FLAG
        cell.content['brain'].total_flags += 1
        if flag > cell.content['brain'].max_flag:
          cell.content['brain'].max_flag = flag

def charge_up(state):
  if state.iteration % 10 == 9:
    for cell, pos in state.board.traverse():
      if cell.content and cell.content[TYPE] == ROBOT:
        cell.content[CHARGES] += 1

def record_statistics(state):
  state.calculate_statistics()

def record_death(content, method, interactive):
  if content[TYPE] == ROBOT:
    brain = content['brain']
    if method not in brain.death_reason:
      brain.death_reason[method] = 0
    brain.death_reason[method] += 1
    if interactive:
      print('{} died from {}'.format(content['brain'].name, method))
