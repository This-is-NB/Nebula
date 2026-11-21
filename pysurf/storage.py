import json
import logging
import sqlite3
from pathlib import Path

LOGGER = logging.getLogger(__name__)


class DataStore:
    def __init__(self, path):
        self.connection = sqlite3.connect(Path(path))
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                title TEXT NOT NULL DEFAULT '',
                visited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS history_url_idx ON history(url);
            CREATE INDEX IF NOT EXISTS history_time_idx ON history(visited_at);

            CREATE TABLE IF NOT EXISTS bookmarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                urls TEXT NOT NULL,
                active_index INTEGER NOT NULL DEFAULT 0
            );
            """
        )
        self.connection.commit()

    def add_history(self, url, title=""):
        if not url or url.startswith(("data:", "qrc:", "about:", "chrome:", "devtools:")):
            return
        self.connection.execute(
            "INSERT INTO history(url, title) VALUES (?, ?)",
            (url, title[:500]),
        )
        self.connection.execute(
            "DELETE FROM history WHERE id NOT IN "
            "(SELECT id FROM history ORDER BY visited_at DESC, id DESC LIMIT 5000)"
        )
        self.connection.commit()

    def history(self, limit=500):
        return self.connection.execute(
            "SELECT url, title, visited_at FROM history "
            "ORDER BY visited_at DESC, id DESC LIMIT ?",
            (limit,),
        ).fetchall()

    def clear_history(self):
        self.connection.execute("DELETE FROM history")
        self.connection.commit()

    def add_bookmark(self, url, title=""):
        self.connection.execute(
            "INSERT INTO bookmarks(url, title) VALUES (?, ?) "
            "ON CONFLICT(url) DO UPDATE SET title=excluded.title",
            (url, title[:500]),
        )
        self.connection.commit()

    def remove_bookmark(self, url):
        self.connection.execute("DELETE FROM bookmarks WHERE url = ?", (url,))
        self.connection.commit()

    def bookmarks(self):
        return self.connection.execute(
            "SELECT url, title FROM bookmarks ORDER BY title, url"
        ).fetchall()

    def is_bookmarked(self, url):
        return bool(
            self.connection.execute(
                "SELECT 1 FROM bookmarks WHERE url = ?", (url,)
            ).fetchone()
        )

    def save_session(self, urls, active_index):
        self.connection.execute(
            "INSERT INTO sessions(id, urls, active_index) VALUES (1, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET urls=excluded.urls, "
            "active_index=excluded.active_index",
            (json.dumps(urls), active_index),
        )
        self.connection.commit()

    def session(self):
        row = self.connection.execute(
            "SELECT urls, active_index FROM sessions WHERE id = 1"
        ).fetchone()
        if not row:
            return [], 0
        try:
            urls = json.loads(row[0])
            if not isinstance(urls, list) or not all(isinstance(url, str) for url in urls):
                return [], 0
            return urls, max(0, int(row[1]))
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            LOGGER.warning("Ignoring invalid saved session: %s", exc)
            return [], 0

    def close(self):
        self.connection.close()
