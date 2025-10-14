from __future__ import annotations

import sys
from types import ModuleType

if "httpx" not in sys.modules:
    fake_httpx = ModuleType("httpx")

    class _DummyClient:
        def request(self, *_args: object, **_kwargs: object) -> object:
            message = "httpx client stub should not be used in tests"
            raise RuntimeError(message)

        def close(self) -> None:
            return None

    def _httpx_client(**_: object) -> _DummyClient:
        return _DummyClient()

    fake_httpx.HTTPError = RuntimeError  # type: ignore[attr-defined]
    fake_httpx.Client = _httpx_client  # type: ignore[attr-defined]
    sys.modules["httpx"] = fake_httpx
