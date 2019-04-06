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

        try:
            while True:
                data = connection.recv(1024)
                decoded = decode_message(data)

                if not data:
                    continue

                print("Received: ", decoded, sep="")

                if phase == 0:
                    username_hash = compute_hash(decoded)
                    print("Sending: ", username_hash, sep="")
                    connection.sendall(create_message((username_hash + SERVER_KEY) % 65536))
                    phase = 1

                elif phase == 1:
                    if (int(decoded) + 65536 - CLIENT_KEY) % 65536 == username_hash:
                        print("Sending: ", SERVER_OK, sep="")
                        connection.sendall(create_message(SERVER_OK))
                    else:
                        print("Sending: ", SERVER_LOGIN_FAILED, sep="")
                        connection.sendall(create_message(SERVER_LOGIN_FAILED))
                        break

        except timeout:
            print("Timeout!")

        finally:
            connection.close()

    def run(self):
        while True:
            connection, address = self.sock.accept()
            connection.settimeout(TIMEOUT)
            t = Thread(target=self.handler, args=(connection, address))
            t.start()
