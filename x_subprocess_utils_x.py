"""Secure subprocess helpers."""

from __future__ import annotations

import os
import subprocess
from typing import Iterable, Mapping, Sequence  # noqa: UP035

from .x_logging_utils_x import log_debug, log_info


class CommandError(RuntimeError):
    def __init__(
        self,
        argv: Sequence[str],
        returncode: int,
        stdout: str,
        stderr: str,
    ) -> None:
        message = (
            "Command "
            + " ".join(argv)
            + f" failed with exit code {returncode}: {stderr or stdout}"
        )
        super().__init__(message)
        self.argv = tuple(argv)
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


_TRUTHY = {"1", "true", "yes", "on"}


def _is_test_mode() -> bool:
    env = os.environ
    explicit = env.get("X_MAKE_TEST_MODE")
    if explicit is not None:
        return explicit.lower() in _TRUTHY
    if env.get("PYTEST_CURRENT_TEST"):
        return True
    return bool(env.get("PYTEST_RUN_CONFIG"))


def _format_command(argv: Sequence[str]) -> str:
    if not argv:
        return "<empty command>"
    try:
        return subprocess.list2cmdline(list(argv))
    except Exception:  # noqa: BLE001 - defensive fallback
        return " ".join(str(part) for part in argv)


def run_command(
    args: Iterable[str],
    *,
    check: bool = True,
    env: Mapping[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    argv = list(args)
    log_debug("Running command:", " ".join(argv))
    if _is_test_mode():
        rendered = _format_command(argv)
        log_info("[test-mode] automation command:", rendered)
        print(f"[test-mode] $ {rendered}")
    completed = subprocess.run(  # noqa: S603 - argv built from trusted call sites
        argv,
        capture_output=True,
        text=True,
        check=False,
        env=dict(env) if env is not None else None,
    )
    if check and completed.returncode != 0:
        raise CommandError(
            argv,
            completed.returncode,
            completed.stdout,
            completed.stderr,
        )
    return completed


__all__ = ["CommandError", "run_command"]
