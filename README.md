# x_make_common_x — Control Room Lab Notes

> "Consistency is chemistry. Measure, refine, and the yield stays pure."

## Manifesto
x_make_common_x houses the shared utilities—logging, subprocess control, HTTP clients, environment helpers—that every other repo in the operation relies on. This solvent dissolves duplication and keeps the Road to 0.20.3 campaign aligned.

## 0.20.3 Command Sequence
Version 0.20.3 distills a JSON-native board engine straight into the common toolkit. The new `JsonBoardState` and `JsonCardRecord` APIs replace any lingering temptation to lean on `x_legatus_tabula_opus`. Now the orchestration stack snapshots tasks with clean, schema-driven payloads and zero foreign dependencies.

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
- [Road to 0.20.3 Control Room Ledger](../x_0_make_all_x/Change%20Control/0.20.3/Road%20to%200.20.3%20Engineering%20Proposal.md)
- [Road to 0.20.3 Engineering Proposal](../x_0_make_all_x/Change%20Control/0.20.3/Road%20to%200.20.3%20Engineering%20Proposal.md)

## Cross-Linked Intelligence
- [x_0_make_all_x](../x_0_make_all_x/README.md) — orchestrator expects these helpers on every run
- [x_make_github_visitor_x](../x_make_github_visitor_x/README.md) — the compliance visitor that consumes common telemetry and logging utilities
- [x_make_pypi_x](../x_make_pypi_x/README.md) — publishing pipeline wired directly into these helpers

## Lab Etiquette
When you alter shared utilities, update the changelog and alert the Downstream repos via the Change Control index. Half measures here create cascading failures everywhere else.
