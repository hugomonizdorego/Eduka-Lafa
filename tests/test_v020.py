"""0.2.0: core memory, ages 5–100, AI Hub and sign-in, agent actions, motion, menu fixes."""
import json
import os
import random
import stat
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest.mock import patch

from lafa import actions, aihub, classroom, curriculum, memory, motion, signin
from lafa.config import Settings, Secrets

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
        self.assertEqual(exam.total, 10)
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
        self.assertEqual((read, failed), (1, 0)); self.assertGreaterEqual(count, 3)
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
                 "open exams": ("page", "exams"), "loke biblioteka": ("page", "learn"), "buka hub ai": ("page", "hub")}
        for text, (kind, target) in cases.items():
            action = actions.parse(text); self.assertEqual((action.kind, action.target), (kind, target), text)
        ask = actions.parse("Tanya Gemini: Apa itu Fotosintesis?"); self.assertEqual((ask.kind, ask.target, ask.text), ("ask_ai", "gemini", "Apa itu Fotosintesis"))
        self.assertEqual(actions.parse("husu chatgpt saida mak átomu").text, "saida mak átomu")
        remind = actions.parse("ingatkan saya 10 menit lagi minum air"); self.assertEqual((remind.kind, remind.minutes, remind.text), ("remind", 10, "minum air"))
        self.assertEqual(actions.parse("cari tentang kopi").text, "kopi")
        for text in ("apa itu atom?", "cari file laporan", "rm -rf /", "buka"): self.assertIsNone(actions.parse(text), text)
    def test_only_installed_allowlisted_programs(self):
        app = actions.APP_BY_KEY["calculator"]
        self.assertEqual(actions.which_app(app, lambda name: "/usr/bin/" + name if name == "gnome-calculator" else None), "/usr/bin/gnome-calculator")
        self.assertIsNone(actions.which_app(app, lambda name: None))

class SignIn(unittest.TestCase):
    def test_pkce_and_openrouter_url(self):
        import base64, hashlib
        verifier, challenge = signin.pkce_pair()
        self.assertEqual(challenge, base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode())
        url = signin.openrouter_url(3000, challenge)
        self.assertTrue(url.startswith("https://openrouter.ai/auth?")); self.assertIn("callback_url=http%3A%2F%2Flocalhost%3A3000%2Fcallback", url); self.assertIn("S256", url)
    def test_browser_signin_end_to_end_with_local_callback(self):
        def open_url(url):
            from urllib.parse import urlsplit, parse_qs
            callback = parse_qs(urlsplit(url).query)["callback_url"][0]
            threading.Timer(0.2, lambda: urllib.request.urlopen(callback + "?code=abc123", timeout=5).read()).start()
        def fake_json(url, data=None, headers=None, timeout=45, **kw):
            if url == signin.OPENROUTER_KEYS:
                self.assertEqual(data["code"], "abc123"); self.assertEqual(data["code_challenge_method"], "S256"); return {"key": "sk-or-v1-test"}
            return {"data": [{"id": "some/paid"}, {"id": "mistral/small:free"}, {"id": "meta-llama/llama-3.3-70b-instruct:free"}]}
        with patch("lafa.signin.json_request", side_effect=fake_json):
            key, model = signin.openrouter_signin(open_url, port=0)
        self.assertEqual(key, "sk-or-v1-test"); self.assertEqual(model, "meta-llama/llama-3.3-70b-instruct:free")
    def test_gemini_key_check_picks_flash(self):
        models = {"models": [{"name": "models/gemini-2.5-pro", "supportedGenerationMethods": ["generateContent"]},
                             {"name": "models/gemini-2.5-flash", "supportedGenerationMethods": ["generateContent"]},
                             {"name": "models/gemini-2.5-flash-lite", "supportedGenerationMethods": ["generateContent"]},
                             {"name": "models/embedding-001", "supportedGenerationMethods": ["embedContent"]}]}
        with patch("lafa.signin.json_request", return_value=models): self.assertEqual(signin.gemini_connect(" AIzaTest "), "gemini-2.5-flash")
        from lafa.net import NetworkError
        with self.assertRaises(NetworkError): signin.gemini_connect("two words")
    def test_lafa_model_file(self):
        text = signin.modelfile("gemma3:4b")
        self.assertTrue(text.startswith("FROM gemma3:4b")); self.assertIn("You are LAFA", text); self.assertNotIn("Return ONLY valid JSON", text)
    def test_openrouter_is_a_provider(self):
        from lafa.config import PROVIDERS
        self.assertIn("openrouter", PROVIDERS); self.assertEqual(Settings.load.__func__ is not None, True)

