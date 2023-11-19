import pytest
from ccpredis import protocol
from ccpredis.protocol import SimpleString, SimpleError


@pytest.mark.parametrize("buffer, expected", [
    ("+OK\r\n", (SimpleString("OK"), 5)),
    ("+PONG\r\n", (SimpleString("PONG"), 7)),
])
def test_simple_string(buffer, expected):
    actual = protocol.parse(buffer)
    assert actual == expected


def test_simple_string_incomplete():
    buffer = "+OK"
    actual = protocol.parse(buffer)
    assert actual == (None, 0)


def test_simple_string_extra_data():
    buffer = "+OK\r\nextra"
    actual = protocol.parse(buffer)
    assert actual == (SimpleString("OK"), 5)


def test_simple_error():
    buffer = "-Error message\r\n"
    actual = protocol.parse(buffer)
    assert actual == (SimpleError("Error message"), 16)
