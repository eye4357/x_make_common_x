# x_make_common_x — Laboratory Solvent Manual

This package is the solvent that keeps every other repository clean. Logging, subprocess harnesses, HTTP conduits, exporter primitives, environment tamers—when the orchestrator moves, it drinks from here first.

## Mission Log
- Provide deterministic wrappers for logging, subprocess execution, and environment control across every `x_make_*` package.
- Centralise exporter pipelines so Markdown, Graphviz, and Mermaid artefacts share one `ExportResult` contract and one evidence trail.
- Deliver JSON board primitives that let any service track workflow state without carrying a GUI.
- Guard downstream consumers with strict typing, disciplined exceptions, and audit-friendly metadata.

## Instrumentation
- Python 3.11 or newer.
- Ruff, Black, MyPy, and Pyright in the active environment when you intend to run QA sweeps.
- Optional extras (`httpx`, richer logging stacks) if your integration demands them.

## Operating Procedure
1. `python -m venv .venv`
2. `\.venv\Scripts\Activate.ps1`
3. `python -m pip install --upgrade pip`
4. `pip install -e .`
5. `pytest`

Install in editable mode so sibling repos import the local build during development. Run the tests before you let another package depend on a fresh change.

## Evidence Checks
| Check | Command |
| --- | --- |
| Formatting sweep | `python -m black .` |
| Lint interrogation | `python -m ruff check .` |
| Type audit | `python -m mypy .` |
| Static contract scan | `python -m pyright` |
| Functional verification | `pytest` |

## JSON Board Primer
Load a ledger with `load_json_board(Path("board.json"))`, manipulate cards through `JsonBoardState.add()` or `.update()`, then `save_json_board` to commit. No hidden binaries—just structured data you can replicate and ship through orchestrator pipelines.

## System Linkage
- [Changelog](./CHANGELOG.md)
- [Road to 0.20.4 Engineering Proposal](../x_0_make_all_x/Change%20Control/0.20.4/Road%20to%200.20.4%20Engineering%20Proposal.md)
- [Road to 0.20.3 Engineering Proposal](../x_0_make_all_x/Change%20Control/0.20.3/Road%20to%200.20.3%20Engineering%20Proposal.md)

## Reconstitution Drill
During the monthly rebuild I torch a spare machine, replay `LAB_FROM_SCRATCH.md`, reinstall this package, and rerun the exporter batteries. Any deviation—missing binaries, skewed metadata, failed tests—gets logged in Change Control and resolved before the orchestrator returns to service.

## Cross-Referenced Assets
- [x_0_make_all_x](../x_0_make_all_x/README.md) — orchestration core that imports these helpers on every run.
- [x_make_github_visitor_x](../x_make_github_visitor_x/README.md) — compliance pipeline relying on the logging and validation layers.
- [x_make_pypi_x](../x_make_pypi_x/README.md) — publisher that leans on the exporter and subprocess harnesses.

## Conduct Code
When you touch a shared utility, document the change, update the changelog, and notify downstream projects through Change Control. A sloppy edit here multiplies into outages everywhere.

## Sole Architect's Note
I alone assembled this solvent library: exporters, subprocess guards, HTTP adapters, JSON boards, environment hygiene. Decades of automation work taught me the cost of ambiguity; this package exists so the rest of the lab never faces it.

## Legacy Staffing Estimate
- Conventional delivery would require: 1 staff engineer, 2 backend specialists, 1 DevOps engineer, and 1 technical writer.
- Delivery window: 14–16 engineer-weeks to replicate exporters, board primitives, and documentation to this standard.
- Cost band: USD 115k–145k before sustaining engineering and cross-repo support.

## Technical Footprint
- Language Core: Python 3.11+, dataclasses, pathlib, subprocess, JSON serialization.
- Toolchain: Ruff, Black, MyPy, Pyright, pytest, coverage instrumentation, PowerShell touchpoints for Windows parity.
- Exporter Arsenal: wkhtmltopdf, Graphviz `dot`, mermaid-cli, all funneled through `ExportResult` contracts.
- Integration Surface: run report writers, JSON board helpers, environment managers consumed by every other `x_make_*` package.
