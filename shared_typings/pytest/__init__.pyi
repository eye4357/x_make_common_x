from __future__ import annotations

from types import ModuleType
from typing import (
    Callable,
    Generic,
    NoReturn,
    ParamSpec,
    Sequence,
    Tuple,
    TypeVar,
    overload,
)

__all__ = [
    "MonkeyPatch",
    "CaptureFixture",
    "fixture",
    "importorskip",
    "mark",
    "skip",
    "raises",
]

class MonkeyPatch:
    @overload
    def setattr(
        self,
        target: object,
        name: str,
        value: object,
        *,
        raising: bool = ...,
    ) -> None: ...
    @overload
    def setattr(
        self,
        target: str,
        value: object,
        *,
        raising: bool = ...,
    ) -> None: ...
    def setitem(self, mapping: object, name: str, value: object) -> None: ...
    def setenv(self, name: str, value: str, *, prepend: bool = ...) -> None: ...
    def delenv(self, name: str, *, raising: bool = ...) -> None: ...
    def undo(self) -> None: ...

_P = ParamSpec("_P")
_R = TypeVar("_R")
_E = TypeVar("_E", bound=BaseException)
_AnyStr = TypeVar("_AnyStr", bound=str | bytes)

class _MarkDecorator:
    def parametrize(
        self,
        argnames: str | Sequence[str],
        argvalues: Sequence[Tuple[object, ...] | object],
        *,
        ids: Sequence[str] | None = ...,
        indirect: bool | Sequence[str] = ...,
    ) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]: ...

class _MarkModule:
    def parametrize(
        self,
        argnames: str | Sequence[str],
        argvalues: Sequence[Tuple[object, ...] | object],
        *,
        ids: Sequence[str] | None = ...,
        indirect: bool | Sequence[str] = ...,
    ) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]: ...
    def __call__(self, func: Callable[_P, _R]) -> Callable[_P, _R]: ...
    def skip(
        self,
        reason: str | None = ...,
    ) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]: ...

mark: _MarkModule

class _ExceptionInfo(Generic[_E]):
    value: _E

class _RaisesContext(Generic[_E]):
    def __enter__(self) -> _ExceptionInfo[_E]: ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: object | None,
    ) -> bool: ...

def raises(
    expected_exception: type[_E] | tuple[type[_E], ...],
    *,
    match: str | None = ...,
) -> _RaisesContext[_E]: ...
class CaptureResult(Generic[_AnyStr]):
    out: _AnyStr
    err: _AnyStr

class CaptureFixture(Generic[_AnyStr]):
    def readouterr(self) -> CaptureResult[_AnyStr]: ...

def importorskip(module_name: str, *, reason: str | None = ...) -> ModuleType: ...
def skip(reason: str | None = ..., *, allow_module_level: bool = ...) -> NoReturn: ...
def fixture(
    function: Callable[_P, _R] | None = None,
    *,
    scope: str | None = ...,
    params: Sequence[object] | None = ...,
    autouse: bool | None = ...,
    ids: Sequence[str] | Callable[[object], str] | None = ...,
    name: str | None = ...,
) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]: ...
