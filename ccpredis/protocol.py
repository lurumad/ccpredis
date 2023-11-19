RESP_TERMINATOR = '\r\n'

def parse(buffer: str) -> (int, str):
    match buffer[0]:
        case '+':
            terminator = buffer.find(RESP_TERMINATOR)

            if terminator != -1:
                return buffer[1:-2], len(buffer)
    return (None, 0)