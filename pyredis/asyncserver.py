import asyncio

from pyredis.commands import handle_command
from pyredis.datastore import DataStore
from pyredis.protocol import parse

_DATASTORE = DataStore()


class RedisServerProtocol(asyncio.Protocol):
    def __init__(self):
        self.transport = None
        self.buffer = bytearray()

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        if not data:
            self.transport.close()

        self.buffer.extend(data)

        command, size = parse(self.buffer)

        if command:
            self.buffer = self.buffer[size:]
            result = handle_command(command, _DATASTORE)
            self.transport.write(result.resp_encode())
