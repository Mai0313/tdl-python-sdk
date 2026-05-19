<div align="center" markdown="1">

# TDL Python SDK

[![PyPI version](https://img.shields.io/pypi/v/tdl-python-sdk.svg)](https://pypi.org/project/tdl-python-sdk/)
[![python](https://img.shields.io/badge/Python-%3E%3D3.11-blue?logo=python&logoColor=white)](https://www.python.org/downloads/source/)
[![uv](https://img.shields.io/badge/-uv_dependency_management-2C5F2D?logo=python&logoColor=white)](https://docs.astral.sh/uv/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)](https://docs.pydantic.dev/latest/contributing/#badges)
[![tests](https://github.com/Mai0313/tdl-python-sdk/actions/workflows/test.yml/badge.svg)](https://github.com/Mai0313/tdl-python-sdk/actions/workflows/test.yml)
[![code-quality](https://github.com/Mai0313/tdl-python-sdk/actions/workflows/code-quality-check.yml/badge.svg)](https://github.com/Mai0313/tdl-python-sdk/actions/workflows/code-quality-check.yml)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/Mai0313/tdl-python-sdk)
[![license](https://img.shields.io/badge/License-MIT-green.svg?labelColor=gray)](https://github.com/Mai0313/tdl-python-sdk/tree/main?tab=License-1-ov-file)
[![PRs](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/Mai0313/tdl-python-sdk/pulls)
[![contributors](https://img.shields.io/github/contributors/Mai0313/tdl-python-sdk.svg)](https://github.com/Mai0313/tdl-python-sdk/graphs/contributors)

</div>

类型安全的 [TDL](https://github.com/iyear/tdl)（Telegram Downloader）Python SDK。这个 package 通过 subprocess 执行外部 `tdl` CLI binary，并提供由 Pydantic 驱动的 Python API，可用于 login、chat export、download、upload、forward、backup、recover、migrate 和 extension 操作。

其他语言: [English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md)

## 特性

- 主要 `tdl` command groups 的 Python facade。
- 使用 Pydantic option models 做 validation 和 CLI flag serialization。
- 以 Enum types 表示常用的 mode 和 output parameters。
- 结构化 `TDLResult` responses，包含 stdout、stderr 和 return code。
- 针对 missing binaries、command failures 和 timeouts 提供 custom exceptions。

## 要求

- Python 3.11 或更新版本。CI 目前验证 Python 3.11、3.12 和 3.13。
- 需要另外安装 [TDL](https://github.com/iyear/tdl) CLI binary。

先安装 `tdl`：

```bash
# macOS / Linux
curl -sSL https://docs.iyear.me/tdl/install.sh | bash

# or via Go
go install github.com/iyear/tdl@latest
```

确认 binary 可用：

```bash
tdl version
```

## 安装

```bash
pip install tdl-python-sdk

# or with uv
uv add tdl-python-sdk
```

## 快速开始

```python
from tdl_sdk import GlobalOptions, LoginOptions, LoginType, TDL

client = TDL(global_options=GlobalOptions(ns="my_session", proxy="socks5://127.0.0.1:1080"))

client.login(LoginOptions(login_type=LoginType.QR))
```

当 binary 不在 `PATH` 上时，请使用 `tdl_path`：

```python
from tdl_sdk import TDL

client = TDL(tdl_path="/usr/local/bin/tdl", timeout=600)
```

## 常见用法

### 登录

TDL 支持 desktop、verification code 和 QR login flows。

```python
from tdl_sdk import LoginOptions, LoginType, TDL

client = TDL()

client.login(LoginOptions(login_type=LoginType.QR))
client.login(LoginOptions(login_type=LoginType.DESKTOP))
client.login(
    LoginOptions(
        login_type=LoginType.DESKTOP, desktop="/path/to/Telegram Desktop", passcode="your_passcode"
    )
)
client.login(LoginOptions(login_type=LoginType.CODE))
```

### Chat 操作

```python
from tdl_sdk import (
    ChatExportOptions,
    ChatListOptions,
    ChatUsersOptions,
    ExportType,
    ListOutput,
    TDL,
)

client = TDL()

result = client.chat_ls(ChatListOptions(output=ListOutput.JSON, chat_filter="Type == 'channel'"))
print(result.stdout)

client.chat_export(
    ChatExportOptions(
        chat="my_channel",
        export_type=ExportType.LAST,
        export_input=[100],
        output="export.json",
        with_content=True,
    )
)

client.chat_users(ChatUsersOptions(chat="my_channel", output="users.json"))
```

### Download

```python
from tdl_sdk import DownloadOptions, TDL

client = TDL()

client.download(
    DownloadOptions(
        url=["https://t.me/channel/123", "https://t.me/channel/456"], download_dir="./downloads"
    )
)

client.download(
    DownloadOptions(
        file=["export.json"],
        download_dir="./media",
        include=["mp4", "mkv"],
        skip_same=True,
        takeout=True,
        template="{{ .DialogID }}_{{ .MessageID }}_{{ filenamify .FileName }}",
    )
)

client.download(DownloadOptions(file=["export.json"], serve=True, port=9090))
```

### Upload

```python
from tdl_sdk import TDL, UploadOptions

client = TDL()

client.upload(UploadOptions(path=["/data/video.mp4", "/data/photos/"]))
client.upload(UploadOptions(path=["./images/"], chat="my_channel", photo=True))
client.upload(UploadOptions(path=["./temp_files/"], chat="my_channel", rm=True))
```

### Forward

```python
from tdl_sdk import ForwardMode, ForwardOptions, TDL

client = TDL()

client.forward(
    ForwardOptions(forward_from=["https://t.me/source_channel/123"], to="target_channel")
)

client.forward(
    ForwardOptions(
        forward_from=["https://t.me/source/123", "export.json"],
        to="target_channel",
        mode=ForwardMode.CLONE,
        silent=True,
    )
)

result = client.forward(
    ForwardOptions(forward_from=["export.json"], to="target_channel", dry_run=True)
)
print(result.stdout)
```

### Backup、Recover 和 Migrate

```python
from tdl_sdk import BackupOptions, MigrateOptions, RecoverOptions, TDL

client = TDL()

client.backup(BackupOptions(dst="./my_backup.tdl"))
client.recover(RecoverOptions(file="./my_backup.tdl"))
client.migrate(MigrateOptions(to={"type": "file", "path": "/new/storage"}))
```

### Extensions

```python
from tdl_sdk import ExtInstallOptions, TDL

client = TDL()

client.ext_install("github.com/user/tdl-ext-name")
client.ext_install("github.com/user/tdl-ext-name", ExtInstallOptions(force=True))

result = client.ext_list()
print(result.stdout)

client.ext_upgrade("ext-name")
client.ext_remove("ext-name")
```

## 错误处理

```python
from tdl_sdk import DownloadOptions, TDL
from tdl_sdk import TDLCommandError, TDLError, TDLNotFoundError, TDLTimeoutError

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

## Global Options

Global options 会在 command path 前序列化，并套用到 client 执行的每个 `tdl` command。

```python
from tdl_sdk import GlobalOptions, TDL

client = TDL(
    global_options=GlobalOptions(
        ns="work_session",
        proxy="socks5://127.0.0.1:1080",
        threads=8,
        limit=4,
        pool=16,
        debug=True,
        reconnect_timeout="10m",
        storage={"type": "bolt", "path": "/custom/data"},
    ),
    tdl_path="/usr/local/bin/tdl",
    timeout=600,
)
```

## 资源

- [API documentation](https://mai0313.github.io/tdl-python-sdk)
- [TDL upstream project](https://github.com/iyear/tdl)
- [Contributing guide](.github/CONTRIBUTING.md)

## 许可证

MIT
