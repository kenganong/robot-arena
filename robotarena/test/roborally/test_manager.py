import pytest
from roborally.api import *
from roborally.game_state import *
import roborally.manager as manager

@pytest.fixture
def state():
  return RoboRallyGameState(16)

@pytest.fixture
def brains():
  robot_brains = {}
  class Stand:
    def move(self):
      return LASER
  class RandomBot:
    def move(self):
      return random.choice(MOVES)
  class HammerBot:
    def move(self):
      my_memory = myself()[MEMORY]
      if 'moved' in my_memory:
        del my_memory['moved']
        return SIDESTEP_LEFT
      else:
        my_memory['moved'] = True
        return SIDESTEP_RIGHT
  class BadBot:
    def move(self):
      raise ValueError
  robot_brains['Stand'] = Brain('Stand', Stand())
  robot_brains['Random'] = Brain('Random', RandomBot())
  robot_brains['HammerBot'] = Brain('HammerBot', HammerBot())
  robot_brains['BadBot'] = Brain('BadBot', BadBot())
  return robot_brains

def put_robot(state, brain, facing, pos):
  robot = make_robot(brain, facing)
  state.board.get_item(pos).content = robot
  return robot

def put_corpse(state, pos):
  corpse = make_corpse()
  state.board.get_item(pos).content = corpse
  return corpse

def put_spinner(state, spinner_type, pos):
  state.board.get_item(pos).floor = spinner_type

def put_flag(state, flag_num, pos):
  state.board.get_item(pos).floor = FLAG + str(flag_num)

def test_record_moves(state, brains):
  put_robot(state, brains['HammerBot'], NORTH, (1, 1))
  put_robot(state, brains['Stand'], WEST, (2, 3))
  put_robot(state, brains['BadBot'], NORTH, (8, 4))
  manager.record_moves_for_robots(state)
  assert state.get_content((1, 1))['move'] == SIDESTEP_RIGHT
  assert state.get_content((2, 3))['move'] == LASER
  assert state.get_content((8, 4))['move'] == LASER
  assert state.get_content((8, 4))[LIFE] == 9
  manager.record_moves_for_robots(state)
  assert state.get_content((1, 1))['move'] == SIDESTEP_LEFT
  assert state.get_content((2, 3))['move'] == LASER
  assert state.get_content((8, 4))['move'] == LASER
  assert state.get_content((8, 4))[LIFE] == 8

def test_perform_priority_moves(state, brains):
  r1 = put_robot(state, brains['Stand'], NORTH, (3, 3))
  r1['move'] = SIDESTEP_RIGHT
  r2 = put_robot(state, brains['Stand'], WEST, (0, 0))
  r2['move'] = FORWARD_TWO
  r3 = put_robot(state, brains['Stand'], NORTH, (4, 5))
  r3['move'] = SIDESTEP_LEFT
  r3[CHARGES] = 0
  r4 = put_robot(state, brains['Stand'], SOUTH, (5, 5))
  r4['move'] = RIGHT
  r5 = put_robot(state, brains['Stand'], WEST, (5, 6))
  r5['move'] = LASER
  manager.perform_priority_moves(state)
  assert r1[LIFE] == 10
  assert r1[CHARGES] == 0
  assert r1[FACING] == NORTH
  assert state.get_content((3, 4)) == r1
  for cell, pos in state.board.traverse():
    assert cell.content != r2
  assert r3[LIFE] == 9
  assert r3[CHARGES] == 0
  assert r3[FACING] == NORTH
  assert state.get_content((4, 4)) == r3
  assert r4[LIFE] == 10
  assert r4[CHARGES] == 1
  assert state.get_content((5, 5)) == r4
  assert r5[LIFE] == 10
  assert r5[CHARGES] == 1
  assert state.get_content((5, 6)) == r5

