import json
import os
import copy
import random
import bottle

from api import ping_response, start_response, move_response, end_response

@bottle.route('/')
def index():
    return '''
    Battlesnake documentation can be found at
       <a href="https://docs.battlesnake.io">https://docs.battlesnake.io</a>.
    '''

@bottle.route('/static/<path:path>')
def static(path):
    """
    Given a path, return the static file located relative
    to the static folder.

    This can be used to return the snake head URL in an API response.
    """
    return bottle.static_file(path, root='static/')

@bottle.post('/ping')
def ping():
    """
    A keep-alive endpoint used to prevent cloud application platforms,
    such as Heroku, from sleeping the application instance.
    """
    return ping_response()


BOARD_KEY = "board"
YOU_KEY = "you"
SNAKES_KEY = "snakes"
BODY_KEY = "body"
FOOD_KEY = "food"
HEIGHT_KEY = "height"
WIDTH_KEY = "width"



@bottle.post('/start')
def start():
    data = bottle.request.json

    """
    TODO: If you intend to have a stateful snake AI,
            initialize your snake state here using the
            request's data if necessary.
    """
    print(json.dumps(data))

    BOARD_HEIGHT = data[BOARD_KEY][HEIGHT_KEY]
    BOARD_WIDTH = data[BOARD_KEY][WIDTH_KEY]
    print(BOARD_WIDTH)

    color = "#342D7E"

    return start_response(color)

direction_map_x = {
  'up' : 0,
  'down' : 0,
  'left' : -1,
  'right' : 1
 }

direction_map_y = {
  'up' : -1,
  'down' : 1,
  'left' : 0,
  'right' : 0
 }

def get_current_location(data):
    return data[YOU_KEY][BODY_KEY][0]


def in_board(xy, data):
    
    BOARD_HEIGHT = data[BOARD_KEY][HEIGHT_KEY]
    BOARD_WIDTH = data[BOARD_KEY][WIDTH_KEY]
    print(BOARD_WIDTH)
    print(BOARD_HEIGHT)
    if xy['x'] >= BOARD_WIDTH or xy['x'] < 0:
        return False
    elif xy['y'] >= BOARD_HEIGHT or xy['y'] < 0:
        return False
       
    return True

def get_action_xy(action, data):

    xy = get_current_location(data)
    next_xy = {
        'x': xy['x'] + direction_map_x[action],
	'y': xy['y'] + direction_map_y[action]
    }

    return next_xy

def is_valid_action(action, data):

    current_xy = get_current_location(data)
    print('Currently at %s' % str(current_xy))
    
    # Check if the action moves you off the board
    new_xy = get_action_xy(action, data)
    print('action : %s moves you to %s' % (action, str(new_xy) ))

    if not in_board(new_xy, data):
        print('Not in board')
        return False

    # Check if you will hit another snake
    snake_bodies = []
    try:
        snakes = data[BOARD_KEY][SNAKES_KEY]

        snakes_bodies = [ snake_xy for snake in snakes for snake_xy in snake[BODY_KEY][:-1] ]

        print("Snakes Bodies")
        print(snakes_bodies)

    except KeyError as e:
        print(e)


    # Check if you will self-collide
    your_bodies = []
    try:
        you = data[YOU_KEY]

        your_bodies = [ you_xy for you_xy in you[BODY_KEY] ]
        print("Your Bodies")
        print(your_bodies)

    except KeyError as e:
        print(e)

    if new_xy in snakes_bodies or new_xy in your_bodies:
        print('Theres a snake in this boot')
        return False


    return True



@bottle.post('/move')
def move():
    data = bottle.request.json

    """
    TODO: Using the data from the endpoint request object, your
            snake AI must choose a direction to move in.
    """
    print(json.dumps(data))

    directions = ['up', 'down', 'left', 'right']

    directions = [ d for d in directions if is_valid_action(d,data) ]

    direction = random.choice(directions)

    return move_response(direction)


@bottle.post('/end')
def end():
    data = bottle.request.json

    """
    TODO: If your snake AI was stateful,
        clean up any stateful objects here.
    """
    print(json.dumps(data))

    return end_response()

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug=os.getenv('DEBUG', True)
    )
