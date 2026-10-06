"""Reproducible Qt captures of LAFA for developer review.

Review fixtures never call the internet or an AI provider and never write the
user's preferences or homework. Run after every UI change:
    QT_QPA_PLATFORM=offscreen python3 scripts/capture-screenshots.py
Set EDUKA_DESKTOP_SRC=/path/to/Eduka-Desktop to also capture the real
Eduka-Settings with Lafa-Configuration (tools/eduka-settings-preview.py).
Output: docs/screenshots/*.png (listed in docs/SCREENSHOTS.md).
"""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lafa.qt import Qt, QRectF, QPoint, QPainter, QLinearGradient, QColor, QFont, QApplication, QWidget, prepare_application, BINDING
prepare_application()
from lafa.app import Window, STYLE, style_sheet
from lafa.config import Settings, STATES
from lafa.mascot import Character, greeting_key
from lafa.tools import FileSearch, Source
from lafa.live_info import Location, WeatherReport, ForecastDay, NewsReport
from lafa.learning import LessonPython
from lafa.i18n import tr
from lafa import personality, osguide, outfits

out = ROOT / 'docs/screenshots'; out.mkdir(parents=True, exist_ok=True)
for old in out.glob('*.png'): old.unlink()
app = QApplication([]); app.setStyle('Fusion'); app.setStyleSheet(STYLE)
saved = []
def pump():
    for _ in range(4): app.processEvents()
def save(widget, name): pump(); widget.grab().save(str(out / name)); saved.append(name)
def morning(window): window.home_greeting.setText(tr(window.settings.locale, greeting_key(9)))
def sample_school(window):
    planner = window.planner
    for subject, title, due in [('math', 'Exercises on fractions, page 42', '2026-10-08'), ('languages', 'Write 5 sentences in Tetun', '2026-10-09'), ('science', 'Poster: the water cycle', '2026-10-12')]:
        planner.add(subject, title, due)
    for day, lessons in enumerate([['Mathematics', 'Tetun', 'Science', 'Sport'], ['Portuguese', 'Mathematics', 'History', 'ICT'], ['Science', 'English', 'Arts', 'Mathematics'],
                                   ['Tetun', 'Geography', 'Mathematics', 'Music'], ['ICT', 'Science', 'Portuguese', 'Counselling'], ['Arts', 'Sport']]):
        for period, lesson in enumerate(lessons): planner.set_cell(day, period, lesson)
    window.build_ui(); window.set_online(True); window.refresh_home()

