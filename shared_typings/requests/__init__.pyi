from __future__ import annotations

from collections.abc import Iterable, Mapping, MutableMapping
from typing import Any

class Response:
    status_code: int
    headers: Mapping[str, str]

    def json(self) -> Any: ...
    def iter_content(self, chunk_size: int = ...) -> Iterable[bytes]: ...
    def raise_for_status(self) -> None: ...

class Session:
    headers: MutableMapping[str, str]

    def __init__(self) -> None: ...
    def request(
        self,
        method: str,
        url: str,
        *,
        params: Mapping[str, str] | None = ...,
        json: Mapping[str, Any] | None = ...,
        stream: bool = ...,
    ) -> Response: ...

__all__ = ["Response", "Session"]
