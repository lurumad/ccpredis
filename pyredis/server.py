import logging
import socket

from pyredis.commands import handle_command
from pyredis.datastore import DataStore
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
        self._datastore = DataStore()

    def run(self):
        logger = logging.getLogger(__name__)
        try:
            while True:
                client_connection, client_address = self.server.accept()
                logger.info(f"Connected by {client_address}")
                self.handle(client_connection)
        except KeyboardInterrupt:
            logger.info("Caught keyboard interrupt, exiting")

    def handle(self, connection):
        with connection:
            while True:
                data = connection.recv(RECV_SIZE)

                if not data:
                    break

                command, size = parse(data)
                command_parsed = handle_command(command, self._datastore)
                connection.sendall(command_parsed.resp_encode())
