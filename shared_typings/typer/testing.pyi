from __future__ import annotations

from typing import Any, Protocol, Sequence


class _TyperApp(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...


class Result:
    exit_code: int
    exception: BaseException | None


class CliRunner:
    def __init__(self, *, mix_stderr: bool | None = ...) -> None: ...

    def invoke(
        self,
        app: _TyperApp,
        args: Sequence[str] | None = ...,
        *,
        catch_exceptions: bool = ...,
        color: bool | None = ...,
    ) -> Result: ...
