from .base import BaseAlgorithm
from ..backend import LimiterBackend


class LeakyBucket(BaseAlgorithm):
    async def request(self, key: str, redis: LimiterBackend, **kwargs) -> bool:
        ...


class TokenBucket(BaseAlgorithm):
    async def request(self, key: str, redis: LimiterBackend, **kwargs) -> bool:
        ...
