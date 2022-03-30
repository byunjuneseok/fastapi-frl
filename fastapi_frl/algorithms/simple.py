from .base import BaseAlgorithm
from ..backend import LimiterBackend


class SimpleAlgorithm(BaseAlgorithm):
    _threshold: int

    def __init__(self, threshold: int):
        if not isinstance(threshold, int):
            raise ValueError('The threshold must be a positive integer.')

        if threshold <= 0:
            raise ValueError('The threshold must be a positive integer.')

        self._threshold = threshold

    async def request(self, key: str, backend: LimiterBackend, **kwargs) -> bool:
        async with backend.get_client() as redis:
            requests = await redis.incr(key)

        if requests == 1:
            await redis.expire(key, 60)

        return requests <= self._threshold
