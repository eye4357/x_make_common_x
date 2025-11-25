from collections.abc import Mapping


class WebsocketClient:
    async def send(self, data: str, /, *args: object, **kwargs: object) -> None: ...

    async def close(self, /, *args: object, **kwargs: object) -> None: ...


async def connect(
    uri: str,
    headers: Mapping[str, str] | None = ...,
    *args: object,
    **kwargs: object,
) -> WebsocketClient: ...
