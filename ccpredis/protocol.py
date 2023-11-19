from ccpredis.data_types.simple_string import SimpleString


RESP_TERMINATOR = '\r\n'

def parse(buffer: str) -> (int, str):
    match buffer[0]:
        case '+':
            resp_terminator = buffer.find(RESP_TERMINATOR)
            if resp_terminator != -1:
                simple_string = SimpleString(buffer[1:resp_terminator])
                return simple_string, 1 + len(simple_string.value + RESP_TERMINATOR)
    return (None, 0)