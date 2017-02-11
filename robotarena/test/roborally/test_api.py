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

def test_opposite_move():
  assert api.opposite_move(api.LASER) == api.LASER
  assert api.opposite_move(api.FORWARD) == api.REVERSE
  assert api.opposite_move(api.FORWARD_TWO) == api.REVERSE
  assert api.opposite_move(api.REVERSE) == api.FORWARD
  assert api.opposite_move(api.SIDESTEP_LEFT) == api.SIDESTEP_RIGHT
  assert api.opposite_move(api.SIDESTEP_RIGHT) == api.SIDESTEP_LEFT
  assert api.opposite_move(api.TURN_LEFT) == api.TURN_RIGHT
  assert api.opposite_move(api.TURN_RIGHT) == api.TURN_LEFT
  assert api.opposite_move(api.U_TURN) == api.U_TURN

def test_moves_in_direction():
  moves = api.moves_in_direction(api.AHEAD)
  assert len(moves) == 2
  assert api.FORWARD in moves
  assert api.FORWARD_TWO in moves
  moves = api.moves_in_direction(api.RIGHT)
  assert len(moves) == 2
  assert api.TURN_RIGHT in moves
  assert api.SIDESTEP_RIGHT in moves
  moves = api.moves_in_direction(api.BEHIND)
  assert len(moves) == 2
  assert api.U_TURN in moves
  assert api.REVERSE in moves
  moves = api.moves_in_direction(api.LEFT)
  assert len(moves) == 2
  assert api.TURN_LEFT in moves
  assert api.SIDESTEP_LEFT in moves

def test_moves_in_directions():
  moves = api.moves_in_directions([api.AHEAD, api.LEFT])
  assert len(moves) == 4
  assert api.FORWARD in moves
  assert api.FORWARD_TWO in moves
  assert api.TURN_LEFT in moves
  assert api.SIDESTEP_LEFT in moves
  moves = api.moves_in_directions([api.BEHIND, api.RIGHT])
  assert len(moves) == 4
  assert api.TURN_RIGHT in moves
  assert api.SIDESTEP_RIGHT in moves
  assert api.U_TURN in moves
  assert api.REVERSE in moves
  moves = api.moves_in_directions([api.BEHIND, api.AHEAD])
  assert len(moves) == 4
  assert api.FORWARD in moves
  assert api.FORWARD_TWO in moves
  assert api.U_TURN in moves
  assert api.REVERSE in moves
  my_moves = [api.TURN_RIGHT, api.SIDESTEP_RIGHT, api.REVERSE]
  moves = api.moves_in_directions([api.BEHIND, api.AHEAD], my_moves)
  assert len(moves) == 1
  assert api.REVERSE in moves
  moves = api.moves_in_directions([api.LEFT, api.AHEAD], my_moves)
  assert len(moves) == 0

def test_moves_in_direction_parameter():
  my_moves = [api.TURN_RIGHT, api.SIDESTEP_RIGHT, api.REVERSE]
  moves = api.moves_in_direction(api.AHEAD, my_moves)
  assert len(moves) == 0
  moves = api.moves_in_direction(api.LEFT, my_moves)
  assert len(moves) == 0
  moves = api.moves_in_direction(api.BEHIND, my_moves)
  assert len(moves) == 1
  assert api.REVERSE in moves
  moves = api.moves_in_direction(api.RIGHT, my_moves)
  assert len(moves) == 2
  assert api.TURN_RIGHT in moves
  assert api.SIDESTEP_RIGHT in moves

def test_direction_of_move():
  assert api.direction_of_move(api.FORWARD) == api.AHEAD
  assert api.direction_of_move(api.FORWARD_TWO) == api.AHEAD
  assert api.direction_of_move(api.REVERSE) == api.BEHIND
  assert api.direction_of_move(api.SIDESTEP_LEFT) == api.LEFT
  assert api.direction_of_move(api.SIDESTEP_RIGHT) == api.RIGHT
  assert not api.direction_of_move(api.LASER)
  assert not api.direction_of_move(api.TURN_RIGHT)
  assert not api.direction_of_move(api.TURN_LEFT)
  assert not api.direction_of_move(api.U_TURN)

