"""Reusable scanners for Python entrypoint discovery."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

DEFAULT_NAME_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"^run_[a-z0-9_]+\.py$", re.IGNORECASE),
    re.compile(r"^[a-z0-9_]+_cli\.py$", re.IGNORECASE),
    re.compile(r"^cli_[a-z0-9_]+\.py$", re.IGNORECASE),
    re.compile(r"^main\.py$", re.IGNORECASE),
    re.compile(r"^__main__\.py$"),
)

DEFAULT_EXCLUDE_DIRS: frozenset[str] = frozenset(
    {
        ".git",
        ".hg",
        ".svn",
        "__pycache__",
        ".mypy_cache",
        ".ruff_cache",
        ".pytest_cache",
        ".venv",
        "venv",
        "node_modules",
        "build",
        "dist",
        "artifacts",
        "out",
        "logs",
    }
)


@dataclass(slots=True)
class EntryPointCandidate:
    """Potential runnable entrypoint discovered by heuristics."""

    path: str
    score: float
    reasons: tuple[str, ...]
    size_bytes: int
    sha256: str
    has_main_guard: bool
    has_shebang: bool
    import_hints: tuple[str, ...]


@dataclass(slots=True)
class EntryPointDiscovery:
    """Container for discovery results."""

    root: str
    candidates: tuple[EntryPointCandidate, ...]
    total_files_scanned: int


def _iter_python_files(root: Path, *, exclude_dirs: frozenset[str]) -> Iterator[Path]:
    stack: list[Path] = [root]
    while stack:
        current = stack.pop()
        try:
            iterator = current.iterdir()
        except OSError:
            continue
        for entry in iterator:
            name = entry.name
            if entry.is_dir():
                if name in exclude_dirs or name.startswith("."):
                    continue
                stack.append(entry)
                continue
            if entry.suffix.lower() == ".py":
                yield entry


def _read_text_prefix(path: Path, limit: int = 65_536) -> str:
    try:
        data = path.read_bytes()
    except OSError:
        return ""
    return data[:limit].decode("utf-8", "ignore")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            while chunk := handle.read(8192):
                h.update(chunk)
    except OSError:
        return ""
    return h.hexdigest()


def _main_guard_present(text: str) -> bool:
    return 'if __name__ == "__main__"' in text or "if __name__ == '__main__'" in text


def _shebang_present(text: str) -> bool:
    lines = text.splitlines()
    if not lines:
        return False
    first = lines[0]
    return first.startswith("#!/") and "python" in first.lower()


def _import_hints(text: str) -> tuple[str, ...]:
    hints: list[str] = []
    if "argparse" in text:
        hints.append("argparse")
    if "click" in text:
        hints.append("click")
    if "typer" in text:
        hints.append("typer")
    if "fire" in text:
        hints.append("fire")
    return tuple(sorted(set(hints)))


def _name_based_reasons(
    path: Path, *, patterns: Sequence[re.Pattern[str]]
) -> list[str]:
    name = path.name
    reasons: list[str] = []
    for pattern in patterns:
        if pattern.match(name):
            reasons.append(f"name matches {pattern.pattern}")
    if path.stem.endswith("_runner"):
        reasons.append("name ends with _runner")
    if "run" in path.stem:
        reasons.append("stem contains 'run'")
    return reasons


def scan_python_entrypoints(
    root: Path,
    *,
    name_patterns: Sequence[re.Pattern[str]] | None = None,
    exclude_dirs: frozenset[str] | None = None,
) -> EntryPointDiscovery:
    """Scan *root* for Python entrypoints using heuristics."""

    patterns = tuple(name_patterns or DEFAULT_NAME_PATTERNS)
    excludes = exclude_dirs or DEFAULT_EXCLUDE_DIRS
    absolute_root = root.resolve()
    candidates: list[EntryPointCandidate] = []
    total_files = 0
    for file_path in _iter_python_files(absolute_root, exclude_dirs=excludes):
        total_files += 1
        text = _read_text_prefix(file_path)
        reasons = _name_based_reasons(file_path, patterns=patterns)
        has_main_guard = _main_guard_present(text)
        has_shebang = _shebang_present(text)
        import_hints = _import_hints(text)
        if has_main_guard:
            reasons.append("contains __main__ guard")
        if has_shebang:
            reasons.append("has python shebang")
        if import_hints:
            reasons.append(f"imports {', '.join(import_hints)}")
        if not reasons:
            continue
        score = 1.0 + 0.5 * (len(reasons) - 1)
        size_bytes = 0
        try:
            size_bytes = file_path.stat().st_size
        except OSError:
            size_bytes = 0
        candidate = EntryPointCandidate(
            path=str(file_path.relative_to(absolute_root)),
            score=score,
            reasons=tuple(reasons),
            size_bytes=size_bytes,
            sha256=_sha256(file_path),
            has_main_guard=has_main_guard,
            has_shebang=has_shebang,
            import_hints=import_hints,
        )
        candidates.append(candidate)
    candidates.sort(key=lambda c: (-c.score, c.path))
    return EntryPointDiscovery(
        root=str(absolute_root),
        candidates=tuple(candidates),
        total_files_scanned=total_files,
    )
