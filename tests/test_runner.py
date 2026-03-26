import subprocess
from unittest.mock import MagicMock, patch

import pytest

from tdl_sdk._enums import LoginType
from tdl_sdk._models import LoginOptions, GlobalOptions, DownloadOptions, ExtInstallOptions
from tdl_sdk._runner import TDLRunner
from tdl_sdk._exceptions import TDLCommandError, TDLTimeoutError, TDLNotFoundError


class TestRun:
    @patch("tdl_sdk._runner.subprocess.run")
    def test_successful_run(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(stdout="output", stderr="", returncode=0)
        runner = TDLRunner()
        opts = LoginOptions(login_type=LoginType.QR)
        result = runner.run(["login"], opts)

        assert result.stdout == "output"
        assert result.return_code == 0

        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "tdl"
        assert "login" in call_args
        assert "--type" in call_args
        assert "qr" in call_args

    @patch("tdl_sdk._runner.subprocess.run")
    def test_command_error(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(stdout="", stderr="error msg", returncode=1)
        runner = TDLRunner()
        with pytest.raises(TDLCommandError) as exc_info:
            runner.run(["download"])

        assert exc_info.value.return_code == 1
        assert exc_info.value.stderr == "error msg"

    @patch("tdl_sdk._runner.subprocess.run")
    def test_not_found_error(self, mock_run: MagicMock) -> None:
        mock_run.side_effect = FileNotFoundError("No such file")
        runner = TDLRunner(tdl_path="/nonexistent/tdl")
        with pytest.raises(TDLNotFoundError):
            runner.run(["version"])

    @patch("tdl_sdk._runner.subprocess.run")
    def test_timeout_error(self, mock_run: MagicMock) -> None:
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="tdl", timeout=5)
        runner = TDLRunner()
        with pytest.raises(TDLTimeoutError):
            runner.run(["download"], timeout=5)

    @patch("tdl_sdk._runner.subprocess.run")
    def test_positional_args(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)
        runner = TDLRunner()
        opts = ExtInstallOptions(force=True)
        runner.run(["extension", "install"], opts, positional_args=["github.com/user/ext"])
        call_args = mock_run.call_args[0][0]
        assert call_args[-1] == "github.com/user/ext"
        assert "--force" in call_args

    @patch("tdl_sdk._runner.subprocess.run")
    def test_global_options_in_command(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)
        opts = GlobalOptions(ns="test_session", proxy="http://proxy:8080")
        runner = TDLRunner(global_options=opts)
        runner.run(["chat", "ls"])

        call_args = mock_run.call_args[0][0]
        ns_idx = call_args.index("--ns")
        assert call_args[ns_idx + 1] == "test_session"
        proxy_idx = call_args.index("--proxy")
        assert call_args[proxy_idx + 1] == "http://proxy:8080"
        chat_idx = call_args.index("chat")
        assert ns_idx < chat_idx

    @patch("tdl_sdk._runner.subprocess.run")
    def test_download_options_cli_args(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)
        runner = TDLRunner()
        opts = DownloadOptions(url=["link1", "link2"], skip_same=True, continue_download=True)
        runner.run(["download"], opts)
        call_args = mock_run.call_args[0][0]
        assert call_args.count("--url") == 2
        assert "--skip-same" in call_args
        assert "--continue" in call_args
