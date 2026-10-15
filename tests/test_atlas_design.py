"""0.1.3: Timor-Leste atlas, online refresh, more subjects and the new design."""
import json
import os
from pathlib import Path
import random
import tempfile
import unittest
from unittest.mock import patch
from lafa import timor_atlas, livefacts, classroom, ui_kit
from lafa.config import Settings
from lafa.net import NetworkError

class AtlasData(unittest.TestCase):
    def test_categories_and_topics(self):
        keys = timor_atlas.CATEGORY_KEYS
        self.assertEqual(len(keys), len(set(keys)))
        for required in ("earth", "symbols", "map", "islands", "nature", "economy", "people", "regions", "tourism", "leaders", "government", "politics"):
            self.assertIn(required, keys)
        self.assertEqual(len({t.key for t in timor_atlas.TOPICS}), len(timor_atlas.TOPICS))
        for t in timor_atlas.TOPICS:
            self.assertIn(t.category, keys)
            for lang in ("en", "id"):
                self.assertTrue(timor_atlas.text(t.title, lang) and timor_atlas.text(t.summary, lang), (t.key, lang))
            for lang in ("pt", "tet"): self.assertTrue(timor_atlas.text(t.summary, lang))
            self.assertIn(t.size, (1, 2, 3))
        for key in ("atauro", "jaco", "oecusse", "flag", "coat_of_arms", "anthem", "population", "exports", "imports", "map_history", "system", "elections"):
            self.assertIsNotNone(timor_atlas.find(key), key)
    def test_leaders_and_municipalities(self):
        self.assertEqual(timor_atlas.PRESIDENTS[2][0], "Xanana Gusmão"); self.assertEqual(timor_atlas.PRESIDENTS[-1][2], "—")
        self.assertEqual(timor_atlas.PRIME_MINISTERS[1][0], "Mari Alkatiri"); self.assertEqual(timor_atlas.PRIME_MINISTERS[-1][0], "Xanana Gusmão")
        self.assertEqual(len(timor_atlas.MUNICIPALITY_NOTES), 14)
        questions = timor_atlas.leader_questions("pt", random.Random(2))
        self.assertGreaterEqual(len(questions), 8)
        for q, options, correct in questions: self.assertIn(correct, options); self.assertEqual(len(set(options)), 4)

class LiveFacts(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory(); self.env = patch.dict(os.environ, {"XDG_CACHE_HOME": self.folder.name}); self.env.start()
    def tearDown(self):
        self.env.stop(); self.folder.cleanup()
    @staticmethod
    def wiki(lang, params):
        """Recorded MediaWiki answers (no network)."""
        if lang == "en":
            return {"query": {"pages": [{"title": "Flag of East Timor", "extract": "The flag of East Timor is red.\\n" + "x " * 2000,
                                         "langlinks": [{"lang": "tet", "title": "Bandeira Timor-Leste"}]}]}}
        return {"query": {"pages": [{"title": params["titles"], "extract": "Bandeira Timor-Leste nian mean."}]}}
    def test_fetch_prefers_reader_language_and_caches(self):
        topic = timor_atlas.find("flag")
        updated, failed = livefacts.refresh([topic], "tet", request=self.wiki)
        self.assertEqual((updated, failed), (1, 0))
        entry = livefacts.get("flag", "tet")
        self.assertEqual(entry["lang"], "tet"); self.assertEqual(entry["url"], "https://tet.wikipedia.org/wiki/Bandeira_Timor-Leste")
        self.assertEqual(livefacts.cache_path().stat().st_mode & 0o777, 0o600)
        # Fresh entries are not downloaded again; English falls back and is bounded.
        self.assertEqual(livefacts.refresh([topic], "tet", request=self.wiki), (0, 0))
        english = livefacts.fetch("Flag of East Timor", "en", self.wiki)
        self.assertEqual(english["lang"], "en"); self.assertLessEqual(len(english["text"]), livefacts.MAX_TEXT + 1)
    def test_failures_and_bad_cache_are_harmless(self):
        def broken(lang, params): raise NetworkError("offline")
        self.assertEqual(livefacts.refresh([timor_atlas.find("flag")], "en", request=broken), (0, 1))
        path = livefacts.cache_path(); path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"flag:en": {"lang": "en", "title": "x", "text": "y", "url": "http://evil.example/", "fetched": "2026-01-01 10:00"}, "bad": 3}))
        self.assertEqual(livefacts.load(), {})
        missing = lambda lang, params: {"query": {"pages": [{"missing": True}]}}
        with self.assertRaises(NetworkError): livefacts.fetch("Nothing", "en", missing)
    def test_staleness(self):
        from datetime import datetime
        self.assertTrue(livefacts.stale({"fetched": "2026-01-01 10:00"}, 24, datetime(2026, 1, 2, 11, 0)))
        self.assertFalse(livefacts.stale({"fetched": "2026-01-02 10:00"}, 24, datetime(2026, 1, 2, 11, 0)))
        self.assertTrue(livefacts.stale({}, 24))

