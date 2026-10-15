"""Regression tests for the AI-free, offline-first Lafa (0.2.0).

They prove that local learning, file search, the calculator and reminders
never touch the network, that an internet failure keeps local results, that
an upgrade from 0.1.x keeps every piece of user data, and that the Virtual
Assistant stays calm by default."""
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import patch

from lafa import search
from lafa.config import Settings, ENTERTAINMENT
from lafa.net import NetworkError
from lafa.reminders import Reminders

ROOT = Path(__file__).resolve().parents[1]
# Words that would claim a generative AI, an AI account or an API key in the UI.
AI_CLAIMS = re.compile(r"API key|API-key|chave API|xave API|kunci API|AI provider|penyedia AI|provedor IA|"
                       r"Summari[sz]e with AI|Explain with AI|Ask AI|AI Hub|AI teacher|Guru AI|sign in to AI", re.I)


class NoNetworkForLocalWork(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory(); self.root = Path(self.folder.name)
        (self.root / "tugas matematika.txt").write_text("Pecahan: 1/2 + 1/4 = 3/4")

    def tearDown(self):
        self.folder.cleanup()

    def test_local_search_file_read_calc_and_reminders_never_use_the_network(self):
        from lafa.tools import FileSearch
        import urllib.request
        with patch("lafa.net.request") as net, patch.object(urllib.request, "urlopen") as urlopen, patch("socket.create_connection") as sock:
            for online in (False, True):
                self.assertEqual(search.search("Apa itu fotosintesis?", "id", [str(self.root)]).mode, "answer")
                found = search.search("cari file tugas matematika", "id", [str(self.root)])
                self.assertEqual(found.mode, "files"); self.assertTrue(found.items)
                self.assertEqual(search.search("12 * (3 + 4)", "id", []).calc, 84)
            self.assertIn("3/4", FileSearch([self.root]).read(self.root / "tugas matematika.txt"))
            now = [1000.0]; reminders = Reminders(self.root, clock=lambda: now[0]); reminders.add(1, "Minum air")
            now[0] += 61; self.assertEqual([r.text for r in reminders.due(online=False)], ["Minum air"])
        net.assert_not_called(); urlopen.assert_not_called(); sock.assert_not_called()

    def test_low_relevance_is_shown_as_choices_and_nothing_is_invented(self):
        nothing = search.search("zzqx unknownword", "en", [])
        self.assertEqual((nothing.mode, nothing.items), ("none", []))
        from lafa.i18n import tr
        self.assertIn("found nothing", search.summary(nothing, "en", tr))

    def test_result_labels(self):
        outcome = search.search("fotosintesis", "id", [])
        self.assertTrue({i.label for i in outcome.items} <= {"lesson", "guide", "atlas", "file", "saved", "internet"})
        from lafa.i18n import tr
        self.assertEqual(tr("id", "label_lesson"), "Materi lokal"); self.assertEqual(tr("id", "label_file"), "File lokal")
        self.assertEqual(tr("id", "label_saved"), "Materi tersimpan"); self.assertEqual(tr("id", "label_internet"), "Sumber internet")


class Upgrade(unittest.TestCase):
    def test_upgrade_from_0_1_keeps_user_data_and_backs_up_ai_settings(self):
        with tempfile.TemporaryDirectory() as home, patch.dict(os.environ, {"XDG_CONFIG_HOME": home + "/config", "XDG_DATA_HOME": home + "/data"}):
            config = Path(home) / "config/lafa"; config.mkdir(parents=True)
            old = {"language": "tet", "companion": True, "roots": [home], "costume": "casual", "provider": "gemini",
                   "models": {"gemini": "gemini-2.5-flash"}, "transcription_model": "whisper-1", "ollama_url": "http://127.0.0.1:11434"}
            (config / "settings.json").write_text(json.dumps(old))
            from lafa import school, classroom
            data = school.data_dir(); data.mkdir(parents=True, exist_ok=True)
            homework = [{"id": 1, "title": "Read chapter 2", "subject": "math", "due": "2026-10-20", "done": False}]
            (data / "homework.json").write_text(json.dumps(homework))
            report = [{"kind": "quiz", "subject": "math", "score": 4, "total": 5, "when": "2026-10-01 10:00"}]
            (data / "report.json").write_text(json.dumps(report))
            reminders = {"version": 1, "items": [{"id": 3, "text": "Exam", "due": 4102444800.0, "created": 1.0, "fired": False}]}
            (data / "reminders.json").write_text(json.dumps(reminders))
            with patch.dict(sys.modules, {"keyring": None}):  # the keyring is never touched
                settings = Settings.load(config / "settings.json")
            self.assertEqual((settings.language, settings.companion, settings.roots, settings.costume), ("tet", True, [home], "casual"))
            self.assertFalse(hasattr(settings, "provider"))
            backup = config / "settings.json.0.1-backup"
            self.assertEqual(json.loads(backup.read_text())["provider"], "gemini"); self.assertEqual(backup.stat().st_mode & 0o777, 0o600)
            settings.save(config / "settings.json"); Settings.load(config / "settings.json")
            self.assertEqual(json.loads(backup.read_text())["provider"], "gemini")  # written once, never overwritten
            self.assertEqual([h.title for h in school.Planner(data).homework], ["Read chapter 2"])
            self.assertEqual(json.loads((data / "report.json").read_text()), report)
            self.assertEqual([r.text for r in Reminders(data).pending], ["Exam"])

    def test_no_code_path_imports_a_keyring_or_ai_client(self):
        for path in (ROOT / "lafa").glob("*.py"):
            text = path.read_text(encoding="utf-8")
            for module in ("import keyring", "from keyring", "providers", "aihub", "signin", "openai", "anthropic"):
                self.assertNotRegex(text, rf"^\s*(?:import|from)\s+\S*{module.split()[-1]}\b", f"{path.name}: {module}")


class AppOffline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from lafa.qt import QApplication
        cls.app = QApplication.instance() or QApplication([])

    def window(self, **kw):
        from lafa.app import Window
        with patch.object(Window, "setup_tray"), patch.object(Window, "probe"):
            w = Window(Settings(language="en", **kw), review=False)
        self.addCleanup(lambda: (w.probe_timer.stop(), w.reminder_timer.stop(), w.companion.close(), w.close(), w.deleteLater(), self.app.processEvents()))
        return w

    def wait(self, check, seconds=10):
        import time
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            self.app.processEvents()
            if check(): return True
            time.sleep(0.01)
        return False

    def test_internet_failure_keeps_local_results_and_shows_no_popup(self):
        w = self.window(); w.set_online(True); panel = w.search_panels["home"]
        w.run_search("home", "photosynthesis"); self.assertTrue(self.wait(lambda: panel["outcome"] is not None))
        local = panel["results"].toPlainText(); self.assertIn("Local material", local)
        with patch("lafa.app.encyclopedia_search", side_effect=NetworkError("down")):
            w.internet_search("home"); self.assertTrue(self.wait(lambda: panel["internet"].isEnabled()))
        self.assertEqual(panel["results"].toPlainText(), local); self.assertTrue(panel["note"].text())
        from lafa.qt import QMessageBox
        self.assertFalse([x for x in self.app.topLevelWidgets() if isinstance(x, QMessageBox) and x.isVisible()])

    def test_offline_search_never_offers_to_send_automatically(self):
        w = self.window(); w.set_online(False); panel = w.search_panels["home"]
        with patch("lafa.app.encyclopedia_search") as wiki:
            w.run_search("home", "zzqx unknownword"); self.assertTrue(self.wait(lambda: panel["outcome"] is not None))
            w.internet_search("home")
        wiki.assert_not_called(); self.assertFalse(panel["internet"].isEnabled()); self.assertIn("internet", panel["note"].text().lower())

    def test_reminder_rings_offline_and_persists(self):
        w = self.window(); w.set_online(False); rang = []
        w.reminder_text.setText("Stretch"); w.add_reminder(5)
        saved = json.loads((w.reminders.path).read_text())["items"]; self.assertEqual([i["text"] for i in saved], ["Stretch"])
        w.reminders.clock = lambda: 10 ** 10
        with patch.object(w, "ring", side_effect=lambda text, missed=False: rang.append(text)):
            w.poll_reminders(); w.poll_reminders()
        self.assertEqual(rang, ["Stretch"])

    def test_no_ai_claims_anywhere_in_the_interface(self):
        from lafa.qt import QLabel, QAbstractButton, QLineEdit
        for lang in ("en", "id", "pt", "tet"):
            w = self.window(); w.settings.language = lang; w.build_ui(); w.open_settings()
            texts = [x.text() for x in w.findChildren(QLabel) + w.findChildren(QAbstractButton)] + [x.placeholderText() for x in w.findChildren(QLineEdit)]
            texts += [x.text() for x in w.settings_dialog.findChildren(QLabel) + w.settings_dialog.findChildren(QAbstractButton)]
            bad = [t for t in texts if AI_CLAIMS.search(t)]; self.assertEqual(bad, [], lang)
            w.settings_dialog.accept()


class CalmAssistant(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from lafa.qt import QApplication
        cls.app = QApplication.instance() or QApplication([])

    def companion(self, **kw):
        from lafa.mascot import Atlas, Companion
        c = Companion(Atlas(), Settings(language="en", companion=True, **kw)); c.set_online(False); c.collapse()
        now = [10_000.0]; c.clock = lambda: now[0]; c.last_activity = 0
        self.addCleanup(lambda: (c.close(), c.deleteLater(), self.app.processEvents()))
        return c, now

    def test_defaults_are_calm(self):
        s = Settings()
        self.assertFalse(s.companion); self.assertFalse(s.entertainment); self.assertFalse(s.quiet_mode)
        self.assertLessEqual(s.messages_per_hour, 4); self.assertGreaterEqual(s.card_minutes, 15)

    def test_quiet_mode_and_hourly_limit(self):
        c, now = self.companion(messages_per_hour=2)
        self.assertTrue(c.can_auto_popup()); c.spoke(); c.spoke(); self.assertFalse(c.can_auto_popup())
        now[0] += 3601; self.assertTrue(c.can_auto_popup())
        c.set_quiet(True); self.assertFalse(c.can_auto_popup())

    def test_fullscreen_pauses_messages(self):
        c, _ = self.companion(); c.fullscreen_ahead = True; self.assertFalse(c.can_auto_popup())

    def test_entertainment_and_motion_are_optional(self):
        c, _ = self.companion()
        self.assertFalse(set(c.activity_choices()) & ENTERTAINMENT)
        c.settings.reduce_motion = True; self.assertFalse({"walking", "tebe", "bidu"} & set(c.activity_choices())); self.assertFalse(c.can_roam())
        c.settings.entertainment = True; c.settings.reduce_motion = False
        self.assertTrue(set(c.activity_choices()) & ENTERTAINMENT)

    def test_quick_actions_work_offline(self):
        c, _ = self.companion(); asked = []; c.action_requested.connect(asked.append)
        for key, b in c.quick_buttons: self.assertTrue(b.isEnabled(), key); self.assertTrue(b.text().strip(), key); b.click()
        self.assertEqual(asked, ["continue", "explore", "tasks", "os"])


if __name__ == "__main__":
    unittest.main()
