import logging
import selectors
import socket
import types

from pyredis.commands import handle_command
from pyredis.datastore import DataStore
from pyredis.persistence import AppendOnlyFilePersistence
from pyredis.protocol import parse

DEFAULT_PORT = 6379
DEFAULT_SERVER = "127.0.0.1"
RECV_SIZE = 1024

sel = selectors.DefaultSelector()


class Server:
    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.bind((self._host, self._port))
        self._server.listen()
        self._server.setblocking(False)
        self._datastore = DataStore()
        self._persistence = AppendOnlyFilePersistence("ccdb.aof")
        self._logger = logging.getLogger(__name__)
        sel.register(self._server, selectors.EVENT_READ, data=None)

    def run(self):
        try:
            while True:
                events = sel.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        self._accept_wrapper(key.fileobj)
                    else:
                        self._service_connection(key, mask)
        except KeyboardInterrupt:
            self._logger.info("Caught keyboard interrupt, exiting")

    def _accept_wrapper(self, sock):
        connection, address = sock.accept()
        self._logger.info(f"Accepted connection from {address}")
        connection.setblocking(False)
        data = types.SimpleNamespace(addr=address, inb=b"", outb="")
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        sel.register(connection, events, data=data)

    def _service_connection(self, key, mask):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(RECV_SIZE)
            if recv_data:
                command, size = parse(recv_data)
                self._logger.info(f"Command received: {command}")
                result = handle_command(command, self._datastore, self._persistence)
                self._logger.info(f"Command result: {result.resp_encode()}")
                data.outb = result.resp_encode()
            else:
                self._logger.info(f"Closing connection to {data.addr}")
                sel.unregister(sock)
                sock.close()
        if mask & selectors.EVENT_WRITE:
            if data.outb:
                self._logger.info(f"Sending {data.outb!r} to {data.addr}")
                sent = sock.send(data.outb)
                data.outb = data.outb[sent:]
