from __future__ import annotations

__all__ = ["ValidationError"]

class ValidationError(Exception):
    message: str
    path: tuple[object, ...]
    schema_path: tuple[object, ...]
    def __init__(self, message: str) -> None: ...
