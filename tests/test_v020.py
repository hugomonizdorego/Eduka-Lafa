"""0.2.0: local memory, ages 5–100, safe actions, motion, offline features and the six sections."""
import json
import os
import random
import stat
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

from lafa import actions, classroom, curriculum, memory, motion
from lafa.config import Settings

ROOT = Path(__file__).resolve().parents[1]

class Curriculum(unittest.TestCase):
    def test_every_subject_has_every_age(self):
        keys = [s.key for s in curriculum.subjects()]
        for key in ("math", "biology", "physics", "geography", "medicine", "it", "technology", "computers", "communication",
                    "history", "astronomy", "atoms", "chemistry", "economics", "environment", "agriculture", "civics", "arts"):
            self.assertIn(key, keys)
            self.assertEqual([l.level for l in curriculum.lessons(key)], curriculum.LEVEL_KEYS, key)
        for lesson in curriculum.lessons():
            for lang in ("en", "id", "pt", "tet"):
                self.assertTrue(curriculum.text(lesson.title, lang) and all(curriculum.text(p, lang) for p in lesson.points))
            self.assertEqual(len(lesson.questions), 3)
    def test_files_pass_the_checker(self):
        import subprocess, sys
        result = subprocess.run([sys.executable, str(ROOT / "tools/check-curriculum.py")], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout[-2000:])
    def test_ages_and_questions(self):
        self.assertEqual([curriculum.level_for_age(a) for a in (3, 5, 9, 13, 16, 20, 40, 75, 120)],
                         ["early", "early", "primary", "middle", "secondary", "university", "adult", "senior", "senior"])
        exam = classroom.ExamSession("test", "age:atoms:secondary", "tet", random.Random(1))
        # A small question bank is never padded with repeats: fewer questions, and the learner is told.
        self.assertTrue(exam.limited); self.assertEqual(exam.requested, 10); self.assertLess(exam.total, 10)
        self.assertEqual(len({q.text for q in exam.items}), exam.total)
        for q in exam.items: self.assertIn(q.correct, q.options); self.assertEqual(len(set(q.options)), 4)
        self.assertEqual(classroom.ExamSession("quiz", "age::senior", "id").total, 5)
        self.assertIn("Fisika", classroom.subject_name("age:physics:secondary", "id"))
        for bad in ("age:", "age:cooking", "age:math:baby"):
            with self.assertRaises(ValueError): classroom.ExamSession("quiz", bad)

