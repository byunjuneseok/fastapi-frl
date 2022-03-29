from typing import TypeVar, Generic

from fastapi import HTTPException, Request

from .algorithms import BaseAlgorithm
from .backend import LimiterBackend
from .key import BaseKeyGenerator

A = TypeVar('A', bound=BaseAlgorithm)
B = TypeVar('B', bound=LimiterBackend)
K = TypeVar('K', bound=BaseKeyGenerator)


class Limiter(Generic[A, B, K]):
    _algorithm: A
    _backend: B
    _key_generator: K
    _threshold: int

    def __init__(self, backend: B, algorithm: A, key_generator: K) -> None:

        if not isinstance(algorithm, BaseAlgorithm):
            raise ValueError('\"algorithm\" is invalid')

        self._algorithm = algorithm

        if not isinstance(backend, LimiterBackend):
            raise ValueError('\"backend\" is invalid.')

        self._backend = backend

        if not isinstance(key_generator, BaseKeyGenerator):
            raise ValueError('\"key_generator\" is invalid.')

        self._key_generator = key_generator

    async def __call__(self, request: Request) -> None:
        key = self._get_key_from_request(request=request)
        result = await self._request(key)

        if not result:
            raise HTTPException(503, detail='Rate limit exceeded.')

    def _get_key_from_request(self, request: Request) -> str:
        return self._key_generator.generate_key_from_request(request=request)

    async def _request(self, key) -> bool:
        return await self._algorithm.request(key, self._backend)