class Subjects(unittest.TestCase):
    def test_new_subjects(self):
        for subject in ("civics", "geography", "health"):
            self.assertIn(subject, classroom.SUBJECTS); self.assertTrue(classroom.lessons(subject))
            self.assertNotEqual(classroom.subject_name(subject, "tet"), subject)
            items = classroom.questions(subject, "id", 10, random.Random(4))
            self.assertEqual(len(items), min(10, classroom.available(subject, "id"))); self.assertEqual(len({q.text for q in items}), len(items))
        history = classroom.questions("history", "en", 200, random.Random(1))
        self.assertTrue(any("Prime Minister" in q.text for q in history))

class Palette(unittest.TestCase):
    def test_light_and_dark_never_black(self):
        light, dark = ui_kit.palette("#00a879"), ui_kit.palette("#26a69a", True)
        self.assertEqual(light["accent"], "#00a879"); self.assertTrue(dark["dark"])
        for tokens in (light, dark):
            for name in ("bg1", "bg2", "surface", "side"): self.assertNotIn(tokens[name].lower(), ("#000000", "#000"))
        self.assertEqual(ui_kit.palette("not-a-colour")["accent"], "#00a879")

class DesignUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from lafa.qt import QApplication
        cls.app = QApplication.instance() or QApplication([])
    def setUp(self):
        from lafa.app import Window
        self.w = Window(Settings(language="en"), review=True); self.w.show(); self.app.processEvents()
    def tearDown(self):
        self.w.companion.close(); self.w.close(); self.w.deleteLater(); self.app.processEvents()
    def test_home_has_four_quick_cards_and_keyboard(self):
        titles = [c.heading.text() for c in self.w.home_quick]
        self.assertEqual(titles, ["Start learning", "Find knowledge", "Tasks & schedule", "OS help"])
        from lafa.qt import QKeyEvent, QEvent, Qt
        self.w.home_quick[2].keyPressEvent(QKeyEvent(QEvent.KeyPress, Qt.Key_Return, Qt.NoModifier))
        self.assertEqual(self.w.current_section(), "activities")
        self.w.home_quick[0].keyPressEvent(QKeyEvent(QEvent.KeyPress, Qt.Key_Return, Qt.NoModifier))
        self.assertEqual(self.w.current_section(), "study")
    def test_continue_learning_and_favourites(self):
        self.assertFalse(self.w.continue_button.isVisibleTo(self.w))
        self.w.progress.opened("lesson", "lafa://lesson/school/science:0", "Water cycle"); self.w.refresh_home()
        self.assertEqual(self.w.home_recent.text(), "Water cycle"); self.assertTrue(self.w.continue_button.isVisibleTo(self.w))
        self.assertTrue(self.w.progress.toggle_favourite("lesson", "lafa://lesson/school/science:0", "Water cycle"))
        self.assertTrue(self.w.progress.is_favourite("lesson", "lafa://lesson/school/science:0"))
    def test_timor_encyclopedia_category_article_back_and_live_text(self):
        self.w.navigate("culture"); b = self.w.timor_browser
        self.assertEqual(b.state["kind"], "home")
        b.open_category("leaders"); self.assertEqual(b.state["kind"], "category")
        ids = [a.id for a in __import__("lafa.encyclopedia", fromlist=["x"]).articles("timor", "leaders")]
        self.assertIn("atlas:presidents", ids); self.assertIn("atlas:prime_ministers", ids)
        b.open_article("atlas:presidents"); self.assertEqual(b.state["kind"], "article")
        self.assertIn("Ramos-Horta", b.page.reader.toPlainText()); self.assertIn("2008", b.page.reader.toPlainText())
        b.go_back()
        self.assertEqual(b.state["kind"], "category")
        with patch("lafa.offline_pack.extract", return_value=None), \
             patch("lafa.livefacts.get", return_value={"lang": "tet", "title": "x", "text": "Testu foun", "url": "https://tet.wikipedia.org/wiki/X", "fetched": "2026-10-13 09:00"}):
            b.open_article("atlas:flag")
        text = b.page.reader.toPlainText()
        self.assertIn("Testu foun", text); self.assertIn("2026-10-13", text)

if __name__ == "__main__": unittest.main()
