import os

import pytest

from pyredis.commands import handle_command
from pyredis.datastore import DataStore
from pyredis.persistence import AppendOnlyFilePersistence, restore_from_file
from pyredis.resp_datatypes import Array, BulkString


@pytest.fixture()
def setup_persistence():
    # setup
    filename = "ccdbtest.aof"
    persistence = AppendOnlyFilePersistence(filename)

    # unit test
    yield persistence

    # teardown
    os.remove(filename)


def test_persists_and_load(setup_persistence):
    datastore = DataStore()
    persistence = setup_persistence
    for i in range(1, 3):
        set_command = Array(
            [
                BulkString(b"set"),
                BulkString(f"key{i}".encode()),
                BulkString("value".encode()),
            ]
        )
        persistence.log_command(set_command)
    del_command = Array(
        [
            BulkString(b"del"),
            BulkString("key1".encode()),
        ]
    )
    persistence.log_command(del_command)
    restore_from_file("ccdbtest.aof", datastore)
    get_command_1 = Array(
        [
            BulkString(b"get"),
            BulkString("key1".encode()),
        ]
    )
    get_command_2 = Array(
        [
            BulkString(b"get"),
            BulkString("key2".encode()),
        ]
    )
    delete_key = handle_command(get_command_1, datastore, persistence)
    existing_key = handle_command(get_command_2, datastore, persistence)
    assert delete_key == BulkString(None)
    assert existing_key == BulkString(b"value")
