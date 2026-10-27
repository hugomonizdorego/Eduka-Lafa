"""Lafa Desktop and the Virtual Assistant in an offscreen Qt session."""
import sys

import pytest

from lafa.config import Settings

ROUTES = ["home", "encyclopedia", "map", "timeline", "places", "calendar", "quiz", "language", "paths", "sources", "data", "settings", "about"]

@pytest.fixture
def errors(monkeypatch):
    seen = []
    monkeypatch.setattr(sys, "excepthook", lambda kind, value, tb: seen.append(value))
    return seen

def pump(app, n=6):
    for _ in range(n): app.processEvents()

def window(qapp, **values):
    from lafa.app import Window
    w = Window(Settings(**{"language": "tet", "learner_name": "Maria", "reduce_motion": True, **values}), review=True)
    w.resize(1366, 860); w.show(); pump(qapp); return w

def close(w):
    w.companion.close(); w.close()

@pytest.mark.parametrize("lang", ["tet", "pt", "id", "en"])
def test_every_page_opens(qapp, errors, lang):
    w = window(qapp, language=lang)
    for route in ROUTES:
        w.open(route); pump(qapp)
        assert w.route == route and w.stack.currentWidget() is w.pages[route]
    w.open("category", category="history"); w.open("search", q="Ramelau"); pump(qapp)
    assert not errors, errors
    close(w)

def test_items_of_every_kind_open(qapp, errors, base):
    w = window(qapp); first = base.all("article")[0].id
    for kind in ("article", "municipality", "place", "day"):
        items = base.all(kind)
        if not items: continue
        for item in items[:3]:
            w.open_item(item.id); pump(qapp)
            assert w.params["id"] == item.id
            page = w.pages["item"]; page.set_tab("quiz"); page.set_depth("simple"); page.set_tab("read"); pump(qapp)
    assert w.progress.is_read(first)
    w.go_back(); pump(qapp)
    assert not errors, errors
    close(w)

def test_millionaire_game_flow(qapp, errors):
    w = window(qapp); w.open("quiz"); page = w.pages["quiz"]
    page.start(); pump(qapp)
    assert page.game is not None and page.game.step == 1
    page.lifeline("fifty"); page.lifeline("audience"); page.lifeline("phone"); pump(qapp)
    page.choose(page.game.answer); pump(qapp, 10)
    assert page.revealed and page.next_button.isVisible()
    page.next_question(); pump(qapp)
    assert page.game.step == 2
    page.walk_away(); pump(qapp)
    assert page.game.over and w.progress.millionaire["games"] == 1
    assert not errors, errors
    close(w)

def test_language_page_tabs(qapp, errors):
    w = window(qapp, vocab_lang="th"); w.open("language"); page = w.pages["language"]
    for tab in ("words", "cards", "quiz"): page.set_tab(tab); pump(qapp)
    page.answer_quiz(0); pump(qapp); page.next_quiz(); pump(qapp)
    page.set_tab("cards"); page.answer_card(True); pump(qapp)
    assert w.progress.words
    assert not errors, errors
    close(w)

def test_settings_change_language_and_theme(qapp, errors):
    w = window(qapp); w.open("settings"); page = w.pages["settings"]
    page.language.setCurrentIndex(page.language.findData("pt")); page.theme.select("dark"); page.save(); pump(qapp)
    assert w.settings.language == "pt" and w.settings.theme == "dark" and w.tok["dark"]
    assert w.nav["home"].text().strip() == "Início"
    assert not errors, errors
    close(w)

def test_school_levels_and_unit_quiz(qapp, errors):
    w = window(qapp); w.open("paths"); page = w.pages["paths"]
    page.set_level("eb2"); page.make_mine(); pump(qapp)
    assert w.settings.school_level == "eb2"
    unit = w.kb.path("eb2")[0]["category"]; page.open_quiz(unit); pump(qapp)
    assert not errors, errors
    close(w)

def test_small_screen_and_compact_sidebar(qapp, errors):
    w = window(qapp); w.resize(1024, 600); pump(qapp)
    assert w.compact and w.sidebar.width() == 84
    w.open("home"); w.open("timeline"); pump(qapp)
    assert not errors, errors
    close(w)

def test_virtual_assistant(qapp, errors):
    w = window(qapp, companion=True, reduce_motion=False)
    c = w.companion; c.set_online(True); pump(qapp)
    c.show_bubble(); pump(qapp)
    assert c.popup.isVisible() and c.tip is not None
    c.ask.setText("tais"); c.search_live("tais"); pump(qapp)
    assert c.results.count() > 1
    opened = []; c.route_requested.connect(lambda r, i: opened.append((r, i)))
    c.tile("quiz"); c.follow("item", "tl.symbols.flag"); pump(qapp)
    assert ("quiz", "") in opened and w.route == "item"
    c.collapse(); pump(qapp)
    assert not c.popup.isVisible()
    from lafa import tips
    import random
    tip = tips.tip_of("quiz", w.kb, w.progress, w.settings, "tet", rng=random.Random(1))
    c.show_tip_balloon(tip, 0); pump(qapp)
    c.balloon.card.answer(tip.quiz["answer"]); pump(qapp)
    assert w.progress.result("assistant:quiz")["best"] == 1
    for outfit in ("casual", "traditional", "tuxedo"):
        w.change_outfit(outfit); pump(qapp)
        assert c.pet.costume == outfit and not w.atlas.pose_pixmap(outfit, 64).isNull()
    assert not errors, errors
    close(w)

def test_character_poses(qapp):
    from lafa.mascot import Atlas, Character
    atlas = Atlas()
    for outfit in ("casual", "traditional", "tuxedo"):
        assert not atlas.pixmap("greeting", 120, outfit).isNull()
        assert atlas.pixmap("idle", 120, outfit) is atlas.pixmap("idle", 120, outfit)   # cached
    pet = Character(atlas, size=150); pet.set_state("greeting"); pet.tick(); pet.grab()
    assert pet.state == "greeting"
