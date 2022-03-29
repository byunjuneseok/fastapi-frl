import threading
from typing import List

import aioredis
from aioredis import Redis


class LimiterBackend:
    _instance = None
    _lock: threading.Lock = threading.Lock()
    _member_names: List[str] = []

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

    def register_member_name(self, member_name: str) -> None:
        if not isinstance(member_name, str):
            raise ValueError('\"member\" is invalid.')

        if member_name in self._member_names:
            raise ValueError(f'\"member_name\" was duplicated. {member_name}')

        self._member_names.append(member_name)
