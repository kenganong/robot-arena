import itertools

RECTANGLE = 0
SQUARE = 1
HEX = 2

NONE = 0
ALL = 1

def init_board(size, fill=' ', shape=RECTANGLE, cell_shape=SQUARE, wrap=NONE):
  if shape == RECTANGLE and cell_shape == SQUARE:
    return RectangleSquareBoard(size, fill, wrap)
  elif shape == RECTANGLE and cell_shape == HEX:
    return ToroidalHexBoard(size, fill, wrap)

class RectangleBoard:
  def __init__(self, size, fill, wrap):
    self.rows = size[0]
    self.cols = size[1]
    self.empty = fill
    self.wrap = wrap
    self.clear()
  def clear(self):
    self.clear_fill(self.empty)
  def clear_fill(self, fill):
    self.contents = [[(fill() if callable(fill) else fill) for j in range(self.cols)] for i in range(self.rows)]
  def get_item(self, pos):
    if self.off_board(pos):
      if self.wrap == NONE:
        return None
      else:
        pos = self.wrap_pos(pos)
    return self.contents[pos[0]][pos[1]]
  def take_item(self, pos):
    fill_item = self.empty() if callable(self.empty) else self.empty
    return exchange_item(pos, fill_item)
  def exchange_item(self, pos, exchange):
    if self.off_board(pos):
      if self.wrap == NONE:
        return None
      else:
        pos = self.wrap_pos(pos)
    item = self.contents[pos[0]][pos[1]]
    self.contents[pos[0]][pos[1]] = exchange
    return item
  def put_item(self, pos, item):
    if self.off_board(pos):
      if self.wrap == NONE:
        raise IndexError('Position out-of-bounds')
      else:
        pos = self.wrap_pos(pos)
    self.contents[pos[0]][pos[1]] = item
  def off_board(self, pos):
    return pos[0] < 0 or pos[0] >= self.rows or pos[1] < 0 or pos[1] >= self.cols
  def wrap_pos(self, pos):
    row, col = pos
    if pos[0] >= self.rows:
      row -= self.rows
    if pos[1] >= self.cols:
      col -= self.cols
    return row, col
  def traverse(self):
    return ((self.contents[pos[0]][pos[1]], pos) for pos in itertools.product(range(self.rows), range(self.cols)))

class RectangleSquareBoard(RectangleBoard):
  def get_surroundings(self, pos, distance):
    # TODO: read wrap
    if self.off_board(pos):
      raise IndexError('Position out-of-bounds')
    surroundings = []
    for row in range(pos[0] - distance, pos[0] + distance + 1):
      row_content = []
      for col in range(pos[1] - distance, pos[1] + distance + 1):
        row_content.append(self.get_item((row, col)))
      surroundings.append(row_content)
    return surroundings

class ToroidalHexBoard(RectangleBoard):
  def get_surroundings(self, pos, distance):
    surroundings = []
    for row in range(pos[0] - distance, pos[0] + distance + 1):
      current_row = []
      rows_away = abs(pos[0] - row)
      offset = pos[0] % 2
      start_col = pos[1] - (distance - ((rows_away + offset) // 2))
      num_cols = distance * 2 + 1 - rows_away
      for col in range(start_col, start_col + num_cols):
        current_row.append(self.get_item((row, col)))
      surroundings.append(current_row)
    return surroundings
