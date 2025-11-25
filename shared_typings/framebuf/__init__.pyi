from __future__ import annotations

class FrameBuffer:
    def __init__(self, buffer: bytearray, width: int, height: int, format: int) -> None: ...

    def fill(self, color: int) -> None: ...

    def text(self, text: str, x: int, y: int, color: int) -> None: ...

MONO_HLSB: int
