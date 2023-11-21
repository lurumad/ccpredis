from pyredis.types import (
    SimpleString,
    SimpleError,
    Integer,
    BulkString, Array,
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
            string_length = int(type_content)

            if string_length == -1:
                return None, type_content_len

            if (
                len(buffer) <
                protocol_terminator_index + PROTOCOL_TERMINATOR_LEN + string_length + PROTOCOL_TERMINATOR_LEN
            ):
                return None, 0

            type_content = buffer[type_content_len:type_content_len + string_length]
            return (
                BulkString(type_content),
                protocol_terminator_index + PROTOCOL_TERMINATOR_LEN + string_length + PROTOCOL_TERMINATOR_LEN
            )
        case '*':
            array_length = int(type_content)
            data = []

            for i in range(0, array_length):
                additional_resp_element = buffer[type_content_len:]
                element, size = parse(additional_resp_element)
                data.append(element)
                type_content_len = type_content_len + size

            if len(data) > 0:
                return Array(data), type_content_len

            return Array([]), protocol_terminator_index + PROTOCOL_TERMINATOR_LEN

    return None, 0
