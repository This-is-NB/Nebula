import json
import logging
import os
import sys
from pathlib import Path

from . import __version__

LOGGER = logging.getLogger(__name__)

APP_NAME = "Nebula"
APP_VERSION = __version__
SEARCH_URL = "https://www.google.com/search?q={}"
APP_DIR = Path(__file__).resolve().parent.parent
APP_ICON = APP_DIR / "PySurfData" / "Designer.png"
APP_ICON_ICO = APP_ICON.with_suffix(".ico")
HOME_PAGE = "nebula://home"
HOME_PAGE_FILE = Path(__file__).with_name("home.html").resolve().as_uri()


def get_app_icon_path():
    if os.name == "nt" and APP_ICON_ICO.is_file():
        return APP_ICON_ICO
    return APP_ICON


def get_data_dir():
    override = os.environ.get("PYSURF_DATA_DIR")
    if override:
        path = Path(override).expanduser()
    elif os.name == "nt":
        path = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")) / "PySurf"
    elif sys.platform == "darwin":
        path = Path.home() / "Library" / "Application Support" / "PySurf"
    else:
        path = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / "pysurf"

    path.mkdir(parents=True, exist_ok=True)
    return path


class SettingsRepository:
    DEFAULTS = {
        "home": HOME_PAGE,
        "search": "google",
        "zoom": 1.0,
        "dark_mode": False,
        "animations": True,
        "block_trackers": True,
        "third_party_cookies": False,
        "restore_session": True,
        "download_path": str(Path.home() / "Downloads"),
    }

    def __init__(self, path, legacy_path=None):
        self.path = Path(path)
        self.legacy_path = Path(legacy_path) if legacy_path else None
        self.values = self._load()

    def _load(self):
        values = dict(self.DEFAULTS)
        if self.legacy_path and self.legacy_path.exists():
            try:
                legacy = json.loads(self.legacy_path.read_text(encoding="utf-8"))
                if not isinstance(legacy, dict):
                    raise ValueError("legacy preference root must be an object")
                old_settings = legacy.get("settings", {})
                if not isinstance(old_settings, dict):
                    raise ValueError("legacy settings must be an object")
                values["home"] = old_settings.get("home", values["home"])
                values["zoom"] = self._valid_zoom(
                    old_settings.get("zoom_factor", values["zoom"])
                )
                values["dark_mode"] = bool(old_settings.get("dark_mode", False))
            except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
                LOGGER.warning("Ignoring invalid legacy preferences: %s", exc)

        if self.path.exists():
            try:
                saved = json.loads(self.path.read_text(encoding="utf-8"))
                if isinstance(saved, dict):
                    values.update(saved)
                else:
                    LOGGER.warning("Ignoring settings file %s: root must be an object", self.path)
            except (OSError, json.JSONDecodeError) as exc:
                LOGGER.warning("Ignoring invalid settings file %s: %s", self.path, exc)

        values["zoom"] = self._valid_zoom(values.get("zoom", 1.0))
        if not isinstance(values.get("home"), str) or not values["home"].strip():
            values["home"] = HOME_PAGE
        elif values["home"] == "https://www.google.com/":
            values["home"] = HOME_PAGE
        if not isinstance(values.get("download_path"), str) or not values["download_path"]:
            values["download_path"] = self.DEFAULTS["download_path"]
        for key in (
            "dark_mode",
            "animations",
            "block_trackers",
            "third_party_cookies",
            "restore_session",
        ):
            if not isinstance(values.get(key), bool):
                values[key] = self.DEFAULTS[key]
        return values

    @staticmethod
    def _valid_zoom(value):
        try:
            return max(0.25, min(5.0, float(value)))
        except (TypeError, ValueError):
            return 1.0

    def get(self, name, default=None):
        if default is None:
            default = self.DEFAULTS.get(name)
        return self.values.get(name, default)

    def set(self, name, value):
        if name == "zoom":
            value = self._valid_zoom(value)
        self.values[name] = value
        self.save()

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.path.with_name(self.path.name + ".tmp")
        temporary_path.write_text(
            json.dumps(self.values, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        temporary_path.replace(self.path)
