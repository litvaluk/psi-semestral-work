SERVER_MOVE = "102 MOVE"
SERVER_TURN_LEFT = "103 TURN LEFT"
SERVER_TURN_RIGHT = "104 TURN RIGHT"
SERVER_PICK_UP = "105 GET MESSAGE"
SERVER_LOGOUT = "106 LOGOUT"
SERVER_OK = "200 OK"
SERVER_LOGIN_FAILED = "300 LOGIN FAILED"
SERVER_SYNTAX_ERROR = "301 SYNTAX ERROR"
SERVER_LOGIC_ERROR = "302 LOGIC ERROR"

SERVER_KEY = 54621
CLIENT_KEY = 45328

TIMEOUT = 1
TIMEOUT_RECHARGING = 5

UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3


class InvalidMessage(Exception):
    pass


def create_message(message):
    if type(message) != str:
        return (str(message) + "\a\b").encode("utf-8")
    return (message + "\a\b").encode("utf-8")


def syntax_check(message, phase, last_action, sep):
    print("Syntax check: ", message, sep="")
    a_at_end = False
    now_separated = False

    if sep == "\a\b":
        now_separated = True

    if len(message) > 0 and message[len(message) - 1] == "\a":
        a_at_end = True
        offset = 1
    else:
        offset = 2

    if phase == 0 and len(message) > 12 - offset:
        raise InvalidMessage("Username too long")
    elif phase == 1 and len(message) > 7 - offset and message != "RECHARGING"[:len(message)] and message != "FULL POWER"[:len(message)]:
        raise InvalidMessage("Client confirmation too long")
    elif phase == 1 and message != "RECHARGING"[:len(message)] and message != "FULL POWER"[:len(message)]:
        if (a_at_end and not message[:-1].isnumeric()) or (not a_at_end and not message.isnumeric()):
            raise InvalidMessage("Client confirmation not numeric")
    elif (phase == 2 or phase == 3 or phase == 4) and len(message) > 12 - offset and last_action != SERVER_PICK_UP:
        raise InvalidMessage("Client action too long")
    elif (phase == 2 or phase == 3 or phase == 4) and last_action != SERVER_PICK_UP and message != "RECHARGING\a"[:len(message)] and message != "FULL POWER\a"[:len(message)]:
        split = message.split(" ")

        if len(split) > 3:
            raise InvalidMessage("Invalid format of client ok response")

        if len(split) == 1:
            if split[0] != "OK" and split[0] != "O":
                raise InvalidMessage("Wrong format of the client action")
        if len(split) == 2:
            if split[0] != "OK" or split[1][-1:] == "\a":
                raise InvalidMessage("Wrong format of the client action")
            if split[1] != "-" and split[1] != "":
                x = None
                try:
                    x = float(split[1])
                except ValueError as e:
                    raise InvalidMessage("Wrong format of the client action")
                if not x.is_integer():
                    raise InvalidMessage("Wrong format of the client action")
        if len(split) == 3:
            if split[0] != "OK" or split[1] == "-" or (split[2] == "-" and now_separated) or (len(split) > 1 and split[2][-2:] == "-\a" and now_separated):
                raise InvalidMessage("Wrong format of the client action")
            if split[2] != "" and split[2] != "-":
                y = None
                try:
                    if a_at_end:
                        y = float(split[2][:-1])
                    else:
                        y = float(split[2])
                except ValueError as e:
                    raise InvalidMessage("Wrong format of the client action")
                if not y.is_integer():
                    raise InvalidMessage("Wrong format of the client action")

    elif last_action == SERVER_PICK_UP and len(message) > 100 - offset and message != "RECHARGING"[:len(message)] and message != "FULL POWER"[:len(message)]:
        raise InvalidMessage("Message too long")
    return message


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

        if x % 2 == 0:
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

# print("RECHARGING"[:20])
