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

class Robot:
  def __init__(self):
    self.life = 10

def create_empty_state(size):
  return GameState(size)

def create_robot():
  return Robot()

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
