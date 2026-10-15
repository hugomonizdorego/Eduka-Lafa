"""Personal learning progress on this computer: "continue learning" and favourites.

Stored in the learner's LAFA folder as progress.json (0600, atomic write).
Nothing is sent anywhere. Practice results stay in the report file
(classroom.ReportCard); this file only remembers what was opened last and
what the learner starred, plus the learner's best and last score for each
encyclopedia quiz and interactive activity.
"""
import json
import os
import tempfile
import time
from pathlib import Path

MAX_FAVOURITES = 300
KINDS = {"lesson", "source", "atlas", "guide", "saved", "article"}
MAX_SCORES = 2000

def _clean_text(value, limit):
    return value.strip()[:limit] if isinstance(value, str) and value.strip() and not any(ord(c) < 32 for c in value) else ""

def _entry(item):
    if not isinstance(item, dict): return None
    kind = item.get("kind"); key = _clean_text(item.get("key"), 500); title = _clean_text(item.get("title"), 200)
    if kind not in KINDS or not key or not title: return None
    if kind in {"source", "saved"} and not key.startswith("https://"): return None
    when = item.get("when", 0)
    return {"kind": kind, "key": key, "title": title, "when": float(when) if isinstance(when, (int, float)) and not isinstance(when, bool) else 0.0}

class Progress:
    def __init__(self, folder=None, clock=time.time):
        self.clock = clock; self.path = Path(folder) / "progress.json" if folder else None
        self.last = None; self.recent = []; self.favourites = []; self.scores = {}
        self.load()
    def load(self):
        if not self.path: return
        try: raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError, UnicodeError): return
        if not isinstance(raw, dict): return
        self.last = _entry(raw.get("last"))
        self.recent = [e for e in (_entry(x) for x in raw.get("recent", [])[:20]) if e]
        seen = set(); self.favourites = []
        for e in (_entry(x) for x in raw.get("favourites", [])[:MAX_FAVOURITES]):
            if e and (e["kind"], e["key"]) not in seen: seen.add((e["kind"], e["key"])); self.favourites.append(e)
        self.scores = {}
        raw_scores = raw.get("scores", {})
        if isinstance(raw_scores, dict):
            for key, value in list(raw_scores.items())[:MAX_SCORES]:
                key = _clean_text(key, 200)
                if not key or not isinstance(value, dict): continue
                try:
                    best, last, total = (int(value.get(k, 0)) for k in ("best", "last", "total"))
                except (TypeError, ValueError): continue
                if 0 < total <= 100 and 0 <= best <= total and 0 <= last <= total:
                    self.scores[key] = {"best": best, "last": last, "total": total, "when": float(value.get("when", 0) or 0)}
    def save(self):
        if not self.path: return
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        fd, tmp = tempfile.mkstemp(dir=self.path.parent, prefix=".progress-")
        try:
            os.fchmod(fd, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump({"version": 1, "last": self.last, "recent": self.recent, "favourites": self.favourites, "scores": self.scores}, handle, ensure_ascii=False, indent=1)
            os.replace(tmp, self.path)
        except BaseException:
            try: os.unlink(tmp)
            except OSError: pass
            raise
    def opened(self, kind, key, title):
        """Remember the material opened last ("continue learning")."""
        entry = _entry({"kind": kind, "key": key, "title": title, "when": self.clock()})
        if not entry: return
        self.last = entry
        self.recent = [entry] + [e for e in self.recent if (e["kind"], e["key"]) != (kind, key)][:9]
        try: self.save()
        except OSError: pass
    def is_favourite(self, kind, key):
        return any(e["kind"] == kind and e["key"] == key for e in self.favourites)
    def toggle_favourite(self, kind, key, title):
        """Add or remove a favourite; returns True when it is now a favourite."""
        if self.is_favourite(kind, key):
            self.favourites = [e for e in self.favourites if not (e["kind"] == kind and e["key"] == key)]; state = False
        else:
            entry = _entry({"kind": kind, "key": key, "title": title, "when": self.clock()})
            if not entry: raise ValueError("This item cannot be saved as a favourite.")
            if len(self.favourites) >= MAX_FAVOURITES: raise ValueError("Too many favourites.")
            self.favourites.insert(0, entry); state = True
        self.save(); return state
    def record(self, key, score, total):
        """Keep the last and best result of a quiz or activity (personal progress)."""
        key = _clean_text(key, 200)
        if not key or not 0 < int(total) <= 100 or not 0 <= int(score) <= int(total): raise ValueError("Invalid result.")
        old = self.scores.get(key, {})
        self.scores[key] = {"best": max(int(score), old.get("best", 0)) if old.get("total") == int(total) else int(score),
                            "last": int(score), "total": int(total), "when": self.clock()}
        if len(self.scores) > MAX_SCORES:
            for k in sorted(self.scores, key=lambda k: self.scores[k]["when"])[:len(self.scores) - MAX_SCORES]: del self.scores[k]
        try: self.save()
        except OSError: pass
        return self.scores[key]
    def result(self, key):
        return self.scores.get(key)
