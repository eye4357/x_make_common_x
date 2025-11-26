"""Persona vetting contracts used by Robot Senate smoke tests."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class PersonaEvidence:
    """Structured response describing persona vetting results."""

    persona_id: str
    score: float
    source: str
    display_name: str | None = None
    synopsis: str | None = None
    tags: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()


class PersonaVettingError(RuntimeError):
    """Raised when a persona vetting adapter encounters a recoverable issue."""


class PersonaVettingService:
    """Abstract interface implemented by persona vetting adapters."""

    def lookup(self, persona_id: str) -> PersonaEvidence:  # pragma: no cover - interface stub
        raise NotImplementedError("PersonaVettingService.lookup must be implemented by subclasses")

    def build_result(
        self,
        persona_id: str,
        *,
        score: float,
        source: str,
        display_name: str | None = None,
        synopsis: str | None = None,
        tags: Sequence[str] | Iterable[str] = (),
        reasons: Sequence[str] | Iterable[str] = (),
    ) -> PersonaEvidence:
        """Helper for subclasses to emit PersonaEvidence objects with normalized tuples."""

        normalized_tags = tuple(str(tag) for tag in tags)
        normalized_reasons = tuple(str(reason) for reason in reasons)
        return PersonaEvidence(
            persona_id=persona_id,
            score=float(score),
            source=source,
            display_name=display_name,
            synopsis=synopsis,
            tags=normalized_tags,
            reasons=normalized_reasons,
        )
