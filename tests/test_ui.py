"""Run with QT_QPA_PLATFORM=offscreen. No account or external requests."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import time
import threading
import unittest
from lafa.qt import QApplication
from lafa.app import Window,STYLE,PAGES,PAGE_INDEX
from lafa.config import Settings,STATES
from lafa.mascot import Companion
from lafa.live_info import Location,LocationChoices
from unittest.mock import patch
from lafa.qt import Qt
from lafa.qt import BINDING as _B; import importlib; QTest=importlib.import_module(_B+'.QtTest').QTest
from lafa.tools import FileResults,FileHit

class UITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=QApplication.instance() or QApplication([])
        cls.app.setStyle('Fusion');cls.app.setStyleSheet(STYLE)
    def setUp(self):
        self.window=Window(settings=Settings(language='id',companion=True),review=True);self.window.show();self.app.processEvents();self.window.companion.collapse()
    def tearDown(self):
        if self.window.settings_dialog:self.window.settings_dialog.accept()
        self.window.companion.close();self.window.close();self.window.deleteLater();self.app.processEvents()
    def test_navigation_and_rendering(self):
        self.assertEqual(self.window.stack.count(),len(PAGES))
        for i in range(len(PAGES)):
            self.window.navigate(i);self.app.processEvents()
            self.assertFalse(self.window.grab().isNull())
        for state in STATES:self.assertFalse(self.window.atlas.pixmap(state).isNull())
    def test_offline_pauses_character_and_actions(self):
        self.window.set_online(False)
        self.assertFalse(self.window.send_button.isEnabled());self.assertFalse(self.window.hero_character.timer.isActive())
        self.assertFalse(self.window.companion.isVisible());self.assertFalse(self.window.companion.walk_timer.isActive())
    def test_pause_stops_idle_and_walk_timers(self):
        companion=self.window.companion
        self.assertTrue(companion.idle_timer.isActive())
        companion.toggle_pause(True)
        self.assertFalse(companion.timer.isActive())
        self.assertFalse(companion.idle_timer.isActive())
        self.assertFalse(companion.walk_timer.isActive())
        companion.toggle_pause(False)
        self.assertTrue(companion.timer.isActive())
        self.assertTrue(companion.idle_timer.isActive())
    def test_worker_callback_on_main_thread(self):
        actual=[];main=threading.get_ident()
        self.window.work(lambda:threading.get_ident(),lambda worker:actual.append((worker,threading.get_ident())))
        deadline=time.monotonic()+3
        while not actual and time.monotonic()<deadline:self.app.processEvents();time.sleep(.01)
        self.assertTrue(actual);self.assertNotEqual(actual[0][0],main);self.assertEqual(actual[0][1],main)
    def test_file_table_and_readonly(self):
        self.window.show_files(FileResults([FileHit('/tmp/sample.pdf','sample.pdf','documents',12)],False,1))
        self.assertEqual(self.window.file_table.item(0,0).text(),'sample.pdf')
        self.assertEqual(self.window.file_table.rowCount(),1)
    def test_all_locales_small_screen(self):
        for lang in ['en','id','pt','tet']:
            self.window.settings.language=lang;self.window.build_ui();self.window.resize(880,640);self.app.processEvents()
            self.assertEqual(self.window.stack.count(),len(PAGES))
            self.assertGreater(self.window.send_button.width(),40)
    def test_review_never_calls_provider(self):
        self.window.agent.run=lambda *a:(_ for _ in ()).throw(AssertionError('should not call'))
        self.window.input.setText('Hi');self.window.send_chat()
        self.assertFalse(self.window.busy)
        self.assertEqual(self.window.last_answer,self.window.t('review_chat'))

    def test_idle_at_sixty_seconds_not_restarted_by_network_probe(self):
        c=self.window.companion;now=[0];c.clock=lambda:now[0];c.mark_activity();c.set_state('idle')
        now[0]=30;c.set_online(True)
        now[0]=59;c.choose_idle();self.assertEqual(c.state,'idle')
        now[0]=60
        with patch('lafa.mascot.random.choice',return_value='sleeping'):c.choose_idle()
        self.assertEqual(c.state,'sleeping');now[0]=119;c.choose_idle();self.assertEqual(c.state,'sleeping')
        now[0]=120
        with patch('lafa.mascot.random.choice',return_value='studying') as choose:
            c.choose_idle();self.assertNotIn('sleeping',choose.call_args.args[0])
        self.assertEqual(c.state,'studying')
    def test_busy_activity_and_personal_pose_filter(self):
        c=self.window.companion;now=[0];c.clock=lambda:now[0];c.mark_activity();c.set_state('idle');c.busy=True
        now[0]=90;c.choose_idle();self.assertEqual(c.state,'idle');c.busy=False
        now[0]=149;c.choose_idle();self.assertEqual(c.state,'idle')
        now[0]=150;c.settings.personal_activities=False
        with patch('lafa.mascot.random.choice',return_value='reading') as choose:
            c.choose_idle();self.assertNotIn('toilet',choose.call_args.args[0]);self.assertNotIn('bathing',choose.call_args.args[0])
        c.mark_activity();now[0]=200;c.choose_idle();self.assertEqual(c.state,'reading')
    def test_actual_overlay_submission_and_click(self):
        c=self.window.companion;c.show_bubble('Hello');self.app.processEvents();self.assertTrue(c.bubblebox.isVisible())
        self.assertEqual(c.width(),440);self.assertIn('Hello',c.message.toPlainText())
        calls=[];c.user_request.connect(calls.append);c.input.setText('cari musik Timor');c.submit()
        self.assertEqual(calls,['cari musik Timor']);self.assertFalse(c.input.text())
        c.collapse();self.assertFalse(c.bubblebox.isVisible());QTest.mouseClick(c.pet,Qt.LeftButton);self.app.processEvents();self.assertTrue(c.bubblebox.isVisible())
    def test_ambiguous_city_ui_requires_explicit_selection(self):
        self.window.show_weather(LocationChoices('Springfield',[Location('Springfield',1,2),Location('Springfield',3,4)]))
        self.assertEqual(self.window.stack.currentIndex(),PAGE_INDEX['live']);self.assertEqual(self.window.city_choices.currentIndex(),-1)
        self.assertEqual(self.window.city_choices.count(),2)
    def test_focus_session_does_not_contact_ai(self):
        self.window.agent.run=lambda *a:(_ for _ in ()).throw(AssertionError('must not call'))
        self.window.start_focus();self.assertEqual(len(self.window.reminders.items),1);self.assertEqual(self.window.companion.state,'studying')

    def test_same_user_launcher_activation(self):
        from lafa.instance import ActivationServer,activate_existing
        import uuid,socket
        try:probe=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);probe.close()
        except PermissionError:self.skipTest('This execution environment blocks AF_UNIX socket creation; test on Edukasaun OS.')
        server=ActivationServer('lafa-test-'+uuid.uuid4().hex);calls=[];server.activated.connect(calls.append)
        try:
            self.assertTrue(activate_existing(server.name,'settings'))
            deadline=time.monotonic()+2
            while not calls and time.monotonic()<deadline:self.app.processEvents();time.sleep(.01)
            self.assertEqual(calls,['settings'])
        finally:server.close();server.deleteLater();self.app.processEvents()

    def test_virtual_role_online_opens_bubble(self):
        with patch.object(Window,'setup_tray'),patch.object(Window,'probe'):
            window=Window(Settings(language='id',companion=True),review=False)
            try:
                window.set_online(True);window.activate_mode('virtual');self.app.processEvents()
                self.assertFalse(window.isVisible());self.assertTrue(window.companion.isVisible());self.assertTrue(window.companion.bubblebox.isVisible())
                self.assertIn('LAFA',window.companion.message.toPlainText())
            finally:
                if window.settings_dialog:window.settings_dialog.accept()
                window.probe_timer.stop();window.reminder_timer.stop();window.companion.close();window.companion.deleteLater();window.deleteLater();self.app.processEvents()
    def test_virtual_role_offline_opens_settings(self):
        with patch.object(Window,'setup_tray'),patch.object(Window,'probe'):
            window=Window(Settings(language='id',companion=True),review=False)
            try:
                window.set_online(False);window.activate_mode('virtual');self.app.processEvents()
                self.assertTrue(window.settings_dialog.isVisible());self.assertFalse(window.companion.isVisible());self.assertFalse(window.send_button.isEnabled())
            finally:
                if window.settings_dialog:window.settings_dialog.accept()
                window.probe_timer.stop();window.reminder_timer.stop();window.companion.close();window.companion.deleteLater();window.deleteLater();self.app.processEvents()

if __name__=='__main__':unittest.main()
