# The text file representing the map to use. Maps will always be square.
map_file = 'roborally/maps/maze.txt'
# Whether to save a replay of the match. Replays are saved as pickle files under roborally/replays
save_replay = True
# The name of the replay. The name of the pickle file will be <replay_name>.pickle
replay_name = 'my_test'
# Whether running a simulation is interactive. Interactive simulations print out every stat encountered to the console
# and require you to press <enter> to go to the next state.
interactive = False
# Whether the results of the match should be printed to the console
print_results = False
# When debug_robots is set to True, a robot's move function that throws an exception will stop the simulation and print
# the exception to the screen. This is useful for debugging.
# When debug_robots is set to 'interactive' (with the quotes), an exception will pause the simulation and drob you to
# a pdb (python debugger) terminal. Ctrl-d to exit, and the exception will then be printed.
# When debug_robots is set to False, a robot that throws an exception will be dealt 1 damage, and will not stop the
# simulation. The official match will have debug_robots set to False.
debug_robots = False
# A list containing the robots to include in the game. Each element in the list is a tuple containing the robot's pithy
# name used in the simulation and the name of the python module.
# For example, if you wrote a robot with the file roborally/robots/my_robot.py and you want the pithy name of your
# robot in the game to be MyRobot, you would add to this list, ('MyRobot', 'my_robot')
# If this is commented out, every module in the roborally/robots directory will be used as a robot.
#robots = [('HammerBot', 'hammer_bot'), ('Beeline', 'beeline'),
#          ('ScaredyCat', 'scaredycat'), ('McShooterson', 'mcshooterson')]
