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
        (
            Array([BulkString(b"exists")]),
            Error("ERR wrong number of arguments for 'exists' command"),
        ),
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
        (
            Array([BulkString(b"del")]),
            Error("ERR wrong number of arguments for 'del' command"),
        ),
        (Array([BulkString(b"del"), BulkString(b"key1")]), Integer(1)),
        (
            Array([BulkString(b"del"), BulkString(b"key1"), BulkString(b"key2")]),
            Integer(2),
        ),
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


def test_incr_invalid_key():
    datastore = DataStore()
    command = Array([BulkString(b"set"), BulkString(b"key"), BulkString(b"value")])
    result = handle_command(command, datastore)
    assert result == SimpleString("OK")
    command = Array([BulkString(b"incr"), BulkString(b"key")])
    result = handle_command(command, datastore)
    assert result == Error("ERR value is not an integer or out of range")


def test_incr_command():
    datastore = DataStore()
    for i in range(1, 5):
        command = Array([BulkString(b"incr"), BulkString(b"key")])
        result = handle_command(command, datastore)
        assert result == Integer(i)


def test_decr_invalid_command():
    datastore = DataStore()
    command = Array([BulkString(b"decr")])
    result = handle_command(command, datastore)
    assert result == Error("ERR wrong number of arguments for 'decr' command")


def test_decr_invalid_key():
    datastore = DataStore()
    command = Array([BulkString(b"set"), BulkString(b"key"), BulkString(b"value")])
    result = handle_command(command, datastore)
    assert result == SimpleString("OK")
    command = Array([BulkString(b"decr"), BulkString(b"key")])
    result = handle_command(command, datastore)
    assert result == Error("ERR value is not an integer or out of range")


def test_decr_command():
    datastore = DataStore()
    for i in range(1, 5):
        command = Array([BulkString(b"decr"), BulkString(b"key")])
        result = handle_command(command, datastore)
        assert result == Integer(i * -1)


@pytest.mark.parametrize(
    "command",
    [
        Array([BulkString(b"lpush")]),
        Array([BulkString(b"lpush"), BulkString(b"key")]),
    ],
    ids=["LPUSH", "LPUSH key"],
)
def test_lpush_invalid_command(command):
    datastore = DataStore()
    result = handle_command(command, datastore)
    assert result == Error("ERR wrong number of arguments for 'lpush' command")


def test_lpush_invalid_key():
    datastore = DataStore()
    command = Array([BulkString(b"set"), BulkString(b"key"), BulkString(b"value")])
    result = handle_command(command, datastore)
    assert result == SimpleString("OK")
    command = Array([BulkString(b"lpush"), BulkString(b"key"), BulkString(b"value")])
    result = handle_command(command, datastore)
    assert result == Error(
        "WRONGTYPE Operation against a key holding the wrong kind of value"
    )


def test_lpush_command():
    datastore = DataStore()
    command = Array(
        [
            BulkString(b"lpush"),
            BulkString(b"mylist"),
            BulkString(b"world"),
            BulkString(b"hello"),
        ]
    )
    result = handle_command(command, datastore)
    assert result == Integer(2)


@pytest.mark.parametrize(
    "command",
    [
        Array([BulkString(b"rpush")]),
        Array([BulkString(b"rpush"), BulkString(b"key")]),
    ],
    ids=["RPUSH", "RPUSH key"],
)
def test_rpush_invalid_command(command):
    datastore = DataStore()
    result = handle_command(command, datastore)
    assert result == Error("ERR wrong number of arguments for 'rpush' command")


def test_rpush_invalid_key():
    datastore = DataStore()
    command = Array([BulkString(b"set"), BulkString(b"key"), BulkString(b"value")])
    result = handle_command(command, datastore)
    assert result == SimpleString("OK")
    command = Array([BulkString(b"rpush"), BulkString(b"key"), BulkString(b"value")])
    result = handle_command(command, datastore)
    assert result == Error(
        "WRONGTYPE Operation against a key holding the wrong kind of value"
    )


def test_rpush_command():
    datastore = DataStore()
    command = Array(
        [
            BulkString(b"rpush"),
            BulkString(b"mylist"),
            BulkString(b"hello"),
            BulkString(b"world"),
        ]
    )
    result = handle_command(command, datastore)
    assert result == Integer(2)


