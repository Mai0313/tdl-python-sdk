from __future__ import annotations

from enum import Enum

from pydantic import Field, BaseModel, ConfigDict, computed_field

from tdl_sdk._enums import LoginType, ExportType, ListOutput, ForwardMode


def _dict_to_cli_args(cli_dict: dict[str, object]) -> list[str]:
    """Convert a dict of CLI flag names to a flat list of CLI arguments."""
    args: list[str] = []
    for key, value in cli_dict.items():
        if value is None:
            continue
        flag = f"--{key}"
        if isinstance(value, bool):
            if value:
                args.append(flag)
        elif isinstance(value, list):
            for item in value:
                args.extend([flag, str(item)])
        elif isinstance(value, dict):
            dict_str = ",".join(f"{k}={v}" for k, v in value.items())
            args.extend([flag, dict_str])
        else:
            args.extend([flag, str(value)])
    return args


class _BaseOptions(BaseModel):
    """Base class for all command option models."""

    model_config = ConfigDict(populate_by_name=True, use_attribute_docstrings=True)

    @computed_field
    @property
    def cli_dict(self) -> dict[str, object]:
        """CLI flag dict. Uses alias as key. Skips None and False bools."""
        result: dict[str, object] = {}
        for field_name, field_info in self.model_fields.items():
            value = getattr(self, field_name)
            if value is None:
                continue
            if isinstance(value, bool) and not value:
                continue
            key = field_info.alias or field_name
            if isinstance(value, Enum):
                value = value.value
            result[key] = value
        return result

    @computed_field
    @property
    def cli_args(self) -> list[str]:
        """Flat list of CLI arguments ready for subprocess."""
        return _dict_to_cli_args(self.cli_dict)


# ------------------------------------------------------------------ #
#  Global Options                                                      #
# ------------------------------------------------------------------ #


class GlobalOptions(BaseModel):
    """Global flags shared across all tdl commands."""

    model_config = ConfigDict(use_attribute_docstrings=True)

    debug: bool = Field(default=False, description="Enable debug mode.")
    delay: str | None = Field(default=None, description="Delay between each task, e.g. '5s'.")
    limit: int = Field(default=2, description="Max number of concurrent tasks.")
    ns: str = Field(default="default", description="Namespace for Telegram session.")
    ntp: str | None = Field(default=None, description="NTP server host.")
    pool: int = Field(default=8, description="Size of the DC pool, 0 means infinity.")
    proxy: str | None = Field(
        default=None, description="Proxy address, format: protocol://username:password@host:port."
    )
    reconnect_timeout: str = Field(
        default="5m", description="Telegram client reconnection backoff timeout."
    )
    storage: dict[str, str] | None = Field(
        default=None, description="Storage options, format: type=driver,key1=value1,key2=value2."
    )
    threads: int = Field(default=4, description="Max threads for transfer one item.")

    @computed_field
    @property
    def cli_args(self) -> list[str]:
        """Flat list of global CLI arguments ready for subprocess."""
        flag_map: dict[str, tuple[str, object]] = {
            "debug": ("--debug", False),
            "delay": ("--delay", None),
            "limit": ("--limit", 2),
            "ns": ("--ns", "default"),
            "ntp": ("--ntp", None),
            "pool": ("--pool", 8),
            "proxy": ("--proxy", None),
            "reconnect_timeout": ("--reconnect-timeout", "5m"),
            "threads": ("--threads", 4),
        }
        args: list[str] = []
        for attr, (flag, default) in flag_map.items():
            value = getattr(self, attr)
            if value == default or value is None:
                continue
            if isinstance(value, bool):
                args.append(flag)
            else:
                args.extend([flag, str(value)])

        if self.storage is not None:
            storage_str = ",".join(f"{k}={v}" for k, v in self.storage.items())
            args.extend(["--storage", storage_str])

        return args


# ------------------------------------------------------------------ #
#  Result                                                              #
# ------------------------------------------------------------------ #


class TDLResult(BaseModel):
    """Result from a tdl command execution."""

    model_config = ConfigDict(extra="allow")

    stdout: str = Field(default="", description="Standard output from the command.")
    stderr: str = Field(default="", description="Standard error from the command.")
    return_code: int = Field(default=0, description="Exit code of the command.")


# ------------------------------------------------------------------ #
#  Account Management Options                                          #
# ------------------------------------------------------------------ #


class LoginOptions(_BaseOptions):
    """Options for the `tdl login` command."""

    login_type: LoginType = Field(
        default=LoginType.DESKTOP, alias="type", description="Login mode: desktop, code, or qr."
    )
    desktop: str | None = Field(
        default=None, description="Official desktop client path (auto-find if empty)."
    )
    passcode: str | None = Field(default=None, description="Passcode for desktop client.")


class BackupOptions(_BaseOptions):
    """Options for the `tdl backup` command."""

    dst: str | None = Field(
        default=None, description="Destination file path. Default: <date>.backup.tdl."
    )


class RecoverOptions(_BaseOptions):
    """Options for the `tdl recover` command."""

    file: str = Field(description="Backup file path.")


class MigrateOptions(_BaseOptions):
    """Options for the `tdl migrate` command."""

    to: dict[str, str] = Field(
        description="Destination storage options, e.g. {'type': 'file', 'path': '/new'}."
    )


# ------------------------------------------------------------------ #
#  Chat Options                                                        #
# ------------------------------------------------------------------ #


class ChatListOptions(_BaseOptions):
    """Options for the `tdl chat ls` command."""

    chat_filter: str = Field(
        default="true", alias="filter", description="Filter chats by expression."
    )
    output: ListOutput = Field(
        default=ListOutput.TABLE, description="Output format: table or json."
    )


