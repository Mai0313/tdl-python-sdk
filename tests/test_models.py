import pytest
from pydantic import ValidationError

from tdl_sdk import (
    LoginType,
    TDLResult,
    ExportType,
    ListOutput,
    ForwardMode,
    LoginOptions,
    BackupOptions,
    GlobalOptions,
    UploadOptions,
    ForwardOptions,
    MigrateOptions,
    RecoverOptions,
    ChatListOptions,
    DownloadOptions,
    ChatUsersOptions,
    ChatExportOptions,
    ExtInstallOptions,
)


class TestGlobalOptions:
    def test_defaults(self) -> None:
        opts = GlobalOptions()
        assert opts.debug is False
        assert opts.delay is None
        assert opts.limit == 2
        assert opts.ns == "default"
        assert opts.ntp is None
        assert opts.pool == 8
        assert opts.proxy is None
        assert opts.reconnect_timeout == "5m"
        assert opts.storage is None
        assert opts.threads == 4

    def test_custom(self) -> None:
        opts = GlobalOptions(
            debug=True,
            delay="5s",
            limit=4,
            ns="test",
            proxy="socks5://127.0.0.1:1080",
            threads=8,
            storage={"type": "bolt", "path": "/data"},
        )
        assert opts.debug is True
        assert opts.delay == "5s"
        assert opts.limit == 4
        assert opts.ns == "test"
        assert opts.proxy == "socks5://127.0.0.1:1080"
        assert opts.threads == 8
        assert opts.storage == {"type": "bolt", "path": "/data"}

    def test_cli_args_default_empty(self) -> None:
        opts = GlobalOptions()
        assert opts.cli_args == []

    def test_cli_args_custom(self) -> None:
        opts = GlobalOptions(debug=True, ns="test", proxy="http://p:8080", threads=8)
        args = opts.cli_args
        assert "--debug" in args
        assert args[args.index("--ns") + 1] == "test"
        assert args[args.index("--proxy") + 1] == "http://p:8080"
        assert args[args.index("--threads") + 1] == "8"

    def test_cli_args_storage(self) -> None:
        opts = GlobalOptions(storage={"type": "bolt", "path": "/data"})
        args = opts.cli_args
        assert "--storage" in args
        val = args[args.index("--storage") + 1]
        assert "type=bolt" in val
        assert "path=/data" in val


class TestTDLResult:
    def test_defaults(self) -> None:
        result = TDLResult()
        assert result.stdout == ""
        assert result.stderr == ""
        assert result.return_code == 0

    def test_custom(self) -> None:
        result = TDLResult(stdout="output", stderr="error", return_code=1)
        assert result.stdout == "output"
        assert result.stderr == "error"
        assert result.return_code == 1


class TestLoginOptions:
    def test_defaults(self) -> None:
        opts = LoginOptions()
        assert opts.login_type == LoginType.DESKTOP
        assert opts.desktop is None
        assert opts.passcode is None

    def test_cli_dict(self) -> None:
        opts = LoginOptions(login_type=LoginType.QR, passcode="1234")
        d = opts.cli_dict
        assert d["type"] == "qr"
        assert d["passcode"] == "1234"
        assert "desktop" not in d

    def test_cli_args(self) -> None:
        opts = LoginOptions(login_type=LoginType.QR, passcode="1234")
        args = opts.cli_args
        assert args == ["--type", "qr", "--passcode", "1234"]

    def test_populate_by_alias(self) -> None:
        opts = LoginOptions(**{"type": LoginType.QR})
        assert opts.login_type == LoginType.QR


class TestBackupOptions:
    def test_defaults(self) -> None:
        opts = BackupOptions()
        assert opts.dst is None

    def test_cli_dict_with_dst(self) -> None:
        opts = BackupOptions(dst="/backup.tdl")
        assert opts.cli_dict == {"dst": "/backup.tdl"}

    def test_cli_dict_empty(self) -> None:
        opts = BackupOptions()
        assert opts.cli_dict == {}


