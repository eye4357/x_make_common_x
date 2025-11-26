from __future__ import annotations

from .QtWidgets import QGraphicsItem

__all__ = ["QGraphicsSvgItem"]

class QGraphicsSvgItem(QGraphicsItem):
    def __init__(
        self,
        file_name: str | None = ...,
        parent: QGraphicsItem | None = ...,
    ) -> None: ...
    def setSharedRenderer(self, renderer: object) -> None: ...
    def setElementId(self, element_id: str) -> None: ...
