from __future__ import annotations

from typing import Mapping

__all__ = ["Draft202012Validator"]

class Draft202012Validator:
    @classmethod
    def check_schema(cls, schema: Mapping[str, object]) -> None: ...
    def __init__(self, schema: Mapping[str, object]) -> None: ...
    def validate(self, instance: object) -> None: ...
