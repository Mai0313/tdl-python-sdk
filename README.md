<div align="center" markdown="1">

# TDL Python SDK

[![python](https://img.shields.io/badge/-Python_%7C_3.11%7C_3.12%7C_3.13%7C_3.14-blue?logo=python&logoColor=white)](https://www.python.org/downloads/source/)
[![uv](https://img.shields.io/badge/-uv_dependency_management-2C5F2D?logo=python&logoColor=white)](https://docs.astral.sh/uv/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)](https://docs.pydantic.dev/latest/contributing/#badges)
[![tests](https://github.com/Mai0313/tdl-python-sdk/actions/workflows/test.yml/badge.svg)](https://github.com/Mai0313/tdl-python-sdk/actions/workflows/test.yml)
[![code-quality](https://github.com/Mai0313/tdl-python-sdk/actions/workflows/code-quality-check.yml/badge.svg)](https://github.com/Mai0313/tdl-python-sdk/actions/workflows/code-quality-check.yml)
[![license](https://img.shields.io/badge/License-MIT-green.svg?labelColor=gray)](https://github.com/Mai0313/tdl-python-sdk/tree/main?tab=License-1-ov-file)
[![PRs](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/Mai0313/tdl-python-sdk/pulls)

</div>

A type-safe Python SDK for [TDL](https://github.com/iyear/tdl) (Telegram Downloader). Wraps the `tdl` CLI binary via subprocess and provides a Pythonic, Pydantic-powered interface for all TDL operations.

Other Languages: [English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md)

## Features

- Full coverage of all `tdl` commands: login, chat, download, upload, forward, backup, recover, migrate, extension
- Strict typing with Pydantic BaseModel for all options and results
- Enum types for mode/type parameters (LoginType, ExportType, ForwardMode, ListOutput)
- Custom exception hierarchy with stdout/stderr/return_code attached
- CLI flag serialization via `@computed_field` properties

## Prerequisites

Install the [TDL](https://github.com/iyear/tdl) CLI tool first:

```bash
# macOS / Linux
curl -sSL https://docs.iyear.me/tdl/install.sh | bash

# or via Go
go install github.com/iyear/tdl@latest
```

Verify installation:

```bash
tdl version
```

## Installation

```bash
pip install tdl-python-sdk

# or with uv
uv add tdl-python-sdk
```

## Quick Start

```python
from tdl_sdk import TDL, GlobalOptions, LoginOptions, LoginType

# Create client with global options
client = TDL(global_options=GlobalOptions(ns="my_session", proxy="socks5://127.0.0.1:1080"))

# Login via QR code
client.login(LoginOptions(login_type=LoginType.QR))
```

## Usage Guide

### Login

TDL supports three login methods: desktop client, verification code, and QR code.

```python
from tdl_sdk import TDL, LoginOptions, LoginType

client = TDL()

# Login via QR code (recommended)
client.login(LoginOptions(login_type=LoginType.QR))

# Login via desktop client (auto-detect path)
client.login(LoginOptions(login_type=LoginType.DESKTOP))

# Login via desktop client with custom path and passcode
client.login(
    LoginOptions(
        login_type=LoginType.DESKTOP, desktop="/path/to/Telegram Desktop", passcode="your_passcode"
    )
)

# Login via verification code
client.login(LoginOptions(login_type=LoginType.CODE))
```

### Chat Operations

#### List Chats

```python
from tdl_sdk import TDL, ChatListOptions, ListOutput

client = TDL()

# List all chats as table
client.chat_ls()

# List chats as JSON with filter
result = client.chat_ls(ChatListOptions(output=ListOutput.JSON, chat_filter="Type == 'channel'"))
print(result.stdout)
```

#### Export Messages

```python
from tdl_sdk import TDL, ChatExportOptions, ExportType

client = TDL()

# Export last 100 messages from a channel
client.chat_export(
    ChatExportOptions(
        chat="my_channel",
        export_type=ExportType.LAST,
        export_input=[100],
        output="export.json",
        with_content=True,
    )
)

# Export all messages (including non-media)
client.chat_export(
    ChatExportOptions(
        chat="my_channel", export_all=True, with_content=True, output="full_export.json"
    )
)
```

#### Export Users

```python
from tdl_sdk import TDL, ChatUsersOptions

client = TDL()

# Export all users from a channel
client.chat_users(ChatUsersOptions(chat="my_channel", output="users.json"))
```

### Download

```python
from tdl_sdk import TDL, DownloadOptions

client = TDL()

# Download by Telegram message links
client.download(
    DownloadOptions(
        url=["https://t.me/channel/123", "https://t.me/channel/456"], download_dir="./downloads"
    )
)

# Download from exported JSON with filters
client.download(
    DownloadOptions(
        file=["export.json"],
        download_dir="./media",
        include=["mp4", "mkv"],  # only video files
        skip_same=True,  # skip duplicates
        takeout=True,  # use takeout for lower flood limits
        template="{{ .DialogID }}_{{ .MessageID }}_{{ filenamify .FileName }}",
    )
)

# Serve media as HTTP server
client.download(DownloadOptions(file=["export.json"], serve=True, port=9090))
```

### Upload

```python
from tdl_sdk import TDL, UploadOptions

client = TDL()

# Upload files to Saved Messages
client.upload(UploadOptions(path=["/data/video.mp4", "/data/photos/"]))

# Upload to a specific chat as photos
client.upload(UploadOptions(path=["./images/"], chat="my_channel", photo=True))

# Upload and remove local files after success
client.upload(UploadOptions(path=["./temp_files/"], chat="my_channel", rm=True))
```

### Forward

```python
from tdl_sdk import TDL, ForwardOptions, ForwardMode

client = TDL()

# Forward messages (direct mode)
client.forward(
    ForwardOptions(forward_from=["https://t.me/source_channel/123"], to="target_channel")
)

# Clone messages (no forward header)
client.forward(
    ForwardOptions(
        forward_from=["https://t.me/source/123", "export.json"],
        to="target_channel",
        mode=ForwardMode.CLONE,
        silent=True,
    )
)

# Dry run to preview
result = client.forward(
    ForwardOptions(forward_from=["export.json"], to="target_channel", dry_run=True)
)
print(result.stdout)
```

### Backup / Recover / Migrate

```python
from tdl_sdk import TDL, BackupOptions, RecoverOptions, MigrateOptions

client = TDL()

# Backup session data
client.backup(BackupOptions(dst="./my_backup.tdl"))

# Recover from backup
client.recover(RecoverOptions(file="./my_backup.tdl"))

# Migrate to file-based storage
client.migrate(MigrateOptions(to={"type": "file", "path": "/new/storage"}))
```

### Extension Management

```python
from tdl_sdk import TDL, ExtInstallOptions

client = TDL()

# Install an extension
client.ext_install("github.com/user/tdl-ext-name")

# Force reinstall
client.ext_install("github.com/user/tdl-ext-name", ExtInstallOptions(force=True))

# List installed extensions
result = client.ext_list()
print(result.stdout)

# Upgrade / Remove
client.ext_upgrade("ext-name")
client.ext_remove("ext-name")
```

### Error Handling

```python
from tdl_sdk import TDL, DownloadOptions
from tdl_sdk import TDLError, TDLNotFoundError, TDLCommandError, TDLTimeoutError

client = TDL(timeout=300)

try:
    client.download(DownloadOptions(url=["https://t.me/channel/123"]))
except TDLNotFoundError:
    print("tdl binary not found. Please install tdl first.")
except TDLTimeoutError as e:
    print(f"Command timed out: {e}")
except TDLCommandError as e:
    print(f"Command failed (exit code {e.return_code}): {e.stderr}")
except TDLError as e:
    print(f"Unexpected error: {e}")
```

### Global Options

Configure shared settings for all commands:

```python
from tdl_sdk import TDL, GlobalOptions

client = TDL(
    global_options=GlobalOptions(
        ns="work_session",  # session namespace
        proxy="socks5://127.0.0.1:1080",
        threads=8,  # max threads per transfer
        limit=4,  # max concurrent tasks
        pool=16,  # DC pool size
        debug=True,  # enable debug output
        reconnect_timeout="10m",
        storage={"type": "bolt", "path": "/custom/data"},
    ),
    tdl_path="/usr/local/bin/tdl",  # custom binary path
    timeout=600,  # default timeout (seconds)
)
```

## Architecture

```
src/tdl_sdk/
    __init__.py          # Public API exports
    _exceptions.py       # TDLError hierarchy
    _enums.py            # LoginType, ExportType, ForwardMode, ListOutput
    _models.py           # Pydantic models (GlobalOptions, *Options, TDLResult)
    _runner.py           # TDLRunner - subprocess execution layer
    _client.py           # TDL - user-facing facade
```

All classes are Pydantic BaseModel. Option models provide `cli_dict` and `cli_args` as `@computed_field` properties for automatic CLI flag serialization.

## Development

```bash
git clone https://github.com/Mai0313/tdl-python-sdk.git
cd tdl-python-sdk
uv sync
make test
```

## License

MIT
