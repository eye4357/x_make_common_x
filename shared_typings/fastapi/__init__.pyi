from __future__ import annotations

from typing import Any, Callable, Protocol

__all__ = ["FastAPI", "HTTPException"]


class _RouteDecorator(Protocol):
	def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]: ...


class FastAPI:
	state: Any

	def __init__(self, *args: Any, **kwargs: Any) -> None: ...

	def get(self, path: str, *args: Any, **kwargs: Any) -> _RouteDecorator: ...

	def post(self, path: str, *args: Any, **kwargs: Any) -> _RouteDecorator: ...


class HTTPException(Exception):
	status_code: int
	detail: Any

	def __init__(self, *, status_code: int, detail: Any) -> None: ...
