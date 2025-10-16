# Changelog — Control Room Production Log

All notable changes to x_make_common_x are logged here. We observe [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) principles and Semantic Versioning even when the heat starts to rise.

## [0.20.4] - 2025-10-15
### Added
- Exporter suite for Markdown→PDF, Graphviz→SVG, and Mermaid→SVG with a shared `ExportResult` contract, binary discovery, and artifact metadata for the Kanban evidence trail.

### Changed
- README and operating guides updated for the Road to 0.20.4 release blueprint, covering exporter guardrails and fallback behaviour when binaries go missing.

## [0.20.3] - 2025-10-14
### Added
- JSON-backed `JsonBoardState` and `JsonCardRecord` so every workflow can track tasks without touching `x_legatus_tabula_opus`.
- `board_from_records`, `load_json_board`, and `save_json_board` exports wired into the package surface for data-first orchestration.

### Changed
- README and operating guides rewritten for the Road to 0.20.3 release blueprint.

## [0.20.2] - 2025-10-14
### Changed
- Hardened documentation for telemetry, subprocess, and HTTP helpers to the Road to 0.20.2 control-room brief so every downstream repo marches in lockstep.

## [0.20.1] - 2025-10-13
### Changed
- Updated README references to the Road to 0.20.1 control-room ledger so shared utilities mirror the current release focus.

## [0.20.0-prep] - 2025-10-12
### Added
- Authored control-room aligned README and changelog to standardize lab behavior across every dependent repository.
- Cross-linked the shared utilities with the Road to 0.20.0 control room and publishing pipeline.

### Changed
- Documented expectations for downstream teams when adjusting common helpers so the orchestration stack never ingests contaminated code.
