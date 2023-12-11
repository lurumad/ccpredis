from pyredis.resp_types import SimpleString, BulkString, Error, Array


def handle_command(command: Array):
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
            if len(command_args) != 2:
                return Error("ERR wrong number of arguments for 'set' command")
            return SimpleString("OK")

    args = " ".join([f"'{arg.data.decode()}'" for arg in command_args])
    return Error(
        f"ERR unknown command '{command.data.decode().upper()}', with args beginning with: {args}"
    )


def encode_command(command):
    return Array([BulkString(data.encode()) for data in command.split()])
