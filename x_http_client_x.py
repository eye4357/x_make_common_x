"""HTTP client helpers built on top of httpx."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, MutableMapping, Sequence
from dataclasses import dataclass
from typing import (
    Any,
    Protocol,
    cast,
)

import httpx


class _HttpxResponse(Protocol):
    status_code: int
    text: str

    def json(self) -> object: ...


class _HttpxClient(Protocol):
    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str] | None = ...,
        json: object | None = ...,
    ) -> _HttpxResponse: ...

    def close(self) -> None: ...


_HTTPX_MODULE: Any = httpx

try:
    _HTTPErrorType = cast("type[Exception]", _HTTPX_MODULE.HTTPError)
except AttributeError:  # pragma: no cover - httpx should provide HTTPError
    _HTTPErrorType = RuntimeError


@dataclass(slots=True)
class HttpResponse:
    status_code: int
    text: str
    json: object | None


class HttpError(RuntimeError):
    """Raised when an HTTP request fails."""


class HttpClient:
    """Thin wrapper around ``httpx.Client`` with conservative defaults."""

    _ERROR_THRESHOLD = 400

    def __init__(
        self,
        *,
        timeout: float = 10.0,
        headers: Mapping[str, str] | Iterable[tuple[str, str]] | None = None,
        follow_redirects: bool = True,
    ) -> None:
        try:
            client_factory = cast("Callable[..., _HttpxClient]", _HTTPX_MODULE.Client)
        except AttributeError as exc:  # pragma: no cover - defensive
            message = "httpx.Client is unavailable"
            raise RuntimeError(message) from exc
        self._client = client_factory(
            timeout=timeout,
            follow_redirects=follow_redirects,
        )
        self._default_headers: MutableMapping[str, str] = {}
        if headers:
            self._default_headers.update(_to_header_mapping(headers))

    def close(self) -> None:
        self._client.close()

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str] | Iterable[tuple[str, str]] | None = None,
        json: object | None = None,
    ) -> HttpResponse:
        combined_headers = dict(self._default_headers)
        if headers:
            combined_headers.update(_to_header_mapping(headers))
        try:
            response = self._client.request(
                method.upper(),
                url,
                headers=combined_headers,
                json=json,
            )
        except _HTTPErrorType as exc:
            message = f"HTTP error calling {url}: {exc}"
            raise HttpError(message) from exc
        status_code = response.status_code
        if status_code >= self._ERROR_THRESHOLD:
            error_body = response.text.strip()
            message = f"HTTP {status_code} calling {url}: {error_body}"
            raise HttpError(message)
        json_payload: object | None
        try:
            json_payload = response.json()
        except ValueError:
            json_payload = None
        return HttpResponse(
            status_code=status_code,
            text=response.text,
            json=json_payload,
        )

    def head(
        self,
        url: str,
        *,
        headers: Mapping[str, str] | Iterable[tuple[str, str]] | None = None,
    ) -> HttpResponse:
        return self.request("HEAD", url, headers=headers)

    def get(
        self,
        url: str,
        *,
        headers: Mapping[str, str] | Iterable[tuple[str, str]] | None = None,
    ) -> HttpResponse:
        return self.request("GET", url, headers=headers)


def _to_header_mapping(
    headers: Mapping[str, str] | Iterable[tuple[str, str]],
) -> Mapping[str, str]:
    if isinstance(headers, Mapping):
        typed_mapping = cast("Mapping[str, str]", headers)
        return {str(key): str(value) for key, value in typed_mapping.items()}
    pairs: Sequence[tuple[str, str]] = tuple(headers)
    return {str(key): str(value) for key, value in pairs}


__all__ = ["HttpClient", "HttpError", "HttpResponse"]
