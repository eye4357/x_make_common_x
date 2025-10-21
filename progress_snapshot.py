"""Progress tracking helpers for orchestrator UIs."""

from __future__ import annotations

import contextlib
import errno
import json
import os
import time
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal, cast

_ATOMIC_WRITE_MAX_ATTEMPTS = 5
_ATOMIC_WRITE_RETRY_BASE_SECONDS = 0.1


ProgressStatus = Literal["pending", "running", "attention", "completed", "blocked"]
_VALID_STATUSES: set[str] = {"pending", "running", "attention", "completed", "blocked"}

__all__ = [
    "ProgressSnapshot",
    "ProgressStage",
    "ProgressStatus",
    "create_progress_snapshot",
    "load_progress_snapshot",
    "write_progress_snapshot",
]


def _now() -> datetime:
    return datetime.now(UTC)


def _sanitize_messages(messages: Sequence[str] | None) -> tuple[str, ...]:
    if not messages:
        return ()
    normalized: list[str] = []
    for message in messages:
        text = str(message).strip()
        if text:
            normalized.append(text)
    return tuple(normalized)


def _sanitize_metadata(metadata: Mapping[str, object] | None) -> dict[str, object]:
    if metadata is None:
        return {}
    sanitized: dict[str, object] = {}
    for key, value in metadata.items():
        sanitized[str(key)] = value
    return sanitized


