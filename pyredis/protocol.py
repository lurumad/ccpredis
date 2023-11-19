from pyredis.types import (
    SimpleString,
    SimpleError,
    Integer,
)

PROTOCOL_TERMINATOR = '\r\n'
PROTOCOL_TERMINATOR_LEN = len(PROTOCOL_TERMINATOR)


def parse(buffer: str) -> (int, str):
    protocol_terminator = buffer.find(PROTOCOL_TERMINATOR)
    if protocol_terminator == -1:
        return None, 0

    match buffer[0]:
        case '+':
            simple_string = SimpleString(buffer[1:protocol_terminator])
            return simple_string, 1 + len(simple_string.value) + PROTOCOL_TERMINATOR_LEN
        case '-':
            simple_error = SimpleError(buffer[1:protocol_terminator])
            return simple_error, 1 + len(simple_error.value) + PROTOCOL_TERMINATOR_LEN
        case ':':
            integer = Integer(int(buffer[1:protocol_terminator]))
            return integer, len(buffer)
