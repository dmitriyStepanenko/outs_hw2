import hashlib
import json
import pytest


@pytest.fixture
def store():
    class Store:
        def __init__(self, cache: dict = None):
            self.cache = cache if cache else {}

        def get(self, name):
            return self.cache.get(name)

        def cache_get(self, name):
            return self.get(name)

        def cache_set(self, name, value, time):
            ...

    init_cache = {
        "uid:" + hashlib.md5("aab77777777777".encode('utf-8')).hexdigest(): 4,
        "i:1": json.dumps(['a', 'b'])
    }
    return Store(init_cache)