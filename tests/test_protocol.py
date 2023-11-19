from ccpredis import protocol


def test_simple_string():
    buffer = "+OK\r\n"
    simple_string, size = protocol.parse(buffer)
    assert "OK" == simple_string
    assert 5 == size

def test_simple_string_incomplete():
    buffer = "+OK"
    simple_string, size = protocol.parse(buffer)
    assert None == simple_string
    assert 0 == size