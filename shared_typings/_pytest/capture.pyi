from __future__ import annotations

from typing import Generic, TypeVar

__all__ = ["CaptureFixture", "CaptureResult"]

_T = TypeVar("_T")

class CaptureResult(Generic[_T]):
    out: _T
    err: _T

class CaptureFixture(Generic[_T]):
    def readouterr(self) -> CaptureResult[_T]: ...
