#!/usr/bin/env python3
"""Screenshots of Lafa 0.3 for docs/screenshots (implementation, not concept art).

    python3 scripts/capture-screenshots.py            # all pages, languages, themes
    python3 scripts/capture-screenshots.py --scaled   # (internal) 150 % captures

Runs offscreen in review mode (sample learner, nothing saved or sent).
"""
import os
import random
import subprocess
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
OUT = ROOT / "docs" / "screenshots"

from lafa.qt import QApplication, QPixmap, QPainter, QColor, prepare_application  # noqa: E402
prepare_application()
app = QApplication([]); app.setStyle("Fusion")
from lafa.desk import theme  # noqa: E402
theme.load_fonts(); app.setFont(theme.app_font())
from lafa.app import Window  # noqa: E402
from lafa.config import Settings  # noqa: E402
from lafa import tips  # noqa: E402

def pump(n=20):
    for _ in range(n): app.processEvents()

def window(lang="tet", size=(1366, 860), **values):
    w = Window(Settings(language=lang, learner_name="Maria", school_level="eb3", reduce_motion=True, **values), review=True)
    w.resize(*size); w.show(); pump(); return w

def save(w, name, route=None, **params):
    if route: w.open(route, **params)
    pump(); w.grab().save(str(OUT / name)); print("saved", name)

def main_set():
    OUT.mkdir(parents=True, exist_ok=True)
    w = window("tet")
    first_place = next(iter(w.kb.places()), None); first_day = next(iter(w.kb.days()), None)
    shots = [("01-home.png", "home", {}), ("02-encyclopedia.png", "encyclopedia", {}), ("03-category-history.png", "category", {"category": "history"}),
             ("04-article-flag.png", "item", {"id": "tl.symbols.flag"}), ("05-article-presidents.png", "item", {"id": "tl.leaders.presidents"}),
             ("06-map.png", "map", {}), ("07-municipality-baucau.png", "item", {"id": "mun.baucau"}), ("08-timeline.png", "timeline", {}),
             ("09-tourism.png", "places", {}), ("11-calendar.png", "calendar", {}), ("13-millionaire-start.png", "quiz", {}),
             ("15-language-words.png", "language", {}), ("18-school-levels.png", "paths", {}), ("19-sources-licences.png", "sources", {}),
             ("20-offline-updates.png", "data", {}), ("21-settings.png", "settings", {}), ("22-about.png", "about", {}), ("23-search.png", "search", {"q": "Ramelau"})]
    for name, route, params in shots: save(w, name, route, **params)
    if first_place: save(w, "10-place.png", "item", id=first_place.id)
    if first_day: save(w, "12-holiday.png", "item", id=first_day.id)
    page = w.pages["item"]; w.open("item", id="tl.symbols.flag"); page.set_tab("quiz"); save(w, "04b-article-quiz.png")
    w.open("quiz"); quiz = w.pages["quiz"]; quiz.start(); quiz.game.rng = random.Random(4)
    for _ in range(2): quiz.choose(quiz.game.answer); pump(); quiz.next_question()
    quiz.lifeline("fifty"); quiz.lifeline("audience"); save(w, "14-millionaire-game.png")
    lang = w.pages["language"]; w.open("language"); lang.set_tab("cards"); save(w, "16-language-flashcards.png")
    lang.set_tab("quiz"); lang.answer_quiz(0); save(w, "17-language-quiz.png")
    w.companion.close(); w.close()
    for code, name in (("pt", "30-home-portugues.png"), ("id", "31-home-indonesia.png"), ("en", "32-home-english.png")):
        w = window(code); save(w, name, "home"); w.companion.close(); w.close()
    w = window("tet", theme="dark"); save(w, "33-home-dark.png", "home"); save(w, "34-article-dark.png", "item", id="tl.culture.tais")
    save(w, "35-quiz-dark.png", "quiz"); w.companion.close(); w.close()
    w = window("tet", (1024, 600)); save(w, "36-home-1024x600.png", "home"); save(w, "37-article-1024x600.png", "item", id="tl.history.restoration_2002")
    w.companion.close(); w.close()
    assistant_shots()
    outfit_sheet()

def assistant_shots():
    for i, outfit in enumerate(("traditional", "casual", "tuxedo")):
        w = Window(Settings(language="tet", learner_name="Maria", companion=True, costume=outfit, reduce_motion=True, quiet_mode=False), review=True)
        c = w.companion; c.set_online(True); pump(); c.chooser.rng = random.Random(3 + i)
        c.show_bubble(); pump(40); popup = c.grab()
        tip = tips.tip_of(("quiz", "holiday", "word")[i], w.kb, w.progress, w.settings, "tet", rng=random.Random(5)) or tips.welcome("tet")
        c.collapse(); c.show_tip_balloon(tip, 0); pump(40)
        bal = c.balloon.grab(); pet = c.grab()
        canvas = QPixmap(popup.width() + bal.width() + 60, max(popup.height(), bal.height() + pet.height())); canvas.fill(QColor("#d9d2f3"))
        p = QPainter(canvas); p.drawPixmap(0, 0, popup); p.drawPixmap(popup.width() + 30, 0, bal)
        p.drawPixmap(popup.width() + 30 + bal.width() - pet.width(), bal.height() - 12, pet); p.end()
        canvas.save(str(OUT / f"4{i}-assistant-{outfit}.png")); print("saved", f"4{i}-assistant-{outfit}.png")
        c.close(); w.close()

def outfit_sheet():
    from lafa.mascot import Atlas
    atlas = Atlas(); states = ["greeting", "idle", "reading", "studying", "thinking", "tebe"]
    sheet = QPixmap(len(states) * 190, 3 * 200); sheet.fill(QColor("#f3efff")); p = QPainter(sheet)
    for r, outfit in enumerate(("casual", "traditional", "tuxedo")):
        for c, state in enumerate(states): p.drawPixmap(c * 190 + 5, r * 200 + 5, atlas.pixmap(state, 185, outfit))
    p.end(); sheet.save(str(OUT / "50-outfits-and-poses.png")); print("saved 50-outfits-and-poses.png")

def scaled():
    w = window("tet", (1024, 600)); save(w, "38-home-150pct.png", "home"); save(w, "39-article-150pct.png", "item", id="tl.symbols.flag")
    w.companion.close(); w.close()

if __name__ == "__main__":
    if "--scaled" in sys.argv: scaled()
    else:
        for old in OUT.glob("*.png"): old.unlink()
        main_set()
        subprocess.run([sys.executable, __file__, "--scaled"], env={**os.environ, "QT_SCALE_FACTOR": "1.5"}, check=False)
    os._exit(0)
