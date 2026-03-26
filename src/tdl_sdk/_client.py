from __future__ import annotations

from pydantic import Field, BaseModel, ConfigDict, computed_field

from tdl_sdk._models import (
    TDLResult,
    LoginOptions,
    BackupOptions,
    GlobalOptions,
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
from tdl_sdk._runner import TDLRunner


class TDL(BaseModel):
    """Python SDK for the TDL (Telegram Downloader) CLI tool.

    Provides a Pythonic interface to all tdl commands by wrapping the CLI binary
    via subprocess.

    Example:
        ```python
        from tdl_sdk import TDL, LoginType, LoginOptions

        client = TDL(ns="my_session", proxy="socks5://127.0.0.1:1080")
        client.login(LoginOptions(login_type=LoginType.QR))
        client.download(DownloadOptions(url=["https://t.me/channel/123"]))
        ```
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    global_options: GlobalOptions = Field(
        default_factory=GlobalOptions, description="Global options for all tdl commands."
    )
    tdl_path: str = Field(default="tdl", description="Path to the tdl binary.")
    timeout: float | None = Field(
        default=None, description="Default timeout in seconds for all commands."
    )

    @computed_field
    @property
    def runner(self) -> TDLRunner:
        """TDLRunner instance built from current config."""
        return TDLRunner(tdl_path=self.tdl_path, global_options=self.global_options)

    # ------------------------------------------------------------------ #
    #  Account Management                                                  #
    # ------------------------------------------------------------------ #

    def login(self, options: LoginOptions | None = None) -> TDLResult:
        """Login to Telegram.

        Args:
            options: Login options. Defaults to desktop login mode.
        """
        return self.runner.run(["login"], options or LoginOptions(), timeout=self.timeout)

    def backup(self, options: BackupOptions | None = None) -> TDLResult:
        """Backup your data.

        Args:
            options: Backup options.
        """
        return self.runner.run(["backup"], options or BackupOptions(), timeout=self.timeout)

    def recover(self, options: RecoverOptions) -> TDLResult:
        """Recover your data from a backup.

        Args:
            options: Recover options with the backup file path.
        """
        return self.runner.run(["recover"], options, timeout=self.timeout)

    def migrate(self, options: MigrateOptions) -> TDLResult:
        """Migrate your current data to another storage.

        Args:
            options: Migrate options with destination storage config.
        """
        return self.runner.run(["migrate"], options, timeout=self.timeout)

    # ------------------------------------------------------------------ #
    #  Chat Operations                                                     #
    # ------------------------------------------------------------------ #

    def chat_ls(self, options: ChatListOptions | None = None) -> TDLResult:
        """List your chats.

        Args:
            options: Chat list options.
        """
        return self.runner.run(["chat", "ls"], options or ChatListOptions(), timeout=self.timeout)

    def chat_export(self, options: ChatExportOptions | None = None) -> TDLResult:
        """Export messages from (protected) chat for download.

        Args:
            options: Chat export options.
        """
        return self.runner.run(
            ["chat", "export"], options or ChatExportOptions(), timeout=self.timeout
        )

    def chat_users(self, options: ChatUsersOptions) -> TDLResult:
        """Export users from (protected) channels.

        Args:
            options: Chat users export options.
        """
        return self.runner.run(["chat", "users"], options, timeout=self.timeout)

    # ------------------------------------------------------------------ #
    #  Download                                                            #
    # ------------------------------------------------------------------ #

    def download(self, options: DownloadOptions | None = None) -> TDLResult:
        """Download anything from Telegram (protected) chat.

        Args:
            options: Download options.
        """
        return self.runner.run(["download"], options or DownloadOptions(), timeout=self.timeout)

    # ------------------------------------------------------------------ #
    #  Upload                                                              #
    # ------------------------------------------------------------------ #

    def upload(self, options: UploadOptions) -> TDLResult:
        """Upload anything to Telegram.

        Args:
            options: Upload options with paths to upload.
        """
        return self.runner.run(["upload"], options, timeout=self.timeout)

    # ------------------------------------------------------------------ #
    #  Forward                                                             #
    # ------------------------------------------------------------------ #

    def forward(self, options: ForwardOptions) -> TDLResult:
        """Forward messages with automatic fallback and message routing.

        Args:
            options: Forward options.
        """
        return self.runner.run(["forward"], options, timeout=self.timeout)

    # ------------------------------------------------------------------ #
    #  Extension Management                                                #
    # ------------------------------------------------------------------ #

    def ext_install(self, name: str, options: ExtInstallOptions | None = None) -> TDLResult:
        """Install a tdl extension.

        Args:
            name: Extension URL, e.g. github.com/user/tdl-ext-name.
            options: Install options.
        """
        return self.runner.run(
            ["extension", "install"],
            options or ExtInstallOptions(),
            positional_args=[name],
            timeout=self.timeout,
        )

    def ext_list(self, options: ExtListOptions | None = None) -> TDLResult:
        """List installed extension commands.

        Args:
            options: List options.
        """
        return self.runner.run(
            ["extension", "list"], options or ExtListOptions(), timeout=self.timeout
        )

    def ext_remove(self, name: str, options: ExtRemoveOptions | None = None) -> TDLResult:
        """Remove an installed extension.

        Args:
            name: Extension name to remove.
            options: Remove options.
        """
        return self.runner.run(
            ["extension", "remove"],
            options or ExtRemoveOptions(),
            positional_args=[name],
            timeout=self.timeout,
        )

    def ext_upgrade(self, name: str, options: ExtUpgradeOptions | None = None) -> TDLResult:
        """Upgrade a tdl extension.

        Args:
            name: Extension name to upgrade.
            options: Upgrade options.
        """
        return self.runner.run(
            ["extension", "upgrade"],
            options or ExtUpgradeOptions(),
            positional_args=[name],
            timeout=self.timeout,
        )
