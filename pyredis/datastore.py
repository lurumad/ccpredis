import time
from dataclasses import dataclass
from threading import Lock


@dataclass
class CacheEntry:
    value: str
    expiry: float

    def expired(self, current_unix_timestamp: float):
        return self.expiry != -1 and current_unix_timestamp > self.expiry


class DataStore:
    def __init__(self):
        self._data = dict()
        self._lock = Lock()

    def __getitem__(self, key):
        with self._lock:
            entry: CacheEntry = self._data[key]
            self._check_expire_passively(key, entry)
            return entry.value

    def __setitem__(self, key, value):
        with self._lock:
            self._data[key] = CacheEntry(
                value=value,
                expiry=-1
            )

    def set_with_expiry(self, key: any, value: any, expiry: float) -> None:
        with self._lock:
            expiry_unix_timestamp = time.time() + expiry
            self._data[key] = CacheEntry(
                value=value,
                expiry=expiry_unix_timestamp
            )

    def _check_expire_passively(self, key, entry):
        if entry.expired(time.time()):
            del self._data[key]
            raise KeyError


