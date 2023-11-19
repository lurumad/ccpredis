from pyredis.types import (
    SimpleString,
    SimpleError,
    Integer,
)

PROTOCOL_TERMINATOR = '\r\n'
PROTOCOL_TERMINATOR_LEN = len(PROTOCOL_TERMINATOR)


def parse(buffer: str) -> (int, str):
    protocol_terminator_index = buffer.find(PROTOCOL_TERMINATOR)
    if protocol_terminator_index == -1:
        return None, 0
    type_content = buffer[1:protocol_terminator_index]
    type_content_len = protocol_terminator_index + PROTOCOL_TERMINATOR_LEN
    match buffer[0]:
        case '+':
            return SimpleString(type_content), type_content_len
        case '-':
            simple_error = SimpleError(type_content)
            return simple_error, type_content_len
        case ':':
            integer = Integer(int(type_content))
            return integer, type_content_len
