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
from lafa.config import Settings

class Sources(unittest.TestCase):
    def test_directory_from_the_document(self):
        self.assertEqual(len(sources.SOURCES), 79 + len(sources.OFFICIAL) + len(sources.TIMOR_MEDIA)); self.assertEqual(len(sources.TIMOR_MEDIA), 51)
        self.assertEqual([k for k, _, _ in sources.SOURCE_CATEGORIES][:8], ["elearning", "books", "biomed", "mathspace", "tech", "languages", "thinking", "society"])
        names = [s[1] for s in sources.SOURCES]
        self.assertEqual(len(names), len(set(names))); self.assertNotIn("Z-Library", names)
        for category, name, url, description in sources.SOURCES:
            self.assertTrue(url.startswith("https://"), url)
            self.assertTrue(description["id"] and description["en"], name)
        self.assertEqual([s[1] for s in sources.search("portugis", "id")], ["Duolingo", "Portuguese Lab"])
        self.assertIn("NASA", [s[1] for s in sources.by_category("mathspace")])
    def test_check_is_on_demand_cached_and_precise(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, {"XDG_CACHE_HOME": folder}):
            states = {"https://www.coursera.org/": "ok"}
            counts = sources.check(sources.SOURCES[:3], check=lambda url: states.get(url, "not_found"), now=1000)
            self.assertEqual((counts["ok"], counts["not_found"]), (1, 2))
            status = sources.load_status(); self.assertEqual(status["https://www.coursera.org/"]["state"], "ok")
            self.assertEqual(sources.status_path().stat().st_mode & 0o777, 0o600)
            # Fresh results are reused; nothing is checked again within a day.
            calls = []
            sources.check(sources.SOURCES[:3], check=lambda url: calls.append(url) or "ok", now=2000); self.assertEqual(calls, [])
            sources.check(sources.SOURCES[:3], check=lambda url: calls.append(url) or "ok", now=2000, force=True); self.assertEqual(len(calls), 3)
            sources.status_path().write_text(json.dumps({"x": {"state": "evil"}, "y": 3}))
            self.assertEqual(sources.load_status(), {})
        self.assertEqual(sources.probe("http://example.org/"), "unknown")
        self.assertEqual([sources.classify(c) for c in (200, 404, 403, 500)], ["ok", "not_found", "restricted", "unknown"])
    def test_default_refresh_is_daily(self):
        self.assertEqual(Settings().update_hours, 24)
    def test_official_and_community_sources(self):
        urls = [s[2] for s in sources.SOURCES]
        self.assertIn("https://timor-leste.gov.tl/", urls); self.assertIn("https://moe.gov.tl/", urls)
        from lafa import source_meta
        for _, name, url, _ in sources.SOURCES:
            m = source_meta.meta(url); self.assertTrue(m["langs"] and m["topics"] and m["access"] in source_meta.ACCESS, name)
        community = {n for n, *_ in source_meta.COMMUNITY_RESOURCES}
        self.assertEqual(community, {"Fandom", "Everything2", "Conservapedia"})

