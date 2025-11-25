import os
import subprocess
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import TypeAlias

CommandRunner: TypeAlias = Callable[[Sequence[str]], subprocess.CompletedProcess[str]]

class ExportResult:
    exporter: str
    succeeded: bool
    output_path: Path | None
    command: tuple[str, ...]
    stdout: str
    stderr: str
    inputs: Mapping[str, Path]
    binary_path: Path | None
    detail: str | None

    def __init__(
        self,
        exporter: str,
        succeeded: bool,
        output_path: Path | None,
        command: tuple[str, ...],
        stdout: str,
        stderr: str,
        inputs: Mapping[str, Path],
        binary_path: Path | None,
        detail: str | None = ...,
    ) -> None: ...
    def to_metadata(self) -> dict[str, object]: ...

def export_markdown_to_pdf(
    markdown_text: str,
    *,
    output_dir: Path,
    stem: str,
    wkhtmltopdf_path: str | os.PathLike[str] | None = ...,
    runner: CommandRunner | None = ...,
    markdown_to_html: Callable[[str], str] | None = ...,
    extra_args: Sequence[str] | None = ...,
    keep_html: bool = ...,
) -> ExportResult: ...
def export_html_to_pdf(
    html_text: str,
    *,
    output_dir: Path,
    stem: str,
    wkhtmltopdf_path: str | os.PathLike[str] | None = ...,
    runner: CommandRunner | None = ...,
    extra_args: Sequence[str] | None = ...,
    keep_html: bool = ...,
) -> ExportResult: ...
def export_graphviz_to_svg(
    dot_source: str,
    *,
    output_dir: Path,
    stem: str,
    dot_path: Path | None = ...,
    graphviz_path: str | os.PathLike[str] | None = ...,
    runner: CommandRunner | None = ...,
    extra_args: Sequence[str] | None = ...,
    keep_dot: bool = ...,
) -> ExportResult: ...
def export_mermaid_to_svg(
    mermaid_source: str,
    *,
    output_dir: Path,
    stem: str,
    mermaid_cli_path: str | os.PathLike[str] | None = ...,
    runner: CommandRunner | None = ...,
    extra_args: Sequence[str] | None = ...,
) -> ExportResult: ...
