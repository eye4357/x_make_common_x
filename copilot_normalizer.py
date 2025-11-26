"""Utility helpers for normalizing Copilot persona responses."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence

DEFAULT_PERSONA_PROMPT = (
    "You are reviewing the persona '{persona_id}'. "
    "Summarize their mission, highlight notable traits, add hashtags, and "
    "return a fitness score between 0.0 and 1.0."
)


class PersonaPromptError(ValueError):
    """Raised when persona prompt templates cannot be rendered."""


def format_persona_question(persona_id: str, template: str = DEFAULT_PERSONA_PROMPT) -> str:
    """Format the persona prompt template, validating basic invariants."""

    normalized_id = persona_id.strip()
    if not normalized_id:
        raise PersonaPromptError("Persona identifier must be a non-empty string.")
    if "{persona_id}" not in template:
        raise PersonaPromptError("Prompt template must include the '{persona_id}' placeholder.")
    try:
        rendered = template.format(persona_id=normalized_id)
    except KeyError as exc:  # pragma: no cover - defensive guard
        raise PersonaPromptError(f"Invalid prompt placeholder: {exc}") from exc
    return rendered.strip()


def extract_answer_text(response: Mapping[str, object]) -> str:
    """Return the most useful text block from a Copilot response payload."""

    answer = response.get("answer")
    if isinstance(answer, str) and answer.strip():
        return answer.strip()
    cli = response.get("cli")
    if isinstance(cli, Mapping):
        stdout = cli.get("stdout")
        if isinstance(stdout, str) and stdout.strip():
            return stdout.strip()
    return ""


def extract_tags(response: Mapping[str, object]) -> tuple[str, ...]:
    """Derive normalized hashtag-style labels from the response payload."""

    tags = response.get("tags")
    if isinstance(tags, Sequence) and not isinstance(tags, (str, bytes)):
        normalized = [str(tag).strip() for tag in tags if str(tag).strip()]
        return tuple(dict.fromkeys(normalized))  # preserve order while removing duplicates

    answer = extract_answer_text(response)
    if not answer:
        return ()
    matches = re.findall(r"#([\w-]{2,32})", answer)
    return tuple(dict.fromkeys(match.lower() for match in matches))


def extract_highlights(response: Mapping[str, object]) -> tuple[str, ...]:
    """Extract short highlight statements from the response."""

    highlights = response.get("highlights")
    if isinstance(highlights, Sequence) and not isinstance(highlights, (str, bytes)):
        normalized = [str(item).strip() for item in highlights if str(item).strip()]
        return tuple(normalized[:5])

    answer = extract_answer_text(response)
    if not answer:
        return ()
    bullet_lines: list[str] = []
    for line in answer.splitlines():
        stripped = line.strip()
        if stripped.startswith(("-", "*", "•")):
            bullet_lines.append(stripped.lstrip("-*• "))
    if bullet_lines:
        return tuple(bullet_lines[:5])

    sentences = [frag.strip() for frag in re.split(r"[.!?]\s+", answer) if frag.strip()]
    return tuple(sentences[:3])


def score_from_answer(answer: str) -> float:
    """Compute a coarse confidence score based on the supplied prose."""

    text = answer.strip()
    if not text:
        return 0.0
    positive = len(re.findall(r"\b(excellent|strong|trusted|reliable|experienced)\b", text.lower()))
    negative = len(re.findall(r"\b(risk|concern|fraud|unsafe|unknown)\b", text.lower()))
    base = min(1.0, len(text) / 600.0)
    score = base + 0.05 * positive - 0.05 * negative
    return max(0.0, min(1.0, score))


def source_from_response(response: Mapping[str, object]) -> str:
    """Determine the provenance of the response (CLI, HTTP, etc.)."""

    source = response.get("source")
    if isinstance(source, str) and source.strip():
        return source.strip()
    cli = response.get("cli")
    if isinstance(cli, Mapping):
        model = cli.get("model")
        if isinstance(model, str) and model.strip():
            return model.strip()
    return "unknown"


def synopsis_from_answer(answer: str) -> str | None:
    """Return a condensed single-line synopsis derived from the answer text."""

    text = answer.strip()
    if not text:
        return None
    sentences = re.split(r"[.!?]\s+", text, maxsplit=1)
    first_sentence = sentences[0].strip()
    return first_sentence[:240] if first_sentence else None
