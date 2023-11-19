def parse(buffer: str) -> (int, str):
    match buffer[0]:
        case '+':
            return buffer[1:-2], len(buffer)