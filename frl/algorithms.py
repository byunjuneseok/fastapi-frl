from abc import ABC, abstractmethod
from enum import Enum
from time import time

from frl.backend import LimiterBackend


class BaseAlgorithm(ABC):

    @abstractmethod
    async def request(self, key: str, redis: LimiterBackend, **kwargs) -> bool:
        ...


class SimpleAlgorithm(BaseAlgorithm):
    _threshold: int

    def __init__(self, threshold: int):
        if not isinstance(threshold, int):
            raise ValueError('The threshold must be a positive integer.')

        if threshold < 0:
            raise ValueError('The threshold must be a positive integer.')

        self._threshold = threshold

    async def request(self, key: str, backend: LimiterBackend, **kwargs) -> bool:
        async with backend.get_client() as redis:
            requests = await redis.incr(key)

        if requests == 1:
            await redis.expire(key, 60)

        return requests <= self._threshold


class WindowSize(Enum):
    SECOND = 1
    MINUTE = 60
    HOUR = 60 * 60
    DAY = 60 * 60 * 24


class FixedWindowCounter(BaseAlgorithm):
    _threshold: int
    _window_size: int

    def __init__(self, window_size: WindowSize, threshold: int):
        if not isinstance(threshold, int):
            raise ValueError('The threshold must be a positive integer.')

        if threshold < 0:
            raise ValueError('The threshold must be a positive integer.')

        self._threshold = threshold

        if not isinstance(window_size, WindowSize):
            raise ValueError('\"window_size\" is invalid.')

        self._window_size = window_size.value

    async def request(self, key: str, backend: LimiterBackend, **kwargs) -> bool:

        key_postfix = int(time() / self._window_size)
        key = f'{key}::{key_postfix}'

        async with backend.get_client() as redis:
            requests = await redis.incr(key)

        if requests == 1:
            await redis.expire(key, self._window_size)

        return requests <= self._threshold
