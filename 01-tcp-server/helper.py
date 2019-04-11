SERVER_MOVE = "102 MOVE"
SERVER_TURN_LEFT = "103 TURN LEFT"
SERVER_TURN_RIGHT = "104 TURN RIGHT"
SERVER_PICK_UP = "105 GET MESSAGE"
SERVER_LOGOUT = "106 LOGOUT"
SERVER_OK = "200 OK"
SERVER_LOGIN_FAILED = "300 LOGIN FAILED"
SERVER_SYNTAX_ERROR = "301 SYNTAX ERROR"
SERVER_LOGIC_ERROR = "302 LOGIC ERROR"

MAX_SERVER_CONFIRMATION = 5

MAX_CLIENT_USERNAME = 12
MAX_CLIENT_CONFIRMATION = 7
MAX_CLIENT_OK = 12
MAX_CLIENT_RECHARGING = 12
MAX_CLIENT_FULL_POWER = 12
MAX_CLIENT_MESSAGE = 100

SERVER_KEY = 54621
CLIENT_KEY = 45328

TIMEOUT = 1
TIMEOUT_RECHARGING = 5

UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3


def create_message(message):
    if type(message) != str:
        return (str(message) + "\a\b").encode("utf-8")
    return (message + "\a\b").encode("utf-8")


def decode_message(message):
    return message.decode("utf-8")[:-2]


def compute_hash(username):
    char_sum = 0
    for c in username:
        char_sum += ord(c)
    return (char_sum * 1000) % 65536


def get_direction(coords1, coords2):
    x1, y1 = coords1
    x2, y2 = coords2

    if x1 == x2 and y1 != y2:
        if y1 < y2:
            return UP
        else:
            return DOWN

    elif x1 != x2 and y1 == y2:
        if x1 < x2:
            return RIGHT
        else:
            return LEFT

    else:
        return 4


def get_next_move(position, direction):
    x, y = position

    if x > -2:
        if direction == UP:
            return SERVER_TURN_LEFT, position, LEFT
        elif direction == DOWN:
            return SERVER_TURN_RIGHT, position, LEFT
        elif direction == RIGHT:
            return SERVER_TURN_LEFT, position, UP
        return SERVER_MOVE, (x-1, y), LEFT

    elif x < -2:
        if direction == UP:
            return SERVER_TURN_RIGHT, position, RIGHT
        elif direction == DOWN:
            return SERVER_TURN_LEFT, position, RIGHT
        elif direction == LEFT:
            return SERVER_TURN_RIGHT, position, UP
        return SERVER_MOVE, (x+1, y), RIGHT

    elif y > 2:
        if direction == LEFT:
            return SERVER_TURN_LEFT, position, DOWN
        elif direction == RIGHT:
            return SERVER_TURN_RIGHT, position, DOWN
        elif direction == UP:
            return SERVER_TURN_RIGHT, position, RIGHT
        return SERVER_MOVE, (x, y-1), DOWN

    elif y < 2:
        if direction == LEFT:
            return SERVER_TURN_RIGHT, position, UP
        elif direction == RIGHT:
            return SERVER_TURN_LEFT, position, UP
        elif direction == DOWN:
            return SERVER_TURN_LEFT, position, RIGHT
        return SERVER_MOVE, (x, y+1), UP


def search_box(position, direction, picked):
    if position == (-2, 2):
        if direction == UP:
            return SERVER_TURN_RIGHT, position, RIGHT, False
        elif direction == RIGHT:
            return SERVER_TURN_RIGHT, position, DOWN, False
        elif direction == LEFT:
            return SERVER_TURN_LEFT, position, DOWN, False

    if not picked:
        picked = True
        return SERVER_PICK_UP, position, direction, picked

    elif position == (2, -2):
        return "Not found!"

    else:
        x, y = position
        picked = False

        if x%2 == 0:
            if y != -2:
                if direction == RIGHT:
                    return SERVER_TURN_RIGHT, position, DOWN, picked
                return SERVER_MOVE, (x, y-1), DOWN, picked
            if y == -2:
                if direction == DOWN:
                    return SERVER_TURN_LEFT, position, RIGHT, True
                else:
                    return SERVER_MOVE, (x+1, y), RIGHT, picked
        else:
            if y != 2:
                if direction == RIGHT:
                    return SERVER_TURN_LEFT, position, UP, picked
                return SERVER_MOVE, (x, y+1), UP, picked
            if y == 2:
                if direction == UP:
                    return SERVER_TURN_RIGHT, position, RIGHT, True
                else:
                    return SERVER_MOVE, (x+1, y), RIGHT, picked
