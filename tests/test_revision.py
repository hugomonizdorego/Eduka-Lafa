"""Role separation, bounded code learning, Timor metadata and hardened access."""
from lafa.qt import BINDING
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch
from lafa.config import Settings,Secrets
from lafa.learning import LessonPython,LearningError
from lafa.timor import CardDeck,matches,timor_news
from lafa.tools import FileSearch,Source
from lafa.agent import Agent,direct_intent
from lafa.live_info import NewsReport

class RevisionTests(unittest.TestCase):
    def test_system_locale_and_explicit_choice(self):
        with patch.dict(os.environ,{'LC_ALL':'pt-PT.UTF-8'},clear=True):
            self.assertEqual(Settings().locale,'pt');self.assertEqual(Settings(language='id').locale,'id')
        with patch.dict(os.environ,{'LANGUAGE':'tet:pt','LANG':'C.UTF-8'},clear=True):self.assertEqual(Settings().locale,'tet')
    def test_virtual_off_until_explicitly_enabled(self):
        self.assertFalse(Settings().companion);self.assertEqual(Settings().costume,'traditional')
    def test_bad_config_types_and_limits(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'settings.json';path.write_text(json.dumps({'companion':'true','models':{'openai':[]},'card_minutes':0,'panel_height':999,'language':[]}))
            settings=Settings.load(path);self.assertFalse(settings.companion);self.assertEqual(settings.locale,'en');self.assertEqual(settings.costume,'traditional')
            path.write_text('x'*70000);self.assertFalse(Settings.load(path).companion)
    def test_internal_and_directory_symlinks_blocked(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'notes.txt').write_text('public');(root/'link.txt').symlink_to(root/'notes.txt')
            directory=root/'docs';directory.mkdir();(directory/'read.txt').write_text('document');(root/'shortcut').symlink_to(directory,target_is_directory=True)
            search=FileSearch([root]);self.assertEqual(search.read(root/'notes.txt'),'public')
            for path in [root/'link.txt',root/'shortcut/read.txt']:
                with self.assertRaises(ValueError):search.read(path)
    def test_fifo_rejected_without_blocking(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);path=root/'pipe.txt';os.mkfifo(path)
            started=time.monotonic()
            with self.assertRaises(ValueError):FileSearch([root]).read(path)
            self.assertLess(time.monotonic()-started,1)
    def test_python_conditions_and_loop_output(self):
        result=LessonPython().run('total = 0\nfor n in range(1, 5):\n    total += n\nif total == 10:\n    print("learn", total)')
        self.assertEqual(result.output,'learn 10')
    def test_python_rejects_host_access_and_memory_attacks(self):
        attacks=['import os','open("/etc/passwd")','exec("print(1)")','().__class__','__import__("os")','print("%999999999s" % "a")','print("a" * 1000000000)','print(99999 ** 99999)','while True:\n    pass','a=[1]*200\nfor n in range(8):\n    a=[a]*200']
        for code in attacks:
            with self.subTest(code=code),self.assertRaises(LearningError):LessonPython().run(code)
    def test_temporary_failure_never_creates_news(self):
        with patch('lafa.timor.fetch_one',return_value=([],'offline')):
            with self.assertRaises(Exception):timor_news()
    def test_news_topic_matching_uses_categories_and_word_boundaries(self):
        self.assertTrue(matches(Source('Novo programa','https://tatoli.tl/a','',categories=('Educação',)),'education'))
        self.assertFalse(matches(Source('Party leader','https://tatoli.tl/a',''),'arts_culture'))
        self.assertTrue(matches(Source('Inteligência artificial nas escolas','https://tatoli.tl/a',''),'technology'))
    def test_cards_citations_locale_and_no_consecutive_repeat(self):
        deck=CardDeck();previous=None
        for _ in range(20):
            card=deck.next('id',True,False);self.assertTrue(card.source.startswith('https://'));self.assertIn('Tahukah kamu',card.text)
            self.assertNotEqual(previous,deck.previous);previous=deck.previous
        self.assertIsNone(deck.next('en',False,False))
    @patch('lafa.agent.encyclopedia_article',return_value='Dili is the capital of Timor-Leste.')
    @patch('lafa.agent.encyclopedia_search',return_value=[Source('Dili','https://en.wikipedia.org/wiki/Dili','Capital')])
    def test_key_free_public_extract_is_cited(self,search,article):
        agent=Agent(Settings(language='en'),Secrets());agent.client.ready=lambda:False
        result=agent.run('/ask What is Dili?',[],True);self.assertIn('https://en.wikipedia.org/wiki/Dili',result.text);self.assertIn('capital',result.text)
    @patch('lafa.agent.encyclopedia_search')
    def test_personal_support_is_not_sent_to_public_search(self,search):
        agent=Agent(Settings(language='id'),Secrets());agent.client.ready=lambda:False
        result=agent.run('Saya ingin curhat, saya sedih',[],True);self.assertIn('mendengarkan',result.text);search.assert_not_called()
    def test_timor_command(self):self.assertEqual(direct_intent('/timor education').tool,'timor_news')
    def test_host_settings_patch_preserves_original_and_compiles(self):
        path=Path(__file__).resolve().parents[1]/'scripts/integrate-eduka-settings.py';spec=importlib.util.spec_from_file_location('hook',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        source='class Settings:\n    def __init__(self):\n        v = QVBoxLayout(self)\n        v.addWidget(existing)\n\n    def save(self):\n        pass\n'
        updated=module.add_hook(source,'Settings','v','PyQt5');self.assertIn('v.addWidget(existing)',updated);self.assertIn("add_lafa_group(v, binding='PyQt5')",updated);compile(updated,'host','exec')
        for bad in ['v); import os','unknown']:
            with self.assertRaises(ValueError):module.add_hook(source,'Settings',bad,'PyQt5')

class RevisionUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from lafa.qt import QApplication
        cls.app=QApplication.instance() or QApplication([])
    def test_default_desktop_and_explicit_settings_toggle(self):
        from lafa.app import Window
        window=Window(Settings(language='en'),review=True);window.activate_mode('desktop');self.app.processEvents()
        try:
            self.assertTrue(window.isVisible());self.assertFalse(window.companion.isVisible());window.open_settings();self.app.processEvents()
            self.assertTrue(window.settings_dialog.isVisible());window.companion_check.setChecked(True);window.save_settings();self.app.processEvents()
            self.assertTrue(window.companion.isVisible());self.assertIn('Timor-Leste',window.companion.message.toPlainText());self.assertEqual(window.companion.pet.costume,'traditional')
            window.activate_mode('disable');self.assertFalse(window.companion.isVisible())
        finally:
            if window.settings_dialog:window.settings_dialog.accept()
            window.companion.close();window.close();window.deleteLater();self.app.processEvents()
    def test_settings_group_keeps_host_qt_binding(self):
        from lafa.qt import QWidget,QVBoxLayout
        path=Path(__file__).resolve().parents[1]/'integration/eduka_lafa_settings.py';spec=importlib.util.spec_from_file_location('native_hook',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        host=QWidget();layout=QVBoxLayout(host);group=module.add_lafa_group(layout,BINDING,['/bin/false']);self.assertEqual(group.title(),'LAFA');self.assertEqual(layout.count(),1);host.deleteLater();self.app.processEvents()

if __name__=='__main__':unittest.main()
