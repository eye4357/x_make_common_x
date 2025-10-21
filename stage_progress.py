"""Stage-level per-repository progress writers."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
from collections.abc import Mapping, MutableMapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

__all__ = [
    "RepoProgressReporter",
    "StageProgressEntry",
    "StageProgressWriter",
]

_ALLOWED_STATUSES: set[str] = {
    "pending",
    "running",
    "completed",
    "attention",
    "blocked",
    "skipped",
}
_COMPLETION_STATUSES = {"completed", "attention", "blocked", "skipped"}
_DETAIL_SCHEMA = "x_make.stage_progress.repo/1.0"
_INDEX_SCHEMA = "x_make.stage_progress.index/1.0"
_MESSAGE_LIMIT = 10


class RepoProgressReporter(Protocol):
    def record_pending(
        self,
        repo_id: str,
        *,
        display_name: str | None = None,
        metadata: Mapping[str, object] | None = None,
        messages: Sequence[str] | None = None,
    ) -> None: ...

    def record_start(
        self,
        repo_id: str,
        *,
        display_name: str | None = None,
        metadata: Mapping[str, object] | None = None,
        messages: Sequence[str] | None = None,
    ) -> None: ...

    def record_success(
        self,
        repo_id: str,
        *,
        display_name: str | None = None,
        metadata: Mapping[str, object] | None = None,
        messages: Sequence[str] | None = None,
    ) -> None: ...

    def record_failure(
        self,
        repo_id: str,
        *,
        display_name: str | None = None,
        metadata: Mapping[str, object] | None = None,
        messages: Sequence[str] | None = None,
    ) -> None: ...

    def record_skipped(
        self,
        repo_id: str,
        *,
        display_name: str | None = None,
        metadata: Mapping[str, object] | None = None,
        messages: Sequence[str] | None = None,
    ) -> None: ...


def _now() -> datetime:
    return datetime.now(UTC)


def _atomic_write(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(payload, encoding="utf-8")
    os.replace(tmp_path, path)


def _sanitize_messages(messages: Sequence[str] | None) -> list[str]:
    if not messages:
        return []
    seen: set[str] = set()
    normalized: list[str] = []
    for message in messages:
        text = str(message).strip()
        if not text or text in seen:
            continue
        normalized.append(text)
        seen.add(text)
        if len(normalized) >= _MESSAGE_LIMIT:
            break
    return normalized


def _json_ready(value: object) -> object:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Mapping):
        mapping = {}
        for key, val in value.items():
            mapping[str(key)] = _json_ready(val)
        return mapping
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_json_ready(item) for item in value]
    return str(value)


def _normalize_status(status: str) -> str:
    candidate = status.strip().lower() if isinstance(status, str) else "attention"
    return candidate if candidate in _ALLOWED_STATUSES else "attention"


def _safe_repo_filename(repo_id: str) -> str:
    cleaned = repo_id.strip().replace("\\", "/")
    cleaned = re.sub(r"/+", "/", cleaned)
    cleaned = cleaned.replace("/", "__")
    cleaned = re.sub(r"[^A-Za-z0-9_.-]", "_", cleaned)
    cleaned = cleaned.strip("._")
    if not cleaned:
        cleaned = "repo"
    digest = hashlib.sha1(repo_id.encode("utf-8", "ignore")).hexdigest()[:8]
    return f"{cleaned}_{digest}.json"


@dataclass(slots=True)
class StageProgressEntry:
    repo_id: str
    display_name: str | None = None
    status: str = "pending"
    messages: tuple[str, ...] = field(default_factory=tuple)
    metadata: dict[str, object] = field(default_factory=dict)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    updated_at: datetime = field(default_factory=_now)

    def to_detail_payload(self, stage_id: str) -> dict[str, object]:
        return {
            "schema_version": _DETAIL_SCHEMA,
            "stage_id": stage_id,
            "repo_id": self.repo_id,
            "display_name": self.display_name,
            "status": self.status,
            "messages": list(self.messages),
            "metadata": self.metadata,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "updated_at": self.updated_at.isoformat(),
        }

    def to_index_payload(self, detail_path: str) -> dict[str, object]:
        return {
            "repo_id": self.repo_id,
            "display_name": self.display_name,
            "status": self.status,
            "detail_path": detail_path,
            "updated_at": self.updated_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "message_preview": list(self.messages[:3]),
        }


class StageProgressWriter(RepoProgressReporter):
    def __init__(self, *, stage_id: str, root_dir: Path | str) -> None:
        self.stage_id = stage_id
        self.root_dir = Path(root_dir)
        self.root_dir.mkdir(parents=True, exist_ok=True)
        self._index_path = self.root_dir / "index.json"
        self._entries: dict[str, StageProgressEntry] = {}
        self._entry_files: dict[str, str] = {}
        self.reset()

    @property
    def index_path(self) -> Path:
        return self._index_path

    @property
    def entries_dir(self) -> Path:
        return self.root_dir

    def describe(self) -> dict[str, object]:
        counts = self._status_counts()
        return {
            "stage_id": self.stage_id,
            "index_path": str(self.index_path),
            "entries_dir": str(self.entries_dir),
            "total_entries": sum(counts.values()),
            "status_counts": counts,
        }

    def reset(self) -> None:
        self._entries.clear()
        self._entry_files.clear()
        if self.root_dir.exists():
            for child in self.root_dir.iterdir():
                try:
                    if child.is_file():
                        child.unlink()
                    else:
                        shutil.rmtree(child)
                except OSError:
                    continue
        self.root_dir.mkdir(parents=True, exist_ok=True)
        self._write_index()

    def record_pending(
        self,
        repo_id: str,
        *,
        display_name: str | None = None,
        metadata: Mapping[str, object] | None = None,
        messages: Sequence[str] | None = None,
    ) -> None:
        entry = self._ensure_entry(repo_id, display_name)
        self._update_entry(
            entry,
            status="pending",
            messages=messages,
            metadata=metadata,
            mark_started=False,
            mark_completed=False,
            replace_messages=True,
        )

    def record_start(
        self,
        repo_id: str,
        *,
        display_name: str | None = None,
        metadata: Mapping[str, object] | None = None,
        messages: Sequence[str] | None = None,
    ) -> None:
        entry = self._ensure_entry(repo_id, display_name)
        self._update_entry(
            entry,
            status="running",
            messages=messages,
            metadata=metadata,
            mark_started=True,
            mark_completed=False,
        )

    def record_success(
        self,
        repo_id: str,
        *,
        display_name: str | None = None,
        metadata: Mapping[str, object] | None = None,
        messages: Sequence[str] | None = None,
    ) -> None:
        entry = self._ensure_entry(repo_id, display_name)
        fallback = (messages or ("Completed successfully.",))
        self._update_entry(
            entry,
            status="completed",
            messages=fallback,
            metadata=metadata,
            mark_started=True,
            mark_completed=True,
        )

    def record_failure(
        self,
        repo_id: str,
        *,
        display_name: str | None = None,
        metadata: Mapping[str, object] | None = None,
        messages: Sequence[str] | None = None,
    ) -> None:
        entry = self._ensure_entry(repo_id, display_name)
        fallback = messages or ("Failed with issues.",)
        self._update_entry(
            entry,
            status="attention",
            messages=fallback,
            metadata=metadata,
            mark_started=True,
            mark_completed=True,
        )

    def record_skipped(
        self,
        repo_id: str,
        *,
        display_name: str | None = None,
        metadata: Mapping[str, object] | None = None,
        messages: Sequence[str] | None = None,
    ) -> None:
        entry = self._ensure_entry(repo_id, display_name)
        fallback = messages or ("Skipped.",)
        self._update_entry(
            entry,
            status="skipped",
            messages=fallback,
            metadata=metadata,
            mark_started=False,
            mark_completed=True,
        )

    # Internal helpers -------------------------------------------------

    def _ensure_entry(
        self,
        repo_id: str,
        display_name: str | None,
    ) -> StageProgressEntry:
        normalized = repo_id.strip() or "<unknown>"
        entry = self._entries.get(normalized)
        if entry is None:
            entry = StageProgressEntry(repo_id=normalized, display_name=display_name)
            self._entries[normalized] = entry
        elif display_name and entry.display_name != display_name:
            entry.display_name = display_name
        return entry

    def _update_entry(
        self,
        entry: StageProgressEntry,
        *,
        status: str,
        messages: Sequence[str] | None,
        metadata: Mapping[str, object] | None,
        mark_started: bool,
        mark_completed: bool,
        replace_messages: bool = False,
    ) -> None:
        normalized_status = _normalize_status(status)
        now = _now()
        if mark_started and entry.started_at is None:
            entry.started_at = now
        if mark_completed or normalized_status in _COMPLETION_STATUSES:
            entry.completed_at = entry.completed_at or now
        entry.status = normalized_status
        sanitized = _sanitize_messages(messages)
        if sanitized:
            if replace_messages:
                entry.messages = tuple(sanitized)
            else:
                combined = list(entry.messages)
                combined.extend(sanitized)
                entry.messages = tuple(_sanitize_messages(combined))
        elif replace_messages:
            entry.messages = ()
        if metadata:
            meta = entry.metadata
            for key, value in metadata.items():
                meta[str(key)] = _json_ready(value)
        entry.updated_at = now
        self._write_entry(entry)

    def _write_entry(self, entry: StageProgressEntry) -> None:
        filename = _safe_repo_filename(entry.repo_id)
        self._entry_files[entry.repo_id] = filename
        detail_path = self.root_dir / filename
        payload = entry.to_detail_payload(self.stage_id)
        serialized = json.dumps(payload, indent=2, sort_keys=False)
        _atomic_write(detail_path, serialized)
        self._write_index()

    def _write_index(self) -> None:
        counts = self._status_counts()
        ordered_entries = sorted(
            self._entries.values(), key=lambda entry: entry.repo_id.lower()
        )
        index_entries = []
        for entry in ordered_entries:
            detail_path = self._entry_files.get(entry.repo_id) or ""
            index_entries.append(entry.to_index_payload(detail_path))
        payload = {
            "schema_version": _INDEX_SCHEMA,
            "stage_id": self.stage_id,
            "updated_at": _now().isoformat(),
            "entries_dir": str(self.entries_dir),
            "total_entries": len(ordered_entries),
            "status_counts": counts,
            "entries": index_entries,
        }
        serialized = json.dumps(payload, indent=2, sort_keys=False)
        _atomic_write(self._index_path, serialized)

    def _status_counts(self) -> dict[str, int]:
        counts: MutableMapping[str, int] = dict.fromkeys(_ALLOWED_STATUSES, 0)
        for entry in self._entries.values():
            counts[entry.status] = counts.get(entry.status, 0) + 1
        return {key: value for key, value in counts.items() if value}