def test_convert_direction():
  for direction in api.CLOCKWISE:
    assert api.convert_direction(api.AHEAD, direction) == direction
    assert api.convert_direction(direction, direction) == api.AHEAD
  assert api.convert_direction(api.RIGHT, api.AHEAD) == api.LEFT
  assert api.convert_direction(api.RIGHT, api.BEHIND) == api.RIGHT
  assert api.convert_direction(api.RIGHT, api.LEFT) == api.BEHIND
  assert api.convert_direction(api.LEFT, api.AHEAD) == api.RIGHT
  assert api.convert_direction(api.LEFT, api.RIGHT) == api.BEHIND
  assert api.convert_direction(api.LEFT, api.BEHIND) == api.LEFT
  assert api.convert_direction(api.BEHIND, api.RIGHT) == api.LEFT
  assert api.convert_direction(api.BEHIND, api.LEFT) == api.RIGHT
  assert api.convert_direction(api.BEHIND, api.AHEAD) == api.BEHIND

def test_turn_direction():
  assert api.turn_direction(api.AHEAD, True) == api.RIGHT
  assert api.turn_direction(api.RIGHT, True) == api.BEHIND
  assert api.turn_direction(api.BEHIND, True) == api.LEFT
  assert api.turn_direction(api.LEFT, True) == api.AHEAD
  assert api.turn_direction(api.AHEAD, False) == api.LEFT
  assert api.turn_direction(api.LEFT, False) == api.BEHIND
  assert api.turn_direction(api.BEHIND, False) == api.RIGHT
  assert api.turn_direction(api.RIGHT, False) == api.AHEAD

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

def test_get_cell_in_sight():
  setup_sight()
  assert not api.get_cell_in_sight((-1, 0))
  assert not api.get_cell_in_sight((1, -4))
  assert not api.get_cell_in_sight((11, 4))
  assert not api.get_cell_in_sight((6, 12))
  cell = api.get_cell_in_sight((3, 4))
  assert not cell.content
  assert cell.floor == api.EMPTY
  cell = api.get_cell_in_sight((4, 2))
  assert cell.content and cell.content[api.TYPE] == api.ROBOT
  assert cell.content[api.NAME] == 'Larry'
  assert cell.floor == api.EMPTY
  cell = api.get_cell_in_sight((3, 5))
  assert not cell.content
  assert cell.floor == api.RIGHT_SPINNER
  cell = api.get_cell_in_sight((7, 9))
  assert cell.content and cell.content[api.TYPE] == api.MOUNTED_LASER
  assert cell.content[api.FACING] == api.LEFT

def test_direction_toward():
  directions = api.direction_toward((8, 8), (8, 11))
  assert len(directions) == 1
  assert api.RIGHT in directions
  directions = api.direction_toward((6, 7), (6, 3))
  assert len(directions) == 1
  assert api.LEFT in directions
  directions = api.direction_toward((8, 9), (5, 9))
  assert len(directions) == 1
  assert api.AHEAD in directions
  directions = api.direction_toward((7, 5), (11, 5))
  assert len(directions) == 1
  assert api.BEHIND in directions
  directions = api.direction_toward((8, 8), (5, 11))
  assert len(directions) == 2
  assert api.RIGHT in directions
  assert api.AHEAD in directions
  directions = api.direction_toward((8, 8), (11, 11))
  assert len(directions) == 2
  assert api.BEHIND in directions
  assert api.RIGHT in directions
  directions = api.direction_toward((8, 8), (11, 5))
  assert len(directions) == 2
  assert api.BEHIND in directions
  assert api.LEFT in directions
  directions = api.direction_toward((8, 8), (5, 5))
  assert len(directions) == 2
  assert api.AHEAD in directions
  assert api.LEFT in directions
  directions = api.direction_toward((8, 8), (8, 8))
  assert len(directions) == 0

