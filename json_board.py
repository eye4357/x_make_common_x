"""JSON-backed kanban ledger utilities."""

from __future__ import annotations

import contextlib
import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

__all__ = ["BoardState", "CardRecord", "dump_board", "load_board", "save_board"]


@dataclass(slots=True)
class CardRecord:
    """Single card snapshot stored in the JSON ledger."""

    card_id: str
    title: str
    status: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    description: str | None = None

    def to_json(self) -> dict[str, object]:
        return {
            "id": self.card_id,
            "title": self.title,
            "status": self.status,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_json(cls, payload: Mapping[str, object]) -> CardRecord:
        card_id_obj = payload.get("id")
        title_obj = payload.get("title")
        if not isinstance(card_id_obj, str) or not card_id_obj.strip():
            msg = "Card payload missing required 'id' field"
            raise ValueError(msg)
        if not isinstance(title_obj, str) or not title_obj.strip():
            msg = "Card payload missing required 'title' field"
            raise ValueError(msg)

        status_obj = payload.get("status")
        status = status_obj.strip() if isinstance(status_obj, str) else "Backlog"
        description_obj = payload.get("description")
        description = description_obj if isinstance(description_obj, str) else None
        created_at = _coerce_timestamp(payload.get("created_at"))
        updated_at = _coerce_timestamp(payload.get("updated_at"))
        return cls(
            card_id=card_id_obj.strip(),
            title=title_obj.strip(),
            status=status or "Backlog",
            created_at=created_at,
            updated_at=updated_at,
            description=description,
        )


def _coerce_timestamp(value: object) -> datetime:
    if isinstance(value, str) and value:
        with contextlib.suppress(ValueError):
            return datetime.fromisoformat(value)
    return datetime.now(UTC)


def _empty_board() -> dict[str, CardRecord]:
    return {}


@dataclass(slots=True)
class BoardState:
    """In-memory board where mutations are mirrored back into JSON."""

    cards: dict[str, CardRecord] = field(default_factory=_empty_board)

    def add(self, record: CardRecord) -> None:
        key = record.card_id
        if key in self.cards:
            msg = f"card already exists: {key}"
            raise ValueError(msg)
        now = datetime.now(UTC)
        record.created_at = now
        record.updated_at = now
        self.cards[key] = record

    def update(self, record: CardRecord) -> None:
        key = record.card_id
        if key not in self.cards:
            msg = f"card not found: {key}"
            raise ValueError(msg)
        original = self.cards[key]
        record.created_at = original.created_at
        record.updated_at = datetime.now(UTC)
        self.cards[key] = record

    def remove(self, card_id: str) -> CardRecord:
        try:
            return self.cards.pop(card_id)
        except KeyError as exc:  # pragma: no cover - defensive barrier
            msg = f"card not found: {card_id}"
            raise ValueError(msg) from exc

    def list_cards(self) -> list[CardRecord]:
        return list(self.cards.values())

    def to_json(self) -> list[dict[str, object]]:
        def _updated_key(card: CardRecord) -> datetime:
            return card.updated_at

        ordered = sorted(self.cards.values(), key=_updated_key)
        return [card.to_json() for card in ordered]


def load_board(path: Path | str) -> BoardState:
    path_obj = Path(path)
    if not path_obj.exists():
        return BoardState()
    payload_obj: object = json.loads(path_obj.read_text(encoding="utf-8"))
    if not isinstance(payload_obj, list):
        msg = "Board JSON must be a list of card objects"
        raise TypeError(msg)
    state = BoardState()
    payload_list = cast("list[object]", payload_obj)
    for entry in payload_list:
        if isinstance(entry, Mapping):
            mapping_entry = cast("Mapping[str, object]", entry)
            record = CardRecord.from_json(mapping_entry)
            state.cards[record.card_id] = record
    return state


def dump_board(state: BoardState) -> list[dict[str, object]]:
    return state.to_json()


def save_board(path: Path | str, state: BoardState) -> None:
    serialized: str = json.dumps(dump_board(state), indent=2, sort_keys=False)
    Path(path).write_text(serialized, encoding="utf-8")


def board_from_records(records: Iterable[Mapping[str, object]]) -> BoardState:
    state = BoardState()
    for entry in records:
        record = CardRecord.from_json(entry)
        state.cards[record.card_id] = record
    return state
