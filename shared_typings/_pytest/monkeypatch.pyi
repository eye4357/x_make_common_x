from __future__ import annotations

from typing import overload

__all__ = ["MonkeyPatch"]

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
    def setenv(self, name: str, value: str, *, prepend: bool = ...) -> None: ...
    def delenv(self, name: str, *, raising: bool = ...) -> None: ...
    def delfirst(self, name: str, *, raising: bool = ...) -> None: ...
    def undo(self) -> None: ...
