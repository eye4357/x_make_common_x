from typing import Protocol


class _ASGIApp(Protocol):
	def __call__(self, scope: object, receive: object, send: object) -> object: ...


def run(app: _ASGIApp, host: str, port: int) -> None: ...
