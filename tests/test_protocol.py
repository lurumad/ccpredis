import pytest
from pyredis import protocol
from pyredis.types import (
    SimpleString,
    SimpleError,
    Integer,
    BulkString,
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
])
def test_protocol_parse(buffer, expected):
    actual = protocol.parse(buffer)
    assert actual == expected

