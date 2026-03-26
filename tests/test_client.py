from unittest.mock import MagicMock, patch

from tdl_sdk import (
    TDL,
    LoginType,
    ExportType,
    ListOutput,
    ForwardMode,
    LoginOptions,
    BackupOptions,
    UploadOptions,
    ExtListOptions,
    ForwardOptions,
    MigrateOptions,
    RecoverOptions,
    ChatListOptions,
    DownloadOptions,
    ChatUsersOptions,
    ExtRemoveOptions,
    ChatExportOptions,
    ExtInstallOptions,
    ExtUpgradeOptions,
)
from tdl_sdk._models import TDLResult, GlobalOptions

MOCK_RESULT = TDLResult(stdout="ok", stderr="", return_code=0)


class TestTDLInit:
    def test_default_init(self) -> None:
        client = TDL()
        assert client.global_options.ns == "default"
        assert client.global_options.threads == 4
        assert client.tdl_path == "tdl"
        assert client.timeout is None

    def test_custom_init(self) -> None:
        opts = GlobalOptions(ns="test", proxy="socks5://localhost:1080", threads=8)
        client = TDL(global_options=opts)
        assert client.global_options.ns == "test"
        assert client.global_options.proxy == "socks5://localhost:1080"
        assert client.global_options.threads == 8

    def test_runner_computed(self) -> None:
        client = TDL(tdl_path="/custom/tdl")
        assert client.runner.tdl_path == "/custom/tdl"
        assert client.runner.global_options == client.global_options


class TestLogin:
    @patch("tdl_sdk._runner.TDLRunner.run", return_value=MOCK_RESULT)
    def test_login_default(self, mock_run: MagicMock) -> None:
        client = TDL()
        client.login()
        opts = mock_run.call_args[1].get("options") or mock_run.call_args[0][1]
        assert isinstance(opts, LoginOptions)
        assert opts.login_type == LoginType.DESKTOP

    @patch("tdl_sdk._runner.TDLRunner.run", return_value=MOCK_RESULT)
    def test_login_qr(self, mock_run: MagicMock) -> None:
        client = TDL()
        client.login(LoginOptions(login_type=LoginType.QR))
        opts = mock_run.call_args[0][1]
        assert isinstance(opts, LoginOptions)
        assert opts.login_type == LoginType.QR

    @patch("tdl_sdk._runner.TDLRunner.run", return_value=MOCK_RESULT)
    def test_login_desktop_with_passcode(self, mock_run: MagicMock) -> None:
        client = TDL()
        client.login(
            LoginOptions(login_type=LoginType.DESKTOP, desktop="/path/to/tg", passcode="1234")
        )
        opts = mock_run.call_args[0][1]
        assert opts.desktop == "/path/to/tg"
        assert opts.passcode == "1234"


class TestBackupRecover:
    @patch("tdl_sdk._runner.TDLRunner.run", return_value=MOCK_RESULT)
    def test_backup(self, mock_run: MagicMock) -> None:
        client = TDL()
        client.backup(BackupOptions(dst="/backups/today.tdl"))
        opts = mock_run.call_args[0][1]
        assert isinstance(opts, BackupOptions)
        assert opts.dst == "/backups/today.tdl"

    @patch("tdl_sdk._runner.TDLRunner.run", return_value=MOCK_RESULT)
    def test_recover(self, mock_run: MagicMock) -> None:
        client = TDL()
        client.recover(RecoverOptions(file="/backups/today.tdl"))
        opts = mock_run.call_args[0][1]
        assert isinstance(opts, RecoverOptions)
        assert opts.file == "/backups/today.tdl"

    @patch("tdl_sdk._runner.TDLRunner.run", return_value=MOCK_RESULT)
    def test_migrate(self, mock_run: MagicMock) -> None:
        client = TDL()
        client.migrate(MigrateOptions(to={"type": "file", "path": "/new"}))
        opts = mock_run.call_args[0][1]
        assert isinstance(opts, MigrateOptions)
        assert opts.to == {"type": "file", "path": "/new"}


class TestChat:
    @patch("tdl_sdk._runner.TDLRunner.run", return_value=MOCK_RESULT)
    def test_chat_ls(self, mock_run: MagicMock) -> None:
        client = TDL()
        client.chat_ls(ChatListOptions(output=ListOutput.JSON))
        opts = mock_run.call_args[0][1]
        assert isinstance(opts, ChatListOptions)
        assert opts.output == ListOutput.JSON

    @patch("tdl_sdk._runner.TDLRunner.run", return_value=MOCK_RESULT)
    def test_chat_export(self, mock_run: MagicMock) -> None:
        client = TDL()
        client.chat_export(
            ChatExportOptions(
                chat="my_channel",
                export_type=ExportType.LAST,
                export_input=[100],
                with_content=True,
            )
        )
        opts = mock_run.call_args[0][1]
        assert isinstance(opts, ChatExportOptions)
        assert opts.chat == "my_channel"
        assert opts.export_type == ExportType.LAST
        assert opts.export_input == [100]
        assert opts.with_content is True

    @patch("tdl_sdk._runner.TDLRunner.run", return_value=MOCK_RESULT)
    def test_chat_users(self, mock_run: MagicMock) -> None:
        client = TDL()
        client.chat_users(ChatUsersOptions(chat="my_channel"))
        opts = mock_run.call_args[0][1]
        assert isinstance(opts, ChatUsersOptions)
        assert opts.chat == "my_channel"


