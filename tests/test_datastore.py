from pyredis.datastore import DataStore


def test_set_and_get_item():
    datastore = DataStore()
    datastore["key"] = "value"
    assert datastore["key"] == "value"