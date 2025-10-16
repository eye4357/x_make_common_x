# ruff: noqa: S101

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

import pytest

from x_make_common_x.json_board import BoardState, CardRecord, load_board, save_board

if TYPE_CHECKING:  # pragma: no cover - type hints only
    from pathlib import Path


def test_board_add_update_remove(tmp_path: Path) -> None:
    board = BoardState()
    record = CardRecord(card_id="chem-1", title="Load JSON schema", status="Backlog")
    board.add(record)
    assert len(board.list_cards()) == 1

    updated = CardRecord(
        card_id="chem-1",
        title="Load JSON schema",
        status="InProgress",
        description="Validating the samples",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    board.update(updated)
    stored = board.list_cards()[0]
    assert stored.status == "InProgress"
    assert stored.description == "Validating the samples"

    removed = board.remove("chem-1")
    assert removed.card_id == "chem-1"
    assert board.list_cards() == []

    save_board(tmp_path / "board.json", board)
    reloaded = load_board(tmp_path / "board.json")
    assert reloaded.list_cards() == []


def test_load_board_rejects_invalid_json(tmp_path: Path) -> None:
    path = tmp_path / "broken.json"
    path.write_text("{}", encoding="utf-8")
    with pytest.raises(TypeError, match="must be a list"):
        load_board(path)
