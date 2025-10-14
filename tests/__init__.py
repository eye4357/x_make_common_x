from __future__ import annotations

import sys
import types

if "httpx" not in sys.modules:
    fake_httpx = types.ModuleType("httpx")

    class _DummyClient:
        def request(self, *args: object, **kwargs: object) -> object:
            raise RuntimeError("httpx client stub should not be used in tests")

        def close(self) -> None:
            return None

    def _httpx_client(**_: object) -> _DummyClient:
        return _DummyClient()

    fake_httpx.HTTPError = RuntimeError
    fake_httpx.Client = _httpx_client
    sys.modules["httpx"] = fake_httpx