class ChatExportOptions(_BaseOptions):
    """Options for the `tdl chat export` command."""

    chat: str | None = Field(
        default=None, description="Chat id or domain. None means Saved Messages."
    )
    export_type: ExportType = Field(
        default=ExportType.TIME, alias="type", description="Export type: time, id, or last."
    )
    export_input: list[int] | None = Field(
        default=None, alias="input", description="Input data, depends on export type."
    )
    output: str = Field(default="tdl-export.json", description="Output JSON file path.")
    export_filter: str = Field(
        default="true",
        alias="filter",
        description="Filter messages by expression. Use '-' to see available fields.",
    )
    export_all: bool = Field(
        default=False, alias="all", description="Export all messages including non-media."
    )
    raw: bool = Field(default=False, description="Export raw MTProto struct (for debugging).")
    with_content: bool = Field(default=False, description="Export with message content.")
    reply: int | None = Field(default=None, description="Specify channel post id.")
    topic: int | None = Field(default=None, description="Specify topic id.")


class ChatUsersOptions(_BaseOptions):
    """Options for the `tdl chat users` command."""

    chat: str = Field(description="Domain id (channels, supergroups, etc.).")
    output: str = Field(default="tdl-users.json", description="Output JSON file path.")
    raw: bool = Field(default=False, description="Export raw MTProto struct.")


# ------------------------------------------------------------------ #
#  Download Options                                                    #
# ------------------------------------------------------------------ #


class DownloadOptions(_BaseOptions):
    """Options for the `tdl download` command."""

    url: list[str] | None = Field(default=None, description="Telegram message links.")
    file: list[str] | None = Field(default=None, description="Official client exported files.")
    download_dir: str = Field(
        default="downloads",
        alias="dir",
        description="Download directory (auto-created if not exists).",
    )
    include: list[str] | None = Field(
        default=None, description="Include file extensions, e.g. ['mp4', 'mp3']."
    )
    exclude: list[str] | None = Field(
        default=None, description="Exclude file extensions, e.g. ['png', 'jpg']."
    )
    desc: bool = Field(default=False, description="Download from newest to oldest.")
    continue_download: bool = Field(
        default=False, alias="continue", description="Continue the last download directly."
    )
    restart: bool = Field(default=False, description="Restart the last download directly.")
    rewrite_ext: bool = Field(
        default=False,
        alias="rewrite-ext",
        description="Rewrite file extension according to file header MIME.",
    )
    skip_same: bool = Field(
        default=False,
        alias="skip-same",
        description="Skip files with same name (without ext) and size.",
    )
    takeout: bool = Field(
        default=False, description="Use takeout sessions for lower flood wait limits."
    )
    group: bool = Field(
        default=False, description="Auto detect grouped messages and download all."
    )
    serve: bool = Field(
        default=False, description="Serve media as HTTP server instead of downloading."
    )
    port: int | None = Field(
        default=None, description="HTTP server port (for serve mode). Default: 8080."
    )
    template: str | None = Field(default=None, description="Download file name template.")


# ------------------------------------------------------------------ #
#  Upload Options                                                      #
# ------------------------------------------------------------------ #


class UploadOptions(_BaseOptions):
    """Options for the `tdl upload` command."""

    path: list[str] = Field(description="Dirs or files to upload.")
    chat: str | None = Field(
        default=None, description="Chat id or domain. None means Saved Messages."
    )
    excludes: list[str] | None = Field(default=None, description="Exclude file extensions.")
    photo: bool = Field(default=False, description="Upload image as photo instead of file.")
    rm: bool = Field(default=False, description="Remove uploaded files after uploading.")


# ------------------------------------------------------------------ #
#  Forward Options                                                     #
# ------------------------------------------------------------------ #


class ForwardOptions(_BaseOptions):
    """Options for the `tdl forward` command."""

    forward_from: list[str] = Field(
        alias="from", description="Messages to be forwarded, can be links or exported JSON files."
    )
    to: str = Field(description="Destination peer, can be a CHAT or router expression.")
    mode: ForwardMode = Field(
        default=ForwardMode.DIRECT, description="Forward mode: direct or clone."
    )
    edit: str | None = Field(
        default=None, description="Edit message or caption with expression engine."
    )
    desc: bool = Field(default=False, description="Forward messages in reverse order.")
    dry_run: bool = Field(
        default=False,
        alias="dry-run",
        description="Do not actually send, just show how they would be sent.",
    )
    silent: bool = Field(default=False, description="Send messages silently.")
    single: bool = Field(
        default=False, description="Do not auto-detect and forward grouped messages."
    )


# ------------------------------------------------------------------ #
#  Extension Options                                                   #
# ------------------------------------------------------------------ #


class ExtInstallOptions(_BaseOptions):
    """Options for the `tdl extension install` command."""

    force: bool = Field(
        default=False, description="Force install even if extension already exists."
    )
    dry_run: bool = Field(
        default=False, alias="dry-run", description="Only print what would be done."
    )


class ExtListOptions(_BaseOptions):
    """Options for the `tdl extension list` command."""

    dry_run: bool = Field(
        default=False, alias="dry-run", description="Only print what would be done."
    )


class ExtRemoveOptions(_BaseOptions):
    """Options for the `tdl extension remove` command."""

    dry_run: bool = Field(
        default=False, alias="dry-run", description="Only print what would be done."
    )


class ExtUpgradeOptions(_BaseOptions):
    """Options for the `tdl extension upgrade` command."""

    dry_run: bool = Field(
        default=False, alias="dry-run", description="Only print what would be done."
    )
