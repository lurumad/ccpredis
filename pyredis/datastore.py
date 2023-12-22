import random
from dataclasses import dataclass
from threading import Lock
from time import time_ns
from typing import Any

COUNT_KEYS = 20


@dataclass
class CacheEntry:
    value: Any
    expiry: int = 0

    def expired(self):
        return self.expiry and self.expiry < int(time_ns())


class DataStore:
    def __init__(self):
        self._data = dict()
        self._lock = Lock()

    def __getitem__(self, key):
        with self._lock:
            entry: CacheEntry = self._data[key]
            self._remove_expired_key(key, entry)
            return entry.value

    def __setitem__(self, key, value):
        with self._lock:
            self._data[key] = CacheEntry(value=value)

    def set_with_expiry(self, key: any, value: any, expiry: int) -> None:
        with self._lock:
            calculated_expiry = time_ns() + self._to_nanoseconds(expiry)
            self._data[key] = CacheEntry(value=value, expiry=calculated_expiry)

    def remove_expired_keys(self):
        while True:
            count = COUNT_KEYS if len(self._data) >= COUNT_KEYS else len(self._data)

            if count == 0:
                break

            keys = random.sample(list(self._data), count)
            if self._count_expired(keys) / count <= 0.25:
                break

    def dbsize(self):
        return len(self._data)

    def _count_expired(self, keys):
        count_expired = 0
        for key in keys:
            try:
                with self._lock:
                    if self._data[key].expired():
                        del self._data[key]
                        count_expired += 1
            except KeyError:
                pass
        return count_expired

    def _remove_expired_key(self, key, entry):
        if entry.expired():
            del self._data[key]
            raise KeyError

    @staticmethod
    def _to_nanoseconds(seconds):
        return seconds * 10**9
