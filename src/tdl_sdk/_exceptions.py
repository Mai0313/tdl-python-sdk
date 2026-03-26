from __future__ import annotations


class TDLError(Exception):
    """Base exception for all tdl-sdk errors."""

    def __init__(
        self, message: str, stdout: str = "", stderr: str = "", return_code: int = -1
    ) -> None:
        super().__init__(message)
        self.stdout = stdout
        self.stderr = stderr
        self.return_code = return_code


class TDLNotFoundError(TDLError):
    """Raised when the tdl binary is not found on PATH."""


class TDLCommandError(TDLError):
    """Raised when tdl exits with a non-zero return code."""


class TDLTimeoutError(TDLError):
    """Raised when a tdl command exceeds the timeout."""


class TDLParseError(TDLError):
    """Raised when JSON output from tdl cannot be parsed."""
