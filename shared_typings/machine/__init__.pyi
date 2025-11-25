from __future__ import annotations

from typing import Optional

class Pin:
    IN: int
    OUT: int
    PULL_UP: int

    def __init__(self, id: int, mode: int, pull: Optional[int] = ...) -> None: ...

    def value(self, value: Optional[int] = ...) -> int: ...


class I2C:
    def __init__(self, id: int, *, scl: Pin, sda: Pin, freq: int) -> None: ...

    def readfrom_mem(self, addr: int, memaddr: int, nbytes: int) -> bytes: ...

    def writeto_mem(self, addr: int, memaddr: int, data: bytes) -> None: ...


class SPI:
    def __init__(self, bus: int, *, baudrate: int, polarity: int, phase: int, sck: Pin, mosi: Pin) -> None: ...


def freq(freq: int) -> None: ...
