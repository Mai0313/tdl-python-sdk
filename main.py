# ruff: noqa: T201
"""Demo: Export messages from a Telegram group using TDL Python SDK.

This script demonstrates a typical workflow:
1. Login to Telegram
2. List available chats
3. Export messages from a target group
4. Download media from the exported messages

Usage:
    uv run python main.py
"""

from tdl_sdk import (
    TDL,
    LoginType,
    ExportType,
    ListOutput,
    LoginOptions,
    GlobalOptions,
    ChatListOptions,
    DownloadOptions,
    TDLCommandError,
    ChatUsersOptions,
    TDLNotFoundError,
    ChatExportOptions,
)

# -- Configuration --
TARGET_GROUP = "my_group"  # Replace with your group username or ID
EXPORT_FILE = "tdl-export.json"
DOWNLOAD_DIR = "./downloads"


def main() -> None:
    # 1. Create client with custom session namespace
    client = TDL(
        global_options=GlobalOptions(
            ns="demo",  # Use a dedicated session namespace
            threads=4,  # Max threads per transfer
            limit=2,  # Max concurrent tasks
        )
    )

    try:
        # 2. Login via QR code
        print("[1/5] Logging in via QR code...")
        client.login(LoginOptions(login_type=LoginType.QR))
        print("  Login successful!\n")

        # 3. List all chats (JSON format for programmatic use)
        print("[2/5] Listing chats...")
        result = client.chat_ls(ChatListOptions(output=ListOutput.JSON))
        print(f"  Found chats (first 200 chars): {result.stdout[:200]}...\n")

        # 4. Export last 50 messages from the target group
        print(f"[3/5] Exporting last 50 messages from '{TARGET_GROUP}'...")
        client.chat_export(
            ChatExportOptions(
                chat=TARGET_GROUP,
                export_type=ExportType.LAST,
                export_input=[50],
                output=EXPORT_FILE,
                with_content=True,
            )
        )
        print(f"  Exported to {EXPORT_FILE}\n")

        # 5. Export group members
        print(f"[4/5] Exporting users from '{TARGET_GROUP}'...")
        client.chat_users(ChatUsersOptions(chat=TARGET_GROUP, output="tdl-users.json"))
        print("  Exported to tdl-users.json\n")

        # 6. Download media from exported messages
        print(f"[5/5] Downloading media to '{DOWNLOAD_DIR}'...")
        client.download(
            DownloadOptions(file=[EXPORT_FILE], download_dir=DOWNLOAD_DIR, skip_same=True)
        )
        print("  Download complete!\n")

    except TDLNotFoundError:
        print("Error: tdl binary not found.")
        print("Install it first: curl -sSL https://docs.iyear.me/tdl/install.sh | bash")
    except TDLCommandError as e:
        print(f"Error: tdl command failed (exit code {e.return_code})")
        print(f"  stderr: {e.stderr.strip()}")


if __name__ == "__main__":
    main()
