"""Personal learning progress on this computer (never sent anywhere).

Stored as progress.json (0600, atomic write) in the learner's Lafa folder:
* last / recent — "continue learning";
* favourites — saved articles, places and words;
* read — encyclopedia items the learner opened (id → first time);
* words — vocabulary boxes for spaced repetition (id → box 0–5, due time);
* scores — best and last result of every quiz (kept from 0.2);
* millionaire — best prize, games and wins of the millionaire quiz;
* xp, achievements and the daily learning streak.
Files written by Lafa 0.2 load unchanged.
"""
import json
import os
import tempfile
import time
from datetime import date, timedelta
from pathlib import Path

MAX_FAVOURITES = 500
MAX_SCORES = 3000
MAX_READ = 5000
KINDS = {"article", "municipality", "place", "day", "word", "lesson", "source", "atlas", "guide", "saved"}
# Leitner boxes: days until a word is asked again.
BOX_DAYS = [0, 1, 3, 7, 16, 35]
XP = {"read": 10, "quiz_right": 5, "word": 2, "unit": 50, "millionaire_step": 3, "day": 5}

ACHIEVEMENTS = [
    # id, test(progress) → bool
    ("first_read", lambda p: len(p.read) >= 1),
    ("reader_10", lambda p: len(p.read) >= 10),
    ("reader_50", lambda p: len(p.read) >= 50),
    ("explorer", lambda p: sum(1 for k in p.read if k.startswith("place.")) >= 10),
    ("municipalities", lambda p: sum(1 for k in p.read if k.startswith("mun.")) >= 14),
    ("words_50", lambda p: sum(1 for w in p.words.values() if w["box"] >= 2) >= 50),
    ("words_200", lambda p: sum(1 for w in p.words.values() if w["box"] >= 2) >= 200),
    ("quiz_perfect", lambda p: any(s["best"] == s["total"] and s["total"] >= 4 for s in p.scores.values())),
    ("millionaire_safe", lambda p: p.millionaire.get("best_step", 0) >= 5),
    ("millionaire_win", lambda p: p.millionaire.get("wins", 0) >= 1),
    ("streak_7", lambda p: p.streak >= 7),
]

def _clean_text(value, limit):
    return value.strip()[:limit] if isinstance(value, str) and value.strip() and not any(ord(c) < 32 for c in value) else ""

def _entry(item):
    if not isinstance(item, dict): return None
    kind = item.get("kind"); key = _clean_text(item.get("key"), 500); title = _clean_text(item.get("title"), 200)
    if kind not in KINDS or not key or not title: return None
    if kind in {"source", "saved"} and not key.startswith("https://"): return None
    when = item.get("when", 0)
    return {"kind": kind, "key": key, "title": title, "when": float(when) if isinstance(when, (int, float)) and not isinstance(when, bool) else 0.0}

def _number(value, default=0):
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) else default

