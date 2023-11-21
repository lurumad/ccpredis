import pytest
from pyredis import protocol
from pyredis.types import (
    SimpleString,
    SimpleError,
    Integer,
    BulkString,
    Array,
)


@pytest.mark.parametrize("buffer, expected", [
    # Simple Strings
    (b"+OK\r\n", (SimpleString("OK"), 5)),
    (b"+PONG\r\n", (SimpleString("PONG"), 7)),
    (b"+OK", (None, 0)),
    (b"+OK\r\nExtra", (SimpleString("OK"), 5)),
    # Simple Errors
    (b"-Error message\r\n", (SimpleError("Error message"), 16)),
    (b"Error message\r\n", (None, 0)),
    (b"-Error message\r\nExtra", (SimpleError("Error message"), 16)),
    # Integers
    (b":1\r\n", (Integer(1), 4)),
    (b":-1\r\n", (Integer(-1), 5)),
    # Bulk Strings
    (b"$5\r\nhello", (None, 0)),
    (b"$5\r\nhello\r\n", (BulkString(b"hello"), 11)),
    (b"$12\r\nHello, World\r\n", (BulkString(b"Hello, World"), 19)),
    (b"$12\r\nHello\r\nWorld\r\n", (BulkString(b"Hello\r\nWorld"), 19)),
    (b"$0\r\n\r\n", (BulkString(b""), 6)),
    (b"$-1\r\n", (None, 5)),
    # Arrays
    (b"*0", (None, 0)),
    (b"*0\r\n", (Array([]), 4)),
    (b"*-1\r\n", (Array(None), 5)),
    (b"*2\r\n$5\r\nhello\r\n$5\r\nworld\r\n", (Array([BulkString(b"hello"), BulkString(b"world")]), 26)),
    (b"*3\r\n:1\r\n:2\r\n:3\r\n", (Array([Integer(1), Integer(2), Integer(3)]), 16))
])
def test_protocol_parse(buffer, expected):
    actual = protocol.parse(buffer)
    assert actual == expected

