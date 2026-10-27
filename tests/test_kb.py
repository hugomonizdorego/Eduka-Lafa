"""Knowledge base: search, calendar, timeline, learning paths, updates."""
import json
from datetime import date

from lafa import kb

def test_search_puts_title_matches_first(base):
    assert base.search("bandeira", "tet", 3)[0][0].id == "tl.symbols.flag"
    assert base.search("Xanana", "en", 3)[0][0].id.startswith("tl.leaders.xanana")
    assert base.search("Santa Cruz", "pt", 3)[0][0].id in ("place.santa_cruz_cemetery", "tl.conflicts.santa_cruz_1991")

def test_search_ignores_accents_apostrophes_and_types_ahead(base):
    assert base.search("Atauro", "tet", 5) and base.search("ataúro", "tet", 5)
    assert base.search("ne'e", "tet", 5) == base.search("nee", "tet", 5)
    assert base.search("bande", "tet", 3)[0][0].id == "tl.symbols.flag"    # prefix of the last word

def test_word_search_and_indonesian_meaning(base):
    word = base.search_words("bondia", "pt")[0]
    assert word.tet == "bondia" and word.meaning("id") == "selamat pagi" and word.meaning("pt") == "bom dia"

def test_easter_and_moving_days():
    assert kb.easter(2026) == date(2026, 4, 5) and kb.easter(2027) == date(2027, 3, 28)

def test_day_dates(base):
    days = base.days_in_year(2026)
    assert days, "days.json"
    assert all(when.year == 2026 for when, _ in days)
    restoration = base.get("day.restoration")
    if restoration: assert base.day_date(restoration, 2026) == date(2026, 5, 20)
    upcoming = base.upcoming(date(2026, 12, 30), 3)
    assert all(when >= date(2026, 12, 30) for when, _ in upcoming)

def test_dates_before_the_common_era():
    assert kb.format_when("-44000", "en") == "44 000 years ago"
    assert kb.format_when("-2500", "en") == "2500 BCE"
    assert kb.format_when("1975-11-28", "pt") == "28 novembro 1975"

def test_timeline_is_sorted_and_eras_follow_dates(base):
    events = base.timeline("en")
    assert len(events) >= 150
    assert [e["key"] for e in events] == sorted(e["key"] for e in events)
    assert kb.era_of((1975, 11, 28)) == "decolonisation" and kb.era_of((1975, 12, 7)) == "occupation"
    assert kb.era_of((2002, 5, 20)) == "state" and kb.era_of((-42000, 0, 0)) == "prehistory"

def test_questions_by_difficulty(base):
    easy = base.questions(None, 1, 5); hard = base.questions(None, 11, 15)
    assert easy and hard and all(1 <= q["difficulty"] <= 5 for q in easy)

def test_learning_path_is_chronological_for_history(base):
    units = base.path("es")
    history = next(u for u in units if u["category"] == "history")["items"]
    starts = [i.get("period", {}).get("from") for i in history if isinstance(i.get("period"), dict) and isinstance(i.get("period", {}).get("from"), (int, float))]
    assert starts == sorted(starts)
    for level in kb.LEVELS: assert base.path(level), level

def test_downloaded_update_replaces_a_packaged_file(tmp_path):
    updates = tmp_path / "updates" / "content"; updates.mkdir(parents=True)
    original = json.loads((kb.ASSETS / "content" / "symbols_society.json").read_text())
    flag = next(a for a in original["articles"] if a["id"] == "tl.symbols.flag")
    flag = dict(flag, title=dict(flag["title"], en="Flag (updated)"))
    (updates / "symbols_society.json").write_text(json.dumps({"articles": [flag]}), encoding="utf-8")
    base = kb.KnowledgeBase(overrides=tmp_path / "updates")
    assert base.get("tl.symbols.flag").title("en") == "Flag (updated)"
    (updates / "broken.json").write_text("{not json", encoding="utf-8")
    assert kb.KnowledgeBase(overrides=tmp_path / "updates").get("tl.symbols.flag")

def test_sources_are_collected_once(base):
    sources = base.sources()
    urls = [s["url"] for s in sources]
    assert len(urls) == len(set(urls)) and all(s["items"] for s in sources)
