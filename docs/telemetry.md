# Telemetry Event Schema — Lab Specification

> "If the data can't survive a schema, it doesn't deserve a log file." This document is the single source of truth for the orchestration telemetry contract introduced in 0.20.2.

## Scope
Every orchestrator-adjacent package SHALL emit events that match this schema:

- `x_0_make_all_x` (control center GUI + CLI snapshotter)
- `x_make_github_clones_x`
- `x_make_github_visitor_x`
- `x_make_pip_updates_x`
- `x_make_pypi_x`

The intent is surgical: events replace free-form log scraping. Consumers can stream them to stdout, rotate files under `out/telemetry/YYYYMMDD/`, and feed dashboards without guesswork.

## Event Object
Each event is a JSON object (or equivalent Python dict) with the following fields. Types use Python typing syntax; enforcement will be handled with a TypedDict plus JSON Schema tests.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `version` | `Literal["0.20.2"]` | ✅ | Schema version. Bump when breaking changes ship. |
| `timestamp` | `datetime` (ISO 8601 string, UTC) | ✅ | Event creation time. UTC only; no local offsets. |
| `source` | `Literal["orchestrator", "clones", "visitor", "pip_updates", "pypi"]` | ✅ | Emitting subsystem. Packages map to literals as listed. |
| `phase` | `str` | ✅ | High-level phase: `startup`, `sync`, `inspection`, `pip`, `publish`, `shutdown`, etc. Keep snake_case. |
| `repository` | `str | None` | ✅ | Repo slug (`x_make_github_clones_x`, etc.). Null when the event is global. |
| `tool` | `str | None` | ✅ | Specific tool execution (`ruff_check`, `mypy`, `git_fetch`). Null when not applicable. |
| `status` | `Literal["started", "succeeded", "failed", "skipped", "retried", "quarantined"]` | ✅ | Outcome indicator. `retried` means an automated rerun triggered. `quarantined` marks repos parked after retries exhaustion. |
| `attempt` | `int` | ✅ | Monotonic attempt counter starting at 1. Automated reruns increment this. |
| `duration_ms` | `int | None` | ✅ | Milliseconds spent on the action. Null if event represents a start without a finish yet. |
| `details` | `dict[str, object]` | ✅ | Structured payload. MUST be JSON-serializable. Use shallow keys: `message`, `diagnostic_url`, `artifact_path`, `retry_reason`, etc. |

### Detail Field Conventions
- `details["message"]`: Single-sentence summary in plain text.
- `details["diagnostic_url"]`: Optional file:// or https:// link to enriched report.
- `details["artifact_path"]`: Relative path under `out/` where supporting files live.
- `details["retry_reason"]`: Populated when `status == "retried"`.
- `details["error_kind"]`: Machine label for failure class (`lint`, `type`, `network`, `auth`, `unknown`).

## Example Payloads

```json
{
  "version": "0.20.2",
  "timestamp": "2025-10-13T18:22:11.904Z",
  "source": "visitor",
  "phase": "inspection",
  "repository": "x_make_pip_updates_x",
  "tool": "mypy",
  "status": "failed",
  "attempt": 1,
  "duration_ms": 8731,
  "details": {
    "message": "mypy --strict exit 1",
    "error_kind": "type",
    "artifact_path": "out/reports/visitor_failures_20251013_182211.md"
  }
}
```

```json
{
  "version": "0.20.2",
  "timestamp": "2025-10-13T18:24:55.121Z",
  "source": "visitor",
  "phase": "inspection",
  "repository": "x_make_pip_updates_x",
  "tool": "mypy",
  "status": "retried",
  "attempt": 2,
  "duration_ms": 915,
  "details": {
    "message": "Automatic rerun triggered after transient failure",
    "retry_reason": "lint-transient",
    "artifact_path": "out/reports/visitor_failures_20251013_182455.md"
  }
}
```

```json
{
  "version": "0.20.2",
  "timestamp": "2025-10-13T18:27:02.443Z",
  "source": "visitor",
  "phase": "inspection",
  "repository": "x_make_pip_updates_x",
  "tool": "mypy",
  "status": "quarantined",
  "attempt": 3,
  "duration_ms": 0,
  "details": {
    "message": "Repo moved to quarantine after failed retry",
    "error_kind": "type",
    "artifact_path": "Change Control/0.20.2/quarantine.md#x_make_pip_updates_x"
  }
}
```

## Validation Strategy
1. **TypedDict contract** — introduce `TelemetryEvent` under `x_make_common_x.telemetry` with mypy enforcement in strict mode.
2. **Schema test** — store a JSON Schema alongside the module; add a pytest that loads sample events and validates via `jsonschema`.
3. **Round-trip guarantee** — helper that accepts any `TelemetryEvent`, serializes to JSON, and back to a dict without data loss.

Consumers MUST refuse events that fail validation; log the offender and continue.

## Emission Guidelines
- Emit a `started` event before long-running work; follow with a terminal event (`succeeded`, `failed`, `skipped`).
- Keep `duration_ms` zero on the initial `started` event; populate it on terminal events.
- Never log raw tracebacks inside `details`; surface a compact message and reference an artifact file instead.
- When in doubt, add a new key to `details` rather than expanding the top-level schema. If the new key becomes common across packages, propose an extension here.

## Storage & Rotation
- Default sink: append newline-delimited JSON to stdout. The orchestrator will tee into daily files under `out/telemetry/YYYYMMDD/events.log`.
- Rotate files at midnight UTC or after 10 MB, whichever comes first.
- Compression (zip) is optional; document retention policies in the orchestrator README.

## Change Management
- Any change to required fields increments `version` and adds a migration note to `CHANGELOG.md` for each affected package.
- Minor additions (new optional detail keys) require README updates but do not bump the version.
- Breaking changes demand coordination across all workstreams; do not merge until every subscriber is updated.

Stay disciplined. Telemetry that lies is worse than no telemetry at all.
