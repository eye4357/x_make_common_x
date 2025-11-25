from __future__ import annotations

from typing import Callable, Mapping, MutableMapping, Sequence

__all__ = [
    "AsyncClient",
    "MockTransport",
    "Request",
    "RequestError",
    "Response",
    "URL",
]

class RequestError(Exception):
    request: object

class Response:
    status_code: int
    content: bytes

    def json(self) -> object: ...
    def raise_for_status(self) -> None: ...

class AsyncClient:
    def __init__(self, *args: object, **kwargs: object) -> None: ...
    async def aclose(self) -> None: ...
    async def get(
        self,
        url: str,
        *,
        params: Mapping[str, object] | None = ...,
        headers: Mapping[str, str] | None = ...,
    ) -> Response: ...
    async def post(
        self,
        url: str,
        *,
        data: MutableMapping[str, object] | Sequence[tuple[str, object]] | None = ...,
        json: object = ...,
        headers: Mapping[str, str] | None = ...,
    ) -> Response: ...
    async def delete(
        self, url: str, *, headers: Mapping[str, str] | None = ...
    ) -> Response: ...

class Request:
    method: str
    url: "URL"
    headers: Mapping[str, str] | None
    content: bytes

    def __init__(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str] | None = ...,
        content: object = ...,
    ) -> None: ...

class URL:
    def __init__(self, url: str) -> None: ...
    def __str__(self) -> str: ...

class MockTransport:
    def __init__(
        self, handler: Callable[[Request], Response] | None = ..., **kwargs: object
    ) -> None: ...