class Memory(unittest.TestCase):
    def setUp(self):
        self.m = memory.Memory()
    def test_search_finds_lessons_atlas_and_sources_in_every_language(self):
        self.assertEqual(self.m.search("quadratic equation", "en")[0].doc.title, "Quadratic equations")
        self.assertEqual(self.m.search("persamaan kuadrat", "id")[0].doc.kind, "lesson")
        self.assertIn("Ataúro", self.m.search("Atauro", "pt")[0].doc.title)       # accents folded
        self.assertIn("TATOLI", [h.doc.title for h in self.m.search("TATOLI", "tet")])
        self.assertTrue(any(h.doc.title == "Internet Archive" for h in self.m.search("livro", "pt")))   # synonyms
    def test_answer_cites_and_stays_relevant(self):
        text, hits = memory.answer("fotosintesis", "id", self.m)
        self.assertIn("[1]", text); self.assertIn("Sumber:", text); self.assertTrue(hits)
        self.assertIsNone(memory.answer("Saya ingin menceritakan masalah keluarga", "id", self.m))
        self.assertIsNone(memory.answer("zzqx unknownword", "en", self.m))
    def test_reads_sites_respecting_robots_and_skipping_facebook(self):
        pages = {
            "https://news.example.tl/robots.txt": ("text/plain", "User-agent: *\nDisallow: /private/"),
            "https://news.example.tl/": ("text/html", '<html lang="tet"><title>Notísia</title><meta name="description" content="Notísia husi Timor-Leste">'
                                       '<link rel="alternate" type="application/rss+xml" href="/feed/"><nav>menu</nav>'
                                       '<p>Eskola foun sira loke iha munisípiu Viqueque ho biblioteka ida ba labarik sira.</p>'
                                       '<a href="/2026/10/eskola/">a</a><a href="/private/x">p</a><a href="https://facebook.com/x">f</a></html>'),
            "https://news.example.tl/2026/10/eskola/": ("text/html", "<html><title>Eskola foun</title><p>" + "Ministériu inaugura eskola foun ho sala-aula sanulu. " * 4 + "</p></html>"),
            "https://news.example.tl/feed/": ("application/rss+xml", '<rss><channel><item><title>Kafé Ermera esporta</title><link>https://news.example.tl/kafe</link><description>Kooperativa esporta kafé.</description></item></channel></rss>'),
        }
        asked = []
        def fetch(url, timeout=12):
            asked.append(url)
            if url not in pages: raise urllib.error.HTTPError(url, 404, "nf", {}, None)
            kind, body = pages[url]; return url, body.encode(), kind
        read, count, failed = memory.refresh(self.m, [("tl_news", "Example", "https://news.example.tl/", {}), ("tl_radio", "FB radio", "https://www.facebook.com/search/pages/?q=x", {})], fetch=fetch)
        self.assertEqual((read, failed), (1, 0)); self.assertGreaterEqual(count, 2)
        # Only the front page and its feed: LAFA never downloads whole sites.
        self.assertNotIn("https://news.example.tl/2026/10/eskola/", asked)
        self.assertNotIn("https://news.example.tl/private/x", asked); self.assertFalse(any("facebook" in u for u in asked))
        self.assertEqual(self.m.search("Ermera esporta", "tet")[0].doc.kind, "news")
        self.assertEqual(stat.S_IMODE(os.stat(self.m.path).st_mode), 0o600)
        again = memory.Memory(self.m.path); self.assertEqual(len(again.web), len(self.m.web))
        # Fresh pages are not read again within the hour.
        asked.clear(); memory.refresh(again, [("tl_news", "Example", "https://news.example.tl/", {})], fetch=fetch); self.assertEqual(asked, [])
    def test_only_https_pages_are_remembered(self):
        self.m.add([memory.Doc("x", "t", "http://insecure.example/", "s", "web", "text")])
        self.assertEqual(self.m.web, {})

class Actions(unittest.TestCase):
    def test_requests_in_four_languages(self):
        cases = {"buka browser": ("app", "browser"), "Lafa, tolong buka kalkulator": ("app", "calculator"), "loke kalkuladora": ("app", "calculator"),
                 "abre o LibreOffice": ("app", "writer"), "buka pengaturan wifi": ("app", "network"), "buka kelas": ("page", "classroom"),
                 "open exams": ("page", "exams"), "loke biblioteka": ("page", "learn"), "buka latihan": ("page", "exams")}
        for text, (kind, target) in cases.items():
            action = actions.parse(text); self.assertEqual((action.kind, action.target), (kind, target), text)
        # Nothing is sent to an AI service: these are not actions any more.
        self.assertIsNone(actions.parse("Tanya Gemini: Apa itu Fotosintesis?"))
        remind = actions.parse("ingatkan saya 10 menit lagi minum air"); self.assertEqual((remind.kind, remind.minutes, remind.text), ("remind", 10, "minum air"))
        self.assertEqual(actions.parse("cari tentang kopi").text, "kopi")
        for text in ("apa itu atom?", "cari file laporan", "rm -rf /", "buka"): self.assertIsNone(actions.parse(text), text)
    def test_only_installed_allowlisted_programs(self):
        app = actions.APP_BY_KEY["calculator"]
        self.assertEqual(actions.which_app(app, lambda name: "/usr/bin/" + name if name == "gnome-calculator" else None), "/usr/bin/gnome-calculator")
        self.assertIsNone(actions.which_app(app, lambda name: None))

class Motion(unittest.TestCase):
    def test_gait_breathing_and_jump(self):
        m = motion.Motion()
        frames = []
        for _ in range(40): m.advance(0.04); frames.append(m.frame("walking"))
        self.assertTrue(all(f.split for f in frames)); self.assertGreater(max(f.step for f in frames), 0.1); self.assertLess(min(f.step for f in frames), -0.1)
        self.assertTrue(all(-7 <= f.dy <= 3 and abs(f.tilt) < 3 for f in frames))
        m.play("jump"); heights = []
        for _ in range(25): m.advance(0.04); heights.append(m.frame("idle").dy)
        self.assertLess(min(heights), -15); self.assertEqual(m.gesture, "")
        self.assertEqual(motion.Motion().frame("idle", animated=False), motion.Frame())

