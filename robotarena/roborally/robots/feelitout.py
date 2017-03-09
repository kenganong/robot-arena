import random
from roborally.api import *

name = 'FeelItOut'

AVOIDING_PIT = 1

PIT_WEIGHT_ONE = 1000
PIT_WEIGHT_TWO = 20
PIT_WEIGHT_THREE = 2
PIT_WEIGHT_FOUR = 1
PIT_WEIGHT_FIVE = 1

FLAG_WEIGHT = 505


AVOID_PIT_OFFSET_WEIGHT = 100

def move():
  my_memory = memory()
  my_memory['left'] = 0
  my_memory['right'] = 0
  my_memory['ahead'] = 1
  my_memory['behind'] = 0
  my_memory['state'] = 0
  if 'my_life' not in my_memory:
    my_memory['my_life'] = myself()['life']
  if 'prev_life' not in my_memory:
    my_memory['prev_life'] = myself()['life']
  if 'two_prev_life' not in my_memory:
    my_memory['two_prev_life'] = myself()['life']
    
  #set up my current and previous life
  my_memory['two_prev_life'] = my_memory['prev_life']
  my_memory['prev_life'] = my_memory['my_life']
  my_memory['my_life'] = myself()['life']

  my_sight = sight()

  #Let's see what's around me
  center = len(my_sight) // 2
  start_pos = (center,center)
  
  
  my_sight = sight()
  for row in range(len(my_sight)):
    for col in range(len(my_sight[row])):
      end_pos = (row, col)
      thinkaboutit(start_pos, end_pos)
      
  # special handling for corpses piled up, this goes around them unless the flag is in line with the piled up corpses
  stack_of_corpses()

  feelforflag()

  #if you're on a wall, deprioritize turning, so that you won't do a bunch of back and forth garbage
  if my_memory['state'] == AVOIDING_PIT:
    my_memory['ahead'] += 1
    my_memory['behind'] -= (2 * AVOID_PIT_OFFSET_WEIGHT)
    my_memory['left'] -= AVOID_PIT_OFFSET_WEIGHT
    my_memory['right'] -= AVOID_PIT_OFFSET_WEIGHT

  return bestfeeling()

def feelforflag():

  my_memory = memory()
  #find which direction the flag is, and weight it
  if AHEAD in sense_flag():
    my_memory['ahead'] += FLAG_WEIGHT
  elif LEFT in sense_flag():
    my_memory['left'] += FLAG_WEIGHT
  elif RIGHT in sense_flag():
    my_memory['right'] += FLAG_WEIGHT
  elif BEHIND in sense_flag():
    my_memory['behind'] += FLAG_WEIGHT

  return
  
  
def stack_of_corpses():

  my_own_self = myself()
  my_memory = memory()
  
  one = get_cell_in_sight((get_pos_in_direction(my_own_self[POSITION], AHEAD, 1)[0], get_pos_in_direction(my_own_self[POSITION], AHEAD, 1)[1]))
  two = get_cell_in_sight((get_pos_in_direction(my_own_self[POSITION], AHEAD, 2)[0], get_pos_in_direction(my_own_self[POSITION], AHEAD, 2)[1]))
  three = get_cell_in_sight((get_pos_in_direction(my_own_self[POSITION], AHEAD, 3)[0], get_pos_in_direction(my_own_self[POSITION], AHEAD, 3)[1]))
  four = get_cell_in_sight((get_pos_in_direction(my_own_self[POSITION], AHEAD, 4)[0], get_pos_in_direction(my_own_self[POSITION], AHEAD, 4)[1]))
  
  # if there's a destroyed robot in front of you and a wall just past that, reconsider
  if one.content and two.content and one.content[TYPE] == CORPSE and two.content[TYPE] in [WALL, MOUNTED_LASER]:
    my_memory['state'] = AVOIDING_PIT
    my_memory['ahead'] -= PIT_WEIGHT_ONE
  
  
  # if there's 2 destroyed robots in front of you and a wall just past that, reconsider
  #I don't know the correct python syntax for doing this more elegantly than just a bunch of if statements
  if one.content and two.content and three.content and one.content[TYPE] == CORPSE and two.content[TYPE] == CORPSE and three.content[TYPE] in [WALL, MOUNTED_LASER]:
    my_memory['state'] = AVOIDING_PIT
    my_memory['ahead'] -= PIT_WEIGHT_ONE
  
  
  
  if one.content and two.content and three.content and four.content and one.content[TYPE] == CORPSE and two.content[TYPE] == CORPSE and three.content[TYPE] == CORPSE and four.content[TYPE] in [WALL, MOUNTED_LASER]:
    my_memory['state'] = AVOIDING_PIT
    my_memory['ahead'] -= PIT_WEIGHT_ONE
  
  return
    
  
  