temp = tempfile.TemporaryDirectory(prefix='lafa-capture-'); os.environ['XDG_CONFIG_HOME'] = temp.name; os.environ['XDG_CACHE_HOME'] = temp.name
settings = Settings(language='en', roots=[])
w = Window(settings=settings, review=True); w.resize(1180, 820); w.show(); pump(); w.hero_character.animate(False)
sample_school(w); morning(w); save(w, '01-home.png')
w.navigate('teachers'); w.teacher_list.setCurrentRow(0); save(w, '02-teachers-mathematics.png')
w.teacher_list.setCurrentRow(2); save(w, '03-teachers-languages.png')
w.teacher_list.setCurrentRow(3); save(w, '04-teachers-history-quiz.png')
w.navigate('homework'); save(w, '05-homework.png')
w.findChildren(__import__(BINDING + '.QtWidgets', fromlist=['QTabWidget']).QTabWidget)[0].setCurrentIndex(1); save(w, '06-timetable.png')
w.navigate('chat'); w.send_message('How do I connect Wi-Fi?'); w.send_message('/calc 12*7'); save(w, '07-conversation.png')
w.navigate('os_help'); w.show_guide(osguide.BY_KEY['apps']); save(w, '08-it-help-desk.png')
w.show_sources([Source('Photosynthesis', 'https://en.wikipedia.org/wiki/Photosynthesis', 'REVIEW SAMPLE · process used by plants to convert light energy'), Source('Dili', 'https://en.wikipedia.org/wiki/Dili', 'REVIEW SAMPLE · capital of Timor-Leste')])
w.navigate('learn'); save(w, '09-library.png')
w.navigate('coding'); w.code_lesson.setCurrentIndex(2); result = LessonPython().run(w.code_editor.toPlainText()); w.code_output.setPlainText(result.output + f'\n\n{result.steps} lesson steps'); save(w, '10-computer-lab.png')
weather = WeatherReport(Location('Dili', -8.5586, 125.5736, 'Asia/Dili', 'Timor-Leste'), 'SAMPLE 10:00', 'REVIEW SAMPLE · not live data', 'Asia/Dili', 29, 32, 65, 12, 2, [ForecastDay('SAMPLE day 1', 24, 31, 20, 2), ForecastDay('SAMPLE day 2', 24, 30, 40, 80), ForecastDay('SAMPLE day 3', 23, 30, 35, 2)])
w.show_weather(weather); w.show_news(NewsReport([Source('Sample headline to review the news layout', 'https://www.bbc.com/news/world', '', 'BBC World · SAMPLE', 'REVIEW SAMPLE'), Source('Open a headline on the publisher website', 'https://www.theguardian.com/world', '', 'The Guardian · SAMPLE', 'REVIEW SAMPLE')], 'REVIEW SAMPLE · not current news'))
w.navigate('live'); save(w, '11-notice-board.png')
w.show_timor_news(NewsReport([Source('SAMPLE · Learning and education in Timor-Leste', 'https://tatoli.tl/', '', 'Tatoli · SAMPLE', 'REVIEW SAMPLE'), Source('SAMPLE · Arts, culture and community life', 'https://timorpost.com/', '', 'Timor Post · SAMPLE', 'REVIEW SAMPLE')], 'REVIEW SAMPLE · not live headlines'))
w.navigate('culture'); save(w, '12-timor-leste.png')
with tempfile.TemporaryDirectory(prefix='lafa-review-') as files:
    root = Path(files) / 'Documents'; root.mkdir()
    for name in ['Lesson_Photosynthesis.txt', 'Lesson_Mathematics.txt', 'Timor_Leste_Notes.md', 'Lesson_Schedule.csv']: (root / name).write_text('REVIEW SAMPLE', encoding='utf-8')
    w.settings.roots = [str(root)]; w.show_files(FileSearch(w.settings.roots).search('', 'documents')); w.navigate('files'); pump(); w.file_table.selectRow(0); save(w, '13-my-files.png')
w.navigate('hub'); save(w, '14-ai-services.png')
w.set_online(False); w.navigate('home'); morning(w); save(w, '15-offline.png'); w.set_online(True)
w.open_settings(); pump()
for row, name in [(0, '16-lafa-settings-virtual-assistant.png'), (3, '17-lafa-settings-desktop.png')]:
    w.settings_categories.setCurrentRow(row); save(w.settings_dialog, name)
w.settings_dialog.accept()

# Eduka-Settings → Lafa-Configuration (real Eduka-Settings when a checkout is given).
eduka_src = os.environ.get('EDUKA_DESKTOP_SRC')
if eduka_src and Path(eduka_src, 'usr/bin/eduka-settings').is_file():
    for name, scroll in [('18-eduka-settings-lafa-configuration.png', 0.0), ('19-eduka-settings-lafa-configuration-2.png', 0.55)]:
        subprocess.run([sys.executable, str(ROOT / 'tools/eduka-settings-preview.py'), eduka_src, str(out / name), '--scroll', str(scroll)],
                       env={**os.environ, 'LAFA_QT': 'pyqt5'}, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); saved.append(name)
else:
    sys.path.insert(0, str(ROOT / 'integration'))
    from demo_eduka_settings import build_host
    with tempfile.TemporaryDirectory(prefix='lafa-host-capture-') as folder, patch.dict(os.environ, {'XDG_CONFIG_HOME': folder}):
        host = build_host(review=True); host.setStyleSheet(STYLE); host.resize(1000, 900); host.show(); save(host, '18-eduka-settings-lafa-configuration.png'); host.close()

