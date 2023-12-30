import time

import pytest

from pyredis.commands import handle_command, encode_command
from pyredis.datastore import DataStore
from pyredis.resp_datatypes import (
    SimpleString,
    Error,
    BulkString,
    Array,
    Integer,
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


@pytest.mark.parametrize(
    "command, expected",
    [
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
    ],
    ids=[
        "GET",
        "GET key",
        "GET invalid",
    ],
)
def test_get_command(command, expected):
    datastore = DataStore()

    set_command = Array(
        [
            BulkString(b"set"),
            BulkString("key".encode()),
            BulkString("value".encode()),
        ]
    )

    result = handle_command(set_command, datastore)
    assert result == SimpleString("OK")
    result = handle_command(command, datastore)
    assert result == expected


@pytest.mark.parametrize(
    "command, expected",
    [
        # EXISTS
        (Array([BulkString(b"exists")]), Error("ERR wrong number of arguments for 'exists' command")),
        (Array([BulkString(b"exists"), BulkString(b"key1")]), Integer(1)),
        (Array([BulkString(b"exists"), BulkString(b"nosuchkey")]), Integer(0)),
        (
            Array([BulkString(b"exists"), BulkString(b"key1"), BulkString(b"key2")]),
            Integer(2),
        ),
    ],
    ids=["EXISTS", "EXISTS key", "EXISTS nosuchkey", "EXISTS key1 key2"],
)
def test_exists_command(command, expected):
    datastore = DataStore()

    for i in range(1, 3):
        set_command = Array(
            [
                BulkString(b"set"),
                BulkString(f"key{i}".encode()),
                BulkString("value".encode()),
            ]
        )

        result = handle_command(set_command, datastore)
        assert result == SimpleString("OK")

    result = handle_command(command, datastore)
    assert result == expected


@pytest.mark.parametrize(
    "command, expected",
    [
        # EXISTS
        (Array([BulkString(b"del")]), Error("ERR wrong number of arguments for 'del' command")),
        (Array([BulkString(b"del"), BulkString(b"key1")]), Integer(1)),
        (Array([BulkString(b"del"), BulkString(b"key1"), BulkString(b"key2")]), Integer(2)),
        (Array([BulkString(b"del"), BulkString(b"nosuchkey")]), Integer(0)),
    ],
    ids=["DEL", "DEL key1", "DEL key1 key 2", "DEL nosuchkey"],
)
def test_del_command(command, expected):
    datastore = DataStore()

    for i in range(1, 3):
        set_command = Array(
            [
                BulkString(b"set"),
                BulkString(f"key{i}".encode()),
                BulkString("value".encode()),
            ]
        )

        result = handle_command(set_command, datastore)
        assert result == SimpleString("OK")

    result = handle_command(command, datastore)
    assert result == expected


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


def test_incr_invalid_command():
    datastore = DataStore()
    command = Array([BulkString(b"incr")])
    result = handle_command(command, datastore)
    assert result == Error("ERR wrong number of arguments for 'incr' command")