def thinkaboutit(start_pos, end_pos):

  my_memory = memory()
  my_cell = get_cell_in_sight(start_pos)
  target_cell = get_cell_in_sight(end_pos)
  direction = direction_toward(start_pos,end_pos)
  distance = distance_between(end_pos)
  

  weight = 0
  # weight all ares based on pits and walls
  #the weight for 4 and 5 is 0, because it was feeling too much, causing it to make wrong decisions like turning the wrong way. I'd need to limit where it can feel (like only feel in front of you), to take advantage of this for navigation.
  if target_cell.content and target_cell.content[TYPE] in [WALL,MOUNTED_LASER]:
    if distance <= 1:
      my_memory['state'] = AVOIDING_PIT
      weight -= PIT_WEIGHT_ONE
    elif distance < 2:
      my_memory['state'] = AVOIDING_PIT
      weight -= PIT_WEIGHT_TWO
    elif distance < 3:
      #my_memory['state'] = AVOIDING_PIT
      weight -= PIT_WEIGHT_THREE
    elif distance < 4 and AHEAD in direction:
      weight -= PIT_WEIGHT_FOUR
    elif AHEAD in direction:
      weight -= PIT_WEIGHT_FIVE
      
  if target_cell.floor == PIT:
    if distance <= 1:
      weight -= PIT_WEIGHT_ONE
      my_memory['state'] = AVOIDING_PIT
    elif distance <= 2:
      weight -= PIT_WEIGHT_TWO
      my_memory['state'] = AVOIDING_PIT
    elif distance <= 3:
      weight -= PIT_WEIGHT_THREE
      #my_memory['state'] = AVOIDING_PIT
    elif distance <= 4 and AHEAD in direction:
      weight -= PIT_WEIGHT_FOUR
    elif AHEAD in direction:
      weight -= PIT_WEIGHT_FIVE





  if AHEAD in direction:
    my_memory['ahead'] += weight
  if LEFT in direction:
    my_memory['left'] += weight
  if RIGHT in direction:
    my_memory['right'] += weight
  if BEHIND in direction:
    my_memory['behind'] += weight





  return
 
    
