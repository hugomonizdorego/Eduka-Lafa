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
    def test_offline_keeps_offline_features(self):
        # Offline: local search and LAFA keep working; only internet actions wait, without popups.
        self.window.set_online(False)
        panel=self.window.search_panels['home'];self.assertTrue(panel['input'].isEnabled());self.assertFalse(panel['internet'].isEnabled())
        self.assertFalse(self.window.weather_button.isEnabled());self.assertFalse(self.window.learn_button.isEnabled())
        self.assertTrue(self.window.companion.isVisible());self.assertTrue(self.window.companion.send_button.isEnabled())
        from lafa.qt import QMessageBox
        self.assertFalse([w for w in self.app.topLevelWidgets() if isinstance(w,QMessageBox) and w.isVisible()])
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
            self.window.settings.language=lang;self.window.build_ui();self.window.resize(1024,600);self.app.processEvents()
            self.assertEqual(self.window.stack.count(),len(PAGES))
            hint=self.window.centralWidget().minimumSizeHint();self.assertLessEqual(hint.width(),1024,lang);self.assertLessEqual(hint.height(),600,lang)
            self.assertLessEqual(self.window.sidebar.width(),80)  # compact, icon-only sidebar on small screens
            for button in self.window.nav:self.assertTrue(button.accessibleName() or button.toolTip(),lang)
    def test_keyboard_shortcuts_reach_every_section(self):
        from lafa.qt import QShortcut
        from lafa.qt import QEvent
        self.window.build_ui();self.app.sendPostedEvents(None,QEvent.DeferredDelete)  # rebuilding must not leave duplicate (ambiguous) shortcuts
        found=[s.key().toString() for s in self.window.findChildren(QShortcut)];keys=set(found);self.assertEqual(len(found),len(keys),found)
        self.assertTrue({'Alt+1','Alt+2','Alt+3','Alt+4','Alt+5','Alt+6','Ctrl+F'}<=keys,keys)
    def test_large_text_keeps_layout(self):
        from lafa.qt import QFont
        font=self.app.font();big=QFont(font);big.setPointSizeF(font.pointSizeF()*1.5 if font.pointSizeF()>0 else 15)
        try:
            self.app.setFont(big);self.window.build_ui();self.window.resize(1024,600);self.app.processEvents()
            self.assertEqual(self.window.stack.count(),len(PAGES))
            # 1366×768 at 150 % scaling leaves about 910×512 logical pixels.
            hint=self.window.centralWidget().minimumSizeHint();self.assertLessEqual(hint.width(),910);self.assertLessEqual(hint.height(),512)
        finally:self.app.setFont(font)

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
        from lafa.mascot import POPUP_WIDTH;self.assertEqual(c.width(),POPUP_WIDTH+16);self.assertIn('Hello',c.message.toPlainText())
        calls=[];c.user_request.connect(calls.append);c.input.setText('cari musik Timor');c.submit()
        self.assertEqual(calls,['cari musik Timor']);self.assertFalse(c.input.text())
        c.collapse();self.assertFalse(c.bubblebox.isVisible());QTest.mouseClick(c.pet,Qt.LeftButton);self.app.processEvents();self.assertTrue(c.bubblebox.isVisible())
    def test_ambiguous_city_ui_requires_explicit_selection(self):
        self.window.show_weather(LocationChoices('Springfield',[Location('Springfield',1,2),Location('Springfield',3,4)]))
        self.assertEqual(self.window.stack.currentIndex(),PAGE_INDEX['timor']);self.assertEqual(self.window.city_choices.currentIndex(),-1)
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
    def test_desktop_never_switches_the_virtual_assistant_on(self):
        with patch.object(Window,'setup_tray'),patch.object(Window,'probe'),patch('lafa.eduka.settings_page_available',return_value=False):
            window=Window(Settings(language='id',companion=False),review=False)
            try:
                window.set_online(False);window.activate_mode('desktop');self.app.processEvents()
                self.assertFalse(window.settings.companion);self.assertFalse(window.companion.isVisible())
                # The launcher entry explains where it is switched on instead.
                window.activate_mode('virtual');self.app.processEvents()
                self.assertTrue(window.settings_dialog.isVisible());self.assertFalse(window.settings.companion)
            finally:
                if window.settings_dialog:window.settings_dialog.accept()
                window.probe_timer.stop();window.reminder_timer.stop();window.companion.close();window.companion.deleteLater();window.deleteLater();self.app.processEvents()

if __name__=='__main__':unittest.main()
