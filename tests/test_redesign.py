"""0.1 Alpha redesign: personality, Edukasaun OS help, panel walking, hover
questions, Home dashboard and the full Eduka-Settings preferences page."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import dataclasses
import importlib.util
import json
from pathlib import Path
import random
import tempfile
import unittest
from unittest.mock import patch
from lafa import personality, osguide
from lafa.agent import Agent, direct_intent
from lafa.config import Settings, Secrets, STATES, IDLE_ACTIVITIES, PROVIDERS

ROOT = Path(__file__).resolve().parents[1]
def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path); item = importlib.util.module_from_spec(spec); spec.loader.exec_module(item); return item

class PersonalityTests(unittest.TestCase):
    def test_every_language_covers_every_activity(self):
        for lang in personality.LANGUAGES:
            self.assertEqual(set(personality.DUTIES[lang]), set(STATES), lang)
            self.assertEqual(set(personality.CAUGHT[lang]), set(personality.CAUGHT['en']), lang)
            self.assertEqual(set(personality.THOUGHTS[lang]), set(personality.THOUGHTS['en']), lang)
            self.assertGreaterEqual(len(personality.HOVER[lang]), 6); self.assertGreaterEqual(len(personality.JOKES[lang]), 5)
    def test_hover_reacts_to_activity_or_offers_help(self):
        caught = random.Random(); caught.random = lambda: 0.1
        self.assertIn('bath', personality.hover_line('en', 'bathing', caught))
        general = random.Random(1); general.random = lambda: 0.9
        self.assertIn(personality.hover_line('id', 'bathing', general), personality.HOVER['id'])
        self.assertIn(personality.hover_line('xx', 'idle'), personality.HOVER['en'])
    def test_thoughts_and_jokes(self):
        for state in STATES:
            self.assertTrue(personality.thought('tet', state)); self.assertTrue(personality.duty('pt', state))
        self.assertIn(personality.joke('en'), personality.JOKES['en'])

class OSGuideTests(unittest.TestCase):
    def test_guides_complete_and_tools_are_plain_names(self):
        self.assertGreaterEqual(len(osguide.GUIDES), 14)
        for guide in osguide.GUIDES:
            for lang in ['en', 'id', 'pt', 'tet']:
                self.assertTrue(guide.title[lang]); self.assertGreaterEqual(len(guide.steps[lang]), 3, (guide.key, lang))
            for tool in guide.tools: self.assertRegex(tool, r'^[a-z0-9-]+$')
    def test_find_in_four_languages(self):
        cases = {'how do I connect wifi': 'wifi', 'bagaimana cara pasang aplikasi?': 'apps', 'oinsá liga Wi-Fi?': 'wifi',
                 'como imprimir um documento': 'printer', 'tidak bisa suara': 'sound', 'how to take a screenshot': 'screenshot'}
        for text, key in cases.items(): self.assertEqual(osguide.find(text).key, key, text)
        self.assertIsNone(osguide.find('wifi is nice')); self.assertIsNone(osguide.find('hello there'))
        self.assertEqual(osguide.find('wifi', False).key, 'wifi')
    def test_available_tool_uses_allowlist_order(self):
        found = {'nm-connection-editor': None, 'cmst': '/usr/bin/cmst'}
        self.assertEqual(osguide.available_tool(osguide.BY_KEY['wifi'], lambda name: found.get(name)), '/usr/bin/cmst')
        self.assertIsNone(osguide.available_tool(osguide.BY_KEY['wifi'], lambda name: None))
    def test_system_report_reads_only_fixture(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); (root / 'etc').mkdir(); (root / 'etc/os-release').write_text('PRETTY_NAME="Edukasaun OS 1.0"\n')
            (root / 'proc').mkdir(); (root / 'proc/meminfo').write_text('MemTotal: 4000000 kB\nMemAvailable: 200000 kB\n')
            battery = root / 'sys/class/power_supply/BAT0'; battery.mkdir(parents=True); (battery / 'capacity').write_text('15'); (battery / 'status').write_text('Discharging')
            items = {k: (v, s) for k, v, s in osguide.system_report(home=folder, root=root).items}
            self.assertEqual(items['sys_os'][0], 'Edukasaun OS 1.0'); self.assertEqual(items['sys_memory'][1], 'warn'); self.assertEqual(items['sys_battery'], ('15% · Discharging', 'warn'))
    def test_tip_rotates_daily(self):
        self.assertNotEqual(osguide.tip_of_day('en', 0), osguide.tip_of_day('en', 1))

class AgentRedesignTests(unittest.TestCase):
    def setUp(self):
        self.agent = Agent(Settings(language='tet'), Secrets()); self.agent.client.ready = lambda: False
    def test_os_questions_use_offline_guides(self):
        result = self.agent.run('oinsá liga Wi-Fi?', [], True)
        self.assertEqual(result.guide.key, 'wifi'); self.assertIn('Wi-Fi', result.text)
        self.assertEqual(self.agent.run('/os printer', [], True).guide.key, 'printer')
        listing = self.agent.run('/os', [], True); self.assertIsNone(listing.guide); self.assertIn('wifi', listing.text)
    @patch('lafa.providers.json_request')
    def test_os_guide_preferred_over_model(self, api):
        self.agent.client.ready = lambda: True
        self.assertEqual(self.agent.run('how do I connect wifi?', [], True).guide.key, 'wifi'); api.assert_not_called()
    def test_joke_command(self):
        self.assertEqual(direct_intent('/joke').tool, 'joke'); self.assertEqual(direct_intent('Tell me a joke').tool, 'joke')
        self.assertIn(self.agent.run('/anedota', [], True).text, personality.JOKES['tet'])

class SettingsTests(unittest.TestCase):
    def test_new_preferences_load_and_bound(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'settings.json'
            path.write_text(json.dumps({'idle_seconds': 5, 'hover_questions': False, 'chatter': 'no', 'fun_messages': False}))
            s = Settings.load(path); self.assertEqual(s.idle_seconds, 20); self.assertFalse(s.hover_questions); self.assertTrue(s.chatter); self.assertFalse(s.fun_messages)
            path.write_text(json.dumps({'idle_seconds': 90})); self.assertEqual(Settings.load(path).idle_seconds, 90)

class CompanionBehaviour(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls.app = QApplication.instance() or QApplication([])
    def setUp(self):
        from lafa.mascot import Atlas, Companion
        self.c = Companion(Atlas(), Settings(language='en', companion=True)); self.c.set_online(True); self.c.collapse(); self.app.processEvents()
        self.now = [1000]; self.c.clock = lambda: self.now[0]; self.c.mark_activity(); self.c.last_card = 1000
    def tearDown(self):
        self.c.close(); self.c.deleteLater(); self.app.processEvents()
    def test_hover_asks_and_click_on_balloon_opens_chat(self):
        with patch('lafa.personality.hover_line', return_value='Can I help you?'):
            self.c.on_hover(True)
        self.assertTrue(self.c.balloon.isVisible()); self.assertEqual(self.c.balloon.text.text(), 'Can I help you?')
        self.assertEqual(self.c.balloon.caption.text(), personality.duty('en', self.c.state))
        self.c.on_hover(False); self.assertTrue(self.c.balloon_timer.isActive())
        self.c.accept_balloon(); self.assertFalse(self.c.balloon.isVisible()); self.assertTrue(self.c.bubblebox.isVisible())
        self.assertIn('Can I help you?', self.c.message.toPlainText())
    def test_hover_respects_setting_and_pauses_cycle(self):
        self.c.settings.hover_questions = False; self.c.on_hover(True); self.assertFalse(self.c.balloon.isVisible())
        self.now[0] += 500; state = self.c.state; self.c.choose_idle(); self.assertEqual(self.c.state, state)
    def test_walk_then_activity_cycle_on_panel(self):
        with patch('lafa.mascot.QGuiApplication.platformName', return_value='xcb'), patch('lafa.mascot.random.random', return_value=0.99):
            self.now[0] += 60; self.c.choose_idle()
            self.assertEqual(self.c.state, 'walking'); self.assertIsNotNone(self.c.walk_target)
            self.assertEqual(self.c.y(), self.c.panel_y())
            self.c.walk_target = self.c.x() + 2; self.c.walk(); self.c.walk()
            self.assertIsNone(self.c.walk_target); self.assertNotEqual(self.c.state, 'walking'); self.assertNotIn('walking', self.c.activity_choices())
    def test_activity_chatter_shows_thought(self):
        with patch('lafa.mascot.random.random', return_value=0.0), patch.object(self.c, 'activity_choices', return_value=['studying']):
            self.now[0] += 200; self.c.last_activity = 0; self.c.choose_idle()
        self.assertEqual(self.c.state, 'studying'); self.assertTrue(self.c.balloon.isVisible())
        self.assertIn(self.c.balloon.text.text(), personality.THOUGHTS['en']['studying'])
    def test_duration_setting_controls_activity_changes(self):
        self.c.settings.idle_seconds = 120; self.now[0] += 100; state = self.c.state; self.c.choose_idle(); self.assertEqual(self.c.state, state)
        with patch('lafa.mascot.random.choice', return_value='reading'): self.now[0] += 30; self.c.choose_idle()
        self.assertEqual(self.c.state, 'reading')
    def test_joke_and_offline_hides_balloon(self):
        self.c.tell_joke(); self.assertTrue(self.c.balloon.isVisible()); self.assertIn(self.c.balloon.text.text(), personality.JOKES['en'])
        self.c.set_online(False); self.assertFalse(self.c.balloon.isVisible())

class DesktopRedesign(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls.app = QApplication.instance() or QApplication([])
    def setUp(self):
        from lafa.app import Window
        self.w = Window(Settings(language='en'), review=True); self.w.show(); self.app.processEvents()
    def tearDown(self):
        if self.w.settings_dialog: self.w.settings_dialog.accept()
        self.w.companion.close(); self.w.close(); self.w.deleteLater(); self.app.processEvents()
    def test_home_dashboard_and_virtual_toggle(self):
        from lafa.app import PAGES
        self.assertEqual(PAGES[0][0], 'home'); self.assertEqual(self.w.stack.currentIndex(), 0)
        self.assertIn('off', self.w.virtual_status.text()); self.w.toggle_virtual()
        self.assertTrue(self.w.settings.companion); self.assertTrue(self.w.companion.isVisible()); self.assertIn('active', self.w.virtual_status.text())
        self.assertNotIn('lafa_settings', [key for key, _ in PAGES])
    def test_home_question_goes_to_chat(self):
        self.w.home_input.setText('/os wifi'); self.w.ask_from_home(); self.app.processEvents()
        self.assertEqual(self.w.stack.currentIndex(), 1); self.assertEqual(self.w.current_guide.key, 'wifi')
    def test_review_chat_runs_local_tools(self):
        self.w.send_message('/calc 6*7'); self.assertIn('42', self.w.last_answer)
        self.w.send_message('how do I take a screenshot?'); self.assertEqual(self.w.current_guide.key, 'screenshot')
    def test_os_page_and_tool_launch_is_allowlisted(self):
        from lafa.app import PAGE_INDEX
        self.w.show_guide(osguide.BY_KEY['sound']); self.assertEqual(self.w.stack.currentIndex(), PAGE_INDEX['os_help']); self.assertIn('🔊', self.w.os_title.text())
        self.w.review = False
        with patch('lafa.osguide.shutil.which', return_value='/usr/bin/pavucontrol'), patch('lafa.app.QProcess.startDetached', return_value=(True, 1)) as start:
            self.w.open_guide_tool(osguide.BY_KEY['sound'])
        start.assert_called_once_with('/usr/bin/pavucontrol', [])
        self.w.review = True
    def test_settings_window_categories_and_personality_save(self):
        self.w.open_settings(); self.assertEqual(self.w.settings_categories.count(), 5)
        self.w.activity_interval.setValue(150); self.w.hover_check.setChecked(False); self.w.save_settings()
        self.assertEqual(self.w.settings.idle_seconds, 150); self.assertFalse(self.w.settings.hover_questions)
    def test_reload_role_applies_preferences_from_eduka_settings(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, {'XDG_CONFIG_HOME': folder}):
            Settings(language='id', chatter=False, idle_seconds=200, roots=[]).save()
            self.w.input.setText('draft'); self.w.activate_mode('reload'); self.app.processEvents()
        self.assertEqual(self.w.settings.locale, 'id'); self.assertFalse(self.w.settings.chatter); self.assertEqual(self.w.settings.idle_seconds, 200)
        self.assertEqual(self.w.input.text(), 'draft')

class EdukaSettingsPage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls.app = QApplication.instance() or QApplication([])
    def test_schema_matches_lafa_settings(self):
        helper = module('redesign_schema', ROOT / 'integration/eduka_lafa_settings.py')
        fields = {f.name: f for f in dataclasses.fields(Settings)}; defaults = Settings(roots=[])
        for _, title, items in helper.SECTIONS:
            self.assertEqual(len(title), 4)
            for name, kind, extra, labels in items:
                self.assertEqual(len(labels), 4, name)
                if kind == 'model': continue
                self.assertIn(name, fields)
                if name in helper.DEFAULTS: self.assertEqual(helper.DEFAULTS[name], getattr(defaults, name), name)
        provider = next(item for _, _, items in helper.SECTIONS for item in items if item[0] == 'provider')
        self.assertEqual(set(provider[2]), set(PROVIDERS))
    def test_full_page_saves_and_requests_reload(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, {'XDG_CONFIG_HOME': folder, 'LC_ALL': 'en_US.UTF-8'}):
            Settings(models={'openai': 'keep-me'}, roots=[]).save(Path(folder) / 'lafa/settings.json')
            helper = module('redesign_page', ROOT / 'integration/eduka_lafa_settings.py')
            with patch('PySide6.QtCore.QProcess.startDetached', return_value=(True, 1)) as start:
                page = helper.create_lafa_page(binding='PySide6', command=['/opt/lafa'])
                controls = page.lafa_preferences.lafa_controls
                controls['chatter'][1].setChecked(False); controls['idle_seconds'][1].setValue(240)
                controls['provider'][1].setCurrentIndex(controls['provider'][1].findData('ollama')); controls['model'][1].setText('llama3.2')
                controls['roots'][1].setPlainText(folder)
                page.lafa_preferences.lafa_save()
            start.assert_called_with('/opt/lafa', ['--reload'])
            path = Path(folder) / 'lafa/settings.json'; self.assertEqual(oct(path.stat().st_mode & 0o777), '0o600')
            loaded = Settings.load(path)
            self.assertFalse(loaded.chatter); self.assertEqual(loaded.idle_seconds, 240); self.assertEqual(loaded.provider, 'ollama')
            self.assertEqual(loaded.models['ollama'], 'llama3.2'); self.assertEqual(loaded.models['openai'], 'keep-me'); self.assertEqual(loaded.roots, [folder])
            self.assertNotIn('key', json.loads(path.read_text()))
            page.deleteLater(); self.app.processEvents()

if __name__ == '__main__': unittest.main()
