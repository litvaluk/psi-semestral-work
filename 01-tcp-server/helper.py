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
