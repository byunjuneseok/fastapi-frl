from typing import TypeVar, Generic, Optional

from fastapi import HTTPException, Request

from .algorithms.base import BaseAlgorithm
from .backend import LimiterBackend
from .key import BaseKeyGenerator

A = TypeVar('A', bound=BaseAlgorithm)
B = TypeVar('B', bound=LimiterBackend)
K = TypeVar('K', bound=BaseKeyGenerator)


class Limiter(Generic[A, K]):
    _name: str
    _algorithm: A
    _backend: LimiterBackend
    _key_generator: K
    _threshold: int

    _exception: Exception = HTTPException(429, detail='Too many requests.')

    def __init__(
            self,
            name: str,
            algorithm: A,
            key_generator: K,
            exception: Optional[Exception] = None
    ) -> None:
        self._backend = LimiterBackend.get_instance()

        if not isinstance(algorithm, BaseAlgorithm):
            raise ValueError('\"algorithm\" is invalid.')

        self._algorithm = algorithm

        if not isinstance(key_generator, BaseKeyGenerator):
            raise ValueError('\"key_generator\" is invalid.')

        self._key_generator = key_generator

        if exception is not None:
            if not isinstance(exception, Exception):
                raise ValueError('\"exception\" is invalid.')

            self._exception = exception

        if not isinstance(name, str):
            raise ValueError('\"name\" is invalid.')

        self._name = name
        self._backend.register_member_name(self._name)

    async def __call__(self, request: Request) -> None:
        key = self._get_key_from_request(request=request)
        result = await self._request(key)

        if not result:
            raise self._exception

    def _get_key_from_request(self, request: Request) -> str:
        key = self._key_generator.generate_key_from_request(request=request)
        return '{}::{}'.format(self._name, key)

    async def _request(self, key) -> bool:
        return await self._algorithm.request(key, self._backend)
