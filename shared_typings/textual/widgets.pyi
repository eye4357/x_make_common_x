from typing import Any, Protocol

class Styles(Protocol):
    border: Any
    opacity: float

class Widget:
    styles: Styles

    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class Static(Widget):
    def update(self, content: str) -> None: ...

class Footer(Widget): ...
class Header(Widget): ...

class DataTable(Widget):
    cursor_type: str

    def clear(self, *, columns: bool = ...) -> None: ...
    def add_columns(self, *columns: str) -> None: ...
    def add_row(self, *values: Any, key: str | None = ...) -> None: ...

class Input(Widget):
    placeholder: str
    value: str

    def disable(self) -> None: ...
    def enable(self) -> None: ...

    class Submitted:
        input: Input

class Button(Widget):
    disabled: bool

    def disable(self) -> None: ...
    def enable(self) -> None: ...

    class Pressed:
        button: Button

class TextLog(Widget):
    border_title: str

    def write(self, message: str) -> None: ...
    def clear(self) -> None: ...

__all__ = [
    "Button",
    "DataTable",
    "Footer",
    "Header",
    "Input",
    "Static",
    "TextLog",
]
