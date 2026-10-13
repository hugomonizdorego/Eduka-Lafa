"""Regression checks for explicit public queries and safer desktop integration."""
from lafa.qt import BINDING
import importlib.util
import json
import os
from pathlib import Path
import shlex
import tempfile
import unittest
from unittest.mock import patch
from lafa.agent import Agent
from lafa.config import Settings,Secrets
from lafa.desktop_entry import exec_path
from lafa.i18n import RELEASE
from lafa.instance import ActivationServer

ROOT=Path(__file__).resolve().parents[1]
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);item=importlib.util.module_from_spec(spec);spec.loader.exec_module(item);return item

class V4Core(unittest.TestCase):
    @patch('lafa.agent.encyclopedia_search')
    @patch('lafa.providers.json_request')
    def test_ordinary_chat_is_never_sent_to_public_search(self,api,search):
        agent=Agent(Settings(language='id'),Secrets());agent.client.ready=lambda:False
        for text in ['My address is private','Saya ingin menceritakan masalah keluarga','What is Dili?']:
            result=agent.run(text,[],True);self.assertIn('Cari sumber publik',result.text)
        api.assert_not_called();search.assert_not_called()
    def test_invalid_config_fields_do_not_erase_valid_preferences(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'settings.json';path.write_text(json.dumps({'language':[],'companion':True,'roots':['/tmp/selected'],'card_minutes':float('inf'),'news_minutes':None,'models':{'openai':'saved-model'}}))
            result=Settings.load(path);self.assertTrue(result.companion);self.assertEqual(result.roots,['/tmp/selected']);self.assertEqual(result.models['openai'],'saved-model');self.assertEqual(result.card_minutes,5)
    def test_preference_fifo_is_rejected_without_blocking(self):
        import time
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'settings.json';os.mkfifo(path);started=time.monotonic();settings=Settings.load(path);self.assertFalse(settings.companion);self.assertLess(time.monotonic()-started,1)
    def test_readiness_report_does_not_contain_private_data_or_query_network(self):
        helper=module('v4_diagnostics',ROOT/'scripts/check-system.py')
        with patch.object(helper.importlib.util,'find_spec',return_value=None),patch.object(helper.Settings,'load',return_value=Settings(roots=['/private/person-folder'],models={'openai':'private-model'})),patch.dict(os.environ,{'OPENAI_API_KEY':'private-test-secret'}),patch('lafa.net.request') as request:
            report=helper.checks(False)
        text=json.dumps(report);self.assertNotIn('person-folder',text);self.assertNotIn('private-model',text);self.assertNotIn('private-test-secret',text);request.assert_not_called()
    def test_locale_catalogues_have_the_same_keys(self):
        for code,strings in RELEASE.items():self.assertEqual(set(strings),set(RELEASE['en']),code)
    def test_exec_path_survives_both_desktop_escape_layers(self):
        for path in ['/tmp/path with spaces/lafa','/tmp/a\\b/lafa','/tmp/$money`quote"%name/lafa']:
            encoded=exec_path(path)
            # First decode the desktop value, then the command argument, then %%.
            value=encoded.replace('\\\\','\\');decoded=shlex.split(value)[0].replace('\\$','$').replace('\\`','`').replace('%%','%')
            self.assertEqual(decoded,path)
        for bad in ['/tmp/key=value/lafa','/tmp/new\nline/lafa']:
            with self.assertRaises(ValueError):exec_path(bad)
    def test_ipc_fragmented_frames_and_injection_are_bounded(self):
        class Signal:
            def __init__(self):self.values=[]
            def emit(self,value):self.values.append(value)
        class Socket:
            def __init__(self):self.chunk=b'';self.closed=False;self.aborted=False
            def readAll(self):return self.chunk
            def disconnectFromServer(self):self.closed=True
            def abort(self):self.aborted=True
        class Server:pass
        socket=Socket();server=Server();server.sockets={socket:bytearray()};server.activated=Signal()
        socket.chunk=b'set';ActivationServer.receive(server,socket);self.assertFalse(socket.closed);self.assertEqual(server.activated.values,[])
        socket.chunk=b'tings\n';ActivationServer.receive(server,socket);self.assertEqual(server.activated.values,['settings']);self.assertTrue(socket.closed)
        for raw in [b'desktop\nsettings\n',b'shell rm -rf /\n',b'\xff\n',b'a'*33]:
            socket=Socket();server.sockets={socket:bytearray()};server.activated=Signal();socket.chunk=raw;ActivationServer.receive(server,socket);self.assertEqual(server.activated.values,[]);self.assertTrue(socket.closed or socket.aborted)
    def test_auto_host_detection_rejects_ambiguous_or_early_return(self):
        helper=module('v4_integrator',ROOT/'scripts/integrate-eduka-settings.py')
        source='from PyQt5.QtWidgets import QWidget, QVBoxLayout\nclass Settings(QWidget):\n    def __init__(self):\n        v = QVBoxLayout(self)\n        v.addWidget(existing)\n'
        self.assertEqual(helper.detect_host(source),('Settings','v','PyQt5'));self.assertIn('add_lafa_group',helper.add_hook(source,*helper.detect_host(source)))
        with self.assertRaises(ValueError):helper.add_hook(source+'        if ready:\n            return\n','Settings','v','PyQt5')
        with self.assertRaises(ValueError):helper.detect_host(source+'        other = QVBoxLayout(self)\n')
    def test_tab_indentation_and_nested_return_remain_safe(self):
        helper=module('v4_integrator_tabs',ROOT/'scripts/integrate-eduka-settings.py')
        source='class Settings:\n\tdef __init__(self):\n\t\tv=QVBoxLayout(self)\n\t\tdef callback():\n\t\t\treturn True\n'
        result=helper.add_hook(source,'Settings','v','PyQt5');compile(result,'host','exec');self.assertIn('\t\tself.lafa_group',result)

class V4UI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from lafa.qt import QApplication
        cls.app=QApplication.instance() or QApplication([])
    def setUp(self):
        from lafa.app import Window
        self.window=Window(Settings(language='en'),review=True)
    def tearDown(self):
        self.window.review=True
        if self.window.settings_dialog:self.window.settings_dialog.accept()
        self.window.companion.close();self.window.close();self.window.deleteLater();self.app.processEvents()
    def test_cancel_provider_edits_does_not_modify_live_models(self):
        self.window.settings.models={'openai':'original','gemini':'original-gemini'};before=dict(self.window.settings.models)
        self.window.open_settings();self.window.model.setText('unsaved');self.window.provider.setCurrentIndex(self.window.provider.findData('gemini'));self.window.settings_dialog.reject()
        self.assertEqual(self.window.settings.models,before);self.window.open_settings();self.assertEqual(self.window.model.text(),'original')
    def test_failed_preference_write_preserves_live_configuration(self):
        self.window.open_settings();self.window.companion_check.setChecked(True);self.window.review=False;errors=[]
        with patch.object(Settings,'save',side_effect=OSError('write denied')),patch.object(self.window,'error',side_effect=errors.append):self.window.save_settings()
        self.assertFalse(self.window.settings.companion);self.assertTrue(errors);self.assertFalse(self.window.companion.isVisible())
    def test_offline_save_keeps_request_buttons_and_all_characters_paused(self):
        from lafa.mascot import Character
        self.window.set_online(False);self.window.open_settings();self.window.save_settings()
        self.assertFalse(self.window.send_button.isEnabled());self.assertFalse(self.window.public_search_button.isEnabled())
        self.assertTrue(all(not pet.timer.isActive() for pet in self.window.findChildren(Character)))
    def test_settings_save_keeps_code_output_and_draft_chat(self):
        self.window.code_lesson.setCurrentIndex(2);self.window.code_editor.setPlainText('print("my lesson")');self.window.code_output.setPlainText('my lesson');self.window.input.setText('unsent message');self.window.open_settings();self.window.save_settings()
        self.assertEqual(self.window.code_lesson.currentIndex(),2);self.assertEqual(self.window.code_editor.toPlainText(),'print("my lesson")');self.assertEqual(self.window.code_output.toPlainText(),'my lesson');self.assertEqual(self.window.input.text(),'unsent message')
    def test_disabling_all_cards_does_not_starve_minute_activity_changes(self):
        companion=self.window.companion;companion.settings.companion=True;companion.set_online(True);companion.collapse();now=[0];companion.clock=lambda:now[0];companion.mark_activity();companion.last_card=0
        companion.settings.card_minutes=1;companion.settings.cultural_cards=False;companion.settings.positive_messages=False;companion.settings.fun_messages=False;companion.set_state('idle');now[0]=60
        with patch('lafa.mascot.random.choice',return_value='sleeping'):companion.choose_idle()
        self.assertEqual(companion.state,'sleeping');now[0]=120
        with patch('lafa.mascot.random.choice',return_value='walking'):companion.choose_idle()
        self.assertEqual(companion.state,'walking')
    def test_automatic_popup_respects_pause_draft_and_open_chat(self):
        from lafa.timor import Card
        c=self.window.companion;c.settings.companion=True;c.set_online(True);c.collapse();c.clock=lambda:1000;c.last_activity=0
        c.input.setText('private draft');c.show_card(Card('automatic'),automatic=True);self.assertFalse(c.bubblebox.isVisible())
        c.input.clear();c.paused=True;c.show_card(Card('automatic'),automatic=True);self.assertFalse(c.bubblebox.isVisible())
        c.paused=False;c.show_card(Card('automatic'),automatic=True);self.assertTrue(c.bubblebox.isVisible())
    def test_public_search_button_uses_an_explicit_command(self):
        calls=[];self.window.input.setText('Dili');self.window.send_message=lambda text:calls.append(text);self.window.search_public_chat();self.assertEqual(calls,['/ask Dili'])
    def test_native_activation_pending_state_and_timeout(self):
        from lafa.qt import QWidget,QVBoxLayout
        helper=module('v4_native_pending',ROOT/'integration/eduka_lafa_settings.py');host=QWidget();layout=QVBoxLayout(host);now=[0]
        with patch.object(helper,'enabled',return_value=False),patch(BINDING+'.QtCore.QProcess.startDetached',return_value=(True,123)):
            group=helper.add_lafa_group(layout,BINDING,['/bin/true'],clock=lambda:now[0]);group.lafa_toggle.setChecked(True);self.assertFalse(group.lafa_toggle.isEnabled());self.assertIs(group.lafa_pending['target'],True)
            now[0]=11;group.lafa_refresh();self.assertTrue(group.lafa_toggle.isEnabled());self.assertFalse(group.lafa_toggle.isChecked());self.assertIn('not applied',group.lafa_status.text())
        host.deleteLater();self.app.processEvents()
    def test_native_activation_confirms_state_and_factory_uses_host_binding(self):
        helper=module('v4_native_factory',ROOT/'integration/eduka_lafa_settings.py')
        with patch.object(helper,'enabled',return_value=False),patch(BINDING+'.QtCore.QProcess.startDetached',return_value=(True,123)):
            page=helper.create_lafa_page(command=['/bin/true']);group=page.lafa_group;group.lafa_toggle.setChecked(True)
        with patch.object(helper,'enabled',return_value=True):group.lafa_refresh()
        self.assertTrue(group.lafa_toggle.isEnabled());self.assertEqual(group.lafa_status.text(),'');page.deleteLater();self.app.processEvents()
        with self.assertRaises(ValueError):helper.host_binding('PySide6' if BINDING=='PyQt5' else 'PyQt5')
    def test_native_locale_recovers_from_bad_config_and_simple_tetun_locale(self):
        helper=module('v4_native_locale',ROOT/'integration/eduka_lafa_settings.py')
        with patch.object(helper,'preferences',return_value={'language':[]}),patch.dict(os.environ,{'LC_ALL':'tet.UTF-8'},clear=True):self.assertEqual(helper.language(),'tet')

if __name__=='__main__':unittest.main()
