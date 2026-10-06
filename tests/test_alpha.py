"""0.1 Alpha restart: open-source providers, commands, fallback search and greetings."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from lafa import __version__, VERSION_LABEL
from lafa.agent import Agent, direct_intent
from lafa.calculator import calculate, CalcError
from lafa.config import Settings, Secrets, PROVIDERS, OPEN_SOURCE, DEFAULT_OLLAMA_URL, valid_endpoint
from lafa.i18n import CATALOG
from lafa.net import NetworkError, allowed_url, request, USER_AGENT
from lafa.providers import ProviderClient, merged
from lafa.tools import encyclopedia_search
from lafa.mascot import greeting_key

class VersionTests(unittest.TestCase):
    def test_version_is_consistent_everywhere(self):
        import re
        root = Path(__file__).resolve().parents[1]
        self.assertRegex(__version__, r"^0\.1\.\d+$"); self.assertEqual(VERSION_LABEL, __version__ + " Alpha")
        self.assertIn(__version__, USER_AGENT)
        self.assertIn('{attr = "lafa.__version__"}', (root / "pyproject.toml").read_text())
        self.assertIn(f"Version: {__version__}", (root / "packaging/DEBIAN/control").read_text())
        self.assertIn(f"## {__version__}", (root / "CHANGELOG.md").read_text())

class OpenSourceProviderTests(unittest.TestCase):
    def test_endpoint_validation(self):
        self.assertTrue(valid_endpoint(DEFAULT_OLLAMA_URL, True))
        self.assertTrue(valid_endpoint("http://localhost:11434", True))
        self.assertFalse(valid_endpoint("http://192.168.1.4:11434", True))
        self.assertFalse(valid_endpoint("http://user:pw@127.0.0.1:11434", True))
        self.assertTrue(valid_endpoint("https://models.example.org/v1"))
        self.assertFalse(valid_endpoint("http://models.example.org/v1"))
        self.assertFalse(valid_endpoint("https://models.example.org/v1?token=x"))
        self.assertFalse(valid_endpoint("https://bad port:x/"))
    def test_loopback_http_only_when_requested(self):
        self.assertFalse(allowed_url("http://127.0.0.1:11434/api/chat"))
        self.assertTrue(allowed_url("http://127.0.0.1:11434/api/chat", True))
        self.assertFalse(allowed_url("http://example.org/api/chat", True))
        with self.assertRaises(NetworkError): request("http://127.0.0.1:11434/api/chat")
    def test_settings_load_rejects_unsafe_endpoints(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "settings.json"
            path.write_text(json.dumps({"provider": "ollama", "ollama_url": "http://10.0.0.2:11434", "compatible_url": "http://plain.example/v1", "greet_by_time": "yes"}))
            s = Settings.load(path)
            self.assertEqual(s.provider, "ollama"); self.assertEqual(s.ollama_url, DEFAULT_OLLAMA_URL)
            self.assertEqual(s.compatible_url, ""); self.assertTrue(s.greet_by_time)
            path.write_text(json.dumps({"provider": "compatible", "compatible_url": "https://models.example.org/v1"}))
            self.assertEqual(Settings.load(path).compatible_url, "https://models.example.org/v1")
    def test_open_source_ready_without_key(self):
        s = Settings(provider="ollama", models={"ollama": "llama3.2"})
        self.assertTrue(ProviderClient(s, Secrets()).ready())
        self.assertFalse(ProviderClient(Settings(provider="compatible", models={"compatible": "m"}), Secrets()).ready())
        self.assertTrue(OPEN_SOURCE <= set(PROVIDERS))
    @patch("lafa.providers.json_request")
    def test_ollama_chat_uses_local_endpoint(self, req):
        req.return_value = {"message": {"role": "assistant", "content": " Halo! "}}
        s = Settings(provider="ollama", models={"ollama": "llama3.2"})
        answer = ProviderClient(s, Secrets()).chat([{"role": "user", "content": "a"}, {"role": "user", "content": "b"}], "sys")
        self.assertEqual(answer.text, "Halo!")
        args, kwargs = req.call_args
        self.assertEqual(args[0], DEFAULT_OLLAMA_URL + "/api/chat"); self.assertTrue(kwargs["loopback_http"])
        self.assertEqual(args[2], {}); self.assertFalse(args[1]["stream"])
        self.assertEqual([m["role"] for m in args[1]["messages"]], ["system", "user"])
    @patch("lafa.providers.json_request")
    def test_compatible_chat_uses_https_and_optional_key(self, req):
        req.return_value = {"choices": [{"message": {"content": "ok"}}]}
        s = Settings(provider="compatible", compatible_url="https://models.example.org/v1/", models={"compatible": "qwen"})
        keys = Secrets(); keys.set("compatible", "school-key")
        ProviderClient(s, keys).chat([{"role": "user", "content": "x"}], "sys")
        args, kwargs = req.call_args
        self.assertEqual(args[0], "https://models.example.org/v1/chat/completions"); self.assertFalse(kwargs["loopback_http"])
        self.assertEqual(args[2]["Authorization"], "Bearer school-key")
    @patch("lafa.providers.json_request")
    def test_list_models(self, req):
        req.return_value = {"models": [{"name": "llama3.2"}, {"name": "gemma3"}, {"name": "bad\nname"}]}
        self.assertEqual(ProviderClient(Settings(), Secrets()).list_models("ollama"), ["gemma3", "llama3.2"])
        req.return_value = {"models": [{"name": "models/gemini-x", "supportedGenerationMethods": ["generateContent"]}, {"name": "models/embed", "supportedGenerationMethods": ["embedContent"]}]}
        self.assertEqual(ProviderClient(Settings(), Secrets()).list_models("gemini", "k"), ["gemini-x"])
        with self.assertRaises(NetworkError): ProviderClient(Settings(), Secrets()).list_models("openai")
        req.return_value = {"data": []}
        with self.assertRaises(NetworkError): ProviderClient(Settings(), Secrets()).list_models("deepseek", "k")
    def test_merged_messages_alternate(self):
        out = merged([{"role": "user", "content": "a"}, {"role": "user", "content": "b"}, {"role": "assistant", "content": "c"}])
        self.assertEqual(out, [{"role": "user", "content": "a\n\nb"}, {"role": "assistant", "content": "c"}])

class CommandTests(unittest.TestCase):
    def test_calculator(self):
        self.assertEqual(calculate("(3+4)*2"), 14); self.assertEqual(calculate("2^10"), 1024)
        self.assertEqual(calculate("10 ÷ 4"), 2.5); self.assertEqual(calculate("sqrt(16)+pi-pi"), 4); self.assertEqual(calculate("2,5*2"), 5)
        for bad in ["__import__('os')", "2**999999", "1/0", "x+1", "().__class__", "9"*300, "round(x=1)", "lambda: 1"]:
            with self.assertRaises(CalcError): calculate(bad)
    def test_help_and_calc_commands(self):
        agent = Agent(Settings(language="tet"), Secrets())
        self.assertEqual(direct_intent("/calc 2+2").tool, "calc"); self.assertEqual(direct_intent("/help").tool, "help")
        self.assertIn("/calc", agent.run("/help", [], True).text)
        self.assertIn("= 4", agent.run("/hitung 2+2", [], True).text)
        with self.assertRaises(CalcError): agent.run("/calc import os", [], True)
        self.assertIn("internet", agent.run("/calc 1+1", [], False).text.casefold())
    def test_translations_complete_for_new_keys(self):
        keys = set(CATALOG["en"])
        for lang in ["id", "pt", "tet"]:
            self.assertFalse({k for k in keys if k.startswith(("greet_", "fetch_", "ollama", "compatible", "help_text", "open_source"))} - set(CATALOG[lang]), lang)

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
    def test_save_open_source_provider_and_reject_bad_endpoint(self):
        w = self.window; errors = []
        w.open_settings(); w.provider.setCurrentIndex(w.provider.findData("ollama")); w.model.setText("llama3.2")
        w.ollama_url.setText("http://192.168.0.9:11434")
        with patch.object(w, "error", side_effect=errors.append): w.save_settings()
        self.assertTrue(errors); self.assertEqual(w.settings.provider, "openai")
        w.ollama_url.setText("http://127.0.0.1:11434"); w.greet_check.setChecked(False); w.save_settings()
        self.assertEqual(w.settings.provider, "ollama"); self.assertEqual(w.settings.models["ollama"], "llama3.2")
        self.assertFalse(w.settings.greet_by_time); self.assertTrue(w.agent.client.ready())
    def test_version_label_and_greeting_in_introduction(self):
        from lafa.qt import QLabel
        self.assertTrue(any(l.text() == "LAFA  " + VERSION_LABEL for l in self.window.findChildren(QLabel)))
        self.assertTrue(self.window.companion.introduction(8).startswith("Good morning!"))
        self.window.settings.greet_by_time = False
        self.assertFalse(self.window.companion.introduction(8).startswith("Good morning!"))

if __name__ == "__main__": unittest.main()
