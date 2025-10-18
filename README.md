# x_make_common_x — Control Room Lab Notes

> "Consistency is chemistry. Measure, refine, and the yield stays pure."

## Manifesto
x_make_common_x houses the shared utilities—logging, subprocess control, HTTP clients, environment helpers—that every other repo in the operation relies on. This solvent dissolves duplication and keeps the Road to 0.20.4 campaign aligned.

## 0.20.4 Command Sequence
Version 0.20.4 loads the exporter arsenal into this toolkit. `export_markdown_to_pdf`, `export_graphviz_to_svg`, and `export_mermaid_to_svg` now drive every documentation rig through a single `ExportResult` contract, resolving binaries once, logging stdout/stderr, and degrading cleanly when wkhtmltopdf, Graphviz, or mermaid-cli are missing. The Kanban evidence trail finally holds deterministic paths for every PDF and SVG we emit.

## Ingredients
- Python 3.11+
- Ruff, Black, MyPy, and Pyright for code hygiene
- Optional extras for downstream integrations (httpx, rich logging stacks) when the lab demands them

## Cook Instructions
1. `python -m venv .venv`
2. `.\.venv\Scripts\Activate.ps1`
3. `python -m pip install --upgrade pip`
4. `pip install -e .` to expose the shared package locally
5. `pytest` to confirm the utilities behave before you drop them into other repos

## Quality Assurance
| Check | Command |
| --- | --- |
| Formatting sweep | `python -m black .`
| Lint interrogation | `python -m ruff check .`
| Type audit | `python -m mypy .`
| Static contract scan | `python -m pyright`
| Functional verification | `pytest`

## JSON Board Primer
The new board helpers let any service capture task flow as structured JSON. Load a ledger with `load_json_board(Path("board.json"))`, mutate through `JsonBoardState.add()` or `.update()`, then `save_json_board` to commit the batch. No binaries, no surprises—just data you can audit, replicate, and ship anywhere in the pipeline.

## Distribution Chain
- [Changelog](./CHANGELOG.md)
- [Road to 0.20.4 Engineering Proposal](../x_0_make_all_x/Change%20Control/0.20.4/Road%20to%200.20.4%20Engineering%20Proposal.md)
- [Road to 0.20.3 Engineering Proposal](../x_0_make_all_x/Change%20Control/0.20.3/Road%20to%200.20.3%20Engineering%20Proposal.md)

## Reconstitution Drill
The monthly lab rebuild incinerates a spare workstation and walks the `lab.md` script from bare metal. x_make_common_x must rebuild clean: rehydrate the virtualenv, reinstall exporters, run the test matrix, and capture any deviation in these docs and the Change Control ledger. If the drill finds drift, fix it before you touch production.

## Cross-Linked Intelligence
- [x_0_make_all_x](../x_0_make_all_x/README.md) — orchestrator expects these helpers on every run
- [x_make_github_visitor_x](../x_make_github_visitor_x/README.md) — the compliance visitor that consumes common telemetry and logging utilities
- [x_make_pypi_x](../x_make_pypi_x/README.md) — publishing pipeline wired directly into these helpers

## Lab Etiquette
When you alter shared utilities, update the changelog and alert the Downstream repos via the Change Control index. Half measures here create cascading failures everywhere else.

## Sole Architect Profile
- One architect forged this library of solvents. I author every exporter, subprocess guard, and telemetry conduit by hand, aligning the entire lab around a single mental model. My experience spans decades of Python infrastructure, report automation, and failure-mode analysis.
- I operate as benevolent dictator: roadmap, implementation, and documentation all route through me, ensuring no ambiguity, no committee drift.

## Legacy Workforce Costing
- Traditional-shop estimate: 1 staff engineer to lead, 2 mid-level backend engineers, 1 DevOps specialist, and 1 technical writer to tame the support matrix.
- Timeline: 14-16 engineer-weeks to recreate exporter parity, environment helpers, and board primitives, not counting tribal knowledge transfer.
- Budget signal: USD 115k–145k for the initial build cycle, before sustaining engineering and cross-repo support costs.

## Techniques and Proficiencies
- Command of Python platform tooling, hermetic packaging, and cross-repo dependency architecture; I keep API surfaces stable while shipping new exporters.
- Strong documentation and governance instincts—Change Control, disaster drills, and telemetry contracts all originate from the same pen.
- Proficient in shaping automation ecosystems solo, from kernel-level environment hygiene to human-readable runbooks.

## Stack Cartography
- Language Core: Python 3.11+, dataclasses, pathlib, subprocess, JSON serialization.
- Tooling Discipline: Ruff, Black, MyPy, Pyright, pytest, coverage hooks, PowerShell touchpoints for Windows parity.
- Exporter Arsenal: wkhtmltopdf, Graphviz `dot`, mermaid-cli, all orchestrated through shared `ExportResult` contracts.
- Integration Surface: Telemetry emitters, JSON board helpers, environment management utilities consumed by every other `x_make_*` package.
