from time import time

from .base import BaseAlgorithm
from ..backend import LimiterBackend


class BaseWindowAlgorithm(BaseAlgorithm):
    _threshold: int
    _window_size: int

    def __init__(self, window_size: int, threshold: int):
        if not isinstance(threshold, int):
            raise ValueError('The threshold must be a positive integer.')

        if threshold <= 0:
            raise ValueError('The threshold must be a positive integer.')

        self._threshold = threshold

        if not isinstance(window_size, int):
            raise ValueError('\"window_size\" is invalid.')

        if window_size <= 0:
            raise ValueError('The threshold must be a positive integer.')

        self._window_size = window_size

    async def request(self, key: str, redis: LimiterBackend, **kwargs) -> bool:
        ...


class FixedWindowCounter(BaseWindowAlgorithm):

    async def request(self, key: str, backend: LimiterBackend, **kwargs) -> bool:

        key_postfix = int(time() / self._window_size)
        key = f'{key}::{key_postfix}'

        async with backend.get_client() as redis:
            requests = await redis.incr(key)

        if requests == 1:
            await redis.expire(key, self._window_size)

        return requests <= self._threshold


class SlidingWindowLog(BaseWindowAlgorithm):

    async def request(self, key: str, backend: LimiterBackend, **kwargs) -> bool:
        async with backend.get_client() as redis:
            requests = await redis.incr(key)

        if requests == 1:
            await redis.expire(key, self._window_size)

        return requests <= self._threshold


class SlidingWindowCounter(BaseWindowAlgorithm):
    async def request(self, key: str, backend: LimiterBackend, **kwargs) -> bool:
        timestamp = time()

        key_postfix = int(timestamp / self._window_size)
        ratio = (timestamp - key_postfix * self._window_size) / self._window_size

        async with backend.get_client() as redis:
            requests = await redis.incr(f'{key}::{key_postfix}')
            previous_requests = await redis.get(f'{key}::{key_postfix - 1}')

        if previous_requests is None:
            previous_requests = 0

        else:
            previous_requests = int(previous_requests)
        expected_requests = previous_requests * (1 - ratio) + requests * ratio

        return expected_requests <= self._threshold
