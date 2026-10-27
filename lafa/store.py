"""Offline store: what Lafa downloaded for use without internet.

SQLite database `lafa.db` in the learner's data folder (~/.local/share/lafa):
* extracts — Wikipedia introductions per item and language (CC BY-SA 4.0),
* media    — one free-licence photo per item from Wikimedia Commons, with
             author, licence and source (the picture file sits in media/),
* meta     — dates of the last download and update checks.
Content updates (JSON) are files in updates/ (read by lafa.kb); indicators
from the World Bank are written there too. Nothing here is ever sent anywhere.
"""
import os
import sqlite3
import threading
import time
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS extracts (item_id TEXT, lang TEXT, title TEXT, text TEXT, url TEXT, source TEXT, licence TEXT, fetched REAL,
                                     PRIMARY KEY (item_id, lang));
CREATE TABLE IF NOT EXISTS media (item_id TEXT PRIMARY KEY, file TEXT, title TEXT, author TEXT, licence TEXT, licence_url TEXT,
                                  source_url TEXT, width INTEGER, height INTEGER, fetched REAL);
"""
MAX_EXTRACT = 6000

class Store:
    def __init__(self, folder):
        self.folder = Path(folder); self.media_dir = self.folder / "media"; self.lock = threading.Lock()
        self.folder.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.db = sqlite3.connect(str(self.folder / "lafa.db"), check_same_thread=False, timeout=10)
        with self.lock:
            self.db.executescript(SCHEMA); self.db.commit()
    def close(self):
        with self.lock: self.db.close()
    # ------------------------------------------------------------------ meta
    def get_meta(self, key, default=""):
        with self.lock:
            row = self.db.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        return row[0] if row else default
    def set_meta(self, key, value):
        with self.lock:
            self.db.execute("INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)", (key, str(value))); self.db.commit()
    # -------------------------------------------------------------- extracts
    def put_extract(self, item_id, lang, title, text, url, source="Wikipedia", licence="CC BY-SA 4.0"):
        if not text or not str(url).startswith("https://"): return
        with self.lock:
            self.db.execute("INSERT OR REPLACE INTO extracts VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            (item_id, lang, title[:300], text[:MAX_EXTRACT], url[:600], source[:120], licence[:60], time.time())); self.db.commit()
    def extract(self, item_id, lang):
        with self.lock:
            row = self.db.execute("SELECT title, text, url, source, licence, fetched FROM extracts WHERE item_id=? AND lang=?", (item_id, lang)).fetchone()
        if not row: return None
        return {"title": row[0], "text": row[1], "url": row[2], "source": row[3], "licence": row[4], "fetched": row[5]}
    # ----------------------------------------------------------------- media
    def put_photo(self, item_id, data, ext, info):
        """Save a downloaded picture (bytes) with its credit; returns the file path."""
        self.media_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        safe = "".join(c if c.isalnum() or c in "._-" else "_" for c in item_id)[:100]
        path = self.media_dir / f"{safe}.{ext}"; tmp = path.with_suffix(path.suffix + ".part")
        tmp.write_bytes(data); os.replace(tmp, path)
        with self.lock:
            self.db.execute("INSERT OR REPLACE INTO media VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                            (item_id, path.name, info.get("title", "")[:300], info.get("author", "")[:300], info.get("licence", "")[:80],
                             info.get("licence_url", "")[:400], info.get("source_url", "")[:600], int(info.get("width", 0)), int(info.get("height", 0)), time.time()))
            self.db.commit()
        return path
    def photo(self, item_id):
        """(path, info) of the downloaded picture, or None."""
        with self.lock:
            row = self.db.execute("SELECT file, title, author, licence, licence_url, source_url FROM media WHERE item_id=?", (item_id,)).fetchone()
        if not row: return None
        path = self.media_dir / row[0]
        if not path.is_file(): return None
        return path, {"title": row[1], "author": row[2], "licence": row[3], "licence_url": row[4], "source_url": row[5]}
    def photos(self):
        with self.lock:
            rows = self.db.execute("SELECT item_id, file, title, author, licence, licence_url, source_url FROM media ORDER BY item_id").fetchall()
        return [{"item": r[0], "file": r[1], "title": r[2], "author": r[3], "licence": r[4], "licence_url": r[5], "source_url": r[6]} for r in rows]
    # ----------------------------------------------------------------- stats
    def stats(self):
        with self.lock:
            extracts = self.db.execute("SELECT COUNT(*) FROM extracts").fetchone()[0]
            media = self.db.execute("SELECT COUNT(*) FROM media").fetchone()[0]
        size = 0
        for p in [self.folder / "lafa.db"] + (list(self.media_dir.glob("*")) if self.media_dir.is_dir() else []):
            try: size += p.stat().st_size
            except OSError: pass
        return {"extracts": extracts, "photos": media, "bytes": size}
    def clear(self):
        """Remove downloaded texts and pictures (content updates stay)."""
        with self.lock:
            self.db.execute("DELETE FROM extracts"); self.db.execute("DELETE FROM media"); self.db.commit()
        if self.media_dir.is_dir():
            for p in self.media_dir.glob("*"):
                try: p.unlink()
                except OSError: pass
