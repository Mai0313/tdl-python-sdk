from __future__ import annotations

from enum import StrEnum


class LoginType(StrEnum):
    """Login mode for Telegram authentication."""

    DESKTOP = "desktop"
    CODE = "code"
    QR = "qr"


class ExportType(StrEnum):
    """Export type for chat message export."""

    TIME = "time"
    ID = "id"
    LAST = "last"


class ForwardMode(StrEnum):
    """Forward mode for message forwarding."""

    DIRECT = "direct"
    CLONE = "clone"


class ListOutput(StrEnum):
    """Output format for chat list."""

    TABLE = "table"
    JSON = "json"
