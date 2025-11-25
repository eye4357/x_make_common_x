from __future__ import annotations

from typing import Protocol

class WebSocketClientProtocol(Protocol):
    async def recv(self) -> bytes | str: ...
    async def send(self, data: bytes | str) -> None: ...
    async def close(self) -> None: ...
    async def __aenter__(self) -> WebSocketClientProtocol: ...
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: object,
    ) -> bool: ...

class WebSocketConnection(Protocol):
    async def __aenter__(self) -> WebSocketClientProtocol: ...
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: object,
    ) -> bool: ...

def connect(
    uri: str,
    *,
    extra_headers: dict[str, str] | None = ...,
) -> WebSocketConnection: ...

__all__ = [
    "WebSocketClientProtocol",
    "WebSocketConnection",
    "connect",
]
