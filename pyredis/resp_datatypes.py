import abc
from dataclasses import dataclass


class RedisType(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, __subclass):
        return (hasattr(__subclass, 'resp_encode') and
                callable(__subclass.resp_encode) or
                NotImplemented)

    def resp_encode(self) -> bytes:
        raise NotImplementedError


@dataclass
class SimpleString(RedisType):
    _data: str

    def resp_encode(self) -> bytes:
        return f"+{self._data}\r\n".encode()

    def resp_decode(self):
        return self._data

    def __str__(self):
        return self._data


@dataclass
class Error(RedisType):
    _data: str

    def resp_encode(self) -> bytes:
        return f"-{self._data}\r\n".encode()

    def __str__(self):
        return self._data


@dataclass
class Integer(RedisType):
    _data: int

    def resp_encode(self) -> bytes:
        return f":{self._data}\r\n".encode()

    def __str__(self):
        return str(self._data)


@dataclass
class BulkString(RedisType):
    _data: bytes

    def resp_encode(self) -> bytes:
        if self._data is None:
            return b"$-1\r\n"
        return f"${len(self._data)}\r\n{self._data.decode()}\r\n".encode()

    def __str__(self):
        return self._data.decode()


@dataclass
class Array(RedisType):
    _data: []

    def resp_encode(self) -> bytes:
        if self._data is None:
            return b"*-1\r\n"

        if len(self._data) == 0:
            return b"*0\r\n"

        encoded_elements = (element.resp_encode() for element in self._data)
        encoded_data = b"".join(encoded_elements)
        return b"*%d\r\n%s" % (len(self._data), encoded_data)

    def resp_decode(self):
        return [str(data_type) for data_type in self._data]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __getitem__(self, index):
        return self._data[index]

    def __str__(self):
        return " ".join([str(data_type) for data_type in self._data])
