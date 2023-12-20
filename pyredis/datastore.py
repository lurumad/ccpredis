from threading import Lock


class DataStore:
    def __init__(self):
        self._data = dict()
        self._lock = Lock()

    def __getitem__(self, item):
        with self._lock:
            return self._data[item]

    def __setitem__(self, key, value):
        with self._lock:
            self._data[key] = value
