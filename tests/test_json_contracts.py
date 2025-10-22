from __future__ import annotations

import pytest
from jsonschema.exceptions import ValidationError

from x_make_common_x.json_contracts import validate_payload, validate_schema

ValidationErrorType: type[Exception] = ValidationError


@pytest.fixture(scope="module")  # type: ignore[misc]
def sample_schema() -> dict[str, object]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {
            "status": {"enum": ["success", "failure"]},
            "details": {"type": "object"},
        },
        "required": ["status"],
        "additionalProperties": False,
    }


def test_validate_schema_accepts_well_formed_schema(
    sample_schema: dict[str, object],
) -> None:
    validate_schema(sample_schema)


def test_validate_payload_success(sample_schema: dict[str, object]) -> None:
    payload = {"status": "success", "details": {}}
    validate_payload(payload, sample_schema)


def test_validate_payload_raises_on_failure(sample_schema: dict[str, object]) -> None:
    with pytest.raises(ValidationErrorType):
        validate_payload({"details": {}}, sample_schema)
