import subprocess
from collections.abc import Iterable, Mapping, Sequence

class CommandError(RuntimeError):
    argv: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str

    def __init__(
        self,
        argv: Sequence[str],
        returncode: int,
        stdout: str,
        stderr: str,
    ) -> None: ...

def run_command(
    args: Iterable[str],
    *,
    check: bool = ...,
    env: Mapping[str, str] | None = ...,
) -> subprocess.CompletedProcess[str]: ...

__all__ = [
    "CommandError",
    "run_command",
]
