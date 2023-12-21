import time

import pytest

from pyredis.datastore import DataStore


def test_set_and_get_item():
    datastore = DataStore()
    datastore["key"] = "value"
    assert datastore["key"] == "value"


def test_expire_key():
    datastore = DataStore()
    datastore.set_with_expiry("key", "value", 0.01)
    time.sleep(0.15)
    with pytest.raises(KeyError):
        datastore["key"]
