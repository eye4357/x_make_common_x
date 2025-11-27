"""Persona vetting contracts used by Robot Senate smoke tests."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence


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

    def lookup(
        self,
        persona_id: str,
    ) -> PersonaEvidence:  # pragma: no cover - interface stub
        message = "PersonaVettingService.lookup must be implemented by subclasses"
        raise NotImplementedError(message)

    def build_result(  # noqa: PLR0913
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
        """Help adapters emit PersonaEvidence objects with normalized tuples."""

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
