from abc import ABC, abstractmethod

from ..backend import LimiterBackend


class BaseAlgorithm(ABC):

    @abstractmethod
    async def request(self, key: str, redis: LimiterBackend, **kwargs) -> bool:
        ...
