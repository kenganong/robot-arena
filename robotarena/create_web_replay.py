#!/usr/bin/env python3
import sys
import os
import pickle
from PIL import Image
import roborally.api as api

image_dir = '../images/'

with open(sys.argv[1], 'rb') as pickle_file:
  replay = pickle.load(pickle_file)
  replay_name = replay['name']
  replay_type = replay['type']
  states = replay['states']

os.makedirs('common/replay/{}'.format(replay_name), exist_ok=True)

def create_robot_image_map(state):
  return {state.brains[i].name: 'robot_{}.gif'.format(i + 1) for i in range(len(state.brains))}

def make_start_page(robot_name_to_img):
  image_dir = 'images/'
  with open('common/replay/{}.html'.format(replay_name), 'w') as file:
    print('<html><body><div style="text-align:center">', end='', file=file)
    print('<h1>Robot Arena</h1><br/><h2>{}</h2><br />'.format(replay_type), file=file)
    print('<a href="{}/iteration_0.html">Start</a><br/><br/>'.format(replay_name), end='', file=file)
    print('<table cellpadding="0" cellspacing="0" style="margin:0 auto">', file=file)
    print('<caption>Contestants</caption><tr><th>Robot</th><th>Name</th></tr>', file=file)
    for name in robot_name_to_img:
      image = image_dir + robot_name_to_img[name]
      print('<tr><td><image src="{}"></td><td>{}</td></tr>'.format(image, name), end='', file=file)
    print('</table>', file=file)
    print('</div></body></html>', file=file)

def make_end_page(final_results, robot_name_to_img):
  with open('common/replay/{}/final.html'.format(replay_name), 'w') as file:
    print('<html><body><div style="text-align:center">', end='', file=file)
    print('<h1>Final Results</h1><br/>', file=file)
    print('<table style="margin:0 auto;border: 1px solid black">', file=file)
    print('<caption>Rankings</caption><tr>', file=file)
    for title in ['Rank', 'Robot', 'Name', 'Max Flag Scored', 'Total Flags Scored', 'Iterations Survived', 'Robots Alive']:
      print('<th style="border: 1px solid black">{}</th>'.format(title), end='', file=file)
    print('</tr>', file=file)
    for brain in sorted(final_results.brains, key = lambda x: x.placement):
      image = image_dir + robot_name_to_img[brain.name]
      print('<tr>', end='', file=file)
      for item in [brain.placement, '<image src="{}"/>'.format(image), brain.name, brain.max_flag,
                   brain.total_flags, brain.iterations_survived, brain.robots_alive]:
        print('<td style="border: 1px solid black">{}</td>'.format(item), end='', file=file)
      print('</tr>', file=file)
    print('</table>', file=file)
    print('</div></body></html>', file=file)

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
    else:
      print('<div style="float:left"><a href="../{}.html">Start</a></div>'.format(replay_name), end='', file=state_file)
    if state.iteration < total_states - 1:
      print('<div style="float:right"><a href="iteration_{}.html">Next</a></div>'.format(state.iteration + 1), end='', file=state_file)
    else:
      print('<div style="float:right"><a href="final.html">Results</a></div>', end='', file=state_file)
    print('</div>', file=state_file)
    print('<div style="clear:both">', file=state_file)
    print('<h1>Iteration {}</h1>'.format(state.iteration), file=state_file)
    image_file = 'iteration_{}.gif'.format(state.iteration)
    make_iteration_image(state).save('common/replay/{}/{}'.format(replay_name, image_file))
    print('<br/><image src="{}"/>'.format(image_file), file=state_file)
    print('</div>', file=state_file)
    print_legend_and_charts(state, robot_name_to_img, state_file)
    print('</body></html>', file=state_file)

def print_legend_and_charts(state, robot_name_to_img, state_file):
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

cached_images = {}
image_rotation = {}
def cache_images(brains):
  image_dir = 'common/replay/images/'
  cached_images['pit'] = Image.open(image_dir + 'pit.gif')
  cached_images[api.WALL] = Image.open(image_dir + 'wall.gif')
  cached_images[api.CORPSE] = Image.open(image_dir + 'corpse.gif')
  cached_images[api.MOUNTED_LASER] = Image.open(image_dir + 'mounted.gif')
  cached_images[api.LEFT_SPINNER] = Image.open(image_dir + 'spinner.gif')
  cached_images[api.RIGHT_SPINNER] = cached_images[api.LEFT_SPINNER].rotate(180)
  cached_images[api.EMPTY] = Image.open(image_dir + 'floor.gif')
  for i in range(1, 9):
    cached_images[api.FLAG + str(i)] = Image.open(image_dir + api.FLAG + str(i) + '.gif')
  for i in range(len(brains)):
    cached_images[brains[i].name] = Image.open(image_dir + 'robot_{}.gif'.format(i + 1))
  image_rotation[api.AHEAD] = 0
  image_rotation[api.BEHIND] = 180
  image_rotation[api.LEFT] = 90
  image_rotation[api.RIGHT] = 270

def make_iteration_image(state):
  pixel_size = 9
  image = Image.new('RGB', (state.board.cols * pixel_size, state.board.rows * pixel_size))
  for row in range(state.board.rows):
    for col in range(state.board.cols):
      cell_image = get_cell_image(state.board.get_item((row, col)))
      image.paste(cell_image, (col * pixel_size, row * pixel_size))
  return image

def get_cell_image(cell):
  if cell.content:
    if cell.content[api.TYPE] == api.ROBOT:
      image = cached_images[cell.content['brain'].name]
    else:
      image = cached_images[cell.content[api.TYPE]]
    rotation = image_rotation[cell.content.get(api.FACING, api.AHEAD)]
    if rotation != 0:
      image = image.rotate(rotation)
  else:
    if cell.floor == None:
      image = cached_images['pit']
    else:
      image = cached_images[cell.floor]
  return image

def make_table_cell(cell, robot_name_to_img):
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

total_states = len(states)
robot_name_to_img = create_robot_image_map(states[0])
cache_images(states[0].brains)
make_start_page(robot_name_to_img)
for state in states:
  make_iteration_page(state, total_states, robot_name_to_img)
make_end_page(states[-1], robot_name_to_img)
