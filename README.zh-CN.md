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

类型安全的 [TDL](https://github.com/iyear/tdl)（Telegram Downloader）Python SDK。通过 subprocess 包装 `tdl` CLI，提供 Pydantic 驱动的 Pythonic 接口。

其他语言: [English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md)

## 特性

- 完整覆盖所有 `tdl` 命令：login、chat、download、upload、forward、backup、recover、migrate、extension
- 使用 Pydantic BaseModel 严格定义所有选项与结果类型
- Enum 类型对应模式/类型参数（LoginType、ExportType、ForwardMode、ListOutput）
- 自定义异常层次，附带 stdout/stderr/return_code
- 通过 `@computed_field` 属性自动序列化 CLI flags

## 前置要求

请先安装 [TDL](https://github.com/iyear/tdl) CLI 工具：

```bash
# macOS / Linux
curl -sSL https://docs.iyear.me/tdl/install.sh | bash

# 或通过 Go
go install github.com/iyear/tdl@latest
```

确认安装成功：

```bash
tdl version
```

## 安装

```bash
pip install tdl-python-sdk

# 或使用 uv
uv add tdl-python-sdk
```

## 快速开始

```python
from tdl_sdk import TDL, GlobalOptions, LoginOptions, LoginType

# 创建带有全局选项的客户端
client = TDL(global_options=GlobalOptions(ns="my_session", proxy="socks5://127.0.0.1:1080"))

# 通过 QR code 登录
client.login(LoginOptions(login_type=LoginType.QR))
```

## 使用指南

### 登录

TDL 支持三种登录方式：桌面客户端、验证码、QR code。

```python
from tdl_sdk import TDL, LoginOptions, LoginType

client = TDL()

# 通过 QR code 登录（推荐）
client.login(LoginOptions(login_type=LoginType.QR))

# 通过桌面客户端登录（自动检测路径）
client.login(LoginOptions(login_type=LoginType.DESKTOP))

# 指定桌面客户端路径与密码
client.login(
    LoginOptions(
        login_type=LoginType.DESKTOP, desktop="/path/to/Telegram Desktop", passcode="your_passcode"
    )
)

# 通过验证码登录
client.login(LoginOptions(login_type=LoginType.CODE))
```

### 聊天操作

#### 列出聊天

```python
from tdl_sdk import TDL, ChatListOptions, ListOutput

client = TDL()

# 以表格列出所有聊天
client.chat_ls()

# 以 JSON 格式列出，加上筛选条件
result = client.chat_ls(ChatListOptions(output=ListOutput.JSON, chat_filter="Type == 'channel'"))
print(result.stdout)
```

#### 导出消息

```python
from tdl_sdk import TDL, ChatExportOptions, ExportType

client = TDL()

# 导出频道最近 100 条消息
client.chat_export(
    ChatExportOptions(
        chat="my_channel",
        export_type=ExportType.LAST,
        export_input=[100],
        output="export.json",
        with_content=True,
    )
)

# 导出所有消息（包含非媒体）
client.chat_export(
    ChatExportOptions(
        chat="my_channel", export_all=True, with_content=True, output="full_export.json"
    )
)
```

#### 导出用户

```python
from tdl_sdk import TDL, ChatUsersOptions

client = TDL()

# 导出频道所有用户
client.chat_users(ChatUsersOptions(chat="my_channel", output="users.json"))
```

### 下载

```python
from tdl_sdk import TDL, DownloadOptions

client = TDL()

# 通过 Telegram 消息链接下载
client.download(
    DownloadOptions(
        url=["https://t.me/channel/123", "https://t.me/channel/456"], download_dir="./downloads"
    )
)

# 从导出的 JSON 下载，附带筛选条件
client.download(
    DownloadOptions(
        file=["export.json"],
        download_dir="./media",
        include=["mp4", "mkv"],  # 仅视频文件
        skip_same=True,  # 跳过重复文件
        takeout=True,  # 使用 takeout 降低限流
        template="{{ .DialogID }}_{{ .MessageID }}_{{ filenamify .FileName }}",
    )
)

# 以 HTTP 服务器提供媒体
client.download(DownloadOptions(file=["export.json"], serve=True, port=9090))
```

### 上传

```python
from tdl_sdk import TDL, UploadOptions

client = TDL()

# 上传文件到「已保存的消息」
client.upload(UploadOptions(path=["/data/video.mp4", "/data/photos/"]))

# 上传到指定聊天（以照片形式）
client.upload(UploadOptions(path=["./images/"], chat="my_channel", photo=True))

# 上传后删除本地文件
client.upload(UploadOptions(path=["./temp_files/"], chat="my_channel", rm=True))
```

### 转发

```python
from tdl_sdk import TDL, ForwardOptions, ForwardMode

client = TDL()

# 直接转发消息
client.forward(
    ForwardOptions(forward_from=["https://t.me/source_channel/123"], to="target_channel")
)

# 复制消息（无转发标头）
client.forward(
    ForwardOptions(
        forward_from=["https://t.me/source/123", "export.json"],
        to="target_channel",
        mode=ForwardMode.CLONE,
        silent=True,
    )
)

# 预览模式（不实际发送）
result = client.forward(
    ForwardOptions(forward_from=["export.json"], to="target_channel", dry_run=True)
)
print(result.stdout)
```

### 备份 / 恢复 / 迁移

```python
from tdl_sdk import TDL, BackupOptions, RecoverOptions, MigrateOptions

client = TDL()

# 备份 session 数据
client.backup(BackupOptions(dst="./my_backup.tdl"))

# 从备份恢复
client.recover(RecoverOptions(file="./my_backup.tdl"))

# 迁移到文件式存储
client.migrate(MigrateOptions(to={"type": "file", "path": "/new/storage"}))
```

### 扩展管理

```python
from tdl_sdk import TDL, ExtInstallOptions

client = TDL()

# 安装扩展
client.ext_install("github.com/user/tdl-ext-name")

# 强制重新安装
client.ext_install("github.com/user/tdl-ext-name", ExtInstallOptions(force=True))

# 列出已安装扩展
result = client.ext_list()
print(result.stdout)

# 升级 / 移除
client.ext_upgrade("ext-name")
client.ext_remove("ext-name")
```

### 错误处理

```python
from tdl_sdk import TDL, DownloadOptions
from tdl_sdk import TDLError, TDLNotFoundError, TDLCommandError, TDLTimeoutError

client = TDL(timeout=300)

try:
    client.download(DownloadOptions(url=["https://t.me/channel/123"]))
except TDLNotFoundError:
    print("找不到 tdl 可执行文件，请先安装 tdl。")
except TDLTimeoutError as e:
    print(f"命令超时：{e}")
except TDLCommandError as e:
    print(f"命令失败（exit code {e.return_code}）：{e.stderr}")
except TDLError as e:
    print(f"未预期错误：{e}")
```

### 全局选项

为所有命令配置共享参数：

```python
from tdl_sdk import TDL, GlobalOptions

client = TDL(
    global_options=GlobalOptions(
        ns="work_session",  # session 命名空间
        proxy="socks5://127.0.0.1:1080",
        threads=8,  # 每项传输的最大线程数
        limit=4,  # 最大并发任务数
        pool=16,  # DC 连接池大小
        debug=True,  # 启用调试输出
        reconnect_timeout="10m",
        storage={"type": "bolt", "path": "/custom/data"},
    ),
    tdl_path="/usr/local/bin/tdl",  # 自定义 binary 路径
    timeout=600,  # 默认超时（秒）
)
```

## 架构

```
src/tdl_sdk/
    __init__.py          # 公开 API 导出
    _exceptions.py       # TDLError 异常层次
    _enums.py            # LoginType, ExportType, ForwardMode, ListOutput
    _models.py           # Pydantic models (GlobalOptions, *Options, TDLResult)
    _runner.py           # TDLRunner - subprocess 执行层
    _client.py           # TDL - 用户接口 facade
```

所有 class 均为 Pydantic BaseModel。选项模型通过 `@computed_field` 属性提供 `cli_dict` 和 `cli_args`，自动序列化为 CLI flags。

## 开发

```bash
git clone https://github.com/Mai0313/tdl-python-sdk.git
cd tdl-python-sdk
uv sync
make test
```

## 许可证

MIT
