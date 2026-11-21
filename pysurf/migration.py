import shutil
import sqlite3
from pathlib import Path


def migrate_legacy_data(data_dir, legacy_dir):
    data_dir = Path(data_dir)
    legacy_dir = Path(legacy_dir)
    if not legacy_dir.exists() or legacy_dir.resolve() == data_dir.resolve():
        return

    legacy_database = legacy_dir / "pysurf.sqlite3"
    destination_database = data_dir / "pysurf.sqlite3"
    if legacy_database.exists() and not destination_database.exists():
        temporary_database = destination_database.with_name(
            destination_database.name + ".migrating"
        )
        source_connection = sqlite3.connect(legacy_database)
        destination_connection = sqlite3.connect(temporary_database)
        try:
            source_connection.backup(destination_connection)
        finally:
            destination_connection.close()
            source_connection.close()
        temporary_database.replace(destination_database)

    legacy_settings = legacy_dir / "settings.json"
    destination_settings = data_dir / "settings.json"
    if legacy_settings.exists() and not destination_settings.exists():
        shutil.copy2(legacy_settings, destination_settings)

    legacy_storage = legacy_dir / "web-storage"
    destination_storage = data_dir / "web-storage"
    if legacy_storage.exists() and not destination_storage.exists():
        shutil.copytree(legacy_storage, destination_storage)
