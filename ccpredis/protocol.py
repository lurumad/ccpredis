RESP_TERMINATOR = '\r\n'

def parse(buffer: str) -> (int, str):
    match buffer[0]:
        case '+':
            resp_terminator = buffer.find(RESP_TERMINATOR)
            if resp_terminator != -1:
                return buffer[1:resp_terminator], 5
    return (None, 0)