def test_perform_normal_moves(state, brains):
  r1 = put_robot(state, brains['Stand'], NORTH, (3, 3))
  r1['move'] = SIDESTEP_RIGHT
  r2 = put_robot(state, brains['Stand'], WEST, (0, 0))
  r2['move'] = FORWARD
  r3 = put_robot(state, brains['Stand'], NORTH, (4, 5))
  r3['move'] = SIDESTEP_LEFT
  r3[CHARGES] = 0
  r4 = put_robot(state, brains['Stand'], SOUTH, (5, 5))
  r4['move'] = TURN_RIGHT
  r5 = put_robot(state, brains['Stand'], WEST, (5, 6))
  r5['move'] = LASER
  r6 = put_robot(state, brains['Stand'], WEST, (1, 3))
  r6['move'] = REVERSE
  r7 = put_robot(state, brains['Stand'], SOUTH, (1, 4))
  r7['move'] = U_TURN
  manager.perform_moves(state)
  assert r1[LIFE] == 10
  assert r1[CHARGES] == 1
  assert r1[FACING] == NORTH
  assert state.get_content((3, 3)) == r1
  for cell, pos in state.board.traverse():
    assert cell.content != r2
  assert r3[LIFE] == 10
  assert r3[CHARGES] == 0
  assert r3[FACING] == NORTH
  assert state.get_content((4, 5)) == r3
  assert r4[LIFE] == 10
  assert r4[CHARGES] == 1
  assert r4[FACING] == WEST
  assert state.get_content((5, 5)) == r4
  assert r5[LIFE] == 10
  assert r5[FACING] == WEST
  assert state.get_content((5, 6)) == r5
  assert r6[LIFE] == 10
  assert r6[FACING] == WEST
  assert state.get_content((1, 4)) == r6
  assert r7[LIFE] == 10
  assert r7[FACING] == NORTH
  assert state.get_content((1, 5)) == r7

def test_perform_attack_moves(state, brains):
  r1 = put_robot(state, brains['Stand'], NORTH, (3, 3))
  r1['move'] = SIDESTEP_RIGHT
  r2 = put_robot(state, brains['Stand'], WEST, (0, 0))
  r2['move'] = FORWARD
  r3 = put_robot(state, brains['Stand'], NORTH, (4, 5))
  r3['move'] = SIDESTEP_LEFT
  r3[CHARGES] = 0
  r4 = put_robot(state, brains['Stand'], SOUTH, (5, 5))
  r4['move'] = TURN_RIGHT
  r5 = put_robot(state, brains['Stand'], WEST, (5, 6))
  r5['move'] = LASER
  r6 = put_robot(state, brains['Stand'], WEST, (1, 3))
  r6['move'] = REVERSE
  r7 = put_robot(state, brains['Stand'], SOUTH, (1, 4))
  r7['move'] = U_TURN
  manager.perform_laser_moves(state)
  assert r1[LIFE] == 10
  assert r1[CHARGES] == 1
  assert r1[FACING] == NORTH
  assert state.get_content((3, 3)) == r1
  assert r2[LIFE] == 10
  assert r2[CHARGES] == 1
  assert r2[FACING] == WEST
  assert state.get_content((0, 0)) == r2
  assert r3[LIFE] == 10
  assert r3[CHARGES] == 0
  assert r3[FACING] == NORTH
  assert state.get_content((4, 5)) == r3
  assert r4[LIFE] == 9
  assert r4[CHARGES] == 1
  assert r4[FACING] == SOUTH
  assert state.get_content((5, 5)) == r4
  assert r5[LIFE] == 10
  assert r5[FACING] == WEST
  assert state.get_content((5, 6)) == r5
  assert r6[LIFE] == 10
  assert r6[FACING] == WEST
  assert state.get_content((1, 3)) == r6
  assert r7[LIFE] == 10
  assert r7[FACING] == SOUTH
  assert state.get_content((1, 4)) == r7

def test_spinners(state, brains):
  r1 = put_robot(state, brains['Stand'], NORTH, (3, 3))
  r2 = put_robot(state, brains['Stand'], WEST, (0, 0))
  r3 = put_robot(state, brains['Stand'], EAST, (4, 5))
  put_spinner(state, LEFT_SPINNER, (3, 3))
  put_spinner(state, RIGHT_SPINNER, (4, 5))
  manager.perform_spinners(state)
  assert r1[LIFE] == 10
  assert r1[CHARGES] == 1
  assert r1[FACING] == WEST
  assert state.get_content((3, 3)) == r1
  assert r2[FACING] == WEST
  assert state.get_content((0, 0)) == r2
  assert r3[FACING] == SOUTH
  assert state.get_content((4, 5)) == r3

def test_handle_destroyed(state, brains):
  r1 = put_robot(state, brains['Stand'], NORTH, (3, 3))
  r2 = put_robot(state, brains['Stand'], WEST, (0, 0))
  r2[LIFE] = 3
  r3 = put_robot(state, brains['Stand'], EAST, (4, 5))
  r3[LIFE] = 1
  r4 = put_robot(state, brains['Stand'], EAST, (7, 7))
  r4[LIFE] = 0
  c1 = put_corpse(state, (3, 4))
  c1[LIFE] = 2
  c2 = put_corpse(state, (1, 1))
  c2[LIFE] = 0
  c3 = put_corpse(state, (4, 6))
  c3[LIFE] = 1
  c4 = put_corpse(state, (3, 5))
  c4[LIFE] = 1
  c5 = put_corpse(state, (5, 7))
  c5[LIFE] = 0
  manager.handle_destroyed(state)
  assert r1[LIFE] == 10
  assert state.get_content((3, 3)) == r1
  assert r2[LIFE] == 2
  assert state.get_content((0, 0)) == r2
  c6 = state.get_content((4, 5))
  assert c6 != None
  assert c6[TYPE] == CORPSE
  assert c6[LIFE] == 10
  c7 = state.get_content((7, 7))
  assert c7 != None
  assert c7[TYPE] == CORPSE
  assert c7[LIFE] == 10
  assert c1[LIFE] == 1
  assert state.get_content((3, 4)) == c1
  for cell, pos in state.board.traverse():
    assert cell.content != r3
    assert cell.content != r4
    assert cell.content != c2
    assert cell.content != c3
    assert cell.content != c4
    assert cell.content != c5

