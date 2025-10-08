"""HTTP client helpers built on top of httpx."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, MutableMapping, cast  # noqa: UP035

import httpx


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
        self._client = httpx.Client(timeout=timeout, follow_redirects=follow_redirects)
        self._default_headers: MutableMapping[str, str] = {}
        if headers:
            self._default_headers.update(dict(headers))

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
            combined_headers.update(dict(headers))
        try:
            response = self._client.request(
                method.upper(),
                url,
                headers=combined_headers,
                json=json,
            )
        except httpx.HTTPError as exc:  # pragma: no cover - network error path
            message = f"HTTP error calling {url}: {exc}"
            raise HttpError(message) from exc
        status_code = response.status_code
        if status_code >= self._ERROR_THRESHOLD:
            error_body = response.text.strip()
            message = f"HTTP {status_code} calling {url}: {error_body}"
            raise HttpError(message)
        json_payload: object | None
        try:
            json_payload = cast(object, response.json())
        except ValueError:
            json_payload = None
        return HttpResponse(
            status_code=response.status_code,
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


__all__ = ["HttpClient", "HttpError", "HttpResponse"]
