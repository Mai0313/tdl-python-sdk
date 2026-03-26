from tdl_sdk import LoginType, ExportType, ListOutput, ForwardMode


def test_login_type_values() -> None:
    assert LoginType.DESKTOP.value == "desktop"
    assert LoginType.CODE.value == "code"
    assert LoginType.QR.value == "qr"


def test_export_type_values() -> None:
    assert ExportType.TIME.value == "time"
    assert ExportType.ID.value == "id"
    assert ExportType.LAST.value == "last"


def test_forward_mode_values() -> None:
    assert ForwardMode.DIRECT.value == "direct"
    assert ForwardMode.CLONE.value == "clone"


def test_list_output_values() -> None:
    assert ListOutput.TABLE.value == "table"
    assert ListOutput.JSON.value == "json"


def test_enums_are_strings() -> None:
    assert isinstance(LoginType.QR, str)
    assert isinstance(ExportType.TIME, str)
    assert isinstance(ForwardMode.DIRECT, str)
    assert isinstance(ListOutput.JSON, str)
