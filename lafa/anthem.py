"""The national anthem «Pátria»: lyrics and the time of each sung line in the
recording (lafa/assets/timor/anthem/patria.json + patria.mp3)."""
import json
from functools import lru_cache

from . import kb

FOLDER = kb.ASSETS / "anthem"

@lru_cache(maxsize=1)
def load():
    try: data = json.loads((FOLDER / "patria.json").read_text(encoding="utf-8"))
    except (OSError, ValueError): data = {"lines": [], "cues": [], "sections": []}
    data["path"] = str(FOLDER / data.get("audio", "patria.mp3"))
    return data

def at(data, seconds):
    """(line index or None, progress 0–1 inside the line, section name or None) at a time."""
    for start, end, line in data.get("cues", []):
        if start <= seconds < end: return line, (seconds - start) / max(0.01, end - start), None
    for start, end, name in data.get("sections", []):
        if start <= seconds < end: return None, 0.0, name
    return None, 0.0, None

def next_time(data, line, after=0.0):
    """When the line is sung next (from `after`), else the first time it is sung, else None."""
    times = [start for start, _end, i in data.get("cues", []) if i == line]
    later = [t for t in times if t >= after]
    return (later or times or [None])[0]

def clock(seconds):
    seconds = max(0, int(seconds)); return f"{seconds // 60}:{seconds % 60:02d}"