class TestRecoverOptions:
    def test_required_file(self) -> None:
        opts = RecoverOptions(file="/backup.tdl")
        assert opts.file == "/backup.tdl"
        assert opts.cli_dict == {"file": "/backup.tdl"}

    def test_missing_file_raises(self) -> None:
        with pytest.raises(ValidationError):
            RecoverOptions()


class TestMigrateOptions:
    def test_cli_dict(self) -> None:
        opts = MigrateOptions(to={"type": "file", "path": "/new"})
        assert opts.cli_dict == {"to": {"type": "file", "path": "/new"}}


class TestChatListOptions:
    def test_defaults(self) -> None:
        opts = ChatListOptions()
        d = opts.cli_dict
        assert d["filter"] == "true"
        assert d["output"] == "table"

    def test_custom(self) -> None:
        opts = ChatListOptions(chat_filter="Type == 'channel'", output=ListOutput.JSON)
        d = opts.cli_dict
        assert d["filter"] == "Type == 'channel'"
        assert d["output"] == "json"


class TestChatExportOptions:
    def test_defaults(self) -> None:
        opts = ChatExportOptions()
        d = opts.cli_dict
        assert d["type"] == "time"
        assert d["output"] == "tdl-export.json"
        assert d["filter"] == "true"

    def test_custom(self) -> None:
        opts = ChatExportOptions(
            chat="my_channel", export_type=ExportType.LAST, export_input=[100], with_content=True
        )
        d = opts.cli_dict
        assert d["chat"] == "my_channel"
        assert d["type"] == "last"
        assert d["input"] == [100]
        assert d["with_content"] is True


class TestChatUsersOptions:
    def test_required_chat(self) -> None:
        opts = ChatUsersOptions(chat="my_channel")
        d = opts.cli_dict
        assert d["chat"] == "my_channel"
        assert d["output"] == "tdl-users.json"


class TestDownloadOptions:
    def test_defaults(self) -> None:
        opts = DownloadOptions()
        d = opts.cli_dict
        assert d["dir"] == "downloads"

    def test_custom(self) -> None:
        opts = DownloadOptions(
            url=["https://t.me/c/123"],
            download_dir="/data",
            include=["mp4"],
            skip_same=True,
            takeout=True,
        )
        d = opts.cli_dict
        assert d["url"] == ["https://t.me/c/123"]
        assert d["dir"] == "/data"
        assert d["include"] == ["mp4"]
        assert d["skip-same"] is True
        assert d["takeout"] is True

    def test_continue_alias(self) -> None:
        opts = DownloadOptions(continue_download=True)
        d = opts.cli_dict
        assert d["continue"] is True


class TestUploadOptions:
    def test_required_path(self) -> None:
        opts = UploadOptions(path=["/data/file.mp4"])
        d = opts.cli_dict
        assert d["path"] == ["/data/file.mp4"]

    def test_missing_path_raises(self) -> None:
        with pytest.raises(ValidationError):
            UploadOptions()


class TestForwardOptions:
    def test_required_fields(self) -> None:
        opts = ForwardOptions(forward_from=["link1"], to="target")
        d = opts.cli_dict
        assert d["from"] == ["link1"]
        assert d["to"] == "target"
        assert d["mode"] == "direct"

    def test_custom(self) -> None:
        opts = ForwardOptions(
            forward_from=["link1"], to="target", mode=ForwardMode.CLONE, dry_run=True, silent=True
        )
        d = opts.cli_dict
        assert d["mode"] == "clone"
        assert d["dry-run"] is True
        assert d["silent"] is True


class TestExtInstallOptions:
    def test_defaults(self) -> None:
        opts = ExtInstallOptions()
        assert opts.cli_dict == {}

    def test_force(self) -> None:
        opts = ExtInstallOptions(force=True)
        d = opts.cli_dict
        assert d["force"] is True
