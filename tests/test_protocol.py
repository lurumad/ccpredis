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
    (b"$5\r\nhello", (None, 0))
])
def test_protocol_parse(buffer, expected):
    actual = protocol.parse(buffer)
    assert actual == expected

