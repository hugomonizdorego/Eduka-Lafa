"""Eduka-Desktop suite compatibility: language, panel, theme, agenda, notify."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from lafa import eduka
from lafa.config import Settings

class EdukaHome(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.home = Path(self.temp.name)
        self.patch = patch('lafa.eduka.Path.home', return_value=self.home); self.patch.start()
    def tearDown(self):
        self.patch.stop(); self.temp.cleanup()
    def write(self, part, data):
        path = self.home / '.config/eduka-desktop' / part; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(data)); return path

class LanguageTests(EdukaHome):
    def test_tetun_chosen_in_eduka_settings(self):
        self.write('menu/settings.json', {'language': 'tet'})
        with patch.dict(os.environ, {'LANG': 'en_US.UTF-8'}, clear=True): self.assertEqual(eduka.language(), 'tet')
    def test_system_language_maps_to_lafa_locales(self):
        self.write('menu/settings.json', {'language': 'system'})
        for value, expected in [('pt_BR.UTF-8', 'pt'), ('id_ID.UTF-8', 'id'), ('ms_MY.UTF-8', 'id'), ('zh_CN.UTF-8', 'en'), ('C.UTF-8', 'en')]:
            with patch.dict(os.environ, {'LANG': value}, clear=True): self.assertEqual(eduka.language(), expected, value)
        with patch.dict(os.environ, {'LANG': 'en_US.UTF-8', 'EDUKA_LOGIN_LANGUAGE': 'tet'}, clear=True): self.assertEqual(eduka.language(), 'tet')
    def test_lafa_system_language_follows_eduka_when_installed(self):
        self.write('menu/settings.json', {'language': 'tet'}); self.write('panel/settings.json', {'height': 42})
        with patch.dict(os.environ, {'LANG': 'en_US.UTF-8'}, clear=True): self.assertEqual(Settings(language='system').locale, 'tet')
        self.assertEqual(Settings(language='pt').locale, 'pt')

class PanelThemeTests(EdukaHome):
    def test_panel_defaults_and_bounds(self):
        self.assertIsNone(eduka.panel())
        self.write('panel/settings.json', {'height': 90, 'position': 'top', 'panel_style': 'full', 'width_percent': 10})
        self.assertEqual(eduka.panel(), {'edge': 'top', 'height': 58, 'gap': 0, 'style': 'full', 'width_percent': 45, 'autohide': False})
        self.write('panel/settings.json', {'height': 'x', 'position': 'diagonal', 'panel_style': '??'})
        info = eduka.panel(); self.assertEqual((info['edge'], info['height'], info['gap'], info['style']), ('bottom', 40, 5, 'floating'))
    def test_panel_span(self):
        self.assertEqual(eduka.panel_span(0, 1000, {'style': 'full', 'width_percent': 96}), (0, 1000))
        self.assertEqual(eduka.panel_span(0, 1000, {'style': 'floating', 'width_percent': 80}), (100, 900))
        self.assertEqual(eduka.panel_span(0, 1000, {'style': 'short', 'width_percent': 96}), (180, 820))
    def test_theme_and_accent(self):
        self.assertEqual(eduka.theme()['accent'], '#00a879')
        self.write('desktop/settings.json', {'theme_style': 'Edukasaun-Dark', 'accent_color': '#DC2626'})
        info = eduka.theme(); self.assertTrue(info['dark']); self.assertEqual(info['accent'], '#dc2626')
        self.write('desktop/settings.json', {'theme_style': 'Unknown', 'accent_color': 'red'})
        self.assertEqual(eduka.theme(), {'name': 'Eduka-Default-Theme', 'dark': False, 'accent': '#00a879', 'high_contrast': False})
    def test_lafa_style_follows_eduka_theme(self):
        from lafa.app import style_sheet, STYLE
        self.write('desktop/settings.json', {'theme_style': 'Edukasaun-Dark', 'accent_color': '#2563eb'}); self.write('panel/settings.json', {})
        qss = style_sheet(Settings()); self.assertIn('#2563eb', qss); self.assertIn('#1f2523', qss)
        self.assertEqual(style_sheet(Settings(follow_eduka_theme=False)), STYLE)

class AgendaNotifyTests(EdukaHome):
    def test_agenda_matches_eduka_format(self):
        self.write('agenda.json', [{'id': 'x', 'date': '2026-10-01', 'time': '', 'text': 'keep', 'alarm': 'notify', 'fired': ''}])
        entry = eduka.add_agenda('2026-10-09', '07:30', '  Math homework  ', 'sound')
        items = json.loads(eduka.agenda_path().read_text())
        self.assertEqual(len(items), 2); self.assertEqual(items[1], entry)
        self.assertEqual((entry['text'], entry['alarm'], entry['fired']), ('LAFA · Math homework', 'sound', ''))
        for args in [('9-10-2026', '', 'x'), ('2026-10-09', '7:30', 'x'), ('2026-10-09', '', '   ')]:
            with self.assertRaises(ValueError): eduka.add_agenda(*args)
    def test_notify_uses_fixed_dbus_arguments(self):
        calls = []
        class Done: returncode = 0
        with patch('lafa.eduka.shutil.which', side_effect=lambda name: '/usr/bin/gdbus' if name == 'gdbus' else None):
            self.assertTrue(eduka.notify('LAFA', 'Break time; $(rm -rf ~)', runner=lambda cmd, **kw: calls.append(cmd) or Done()))
        command = calls[0]; self.assertEqual(command[:3], ['gdbus', 'call', '--session']); self.assertIn('Break time; $(rm -rf ~)', command)
        with patch('lafa.eduka.shutil.which', return_value=None): self.assertFalse(eduka.notify('a', 'b'))
    def test_prefer_xwayland_like_eduka(self):
        with patch.dict(os.environ, {'XDG_SESSION_TYPE': 'wayland', 'DISPLAY': ':0'}, clear=True):
            self.assertTrue(eduka.prefer_xwayland()); self.assertEqual(os.environ['QT_QPA_PLATFORM'], 'xcb')
        with patch.dict(os.environ, {'XDG_SESSION_TYPE': 'wayland', 'DISPLAY': ':0', 'LAFA_NATIVE_WAYLAND': '1'}, clear=True):
            self.assertFalse(eduka.prefer_xwayland())

class CompanionOnEdukaPanel(EdukaHome):
    @classmethod
    def setUpClass(cls):
        from lafa.qt import QApplication
        cls.app = QApplication.instance() or QApplication([])
    def test_lafa_stands_on_floating_eduka_panel(self):
        from lafa.mascot import Atlas, Companion
        from lafa.qt import QGuiApplication
        self.write('panel/settings.json', {'height': 48, 'position': 'Bottom', 'panel_style': 'floating', 'width_percent': 80})
        c = Companion(Atlas(), Settings(companion=True))
        try:
            screen = QGuiApplication.primaryScreen().geometry(); rect = c.panel_rect()
            self.assertEqual(c.panel_y(), screen.bottom() + 1 - 5 - 48 - c.height())
            self.assertEqual(rect.left(), screen.left() + int(screen.width() * 0.1)); self.assertLess(rect.width(), screen.width())
            c.settings.follow_eduka_panel = False; self.assertEqual(c.panel_rect().width(), screen.width())
            c.settings.character_size = 'large'; c.settings.animation_speed = 'fast'; c.apply_preferences()
            self.assertEqual(c.pet.width(), 220); self.assertEqual(c.width(), 236); self.assertEqual(c.pet.rate, 1.6)
        finally:
            c.close(); c.deleteLater(); self.app.processEvents()

if __name__ == '__main__': unittest.main()
