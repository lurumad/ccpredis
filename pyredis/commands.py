from pyredis.datastore import DataStore
from pyredis.resp_types import SimpleString, BulkString, Error, Array


def handle_command(command: Array, datastore: DataStore):
    command, *command_args = command.data
    match command.data.decode().upper():
        case "PING":
            if len(command_args) == 0:
                return SimpleString("PONG")
            if len(command_args) == 1:
                return BulkString(command_args[0].data)
            return Error("ERR wrong number of arguments for 'ping' command")
        case "ECHO":
            if len(command_args) == 1:
                return BulkString(command_args[0].data)
            return Error("ERR wrong number of arguments for 'echo' command")
        case "SET":
            if len(command_args) < 2:
                return Error("ERR wrong number of arguments for 'set' command")
            key = command_args[0].data.decode()
            value = command_args[1].data.decode()
            datastore[key] = value
            if len(command_args) == 4:
                option = command_args[2].data.decode()
                try:
                    option_value = float(command_args[3].data.decode())
                except ValueError:
                    return Error("ERR value is not an integer or out of range")

                match option.upper():
                    case "EX":
                        datastore.set_with_expiry(
                            key=key, value=value, expiry=option_value
                        )
                    case "PX":
                        datastore.set_with_expiry(
                            key=key, value=value, expiry=option_value / 1000
                        )
            return SimpleString("OK")
        case "GET":
            if len(command_args) != 1:
                return Error("ERR wrong number of arguments for 'get' command")
            try:
                key = command_args[0].data.decode()
                value = datastore[key]
            except KeyError:
                return BulkString(None)
            return BulkString(value.encode())

    args = " ".join([f"'{arg.data.decode()}'" for arg in command_args])
    return Error(
        f"ERR unknown command '{command.data.decode().upper()}', with args beginning with: {args}"
    )


def encode_command(command):
    return Array([BulkString(data.encode()) for data in command.split()])
