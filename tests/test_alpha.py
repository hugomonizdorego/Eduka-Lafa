"""Version, network policy, commands, Wikipedia fallback and greetings."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from lafa import __version__, VERSION_LABEL
from lafa.agent import Agent, direct_intent
from lafa.calculator import calculate, CalcError
from lafa.config import Settings
from lafa.i18n import CATALOG
from lafa.net import NetworkError, allowed_url, request, USER_AGENT
from lafa.tools import encyclopedia_search
from lafa.mascot import greeting_key

class VersionTests(unittest.TestCase):
    def test_version_is_consistent_everywhere(self):
        import re
        root = Path(__file__).resolve().parents[1]
        self.assertRegex(__version__, r"^0\.\d+\.\d+$"); self.assertEqual(VERSION_LABEL, __version__ + " Alpha")
        self.assertIn(__version__, USER_AGENT)
        self.assertIn('{attr = "lafa.__version__"}', (root / "pyproject.toml").read_text())
        self.assertIn(f"Version: {__version__}", (root / "packaging/DEBIAN/control").read_text())
        self.assertIn(f"## {__version__}", (root / "CHANGELOG.md").read_text())

class NetworkPolicyTests(unittest.TestCase):
    def test_only_https_requests(self):
        self.assertFalse(allowed_url("http://127.0.0.1:11434/api/chat"))
        self.assertFalse(allowed_url("http://example.org/x", True))
        with self.assertRaises(NetworkError): request("http://example.org/x")
    def test_settings_ignore_old_ai_fields_and_keep_a_backup(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "settings.json"
            old = {"provider": "ollama", "models": {"ollama": "llama3.2"}, "ollama_url": "http://127.0.0.1:11434", "greet_by_time": "yes", "language": "tet", "start_page": "exams"}
            path.write_text(json.dumps(old))
            s = Settings.load(path)
            self.assertFalse(hasattr(s, "provider")); self.assertTrue(s.greet_by_time); self.assertEqual(s.language, "tet"); self.assertEqual(s.start_page, "study")
            backup = Path(str(path) + ".0.1-backup"); self.assertEqual(json.loads(backup.read_text()), old)
            self.assertEqual(backup.stat().st_mode & 0o777, 0o600)

class CommandTests(unittest.TestCase):
    def test_calculator(self):
        self.assertEqual(calculate("(3+4)*2"), 14); self.assertEqual(calculate("2^10"), 1024)
        self.assertEqual(calculate("10 ÷ 4"), 2.5); self.assertEqual(calculate("sqrt(16)+pi-pi"), 4); self.assertEqual(calculate("2,5*2"), 5)
        for bad in ["__import__('os')", "2**999999", "1/0", "x+1", "().__class__", "9"*300, "round(x=1)", "lambda: 1"]:
            with self.assertRaises(CalcError): calculate(bad)
    def test_help_and_calc_commands(self):
        agent = Agent(Settings(language="tet"))
        self.assertEqual(direct_intent("/calc 2+2").tool, "calc"); self.assertEqual(direct_intent("/help").tool, "help")
        self.assertIn("/calc", agent.run("/help", [], True).text)
        self.assertIn("= 4", agent.run("/hitung 2+2", [], True).text)
        with self.assertRaises(CalcError): agent.run("/calc import os", [], True)
        self.assertIn("= 2", agent.run("/calc 1+1", [], False).text)  # local tools also work offline
    def test_translations_complete_for_new_keys(self):
        keys = set(CATALOG["en"])
        for lang in ["id", "pt", "tet"]:
            self.assertFalse({k for k in keys if k.startswith(("greet_", "help_text", "tab_", "menu_", "label_"))} - set(CATALOG[lang]), lang)

class FallbackAndGreetingTests(unittest.TestCase):
    @patch("lafa.tools.json_request")
    def test_tetun_search_falls_back_to_english(self, req):
        req.side_effect = [{"query": {"search": []}}, {"query": {"search": [{"title": "Dili", "snippet": "City"}]}}]
        sources = encyclopedia_search("Dili", "tet")
        self.assertEqual(sources[0].url, "https://en.wikipedia.org/wiki/Dili")
        self.assertIn("tet.wikipedia.org", req.call_args_list[0].args[0])
    @patch("lafa.tools.json_request")
    def test_english_search_has_no_second_call(self, req):
        req.return_value = {"query": {"search": []}}
        self.assertEqual(encyclopedia_search("zzz", "en"), []); self.assertEqual(req.call_count, 1)
    def test_greeting_by_hour(self):
        self.assertEqual(greeting_key(7), "greet_morning"); self.assertEqual(greeting_key(14), "greet_afternoon")
        self.assertEqual(greeting_key(21), "greet_evening"); self.assertEqual(greeting_key(2), "greet_evening")

class AlphaUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from lafa.qt import QApplication
        cls.app = QApplication.instance() or QApplication([])
    def setUp(self):
        from lafa.app import Window
        self.window = Window(Settings(language="en"), review=True)
    def tearDown(self):
        if self.window.settings_dialog: self.window.settings_dialog.accept()
        self.window.companion.close(); self.window.close(); self.window.deleteLater(); self.app.processEvents()
    def test_save_settings_without_any_ai_field(self):
        w = self.window
        w.open_settings(); w.greet_check.setChecked(False); w.quiet_check.setChecked(True); w.save_settings()
        self.assertFalse(w.settings.greet_by_time); self.assertTrue(w.settings.quiet_mode)
        self.assertFalse(hasattr(w, "provider")); self.assertFalse(hasattr(w.agent, "client"))
    def test_version_label_and_greeting_in_introduction(self):
        from lafa.qt import QLabel
        self.window.open_about()
        self.assertTrue(any(VERSION_LABEL in l.text() for l in self.window.about_dialog.findChildren(QLabel)))
        self.window.about_dialog.close()
        self.assertTrue(self.window.companion.introduction(8).startswith("Good morning!"))
        self.window.settings.greet_by_time = False
        self.assertFalse(self.window.companion.introduction(8).startswith("Good morning!"))

if __name__ == "__main__": unittest.main()
