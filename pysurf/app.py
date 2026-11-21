import ctypes
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QApplication

from .browser import BrowserWindow
from .config import (
    APP_DIR,
    APP_NAME,
    APP_VERSION,
    SettingsRepository,
    get_app_icon_path,
    get_data_dir,
)
from .migration import migrate_legacy_data
from .storage import DataStore


def create_application(arguments=None):
    if sys.platform == "win32":
        shell32 = ctypes.WinDLL("shell32", use_last_error=True)
        set_app_id = shell32.SetCurrentProcessExplicitAppUserModelID
        set_app_id.argtypes = [ctypes.c_wchar_p]
        set_app_id.restype = ctypes.c_long
        result = set_app_id("This-is-NB.Nebula")
        if result != 0:
            raise OSError(
                "Could not set Nebula's Windows app ID "
                f"(HRESULT 0x{result & 0xFFFFFFFF:08X})"
            )

    QApplication.setApplicationName(APP_NAME)
    QApplication.setApplicationVersion(APP_VERSION)
    QApplication.setOrganizationName(APP_NAME)
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    application = QApplication(arguments if arguments is not None else sys.argv)
    application.setFont(QFont("Segoe UI", 10))
    icon_path = get_app_icon_path()
    if icon_path.is_file():
        application.setWindowIcon(QIcon(str(icon_path)))

    data_dir = get_data_dir()
    migrate_legacy_data(data_dir, APP_DIR / "PySurfData")
    settings = SettingsRepository(
        data_dir / "settings.json",
        legacy_path=APP_DIR / "preference.json",
    )
    store = DataStore(data_dir / "pysurf.sqlite3")
    window = BrowserWindow(settings, store, data_dir)
    if icon_path.is_file():
        window.setWindowIcon(QIcon(str(icon_path)))
    window.show()
    return application, window


def main():
    application, _window = create_application()
    sys.exit(application.exec())