def _atomic_write(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(payload, encoding="utf-8")
    last_error: PermissionError | OSError | None = None
    for attempt in range(1, _ATOMIC_WRITE_MAX_ATTEMPTS + 1):
        try:
            os.replace(tmp_path, path)
        except PermissionError as exc:
            winerror = getattr(exc, "winerror", None)
            if winerror not in {5, 32} and exc.errno not in {errno.EACCES, errno.EPERM}:
                tmp_path.unlink(missing_ok=True)
                raise
            last_error = exc
        except OSError as exc:
            if exc.errno not in {errno.EACCES, errno.EPERM}:
                tmp_path.unlink(missing_ok=True)
                raise
            last_error = exc
        else:
            return
        time.sleep(_ATOMIC_WRITE_RETRY_BASE_SECONDS * attempt)

    tmp_path.unlink(missing_ok=True)
    if last_error is None:
        last_error = PermissionError("os.replace repeatedly failed")
    raise last_error


@dataclass(slots=True)
class ProgressStage:
    stage_id: str
    title: str
    status: ProgressStatus = "pending"
    messages: tuple[str, ...] = field(default_factory=tuple)
    metadata: dict[str, object] = field(default_factory=dict)
    updated_at: datetime = field(default_factory=_now)

    def to_json(self) -> dict[str, object]:
        return {
            "id": self.stage_id,
            "title": self.title,
            "status": self.status,
            "messages": list(self.messages),
            "metadata": self.metadata,
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_json(cls, payload: Mapping[str, object]) -> ProgressStage:
        stage_id_obj = payload.get("id")
        title_obj = payload.get("title")
        if not isinstance(stage_id_obj, str) or not stage_id_obj.strip():
            raise ValueError("progress stage payload missing 'id'")
        if not isinstance(title_obj, str) or not title_obj.strip():
            raise ValueError("progress stage payload missing 'title'")
        status_obj = payload.get("status")
        status_raw = status_obj if isinstance(status_obj, str) else "pending"
        status = status_raw if status_raw in _VALID_STATUSES else "attention"
        messages_obj = payload.get("messages")
        messages: tuple[str, ...] = ()
        if isinstance(messages_obj, Sequence) and not isinstance(
            messages_obj, (str, bytes, bytearray)
        ):
            cleaned: list[str] = []
            for entry in messages_obj:
                normalized = str(entry).strip()
                if normalized:
                    cleaned.append(normalized)
            messages = tuple(cleaned)
        metadata_obj = payload.get("metadata")
        metadata: dict[str, object] = {}
        if isinstance(metadata_obj, Mapping):
            metadata = {str(key): value for key, value in metadata_obj.items()}
        updated_obj = payload.get("updated_at")
        updated_at = _now()
        if isinstance(updated_obj, str) and updated_obj:
            try:
                updated_at = datetime.fromisoformat(updated_obj)
            except ValueError:
                updated_at = _now()
        normalized_status = cast("ProgressStatus", status)
        return cls(
            stage_id=stage_id_obj.strip(),
            title=title_obj.strip(),
            status=normalized_status,
            messages=messages,
            metadata=metadata,
            updated_at=updated_at,
        )


@dataclass(slots=True)
class ProgressSnapshot:
    stages: dict[str, ProgressStage] = field(default_factory=dict)
    created_at: datetime = field(default_factory=_now)
    updated_at: datetime = field(default_factory=_now)
    summary: str | None = None

    def ensure_stage(self, stage_id: str, title: str) -> ProgressStage:
        normalized_id = str(stage_id).strip()
        normalized_title = str(title).strip()
        stage = self.stages.get(normalized_id)
        if stage is None:
            stage = ProgressStage(stage_id=normalized_id, title=normalized_title)
            self.stages[normalized_id] = stage
            self.updated_at = _now()
        elif normalized_title and stage.title != normalized_title:
            stage.title = normalized_title
        return stage

    def update_stage(
        self,
        stage_id: str,
        *,
        title: str,
        status: str,
        messages: Sequence[str] | None = None,
        metadata: Mapping[str, object] | None = None,
    ) -> None:
        normalized_status = status if status in _VALID_STATUSES else "attention"
        stage = self.ensure_stage(stage_id, title)
        stage.status = cast("ProgressStatus", normalized_status)
        stage.messages = _sanitize_messages(messages)
        stage.metadata = _sanitize_metadata(metadata)
        stage.updated_at = _now()
        self.updated_at = stage.updated_at

    def to_json(self) -> dict[str, object]:
        ordered = [self.stages[key] for key in sorted(self.stages)]
        return {
            "schema_version": "x_make.progress/1.0",
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "summary": self.summary,
            "stages": [stage.to_json() for stage in ordered],
        }

    @classmethod
    def from_json(cls, payload: Mapping[str, object]) -> ProgressSnapshot:
        stages_payload = payload.get("stages")
        if not isinstance(stages_payload, Sequence):
            raise ValueError("progress snapshot requires 'stages' list")
        snapshot = cls()
        created_obj = payload.get("created_at")
        updated_obj = payload.get("updated_at")
        if isinstance(created_obj, str) and created_obj:
            with contextlib.suppress(ValueError):
                snapshot.created_at = datetime.fromisoformat(created_obj)
        if isinstance(updated_obj, str) and updated_obj:
            with contextlib.suppress(ValueError):
                snapshot.updated_at = datetime.fromisoformat(updated_obj)
        summary_obj = payload.get("summary")
        snapshot.summary = str(summary_obj) if isinstance(summary_obj, str) else None
        for entry in stages_payload:
            if isinstance(entry, Mapping):
                stage = ProgressStage.from_json(entry)
                snapshot.stages[stage.stage_id] = stage
        return snapshot


def create_progress_snapshot(stage_definitions: Iterable[tuple[str, str]]) -> ProgressSnapshot:
    snapshot = ProgressSnapshot()
    for stage_id, title in stage_definitions:
        snapshot.ensure_stage(str(stage_id), str(title))
    return snapshot


def write_progress_snapshot(path: Path | str, snapshot: ProgressSnapshot) -> Path:
    path_obj = Path(path)
    serialized = json.dumps(snapshot.to_json(), indent=2, sort_keys=False)
    _atomic_write(path_obj, serialized)
    return path_obj


def load_progress_snapshot(path: Path | str) -> ProgressSnapshot | None:
    path_obj = Path(path)
    if not path_obj.exists():
        return None
    payload = json.loads(path_obj.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise TypeError("progress snapshot JSON must be an object")
    return ProgressSnapshot.from_json(payload)
