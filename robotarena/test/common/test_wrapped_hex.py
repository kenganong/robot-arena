import pytest
import common.model.board as board_api

@pytest.fixture
def board():
  return board_api.init_board((8, 8), ' ', cell_shape=board_api.HEX, wrap=board_api.ALL)

# · · · · · · · ·
#  · · A · · D · ·
# · · · · · · · ·
#  · · · A · · · ·
# · · · E · · C ·
#  · B · · · · · ·
# · · · · · · · ·
#  · · · · · · F ·
@pytest.fixture
def board_a():
  my_board = board()
  my_board.put_item((1, 2), 'A')
  my_board.put_item((3, 3), 'A')
  my_board.put_item((5, 1), 'B')
  my_board.put_item((4, 6), 'C')
  my_board.put_item((1, 5), 'D')
  my_board.put_item((4, 3), 'E')
  my_board.put_item((7, 6), 'F')
  return my_board

def test_empty_surroundings(board):
  surroundings = board.get_surroundings((2, 2), 2)
  assert len(surroundings) == 5
  for row in range(5):
    assert len(surroundings[row]) == 5 - abs(2 - row)
    for cell in surroundings[row]:
      assert cell == ' '

def test_empty_surroundings_near_edge(board):
  surroundings = board.get_surroundings((0, 1), 2)
  assert len(surroundings) == 5
  for row in range(5):
    assert len(surroundings[row]) == 5 - abs(2 - row)
    for cell in surroundings[row]:
      assert cell == ' '

def test_simple_surroundings(board_a):
  surroundings = board_a.get_surroundings((4, 3), 2)
  assert len(surroundings) == 5
  for row in range(5):
    row_length = 5 - abs(2 - row)
    assert len(surroundings[row]) == row_length
    for col in range(row_length):
      item = surroundings[row][col]
      if row == 1 and col == 2:
        assert item == 'A'
      elif row == 2 and col == 2:
        assert item == 'E'
      elif row == 3 and col == 0:
        assert item == 'B'
      else:
        assert item == ' '

def test_immediate_surroundings(board_a):
  surroundings = board_a.get_surroundings((4, 3), 1)
  assert len(surroundings) == 3
  for row in range(3):
    row_length = 3 - abs(1 - row)
    assert len(surroundings[row]) == row_length
    for col in range(row_length):
      item = surroundings[row][col]
      if row == 0 and col == 1:
        assert item == 'A'
      elif row == 1 and col == 1:
        assert item == 'E'
      else:
        assert item == ' '

def test_blind_surroundings(board_a):
  surroundings = board_a.get_surroundings((4, 3), 0)
  assert len(surroundings) == 1
  assert len(surroundings[0]) == 1
  assert surroundings[0][0] == 'E'

def test_edge_surroundings(board_a):
  surroundings = board_a.get_surroundings((7, 6), 2)
  assert len(surroundings) == 5
  for row in range(5):
    row_length = 5 - abs(2 - row)
    assert len(surroundings[row]) == row_length
    for col in range(row_length):
      item = surroundings[row][col]
      if row == 2 and col == 2:
        assert item == 'F'
      elif row == 4 and col == 0:
        assert item == 'D'
      else:
        assert item == ' '
