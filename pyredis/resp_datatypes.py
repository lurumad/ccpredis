from dataclasses import dataclass


@dataclass
class SimpleString:
    data: str

    def as_str(self) -> str:
        return self.data

    def resp_encode(self) -> bytes:
        return f"+{self.data}\r\n".encode()


@dataclass
class Error:
    data: str

    def as_str(self) -> str:
        return self.data

    def resp_encode(self) -> bytes:
        return f"-{self.data}\r\n".encode()


@dataclass
class Integer:
    data: int

    def as_str(self) -> str:
        return str(self.data)

    def resp_encode(self) -> bytes:
        return f":{self.data}\r\n".encode()


@dataclass
class BulkString:
    data: bytes

    def as_str(self) -> str:
        return self.data.decode()

    def resp_encode(self) -> bytes:
        if self.data is None:
            return b"$-1\r\n"

        return f"${len(self.data)}\r\n{self.data.decode()}\r\n".encode()


@dataclass
class Array:
    data: []

    def as_str(self) -> str:
        return " ".join([data_type.as_str() for data_type in self.data])

    def resp_encode(self) -> bytes:
        if self.data is None:
            return b"*-1\r\n"

        if len(self.data) == 0:
            return b"*0\r\n"

        encoded_elements = (element.resp_encode() for element in self.data)
        encoded_data = b"".join(encoded_elements)
        # for element in self.data:
        #     resp_elements.append(element.resp_encode().decode())
        return b"*%d\r\n%s" % (len(self.data), encoded_data)
