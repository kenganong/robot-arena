import pytest
import roborally.api as api

# & & & & & & & & & & &
# & & · · · · · · · · ·
# & & · · · · / · · · ·
# & & · · · } · · · ·←T
# & &→L · ·↑L · · ·←M ·
# & & · · ·↑S · · ·←M ·
# & & · · · · · · · # ·
# & & · · ·←L · · · < ·
# & & · · · · · · · # ·
# & & · · · · · · · # ·
# & & · · · # ^ # # # #
def setup_sight():
  class Cell:
    def __init__(self):
      self.floor = api.EMPTY
      self.content = None
  api.SIGHT = [[Cell() for j in range(11)] for i in range(11)]
  for x in range(11):
    put_pit((0, x))
    put_pit((x, 0))
    put_pit((x, 1))
  put_wall((6, 9), 50)
  put_wall((8, 9), 30)
  put_wall((9, 9), 50)
  put_wall((10, 5), 25)
  put_wall((10, 7), 32)
  put_wall((10, 8), 48)
  put_wall((10, 9), 50)
  put_wall((10, 10), 50)
  put_mounted((7, 9), 44, api.LEFT)
  put_mounted((10, 6), 32, api.AHEAD)
  put_corpse((2, 6), 8)
  put_spinner((3, 5), api.RIGHT_SPINNER)
  put_robot((3, 10), 10, api.LEFT, 'Thomas')
  put_robot((4, 2), 7, api.RIGHT, 'Larry')
  put_robot((4, 5), 2, api.AHEAD, 'Larry')
  put_robot((4, 9), 10, api.LEFT, 'Mary')
  put_robot((5, 9), 9, api.LEFT, 'Mary')
  put_robot((7, 5), 3, api.LEFT, 'Larry')
  put_robot((5, 5), 7, api.AHEAD, 'Self')
  api.SIGHT[5][5].content[api.FLAGS_SCORED] = 1
  api.SIGHT[5][5].content[api.CHARGES] = 2
  api.SIGHT[5][5].content[api.MEMORY] = {'Keys': 'Home'}
  api.SIGHT[5][5].content[api.FLAG_SENSE] = [api.BEHIND, api.RIGHT]

def put_robot(pos, life, facing, name):
  api.SIGHT[pos[0]][pos[1]].content = {api.TYPE: api.ROBOT, api.POSITION: pos, api.LIFE: life,
                                       api.FACING: facing, api.NAME: name}

def put_corpse(pos, life):
  api.SIGHT[pos[0]][pos[1]].content = {api.TYPE: api.CORPSE, api.POSITION: pos, api.LIFE: life,
                                       api.FACING: api.AHEAD, api.NAME: api.CORPSE}

def put_mounted(pos, life, facing):
  api.SIGHT[pos[0]][pos[1]].content = {api.TYPE: api.MOUNTED_LASER, api.POSITION: pos, api.LIFE: life,
                                       api.FACING: facing, api.NAME: api.MOUNTED_LASER}

def put_wall(pos, life):
  api.SIGHT[pos[0]][pos[1]].content = {api.TYPE: api.WALL, api.POSITION: pos, api.LIFE: life,
                                       api.FACING: api.AHEAD, api.NAME: api.WALL}

def put_pit(pos):
  api.SIGHT[pos[0]][pos[1]].floor = None

def put_spinner(pos, spin_type):
  api.SIGHT[pos[0]][pos[1]].floor = spin_type

def test_get_pos_in_direction():
  assert api.get_pos_in_direction((6, 3), api.AHEAD) == (5, 3)
  assert api.get_pos_in_direction((6, 3), api.AHEAD, 3) == (3, 3)
  assert api.get_pos_in_direction((6, 3), api.RIGHT) == (6, 4)
  assert api.get_pos_in_direction((6, 3), api.RIGHT, 3) == (6, 6)
  assert api.get_pos_in_direction((6, 3), api.BEHIND) == (7, 3)
  assert api.get_pos_in_direction((6, 3), api.BEHIND, 3) == (9, 3)
  assert api.get_pos_in_direction((6, 3), api.LEFT) == (6, 2)
  assert api.get_pos_in_direction((6, 3), api.LEFT, 3) == (6, 0)

def test_opposite_direction():
  assert api.opposite_direction(api.AHEAD) == api.BEHIND
  assert api.opposite_direction(api.BEHIND) == api.AHEAD
  assert api.opposite_direction(api.LEFT) == api.RIGHT
  assert api.opposite_direction(api.RIGHT) == api.LEFT

def test_myself():
  setup_sight()
  assert api.myself()[api.NAME] == 'Self'
  assert api.memory()['Keys'] == 'Home'
  assert api.charges() == 2
  assert api.flags() == 1
  assert api.life() == 7
  flag_sense = api.sense_flag()
  assert len(flag_sense) == 2
  assert api.BEHIND in flag_sense and api.RIGHT in flag_sense
