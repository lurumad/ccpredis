from dataclasses import dataclass


RESP_TERMINATOR = '\r\n'


@dataclass
class SimpleString:
    value: str

@dataclass
class SimpleError:
    value: str


def parse(buffer: str) -> (int, str):
    match buffer[0]:
        case '+':
            resp_terminator = buffer.find(RESP_TERMINATOR)
            if resp_terminator != -1:
                simple_string = SimpleString(buffer[1:resp_terminator])
                return simple_string, 1 + len(simple_string.value + RESP_TERMINATOR)
        case '-':
            resp_terminator = buffer.find(RESP_TERMINATOR)
            if resp_terminator != -1:
                simple_error = SimpleError(buffer[1:resp_terminator])
                return simple_error, 1 + len(simple_error.value + RESP_TERMINATOR)
    return None, 0
