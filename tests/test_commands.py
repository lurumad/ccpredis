import pytest

from pyredis.commands import handle_command
from pyredis.resp_types import (
    SimpleString,
    SimpleError,
    BulkString,
    Array,
)


@pytest.mark.parametrize(
    "command, expected",
    [
        # Echo Tests
        (
                Array([BulkString(b"ECHO")]),
                SimpleError("ERR wrong number of arguments for 'echo' command"),
        ),
        (Array([BulkString(b"echo"), BulkString(b"Hello")]), BulkString(b"Hello")),
        (
                Array([BulkString(b"echo"), BulkString(b"Hello"), BulkString(b"World")]),
                SimpleError("ERR wrong number of arguments for 'echo' command"),
        ),
        # Ping Tests
        (Array([BulkString(b"ping")]), SimpleString("PONG")),
        (Array([BulkString(b"ping"), BulkString(b"Hello")]), BulkString(b"Hello")),
    ],
)
def test_handle_command(command, expected):
    result = handle_command(command)
    assert result == expected
