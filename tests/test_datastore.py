import time

import pytest

from pyredis.datastore import DataStore


def test_contains():
    datastore = DataStore()
    datastore["key"] = "value"
    assert "key" in datastore


def test_delete():
    datastore = DataStore()
    datastore["key"] = "value"
    del datastore["key"]
    assert "key" not in datastore


def test_set_and_get_item():
    datastore = DataStore()
    datastore["key"] = "value"
    assert datastore["key"] == "value"


def test_expire_key():
    datastore = DataStore()
    datastore.set_with_expiry("key", "value", 0.01)
    time.sleep(0.15)
    with pytest.raises(KeyError):
        _ = datastore["key"]


def test_expire_actively():
    datastore = DataStore()
    datastore.set_with_expiry("key1", "value1", 0.01)
    datastore.set_with_expiry("key2", "value2", 0.01)
    datastore["key3"] = "value3"
    datastore["key4"] = "value4"
    time.sleep(0.15)
    datastore.remove_expired_keys()

    assert "key1" not in datastore
    assert "key2" not in datastore
    assert datastore.dbsize() == 2


def test_increment():
    datastore = DataStore()
    datastore["key"] = "1"
    incremented = datastore.increment("key")
    assert incremented == 2


def test_decrement():
    datastore = DataStore()
    datastore["key"] = "1"
    incremented = datastore.decrement("key")
    assert incremented == 0
