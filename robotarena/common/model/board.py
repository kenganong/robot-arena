RECTANGLE = 0
SQUARE = 1

def init_board(size, fill=' ', shape=RECTANGLE, cell_shape=SQUARE, infinite=False):
  if shape == RECTANGLE and cell_shape == SQUARE and not infinite:
    return RectangleSquareBoard(size, fill)

class RectangleSquareBoard:
  def __init__(self, size, fill):
    self.rows = size[0]
    self.cols = size[1]
    self.empty = fill
    self.clear()
  def clear(self):
    self.clear_fill(self.empty)
  def clear_fill(self, fill):
    self.contents = []
    for row in range(self.rows):
      row_content = []
      for col in range(self.cols):
        fill_item = fill() if callable(fill) else fill
        row_content.append(fill_item)
      self.contents.append(row_content)
  def get_item(self, pos):
    if self.off_board(pos):
      return None
    return self.contents[pos[0]][pos[1]]
  def take_item(self, pos):
    fill_item = self.empty() if callable(self.empty) else self.empty
    return exchange_item(pos, fill_item)
  def exchange_item(self, pos, exchange):
    if self.off_board(pos):
      return None
    item = self.contents[pos[0]][pos[1]]
    self.contents[pos[0]][pos[1]] = exchange
    return item
  def put_item(self, pos, item):
    if self.off_board(pos):
      raise IndexError('Position out-of-bounds')
    self.contents[pos[0]][pos[1]] = item
  def off_board(self, pos):
    return pos[0] < 0 or pos[0] >= self.rows or pos[1] < 0 or pos[1] >= self.cols
  def traverse(self):
    return ((self.contents[row][col], (row, col)) for col in range(self.cols) for row in range(self.rows))
  def get_surroundings(self, pos, distance):
    if self.off_board(pos):
      raise IndexError('Position out-of-bounds')
    surroundings = []
    for row in range(pos[0] - distance, pos[0] + distance + 1):
      row_content = []
      for col in range(pos[1] - distance, pos[1] + distance + 1):
        row_content.append(self.get_item((row, col)))
      surroundings.append(row_content)
    return surroundings
