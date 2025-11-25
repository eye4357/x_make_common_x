from __future__ import annotations

from typing import Any, Callable

__all__ = ["Depends", "Header"]


def Depends(dependency: Callable[..., Any] | None = ..., *args: Any, **kwargs: Any) -> Any: ...


def Header(
    default: Any = ...,
    *,
    alias: str | None = ...,
    convert_underscores: bool = ...,
    **kwargs: Any,
) -> Any: ...
