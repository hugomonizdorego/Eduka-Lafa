"""Reminders that work without internet.

* Dated reminders are saved in the learner's LAFA folder (reminders.json,
  0600, written atomically) and survive a restart.
* While LAFA is running they fire offline too (LAFA checks every few seconds).
* A reminder whose time passed while LAFA was closed is shown once, as
  "missed", at the next start; it never fires again.
* Focus timers belong to the current session only (they are not saved) and
  are labelled so in the interface. LAFA has no system scheduler: when LAFA is
  completely closed, nothing rings.
"""
from dataclasses import dataclass, asdict
import json
import os
import tempfile
import time
from pathlib import Path

MAX_TEXT = 240
MAX_ITEMS = 500
KEEP_FIRED_DAYS = 7

@dataclass
class Reminder:
    id: int
    text: str
    due: float              # seconds since the epoch (wall clock)
    created: float = 0.0
    fired: bool = False
    session: bool = False   # focus timers: this session only, never saved
    missed: bool = False    # fired late because LAFA was closed

def _valid(item):
    """A Reminder from stored data, or None when the entry is damaged."""
    if not isinstance(item, dict): return None
    try:
        rid, text, due = item["id"], item["text"], item["due"]
        if isinstance(rid, bool) or not isinstance(rid, int) or rid <= 0: return None
        if not isinstance(text, str) or not text.strip() or len(text) > MAX_TEXT or any(ord(c) < 32 for c in text): return None
        if isinstance(due, bool) or not isinstance(due, (int, float)) or not 0 < due < 32503680000: return None
        created = item.get("created", 0.0); fired = item.get("fired", False)
        return Reminder(rid, text.strip(), float(due), float(created) if isinstance(created, (int, float)) and not isinstance(created, bool) else 0.0,
                        fired if isinstance(fired, bool) else False)
    except (KeyError, TypeError, ValueError):
        return None

class Reminders:
    """Reminders saved in `folder` (None: memory only, e.g. tests and review)."""
    def __init__(self, folder=None, clock=time.time):
        self.clock = clock; self.items = []; self.next_id = 1
        self.path = Path(folder) / "reminders.json" if folder else None
        self.started = clock()
        self.load()
    # ---------------------------------------------------------- storage
    def load(self):
        if not self.path: return
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError, UnicodeError):
            return
        items = [r for r in (_valid(x) for x in (raw.get("items", []) if isinstance(raw, dict) else [])[:MAX_ITEMS]) if r]
        ids = set(); clean = []
        for r in items:
            if r.id not in ids: ids.add(r.id); clean.append(r)
        self.items = clean; self.next_id = max([r.id for r in clean], default=0) + 1
    def save(self):
        if not self.path: return
        old = self.clock() - KEEP_FIRED_DAYS * 86400
        keep = [r for r in self.items if not r.session and (not r.fired or r.due >= old)]
        data = {"version": 1, "items": [{k: v for k, v in asdict(r).items() if k not in ("session", "missed")} for r in keep]}
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        fd, tmp = tempfile.mkstemp(dir=self.path.parent, prefix=".reminders-")
        try:
            os.fchmod(fd, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as handle: json.dump(data, handle, ensure_ascii=False, indent=1)
            os.replace(tmp, self.path)
        except BaseException:
            try: os.unlink(tmp)
            except OSError: pass
            raise
    # ---------------------------------------------------------- changes
    def _check_text(self, text):
        text = str(text).strip()
        if not text or len(text) > MAX_TEXT or any(ord(c) < 32 for c in text): raise ValueError("Enter a reminder of 1–240 characters.")
        return text
    def add(self, minutes, text, session=False):
        """Reminder in `minutes` (1 minute – 24 hours)."""
        minutes = float(minutes)
        if not 1 <= minutes <= 1440: raise ValueError("Reminder must be between 1 minute and 24 hours.")
        return self.add_at(self.clock() + minutes * 60, text, session)
    def add_at(self, when, text, session=False):
        """Reminder at a date and time (seconds since the epoch), up to a year ahead."""
        text = self._check_text(text); now = self.clock(); when = float(when)
        if not now < when <= now + 366 * 86400: raise ValueError("Choose a time in the future (within one year).")
        if len([r for r in self.items if not r.fired]) >= MAX_ITEMS: raise ValueError("Too many reminders.")
        reminder = Reminder(self.next_id, text, when, now, False, session); self.next_id += 1
        self.items.append(reminder)
        if not session: self.save()
        return reminder
    def cancel(self, identifier):
        before = len(self.items); self.items = [r for r in self.items if r.id != identifier]
        if len(self.items) != before: self.save()
    # ---------------------------------------------------------- firing
    @property
    def pending(self):
        return sorted((r for r in self.items if not r.fired), key=lambda r: r.due)
    def due(self, online=True):
        """Reminders whose time has come; each fires exactly once (offline too).

        `online` is ignored: reminders never depend on the internet."""
        now = self.clock(); fired = []
        for r in self.items:
            if not r.fired and r.due <= now:
                r.fired = True; r.missed = r.due < self.started; fired.append(r)
        if fired:
            if any(not r.session for r in fired): self.save()
            self.items = [r for r in self.items if not (r.session and r.fired)]
        return fired
    def missed(self):
        """Reminders that passed while LAFA was closed (shown once, at start)."""
        return [r for r in self.due() if r.missed]
    def remaining(self, item):
        return max(0, int(item.due - self.clock()))
    def next(self):
        pending = self.pending
        return pending[0] if pending else None
