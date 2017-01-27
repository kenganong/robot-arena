import random
from roborally.api import *

def move():
  my_moves = list(MOVES)
  random.shuffle(my_moves) # This is used so we don't favor moves that appear first in MOVES
  scored_moves = {}
  for move in my_moves:
    scored_moves[move] = score(move)
  return min(scored_moves, key=scored_moves.get)
def score(move):
  # Score the move based on how much damage the robot will take if it makes the move
  if falls_into_pit(move):
    return 10
  else:
    move_score = len(shot_by(move))
    if move in PRIORITY_MOVES and charges() < 1:
      move_score += 1
    return move_score
