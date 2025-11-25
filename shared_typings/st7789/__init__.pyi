from __future__ import annotations

from machine import Pin, SPI

class ST7789:
    def __init__(
        self,
        spi: SPI,
        width: int,
        height: int,
        *,
        reset: Pin,
        dc: Pin,
        cs: Pin,
        rotation: int,
    ) -> None: ...
    def init(self) -> None: ...
    def fill(self, color: int) -> None: ...
    def fill_rect(
        self, x: int, y: int, width: int, height: int, color: int
    ) -> None: ...
    def text(self, font: object, text: str, x: int, y: int, color: int) -> None: ...
