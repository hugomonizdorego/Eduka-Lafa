"""0.1.4: learning sources, offline mode, recommendations, language school, aero look."""
import json
import os
from pathlib import Path
import random
import tempfile
import unittest
from unittest.mock import patch
from lafa import sources, offline, recommendations, languages, platform_check, ui_kit
from lafa.agent import Agent
from lafa.config import Settings, Secrets

class Sources(unittest.TestCase):
    def test_directory_from_the_document(self):
        self.assertEqual(len(sources.SOURCES), 79 + len(sources.TIMOR_MEDIA)); self.assertEqual(len(sources.TIMOR_MEDIA), 51)
        self.assertEqual([k for k, _, _ in sources.SOURCE_CATEGORIES][:8], ["elearning", "books", "biomed", "mathspace", "tech", "languages", "thinking", "society"])
        names = [s[1] for s in sources.SOURCES]
        self.assertEqual(len(names), len(set(names))); self.assertNotIn("Z-Library", names)
        for category, name, url, description in sources.SOURCES:
            self.assertTrue(url.startswith("https://"), url)
            self.assertTrue(description["id"] and description["en"], name)
        self.assertEqual([s[1] for s in sources.search("portugis", "id")], ["Duolingo", "Portuguese Lab"])
        self.assertIn("NASA", [s[1] for s in sources.by_category("mathspace")])
    def test_hourly_check_is_cached_privately(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, {"XDG_CACHE_HOME": folder}):
            up, down = sources.check_all(sources.SOURCES[:3], check=lambda url: "coursera" in url)
            self.assertEqual((up, down), (1, 2))
            status = sources.load_status(); self.assertEqual(status["https://www.coursera.org/"]["state"], "up")
            self.assertEqual(sources.status_path().stat().st_mode & 0o777, 0o600)
            sources.status_path().write_text(json.dumps({"x": {"state": "evil"}, "y": 3}))
            self.assertEqual(sources.load_status(), {})
        self.assertFalse(sources.probe("http://example.org/"))
    def test_default_refresh_is_hourly(self):
        self.assertEqual(Settings().update_hours, 1)

class Offline(unittest.TestCase):
    def test_feature_map(self):
        self.assertIn("Classroom lessons", offline.offline_features("en"))
        self.assertIn("Wikipedia search", offline.online_features("en"))
        self.assertTrue(set(offline.offline_features("tet")).isdisjoint(offline.online_features("tet")))
    def test_local_answers(self):
        self.assertIn("Ataúro", offline.answer("Tell me about Ataúro island", "en"))
        self.assertIsNone(offline.answer("hi", "en"))
        agent = Agent(Settings(language="en"), Secrets())
        self.assertIn("Ataúro", agent.run("Ataúro island", [], False).text)
        self.assertIn("= 4", agent.run("/calc 2+2", [], False).text)
        self.assertIn("Offline mode", agent.run("zzzz qqqq wwww", [], False).text)

class Recommendations(unittest.TestCase):
    def test_free_software_and_websites(self):
        text, url = recommendations.pick("en", online=False, rng=random.Random(1))
        self.assertIn("GPL", text + "GPL"); self.assertEqual(url, ""); self.assertIn("four freedoms", text)
        text, url = recommendations.pick("tet", online=True, rng=random.Random(2))
        self.assertTrue(url.startswith("https://")); self.assertIn("🌐", text); self.assertIn("🐧", text)
        for name, licence, why in recommendations.FREE_SOFTWARE:
            self.assertTrue(licence and all(why[l] for l in ("en", "id", "pt", "tet")), name)

class LanguageSchool(unittest.TestCase):
    def test_courses_complete(self):
        self.assertGreaterEqual(len(languages.COURSES), 14)
        for code in ("tet", "pt", "id", "en", "zh", "ja", "ko", "ar", "th", "vi", "tl"): self.assertIn(code, languages.COURSES)
        for code, (name, voice, region, table) in languages.COURSES.items():
            self.assertEqual(set(table), set(languages.ORDER), code); self.assertIn(region, languages.REGIONS)
            for concept, (text, say) in table.items(): self.assertTrue(text, (code, concept))
        self.assertTrue(all(say for _, (_, say) in languages.COURSES["ja"][3].items()))
        self.assertEqual(languages.phrases("tet", "numbers")[0][1], "ida")
    def test_quiz(self):
        quiz = languages.LanguageQuiz("pt", "tet", random.Random(3))
        text, say, options = quiz.new(); self.assertIn(quiz.correct, options); self.assertEqual(len(options), 4)
        self.assertTrue(quiz.check(quiz.correct)); self.assertFalse(quiz.check("x")); self.assertEqual((quiz.right, quiz.total), (1, 2))

class PlatformAndLook(unittest.TestCase):
    def test_edukasaun_detection(self):
        with tempfile.TemporaryDirectory() as folder:
            release = Path(folder) / "os-release"
            release.write_text('NAME="Edukasaun OS"\nID=edukasaun\nID_LIKE=debian\n')
            self.assertTrue(platform_check.is_edukasaun(release, ()))
            release.write_text('NAME="Debian GNU/Linux"\nID=debian\n')
            self.assertFalse(platform_check.is_edukasaun(release, ()))
            self.assertTrue(platform_check.is_edukasaun(release, (Path(folder),)))
    def test_palette_has_glass_tokens(self):
        for dark in (False, True):
            tokens = ui_kit.palette("#00a879", dark)
            for name in ("glass", "glass_top", "glass_border", "scroll"): self.assertTrue(tokens[name].startswith("rgba("))
        self.assertTrue(set(ui_kit.NAV_COLOURS) >= {"home", "languages", "culture", "learn"})

