import random
from roborally.api import *

def move():
  my_moves = list(MOVES)
  scored_moves = {}
  for move in my_moves:
    scored_moves[move] = score(move)
  min_score = min(scored_moves.values())
  return random.choice([move for move in scored_moves if scored_moves[move] == min_score])
def score(move):
  # Score the move based on how much damage the robot will take if it makes the move
  if falls_into_pit(move):
    return 20
  else:
    move_score = len(shot_by(move))
    if move in PRIORITY_MOVES and charges() < 1:
      move_score += 1
    return move_score
