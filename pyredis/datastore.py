import random
from dataclasses import dataclass
from itertools import islice
from threading import Lock
from time import time_ns
from typing import Any

COUNT_KEYS = 20


@dataclass
class CacheEntry:
    value: Any
    expiry: float = 0

    def expired(self):
        return self.expiry and self.expiry < int(time_ns())


class DataStore:
    def __init__(self):
        self._data = dict()
        self._lock = Lock()

    def __getitem__(self, key: str):
        with self._lock:
            entry: CacheEntry = self._data[key]
            self._remove_expired_key(key, entry)
            return entry.value

    def __setitem__(self, key: str, value: Any):
        with self._lock:
            self._data[key] = CacheEntry(value=value)

    def __contains__(self, item: Any):
        return item in self._data

    def __delitem__(self, key: str):
        del self._data[key]

    def set_with_expiry(self, key: str, value: any, expiry: float) -> None:
        with self._lock:
            calculated_expiry = time_ns() + self._to_nanoseconds(expiry)
            self._data[key] = CacheEntry(value=value, expiry=calculated_expiry)

    def remove_expired_keys(self) -> None:
        while True:
            count = COUNT_KEYS if len(self._data) >= COUNT_KEYS else len(self._data)

            if count == 0:
                break

            keys = random.sample(list(self._data), count)
            if self._expire(keys) / count <= 0.25:
                break

    def dbsize(self) -> int:
        return len(self._data)

    def _expire(self, keys: list[str]) -> int:
        count_expired = 0
        for key in keys:
            with self._lock:
                if key not in self._data:
                    pass
                if self._data[key].expired():
                    del self._data[key]
                    count_expired += 1
        return count_expired

    def _remove_expired_key(self, key: str, entry: CacheEntry) -> None:
        if entry.expired():
            del self._data[key]
            raise KeyError

    @staticmethod
    def _to_nanoseconds(seconds: float) -> int:
        return seconds * 10**9

    def increment(self, key: str) -> int:
        with self._lock:
            if key not in self._data:
                self._data[key] = CacheEntry(0)
            value = int(self._data[key].value)
            value += 1
            self._data[key] = CacheEntry(value)
            return value

    def decrement(self, key: str) -> int:
        with self._lock:
            if key not in self._data:
                self._data[key] = CacheEntry(0)
            value = int(self._data[key].value)
            value -= 1
            self._data[key] = CacheEntry(value)
            return value

    def prepend(self, key: str, value: Any) -> int:
        with self._lock:
            item = self._data.get(key, CacheEntry([]))
            if not isinstance(item.value, list):
                raise TypeError
            item.value.insert(0, value)
            self._data[key] = item
            return len(item.value)

    def append(self, key: str, value: Any) -> int:
        with self._lock:
            item = self._data.get(key, CacheEntry([]))
            if not isinstance(item.value, list):
                raise TypeError
            item.value.append(value)
            self._data[key] = item
            return len(item.value)

    def range(self, key: str, start: int, stop: int) -> list:
        with self._lock:
            item = self._data.get(key, CacheEntry([]))
            if not isinstance(item.value, list):
                raise TypeError

            length = len(item.value)
            if start > length:
                return []
            if stop > length:
                stop = length
            if start < 0:
                start = max(length + start, 0)

            return list(islice(item.value, start, stop))
