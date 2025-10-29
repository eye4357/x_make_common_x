"""Telemetry support removed in 0.21.1."""

from __future__ import annotations

_TELEMETRY_REMOVAL_MESSAGE = (
    "x_make_common_x.telemetry no longer exists. Use JSON summaries or logging."
)

raise RuntimeError(_TELEMETRY_REMOVAL_MESSAGE)
