import tempfile
import unittest
from pathlib import Path

from pysurf.storage import DataStore


class DataStoreTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.store = DataStore(Path(self.directory.name) / "test.sqlite3")

    def tearDown(self):
        self.store.close()
        self.directory.cleanup()

    def test_history_excludes_local_and_internal_schemes(self):
        self.store.add_history("https://example.com", "Example")
        self.store.add_history("data:text/html,test")

        self.assertEqual(len(self.store.history()), 1)
        self.assertEqual(self.store.history()[0][0], "https://example.com")

    def test_bookmark_upsert_and_remove(self):
        self.store.add_bookmark("https://example.com", "Old title")
        self.store.add_bookmark("https://example.com", "New title")

        self.assertEqual(
            self.store.bookmarks(),
            [("https://example.com", "New title")],
        )
        self.store.remove_bookmark("https://example.com")
        self.assertEqual(self.store.bookmarks(), [])

    def test_session_round_trip(self):
        self.store.save_session(["https://example.com"], 0)
        self.assertEqual(self.store.session(), (["https://example.com"], 0))

    def test_session_rejects_malformed_data(self):
        self.store.connection.execute(
            "INSERT INTO sessions(id, urls, active_index) VALUES (1, ?, 0)",
            ("not-json",),
        )
        self.store.connection.commit()

        with self.assertLogs("pysurf.storage", level="WARNING"):
            self.assertEqual(self.store.session(), ([], 0))
