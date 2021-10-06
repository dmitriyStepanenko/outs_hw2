import redis
from datetime import datetime
from datetime import timedelta
from collections import namedtuple
from typing import Dict

ValueWithTime = namedtuple('ValueWithTime', ['time', 'value'])


class Storage:
    def __init__(self):
        self._redis = redis.Redis()

    def get(self, name: str):
        if not isinstance(name, str):
            raise ValueError('name должно быть строкой')
        return self._redis.get(name)

    def set(self, name: str, value):
        self._redis.set(name, value)

    def cache_get(self, name: str):
        return self.get(name)

    def cache_set(self, name: str, value: float, time__sec: int):
        self._redis.setex(name=name, time=time__sec, value=value)