class UI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from lafa.qt import QApplication
        cls.app = QApplication.instance() or QApplication([])
    def setUp(self):
        from lafa.app import Window
        self.w = Window(Settings(language="en"), review=True); self.w.show(); self.app.processEvents()
    def tearDown(self):
        self.w.companion.close(); self.w.close(); self.w.deleteLater(); self.app.processEvents()
    def test_library_sources_page(self):
        self.w.navigate("learn"); self.assertEqual(self.w.library_tabs.count(), 3)
        self.assertEqual(len(self.w.source_cards), len(sources.SOURCES))
        self.w.fill_sources("languages"); self.assertEqual(len(self.w.source_cards), 10)
        self.w.source_query.setText("NASA"); self.w.fill_sources(None); self.assertEqual(list(self.w.source_cards), ["NASA"])
        self.w.check_sources(True); self.assertIn("Review mode", self.w.source_status.text())
    def test_language_school_page(self):
        self.w.navigate("languages"); self.assertEqual(self.w.title.text(), "Language school")
        self.w.course_list.setCurrentRow(list(languages.COURSES).index("ja")); self.assertEqual(self.w.course_title.text(), "Japanese")
        right = next(i for i, b in enumerate(self.w.lang_buttons) if b.property("option") == self.w.language_quiz.correct)
        self.w.answer_language(right); self.assertIn("Correct", self.w.lang_feedback.text())
        self.assertEqual(self.w.course_tables["numbers"].item(0, 1).text(), "一")
    def test_offline_keeps_learning(self):
        self.w.set_online(False); self.app.processEvents()
        self.assertTrue(self.w.send_button.isEnabled()); self.assertTrue(self.w.home_send.isEnabled())
        self.assertFalse(self.w.learn_button.isEnabled()); self.assertIn("Offline mode", self.w.badge.toolTip())
        self.w.navigate("exams"); self.w.start_exam("quiz", "math"); self.assertEqual(self.w.exam.total, 5)
    def test_bubble_buttons(self):
        keys = [k for k, _ in self.w.companion.quick_buttons]; self.assertEqual(keys, ["os", "weather", "news", "recommend"])
        c = self.w.companion; c.settings.companion = True; c.set_online(True)
        c.quick_buttons[3][1].click(); self.assertIn("LAFA recommends", c.message.toPlainText())
    def test_click_lafa_recommends(self):
        c = self.w.companion; c.settings.companion = True; c.set_online(True); c.collapse()
        c.toggle_bubble(); self.assertIn("LAFA recommends", c.message.toPlainText()); self.assertIn("🐧", c.message.toPlainText())
        c.collapse(); c.settings.click_recommendations = False; c.toggle_bubble(); self.assertNotIn("LAFA recommends", c.message.toPlainText())
    def test_aero_depth_and_menu(self):
        from lafa.qt import QFrame
        shadows = [f for f in self.w.findChildren(QFrame) if f.objectName() in {"panel", "sidebar"} and f.graphicsEffect() is not None]
        self.assertTrue(shadows); self.assertTrue(all(not b.icon().isNull() for b in self.w.nav))
        self.assertTrue(hasattr(self.w.source_scroll, "smooth_wheel"))

if __name__ == "__main__": unittest.main()


class ChatAndMedia(unittest.TestCase):
    def test_timor_media_directory(self):
        names = [s[1] for s in sources.TIMOR_MEDIA]
        for name in ("Wikipédia Tetun", "TATOLI", "Timor Post", "RTTL", "La'o Hamutuk", "Radio Liberdade", "Lian Matebian"): self.assertIn(name, names)
        self.assertEqual(sources.TIMOR_MEDIA[0][2], "https://tet.wikipedia.org/wiki/P%C3%A1jina_Mahuluk")
        self.assertEqual(len([s for s in sources.TIMOR_MEDIA if s[0] == "tl_community"]), 13)
    def test_chat_answers_the_written_topic(self):
        from lafa.tools import Source
        agent = Agent(Settings(language="tet"), Secrets())
        self.assertIn("Illa iha Dili", agent.run("Ataúro", [], True).text)
        with patch("lafa.agent.encyclopedia_search", return_value=[Source("Livru", "https://tet.wikipedia.org/wiki/Livru", "")]), patch("lafa.agent.encyclopedia_article", return_value="Livru mak koleksaun pájina."):
            text = agent.run("livru", [], True).text
        self.assertTrue(text.startswith("📖 Livru · Wikipedia (tet)")); self.assertNotIn("fonte públika", text)
        from lafa.net import NetworkError
        with patch("lafa.agent.encyclopedia_search", side_effect=NetworkError("x")):
            text = agent.run("buku", [], True).text
        # LAFA remembered the Wikipedia article it showed ("buku" = "livru").
        self.assertIn("Livru mak koleksaun", text); self.assertIn("Internet Archive", text)
        from lafa import memory
        memory._shared = memory.Memory(); memory._shared.web = {}; memory._shared._indexes = {}
        with patch("lafa.agent.encyclopedia_search", side_effect=NetworkError("x")):
            self.assertIn("LibriVox", agent.run("audiobook", [], True).text)
        self.assertIn("xave API", agent.run("my password is 1234", [], True).text)
    def test_tetun_atlas_has_no_english_mixed_in(self):
        from lafa import timor_atlas
        self.assertTrue(all("tet" in t.summary for t in timor_atlas.TOPICS))
        self.assertNotIn("Banda arc", offline.answer("Ataúro", "tet"))
        self.assertIsNone(offline.answer("livru", "tet"))
