import random
from roborally.constants import *
import common.model.board as board_api

class Cell:
  def __init__(self):
    self.floor = EMPTY
    self.content = None
    self.facing = NORTH

class GameState:
  def __init__(self, size):
    self.board = board_api.init_board((size, size), lambda: Cell())
    self.iteration = 0
  def put_robot(self, pos, robot, facing):
    cell = self.board.get_item(pos)
    if cell != None:
      cell.content = robot
      cell.facing = facing

class Brain:
  def __init__(self, name, module):
    self.name = name
    self.module = module

class Robot:
  def __init__(self):
    self.life = 10
    self.type = ROBOT

class Wall:
  def __init__(self):
    self.life = 50
    self.type = WALL

class Laser:
  def __init__(self):
    self.life = 50
    self.type = LASER

class Flag:
  def __init__(self, number):
    self.number = number
    self.type = FLAG

def create_empty_state(size):
  return GameState(size)

def create_state(board_file):
  lines = [line.rstrip('\n') for line in board_file]
  size = max(len(lines), max(len(line) for line in lines))
  state = create_empty_state(size)
  for row in range(len(lines)):
    for col in range(len(lines[row])):
      char = lines[row][col]
      thing = None
      floor = EMPTY
      facing = NORTH
      if char == '#':
        thing = Wall()
      elif char == '^':
        thing = Laser()
      elif char == 'v':
        thing = Laser()
        facing = SOUTH
      elif char == '<':
        thing = Laser()
        facing = WEST
      elif char == '>':
        thing = Laser()
        facing = EAST
      elif char.isdigit():
        floor = Flag(int(char))
      cell = state.board.get_item((row, col))
      cell.content = thing
      cell.floor = floor
      cell.facing = facing
  return state

def create_brain(name, module):
  return Brain(name, module)

def create_robot():
  return Robot()

def place_robots(state, robot_brains):
  robots = []
  for brain in robot_brains:
    for i in range(20):
      robot = create_robot()
      robot.brain = brain
      robots.append(robot)
  empty_spaces = [pos for cell, pos in state.board.traverse() if cell.content == None]
  places = random.sample(empty_spaces, len(robots))
  for robot, pos in zip(robots, places):
    facing = random.choice(DIRECTIONS)
    state.put_robot(pos, robot, facing)
  state.robots = robots

def get_pos_in_direction(pos, direction, distance=1):
  return tuple(x + y for x, y in zip(pos, tuple(distance * z for z in direction)))

def perform_lasers(state):
  for cell, pos in state.board.traverse():
    if cell.content != None and isinstance(cell.content, Robot):
      laser_pos = pos
      while True:
        laser_pos = get_pos_in_direction(laser_pos, cell.facing)
        laser_cell = state.board.get_item(laser_pos)
        if laser_cell == None:
          break;
        elif laser_cell.content != None:
          laser_cell.content.life -= 1
          break;
