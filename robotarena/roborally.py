import roborally.manager as manager

state = manager.create_start_state()
while True: # TODO: while not end_state
  print(state)
  input()
  manager.next_iteration(state)
print(state)
