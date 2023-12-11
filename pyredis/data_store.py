class DataStore:
    def __init__(self):
        self._data = dict()

    def __getitem__(self, item):
        return self._data[item]

    def __setitem__(self, key, value):
        self._data[key] = value