def test_handle_flags(state, brains):
  r1 = put_robot(state, brains['Stand'], NORTH, (3, 3))
  r1[FLAGS_SCORED] = 3
  r2 = put_robot(state, brains['Stand'], WEST, (0, 0))
  r2[FLAGS_SCORED] = 2
  r3 = put_robot(state, brains['Stand'], EAST, (4, 5))
  r3[FLAGS_SCORED] = 2
  r4 = put_robot(state, brains['Stand'], SOUTH, (7, 7))
  r4[FLAGS_SCORED] = 0
  put_flag(state, 1, (3, 3))
  put_flag(state, 2, (7, 7))
  put_flag(state, 3, (4, 5))
  manager.handle_flags(state)
  assert r1[FLAGS_SCORED] == 3
  assert r2[FLAGS_SCORED] == 2
  assert r3[FLAGS_SCORED] == 3
  assert r4[FLAGS_SCORED] == 0

def test_charge_up(state, brains):
  r1 = put_robot(state, brains['Stand'], NORTH, (3, 3))
  r1[CHARGES] = 3
  r2 = put_robot(state, brains['Stand'], WEST, (0, 0))
  r2[CHARGES] = 2
  r3 = put_robot(state, brains['Stand'], EAST, (4, 5))
  r3[CHARGES] = 0
  manager.charge_up(state)
  assert r1[CHARGES] == 3
  assert r2[CHARGES] == 2
  assert r3[CHARGES] == 0
  state.iteration = 3
  manager.charge_up(state)
  assert r1[CHARGES] == 3
  assert r2[CHARGES] == 2
  assert r3[CHARGES] == 0
  state.iteration = 9
  manager.charge_up(state)
  assert r1[CHARGES] == 4
  assert r2[CHARGES] == 3
  assert r3[CHARGES] == 1
  state.iteration = 10
  manager.charge_up(state)
  assert r1[CHARGES] == 4
  assert r2[CHARGES] == 3
  assert r3[CHARGES] == 1
  state.iteration = 19
  manager.charge_up(state)
  assert r1[CHARGES] == 5
  assert r2[CHARGES] == 4
  assert r3[CHARGES] == 2

def laser_assertions(state, items, before_life, after_life):
  for i in range(len(items)):
    assert items[i][LIFE] == before_life[i]
  manager.perform_lasers(state)
  for i in range(len(items)):
    assert items[i][LIFE] == after_life[i]

def test_robot_laser_immediate(state, brains):
  robot_shooter = put_robot(state, brains['Stand'], NORTH, (6, 3))
  robot_shot = put_robot(state, brains['Stand'], WEST, (5, 3))
  laser_assertions(state, (robot_shooter, robot_shot), (10, 10), (10, 9))

def test_robot_laser_nearby(state, brains):
  robot_shooter = put_robot(state, brains['Stand'], NORTH, (6, 3))
  robot_shot = put_robot(state, brains['Stand'], WEST, (4, 3))
  laser_assertions(state, (robot_shooter, robot_shot), (10, 10), (10, 9))

def test_robot_laser_far(state, brains):
  robot_shooter = put_robot(state, brains['Stand'], NORTH, (7, 3))
  robot_shot = put_robot(state, brains['Stand'], WEST, (0, 3))
  laser_assertions(state, (robot_shooter, robot_shot), (10, 10), (10, 9))

def test_robot_laser_crossfire(state, brains):
  r1 = put_robot(state, brains['Stand'], NORTH, (6, 3))
  r2 = put_robot(state, brains['Stand'], SOUTH, (5, 3))
  r3 = put_robot(state, brains['Stand'], SOUTH, (3, 3))
  r4 = put_robot(state, brains['Stand'], EAST, (4, 2))
  r5 = put_robot(state, brains['Stand'], SOUTH, (4, 4))
  laser_assertions(state, (r1, r2, r3, r4, r5), (10, 10, 10, 10, 10), (9, 8, 10, 10, 9))
