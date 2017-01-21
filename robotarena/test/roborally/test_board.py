import os
import random
import pytest
from roborally.api import *
import roborally.game_state as game_state

@pytest.fixture
def no_brain_state():
  file_name = os.path.join(os.path.dirname(__file__), 'test_board_1.txt')
  with open(file_name, 'r') as board_file:
    return game_state.create_state(board_file, [])

@pytest.fixture
def robot_brains():
  brains = []
  class Stand:
    def get_move():
      return LASER
  class RandomBot:
    def get_move():
      return random.choice(MOVES)
  brains.append(game_state.Brain('Stand', Stand()))
  brains.append(game_state.Brain('Random', RandomBot()))
  return brains

@pytest.fixture
def brain_state():
  brains = robot_brains()
  file_name = os.path.join(os.path.dirname(__file__), 'test_board_1.txt')
  with open(file_name, 'r') as board_file:
    return game_state.create_state(board_file, brains)

def board_assertions(test_state):
  positions_seen = 0
  for cell, pos in test_state.board.traverse():
    row, col = pos
    positions_seen += 1
    if row == 19 or row == 20:
      if col < 5 or col >= 35:
        assert cell.content == None or cell.content[TYPE] == ROBOT
      elif col == 6 or col == 33:
        assert cell.content[TYPE] == MOUNTED_LASER
        if row == 19:
          assert cell.content[FACING] == game_state.NORTH
        else:
          assert cell.content[FACING] == game_state.SOUTH
      else:
        assert cell.content[TYPE] == WALL
    elif col == 19 or col == 20:
      if row < 5 or row >= 35:
        assert cell.content == None or cell.content[TYPE] == ROBOT
      elif row == 6 or row == 33:
        assert cell.content[TYPE] == MOUNTED_LASER
        if col == 19:
          assert cell.content[FACING] == game_state.WEST
        else:
          assert cell.content[FACING] == game_state.EAST
      else:
        assert cell.content[TYPE] == WALL
    elif row == 9 and col == 25:
      assert cell.floor.startswith(FLAG)
      assert int(cell.floor[len(FLAG):]) == 1
    elif row == 25 and col == 25:
      assert cell.floor.startswith(FLAG)
      assert int(cell.floor[len(FLAG):]) == 2
    elif row == 14 and col == 13:
      assert cell.floor.startswith(FLAG)
      assert int(cell.floor[len(FLAG):]) == 3
    elif row == 26 and col == 13:
      assert cell.floor.startswith(FLAG)
      assert int(cell.floor[len(FLAG):]) == 4
    elif row == 16 and col == 28:
      assert cell.floor.startswith(FLAG)
      assert int(cell.floor[len(FLAG):]) == 5
    else:
      assert cell.floor == EMPTY
      assert cell.content == None or cell.content[TYPE] == ROBOT
  assert positions_seen == 1600
  assert test_state.flags[0] == (9, 25)
  assert test_state.flags[1] == (25, 25)
  assert test_state.flags[2] == (14, 13)
  assert test_state.flags[3] == (26, 13)
  assert test_state.flags[4] == (16, 28)

def test_open_board_file(no_brain_state):
  board_assertions(no_brain_state)

def test_place_robots(brain_state):
  assert len(brain_state.brains) == 2
  robots_seen = 0
  for cell, pos in brain_state.board.traverse():
    if cell.content != None and cell.content[TYPE] == ROBOT:
      robots_seen += 1
  assert robots_seen == 2 * game_state.NUM_ROBOTS_PER_BRAIN
  board_assertions(brain_state) # Verify placing robots didn't destroy a wall
