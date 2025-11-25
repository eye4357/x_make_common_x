"""Append-only ledger utilities."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path


@dataclass(slots=True, frozen=True)
class LedgerEvent:
    """Structured event suitable for immutable ledgers."""

    event_type: str
    payload: Mapping[str, Any]
    emitted_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "payload": dict(self.payload),
            "emitted_at": self.emitted_at,
        }


class LedgerWriter:
    """Append-only JSONL writer that includes per-entry checksums."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: LedgerEvent) -> str:
        entry = event.to_dict()
        serialized = json.dumps(entry, sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        line = json.dumps({**entry, "sha256": digest})
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(line)
            handle.write("\n")
        return digest


def append_event(path: Path, event_type: str, payload: Mapping[str, Any]) -> str:
    """Append a ledger event to *path*, returning the checksum."""

    writer = LedgerWriter(path)
    return writer.append(LedgerEvent(event_type=event_type, payload=payload))
