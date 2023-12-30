import time

import pytest

from pyredis.commands import handle_command, encode_command
from pyredis.datastore import DataStore
from pyredis.resp_datatypes import (
    SimpleString,
    Error,
    BulkString,
    Array, Integer,
)

data_store = DataStore()


@pytest.mark.parametrize(
    "command, expected",
    [
        # ECHO
        (
            Array([BulkString(b"ECHO")]),
            Error("ERR wrong number of arguments for 'echo' command"),
        ),
        (Array([BulkString(b"echo"), BulkString(b"Hello")]), BulkString(b"Hello")),
        (
            Array([BulkString(b"echo"), BulkString(b"Hello"), BulkString(b"World")]),
            Error("ERR wrong number of arguments for 'echo' command"),
        ),
        # PING
        (Array([BulkString(b"ping")]), SimpleString("PONG")),
        (Array([BulkString(b"ping"), BulkString(b"Hello")]), BulkString(b"Hello")),
        # SET
        (
            Array([BulkString(b"set")]),
            Error("ERR wrong number of arguments for 'set' command"),
        ),
        (
            Array([BulkString(b"set"), BulkString(b"key")]),
            Error("ERR wrong number of arguments for 'set' command"),
        ),
        (
            Array(
                [
                    BulkString(b"set"),
                    BulkString(b"key"),
                    BulkString(b"value"),
                    BulkString(b"ex"),
                ]
            ),
            Error("ERR syntax error"),
        ),
        (
            Array([BulkString(b"set"), BulkString(b"key"), BulkString(b"value")]),
            SimpleString("OK"),
        ),
        (
            Array(
                [
                    BulkString(b"set"),
                    BulkString(b"key"),
                    BulkString(b"value"),
                    BulkString(b"ex"),
                    BulkString(b"60"),
                ]
            ),
            SimpleString("OK"),
        ),
        (
            Array(
                [
                    BulkString(b"set"),
                    BulkString(b"key"),
                    BulkString(b"value"),
                    BulkString(b"ex"),
                    BulkString(b"a"),
                ]
            ),
            Error("ERR value is not an integer or out of range"),
        ),
        # GET
        (
            Array([BulkString(b"get")]),
            Error("ERR wrong number of arguments for 'get' command"),
        ),
        (
            Array([BulkString(b"get"), BulkString(b"key")]),
            BulkString(b"value"),
        ),
        (Array([BulkString(b"get"), BulkString(b"invalid")]), BulkString(None)),
        # EXISTS
        (Array([BulkString(b"exists"), BulkString(b"key")]), Integer(1)),
    ],
    ids=[
        "ECHO",
        "ECHO hello",
        "ECHO hello world",
        "PING",
        "PING hello",
        "SET",
        "SET key",
        "SET key value",
        "SET key value EX",
        "SET key value EX 60",
        "SET key value EX invalid_integer",
        "GET",
        "GET key",
        "GET invalid",
        "EXISTS key",
    ],
)
def test_handle_command(command, expected):
    result = handle_command(command, data_store)
    assert result == expected


@pytest.mark.parametrize(
    "command, expected",
    [
        ("ping", Array([BulkString(b"ping")])),
        ("ping hello", Array([BulkString(b"ping"), BulkString(b"hello")])),
        ("echo hello", Array([BulkString(b"echo"), BulkString(b"hello")])),
        (
            "set key value",
            Array([BulkString(b"set"), BulkString(b"key"), BulkString(b"value")]),
        ),
        ("get key", Array([BulkString(b"get"), BulkString(b"key")])),
    ],
)
def test_encode_command(command, expected):
    encoded_command = encode_command(command)
    assert encoded_command == expected


def test_get_with_expiry():
    datastore = DataStore()
    key = "key"
    value = "value"
    px = 100

    command = Array(
        [
            BulkString(b"set"),
            BulkString(f"{key}".encode()),
            BulkString(f"{value}".encode()),
            BulkString(b"px"),
            BulkString(f"{px}".encode()),
        ]
    )

    result = handle_command(command, datastore)
    assert result == SimpleString("OK")
    time.sleep((px + 100) / 1000)
    command = Array([BulkString(b"get"), BulkString(f"{key}".encode())])
    result = handle_command(command, datastore)
    assert result == BulkString(None)