class DesktopReview(QWidget):
    """Actual LAFA widget pixels composited on an explicitly illustrative desktop."""
    def __init__(self, title, subtitle, layers): super().__init__(); self.title = title; self.subtitle = subtitle; self.layers = layers; self.resize(1280, 800)
    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        gradient = QLinearGradient(0, 0, 1280, 800); gradient.setColorAt(0, QColor('#0b4339')); gradient.setColorAt(1, QColor('#218163')); p.fillRect(self.rect(), gradient)
        p.setPen(QColor('#e9f7ef')); p.setFont(QFont('DejaVu Sans', 26, QFont.Bold)); p.drawText(50, 80, self.title)
        p.setFont(QFont('DejaVu Sans', 11)); p.drawText(51, 112, self.subtitle)
        p.setFont(QFont('DejaVu Sans', 9)); p.setPen(QColor('#bfe0cf')); p.drawText(51, 136, 'REVIEW · actual LAFA widgets on an illustrated desktop · target OS integration still requires testing')
        p.setPen(Qt.NoPen); p.setBrush(QColor(255, 255, 255, 238)); p.drawRoundedRect(QRectF(64, 753, 1152, 42), 21, 21)   # floating Eduka-Panel
        p.setBrush(QColor('#00a879')); p.drawRoundedRect(QRectF(72, 759, 130, 30), 15, 15)
        p.setPen(QColor('#ffffff')); p.setFont(QFont('DejaVu Sans', 10, QFont.Bold)); p.drawText(QRectF(72, 759, 130, 30), Qt.AlignCenter, 'Edukasaun')
        p.setPen(QColor('#1f2d2a')); p.setFont(QFont('DejaVu Sans', 10)); p.drawText(230, 780, 'LAFA Desktop      Files      Browser'); p.drawText(1110, 780, '09:00')
        for pixmap, point in self.layers: p.drawPixmap(point, pixmap)
reviews = []
def compose(name, title, subtitle, layers):
    review = DesktopReview(title, subtitle, layers); reviews.append(review); review.show(); save(review, name)
PANEL_TOP = 753 - 5
w.activate_mode('enable'); c = w.companion; c.animate(False); c.collapse(); pump()
def pet(state, outfit='traditional'):
    c.settings.costume = outfit; c.apply_preferences(); c.set_state(state); pump(); return c.grab()
def balloon_for(state, text):
    with patch('lafa.personality.hover_line', return_value=text): c.on_hover(True)
    image = c.balloon.grab(); c.hide_balloon(); c.hovered = False; return image
walker = pet('walking')
compose('20-virtual-walking-on-panel.png', 'LAFA walks on the Eduka-Panel', 'When idle, LAFA walks along the real panel, then studies, reads, plays or dances.', [(walker, QPoint(640, PANEL_TOP - walker.height() + 12))])
studying = pet('studying'); bubble = balloon_for('studying', personality.CAUGHT['en']['studying'])
compose('21-virtual-hover-question.png', 'Touch LAFA with the cursor…', '…and LAFA stops, asks how it can help, and says what it was doing.', [(studying, QPoint(900, PANEL_TOP - studying.height() + 12)), (bubble, QPoint(900 + studying.width() - bubble.width() + 40, PANEL_TOP - studying.height() - bubble.height() + 40))])
party = pet('party', 'tuxedo'); bubble = balloon_for('party', personality.CAUGHT['en']['party'])
compose('22-virtual-tuxedo-party.png', 'Tuxedo: formal activities', 'Parties, meetings, presentations, ceremonies and gala dinners.', [(party, QPoint(860, PANEL_TOP - party.height() + 12)), (bubble, QPoint(860 + party.width() - bubble.width() + 40, PANEL_TOP - party.height() - bubble.height() + 40))])
beach = pet('beach', 'casual'); bubble = balloon_for('beach', personality.CAUGHT['en']['beach'])
compose('23-virtual-casual-beach.png', 'Casual: summer activities', 'Beach, sightseeing, hanging out at a café and shopping.', [(beach, QPoint(500, PANEL_TOP - beach.height() + 12)), (bubble, QPoint(500 + beach.width() - bubble.width() + 40, PANEL_TOP - beach.height() - bubble.height() + 40))])
pet('idle'); c.introduced = False; c.show_bubble(c.introduction(9)); pump(); chat = c.grab()
compose('24-virtual-chat-bubble.png', 'Click LAFA to chat', 'Quick help for Edukasaun OS, weather, Timor-Leste news, focus and jokes.', [(chat, QPoint(800, PANEL_TOP - chat.height() + 12))])
c.collapse()

