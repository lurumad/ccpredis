import asyncio
import logging

from pyredis.commands import handle_command
from pyredis.datastore import DataStore
from pyredis.protocol import parse

_DATASTORE = DataStore()


class RedisServerProtocol(asyncio.Protocol):
    def __init__(self):
        self._transport = None
        self._buffer = bytearray()
        self._logger = logging.getLogger(__name__)

    def connection_made(self, transport):
        self._transport = transport

    def data_received(self, data):
        if not data:
            self._transport.close()
        self._logger.info(data)
        self._buffer.extend(data)

        command, size = parse(self._buffer)
        self._logger.info(command)
        if command:
            self._buffer = self._buffer[size:]
            result = handle_command(command, _DATASTORE)
            self._transport.write(result.resp_encode())
