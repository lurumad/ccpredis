from pyredis.types import (
    SimpleString,
    SimpleError,
    Integer,
    BulkString,
)

PROTOCOL_TERMINATOR = b"\r\n"
PROTOCOL_TERMINATOR_LEN = len(PROTOCOL_TERMINATOR)


def parse(buffer):
    protocol_terminator_index = buffer.find(PROTOCOL_TERMINATOR)
    if protocol_terminator_index == -1:
        return None, 0
    type_content = buffer[1:protocol_terminator_index].decode()
    type_content_len = protocol_terminator_index + PROTOCOL_TERMINATOR_LEN
    match chr(buffer[0]):
        case '+':
            return SimpleString(type_content), type_content_len
        case '-':
            return SimpleError(type_content), type_content_len
        case ':':
            return Integer(int(type_content)), type_content_len
        case '$':
            if not buffer.endswith(b"\r\n"):
                return None, 0
            return BulkString(type_content), type_content_len
    return None, 0
