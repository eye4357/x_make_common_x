# x_make_common_x — Control Room Lab Notes

> "When every cook uses the same lab gear, quality stops fluctuating. This repository delivers that gear."

## Manifesto
x_make_common_x houses the shared utilities—logging, subprocess control, HTTP clients, environment helpers—that every other repo in the operation relies on. This is the solvent that dissolves duplication and keeps the whole Road to 0.20.1 campaign aligned.

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

## Distribution Chain
- [Changelog](./CHANGELOG.md)
- [Road to 0.20.1 Control Room Ledger](../x_0_make_all_x/Change%20Control/0.20.1/Road%20to%200.20.1%20Engineering%20Proposal.md)
- [Road to 0.20.1 Engineering Proposal](../x_0_make_all_x/Change%20Control/0.20.1/Road%20to%200.20.1%20Engineering%20Proposal.md)

## Cross-Linked Intelligence
- [x_0_make_all_x](../x_0_make_all_x/README.md) — orchestrator expects these helpers on every run
- [x_make_github_visitor_x](../x_make_github_visitor_x/README.md) — the compliance visitor that consumes common telemetry and logging utilities
- [x_make_pypi_x](../x_make_pypi_x/README.md) — publishing pipeline wired directly into these helpers

## Lab Etiquette
When you alter shared utilities, update the changelog and alert the Downstream repos via the Change Control index. Half measures here create cascading failures everywhere else.
