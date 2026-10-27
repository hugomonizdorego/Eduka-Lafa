"""The millionaire game logic, the calendar export and the assistant's tips."""
import random
from datetime import date

from lafa import tips
from lafa.config import Settings
from lafa.progress import Progress

def game_module():
    from lafa.desk.pages import millionaire
    return millionaire

def test_questions_climb_in_difficulty_for_each_level(base):
    m = game_module()
    for level in ("eb1", "eb3", "sup"):
        qs = m.pick_questions(base, level, rng=random.Random(1))
        assert len(qs) == 15
        d = [q["difficulty"] for q in qs]
        assert d[0] <= d[-1] and len({(q["item"], q["index"]) for q in qs}) == 15

def test_prizes_safe_havens_and_walking_away(base):
    m = game_module(); g = m.Game(m.pick_questions(base, "es", rng=random.Random(2)), random.Random(3))
    for _ in range(4): assert g.choose(g.answer); g.advance()
    assert g.banked == 500 and g.guaranteed == 0
    assert g.choose(g.answer); g.advance()                 # question 5 right: $1 000 is safe
    assert g.guaranteed == 1000
    assert not g.choose((g.answer + 1) % 4) and g.over and g.prize == 1000
    g2 = m.Game(m.pick_questions(base, "es", rng=random.Random(4)), random.Random(5))
    g2.choose(g2.answer); g2.advance(); g2.walk_away()
    assert g2.prize == 100 and g2.reached == 1

def test_winning_the_million(base):
    m = game_module(); g = m.Game(m.pick_questions(base, "eb3", rng=random.Random(6)))
    for step in range(15):
        assert g.choose(g.answer)
        if step < 14: g.advance()
    assert g.won and g.prize == 1_000_000 and g.reached == 15

def test_lifelines(base):
    m = game_module(); g = m.Game(m.pick_questions(base, "eb2", rng=random.Random(7)), random.Random(8))
    hidden = g.fifty()
    assert len(hidden) == 2 and g.answer not in hidden and g.fifty() == set()
    votes = g.audience()
    assert sum(votes) == 100 and all(votes[i] == 0 for i in hidden)
    guess, conf = g.phone()
    assert guess not in hidden and 30 <= conf <= 99 and g.phone() is None

def test_ics_export(base):
    from lafa.desk.pages.calendar import ics_text
    text = ics_text(base, 2026, "tet")
    assert text.startswith("BEGIN:VCALENDAR\r\n") and text.endswith("END:VCALENDAR\r\n")
    assert text.count("BEGIN:VEVENT") == len(base.days_in_year(2026))
    assert all(len(line.encode("utf-8")) <= 75 for line in text.split("\r\n"))

def test_every_tip_kind(base, tmp_path):
    progress = Progress(tmp_path); settings = Settings(school_level="eb3", vocab_lang="pt")
    progress.opened("article", "tl.symbols.flag", "Flag"); progress.opened("article", "tl.symbols.flag", "Flag")
    for kind in tips.KINDS:
        tip = tips.tip_of(kind, base, progress, settings, "tet", date(2026, 5, 18), random.Random(1))
        if tip is None: continue
        assert tip.title and tip.icon, kind
        for label, route, item in tip.actions: assert route and (not item or base.get(item) or route == "map"), (kind, item)
        if tip.quiz: assert len(tip.quiz["options"]) == 4 and 0 <= tip.quiz["answer"] <= 3

def test_holiday_tip_comes_first_on_the_eve(base, tmp_path):
    chooser = tips.TipChooser(random.Random(2)); settings = Settings()
    first = chooser.next(base, Progress(tmp_path), settings, "en", date(2026, 5, 19))
    if base.get("day.restoration"): assert first.kind == "holiday"
    kinds = [chooser.next(base, Progress(tmp_path), settings, "en", date(2026, 5, 19)).kind for _ in range(12)]
    assert all(a != b for a, b in zip(kinds, kinds[1:]))
