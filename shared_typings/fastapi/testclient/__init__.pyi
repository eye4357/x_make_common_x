from __future__ import annotations

from collections.abc import Mapping
from typing import Any

class TestClient:
    def __init__(self, app: Any) -> None: ...
    def get(
        self,
        path: str,
        *,
        headers: Mapping[str, str] | None = ...,
    ) -> Any: ...
    def post(
        self,
        path: str,
        *,
        json: Any | None = ...,
        headers: Mapping[str, str] | None = ...,
    ) -> Any: ...
    def close(self) -> None: ...
