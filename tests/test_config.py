import json
import tempfile
import unittest
from pathlib import Path

from pysurf.config import HOME_PAGE, SettingsRepository


class SettingsRepositoryTests(unittest.TestCase):
    def test_legacy_preferences_migrate_and_zoom_is_bounded(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            legacy = root / "preference.json"
            target = root / "settings.json"
            legacy.write_text(
                json.dumps({
                    "settings": {
                        "home": "https://example.com",
                        "zoom_factor": 8.0,
                        "dark_mode": True,
                    }
                }),
                encoding="utf-8",
            )

            settings = SettingsRepository(target, legacy)

            self.assertEqual(settings.get("home"), "https://example.com")
            self.assertEqual(settings.get("zoom"), 5.0)
            self.assertTrue(settings.get("dark_mode"))

    def test_invalid_saved_values_fall_back_to_defaults(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "settings.json"
            target.write_text(
                json.dumps({
                    "home": "",
                    "zoom": "invalid",
                    "block_trackers": "false",
                }),
                encoding="utf-8",
            )

            settings = SettingsRepository(target)

            self.assertEqual(settings.get("home"), HOME_PAGE)
            self.assertEqual(settings.get("zoom"), 1.0)
            self.assertTrue(settings.get("block_trackers"))

    def test_previous_default_home_page_migrates_to_nebula_start_page(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "settings.json"
            target.write_text(
                json.dumps({"home": "https://www.google.com/"}),
                encoding="utf-8",
            )

            settings = SettingsRepository(target)

            self.assertEqual(settings.get("home"), HOME_PAGE)

    def test_updates_are_persisted_atomically(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "settings.json"
            settings = SettingsRepository(target)
            settings.set("home", "https://example.net/")

            reloaded = SettingsRepository(target)

            self.assertEqual(reloaded.get("home"), "https://example.net/")
            self.assertFalse(target.with_name("settings.json.tmp").exists())
