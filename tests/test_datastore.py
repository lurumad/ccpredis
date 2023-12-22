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


def test_expire_actively():
    datastore = DataStore()
    datastore.set_with_expiry("key1", "value1", 0.01)
    datastore.set_with_expiry("key2", "value2", 0.01)
    datastore["key3"] = "value3"
    datastore["key4"] = "value4"
    time.sleep(0.15)
    datastore.remove_expired_keys()

    assert datastore.dbsize() == 2
