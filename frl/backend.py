import threading

import aioredis
from aioredis import Redis


class LimiterBackend:
    _instance = None
    _lock = threading.Lock()

    @classmethod
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(LimiterBackend, cls).__new__(cls)

        return cls._instance

    def __init__(self, backend_url=None, **kwargs) -> None:
        self._install_redis(url=backend_url, **kwargs)

    def _install_redis(self, url, **kwargs):
        self._redis_backend = aioredis.from_url(url, **kwargs)

    def get_client(self) -> Redis:
        return self._redis_backend.client()
