import random
from roborally.api import *

name = 'Cautious'

def move():
  my_moves = list(MOVES)
  # Score the moves based on damage received
  scored_moves = {}
  for move in my_moves:
    scored_moves[move] = score(move)
  my_moves = get_best(scored_moves)
  if len(my_moves) == 1:
    return my_moves[0]
  # Score the moves based on moving away from danger
  scored_moves = {}
  for move in my_moves:
    scored_moves[move] = away_from_danger_toward_flag(move)
  my_moves = get_best(scored_moves)
  return random.choice(my_moves)
def get_best(scored_moves):
  best_score = max(scored_moves.values())
  return [key for key in scored_moves if scored_moves[key] == best_score]
def score(move):
  if falls_into_pit(move):
    return -10
  move_score = 0
  if move in PRIORITY_MOVES and charges() < 1:
    move_score -= 2
  for shooter in shot_by(move):
    if shooter[TYPE] == MOUNTED_LASER:
      move_score -= 2
    else:
      move_score -= 1
  target = shooting(move)
  if target:
    if target[NAME] == myself()[NAME]:
      move_score -= 1
      if move == LASER:
        move_score -= 2
    elif target[TYPE] == ROBOT:
      if move == LASER:
        move_score += 1
  if move in PROGRESS_MOVES:
    direction = direction_of_move(move)
    pos = get_pos_in_direction(myself()[POSITION], direction)
    cell = get_cell_in_sight(pos)
    pos_past = get_pos_in_direction(position_after_move(move), direction)
    cell_past = get_cell_in_sight(pos_past)
    if cell_past.floor == PIT and cell.content and cell.content[TYPE] == ROBOT:
      if cell.content[NAME] == myself()[NAME]:
        move_score -= 10
      else:
        move_score += 4
  return move_score
def away_from_danger_toward_flag(move):
  pos = position_after_move(move)
  score = 0
  for row in sight():
    for cell in row:
      if cell and cell.content:
        if cell.content[TYPE] == ROBOT and cell.content[NAME] != myself()[NAME]:
          score += distance_between(pos, cell.content[POSITION]) - 20
        elif cell.content[TYPE] in [MOUNTED_LASER, CORPSE]:
          score += distance_between(pos, cell.content[POSITION]) - 7
  if move not in PRIORITY_MOVES:
    score += 1
  moves_toward_flag = moves_in_directions(sense_flag())
  if move in moves_toward_flag and not bumps_into_wall(move):
    score += 4
  return score