def test_direction_toward_far():
  directions = api.direction_toward((8, 8), (9, 15))
  assert len(directions) == 1
  assert api.RIGHT in directions
  directions = api.direction_toward((6, 7), (7, 0))
  assert len(directions) == 1
  assert api.LEFT in directions
  directions = api.direction_toward((9, 9), (1, 7))
  assert len(directions) == 1
  assert api.AHEAD in directions
  directions = api.direction_toward((7, 5), (11, 4))
  assert len(directions) == 1
  assert api.BEHIND in directions

def test_pos_after_move():
  setup_sight()
  assert api.position_after_move(api.LASER) == (5, 5)
  assert api.position_after_move(api.TURN_LEFT) == (5, 5)
  assert api.position_after_move(api.TURN_RIGHT) == (5, 5)
  assert api.position_after_move(api.U_TURN) == (5, 5)
  assert api.position_after_move(api.REVERSE) == (6, 5)
  assert api.position_after_move(api.FORWARD) == (4, 5)
  assert api.position_after_move(api.FORWARD_TWO) == (3, 5)
  assert api.position_after_move(api.SIDESTEP_LEFT) == (5, 4)
  assert api.position_after_move(api.SIDESTEP_RIGHT) == (5, 6)
  put_pit((5, 6))
  assert api.position_after_move(api.SIDESTEP_RIGHT) == None
  put_wall((6, 5), 40)
  assert api.position_after_move(api.REVERSE) == (5, 5)
  put_wall((2, 5), 50)
  assert api.position_after_move(api.FORWARD_TWO) == (4, 5)

def test_direction_after_move():
  setup_sight()
  assert api.direction_after_move(api.LASER) == api.AHEAD
  assert api.direction_after_move(api.TURN_LEFT) == api.LEFT
  assert api.direction_after_move(api.TURN_RIGHT) == api.RIGHT
  assert api.direction_after_move(api.U_TURN) == api.BEHIND
  assert api.direction_after_move(api.REVERSE) == api.AHEAD
  assert api.direction_after_move(api.FORWARD) == api.AHEAD
  assert api.direction_after_move(api.FORWARD_TWO) == api.RIGHT
  assert api.direction_after_move(api.SIDESTEP_LEFT) == api.AHEAD
  assert api.direction_after_move(api.SIDESTEP_RIGHT) == api.AHEAD
  put_spinner((5, 5), api.LEFT_SPINNER)
  assert api.direction_after_move(api.LASER) == api.LEFT
  assert api.direction_after_move(api.TURN_LEFT) == api.BEHIND

def test_bumps_into_wall():
  setup_sight()
  assert not api.bumps_into_wall(api.LASER)
  assert not api.bumps_into_wall(api.TURN_LEFT)
  assert not api.bumps_into_wall(api.TURN_RIGHT)
  assert not api.bumps_into_wall(api.U_TURN)
  assert not api.bumps_into_wall(api.REVERSE)
  assert not api.bumps_into_wall(api.FORWARD)
  assert not api.bumps_into_wall(api.FORWARD_TWO)
  assert not api.bumps_into_wall(api.SIDESTEP_LEFT)
  assert not api.bumps_into_wall(api.SIDESTEP_RIGHT)
  put_wall((5, 4), 42)
  assert not api.bumps_into_wall(api.TURN_RIGHT)
  assert api.bumps_into_wall(api.SIDESTEP_LEFT)
  assert not api.bumps_into_wall(api.SIDESTEP_RIGHT)
  put_wall((2, 5), 50)
  assert not api.bumps_into_wall(api.FORWARD)
  assert api.bumps_into_wall(api.FORWARD_TWO)

