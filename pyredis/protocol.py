from pyredis.resp_datatypes import (
    SimpleString,
    Error,
    Integer,
    BulkString,
    Array,
)

PROTOCOL_TERMINATOR = b"\r\n"
PROTOCOL_TERMINATOR_LEN = len(PROTOCOL_TERMINATOR)


def parse(buffer):
    protocol_terminator_index = buffer.find(PROTOCOL_TERMINATOR)

    if protocol_terminator_index == -1:
        return None, 0

    first_byte = buffer[0]
    data = buffer[1:protocol_terminator_index].decode()
    data_length = protocol_terminator_index + PROTOCOL_TERMINATOR_LEN

    match chr(first_byte):
        case "+":
            return SimpleString(data), data_length
        case "-":
            return Error(data), data_length
        case ":":
            return Integer(int(data)), data_length
        case "$":
            string_length = int(data)

            if string_length == -1:
                return None, data_length

            if not is_bulk_string_properly_terminated(
                buffer, protocol_terminator_index, string_length
            ):
                return None, 0

            data = buffer[data_length : data_length + string_length]

            return (
                BulkString(data),
                protocol_terminator_index
                + PROTOCOL_TERMINATOR_LEN
                + string_length
                + PROTOCOL_TERMINATOR_LEN,
            )
        case "*":
            array_length = int(data)
            resp_elements = []

            if array_length == 0:
                return Array([]), data_length

            if array_length == -1:
                return Array(None), data_length

            for i in range(0, array_length):
                additional_resp_elements = buffer[data_length:]
                element, size = parse(additional_resp_elements)
                resp_elements.append(element)
                data_length = data_length + size

            return Array(resp_elements), data_length

    return None, 0


def is_bulk_string_properly_terminated(
    buffer, protocol_terminator_index, string_length
):
    return (
        len(buffer)
        >= protocol_terminator_index
        + PROTOCOL_TERMINATOR_LEN
        + string_length
        + PROTOCOL_TERMINATOR_LEN
    )


def encode_message(data_type):
    return data_type.resp_encode()
