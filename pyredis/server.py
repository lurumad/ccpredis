import socket

from pyredis.commands import handle_command
from pyredis.protocol import parse

DEFAULT_PORT = 6379
DEFAULT_SERVER = "127.0.0.1"
RECV_SIZE = 1024


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen()

    def run(self):
        try:
            while True:
                client_connection, client_address = self.server.accept()
                print(f"Connected by {client_address}")
                self.handle(client_connection)
        except KeyboardInterrupt:
            print("Caught keyboard interrupt, exiting")

    def handle(self, connection):
        try:
            while True:
                data = connection.recv(RECV_SIZE)

                if not data:
                    break

                command, size = parse(data)
                command_parsed = handle_command(command)
                connection.sendall(command_parsed.resp_encode())
        finally:
            connection.close()
