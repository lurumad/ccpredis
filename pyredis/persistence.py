from pyredis import protocol
from pyredis.datastore import DataStore


class RedisPersistence:
    def log_command(self, command):
        pass


class AppendOnlyFilePersistence(RedisPersistence):
    def __init__(self, filename):
        self._filename = filename
        self.file = open(filename, mode="ab", buffering=0)

    def log_command(self, command):
        print(command)
        self.file.write(f"*{len(command)}\r\n".encode())

        for item in command:
            self.file.write(item.resp_encode())


class NoPersistence(RedisPersistence):
    def log_command(self, command):
        pass


def restore_from_file(filename: str, datastore: DataStore):
    buffer = bytearray()
    with open(filename, mode="rb") as file:
        for line in file:
            if line.startswith(b"*") and len(buffer) > 0:
                update_datastore(buffer, datastore)
                buffer = bytearray()
            buffer.extend(line)
    if len(buffer) > 0:
        update_datastore(buffer, datastore)


def update_datastore(buffer, datastore):
    from pyredis.commands import handle_command

    command, size = protocol.parse(buffer)
    handle_command(command, datastore, NoPersistence())
