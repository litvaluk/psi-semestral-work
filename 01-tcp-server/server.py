from socket import socket, AF_INET, SOCK_STREAM, timeout
from threading import Thread
from helper import *


class Server:

    def __init__(self, address, port):
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.bind((address, port))
        self.sock.listen()
        print("server started at " + str(address) + ":" + str(port))

    def handler(self, connection, address):
        print("established connection from {}:{}".format(*address))
        phase = 0
        username_hash = 0
        first_position = 0, 0
        second_position = 0, 0
        actual_position = 0, 0
        direction = 4
        picked = False
        last_action = None
        recharging = False

        try:
            while True:
                data = connection.recv(1024)
                decoded = decode_message(data)

                if not data:
                    continue

                print("Received: ", decoded, sep="")

                if decoded == "RECHARGING":
                    connection.settimeout(TIMEOUT_RECHARGING)
                    recharging = True
                    continue

                if decoded == "FULL POWER":
                    recharging = False
                    connection.settimeout(TIMEOUT)
                    continue

                if recharging:
                    connection.sendall(create_message(SERVER_LOGIC_ERROR))
                    break

                if phase == 0:
                    username_hash = compute_hash(decoded)
                    print("Sending: ", username_hash, sep="")
                    connection.sendall(create_message((username_hash + SERVER_KEY) % 65536))
                    phase = 1

                elif phase == 1:
                    if (int(decoded) + 65536 - CLIENT_KEY) % 65536 == username_hash:
                        print("Sending: ", SERVER_OK, sep="")
                        connection.sendall(create_message(SERVER_OK))

                        print("Sending: ", SERVER_MOVE, sep="")
                        connection.sendall(create_message(SERVER_MOVE))
                        phase = 2
                    else:
                        print("Sending: ", SERVER_LOGIN_FAILED, sep="")
                        connection.sendall(create_message(SERVER_LOGIN_FAILED))
                        break

                elif phase == 2:
                    if "OK" in decoded:
                        split = decoded.split(" ")
                        first_position = int(split[1]), int(split[2])
                    print("Sending: ", SERVER_MOVE, sep="")
                    connection.sendall(create_message(SERVER_MOVE))
                    phase = 3

                elif phase == 3:
                    if "OK" in decoded:
                        split = decoded.split(" ")
                        second_position = int(split[1]), int(split[2])
                        if second_position != first_position:
                            actual_position = second_position
                            direction = get_direction(first_position, second_position)
                            print("Coordinates = ", actual_position, sep="")
                            print("Direction = ", direction, sep="")
                            phase = 4
                        else:
                            first_position = second_position
                            print("Sending: ", SERVER_MOVE, sep="")
                            connection.sendall(create_message(SERVER_MOVE))

                if phase == 4:
                    if actual_position == (-2, 2):
                        phase = 5
                    else:
                        split = decoded.split(" ")
                        actual_position = (int(split[1]), int(split[2]))
                        move, actual_position, direction = get_next_move(actual_position, direction)
                        print("Sending: ", move, sep="")
                        print("Position: ", actual_position, "   Direction: ",  direction, sep="")
                        last_action = move
                        connection.sendall(create_message(move))

                if phase == 5:
                    if picked and decoded != "" and last_action != SERVER_TURN_RIGHT and last_action != SERVER_TURN_LEFT:
                        phase = 42
                    else:
                        # if last_action == SERVER_MOVE and actual_position != (int(split[1]), int(split[2])):
                        #     actual_position = (int(split[1]), int(split[2]))
                        #     picked = True
                        action, actual_position, direction, picked = search_box(actual_position, direction, picked)
                        print("Sending: ", action, sep="")
                        print("Position: ", actual_position, "   Direction: ", direction)
                        last_action = action
                        connection.sendall(create_message(action))

                if phase == 42:
                    print("Sending: ", SERVER_LOGOUT, sep="")
                    connection.sendall(create_message(SERVER_LOGOUT))
                    break

        except timeout:
            print("Timeout!")

        finally:
            connection.close()

    def run(self):
        while True:
            connection, address = self.sock.accept()
            connection.settimeout(10000000)
            t = Thread(target=self.handler, args=(connection, address))
            t.start()
