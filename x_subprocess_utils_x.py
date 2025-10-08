"""Secure subprocess helpers."""

from __future__ import annotations

import subprocess
from typing import Iterable, Sequence  # noqa: UP035

from .x_logging_utils_x import log_debug


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


def run_command(
    args: Iterable[str],
    *,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    argv = list(args)
    log_debug("Running command:", " ".join(argv))
    completed = subprocess.run(  # noqa: S603 - argv built from trusted call sites
        argv,
        capture_output=True,
        text=True,
        check=False,
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
