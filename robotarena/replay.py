import os
import pickle
import roborally.api as api

replay_name = 'my_test'

with open('roborally/replays/{}.pickle'.format(replay_name), 'rb') as pickle_file:
  states = pickle.load(pickle_file)

os.makedirs('common/replay/{}'.format(replay_name), exist_ok=True)

def create_robot_image_map(state):
  return {state.brains[i].name: 'robot_{}.gif'.format(i + 1) for i in range(len(state.brains))}

def make_start_page():
  with open('common/replay/{}.html'.format(replay_name), 'w') as file:
    print('<html><body><a href="{}/iteration_0.html">Start</a></body></html>'.format(replay_name), end='', file=file)

def make_iteration_page(state, total_states, robot_name_to_img):
  with open('common/replay/{}/iteration_{}.html'.format(replay_name, state.iteration), 'w') as state_file:
    print('<html>', file=state_file)
    print('<head>', file=state_file)
    print('<link rel="stylesheet" type="text/css" href="../roborally.css"/>', file=state_file)
    print('<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.1/jquery.min.js"></script>', file=state_file)
    print('<script src="http://code.highcharts.com/highcharts.js"></script>', file=state_file)
    print('</head>', file=state_file)
    print('<body><div style="width:100%">', end='', file=state_file)
    if state.iteration > 0:
      print('<div style="float:left"><a href="iteration_{}.html">Previous</a></div>'.format(state.iteration - 1), end='', file=state_file)
    if state.iteration < total_states - 1:
      print('<div style="float:right"><a href="iteration_{}.html">Next</a></div>'.format(state.iteration + 1), end='', file=state_file)
    print('</div>', file=state_file)
    print('<div style="clear:both">', file=state_file)
    print('<h1>Iteration {}</h1>'.format(state.iteration), file=state_file)
    print('<br/><table cellpadding="0" cellspacing="0">', file=state_file)
    for row in range(state.board.rows):
      print('<tr>', end='', file=state_file)
      for col in range(state.board.cols):
        cell = state.board.get_item((row, col))
        print(make_table_cell(cell, robot_name_to_img), end='', file=state_file)
      print('</tr>', file=state_file)
    print('</table>', file=state_file)
    print('</div>', file=state_file)
    print_legend_and_charts(state, robot_name_to_img, state_file)
    print('</body></html>', file=state_file)

def print_legend_and_charts(state, robot_name_to_img, state_file):
  image_dir = '../images/'
  print('<div style="width:100%;display:inline-block">', end='', file=state_file)
  print('<table cellpadding="0" cellspacing="0" style="height:216;float:left">', file=state_file)
  print('<caption>Legend</caption><tr><th>Robot</th><th>Name</th></tr>', file=state_file)
  for brain in state.brains:
    image = image_dir + robot_name_to_img[brain.name]
    print('<tr><td><image src="{}"></td><td>{}</td></tr>'.format(image, brain.name), end='', file=state_file)
  print('</table>', file=state_file)
  print('<div id="flags" style="width:48%;height:216;float:left"></div>', file=state_file)
  print('<div id="living" style="width:48%;height:216;float:left"></div>', file=state_file)
  print('<div id="death" style="width:48%;height:216;float:left"></div>', file=state_file)
  print(make_flags_chart(state), file=state_file)
  print(make_living_chart(state), file=state_file)
  print(make_death_chart(state), file=state_file)
  print('</div>', file=state_file)

def make_flags_chart(state):
  title = 'Flags Scored'
  names = [brain.name for brain in state.brains]
  data = [str(brain.total_flags) for brain in state.brains]
  name_str = '\'' + '\', \''.join(names) + '\''
  data_str = ', '.join(data)
  return ('<script>$(function () {\nvar myChart = Highcharts.chart(\'flags\', { chart: { type: \'column\' },\n' +
          'title: { text: \'' + title + '\' }, xAxis: { categories: [' + name_str + '] },\n' +
          'yAxis: { title: { text: \'' + title + '\' } },\n' +
          'legend: { enabled: false },\n' +
          'series: [{ name: \'robots\', data: [' + data_str + '] }]\n' +
          '}); });</script>')

def make_living_chart(state):
  title = 'Surviving'
  names = [brain.name for brain in state.brains]
  data = [str(brain.robots_alive) for brain in state.brains]
  name_str = '\'' + '\', \''.join(names) + '\''
  data_str = ', '.join(data)
  return ('<script>$(function () {\nvar myChart = Highcharts.chart(\'living\', { chart: { type: \'column\' },\n' +
          'title: { text: \'' + title + '\' }, xAxis: { categories: [' + name_str + '] },\n' +
          'yAxis: { title: { text: \'' + title + '\' } },\n' +
          'legend: { enabled: false },\n' +
          'series: [{ name: \'robots\', data: [' + data_str + '] }]\n' +
          '}); });</script>')

def make_death_chart(state):
  title = 'Deaths'
  death_types = []
  for brain in state.brains:
    for key in brain.death_reason:
      if key not in death_types:
        death_types.append(key)
  if not death_types:
    return ''
  death_types.sort()
  type_str = '\'' + '\', \''.join(death_types) + '\''
  names = [brain.name for brain in state.brains]
  retval = ('<script>$(function () {\nvar myChart = Highcharts.chart(\'death\', { chart: { type: \'column\' },\n' +
          'title: { text: \'' + title + '\' }, xAxis: { categories: [' + type_str + '] },\n' +
          'yAxis: { title: { text: \'' + title + '\' } },\n' +
          'legend: { enabled: false },\n' +
          'series: [')
  brains_data = []
  for brain in state.brains:
    data = [str(brain.death_reason.get(method, 0)) for method in death_types]
    data_str = ', '.join(data)
    brain_str = '{ name: \'' + brain.name + '\', data: [' + data_str + '] }'
    brains_data.append(brain_str)
  retval += ', '.join(brains_data)
  retval += ']\n}); });</script>'
  return retval

def make_table_cell(cell, robot_name_to_img):
  image_dir = '../images/'
  style = None
  style_map = {api.AHEAD: None, api.RIGHT: 'rotateimg90', api.BEHIND: 'rotateimg180', api.LEFT: 'rotateimg270'}
  if cell.content:
    if cell.content[api.TYPE] == api.WALL:
      image = 'wall.gif'
    elif cell.content[api.TYPE] == api.CORPSE:
      image = 'corpse.gif'
    elif cell.content[api.TYPE] == api.MOUNTED_LASER:
      image = 'mounted.gif'
      style = style_map[cell.content[api.FACING]]
    elif cell.content[api.TYPE] == api.ROBOT:
      image = robot_name_to_img[cell.content['brain'].name]
      style = style_map[cell.content[api.FACING]]
  else:
    if cell.floor == None:
      image = 'pit.gif'
    elif cell.floor == api.LEFT_SPINNER:
      image = 'spinner.gif'
    elif cell.floor == api.RIGHT_SPINNER:
      image = 'spinner.gif'
      style = 'fliphorizontal'
    elif cell.floor.startswith(api.FLAG):
      image = cell.floor + '.gif'
    else:
      image = 'floor.gif'
  if style:
    return '<td><image src="{}" class="{}"></td>'.format(image_dir + image, style)
  else:
    return '<td><image src="{}"></td>'.format(image_dir + image)

make_start_page()
total_states = len(states)
robot_name_to_img = create_robot_image_map(states[0])
for state in states:
  make_iteration_page(state, total_states, robot_name_to_img)