class AppV020(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from lafa.qt import QApplication
        cls.app = QApplication.instance() or QApplication([])
    def setUp(self):
        from lafa.app import Window
        self.w = Window(Settings(language="en"), review=True)
    def tearDown(self):
        self.w.companion.close(); self.w.close(); self.w.deleteLater(); self.app.processEvents()
    def wait(self, check):
        import time
        end = time.monotonic() + 10
        while time.monotonic() < end:
            self.app.processEvents()
            if check(): return True
            time.sleep(0.01)
        return False
    @patch("lafa.net.request")
    def test_local_features_work_offline(self, net):
        self.w.set_online(False); errors = []
        with patch.object(self.w, "error", side_effect=errors.append):
            self.w.navigate("reminders"); self.w.reminder_text.setText("drink water"); self.w.add_reminder(); self.w.start_focus()
            self.w.navigate("coding"); self.w.code_language.setCurrentText("Python"); self.w.run_lesson()
        self.assertEqual(errors, []); self.assertEqual(len(self.w.reminders.items), 2)
        self.assertEqual([r.text for r in self.w.reminders.items if not r.session], ["drink water"])
        net.assert_not_called()
    def test_empty_buttons_give_a_hint(self):
        self.w.navigate("home"); self.w.run_search("home", ""); self.assertEqual(self.w.chat_status.text(), "Type something first.")
        self.w.navigate("live"); self.w.open_news(); self.assertEqual(self.w.chat_status.text(), "Load the news first.")
    def test_actions_from_the_search_box(self):
        from lafa.app import PAGE_INDEX
        self.w.run_search("home", "buka kelas"); self.assertEqual(self.w.current_section(), "study")
        self.w.run_search("home", "remind me in 5 minutes to stretch"); self.assertEqual(self.w.reminders.items[-1].text, "stretch")
        with patch("lafa.actions.shutil.which", return_value=None):
            self.w.run_search("home", "open the calculator"); self.assertIn("not installed", self.w.last_answer)
        self.w.run_search("home", "search for coffee")
        self.assertTrue(self.wait(lambda: self.w.search_panels["home"]["outcome"] is not None))
        self.assertIn("coffee", self.w.search_panels["home"]["results"].toPlainText().lower())
    def test_classroom_for_every_age(self):
        self.w.navigate("classroom"); self.w.age_level.setCurrentIndex(self.w.age_level.findData("senior"))
        self.assertEqual(self.w.lesson_list.count(), len(curriculum.subjects())); self.assertIn("60–100", self.w.lesson_subject.text())
        self.w.quiz_current_lesson(); self.assertTrue(self.w.exam.subject.startswith("age:math:senior"))
    def test_ai_links_only_open_the_browser(self):
        from lafa.config import AI_LINKS
        self.assertEqual([name for name, _ in AI_LINKS], ["ChatGPT", "Claude", "Gemini"]); self.assertTrue(all(url.startswith("https://") for _, url in AI_LINKS))
        opened = []
        with patch.object(self.w, "open_web", side_effect=opened.append):
            self.w.navigate("library", "external")
            from lafa.qt import QPushButton
            buttons = [b for b in self.w.findChildren(QPushButton) if b.property("ai_link")]
            self.assertEqual(len(buttons), 3); buttons[2].click()
        self.assertEqual(opened, [AI_LINKS[2][1]])
    def test_navigation_sections(self):
        from lafa.app import PAGES, ROUTES
        self.assertEqual([k for k, _ in PAGES], ["home", "study", "library", "timor", "activities", "oshelp"])
        for old in ("chat", "classroom", "exams", "teachers", "languages", "learn", "hub", "live", "reminders", "coding", "os_help", "culture"):
            self.w.navigate(old); self.assertEqual(self.w.current_section(), ROUTES[old][0], old)

if __name__ == "__main__": unittest.main()
