"""
murder_if_convenient's first priority is to murder other robots, but only
if they happen to be right in the way. Otherwise he'll head for the flag
as best as possible, attempting to follow an obsticle if one is in the way.
"""
from roborally.api import *

name = 'ConvenientMurderer'

friendly_bots = ('ConvenientMurderer', 'ConvenientMurderer2')
surroundings = {}

def is_friendly(content):
    return content and content[TYPE] == ROBOT and content[NAME] in friendly_bots

def is_enemy(content):
    return content and content[TYPE] == ROBOT and content[NAME] not in friendly_bots

def contains_enemy(cell):
    return is_enemy(cell.content)

def is_corpse(content):
    return content and content[TYPE] == CORPSE

def is_pit(cell):
    return not cell.floor

def is_obstacle(cell):
    return is_pit(cell) or cell.content and cell.content[TYPE] in (WALL, MOUNTED_LASER)

def is_spinner(cell):
    return cell.floor in (LEFT_SPINNER, RIGHT_SPINNER)

def am_on_flag():
    cell = get_cell_in_sight(me)
    return cell.floor == FLAG

def turn(direction):
    mem = memory()['flag_directions']
    new_mem = set()

    for remembered_dir in mem:
        new_mem.add(convert_direction(direction, remembered_dir))
    memory()['flag_directions'] = new_mem

    if direction == LEFT:
        return TURN_LEFT
    if direction == RIGHT:
        return TURN_RIGHT
    return U_TURN

def sidestep(direction):
    if 'follow_obstacle' in memory():
        if memory()['follow_obstacle'] == direction:
            memory()['distance_from_obstacle'] += 1
        else:
            memory()['distance_from_obstacle'] -= 1

    if direction == LEFT:
        return SIDESTEP_LEFT
    return SIDESTEP_RIGHT

def follow_obstacle(direction):
    opposite = opposite_direction(direction)
    cell = get_cell_in_sight(get_pos_in_direction(me, opposite, distance=memory()['distance_from_obstacle']))
    if not cell or not is_obstacle(cell):
        # we reached the end, turn that way and stop following
        memory()['follow_obstacle'] = False
        return turn(opposite)
    if is_obstacle(surroundings['forward1']):
        return turn(direction)
    return FORWARD


def go_towards_flag(good_options):
    direction = good_options[0]
    if AHEAD in good_options:
        if not is_obstacle(surroundings['forward1']):
            return FORWARD

        if len(good_options) == 1:
            good_options = memory()['flag_directions']

        direction_decided = False
        if len(good_options) > 1:
            other = list(set(good_options) - set([AHEAD]))[0]
            if not is_obstacle(get_cell_in_sight(get_pos_in_direction(me, other))):
                memory()['follow_obstacle'] = other
                direction_decided = True

        if not direction_decided:
            if is_obstacle(surroundings['right1']):
                memory()['follow_obstacle'] = LEFT
            else:
                memory()['follow_obstacle'] = RIGHT

        memory()['distance_from_obstacle'] = 1
        return turn(memory()['follow_obstacle'])

    return turn(direction)


def move():
    """
    if we can shove an enemy in a pit, do it!
    if enemy robot is straight ahead, blast him!
    if going around obstacle, follow it
    else go towards flag
     - don't fall into holes
     - go towards flag
    """
    # setup variables
    global surroundings, me
    me = (5,5)
    surroundings['forward1'] = get_cell_in_sight(get_pos_in_direction(me, AHEAD))
    surroundings['forward2'] = get_cell_in_sight(get_pos_in_direction(me, AHEAD, distance=2))
    surroundings['forward3'] = get_cell_in_sight(get_pos_in_direction(me, AHEAD, distance=3))
    surroundings['back1'] = get_cell_in_sight(get_pos_in_direction(me, BEHIND))
    surroundings['back2'] = get_cell_in_sight(get_pos_in_direction(me, BEHIND, distance=2))
    surroundings['left1'] = get_cell_in_sight(get_pos_in_direction(me, LEFT))
    surroundings['left2'] = get_cell_in_sight(get_pos_in_direction(me, LEFT, distance=2))
    surroundings['right1'] = get_cell_in_sight(get_pos_in_direction(me, RIGHT))
    surroundings['right2'] = get_cell_in_sight(get_pos_in_direction(me, RIGHT, distance=2))

    # remember the last two directions that we sensed the flag in
    flag_direction = sense_flag()
    if not 'flag_directions' in memory() or len(flag_direction) == 2:
        memory()['flag_directions'] = set(flag_direction)

    # remember what turn it is
    if not 'turn' in memory():
        memory()['turn'] = 1
    else:
        memory()['turn'] += 1

    # remember how many turns in a row we get shot
    health = life()
    if 'life_last_turn' not in memory():
        memory()['life_last_turn'] = 10
    else:
        memory()['life_last_turn'] = memory()['life_this_turn']
    memory()['life_this_turn'] = health
    if memory()['life_last_turn'] > health:
        if not 'turns_getting_shot' in memory():
            memory()['turns_getting_shot'] = 1
        else:
            memory()['turns_getting_shot'] += 1
    else:
        if 'turns_getting_shot' in memory():
            del memory()['turns_getting_shot']

    # if we can shove an enemy in a pit, do it!
    if contains_enemy(surroundings['forward1']) and is_pit(surroundings['forward2']):
        return FORWARD
    
    if (contains_enemy(surroundings['forward1']) or contains_enemy(surroundings['forward2'])) and is_pit(surroundings['forward3']):
        return FORWARD_TWO

    if contains_enemy(surroundings['back1']) and is_pit(surroundings['back2']):
        return REVERSE

    if contains_enemy(surroundings['left1']) and is_pit(surroundings['left2']):
        return sidestep(LEFT)

    if contains_enemy(surroundings['right1']) and is_pit(surroundings['right2']):
        return sidestep(RIGHT)

    # if enemy is straight ahead, blast him!
    target = shooting()
    if is_enemy(target) or is_corpse(target):
        return LASER

    # if i'm shooting friendly, try to sidestep.
    if is_friendly(shooting()) and not is_obstacle(surroundings['right1']):
        friendly = shooting()
        if not friendly[FACING] == RIGHT and not is_obstacle(surroundings['right1']):
            return sidestep(RIGHT)
        #if not friendly[FACING] == LEFT and not is_obstacle(surroundings['left1']):
        #    return SIDESTEP_LEFT

    # if it's after the initial fray and i've been shot three turns in a row,
    # someone's probably following me. try to dodge.
    if memory()['turn'] > 20 and 'turns_getting_shot' in memory() and memory()['turns_getting_shot'] > 2:
        if not is_obstacle(surroundings['left1']):
            del memory()['turns_getting_shot']
            return sidestep(LEFT)
        if not is_obstacle(surroundings['right1']):
            del memory()['turns_getting_shot']
            return sidestep(RIGHT)

    # if going around obstacle, follow it
    if 'follow_obstacle' in memory():
        if not memory()['follow_obstacle']:
            # we are in the process of not following the obstacle any more.
            # go forward the appropriate number of times.
            if memory()['distance_from_obstacle'] <= 1:
                del memory()['follow_obstacle']
                del memory()['distance_from_obstacle']
            else:
                memory()['distance_from_obstacle'] -= 1
            return FORWARD
        return follow_obstacle(memory()['follow_obstacle'])

    # if i'm on a spinner, get off the dang thing
    if is_spinner(get_cell_in_sight(me)):
        return FORWARD

    # else go towards flag
    return go_towards_flag(flag_direction)