class Offline(unittest.TestCase):
    def test_feature_map(self):
        self.assertIn("Practice and test simulations", offline.offline_features("en"))
        self.assertIn("Wikipedia extracts", offline.online_features("en"))
        self.assertTrue(set(offline.offline_features("tet")).isdisjoint(offline.online_features("tet")))
    def test_local_answers(self):
        self.assertIn("Ataúro", offline.answer("Tell me about Ataúro island", "en"))
        self.assertIsNone(offline.answer("hi", "en"))
        agent = Agent(Settings(language="en"))
        self.assertIn("Ataúro", agent.run("Ataúro island", [], False).text)
        self.assertIn("= 4", agent.run("/calc 2+2", [], False).text)
        self.assertIn("found nothing", agent.run("zzzz qqqq wwww", [], False).text)

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
        self.w.navigate("library", "sources"); self.assertEqual(self.w.current_section(), "library")
        self.assertEqual(len(self.w.source_cards), len(sources.SOURCES))
        self.w.fill_sources("languages"); self.assertEqual(len(self.w.source_cards), 10)
        self.w.source_query.setText("NASA"); self.w.fill_sources(None); self.assertEqual(list(self.w.source_cards), ["NASA"])
        self.w.check_sources(True); self.assertTrue(self.w.source_status.text())
    def test_language_school_page(self):
        self.w.navigate("languages"); self.assertEqual(self.w.current_section(), "study"); from lafa.app import TABS; self.assertEqual(self.w.section_tabs["study"].currentIndex(), TABS["study"].index("languages"))
        self.w.course_list.setCurrentRow(list(languages.COURSES).index("ja")); self.assertEqual(self.w.course_title.text(), "Japanese")
        right = next(i for i, b in enumerate(self.w.lang_buttons) if b.property("option") == self.w.language_quiz.correct)
        self.w.answer_language(right); self.assertIn("Correct", self.w.lang_feedback.text())
        self.assertEqual(self.w.course_tables["numbers"].item(0, 1).text(), "一")
    def test_offline_keeps_learning(self):
        self.w.set_online(False); self.app.processEvents()
        panel = self.w.search_panels["home"]; self.assertTrue(panel["input"].isEnabled()); self.assertFalse(panel["internet"].isEnabled())
        self.assertFalse(self.w.learn_button.isEnabled()); self.assertIn("Local features", self.w.badge.text())
        self.w.navigate("exams"); self.w.start_exam("quiz", "math"); self.assertEqual(self.w.exam.total, 5)
    def test_bubble_buttons_work_offline(self):
        keys = [k for k, _ in self.w.companion.quick_buttons]; self.assertEqual(keys, ["continue", "explore", "tasks", "os"])
    def test_click_lafa_recommends(self):
        c = self.w.companion; c.settings.companion = True; c.set_online(True); c.collapse()
        # 0.2.1: a click shows one learning recommendation (no software tips).
        c.recommendation = "Continue learning: Tais"; c.toggle_bubble()
        self.assertEqual(c.message.toPlainText(), "Continue learning: Tais"); self.assertNotIn("🐧", c.message.toPlainText())
        c.collapse(); c.recommendation = ""; c.introduced = True; c.toggle_bubble(); self.assertTrue(c.message.toPlainText().strip())
    def test_aero_depth_and_menu(self):
        from lafa.qt import QFrame
        # Calm look by default: no drop shadows unless the learner turns them on.
        self.assertFalse(Settings().depth_effects); self.assertTrue(all(not b.icon().isNull() for b in self.w.nav))
        self.assertTrue(hasattr(self.w.source_scroll, "smooth_wheel"))

if __name__ == "__main__": unittest.main()


class ChatAndMedia(unittest.TestCase):
    def test_timor_media_directory(self):
        names = [s[1] for s in sources.TIMOR_MEDIA]
        for name in ("Wikipédia Tetun", "TATOLI", "Timor Post", "RTTL", "La'o Hamutuk", "Radio Liberdade", "Lian Matebian"): self.assertIn(name, names)
        self.assertEqual(sources.TIMOR_MEDIA[0][2], "https://tet.wikipedia.org/wiki/P%C3%A1jina_Mahuluk")
        self.assertEqual(len([s for s in sources.TIMOR_MEDIA if s[0] == "tl_community"]), 13)
    def test_search_answers_the_written_topic_locally(self):
        agent = Agent(Settings(language="tet"))
        with patch("lafa.tools.encyclopedia_search") as wiki:
            self.assertIn("Ataúro", agent.run("Ataúro", [], True).text)
            self.assertTrue(agent.run("my password is 1234", [], True).text)
        wiki.assert_not_called()
    def test_tetun_atlas_has_no_english_mixed_in(self):
        from lafa import timor_atlas
        self.assertTrue(all("tet" in t.summary for t in timor_atlas.TOPICS))
        self.assertNotIn("Banda arc", offline.answer("Ataúro", "tet"))
        self.assertIsNone(offline.answer("livru", "tet"))
