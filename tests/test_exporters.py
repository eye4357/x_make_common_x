from __future__ import annotations

from pathlib import Path
from subprocess import CompletedProcess
from typing import TYPE_CHECKING, cast

# ruff: noqa: S101 - pytest prefers assert statements for readability

if TYPE_CHECKING:
    from collections.abc import Sequence

    import pytest

import x_make_common_x.exporters as exporters_module
from x_make_common_x.exporters import (
    export_graphviz_to_svg,
    export_html_to_pdf,
    export_markdown_to_pdf,
    export_mermaid_to_svg,
)


def _stub_which(_name: str) -> str | None:
    return None


def _completed(
    command: Sequence[str],
    *,
    stdout: str = "",
    stderr: str = "",
    returncode: int = 0,
) -> CompletedProcess[str]:
    return CompletedProcess(list(command), returncode, stdout=stdout, stderr=stderr)


def _write_from_command(command: Sequence[str], *, flag: str | None = None) -> Path:
    cmd = list(command)
    if flag is None:
        target = Path(cmd[-1])
    else:
        try:
            idx = cmd.index(flag)
        except ValueError as exc:
            message = f"flag {flag!r} not found in command {cmd!r}"
            raise AssertionError(message) from exc
        target = Path(cmd[idx + 1])
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("artifact", encoding="utf-8")
    return target


def test_export_markdown_to_pdf_missing_binary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("X_WKHTMLTOPDF_PATH", str(tmp_path / "missing.exe"))
    shutil_module = cast("object", getattr(exporters_module, "shutil", None))
    assert shutil_module is not None
    monkeypatch.setattr(shutil_module, "which", _stub_which)
    monkeypatch.setattr(
        exporters_module,
        "_DEFAULT_WKHTMLTOPDF_CANDIDATES",
        (),
        raising=False,
    )

    result = export_markdown_to_pdf(
        "# Heading",
        output_dir=tmp_path,
        stem="report",
        wkhtmltopdf_path=None,
    )

    assert result.succeeded is False
    assert result.output_path is None
    assert "wkhtmltopdf" in (result.detail or "")
    assert result.inputs["markdown"].exists()
    assert result.inputs["html"].exists()


def test_export_markdown_to_pdf_success_with_stub(tmp_path: Path) -> None:
    def runner(command: Sequence[str]) -> CompletedProcess[str]:
        _write_from_command(command)
        return _completed(command, stdout="ok")

    result = export_markdown_to_pdf(
        "# Heading",
        output_dir=tmp_path,
        stem="report",
        wkhtmltopdf_path=tmp_path / "wkhtmltopdf.exe",
        runner=runner,
    )

    assert result.succeeded is True
    assert result.output_path == tmp_path / "report.pdf"
    assert result.command[-1].endswith("report.pdf")
    assert result.stdout == "ok"


def test_export_graphviz_to_svg_missing_binary(tmp_path: Path) -> None:
    result = export_graphviz_to_svg("digraph { A -> B }", output_dir=tmp_path, stem="g")

    assert result.succeeded is False
    assert result.output_path is None
    assert "graphviz" in (result.detail or "")
    assert result.inputs["dot"].exists()


def test_export_graphviz_to_svg_success_with_stub(tmp_path: Path) -> None:
    def runner(command: Sequence[str]) -> CompletedProcess[str]:
        _write_from_command(command, flag="-o")
        return _completed(command, stdout="svg ok")

    dot_binary = tmp_path / "dot.exe"
    dot_binary.write_text("binary", encoding="utf-8")

    result = export_graphviz_to_svg(
        "digraph { A -> B }",
        output_dir=tmp_path,
        stem="graph",
        graphviz_path=dot_binary,
        runner=runner,
    )

    assert result.succeeded is True
    assert result.output_path == tmp_path / "graph.svg"
    assert "graph.svg" in result.command[-1]
    assert result.stdout == "svg ok"


def test_export_html_to_pdf_success_with_stub(tmp_path: Path) -> None:
    def runner(command: Sequence[str]) -> CompletedProcess[str]:
        _write_from_command(command)
        return _completed(command, stdout="ok")

    result = export_html_to_pdf(
        "<h1>Hello</h1>",
        output_dir=tmp_path,
        stem="report",
        wkhtmltopdf_path=tmp_path / "wkhtmltopdf.exe",
        runner=runner,
    )

    assert result.succeeded is True
    assert result.output_path == tmp_path / "report.pdf"


def test_export_mermaid_to_svg_missing_binary(tmp_path: Path) -> None:
    result = export_mermaid_to_svg("graph TD; A-->B;", output_dir=tmp_path, stem="m")

    assert result.succeeded is False
    assert result.output_path is None
    assert "mermaid" in (result.detail or "")
    assert result.inputs["mermaid"].exists()


def test_export_mermaid_to_svg_success_with_stub(tmp_path: Path) -> None:
    def runner(command: Sequence[str]) -> CompletedProcess[str]:
        _write_from_command(command, flag="-o")
        return _completed(command, stdout="mmd ok")

    mmdc = tmp_path / "mmdc.cmd"
    mmdc.write_text("binary", encoding="utf-8")

    result = export_mermaid_to_svg(
        "graph TD; A-->B;",
        output_dir=tmp_path,
        stem="flow",
        mermaid_cli_path=mmdc,
        runner=runner,
    )

    assert result.succeeded is True
    assert result.output_path == tmp_path / "flow.svg"
    assert result.command[-1].endswith("flow.svg")
    assert result.stdout == "mmd ok"
