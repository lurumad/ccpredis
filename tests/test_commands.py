import pytest

from pyredis.commands import handle_command
from pyredis.datastore import DataStore
from pyredis.resp_types import (
    SimpleString,
    Error,
    BulkString,
    Array,
)

data_store = DataStore()


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
            Array([BulkString(b"set"), BulkString(b"key")]),
            Error("ERR wrong number of arguments for 'set' command"),
        ),
        (
            Array([BulkString(b"set"), BulkString(b"key"), BulkString(b"value")]),
            SimpleString("OK"),
        ),
        # Get Tests
        (
            Array([BulkString(b"get")]),
            Error("ERR wrong number of arguments for 'get' command"),
        ),
        (
            Array([BulkString(b"get"), BulkString(b"key")]),
            BulkString(b"value"),
        ),
        (Array([BulkString(b"get"), BulkString(b"invalid")]), BulkString(None)),
    ],
)
def test_handle_command(command, expected):
    result = handle_command(command, data_store)
    assert result == expected
