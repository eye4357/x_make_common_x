from __future__ import annotations

from typing import Any, Iterable

class PyJWTError(Exception): ...

DefDict = dict[str, Any]

def encode(payload: DefDict, key: str, *, algorithm: str) -> str: ...
def decode(token: str, key: str, *, algorithms: Iterable[str]) -> DefDict: ...
