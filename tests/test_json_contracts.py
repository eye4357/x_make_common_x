from __future__ import annotations

import typing
from typing import TYPE_CHECKING, ParamSpec, TypeVar, cast

import pytest
from jsonschema.exceptions import ValidationError

from x_make_common_x.json_contracts import validate_payload, validate_schema

ValidationErrorType: type[Exception] = ValidationError

_P = ParamSpec("_P")
_T = TypeVar("_T")
if TYPE_CHECKING:
    from collections.abc import Callable
else:
    Callable = typing.Callable


if TYPE_CHECKING:

    def typed_fixture(
        *_args: object, **_kwargs: object
    ) -> Callable[[Callable[_P, _T]], Callable[_P, _T]]: ...

else:

    def typed_fixture(
        *args: object, **kwargs: object
    ) -> Callable[[Callable[_P, _T]], Callable[_P, _T]]:
        def _decorate(func: Callable[_P, _T]) -> Callable[_P, _T]:
            decorated = pytest.fixture(*args, **kwargs)(func)
            return cast("Callable[_P, _T]", decorated)

        return _decorate


@typed_fixture(scope="module")
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