def test_falls_into_pit():
  setup_sight()
  assert not api.falls_into_pit(api.LASER)
  assert not api.falls_into_pit(api.TURN_LEFT)
  assert not api.falls_into_pit(api.TURN_RIGHT)
  assert not api.falls_into_pit(api.U_TURN)
  assert not api.falls_into_pit(api.REVERSE)
  assert not api.falls_into_pit(api.FORWARD)
  assert not api.falls_into_pit(api.FORWARD_TWO)
  assert not api.falls_into_pit(api.SIDESTEP_LEFT)
  assert not api.falls_into_pit(api.SIDESTEP_RIGHT)
  put_pit((5, 4))
  assert not api.falls_into_pit(api.TURN_RIGHT)
  assert api.falls_into_pit(api.SIDESTEP_LEFT)
  assert not api.falls_into_pit(api.SIDESTEP_RIGHT)
  put_pit((3, 5))
  assert not api.falls_into_pit(api.FORWARD)
  assert api.falls_into_pit(api.FORWARD_TWO)

def test_shooting():
  setup_sight()
  target = api.shooting()
  assert target and target[api.NAME] == 'Larry'
  assert target[api.POSITION] == (4, 5)
  target = api.shooting(api.LASER)
  assert target and target[api.NAME] == 'Larry'
  assert target[api.POSITION] == (4, 5)
  target = api.shooting(api.FORWARD)
  assert target and target[api.NAME] == 'Larry'
  assert target[api.POSITION] == (4, 5)
  target = api.shooting(api.FORWARD_TWO)
  assert target and target[api.NAME] == 'Thomas'
  assert target[api.POSITION] == (3, 10)
  target = api.shooting(api.TURN_LEFT)
  assert not target
  target = api.shooting(api.TURN_RIGHT)
  assert target and target[api.NAME] == 'Mary'
  assert target[api.POSITION] == (5, 9)
  target = api.shooting(api.U_TURN)
  assert target and target[api.NAME] == 'Larry'
  assert target[api.POSITION] == (7, 5)
  api.SIGHT[3][5].floor = api.EMPTY
  target = api.shooting(api.FORWARD_TWO)
  assert target and target[api.NAME] == 'Larry'
  assert target[api.POSITION] == (4, 5)
  put_pit((3, 5))
  target = api.shooting(api.FORWARD_TWO)
  assert not target

def test_shot_by():
  setup_sight()
  shooters = api.shot_by()
  assert len(shooters) == 1
  assert shooters[0][api.NAME] == 'Mary'
  assert shooters[0][api.POSITION] == (5, 9)
  shooters = api.shot_by(api.LASER)
  assert len(shooters) == 1
  assert shooters[0][api.NAME] == 'Mary'
  assert shooters[0][api.POSITION] == (5, 9)
  shooters = api.shot_by(api.TURN_LEFT)
  assert len(shooters) == 1
  assert shooters[0][api.NAME] == 'Mary'
  assert shooters[0][api.POSITION] == (5, 9)
  shooters = api.shot_by(api.SIDESTEP_LEFT)
  assert len(shooters) == 1
  assert shooters[0][api.NAME] == 'Mary'
  assert shooters[0][api.POSITION] == (5, 9)
  shooters = api.shot_by(api.SIDESTEP_RIGHT)
  assert len(shooters) == 2
  names = [x[api.NAME] for x in shooters]
  assert 'Mary' in names
  assert api.MOUNTED_LASER in names
  shooters = api.shot_by(api.REVERSE)
  assert len(shooters) == 0
  shooters = api.shot_by(api.FORWARD)
  assert len(shooters) == 2
  names = [x[api.NAME] for x in shooters]
  assert 'Larry' in names
  assert 'Mary' in names
  shooters = api.shot_by(api.FORWARD_TWO)
  assert len(shooters) == 1
  assert shooters[0][api.NAME] == 'Thomas'
  assert shooters[0][api.POSITION] == (3, 10)
  put_robot((3, 5), 5, api.BEHIND, 'Bill')
  shooters = api.shot_by(api.FORWARD_TWO)
  assert len(shooters) == 1
  assert shooters[0][api.NAME] == 'Thomas'
  api.SIGHT[4][5].content = None
  shooters = api.shot_by(api.FORWARD_TWO)
  assert len(shooters) == 2
  names = [x[api.NAME] for x in shooters]
  assert 'Thomas' in names
  assert 'Bill' in names
