import sqlite3
import tempfile
import unittest
from pathlib import Path

from pysurf.migration import migrate_legacy_data


class LegacyMigrationTests(unittest.TestCase):
    def test_database_migrates_without_overwriting_existing_data(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            legacy = root / "legacy"
            destination = root / "new"
            legacy.mkdir()
            destination.mkdir()

            old_database = sqlite3.connect(legacy / "pysurf.sqlite3")
            old_database.execute("CREATE TABLE sample(value TEXT)")
            old_database.execute("INSERT INTO sample(value) VALUES ('preserved')")
            old_database.commit()
            old_database.close()

            migrate_legacy_data(destination, legacy)

            migrated = sqlite3.connect(destination / "pysurf.sqlite3")
            value = migrated.execute("SELECT value FROM sample").fetchone()[0]
            migrated.close()
            self.assertEqual(value, "preserved")

            existing_database = sqlite3.connect(destination / "pysurf.sqlite3")
            existing_database.execute("INSERT INTO sample(value) VALUES ('new')")
            existing_database.commit()
            existing_database.close()
            migrate_legacy_data(destination, legacy)

            existing_database = sqlite3.connect(destination / "pysurf.sqlite3")
            values = existing_database.execute(
                "SELECT value FROM sample ORDER BY rowid"
            ).fetchall()
            existing_database.close()
            self.assertEqual(values, [("preserved",), ("new",)])
