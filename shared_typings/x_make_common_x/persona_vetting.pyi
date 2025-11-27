from collections.abc import Iterable, Sequence

class PersonaEvidence:
    persona_id: str
    score: float
    source: str
    display_name: str | None
    synopsis: str | None
    tags: tuple[str, ...]
    reasons: tuple[str, ...]

class PersonaVettingError(RuntimeError): ...

class PersonaVettingService:
    def lookup(self, persona_id: str) -> PersonaEvidence: ...
    def build_result(
        self,
        persona_id: str,
        *,
        score: float,
        source: str,
        display_name: str | None = ...,
        synopsis: str | None = ...,
        tags: Sequence[str] | Iterable[str] = ...,
        reasons: Sequence[str] | Iterable[str] = ...,
    ) -> PersonaEvidence: ...
