import random
import common.model.board as board_api
from roborally.api import *

NUM_FLAGS = 8
NUM_ROBOTS_PER_BRAIN = 40

NORTH = AHEAD
EAST = RIGHT
SOUTH = BEHIND
WEST = LEFT

DIRECTIONS = [NORTH, EAST, SOUTH, WEST]

class Cell:
  def __init__(self):
    self.floor = EMPTY
    self.content = None

def make_content(type, life):
  return {TYPE: type, LIFE: life}

def make_wall():
  return make_content(WALL, 50)

def make_mounted(facing):
  content = make_content(MOUNTED_LASER, 50)
  content[FACING] = facing
  return content

def make_robot(brain, facing):
  content = make_content(ROBOT, 10)
  content[FACING] = facing
  content[CHARGES] = 1
  content[FLAGS_SCORED] = 0
  content[MEMORY] = {}
  content['brain'] = brain
  return content

def make_corpse():
  return make_content(CORPSE, 10)

class Brain:
  def __init__(self, name, ai):
    self.name = name
    self.ai = ai
    self.robots_alive = 0
    self.most_flags = 0

class RoboRallyGameState:
  def __init__(self, size):
    self.board = board_api.init_board((size, size), lambda: Cell())
    self.iteration = 0
    self.brains = []
    self.flags = [(0, 0)] * NUM_FLAGS
  def __str__(self):
    retval = '\nIteration: {}'.format(self.iteration)
    for row in range(self.board.rows):
      retval += '\n'
      for col in range(self.board.cols):
        cell = self.board.get_item((row, col))
        if cell.content:
          if cell.content[TYPE] == WALL:
            retval += ' # '
          elif cell.content[TYPE] == CORPSE:
            retval += ' / '
          elif cell.content[TYPE] == MOUNTED_LASER:
            if cell.content[FACING] == NORTH:
              retval += ' ^ '
            elif cell.content[FACING] == WEST:
              retval += ' < '
            elif cell.content[FACING] == EAST:
              retval += ' > '
            elif cell.content[FACING] == SOUTH:
              retval += ' v '
          elif cell.content[TYPE] == ROBOT:
            if cell.content[FACING] == NORTH:
              retval += '↑'
            elif cell.content[FACING] == WEST:
              retval += '←'
            elif cell.content[FACING] == EAST:
              retval += '→'
            elif cell.content[FACING] == SOUTH:
              retval += '↓'
            retval += cell.content['brain'].name[0] + ' '
        else:
          if cell.floor == EMPTY:
            retval += ' · '
          elif cell.floor == LEFT_SPINNER:
            retval += ' { '
          elif cell.floor == RIGHT_SPINNER:
            retval += ' } '
          elif cell.floor.startswith(FLAG):
            retval += ' {} '.format(cell.floor[len(FLAG)])
      self.calculate_statistics()
    for brain in self.brains:
      retval += '\n{} - living robots = {}   most_flags = {}'.format(brain.name, brain.robots_alive, brain.most_flags)
    return retval
  def get_content(self, pos):
    cell = self.board.get_item(pos)
    if not cell:
      return None
    return cell.content
  def calculate_statistics(self):
    # TODO: test this method, and get better statistics
    for brain in self.brains:
      brain.robots_alive = 0
      brain.most_flags = 0
    for cell, pos in self.board.traverse():
      if cell.content and cell.content[TYPE] == ROBOT:
        brain = cell.content['brain']
        brain.robots_alive += 1
        if brain.most_flags < cell.content[FLAGS_SCORED]:
          brain.most_flags = cell.content[FLAGS_SCORED]

def create_state(board_file, brains):
  lines = [line.rstrip('\n') for line in board_file]
  size = max(len(lines), max(len(line) for line in lines))
  state = RoboRallyGameState(size)
  for row in range(len(lines)):
    for col in range(len(lines[row])):
      char = lines[row][col]
      cell = state.board.get_item((row, col))
      if char == '#':
        cell.content = make_wall()
      elif char == '<':
        cell.content = make_mounted(WEST)
      elif char == '>':
        cell.content = make_mounted(EAST)
      elif char == 'v':
        cell.content = make_mounted(SOUTH)
      elif char == '^':
        cell.content = make_mounted(NORTH)
      elif char == '{':
        cell.floor = LEFT_SPINNER
      elif char == '}':
        cell.floor = RIGHT_SPINNER
      elif char.isdecimal():
        cell.floor = FLAG + char
        state.flags[int(char) - 1] = (row, col)
  state.brains = brains
  empty_cells = [cell for cell, pos in state.board.traverse() if not cell.content and cell.floor == EMPTY]
  for cell, brain in zip(random.sample(empty_cells, len(brains) * NUM_ROBOTS_PER_BRAIN), brains * NUM_ROBOTS_PER_BRAIN):
    cell.content = make_robot(brain, random.choice([NORTH, WEST, EAST, SOUTH]))
  return state