class TestDownload:
    @patch("tdl_sdk._runner.TDLRunner.run", return_value=MOCK_RESULT)
    def test_download_by_url(self, mock_run: MagicMock) -> None:
        client = TDL()
        client.download(DownloadOptions(url=["https://t.me/c/123"]))
        opts = mock_run.call_args[0][1]
        assert isinstance(opts, DownloadOptions)
        assert opts.url == ["https://t.me/c/123"]

    @patch("tdl_sdk._runner.TDLRunner.run", return_value=MOCK_RESULT)
    def test_download_with_options(self, mock_run: MagicMock) -> None:
        client = TDL()
        client.download(
            DownloadOptions(
                file=["export.json"],
                download_dir="/data",
                include=["mp4"],
                skip_same=True,
                takeout=True,
            )
        )
        opts = mock_run.call_args[0][1]
        assert opts.file == ["export.json"]
        assert opts.download_dir == "/data"
        assert opts.include == ["mp4"]
        assert opts.skip_same is True
        assert opts.takeout is True


class TestUpload:
    @patch("tdl_sdk._runner.TDLRunner.run", return_value=MOCK_RESULT)
    def test_upload(self, mock_run: MagicMock) -> None:
        client = TDL()
        client.upload(UploadOptions(path=["/data/file.mp4"], chat="channel", photo=True))
        opts = mock_run.call_args[0][1]
        assert isinstance(opts, UploadOptions)
        assert opts.path == ["/data/file.mp4"]
        assert opts.chat == "channel"
        assert opts.photo is True


class TestForward:
    @patch("tdl_sdk._runner.TDLRunner.run", return_value=MOCK_RESULT)
    def test_forward(self, mock_run: MagicMock) -> None:
        client = TDL()
        client.forward(
            ForwardOptions(
                forward_from=["https://t.me/c/123"],
                to="target",
                mode=ForwardMode.CLONE,
                dry_run=True,
            )
        )
        opts = mock_run.call_args[0][1]
        assert isinstance(opts, ForwardOptions)
        assert opts.forward_from == ["https://t.me/c/123"]
        assert opts.to == "target"
        assert opts.mode == ForwardMode.CLONE
        assert opts.dry_run is True


class TestExtension:
    @patch("tdl_sdk._runner.TDLRunner.run", return_value=MOCK_RESULT)
    def test_ext_install(self, mock_run: MagicMock) -> None:
        client = TDL()
        client.ext_install("github.com/user/ext", ExtInstallOptions(force=True))
        call_args = mock_run.call_args
        assert call_args[0][0] == ["extension", "install"]
        opts = call_args[0][1]
        assert isinstance(opts, ExtInstallOptions)
        assert opts.force is True
        assert call_args[1]["positional_args"] == ["github.com/user/ext"]

    @patch("tdl_sdk._runner.TDLRunner.run", return_value=MOCK_RESULT)
    def test_ext_list(self, mock_run: MagicMock) -> None:
        client = TDL()
        client.ext_list()
        call_args = mock_run.call_args
        assert call_args[0][0] == ["extension", "list"]
        assert isinstance(call_args[0][1], ExtListOptions)

    @patch("tdl_sdk._runner.TDLRunner.run", return_value=MOCK_RESULT)
    def test_ext_remove(self, mock_run: MagicMock) -> None:
        client = TDL()
        client.ext_remove("ext-name")
        call_args = mock_run.call_args
        assert call_args[0][0] == ["extension", "remove"]
        assert isinstance(call_args[0][1], ExtRemoveOptions)
        assert call_args[1]["positional_args"] == ["ext-name"]

    @patch("tdl_sdk._runner.TDLRunner.run", return_value=MOCK_RESULT)
    def test_ext_upgrade(self, mock_run: MagicMock) -> None:
        client = TDL()
        client.ext_upgrade("ext-name")
        call_args = mock_run.call_args
        assert call_args[0][0] == ["extension", "upgrade"]
        assert isinstance(call_args[0][1], ExtUpgradeOptions)
        assert call_args[1]["positional_args"] == ["ext-name"]
