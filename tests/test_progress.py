"""Learning progress: reading, achievements, spaced repetition, the quiz game."""
import json
from datetime import date, timedelta

from lafa.progress import Progress, BOX_DAYS

class Clock:
    def __init__(self): self.t = 1_000_000.0
    def __call__(self): return self.t

def test_reading_gives_xp_and_achievements(tmp_path):
    p = Progress(tmp_path)
    assert p.opened("article", "tl.symbols.flag", "Flag") == ["first_read"]
    assert p.is_read("tl.symbols.flag") and p.xp > 0
    assert p.opened("article", "tl.symbols.flag", "Flag") == []      # once
    again = Progress(tmp_path)
    assert again.is_read("tl.symbols.flag") and again.last["key"] == "tl.symbols.flag"

def test_leitner_boxes(tmp_path):
    clock = Clock(); p = Progress(tmp_path, clock=clock)
    assert p.word_seen("w0001", True) == 1 and p.word_seen("w0001", True) == 2
    assert p.words["w0001"]["due"] == clock.t + BOX_DAYS[2] * 86400
    assert p.word_seen("w0001", False) == 0
    assert p.due_words(["w0001", "w0002"]) == ["w0001", "w0002"]

def test_streak_counts_days_in_a_row(tmp_path):
    days = [date(2026, 10, 25)]
    p = Progress(tmp_path, today=lambda: days[0])
    p.opened("article", "a", "A"); days[0] += timedelta(days=1); p.opened("article", "b", "B")
    assert p.streak == 2
    days[0] += timedelta(days=3); p.opened("article", "c", "C")
    assert p.streak == 1

def test_millionaire_results(tmp_path):
    p = Progress(tmp_path)
    assert "millionaire_safe" in p.millionaire_game(7, 2000, False)
    assert "millionaire_win" in p.millionaire_game(15, 1_000_000, True)
    assert p.millionaire["best_prize"] == 1_000_000 and p.millionaire["games"] == 2

def test_version_1_files_still_load(tmp_path):
    (tmp_path / "progress.json").write_text(json.dumps({"last": {"kind": "article", "key": "tl.x", "title": "X", "when": 1},
                                                         "scores": {"quiz:a": {"best": 3, "last": 2, "total": 4, "when": 1}}}))
    p = Progress(tmp_path)
    assert p.last["key"] == "tl.x" and p.result("quiz:a")["best"] == 3

def test_bad_files_are_ignored(tmp_path):
    (tmp_path / "progress.json").write_text("[1, 2")
    assert Progress(tmp_path).xp == 0
