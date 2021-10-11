import time
from redis import ConnectionError
from redis import Redis
from redis import ConnectionPool
from collections import namedtuple

ValueWithTime = namedtuple('ValueWithTime', ['time', 'value'])


class Storage:
    def __init__(
            self,
            host='localhost',
            port=6379,
            db=0,
            socket_timeout=None,
            socket_connect_timeout=None,
            count_retry=5,
            reconnect_delay=0.01,
            auto_connect=True
    ):
        self.connection_pool = ConnectionPool(
            host=host,
            port=port,
            db=db,
            socket_timeout=socket_timeout,
            socket_connect_timeout=socket_connect_timeout,
        )
        self.count_retry = count_retry
        self.reconnect_delay = reconnect_delay
        self._cache = {}
        self._redis = None
        if auto_connect:
            self.connect()

    def connect(self):
        self._redis = Redis(connection_pool=self.connection_pool)

    def get(self, name: str):
        if self._redis is None:
            raise ValueError('Соединение с базой данных не было установлено, '
                             'используйте метод "connect" для этого')
        if not isinstance(name, str):
            raise ValueError('name должно быть строкой')

        for _ in range(self.count_retry):
            try:
                return self._redis.get(name)
            except ConnectionError:
                time.sleep(self.reconnect_delay)
                self.connect()

        raise ConnectionError

    def set(self, name: str, value, time__sec=None):
        if self._redis is None:
            raise ValueError('Соединение с базой данных не было установлено, '
                             'используйте метод "connect" для этого')

        for _ in range(self.count_retry):
            try:
                if time__sec is None:
                    self._redis.set(name, value)
                else:
                    self._redis.setex(name=name, time=time__sec, value=value)
                break
            except ConnectionError:
                time.sleep(self.reconnect_delay)
                self.connect()

    def cache_get(self, name: str):
        try:
            return self.get(name)
        except ConnectionError:
            return self._cache.get(name)

    def cache_set(self, name: str, value: float, time__sec: int):
        self._cache[name] = value
        try:
            self.set(name, value, time__sec)
        except ConnectionError:
            pass

