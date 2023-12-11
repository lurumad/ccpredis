import pytest

from pyredis.commands import handle_command
from pyredis.resp_types import (
    SimpleString,
    Error,
    BulkString,
    Array,
)


@pytest.mark.parametrize(
    "command, expected",
    [
        # Echo Tests
        (
            Array([BulkString(b"ECHO")]),
            Error("ERR wrong number of arguments for 'echo' command"),
        ),
        (Array([BulkString(b"echo"), BulkString(b"Hello")]), BulkString(b"Hello")),
        (
            Array([BulkString(b"echo"), BulkString(b"Hello"), BulkString(b"World")]),
            Error("ERR wrong number of arguments for 'echo' command"),
        ),
        # Ping Tests
        (Array([BulkString(b"ping")]), SimpleString("PONG")),
        (Array([BulkString(b"ping"), BulkString(b"Hello")]), BulkString(b"Hello")),
        # Set Tests
        (
            Array([BulkString(b"set")]),
            Error("ERR wrong number of arguments for 'set' command"),
        ),
        (
            Array([BulkString(b"set"), SimpleString("key")]),
            Error("ERR wrong number of arguments for 'set' command"),
        ),
        (
            Array([BulkString(b"set"), SimpleString("key"), SimpleString("value")]),
            SimpleString("OK"),
        ),
    ],
)
def test_handle_command(command, expected):
    result = handle_command(command)
    assert result == expected
