import os
import random
import pytest
from roborally.constants import *
import roborally.manager as manager

@pytest.fixture
def state():
  return manager.create_empty_state(8)

@pytest.fixture
def test_state():
  file_name = os.path.join(os.path.dirname(__file__), 'test_board_1.txt')
  with open(file_name, 'r') as board_file:
    return manager.create_state(board_file)

@pytest.fixture
def robot_brains():
  brains = []
  class Stand:
    def get_move():
      return SHOOT
  class RandomBot:
    def get_move():
      return random.choice(MOVES)
  brains.append(manager.create_brain('Stand', Stand()))
  brains.append(manager.create_brain('Random', RandomBot()))
  return brains

def laser_assertions(state, items, before_life, after_life):
  for i in range(len(items)):
    assert items[i].life == before_life[i]
  manager.perform_lasers(state)
  for i in range(len(items)):
    assert items[i].life == after_life[i]

def test_get_pos_in_direction():
  assert manager.get_pos_in_direction((6, 3), NORTH) == (5, 3)
  assert manager.get_pos_in_direction((6, 3), NORTH, 3) == (3, 3)
  assert manager.get_pos_in_direction((6, 3), EAST) == (6, 4)
  assert manager.get_pos_in_direction((6, 3), EAST, 3) == (6, 6)
  assert manager.get_pos_in_direction((6, 3), SOUTH) == (7, 3)
  assert manager.get_pos_in_direction((6, 3), SOUTH, 3) == (9, 3)
  assert manager.get_pos_in_direction((6, 3), WEST) == (6, 2)
  assert manager.get_pos_in_direction((6, 3), WEST, 3) == (6, 0)

def test_robot_laser_immediate(state):
  robot_shooter = manager.create_robot()
  robot_shot = manager.create_robot()
  state.put_robot((6, 3), robot_shooter, NORTH)
  state.put_robot((5, 3), robot_shot, WEST)
  laser_assertions(state, (robot_shooter, robot_shot), (10, 10), (10, 9))

def test_robot_laser_nearby(state):
  robot_shooter = manager.create_robot()
  robot_shot = manager.create_robot()
  state.put_robot((6, 3), robot_shooter, NORTH)
  state.put_robot((4, 3), robot_shot, WEST)
  laser_assertions(state, (robot_shooter, robot_shot), (10, 10), (10, 9))

def test_robot_laser_far(state):
  robot_shooter = manager.create_robot()
  robot_shot = manager.create_robot()
  state.put_robot((7, 3), robot_shooter, NORTH)
  state.put_robot((0, 3), robot_shot, WEST)
  laser_assertions(state, (robot_shooter, robot_shot), (10, 10), (10, 9))

def test_robot_laser_crossfire(state):
  r1 = manager.create_robot()
  r2 = manager.create_robot()
  r3 = manager.create_robot()
  r4 = manager.create_robot()
  r5 = manager.create_robot()
  state.put_robot((6, 3), r1, NORTH)
  state.put_robot((5, 3), r2, SOUTH)
  state.put_robot((3, 3), r3, SOUTH)
  state.put_robot((4, 2), r4, EAST)
  state.put_robot((4, 4), r5, SOUTH)
  laser_assertions(state, (r1, r2, r3, r4, r5), (10, 10, 10, 10, 10), (9, 8, 10, 10, 9))

def board_assertions(test_state):
  positions_seen = 0
  for cell, pos in test_state.board.traverse():
    row, col = pos
    positions_seen += 1
    if row == 19 or row == 20:
      if col < 5 or col >= 35:
        assert cell.content == None or cell.content.type == ROBOT
      elif col == 6 or col == 33:
        assert cell.content.type == LASER
        if row == 19:
          assert cell.facing == NORTH
        else:
          assert cell.facing == SOUTH
      else:
        assert cell.content.type == WALL
    elif col == 19 or col == 20:
      if row < 5 or row >= 35:
        assert cell.content == None or cell.content.type == ROBOT
      elif row == 6 or row == 33:
        assert cell.content.type == LASER
        if col == 19:
          assert cell.facing == WEST
        else:
          assert cell.facing == EAST
      else:
        assert cell.content.type == WALL
    elif row == 9 and col == 25:
      assert cell.floor.type == FLAG
      assert cell.floor.number == 1
    elif row == 25 and col == 25:
      assert cell.floor.type == FLAG
      assert cell.floor.number == 2
    elif row == 14 and col == 13:
      assert cell.floor.type == FLAG
      assert cell.floor.number == 3
    elif row == 26 and col == 13:
      assert cell.floor.type == FLAG
      assert cell.floor.number == 4
    elif row == 16 and col == 28:
      assert cell.floor.type == FLAG
      assert cell.floor.number == 5
    else:
      assert cell.floor == EMPTY
      assert cell.content == None or cell.content.type == ROBOT
  assert positions_seen == 1600

def test_open_board_file(test_state):
  board_assertions(test_state)

def test_place_robots(test_state, robot_brains):
  manager.place_robots(test_state, robot_brains)
  robots_seen = 0
  for cell, pos in test_state.board.traverse():
    if cell.content != None and cell.content.type == ROBOT:
      robots_seen += 1
  assert robots_seen == 40
  board_assertions(test_state) # Verify placing robots didn't destroy a wall
