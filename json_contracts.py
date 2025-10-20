"""Helpers for validating JSON schemas and payloads used across the lab."""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping
from typing import Protocol, cast

from jsonschema.validators import Draft202012Validator

SchemaMapping = Mapping[str, object]
MutableSchemaMapping = MutableMapping[str, object]


class _DraftValidator(Protocol):
    """Subset of the Draft 2020-12 validator API we rely on."""

    @classmethod
    def check_schema(cls, schema: Mapping[str, object]) -> None: ...

    def __init__(self, schema: Mapping[str, object]) -> None: ...

    def validate(self, payload: object) -> None: ...


_DRAFT_VALIDATOR: type[_DraftValidator] = cast(
    "type[_DraftValidator]",
    Draft202012Validator,
)


def validate_schema(schema: SchemaMapping | MutableSchemaMapping) -> None:
    """Raise ``ValidationError`` if *schema* is not a valid JSON Schema."""

    _DRAFT_VALIDATOR.check_schema(dict(schema))


def validate_payload(
    payload: object, schema: SchemaMapping | MutableSchemaMapping
) -> None:
    """Validate *payload* against *schema* using Draft 2020-12 semantics."""

    validator = _DRAFT_VALIDATOR(dict(schema))
    validator.validate(payload)


__all__ = ["validate_payload", "validate_schema"]
