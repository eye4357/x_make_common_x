from collections.abc import Iterable, Mapping

class HttpResponse:
    status_code: int
    text: str
    json: object | None

    def __init__(self, status_code: int, text: str, json: object | None) -> None: ...

class HttpError(RuntimeError): ...

class HttpClient:
    def __init__(
        self,
        *,
        timeout: float = ...,
        headers: Mapping[str, str] | Iterable[tuple[str, str]] | None = ...,
        follow_redirects: bool = ...,
        base_url: str | None = ...,
        transport: object | None = ...,
    ) -> None: ...
    def close(self) -> None: ...
    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str] | Iterable[tuple[str, str]] | None = ...,
        json: object | None = ...,
        params: Mapping[str, object] | Iterable[tuple[str, object]] | None = ...,
        allowed_status_codes: Iterable[int] | None = ...,
    ) -> HttpResponse: ...
    def head(
        self,
        url: str,
        *,
        headers: Mapping[str, str] | Iterable[tuple[str, str]] | None = ...,
        params: Mapping[str, object] | Iterable[tuple[str, object]] | None = ...,
        allowed_status_codes: Iterable[int] | None = ...,
    ) -> HttpResponse: ...
    def get(
        self,
        url: str,
        *,
        headers: Mapping[str, str] | Iterable[tuple[str, str]] | None = ...,
        params: Mapping[str, object] | Iterable[tuple[str, object]] | None = ...,
        allowed_status_codes: Iterable[int] | None = ...,
    ) -> HttpResponse: ...

__all__ = ["HttpClient", "HttpError", "HttpResponse"]
