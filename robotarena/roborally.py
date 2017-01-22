import roborally.manager as manager

state = manager.create_start_state()
while not manager.end_state(state):
  print(state)
  input()
  manager.next_iteration(state)
print(state)
