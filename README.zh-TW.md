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

型別安全的 [TDL](https://github.com/iyear/tdl)（Telegram Downloader）Python SDK。透過 subprocess 包裝 `tdl` CLI，提供 Pydantic 驅動的 Pythonic 介面。

其他語言: [English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md)

## 特色

- 完整覆蓋所有 `tdl` 命令：login、chat、download、upload、forward、backup、recover、migrate、extension
- 使用 Pydantic BaseModel 嚴格定義所有選項與結果型態
- Enum 型別對應模式/類型參數（LoginType、ExportType、ForwardMode、ListOutput）
- 自訂例外階層，附帶 stdout/stderr/return_code
- 透過 `@computed_field` 屬性自動序列化 CLI flags

## 前置需求

請先安裝 [TDL](https://github.com/iyear/tdl) CLI 工具：

```bash
# macOS / Linux
curl -sSL https://docs.iyear.me/tdl/install.sh | bash

# 或透過 Go
go install github.com/iyear/tdl@latest
```

確認安裝成功：

```bash
tdl version
```

## 安裝

```bash
pip install tdl-python-sdk

# 或使用 uv
uv add tdl-python-sdk
```

## 快速開始

```python
from tdl_sdk import TDL, GlobalOptions, LoginOptions, LoginType

# 建立帶有全域選項的客戶端
client = TDL(global_options=GlobalOptions(ns="my_session", proxy="socks5://127.0.0.1:1080"))

# 透過 QR code 登入
client.login(LoginOptions(login_type=LoginType.QR))
```

## 使用指南

### 登入

TDL 支援三種登入方式：桌面客戶端、驗證碼、QR code。

```python
from tdl_sdk import TDL, LoginOptions, LoginType

client = TDL()

# 透過 QR code 登入（推薦）
client.login(LoginOptions(login_type=LoginType.QR))

# 透過桌面客戶端登入（自動偵測路徑）
client.login(LoginOptions(login_type=LoginType.DESKTOP))

# 指定桌面客戶端路徑與密碼
client.login(
    LoginOptions(
        login_type=LoginType.DESKTOP, desktop="/path/to/Telegram Desktop", passcode="your_passcode"
    )
)

# 透過驗證碼登入
client.login(LoginOptions(login_type=LoginType.CODE))
```

### 聊天操作

#### 列出聊天

```python
from tdl_sdk import TDL, ChatListOptions, ListOutput

client = TDL()

# 以表格列出所有聊天
client.chat_ls()

# 以 JSON 格式列出，加上篩選條件
result = client.chat_ls(ChatListOptions(output=ListOutput.JSON, chat_filter="Type == 'channel'"))
print(result.stdout)
```

#### 匯出訊息

```python
from tdl_sdk import TDL, ChatExportOptions, ExportType

client = TDL()

# 匯出頻道最近 100 則訊息
client.chat_export(
    ChatExportOptions(
        chat="my_channel",
        export_type=ExportType.LAST,
        export_input=[100],
        output="export.json",
        with_content=True,
    )
)

# 匯出所有訊息（包含非媒體）
client.chat_export(
    ChatExportOptions(
        chat="my_channel", export_all=True, with_content=True, output="full_export.json"
    )
)
```

#### 匯出使用者

```python
from tdl_sdk import TDL, ChatUsersOptions

client = TDL()

# 匯出頻道所有使用者
client.chat_users(ChatUsersOptions(chat="my_channel", output="users.json"))
```

### 下載

```python
from tdl_sdk import TDL, DownloadOptions

client = TDL()

# 透過 Telegram 訊息連結下載
client.download(
    DownloadOptions(
        url=["https://t.me/channel/123", "https://t.me/channel/456"], download_dir="./downloads"
    )
)

# 從匯出的 JSON 下載，附帶篩選條件
client.download(
    DownloadOptions(
        file=["export.json"],
        download_dir="./media",
        include=["mp4", "mkv"],  # 僅影片檔案
        skip_same=True,  # 跳過重複檔案
        takeout=True,  # 使用 takeout 降低限流
        template="{{ .DialogID }}_{{ .MessageID }}_{{ filenamify .FileName }}",
    )
)

# 以 HTTP 伺服器提供媒體
client.download(DownloadOptions(file=["export.json"], serve=True, port=9090))
```

### 上傳

```python
from tdl_sdk import TDL, UploadOptions

client = TDL()

# 上傳檔案到「已儲存的訊息」
client.upload(UploadOptions(path=["/data/video.mp4", "/data/photos/"]))

# 上傳到指定聊天（以照片形式）
client.upload(UploadOptions(path=["./images/"], chat="my_channel", photo=True))

# 上傳後刪除本地檔案
client.upload(UploadOptions(path=["./temp_files/"], chat="my_channel", rm=True))
```

### 轉發

```python
from tdl_sdk import TDL, ForwardOptions, ForwardMode

client = TDL()

# 直接轉發訊息
client.forward(
    ForwardOptions(forward_from=["https://t.me/source_channel/123"], to="target_channel")
)

# 複製訊息（無轉發標頭）
client.forward(
    ForwardOptions(
        forward_from=["https://t.me/source/123", "export.json"],
        to="target_channel",
        mode=ForwardMode.CLONE,
        silent=True,
    )
)

# 預覽模式（不實際傳送）
result = client.forward(
    ForwardOptions(forward_from=["export.json"], to="target_channel", dry_run=True)
)
print(result.stdout)
```

### 備份 / 還原 / 遷移

```python
from tdl_sdk import TDL, BackupOptions, RecoverOptions, MigrateOptions

client = TDL()

# 備份 session 資料
client.backup(BackupOptions(dst="./my_backup.tdl"))

# 從備份還原
client.recover(RecoverOptions(file="./my_backup.tdl"))

# 遷移到檔案式儲存
client.migrate(MigrateOptions(to={"type": "file", "path": "/new/storage"}))
```

### 擴充套件管理

```python
from tdl_sdk import TDL, ExtInstallOptions

client = TDL()

# 安裝擴充套件
client.ext_install("github.com/user/tdl-ext-name")

# 強制重新安裝
client.ext_install("github.com/user/tdl-ext-name", ExtInstallOptions(force=True))

# 列出已安裝擴充套件
result = client.ext_list()
print(result.stdout)

# 升級 / 移除
client.ext_upgrade("ext-name")
client.ext_remove("ext-name")
```

### 錯誤處理

```python
from tdl_sdk import TDL, DownloadOptions
from tdl_sdk import TDLError, TDLNotFoundError, TDLCommandError, TDLTimeoutError

client = TDL(timeout=300)

try:
    client.download(DownloadOptions(url=["https://t.me/channel/123"]))
except TDLNotFoundError:
    print("找不到 tdl 執行檔，請先安裝 tdl。")
except TDLTimeoutError as e:
    print(f"命令逾時：{e}")
except TDLCommandError as e:
    print(f"命令失敗（exit code {e.return_code}）：{e.stderr}")
except TDLError as e:
    print(f"未預期錯誤：{e}")
```

### 全域選項

為所有命令設定共用參數：

```python
from tdl_sdk import TDL, GlobalOptions

client = TDL(
    global_options=GlobalOptions(
        ns="work_session",  # session 命名空間
        proxy="socks5://127.0.0.1:1080",
        threads=8,  # 每項傳輸的最大執行緒
        limit=4,  # 最大並行任務數
        pool=16,  # DC 連線池大小
        debug=True,  # 啟用除錯輸出
        reconnect_timeout="10m",
        storage={"type": "bolt", "path": "/custom/data"},
    ),
    tdl_path="/usr/local/bin/tdl",  # 自訂 binary 路徑
    timeout=600,  # 預設逾時（秒）
)
```

## 架構

```
src/tdl_sdk/
    __init__.py          # 公開 API 匯出
    _exceptions.py       # TDLError 例外階層
    _enums.py            # LoginType, ExportType, ForwardMode, ListOutput
    _models.py           # Pydantic models (GlobalOptions, *Options, TDLResult)
    _runner.py           # TDLRunner - subprocess 執行層
    _client.py           # TDL - 使用者介面 facade
```

所有 class 皆為 Pydantic BaseModel。選項模型透過 `@computed_field` 屬性提供 `cli_dict` 和 `cli_args`，自動序列化為 CLI flags。

## 開發

```bash
git clone https://github.com/Mai0313/tdl-python-sdk.git
cd tdl-python-sdk
uv sync
make test
```

## 授權

MIT
