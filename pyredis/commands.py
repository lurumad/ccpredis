import logging

from pyredis.datastore import DataStore
from pyredis.resp_datatypes import SimpleString, BulkString, Error, Array, Integer


logger = logging.getLogger(__name__)


def handle_command(command: Array, datastore: DataStore):
    command, *command_args = command.data
    match command.data.decode().upper():
        case "PING":
            return handle_ping(command_args)
        case "ECHO":
            return handle_echo(command_args)
        case "SET":
            return handle_set(command_args, datastore)
        case "GET":
            return handle_get(command_args, datastore)
        case "EXISTS":
            return handle_exists(command_args, datastore)

    return handle_unknown(command, command_args)


def handle_exists(command_args, datastore):
    if len(command_args) < 1:
        return Error("ERR wrong number of arguments for 'exists' command")
    count = 0
    try:
        for command_arg in command_args:
            key = command_arg.data.decode()
            _ = datastore[key]
            count += 1
    except KeyError as e:
        logger.debug(f"{e.args[0]} does not exists")
        pass

    return Integer(count)


def handle_unknown(command, command_args):
    args = " ".join([f"'{arg.data.decode()}'" for arg in command_args])
    return Error(
        f"ERR unknown command '{command.data.decode().upper()}', with args beginning with: {args}"
    )


def handle_get(command_args, datastore):
    if len(command_args) != 1:
        return Error("ERR wrong number of arguments for 'get' command")
    try:
        key = command_args[0].data.decode()
        value = datastore[key]
    except KeyError:
        return BulkString(None)
    return BulkString(value.encode())


def handle_set(command_args, datastore):
    if len(command_args) < 2:
        return Error("ERR wrong number of arguments for 'set' command")
    key = command_args[0].data.decode()
    value = command_args[1].data.decode()
    if len(command_args) == 2:
        datastore[key] = value
        return SimpleString("OK")
    if len(command_args) == 4:
        option = command_args[2].data.decode()
        try:
            option_value = float(command_args[3].data.decode())
        except ValueError:
            return Error("ERR value is not an integer or out of range")

        match option.upper():
            case "EX":
                datastore.set_with_expiry(key=key, value=value, expiry=option_value)
                return SimpleString("OK")
            case "PX":
                datastore.set_with_expiry(
                    key=key, value=value, expiry=option_value / 1000
                )
                return SimpleString("OK")
    return Error("ERR syntax error")


def handle_echo(command_args):
    if len(command_args) == 1:
        return BulkString(command_args[0].data)
    return Error("ERR wrong number of arguments for 'echo' command")


def handle_ping(command_args):
    if len(command_args) == 0:
        return SimpleString("PONG")
    if len(command_args) == 1:
        return BulkString(command_args[0].data)
    return Error("ERR wrong number of arguments for 'ping' command")


def encode_command(command):
    return Array([BulkString(data.encode()) for data in command.split()])