@pytest.mark.parametrize(
    "command, expected",
    [
        (
            Array([BulkString(b"lrange")]),
            Error("ERR wrong number of arguments for 'lrange' command"),
        ),
        (
            Array([BulkString(b"lrange"), BulkString(b"key")]),
            Error("ERR wrong number of arguments for 'lrange' command"),
        ),
        (
            Array(
                [
                    BulkString(b"lrange"),
                    BulkString(b"key"),
                    BulkString(b"a"),
                    BulkString(b"-1"),
                ]
            ),
            Error("ERR value is not an integer or out of range"),
        ),
        (
            Array(
                [
                    BulkString(b"lrange"),
                    BulkString(b"key"),
                    BulkString(b"0"),
                    BulkString(b"b"),
                ]
            ),
            Error("ERR value is not an integer or out of range"),
        ),
    ],
    ids=["LRANGE", "LRANGE key", "LRANGE key a -1", "LRANGE key 0 b"],
)
def test_lrange_invalid_command(command, expected):
    datastore = DataStore()
    result = handle_command(command, datastore)
    assert result == expected


@pytest.mark.parametrize(
    "command, expected",
    [
        (
            Array(
                [
                    BulkString(b"lrange"),
                    BulkString(b"myList"),
                    BulkString(b"0"),
                    BulkString(b"0"),
                ]
            ),
            Array([BulkString(b"three")]),
        ),
        (
            Array(
                [
                    BulkString(b"lrange"),
                    BulkString(b"myList"),
                    BulkString(b"-2"),
                    BulkString(b"2"),
                ]
            ),
            Array([BulkString(b"two"), BulkString(b"one")]),
        ),
        (
            Array(
                [
                    BulkString(b"lrange"),
                    BulkString(b"myList"),
                    BulkString(b"-100"),
                    BulkString(b"100"),
                ]
            ),
            Array([BulkString(b"three"), BulkString(b"two"), BulkString(b"one")]),
        ),
        (
            Array(
                [
                    BulkString(b"lrange"),
                    BulkString(b"myList"),
                    BulkString(b"5"),
                    BulkString(b"10"),
                ]
            ),
            Array([]),
        ),
    ],
    ids=[
        "LRANGE myList 0 0",
        "LRANGE myList -3 2",
        "LRANGE myList -100 100",
        "LRANGE myList 5 10",
    ],
)
def test_lpush_lrange_command(command, expected):
    datastore = DataStore()
    lpush = Array(
        [
            BulkString(b"lpush"),
            BulkString(b"myList"),
            BulkString(b"one"),
            BulkString(b"two"),
            BulkString(b"three"),
        ]
    )
    handle_command(lpush, datastore)
    result = handle_command(command, datastore)
    assert result == expected


@pytest.mark.parametrize(
    "command, expected",
    [
        (
            Array(
                [
                    BulkString(b"lrange"),
                    BulkString(b"myList"),
                    BulkString(b"0"),
                    BulkString(b"0"),
                ]
            ),
            Array([BulkString(b"one")]),
        ),
        (
            Array(
                [
                    BulkString(b"lrange"),
                    BulkString(b"myList"),
                    BulkString(b"-3"),
                    BulkString(b"2"),
                ]
            ),
            Array([BulkString(b"one"), BulkString(b"two"), BulkString(b"three")]),
        ),
        (
            Array(
                [
                    BulkString(b"lrange"),
                    BulkString(b"myList"),
                    BulkString(b"-100"),
                    BulkString(b"100"),
                ]
            ),
            Array([BulkString(b"one"), BulkString(b"two"), BulkString(b"three")]),
        ),
        (
            Array(
                [
                    BulkString(b"lrange"),
                    BulkString(b"myList"),
                    BulkString(b"5"),
                    BulkString(b"10"),
                ]
            ),
            Array([]),
        ),
    ],
    ids=[
        "LRANGE myList 0 0",
        "LRANGE myList -3 2",
        "LRANGE myList -100 100",
        "LRANGE myList 5 10",
    ],
)
def test_rpush_lrange_command(command, expected):
    datastore = DataStore()
    lpush = Array(
        [
            BulkString(b"rpush"),
            BulkString(b"myList"),
            BulkString(b"one"),
            BulkString(b"two"),
            BulkString(b"three"),
        ]
    )
    handle_command(lpush, datastore)
    result = handle_command(command, datastore)
    assert result == expected
