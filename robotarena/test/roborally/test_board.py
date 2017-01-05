import pytest
from roborally.constants import *
import roborally.manager as manager

@pytest.fixture
def state():
  return manager.create_empty_state(8)

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
