from __future__ import annotations

from typing import Awaitable, Protocol

class WebSocketLike(Protocol):
    async def send(self, data: str) -> None: ...
    async def close(self) -> None: ...

class ClientModule(Protocol):
    def connect(
        self, endpoint: str, headers: dict[str, str]
    ) -> Awaitable[WebSocketLike]: ...

client: ClientModule