class Sheet(QWidget):
    """Grid of LAFA poses with captions."""
    def __init__(self, title, subtitle, items, columns=4, size=200):
        super().__init__(); self.title, self.subtitle, self.items, self.columns, self.cell = title, subtitle, items, columns, size + 60
        rows = (len(items) + columns - 1) // columns; self.resize(columns * (size + 50) + 40, 100 + rows * (size + 76)); self.setStyleSheet('background:#f3f6f2;')
        for i, (state, outfit, _, _) in enumerate(items):
            pet_ = Character(w.atlas, self, size); pet_.costume = outfit; pet_.set_state(state); pet_.animate(False); pet_.phase = 0.8
            pet_.move(20 + (i % columns) * (size + 50) + 25, 84 + (i // columns) * (size + 76))
        self.size_ = size
    def paintEvent(self, event):
        p = QPainter(self); p.setPen(QColor('#0f5a46')); p.setFont(QFont('DejaVu Sans', 16, QFont.Bold)); p.drawText(28, 40, self.title)
        p.setFont(QFont('DejaVu Sans', 10)); p.setPen(QColor('#56705f')); p.drawText(28, 64, self.subtitle)
        for i, (state, outfit, caption, sub) in enumerate(self.items):
            x = 20 + (i % self.columns) * (self.size_ + 50); y = 84 + (i // self.columns) * (self.size_ + 76) + self.size_ + 18
            p.setPen(QColor('#1f3530')); p.setFont(QFont('DejaVu Sans', 10, QFont.Bold)); p.drawText(QRectF(x, y, self.size_ + 50, 20), Qt.AlignCenter, caption)
            p.setPen(QColor('#8a6d2b')); p.setFont(QFont('DejaVu Sans', 9)); p.drawText(QRectF(x, y + 18, self.size_ + 50, 18), Qt.AlignCenter, sub)
sheets = []
def sheet(name, *args, **kwargs):
    widget = Sheet(*args, **kwargs); sheets.append(widget); widget.show(); save(widget, name)
sheet('25-outfits.png', 'LAFA · three outfits', 'Tais Mane (default), Tuxedo and Casual. Change them in Lafa-Configuration or by right-clicking LAFA.',
      [(s, o, tr('en', o), tr('en', s)) for o in outfits.OUTFITS for s in ['idle', 'talking', 'walking']], columns=3, size=210)
sheet('26-formal-activities.png', 'Tuxedo · formal activities', 'Each activity is a pose of the outfit plus a small scene.', [(a, 'tuxedo', tr('en', a), personality.duty('en', a)) for a in outfits.FORMAL])
sheet('27-casual-activities.png', 'Casual · summer activities', 'Beach, town, café and shopping.', [(a, 'casual', tr('en', a), personality.duty('en', a)) for a in outfits.CASUAL])
sheet('28-tais-mane-activities.png', 'Tais Mane · school and daily life', 'The default outfit, including Tebe-tebe and Bidu dances.', [(a, 'traditional', tr('en', a), personality.duty('en', a)) for a in outfits.TRADITIONAL], columns=5, size=170)

with patch.dict(os.environ, {'LC_ALL': 'tet_TL.UTF-8'}):
    tet = Window(Settings(language='tet', roots=[]), review=True); tet.resize(1180, 820); tet.show(); pump(); tet.hero_character.animate(False); sample_school(tet); morning(tet); save(tet, '29-home-tetun.png')
    tet.navigate('teachers'); tet.teacher_list.setCurrentRow(5); save(tet, '30-teachers-tetun.png'); tet.companion.close(); tet.close()
with tempfile.TemporaryDirectory(prefix='lafa-eduka-') as home, patch('lafa.eduka.Path.home', return_value=Path(home)):
    for part, data in [('panel/settings.json', {'height': 42}), ('desktop/settings.json', {'theme_style': 'Edukasaun-Dark', 'accent_color': '#26a69a'})]:
        path = Path(home) / '.config/eduka-desktop' / part; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(data))
    app.setStyleSheet(style_sheet(Settings()))
    dark = Window(Settings(language='en', roots=[], costume='casual'), review=True); dark.resize(1180, 820); dark.show(); pump(); dark.hero_character.animate(False); morning(dark); save(dark, '31-home-eduka-dark-theme.png'); dark.companion.close(); dark.close()
    app.setStyleSheet(STYLE)
w.companion.close(); w.close()
for widget in [*reviews, *sheets]: widget.close()
temp.cleanup()
print(f'Saved {len(saved)} reproducible Qt captures to docs/screenshots.')
os._exit(0)
