from collections.abc import Callable

from typing import Protocol

__all__ = [
    "Argument",
    "BadParameter",
    "Option",
    "Typer",
    "echo",
    "get_click_type",
]

class _CallableReturn(Protocol):
    def __call__(self, *args: object, **kwargs: object) -> object: ...

class BadParameter(ValueError):
    param_hint: str | None

class Option:  # minimal click.Option surface
    def __init__(self, *args: object, **kwargs: object) -> None: ...

class Argument:  # minimal click.Argument surface
    def __init__(self, *args: object, **kwargs: object) -> None: ...

class Typer:
    def __init__(self, *args: object, **kwargs: object) -> None: ...
    def callback(self, func: _CallableReturn) -> _CallableReturn: ...
    def command(
        self, *args: object, **kwargs: object
    ) -> Callable[[_CallableReturn], _CallableReturn]: ...
    def __call__(self, *args: object, **kwargs: object) -> object: ...

def echo(
    value: object, *, color: bool | None = ..., err: bool | None = ...
) -> None: ...
def get_click_type(value: object) -> object: ...
