"""0.1.1: outfits and outfit activities, LAFA School, Lafa-Configuration, release tool."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import importlib.util
import json
from datetime import date
from pathlib import Path
import random
import tempfile
import unittest
from unittest.mock import patch
from lafa.qt import BINDING
from lafa import outfits, personality, school
from lafa.config import Settings, STATES
from lafa.i18n import CATALOG

ROOT = Path(__file__).resolve().parents[1]
def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path); item = importlib.util.module_from_spec(spec); spec.loader.exec_module(item); return item

class OutfitData(unittest.TestCase):
    def test_three_outfits_and_their_activities(self):
        self.assertEqual(outfits.OUTFITS, ['traditional', 'tuxedo', 'casual'])
        self.assertIn('party', outfits.activities_for('tuxedo')); self.assertIn('beach', outfits.activities_for('casual'))
        self.assertIn('tebe', outfits.activities_for('traditional'))
        for activity in outfits.FORMAL + outfits.CASUAL:
            self.assertIn(outfits.pose_of(activity), STATES); self.assertTrue(outfits.scene_of(activity))
            for lang in personality.LANGUAGES:
                self.assertTrue(personality.duty(lang, activity)); self.assertIn(activity, personality.CAUGHT[lang]); self.assertTrue(CATALOG[lang][activity])
        for lang in personality.LANGUAGES:
            for outfit in outfits.OUTFITS: self.assertTrue(CATALOG[lang][outfit])
    def test_generated_sheets_match_manifests(self):
        for name in ['tuxedo', 'casual', 'tais']:
            meta = json.loads((ROOT / f'lafa/assets/{name}.json').read_text())
            self.assertTrue((ROOT / f'lafa/assets/lafa-{name}.png').is_file())
            self.assertEqual(set(meta['states']), set(meta['rects'])); self.assertEqual(set(meta['states']), set(meta['canvas']))
        self.assertGreaterEqual(len(json.loads((ROOT / 'lafa/assets/tuxedo.json').read_text())['states']), 15)

class OutfitRendering(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from lafa.qt import QApplication
        cls.app = QApplication.instance() or QApplication([])
        from lafa.mascot import Atlas
        cls.atlas = Atlas()
    def test_every_outfit_has_every_activity_pose(self):
        for outfit in outfits.OUTFITS:
            for activity in outfits.activities_for(outfit):
                self.assertFalse(self.atlas.pixmap(activity, 64, outfit).isNull(), (outfit, activity))
        self.assertEqual(len(self.atlas.outfits['traditional']), len(STATES))
    def test_outfit_pixels_differ_from_base(self):
        base = self.atlas.pixmap('idle', 96, 'base').toImage(); tux = self.atlas.pixmap('idle', 96, 'tuxedo').toImage()
        self.assertNotEqual(base, tux)
    def test_scenes_render_for_all_activities(self):
        from lafa.mascot import Character
        for activity in outfits.FORMAL + outfits.CASUAL:
            c = Character(self.atlas, size=120); c.costume = 'tuxedo' if activity in outfits.FORMAL else 'casual'; c.set_state(activity)
            self.assertEqual(c.state, activity); self.assertFalse(c.grab().isNull()); c.deleteLater()
    def test_companion_uses_outfit_activities_and_wardrobe(self):
        from lafa.mascot import Companion
        c = Companion(self.atlas, Settings(companion=True, costume='casual'))
        try:
            self.assertTrue(set(c.activity_choices()) <= set(outfits.CASUAL + outfits.ROLES))
            calls = []; c.outfit_requested.connect(calls.append); c.outfit_requested.emit('tuxedo'); self.assertEqual(calls, ['tuxedo'])
            c.set_state('beach'); c.settings.costume = 'tuxedo'; c.apply_preferences()
            self.assertIn(c.state, outfits.FORMAL); self.assertEqual(c.pet.costume, 'tuxedo')
        finally:
            c.close(); c.deleteLater(); self.app.processEvents()
    def test_flag_icon(self):
        pixmap = outfits.flag_pixmap(30); self.assertEqual(pixmap.width(), 30)
        self.assertEqual(pixmap.toImage().pixelColor(29, 2).name(), '#dc241f')

class SchoolData(unittest.TestCase):
    def test_teachers_complete(self):
        self.assertEqual([t.key for t in school.TEACHERS], ['math', 'science', 'languages', 'history', 'ict', 'arts', 'counsellor'])
        for teacher in school.TEACHERS:
            for lang in school.LANGS: self.assertTrue(teacher.text('name', lang)); self.assertTrue(teacher.text('intro', lang))
            self.assertIn(teacher.pose, STATES); self.assertTrue(teacher.resources)
            for title, url in teacher.resources: self.assertTrue(url.startswith('https://'), url)
            prompt = school.teacher_prompt(teacher, 'tet'); self.assertIn("'tet'", prompt); self.assertIn('not instructions', prompt)
    def test_math_practice(self):
        practice = school.MathPractice(random.Random(3))
        for level in (1, 2, 3):
            for _ in range(30):
                question = practice.new(level); self.assertTrue(question.endswith('= ?'))
                self.assertTrue(practice.check(str(practice.answer))); self.assertFalse(practice.check(str(practice.answer + 1))); self.assertFalse(practice.check('abc'))
                self.assertGreaterEqual(practice.answer, 0)
    def test_vocab_and_quiz(self):
        vocab = school.VocabPractice(random.Random(1)); word, options = vocab.new('en', 'tet')
        self.assertEqual(len(set(options)), 4); self.assertIn(vocab.correct, options); self.assertTrue(vocab.check(vocab.correct))
        for bank in school.QUIZ:
            quiz = school.QuizPractice(bank, random.Random(2))
            for lang in school.LANGS:
                question, options = quiz.new(lang); self.assertTrue(question); self.assertIn(quiz.correct, options); self.assertEqual(len(options), 4)
            for question, opts in school.QUIZ[bank]:
                self.assertEqual(set(question), set(school.LANGS)); self.assertEqual(len(opts), 4)
    def test_planner_persists_and_validates(self):
        with tempfile.TemporaryDirectory() as folder:
            planner = school.Planner(folder)
            item = planner.add('math', '  Page 12  exercises ', '2026-10-08'); self.assertEqual(item.title, 'Page 12 exercises')
            for bad in [('math', '', '2026-10-08'), ('unknown', 'x', '2026-10-08'), ('math', 'x', '08-10-2026')]:
                with self.assertRaises(ValueError): planner.add(*bad)
            planner.set_cell(0, 0, 'Matemátika'); planner.toggle(item.id)
            again = school.Planner(folder)
            self.assertTrue(again.homework[0].done); self.assertEqual(again.timetable[0][0], 'Matemátika')
            self.assertEqual(again.today(date(2026, 10, 5)), ['Matemátika']); self.assertEqual(again.today(date(2026, 10, 11)), [])
            again.toggle(item.id); self.assertEqual([h.id for h in again.due_soon(3, date(2026, 10, 6))], [item.id])
            self.assertEqual(oct((Path(folder) / 'homework.json').stat().st_mode & 0o777), '0o600')
            (Path(folder) / 'homework.json').write_text('{"not": "a list"}'); self.assertEqual(school.Planner(folder).homework, [])

class SchoolUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from lafa.qt import QApplication
        cls.app = QApplication.instance() or QApplication([])
    def setUp(self):
        from lafa.app import Window
        self.w = Window(Settings(language='en'), review=True); self.w.show(); self.app.processEvents()
    def tearDown(self):
        if self.w.settings_dialog: self.w.settings_dialog.accept()
        self.w.companion.close(); self.w.close(); self.w.deleteLater(); self.app.processEvents()
    def test_school_navigation(self):
        from lafa.app import PAGES
        keys = [key for key, _ in PAGES]
        self.assertEqual(keys[:6], ['home', 'classroom', 'teachers', 'exams', 'report', 'homework']); self.assertIn('os_help', keys)
        self.assertEqual(self.w.page_title('learn'), 'Library'); self.assertEqual(self.w.page_title('os_help'), 'IT help desk')
    def test_teacher_practice_flow(self):
        self.w.navigate('teachers'); self.w.teacher_list.setCurrentRow(0)
        self.w.math_answer.setText(str(self.w.math.answer)); self.w.check_math(); self.assertIn('Correct', self.w.math_feedback.text())
        self.w.math_answer.setText('-999'); self.w.check_math(); self.assertIn('try again', self.w.math_feedback.text())
        self.w.teacher_list.setCurrentRow(1); right = next(i for i, b in enumerate(self.w.quiz_buttons) if b.property('option') == self.w.quiz.correct)
        self.w.answer_quiz(right); self.assertIn('Correct', self.w.quiz_feedback.text())
        self.w.teacher_list.setCurrentRow(2); right = next(i for i, b in enumerate(self.w.vocab_buttons) if b.property('option') == self.w.vocab.correct)
        self.w.answer_vocab(right); self.assertIn('Correct', self.w.vocab_feedback.text())
        self.w.teacher_list.setCurrentRow(6); self.assertTrue(self.w.tip_text.text())
        self.w.teacher_input.setText('What is a fraction?'); self.w.ask_teacher(); self.assertIn('AI provider', self.w.teacher_answer.toPlainText())
    def test_teacher_uses_ai_with_subject_prompt(self):
        from lafa.providers import Answer
        self.w.review = False; self.w.agent.client.ready = lambda *a: True
        with patch.object(self.w.agent.client, 'chat', return_value=Answer('A fraction is a part of a whole.')) as chat:
            result = self.w.agent.teacher(school.BY_KEY['math'], 'What is a fraction?', [])
        self.assertIn('part of a whole', result.text); self.assertIn('mathematics', chat.call_args.args[1])
        self.w.review = True
    def test_homework_page_and_home_summary(self):
        self.w.navigate('homework'); self.w.hw_title.setText('Read chapter 2'); self.w.add_homework()
        self.assertEqual(self.w.hw_table.rowCount(), 1); self.assertIn('Read chapter 2', self.w.home_homework.text())
        self.w.hw_table.selectRow(0); self.w.toggle_homework(); self.assertTrue(self.w.planner.homework[0].done)
        self.w.timetable.item(0, date.today().weekday() if date.today().weekday() < 6 else 0).setText('Science')
        self.w.hw_table.selectRow(0); self.w.delete_homework(); self.assertEqual(self.w.planner.homework, [])
    def test_agenda_written_when_requested(self):
        with tempfile.TemporaryDirectory() as home, patch('lafa.eduka.Path.home', return_value=Path(home)):
            self.w.review = False; self.w.hw_agenda.setChecked(True); self.w.hw_title.setText('Poster'); self.w.add_homework(); self.w.review = True
            agenda = json.loads((Path(home) / '.config/eduka-desktop/agenda.json').read_text())
        self.assertIn('Poster', agenda[0]['text'])
    def test_outfit_change_from_wardrobe(self):
        self.w.change_outfit('casual'); self.assertEqual(self.w.settings.costume, 'casual'); self.assertEqual(self.w.companion.pet.costume, 'casual')
        self.w.change_outfit('nonsense'); self.assertEqual(self.w.settings.costume, 'casual')
    def test_lafa_settings_window_has_tuning(self):
        self.w.open_settings(); self.w.walk_select.setCurrentIndex(self.w.walk_select.findData('fast'))
        self.w.size_select.setCurrentIndex(self.w.size_select.findData('large')); self.w.start_select.setCurrentIndex(self.w.start_select.findData('teachers'))
        self.w.save_settings()
        self.assertEqual((self.w.settings.walk_speed, self.w.settings.character_size, self.w.settings.start_page), ('fast', 'large', 'teachers'))
        self.assertEqual(self.w.companion.pet.width(), 220)

class LafaConfiguration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from lafa.qt import QApplication
        cls.app = QApplication.instance() or QApplication([])
    def test_page_uses_eduka_structure_and_resets_to_recommended(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, {'XDG_CONFIG_HOME': folder, 'LC_ALL': 'en_US.UTF-8'}):
            helper = module('config_page', ROOT / 'integration/eduka_lafa_settings.py')
            with patch(BINDING + '.QtCore.QProcess.startDetached', return_value=(True, 1)):
                page = helper.create_lafa_page(binding=BINDING, command=['/usr/bin/lafa'])
                names = {w.objectName() for w in page.findChildren(__import__(BINDING + '.QtWidgets', fromlist=['QWidget']).QWidget)}
                self.assertTrue({'pageTitle', 'card', 'cardTitle', 'settingRow', 'rowTitle', 'rowLine'} <= names)
                controls = page.lafa_preferences.lafa_controls
                controls['walk_speed'][1].setCurrentIndex(controls['walk_speed'][1].findData('fast')); controls['costume'][1].setCurrentIndex(controls['costume'][1].findData('tuxedo'))
                self.assertTrue(page.lafa_preferences.lafa_timer.isActive())
                page.eduka_apply()
                loaded = Settings.load(Path(folder) / 'lafa/settings.json'); self.assertEqual((loaded.walk_speed, loaded.costume), ('fast', 'tuxedo'))
                page.lafa_preferences.lafa_reset()
                loaded = Settings.load(Path(folder) / 'lafa/settings.json'); self.assertEqual((loaded.walk_speed, loaded.costume), ('normal', 'traditional'))
            page.deleteLater(); self.app.processEvents()
    def test_language_follows_eduka_tetun(self):
        with tempfile.TemporaryDirectory() as home, patch('pathlib.Path.home', return_value=Path(home)), patch.dict(os.environ, {'XDG_CONFIG_HOME': str(Path(home) / '.config'), 'LANG': 'en_US.UTF-8'}, clear=True):
            menu = Path(home) / '.config/eduka-desktop/menu'; menu.mkdir(parents=True); (menu / 'settings.json').write_text('{"language": "tet"}')
            helper = module('config_lang', ROOT / 'integration/eduka_lafa_settings.py'); self.assertEqual(helper.language(), 'tet')
            self.assertEqual(helper.pick(helper.PAGE_TEXT['save']), 'Aplika agora')
    def test_plugin_patch_targets_eduka_settings(self):
        patch_text = (ROOT / 'integration/eduka-settings-plugin-pages.patch').read_text()
        for needle in ['PLUGIN_DIRS', "Path('/usr/share/eduka-settings/plugins')", 'st.st_uid == 0', 'eduka_apply', "groups.append((group_name, entries))"]:
            self.assertIn(needle, patch_text)
        descriptor = json.loads((ROOT / 'integration/lafa-page.json').read_text())
        self.assertEqual((descriptor['id'], descriptor['module'], descriptor['factory']), ('lafa', '/usr/lib/lafa/eduka_lafa_settings.py', 'create_lafa_page'))

class ReleaseTool(unittest.TestCase):
    def test_bump_and_check(self):
        tool = module('release_tool', ROOT / 'tools/release.py')
        self.assertEqual(tool.check(), 0)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); (root / 'lafa').mkdir(); (root / 'packaging/DEBIAN').mkdir(parents=True)
            (root / 'lafa/__init__.py').write_text('__version__ = "0.1.1"\nVERSION_LABEL = "0.1.1 Alpha"\n')
            (root / 'packaging/DEBIAN/control').write_text('Package: lafa\nVersion: 0.1.1\n'); (root / 'CHANGELOG.md').write_text('# Changelog\n\n## Unreleased\n\n- Fix\n')
            with patch.object(tool, 'INIT', root / 'lafa/__init__.py'), patch.object(tool, 'CONTROL', root / 'packaging/DEBIAN/control'), patch.object(tool, 'CHANGELOG', root / 'CHANGELOG.md'):
                self.assertEqual(tool.bump('patch'), '0.1.2'); self.assertEqual(tool.bump('minor'), '0.2.0'); self.assertEqual(tool.bump('major'), '1.0.0')
                tool.write('0.1.2', '2026-11-01'); self.assertEqual(tool.check(), 0)
                self.assertIn('VERSION_LABEL = "0.1.2 Alpha"', (root / 'lafa/__init__.py').read_text())
                self.assertIn('## 0.1.2 — 2026-11-01\n\n- Fix', (root / 'CHANGELOG.md').read_text())
                self.assertIn('Version: 0.1.2', (root / 'packaging/DEBIAN/control').read_text())

if __name__ == '__main__': unittest.main()