class Hub(unittest.TestCase):
    def test_injection_script_escapes_the_prompt(self):
        script = aihub.inject_script('Apa itu "atom"?</script>', aihub.BY_KEY["chatgpt"])
        self.assertIn(json.dumps('Apa itu "atom"?</script>'), script); self.assertIn("#prompt-textarea", script)
    def test_tabs_stay_on_their_service(self):
        gemini = aihub.BY_KEY["gemini"]
        self.assertTrue(aihub.allowed_host(gemini, "gemini.google.com")); self.assertTrue(aihub.allowed_host(gemini, "accounts.google.com"))
        self.assertFalse(aihub.allowed_host(gemini, "evil.example.com"))
        self.assertIn("Chrome/", aihub.chrome_agent("Mozilla/5.0 QtWebEngine/5.15.2 Chrome/87.0.4280.144 Safari/537.36"))
        self.assertNotIn("QtWebEngine", aihub.chrome_agent("Mozilla/5.0 QtWebEngine/5.15.2 Chrome/87.0.4280.144 Safari/537.36"))

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
    def test_local_features_work_offline(self):
        self.w.set_online(False); errors = []
        with patch.object(self.w, "error", side_effect=errors.append):
            self.w.navigate("reminders"); self.w.reminder_text.setText("drink water"); self.w.add_reminder(); self.w.start_focus()
            self.w.navigate("coding"); self.w.code_language.setCurrentText("Python"); self.w.run_lesson()
        self.assertEqual(errors, []); self.assertEqual(len(self.w.reminders.items), 2)
    def test_empty_buttons_give_a_hint(self):
        self.w.navigate("chat"); self.w.input.clear(); self.w.send_chat(); self.assertEqual(self.w.chat_status.text(), "Type something first.")
        self.w.navigate("live"); self.w.open_news(); self.assertEqual(self.w.chat_status.text(), "Load the news first.")
    def test_agent_actions_from_chat(self):
        self.w.send_message("buka kelas"); self.assertEqual(self.w.stack.currentIndex(), self.w.stack.indexOf(self.w.stack.widget(1)))
        from lafa.app import PAGE_INDEX
        self.assertEqual(self.w.stack.currentIndex(), PAGE_INDEX["classroom"])
        self.w.send_message("remind me in 5 minutes to stretch"); self.assertEqual(self.w.reminders.items[-1].text, "stretch")
        with patch("lafa.actions.shutil.which", return_value=None):
            self.w.send_message("open the calculator"); self.assertIn("not installed", self.w.last_answer)
        self.w.send_message("search for coffee"); self.assertEqual(self.w.stack.currentIndex(), PAGE_INDEX["learn"]); self.assertIn("Coffee", self.w.memory_results.toPlainText())
    def test_classroom_for_every_age(self):
        self.w.navigate("classroom"); self.w.age_level.setCurrentIndex(self.w.age_level.findData("senior"))
        self.assertEqual(self.w.lesson_list.count(), len(curriculum.subjects())); self.assertIn("60–100", self.w.lesson_subject.text())
        self.w.quiz_current_lesson(); self.assertTrue(self.w.exam.subject.startswith("age:math:senior"))
        self.w.navigate("learn"); self.w.search_memory("solar system")
        self.assertIn("solar system", self.w.memory_results.toPlainText().lower())
    def test_ai_hub_without_web_engine_opens_the_browser(self):
        self.w.navigate("hub"); opened = []
        with patch("lafa.aihub.QDesktopServices.openUrl", side_effect=lambda url: opened.append(url.toString()) or True), patch.object(aihub.qt, "WEBENGINE", False):
            self.w.ai_hub.open_site("gemini"); keys = self.w.ai_hub.ask("What is an atom?", ["chatgpt"])
        self.assertEqual(keys, ["chatgpt"]); self.assertEqual(opened, ["https://gemini.google.com/app", "https://chatgpt.com/"])
        self.w.ai_hub.prompt.clear(); self.w.ai_hub.ask_selected(); self.assertEqual(self.w.ai_hub.status.text(), "Type something first.")
    def test_navigation_groups(self):
        from lafa.app import PAGES, SECTIONS
        keys = [k for k, _ in PAGES]
        self.assertLess(keys.index("languages"), keys.index("culture")); self.assertLess(keys.index("live"), keys.index("learn"))
        self.assertEqual(keys[keys.index("learn"):keys.index("learn") + 3], ["learn", "hub", "chat"]); self.assertEqual(set(SECTIONS.values()), {"sec_school", "sec_timor", "sec_ai", "sec_tools"})

if __name__ == "__main__": unittest.main()