class Progress:
    def __init__(self, folder=None, clock=time.time, today=date.today):
        self.clock = clock; self.today = today; self.path = Path(folder) / "progress.json" if folder else None
        self.last = None; self.recent = []; self.favourites = []; self.scores = {}
        self.read = {}; self.words = {}; self.xp = 0; self.achievements = {}; self.millionaire = {}
        self.streak = 0; self.last_day = ""
        self.load()
    # ------------------------------------------------------------ storage
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
                try: best, last, total = (int(value.get(k, 0)) for k in ("best", "last", "total"))
                except (TypeError, ValueError): continue
                if 0 < total <= 100 and 0 <= best <= total and 0 <= last <= total:
                    self.scores[key] = {"best": best, "last": last, "total": total, "when": float(_number(value.get("when")))}
        read = raw.get("read", {})
        if isinstance(read, dict):
            self.read = {k[:120]: float(_number(v)) for k, v in list(read.items())[:MAX_READ] if isinstance(k, str) and k}
        words = raw.get("words", {})
        if isinstance(words, dict):
            for k, v in list(words.items())[:5000]:
                if isinstance(k, str) and isinstance(v, dict):
                    box = int(_number(v.get("box"))); due = float(_number(v.get("due")))
                    self.words[k[:20]] = {"box": max(0, min(5, box)), "due": due, "seen": int(_number(v.get("seen")))}
        self.xp = max(0, int(_number(raw.get("xp"))))
        ach = raw.get("achievements", {})
        if isinstance(ach, dict): self.achievements = {k[:40]: float(_number(v)) for k, v in ach.items() if isinstance(k, str)}
        mil = raw.get("millionaire", {})
        if isinstance(mil, dict): self.millionaire = {k: int(_number(mil.get(k))) for k in ("best_step", "best_prize", "games", "wins")}
        self.streak = max(0, int(_number(raw.get("streak")))); self.last_day = str(raw.get("last_day", ""))[:10]
    def save(self):
        if not self.path: return
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        fd, tmp = tempfile.mkstemp(dir=self.path.parent, prefix=".progress-")
        try:
            os.fchmod(fd, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump({"version": 2, "last": self.last, "recent": self.recent, "favourites": self.favourites, "scores": self.scores,
                           "read": self.read, "words": self.words, "xp": self.xp, "achievements": self.achievements,
                           "millionaire": self.millionaire, "streak": self.streak, "last_day": self.last_day},
                          handle, ensure_ascii=False, indent=1)
            os.replace(tmp, self.path)
        except BaseException:
            try: os.unlink(tmp)
            except OSError: pass
            raise
    def _save_quietly(self):
        try: self.save()
        except OSError: pass
    # ------------------------------------------------------------ activity
    def _touch_day(self):
        today = self.today(); key = today.isoformat()
        if self.last_day == key: return
        yesterday = (today - timedelta(days=1)).isoformat()
        self.streak = self.streak + 1 if self.last_day == yesterday else 1
        self.last_day = key; self.xp += XP["day"]
    def _check_achievements(self):
        new = []
        for key, test in ACHIEVEMENTS:
            if key not in self.achievements:
                try: ok = test(self)
                except (KeyError, TypeError, ValueError): ok = False
                if ok: self.achievements[key] = self.clock(); new.append(key)
        return new
    def opened(self, kind, key, title):
        """Remember the material opened last ("continue learning") and mark it read."""
        entry = _entry({"kind": kind, "key": key, "title": title, "when": self.clock()})
        if not entry: return []
        self.last = entry
        self.recent = [entry] + [e for e in self.recent if (e["kind"], e["key"]) != (kind, key)][:9]
        if kind in ("article", "municipality", "place", "day") and key not in self.read:
            if len(self.read) < MAX_READ: self.read[key] = self.clock(); self.xp += XP["read"]
        self._touch_day(); new = self._check_achievements(); self._save_quietly(); return new
    def is_read(self, key): return key in self.read
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
        """Keep the last and best result of a quiz (personal progress)."""
        key = _clean_text(key, 200)
        if not key or not 0 < int(total) <= 100 or not 0 <= int(score) <= int(total): raise ValueError("Invalid result.")
        old = self.scores.get(key, {})
        self.scores[key] = {"best": max(int(score), old.get("best", 0)) if old.get("total") == int(total) else int(score),
                            "last": int(score), "total": int(total), "when": self.clock()}
        if len(self.scores) > MAX_SCORES:
            for k in sorted(self.scores, key=lambda k: self.scores[k]["when"])[:len(self.scores) - MAX_SCORES]: del self.scores[k]
        self.xp += XP["quiz_right"] * int(score); self._touch_day(); self._check_achievements(); self._save_quietly()
        return self.scores[key]
    def result(self, key): return self.scores.get(key)
    # ---------------------------------------------------------- vocabulary
    def word_seen(self, word_id, correct):
        """Leitner boxes: right → next box (asked later), wrong → back to box 0."""
        w = self.words.get(word_id, {"box": 0, "due": 0.0, "seen": 0})
        box = min(5, w["box"] + 1) if correct else 0
        if correct and box > w["box"]: self.xp += XP["word"]
        self.words[word_id] = {"box": box, "due": self.clock() + BOX_DAYS[box] * 86400, "seen": w["seen"] + 1}
        self._touch_day(); self._check_achievements(); self._save_quietly(); return box
    def word_box(self, word_id): return self.words.get(word_id, {}).get("box", 0)
    def due_words(self, ids, limit=20):
        now = self.clock(); fresh = [i for i in ids if i not in self.words]
        due = sorted((i for i in ids if i in self.words and self.words[i]["due"] <= now), key=lambda i: self.words[i]["due"])
        return (due + fresh)[:limit]
    def words_learned(self): return sum(1 for w in self.words.values() if w["box"] >= 2)
    # --------------------------------------------------------- millionaire
    def millionaire_game(self, step, prize, won):
        m = self.millionaire
        m["games"] = m.get("games", 0) + 1; m["wins"] = m.get("wins", 0) + (1 if won else 0)
        m["best_step"] = max(m.get("best_step", 0), int(step)); m["best_prize"] = max(m.get("best_prize", 0), int(prize))
        self.xp += XP["millionaire_step"] * int(step); self._touch_day(); new = self._check_achievements(); self._save_quietly(); return new
    def unit_done(self, key):
        if f"unit:{key}" not in self.achievements:
            self.achievements[f"unit:{key}"] = self.clock(); self.xp += XP["unit"]; self._save_quietly()
    @property
    def level_name(self):
        """XP levels shown on the profile: 0, 100, 300, 700, 1500, 3000 …"""
        n = 0; need = 100
        while self.xp >= need and n < 20: n += 1; need = need * 2 + 100
        return n + 1
