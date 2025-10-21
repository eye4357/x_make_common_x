"""Shared exporters for PDF and SVG artifacts.

These helpers centralize binary discovery and command execution so every
repository invokes the same pipeline when rendering Markdown, Graphviz, or
Mermaid outputs. Each function returns an :class:`ExportResult` describing the
command that ran, the primary artifact that was produced, and any diagnostic
output captured along the way.
"""

from __future__ import annotations

import contextlib
import os
import shutil
import subprocess
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from .x_logging_utils_x import log_debug, log_info
from .x_subprocess_utils_x import run_command

CommandRunner = Callable[[Sequence[str]], subprocess.CompletedProcess[str]]

# Default search locations for wkhtmltopdf on common platforms.
_DEFAULT_WKHTMLTOPDF_CANDIDATES: tuple[Path, ...] = (
    Path(r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"),
    Path(r"C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe"),
    Path("/usr/local/bin/wkhtmltopdf"),
    Path("/usr/bin/wkhtmltopdf"),
)


def _preferred_binary(
    preferred_path: str | os.PathLike[str] | None,
    *,
    allow_missing: bool,
) -> Path | None:
    if not preferred_path:
        return None
    candidate = Path(preferred_path)
    if candidate.is_file() or allow_missing:
        return candidate
    return None


def _env_binary(env_var: str | None) -> Path | None:
    if not env_var:
        return None
    env_value = os.environ.get(env_var)
    if not env_value:
        return None
    candidate = Path(env_value)
    if candidate.is_file():
        return candidate
    return None


def _first_existing(default_candidates: Sequence[Path] | None) -> Path | None:
    if not default_candidates:
        return None
    for default in default_candidates:
        if default.is_file():
            return default
    return None


@dataclass(slots=True)
class ExportResult:
    """Outcome details for a rendering attempt."""

    exporter: str
    succeeded: bool
    output_path: Path | None
    command: tuple[str, ...]
    stdout: str
    stderr: str
    inputs: Mapping[str, Path]
    binary_path: Path | None
    detail: str | None = None

    def to_metadata(self) -> dict[str, object]:
        """Return a JSON-serialisable payload describing the result."""

        return {
            "exporter": self.exporter,
            "succeeded": self.succeeded,
            "output_path": str(self.output_path) if self.output_path else None,
            "command": list(self.command),
            "stdout": self.stdout,
            "stderr": self.stderr,
            "inputs": {key: str(path) for key, path in self.inputs.items()},
            "binary_path": str(self.binary_path) if self.binary_path else None,
            "detail": self.detail,
        }


def _resolve_binary(
    *,
    preferred_path: str | os.PathLike[str] | None,
    env_var: str | None,
    fallback_names: Sequence[str],
    default_candidates: Sequence[Path] | None = None,
    allow_missing_preferred: bool = False,
) -> Path | None:
    """Resolve a binary path using explicit, env, and PATH lookups."""

    preferred = _preferred_binary(
        preferred_path,
        allow_missing=allow_missing_preferred,
    )
    if preferred is not None:
        return preferred

    env_candidate = _env_binary(env_var)
    if env_candidate is not None:
        return env_candidate

    for name in fallback_names:
        located = shutil.which(name)
        if located:
            return Path(located)

    default_candidate = _first_existing(default_candidates)
    if default_candidate is not None:
        return default_candidate

    return None


def _execute_command(
    command: Sequence[str],
    *,
    runner: CommandRunner | None,
) -> subprocess.CompletedProcess[str]:
    """Run a command via the provided runner or the shared subprocess helper."""

    if runner is not None:
        return runner(tuple(command))
    log_debug("Running exporter command:", " ".join(command))
    return run_command(tuple(command), check=False)


def _write_text(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def export_markdown_to_pdf(  # noqa: PLR0913 - explicit parameters aid clarity
    markdown_text: str,
    *,
    output_dir: Path,
    stem: str,
    wkhtmltopdf_path: str | os.PathLike[str] | None = None,
    runner: CommandRunner | None = None,
    markdown_to_html: Callable[[str], str] | None = None,
    extra_args: Sequence[str] | None = None,
    keep_html: bool = True,
) -> ExportResult:
    """Render Markdown to PDF using wkhtmltopdf."""

    exporter_name = "markdown->pdf"
    output_dir = output_dir.resolve()
    markdown_path = _write_text(output_dir / f"{stem}.md", markdown_text)
    render_md = markdown_to_html or _default_markdown_to_html
    html_content = render_md(markdown_text)
    html_path = _write_text(output_dir / f"{stem}.html", html_content)

    binary = _resolve_binary(
        preferred_path=wkhtmltopdf_path,
        env_var="X_WKHTMLTOPDF_PATH",
        fallback_names=("wkhtmltopdf", "wkhtmltopdf.exe"),
        default_candidates=_DEFAULT_WKHTMLTOPDF_CANDIDATES,
        allow_missing_preferred=runner is not None,
    )
    pdf_path = output_dir / f"{stem}.pdf"
    return _run_wkhtmltopdf(
        exporter=exporter_name,
        binary=binary,
        html_path=html_path,
        pdf_path=pdf_path,
        inputs={"markdown": markdown_path, "html": html_path},
        runner=runner,
        extra_args=extra_args,
        keep_html=keep_html,
    )


def export_html_to_pdf(  # noqa: PLR0913 - explicit parameters aid clarity
    html_text: str,
    *,
    output_dir: Path,
    stem: str,
    wkhtmltopdf_path: str | os.PathLike[str] | None = None,
    runner: CommandRunner | None = None,
    extra_args: Sequence[str] | None = None,
    keep_html: bool = True,
) -> ExportResult:
    """Render raw HTML to PDF using wkhtmltopdf."""

    exporter_name = "html->pdf"
    output_dir = output_dir.resolve()
    html_path = _write_text(output_dir / f"{stem}.html", html_text)
    binary = _resolve_binary(
        preferred_path=wkhtmltopdf_path,
        env_var="X_WKHTMLTOPDF_PATH",
        fallback_names=("wkhtmltopdf", "wkhtmltopdf.exe"),
        default_candidates=_DEFAULT_WKHTMLTOPDF_CANDIDATES,
        allow_missing_preferred=runner is not None,
    )
    pdf_path = output_dir / f"{stem}.pdf"
    return _run_wkhtmltopdf(
        exporter=exporter_name,
        binary=binary,
        html_path=html_path,
        pdf_path=pdf_path,
        inputs={"html": html_path},
        runner=runner,
        extra_args=extra_args,
        keep_html=keep_html,
    )


def export_graphviz_to_svg(  # noqa: PLR0913 - explicit parameters aid clarity
    dot_source: str,
    *,
    output_dir: Path,
    stem: str,
    dot_path: Path | None = None,
    graphviz_path: str | os.PathLike[str] | None = None,
    runner: CommandRunner | None = None,
    extra_args: Sequence[str] | None = None,
    keep_dot: bool = True,
) -> ExportResult:
    """Render Graphviz DOT source to SVG using the ``dot`` binary."""

    exporter_name = "graphviz->svg"
    output_dir = output_dir.resolve()
    dot_path = dot_path or output_dir / f"{stem}.dot"
    _write_text(dot_path, dot_source)
    binary = _resolve_binary(
        preferred_path=graphviz_path,
        env_var="GRAPHVIZ_DOT",
        fallback_names=("dot", "dot.exe"),
        default_candidates=(),
    )
    if binary is None:
        detail_missing = (
            "graphviz 'dot' binary not found; install Graphviz or set GRAPHVIZ_DOT"
        )
        return ExportResult(
            exporter=exporter_name,
            succeeded=False,
            output_path=None,
            command=(),
            stdout="",
            stderr="",
            inputs={"dot": dot_path},
            binary_path=None,
            detail=detail_missing,
        )

    svg_path = output_dir / f"{stem}.svg"
    command: list[str] = [str(binary), "-Tsvg", str(dot_path), "-o", str(svg_path)]
    if extra_args:
        command[1:1] = [str(arg) for arg in extra_args]
    completed = _execute_command(command, runner=runner)
    stdout_raw = cast("str | None", getattr(completed, "stdout", None))
    stderr_raw = cast("str | None", getattr(completed, "stderr", None))
    stdout = stdout_raw or ""
    stderr = stderr_raw or ""
    succeeded = completed.returncode == 0 and svg_path.exists()
    detail: str | None = None if succeeded else "dot execution failed"
    if not keep_dot and svg_path.exists():
        with contextlib.suppress(OSError):
            dot_path.unlink()
    return ExportResult(
        exporter=exporter_name,
        succeeded=succeeded,
        output_path=svg_path if succeeded else None,
        command=tuple(command),
        stdout=stdout,
        stderr=stderr,
        inputs={"dot": dot_path},
        binary_path=binary,
        detail=detail,
    )


def export_mermaid_to_svg(  # noqa: PLR0913 - explicit parameters aid clarity
    mermaid_source: str,
    *,
    output_dir: Path,
    stem: str,
    mermaid_cli_path: str | os.PathLike[str] | None = None,
    runner: CommandRunner | None = None,
    extra_args: Sequence[str] | None = None,
) -> ExportResult:
    """Render Mermaid source to SVG using ``mmdc`` (mermaid-cli)."""

    exporter_name = "mermaid->svg"
    output_dir = output_dir.resolve()
    mmd_path = _write_text(output_dir / f"{stem}.mmd", mermaid_source)
    binary = _resolve_binary(
        preferred_path=mermaid_cli_path,
        env_var="MMDC",
        fallback_names=("mmdc", "mmdc.cmd", "mmdc.ps1"),
        default_candidates=(),
    )
    if binary is None:
        detail_missing = "mermaid-cli 'mmdc' not found; install mermaid-cli or set MMDC"
        return ExportResult(
            exporter=exporter_name,
            succeeded=False,
            output_path=None,
            command=(),
            stdout="",
            stderr="",
            inputs={"mermaid": mmd_path},
            binary_path=None,
            detail=detail_missing,
        )

    svg_path = output_dir / f"{stem}.svg"
    command: list[str] = [str(binary), "-i", str(mmd_path), "-o", str(svg_path)]
    if extra_args:
        command.extend(str(arg) for arg in extra_args)
    completed = _execute_command(command, runner=runner)
    stdout_raw = cast("str | None", getattr(completed, "stdout", None))
    stderr_raw = cast("str | None", getattr(completed, "stderr", None))
    stdout = stdout_raw or ""
    stderr = stderr_raw or ""
    succeeded = completed.returncode == 0 and svg_path.exists()
    detail: str | None = None if succeeded else "mmdc execution failed"
    return ExportResult(
        exporter=exporter_name,
        succeeded=succeeded,
        output_path=svg_path if succeeded else None,
        command=tuple(command),
        stdout=stdout,
        stderr=stderr,
        inputs={"mermaid": mmd_path},
        binary_path=binary,
        detail=detail,
    )


def _default_markdown_to_html(markdown_text: str) -> str:
    """Render Markdown to HTML using python-markdown when available."""

    try:
        module = __import__("markdown")
        renderer = cast(
            "Callable[[str], object] | None",
            getattr(module, "markdown", None),
        )
        if renderer is not None:
            rendered = renderer(markdown_text or "")
            return str(rendered)
    except Exception:  # noqa: BLE001 - fall through to minimal HTML
        log_info("python-markdown unavailable; falling back to <pre> wrapper for HTML")
    escaped = (markdown_text or "").replace("<", "&lt;").replace(">", "&gt;")
    return f"<pre>{escaped}</pre>"


def _run_wkhtmltopdf(  # noqa: PLR0913 - explicit options keep callsites obvious
    *,
    exporter: str,
    binary: Path | None,
    html_path: Path,
    pdf_path: Path,
    inputs: Mapping[str, Path],
    runner: CommandRunner | None,
    extra_args: Sequence[str] | None,
    keep_html: bool,
) -> ExportResult:
    if binary is None:
        detail_missing = (
            "wkhtmltopdf binary not found; install it or set X_WKHTMLTOPDF_PATH"
        )
        return ExportResult(
            exporter=exporter,
            succeeded=False,
            output_path=None,
            command=(),
            stdout="",
            stderr="",
            inputs=dict(inputs),
            binary_path=None,
            detail=detail_missing,
        )

    command: list[str] = [str(binary)]
    if extra_args:
        command.extend(str(arg) for arg in extra_args)
    command.extend((str(html_path), str(pdf_path)))
    completed = _execute_command(command, runner=runner)
    stdout_raw = cast("str | None", getattr(completed, "stdout", None))
    stderr_raw = cast("str | None", getattr(completed, "stderr", None))
    stdout = stdout_raw or ""
    stderr = stderr_raw or ""
    succeeded = completed.returncode == 0 and pdf_path.exists()
    detail: str | None = None if succeeded else "wkhtmltopdf execution failed"
    if not keep_html and pdf_path.exists():
        with contextlib.suppress(OSError):
            html_path.unlink()
    return ExportResult(
        exporter=exporter,
        succeeded=succeeded,
        output_path=pdf_path if succeeded else None,
        command=tuple(command),
        stdout=stdout,
        stderr=stderr,
        inputs=dict(inputs),
        binary_path=binary,
        detail=detail,
    )


__all__ = [
    "CommandRunner",
    "ExportResult",
    "export_graphviz_to_svg",
    "export_html_to_pdf",
    "export_markdown_to_pdf",
    "export_mermaid_to_svg",
]