def bestfeeling():

  my_memory = memory()
  
  #find the direction with the best value
  highest_direction = 'ahead'
  highest_value = my_memory['ahead']
  
  if my_memory['left'] > highest_value:
    highest_value = my_memory['left']
    highest_direction = 'left'
    
    
  if my_memory['right'] > highest_value:
    highest_value = my_memory['right']
    highest_direction = 'right'
    
    
  if my_memory['behind'] > highest_value:
    highest_value = my_memory['behind']
    highest_direction = 'behind'
    
    
  if highest_direction == 'ahead':
    return considermovingforward()
    
    #if you want to turn, but you're on a spinner, just slide off
  elif highest_direction == 'left':
    if get_cell_in_sight((len(sight()) // 2,len(sight()) // 2)).floor == LEFT_SPINNER and charges() > 0:
      return SIDESTEP_LEFT
    if get_cell_in_sight((len(sight()) // 2,len(sight()) // 2)).floor == RIGHT_SPINNER and charges() > 0:
      return SIDESTEP_LEFT
    return TURN_LEFT
  elif highest_direction == 'right':
    if get_cell_in_sight((len(sight()) // 2,len(sight()) // 2)).floor == RIGHT_SPINNER and charges() > 0:
      return SIDESTEP_RIGHT
    if get_cell_in_sight((len(sight()) // 2,len(sight()) // 2)).floor == LEFT_SPINNER and charges() > 0:
      return SIDESTEP_RIGHT
    return TURN_RIGHT
  elif highest_direction == 'behind':
    if get_cell_in_sight((len(sight()) // 2,len(sight()) // 2)).floor == RIGHT_SPINNER:
      return REVERSE
    if get_cell_in_sight((len(sight()) // 2,len(sight()) // 2)).floor == LEFT_SPINNER:
      return REVERSE
    return U_TURN
    
  return FORWARD
  
  
def considermovingforward():

  my_own_self = myself()
  shooting_target = shooting()


# if there's a spinner in front of me and it won't kill me to move past it, just move two spaces to avoid that crap
  if get_cell_in_sight(get_pos_in_direction((len(sight()) // 2,len(sight()) // 2) , AHEAD)).floor == LEFT_SPINNER:
    if not falls_into_pit(FORWARD_TWO) and not bumps_into_wall(FORWARD_TWO) and charges() > 0:
      return FORWARD_TWO
  if get_cell_in_sight(get_pos_in_direction((len(sight()) // 2,len(sight()) // 2) , AHEAD)).floor == RIGHT_SPINNER:
    if not falls_into_pit(FORWARD_TWO) and not bumps_into_wall(FORWARD_TWO) and charges() > 0:
      return FORWARD_TWO
      
  #if i'm shooting another of my robots and we're either going the same direction or going head to head, let's sidestep that, as long at it won't kill me
  if shooting_target and shooting_target[TYPE] == ROBOT and shooting_target[NAME] == my_own_self[NAME] and my_own_self[FACING] == shooting_target[FACING]:
    my_choice = random.choice([SIDESTEP_LEFT, SIDESTEP_RIGHT])
    if not falls_into_pit(my_choice) and not bumps_into_wall(my_choice) and charges() > 0:
      return my_choice
    if not falls_into_pit(SIDESTEP_LEFT) and not bumps_into_wall(SIDESTEP_LEFT) and charges() > 0:
      return SIDESTEP_LEFT
    if not falls_into_pit(SIDESTEP_RIGHT) and not bumps_into_wall(SIDESTEP_RIGHT) and charges() > 0:
      return SIDESTEP_RIGHT
  
  if shooting_target and shooting_target[TYPE] == ROBOT and shooting_target[NAME] == my_own_self[NAME] and my_own_self[FACING] == opposite_direction(shooting_target[FACING]):
    if not falls_into_pit(SIDESTEP_LEFT) and not bumps_into_wall(SIDESTEP_LEFT) and charges() > 0:
      return SIDESTEP_LEFT
    #doing it both ways makes it so that two guys facing each other along a wall will keep facing each other, and does not really impact other scenarios, so only try one way

  
  # if there's a wall mounted laser in front of or behind me, consider sidestepping
  shot_me = shot_by()
  for hitter in shot_me:
    if hitter[TYPE] == MOUNTED_LASER and hitter[FACING] == my_own_self[FACING] and charges() > 0 and not falls_into_pit(SIDESTEP_LEFT) and not bumps_into_wall(SIDESTEP_LEFT):
      return SIDESTEP_LEFT
    if hitter[TYPE] == MOUNTED_LASER and hitter[FACING] == my_own_self[FACING] and charges() > 0 and not falls_into_pit(SIDESTEP_RIGHT) and not bumps_into_wall(SIDESTEP_RIGHT):
      return SIDESTEP_RIGHT
    if hitter[TYPE] == MOUNTED_LASER and hitter[FACING] == opposite_direction(my_own_self[FACING]) and charges() > 0 and not falls_into_pit(SIDESTEP_LEFT) and not bumps_into_wall(SIDESTEP_LEFT):
      return SIDESTEP_LEFT
    if hitter[TYPE] == MOUNTED_LASER and hitter[FACING] == opposite_direction(my_own_self[FACING]) and charges() > 0 and not falls_into_pit(SIDESTEP_RIGHT) and not bumps_into_wall(SIDESTEP_RIGHT):
      return SIDESTEP_RIGHT
      
    # if there's a bad guy who is not one of me behind me shooting me, let's shake him (if he's one of me, he will move himself)
    if hitter[TYPE] == ROBOT and hitter[FACING] == my_own_self[FACING] and charges() > 0 and not falls_into_pit(SIDESTEP_RIGHT) and not bumps_into_wall(SIDESTEP_RIGHT) and not hitter[NAME] == my_own_self[NAME]:
      return SIDESTEP_RIGHT
    if hitter[TYPE] == ROBOT and hitter[FACING] == my_own_self[FACING] and charges() > 0 and not falls_into_pit(SIDESTEP_LEFT) and not bumps_into_wall(SIDESTEP_LEFT) and not hitter[NAME] == my_own_self[NAME]:
      return SIDESTEP_LEFT
      
  # if there is a bad guy in front of me (not named me) and he's looking at me, let's rock his face off.
  if shooting_target and shooting_target[TYPE] == ROBOT and not shooting_target[NAME] == my_own_self[NAME] and my_own_self[FACING] == opposite_direction(shooting_target[FACING]):
    return LASER
  
  #if i've been shot twice in a row, there's a chance i'll dodge. i give it one for free, since my own type will move out of the way after one shot
  my_memory = memory()
  if my_memory['two_prev_life'] > (my_memory['my_life'] + 1) and charges() > 0:
    my_dodge_choice = random.choice([FORWARD, SIDESTEP_LEFT, SIDESTEP_RIGHT, FORWARD, FORWARD, FORWARD, FORWARD])
    if not falls_into_pit(my_dodge_choice) and not bumps_into_wall(my_dodge_choice):
      return my_dodge_choice
  
  return FORWARD

