from abc import ABC, abstractmethod
from uuid import uuid4

from fastapi import Request


class BaseKeyGenerator(ABC):

    @abstractmethod
    def generate_key_from_request(self, request: Request) -> str:
        ...


class NoKey(BaseKeyGenerator):
    def __init__(self) -> None:
        self.unique_uuid = uuid4().__str__()

    def generate_key_from_request(self, request: Request) -> str:
        return self.unique_uuid


class KeyByIP(BaseKeyGenerator):
    def generate_key_from_request(self, request: Request) -> str:
        return request.client.host


class KeyByMethod(BaseKeyGenerator):
    def generate_key_from_request(self, request: Request) -> str:
        return request.method


class KeyByPath(BaseKeyGenerator):
    def generate_key_from_request(self, request: Request) -> str:
        return request.url.path
