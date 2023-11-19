from ccpredis import protocol


def test_simple_string():
    buffer = "+OK\r\n"
    simple_string, size = protocol.parse(buffer)
    assert "OK" == simple_string
    assert 5 == size