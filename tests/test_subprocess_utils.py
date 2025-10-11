from __future__ import annotations

import subprocess
import typing
from subprocess import CompletedProcess
from typing import TYPE_CHECKING, ParamSpec, TypeVar, cast

import pytest

from x_make_common_x.x_subprocess_utils_x import run_command

if TYPE_CHECKING:
    from collections.abc import Callable

    from _pytest.capture import CaptureFixture
else:
    Callable = typing.Callable

_P = ParamSpec("_P")
_T = TypeVar("_T")


if TYPE_CHECKING:

    def typed_fixture(func: Callable[_P, _T]) -> Callable[_P, _T]: ...

else:

    def typed_fixture(func: Callable[_P, _T]) -> Callable[_P, _T]:
        decorated = pytest.fixture()(func)
        return cast("Callable[_P, _T]", decorated)


class ExpectationFailedError(AssertionError):
    """Raised when a test expectation fails without using assert statements."""


def expect(condition: object, message: str) -> None:
    if not bool(condition):
        raise ExpectationFailedError(message)


# Pytest's fixture decorator is dynamically typed; suppress strict typing complaint.
@typed_fixture
def fake_run(monkeypatch: pytest.MonkeyPatch) -> list[list[str]]:
    calls: list[list[str]] = []

    def _fake_run(
        argv: list[str],
        **_kwargs: object,
    ) -> CompletedProcess[str]:
        calls.append(list(argv))
        return CompletedProcess(argv, 0, "", "")

    monkeypatch.setattr(subprocess, "run", _fake_run)
    return calls


def test_run_command_echoes_when_explicit_test_mode(
    monkeypatch: pytest.MonkeyPatch,
    capsys: CaptureFixture[str],
    fake_run: list[list[str]],
) -> None:
    monkeypatch.setenv("X_MAKE_TEST_MODE", "1")

    run_command(["python", "--version"])

    captured = capsys.readouterr()
    expect(
        "[test-mode] $" in captured.out,
        "expected test-mode banner in captured output",
    )
    expect(
        "python" in captured.out,
        "expected command name in captured output",
    )
    expect(
        fake_run[0] == ["python", "--version"],
        "unexpected subprocess invocation",
    )


def test_run_command_suppresses_echo_when_explicitly_disabled(
    monkeypatch: pytest.MonkeyPatch,
    capsys: CaptureFixture[str],
    fake_run: list[list[str]],
) -> None:
    monkeypatch.setenv("X_MAKE_TEST_MODE", "0")

    run_command(["python", "--version"])

    captured = capsys.readouterr()
    expect(
        "[test-mode] $" not in captured.out,
        "test-mode banner should be suppressed when disabled",
    )
    expect(
        fake_run[0] == ["python", "--version"],
        "unexpected subprocess invocation",
    )
