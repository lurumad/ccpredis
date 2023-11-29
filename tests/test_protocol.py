import pytest
from pyredis import protocol
from pyredis.protocol import encode_message
from pyredis.commands import encode_command
from pyredis.resp_types import (
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


@pytest.mark.parametrize(
    "data_type, expected",
    [
        (SimpleString("OK"), b"+OK\r\n"),
        (SimpleError("Error"), b"-Error\r\n"),
        (Integer(100), b":100\r\n"),
        (BulkString(b"This is a Bulk String"), b"$21\r\nThis is a Bulk String\r\n"),
        (BulkString(b""), b"$0\r\n\r\n"),
        (BulkString(None), b"$-1\r\n"),
        (Array([]), b"*0\r\n"),
        (Array(None), b"*-1\r\n"),
        (
                Array([SimpleString("String"), Integer(2), SimpleString("String2")]),
                b"*3\r\n+String\r\n:2\r\n+String2\r\n",
        ),
    ],
)
def test_encode_message(data_type, expected):
    encoded_message = encode_message(data_type)
    assert encoded_message == expected


@pytest.mark.parametrize(
    "command, expected",
    [
        ("ping", Array([BulkString(b"ping")])),
        ("ping hello", Array([BulkString(b"ping"), BulkString(b"hello")])),
        ("echo hello", Array([BulkString(b"echo"), BulkString(b"hello")])),
        ("set key value", Array([BulkString(b"set"), BulkString(b"key"), BulkString(b"value")])),
        ("get key", Array([BulkString(b"get"), BulkString(b"key")])),
    ],
)
def test_encode_command(command, expected):
    encoded_command = encode_command(command)
    assert encoded_command == expected

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


