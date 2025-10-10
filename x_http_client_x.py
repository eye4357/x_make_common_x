"""HTTP client helpers built on top of httpx."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, MutableMapping, Sequence
from dataclasses import dataclass
from typing import Protocol, cast

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
        headers: Mapping[str, str] | None = None,
        json: object | None = None,
        params: Mapping[str, str] | None = None,
    ) -> _HttpxResponse: ...

    def close(self) -> None: ...


class _HttpxClientFactory(Protocol):
    def __call__(
        self,
        *,
        timeout: float,
        follow_redirects: bool,
        **kwargs: object,
    ) -> _HttpxClient: ...


_HTTPErrorType = cast(
    "type[Exception]",
    getattr(httpx, "HTTPError", RuntimeError),
)


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
        base_url: str | None = None,
        transport: object | None = None,
    ) -> None:
        client_factory = cast(
            "_HttpxClientFactory | None",
            getattr(httpx, "Client", None),
        )
        if client_factory is None:
            message = "httpx.Client is unavailable"
            raise TypeError(message)

        client_kwargs: dict[str, object] = {}
        if base_url is not None:
            client_kwargs["base_url"] = base_url
        if transport is not None:
            client_kwargs["transport"] = transport
        client_instance = client_factory(
            timeout=timeout,
            follow_redirects=follow_redirects,
            **client_kwargs,
        )
        self._client = client_instance
        self._default_headers: MutableMapping[str, str] = {}
        if headers:
            self._default_headers.update(_to_header_mapping(headers))

    def close(self) -> None:
        self._client.close()

    def request(  # noqa: PLR0913 -- keyword-only params keep call sites explicit
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str] | Iterable[tuple[str, str]] | None = None,
        json: object | None = None,
        params: Mapping[str, object] | Iterable[tuple[str, object]] | None = None,
        allowed_status_codes: Iterable[int] | None = None,
    ) -> HttpResponse:
        combined_headers = dict(self._default_headers)
        if headers:
            combined_headers.update(_to_header_mapping(headers))
        query_params = _to_param_mapping(params) if params else None
        allowed = {int(code) for code in allowed_status_codes or ()}
        try:
            response = self._client.request(
                method.upper(),
                url,
                headers=combined_headers,
                json=json,
                params=query_params,
            )
        except _HTTPErrorType as exc:
            message = f"HTTP error calling {url}: {exc}"
            raise HttpError(message) from exc
        status_code = response.status_code
        if status_code >= self._ERROR_THRESHOLD and status_code not in allowed:
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
        params: Mapping[str, object] | Iterable[tuple[str, object]] | None = None,
        allowed_status_codes: Iterable[int] | None = None,
    ) -> HttpResponse:
        return self.request(
            "HEAD",
            url,
            headers=headers,
            params=params,
            allowed_status_codes=allowed_status_codes,
        )

    def get(
        self,
        url: str,
        *,
        headers: Mapping[str, str] | Iterable[tuple[str, str]] | None = None,
        params: Mapping[str, object] | Iterable[tuple[str, object]] | None = None,
        allowed_status_codes: Iterable[int] | None = None,
    ) -> HttpResponse:
        return self.request(
            "GET",
            url,
            headers=headers,
            params=params,
            allowed_status_codes=allowed_status_codes,
        )


def _to_header_mapping(
    headers: Mapping[str, str] | Iterable[tuple[str, str]],
) -> Mapping[str, str]:
    if isinstance(headers, Mapping):
        typed_mapping = cast("Mapping[str, str]", headers)
        return {str(key): str(value) for key, value in typed_mapping.items()}
    pairs: Sequence[tuple[str, str]] = tuple(headers)
    return {str(key): str(value) for key, value in pairs}


def _to_param_mapping(
    params: Mapping[str, object] | Iterable[tuple[str, object]],
) -> Mapping[str, str]:
    if isinstance(params, Mapping):
        typed_mapping = cast("Mapping[str, object]", params)
        return {str(key): str(value) for key, value in typed_mapping.items()}
    pairs: Sequence[tuple[str, object]] = tuple(params)
    return {str(key): str(value) for key, value in pairs}


__all__ = ["HttpClient", "HttpError", "HttpResponse"]
