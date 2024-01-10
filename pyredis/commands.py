import logging

from pyredis.datastore import DataStore
from pyredis.persistence import RedisPersistence
from pyredis.resp_datatypes import SimpleString, BulkString, Error, Array, Integer


logger = logging.getLogger(__name__)


def handle_command(array: Array, datastore: DataStore, persistence: RedisPersistence):
    command, *command_args = array.data
    match command.data.decode().upper():
        case "PING":
            return handle_ping(command_args)
        case "ECHO":
            return handle_echo(command_args)
        case "SET":
            persistence.log_command(array.data)
            return handle_set(command_args, datastore)
        case "GET":
            return handle_get(command_args, datastore)
        case "EXISTS":
            return handle_exists(command_args, datastore)
        case "DEL":
            persistence.log_command(array.data)
            return handle_del(command_args, datastore)
        case "INCR":
            persistence.log_command(array.data)
            return handle_incr(command_args, datastore)
        case "DECR":
            persistence.log_command(array.data)
            return handle_decr(command_args, datastore)
        case "LPUSH":
            persistence.log_command(array.data)
            return handle_lpush(command_args, datastore)
        case "RPUSH":
            persistence.log_command(array.data)
            return handle_rpush(command_args, datastore)
        case "LRANGE":
            return handle_lrange(command_args, datastore)

    return handle_unknown(command, command_args)


def handle_ping(command_args):
    if len(command_args) == 0:
        return SimpleString("PONG")
    if len(command_args) == 1:
        return BulkString(command_args[0].data)
    return Error("ERR wrong number of arguments for 'ping' command")


def handle_echo(command_args):
    if len(command_args) == 1:
        return BulkString(command_args[0].data)
    return Error("ERR wrong number of arguments for 'echo' command")


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
            expiry = int(command_args[3].data.decode())
        except ValueError:
            return Error("ERR value is not an integer or out of range")

        match option.upper():
            case "EX":
                datastore.set_with_expiry(key=key, value=value, expiry=expiry)
                return SimpleString("OK")
            case "PX":
                datastore.set_with_expiry(key=key, value=value, expiry=expiry / 1000)
                return SimpleString("OK")
    return Error("ERR syntax error")


def handle_get(command_args, datastore):
    if len(command_args) != 1:
        return Error("ERR wrong number of arguments for 'get' command")
    try:
        key = command_args[0].data.decode()
        value = datastore[key]
    except KeyError:
        return BulkString(None)
    return BulkString(value.encode())


def handle_exists(command_args, datastore):
    if len(command_args) < 1:
        return Error("ERR wrong number of arguments for 'exists' command")
    count = 0
    try:
        for command_arg in command_args:
            key = command_arg.data.decode()
            if key in datastore:
                count += 1
    except KeyError as e:
        logger.debug(f"{e.args[0]} does not exists")
        pass

    return Integer(count)


def handle_del(command_args, datastore: DataStore):
    if len(command_args) < 1:
        return Error("ERR wrong number of arguments for 'del' command")
    count = 0
    try:
        for command_arg in command_args:
            key = command_arg.data.decode()
            del datastore[key]
            count += 1
    except KeyError as e:
        logger.debug(f"{e.args[0]} does not exists")
    return Integer(count)


def handle_incr(command_args, datastore: DataStore):
    if len(command_args) != 1:
        return Error("ERR wrong number of arguments for 'incr' command")
    try:
        key = command_args[0].data.decode()
        result = datastore.increment(key)
        return Integer(result)
    except ValueError:
        return Error("ERR value is not an integer or out of range")


def handle_decr(command_args, datastore: DataStore):
    if len(command_args) != 1:
        return Error("ERR wrong number of arguments for 'decr' command")
    try:
        key = command_args[0].data.decode()
        result = datastore.decrement(key)
        return Integer(result)
    except ValueError:
        return Error("ERR value is not an integer or out of range")


def handle_lpush(command_args, datastore: DataStore):
    if len(command_args) < 2:
        return Error("ERR wrong number of arguments for 'lpush' command")
    count = 0
    try:
        key = command_args[0].data.decode()
        for value in command_args[1:]:
            count = datastore.prepend(key, value.data.decode())
    except TypeError:
        return Error(
            "WRONGTYPE Operation against a key holding the wrong kind of value"
        )
    return Integer(count)


def handle_rpush(command_args, datastore: DataStore):
    if len(command_args) < 2:
        return Error("ERR wrong number of arguments for 'rpush' command")
    count = 0
    try:
        key = command_args[0].data.decode()
        for value in command_args[1:]:
            count = datastore.append(key, value.data.decode())
    except TypeError:
        return Error(
            "WRONGTYPE Operation against a key holding the wrong kind of value"
        )
    return Integer(count)


def handle_lrange(command_args, datastore: DataStore):
    if len(command_args) < 3:
        return Error("ERR wrong number of arguments for 'lrange' command")
    try:
        key = command_args[0].data.decode()
        start = int(command_args[1].data.decode())
        stop = int(command_args[2].data.decode()) + 1
        values = datastore.range(key, start, stop)
        return Array([BulkString(value.encode()) for value in values])
    except ValueError:
        return Error("ERR value is not an integer or out of range")
    except KeyError:
        return Array([])


def handle_unknown(command, command_args):
    args = " ".join([f"'{arg.data.decode()}'" for arg in command_args])
    return Error(
        f"ERR unknown command '{command.data.decode().upper()}', with args beginning with: {args}"
    )


def encode_command(command):
    return Array([BulkString(data.encode()) for data in command.split()])
