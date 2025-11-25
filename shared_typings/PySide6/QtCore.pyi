from __future__ import annotations

__all__ = [
    "QObject",
    "QPoint",
    "QRunnable",
    "QThread",
    "QThreadPool",
    "Signal",
    "QTimer",
    "Qt",
]

class Signal:
    def __init__(self, *types: type[object]) -> None: ...
    def connect(self, slot: object) -> None: ...
    def emit(self, *args: object) -> None: ...

class QObject:
    def __init__(self, parent: QObject | None = ...) -> None: ...
    def deleteLater(self) -> None: ...
    def blockSignals(self, block: bool) -> None: ...

class QPoint:
    def __init__(self, x: int = ..., y: int = ...) -> None: ...
    def x(self) -> int: ...
    def y(self) -> int: ...

class QThread(QObject):
    finished: Signal

    def __init__(self, parent: QObject | None = ...) -> None: ...
    def start(self) -> None: ...
    def quit(self) -> None: ...
    def wait(self, msecs: int | None = ...) -> bool: ...
    def isRunning(self) -> bool: ...

class QRunnable(QObject):
    def __init__(self) -> None: ...
    def setAutoDelete(self, auto_delete: bool) -> None: ...

class QThreadPool(QObject):
    def __init__(self, parent: QObject | None = ...) -> None: ...
    def start(self, runnable: QRunnable) -> None: ...
    def clear(self) -> None: ...
    def waitForDone(self, msecs: int | None = ...) -> None: ...
    def activeThreadCount(self) -> int: ...

class _ItemDataRole:
    DisplayRole: int
    UserRole: int
    ToolTipRole: int

class _ItemFlag:
    ItemIsEditable: int

class _AlignmentFlag:
    AlignLeft: int
    AlignRight: int
    AlignHCenter: int
    AlignVCenter: int
    AlignCenter: int
    AlignTop: int

class _CheckState:
    Unchecked: int
    PartiallyChecked: int
    Checked: int

class _Orientation:
    Horizontal: int
    Vertical: int

class _ContextMenuPolicy:
    CustomContextMenu: int

class _QtNamespace:
    AlignLeft: int
    AlignVCenter: int
    AlignCenter: int
    UserRole: int
    ItemIsSelectable: int
    ItemIsEnabled: int
    ScrollBarAsNeeded: int
    ItemDataRole: type[_ItemDataRole]
    ItemFlag: type[_ItemFlag]
    AlignmentFlag: type[_AlignmentFlag]
    CheckState: type[_CheckState]
    Orientation: type[_Orientation]
    ContextMenuPolicy: type[_ContextMenuPolicy]

class QTimer(QObject):
    timeout: Signal

    def __init__(self, parent: QObject | None = ...) -> None: ...
    def setInterval(self, msec: int) -> None: ...
    def start(self, msec: int | None = ...) -> None: ...
    def stop(self) -> None: ...
    @staticmethod
    def singleShot(msec: int, slot: object) -> None: ...

Qt: _QtNamespace
