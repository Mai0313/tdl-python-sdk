from __future__ import annotations

import subprocess

from pydantic import Field, BaseModel, ConfigDict

from tdl_sdk._models import TDLResult, GlobalOptions, _BaseOptions
from tdl_sdk._exceptions import TDLError, TDLCommandError, TDLTimeoutError, TDLNotFoundError


class TDLRunner(BaseModel):
    """Low-level subprocess runner for the tdl CLI binary."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    tdl_path: str = Field(default="tdl", description="Path to the tdl binary.")
    global_options: GlobalOptions = Field(
        default_factory=GlobalOptions, description="Global options for all tdl commands."
    )

    def run(
        self,
        command: list[str],
        options: _BaseOptions | None = None,
        positional_args: list[str] | None = None,
        timeout: float | None = None,
    ) -> TDLResult:
        """Execute a tdl command.

        Args:
            command: The command path, e.g. ["chat", "ls"] or ["download"].
            options: Command-specific options model.
            positional_args: Positional arguments appended after flags.
            timeout: Timeout in seconds for the command.

        Returns:
            TDLResult with stdout, stderr, and return_code.

        Raises:
            TDLNotFoundError: If the tdl binary is not found.
            TDLCommandError: If tdl exits with a non-zero return code.
            TDLTimeoutError: If the command exceeds the timeout.
        """
        cmd = [self.tdl_path, *self.global_options.cli_args, *command]

        if options is not None:
            cmd.extend(options.cli_args)

        if positional_args:
            cmd.extend(positional_args)

        try:
            result = subprocess.run(  # noqa: S603
                cmd, capture_output=True, text=True, timeout=timeout, check=False
            )
        except FileNotFoundError as e:
            raise TDLNotFoundError(
                f"tdl binary not found at '{self.tdl_path}'. "
                "Make sure tdl is installed and available on PATH."
            ) from e
        except subprocess.TimeoutExpired as e:
            raise TDLTimeoutError(
                f"Command timed out after {timeout}s: {' '.join(cmd)}",
                stdout=e.stdout or "",
                stderr=e.stderr or "",
            ) from e
        except OSError as e:
            raise TDLError(f"Failed to execute tdl: {e}") from e

        if result.returncode != 0:
            raise TDLCommandError(
                f"tdl command failed with exit code {result.returncode}: {result.stderr.strip()}",
                stdout=result.stdout,
                stderr=result.stderr,
                return_code=result.returncode,
            )

        return TDLResult(stdout=result.stdout, stderr=result.stderr, return_code=result.returncode)
