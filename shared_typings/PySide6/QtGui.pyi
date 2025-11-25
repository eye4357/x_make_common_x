from __future__ import annotations

__all__ = [
    "QColor",
    "QFont",
    "QTextCursor",
]

class QColor:
    def __init__(self, value: str) -> None: ...

class QFont:
    def setUnderline(self, value: bool) -> None: ...

class QTextCursor:
    End: int

    def movePosition(self, operation: int) -> None: ...
