"""Reproducible Qt captures of LAFA for developer review.

Review fixtures never call the internet and never write the
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
from lafa import personality, osguide, outfits, classroom
import random

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
w = Window(settings=settings, review=True); w.resize(1180, 820); w.show(); pump()
def wait_search(name='home'):
    import time
    end = time.monotonic() + 15; panel = w.search_panels[name]
    while time.monotonic() < end:
        app.processEvents()
        if panel['outcome'] is not None or panel['results'].toPlainText().strip(): break
        time.sleep(0.02)
    pump()
def search(text, name='home'):
    w.navigate('home'); w.search_panels[name]['outcome'] = None; w.search_panels[name]['results'].clear(); w.run_search(name, text); wait_search(name)
sample_school(w); morning(w)
w.reminders.add(45, 'Bring the science poster'); w.progress.opened('lesson', 'lafa://lesson/school/science:0', 'Science · The water cycle'); w.refresh_home()
save(w, '01-home.png')
w.resize(1024, 600); pump(); save(w, '02-home-1024x600.png'); w.resize(1180, 820); pump()
search('What is photosynthesis?'); save(w, '03-search-local-material.png')
w.search_panels['home']['wiki'] = [Source('Photosynthesis', 'https://en.wikipedia.org/wiki/Photosynthesis', 'REVIEW SAMPLE · extract shown only after “Search internet sources”')]
w.show_outcome('home', w.search_panels['home']['outcome']); save(w, '04-search-with-internet-source.png'); w.search_panels['home']['wiki'] = []
with tempfile.TemporaryDirectory(prefix='lafa-review-') as files:
    root = Path(files) / 'Documents'; root.mkdir()
    for name in ['Math_Homework_Fractions.txt', 'Math_Homework_Geometry.odt', 'Science_Notes.md', 'Timetable.csv']: (root / name).write_text('REVIEW SAMPLE', encoding='utf-8')
    w.settings.roots = [str(root)]; search('Find file math homework'); save(w, '05-search-files.png')
    w.show_files(FileSearch(w.settings.roots).search('', 'documents')); w.navigate('library', 'files'); pump(); w.file_table.selectRow(0); save(w, '15-library-my-files.png')
    w.settings.roots = []
search('How do I change the wallpaper?'); save(w, '06-search-os-guide.png')
search('zzqx unknownword'); save(w, '07-search-nothing-found.png')
w.navigate('study', 'lessons'); w.class_subject.setCurrentIndex(w.class_subject.findData('science')); w.lesson_list.setCurrentRow(1); save(w, '08-learn-lessons.png')
w.age_level.setCurrentIndex(w.age_level.findData('secondary')); w.class_subject.setCurrentIndex(w.class_subject.findData('atoms')); save(w, '09-learn-every-age.png'); w.age_level.setCurrentIndex(0)
w.navigate('study', 'subjects'); w.teacher_list.setCurrentRow(0); save(w, '10-learn-subject-guide.png')
def exam(kind, subject, seed, right):
    w.navigate('study', 'practice'); w.start_exam(kind, subject); w.exam = classroom.ExamSession(kind, subject, w.settings.locale, random.Random(seed)); w.show_exam_question()
    for i in range(right[0]):
        q = w.exam.current; w.answer_exam(next(j for j, b in enumerate(w.exam_buttons) if b.property('option') == (q.correct if i % right[1] else q.options[0] if q.options[0] != q.correct else q.options[1]))); w.show_exam_question()
exam('quiz', 'math', 3, (5, 5)); w.finish_exam()
exam('quiz', 'health', 11, (0, 1)); q = w.exam.current; w.answer_exam(next(j for j, b in enumerate(w.exam_buttons) if b.property('option') != q.correct)); save(w, '11-practice-explanation.png')
w.show_exam_question()
while w.exam.current: exam_q = w.exam.current; w.answer_exam(next(j for j, b in enumerate(w.exam_buttons) if b.property('option') == exam_q.correct)); w.show_exam_question()
w.finish_exam(); save(w, '12-practice-result.png')
w.navigate('study', 'languages'); w.course_list.setCurrentRow(0); save(w, '13-learn-languages.png')
w.navigate('study', 'coding'); w.code_lesson.setCurrentIndex(2); result = LessonPython().run(w.code_editor.toPlainText()); w.code_output.setPlainText(result.output + f'\n\n{result.steps} lesson steps'); save(w, '14-learn-programming.png')
w.navigate('library', 'sources'); w.fill_sources(None); save(w, '16-library-sources.png')
w.fill_sources('tl_gov'); save(w, '17-library-timor-leste-government.png'); w.fill_sources(None)
w.navigate('library', 'external'); save(w, '18-library-external-sites.png')
tb = w.timor_browser
w.navigate('timor', 'atlas'); tb.go({'kind': 'home'}); save(w, '19-timor-leste-encyclopedia.png')
tb.open_category('culture'); save(w, '20-timor-leste-culture-topics.png')
tb.open_article('tl.culture.tais'); save(w, '20b-timor-leste-article-tais.png')
tb.open_category('leaders'); tb.open_article('atlas:presidents'); save(w, '20c-timor-leste-presidents.png')
tb.open_article('atlas:history_17'); save(w, '20d-timor-leste-history.png')
wb = w.world_browser
w.navigate('study', 'encyclopedia'); wb.go({'kind': 'home'}); save(w, '70-learn-world-encyclopedia.png')
wb.open_category('dinosaurs'); save(w, '71-world-dinosaurs-topics.png')
wb.open_article('w.dinosaurs.what_are_dinosaurs'); save(w, '72-article-dinosaurs-read.png')
wb.page.set_tab('explore'); save(w, '73-module-dinosaurs-explore.png')
wb.page.set_tab('practice'); save(w, '74-article-practice-quiz.png')
wb.open_article('w.earth.formation', 'explore'); save(w, '75-module-earth-history-timeline.png')
wb.open_article('w.industrial_revolution.steam_factories', 'explore'); save(w, '76-module-industrial-revolution.png')
wb.go({'kind': 'coverage'}); save(w, '77-encyclopedia-coverage.png')
w.navigate('library', 'sources'); save(w, '78-library-offline-pack.png')
for size, name in [((1024, 600), '80-1024x600-timor-leste.png'), ((1366, 768), '81-1366x768-article.png'), ((1920, 1080), '82-1920x1080-world-encyclopedia.png')]:
    w.resize(*size); pump()
    if name.startswith('80'): w.navigate('timor', 'atlas'); tb.go({'kind': 'home'})
    elif name.startswith('81'): w.navigate('timor', 'atlas'); tb.open_article('tl.culture.tais')
    else: w.navigate('study', 'encyclopedia'); wb.go({'kind': 'home'})
    save(w, name)
w.resize(1180, 820); pump()
w.show_timor_news(NewsReport([Source('SAMPLE · Learning and education in Timor-Leste', 'https://tatoli.tl/', '', 'Tatoli · SAMPLE', 'REVIEW SAMPLE'), Source('SAMPLE · Arts, culture and community life', 'https://timorpost.com/', '', 'Timor Post · SAMPLE', 'REVIEW SAMPLE')], 'REVIEW SAMPLE · not live headlines'))
w.navigate('timor', 'news'); save(w, '21-timor-leste-news.png'); tb.go({'kind': 'home'})
w.navigate('activities', 'tasks'); save(w, '22-activities-tasks.png')
w.navigate('activities', 'reminders'); w.start_focus(25); w.render_reminders(); save(w, '23-activities-reminders-focus.png')
w.navigate('activities', 'results'); save(w, '24-activities-practice-results.png')
w.navigate('oshelp', 'guides'); w.show_guide(osguide.BY_KEY['display']); save(w, '25-os-help-guides.png')
w.navigate('oshelp', 'access'); save(w, '26-os-help-accessibility.png')
w.set_online(False); w.navigate('home'); morning(w); save(w, '27-offline-home.png')
search('Ataúro'); save(w, '28-offline-search.png'); w.set_online(True)
w.open_about(); pump(); save(w.about_dialog, '29-about.png'); w.about_dialog.accept()
w.open_settings(); pump()
for row, name in [(0, '30-lafa-settings-virtual-assistant.png'), (3, '31-lafa-settings-desktop.png')]:
    w.settings_categories.setCurrentRow(row); save(w.settings_dialog, name)
w.settings_dialog.accept()

# Eduka-Settings → Lafa-Configuration (real Eduka-Settings when a checkout is given).
eduka_src = os.environ.get('EDUKA_DESKTOP_SRC')
if eduka_src and Path(eduka_src, 'usr/bin/eduka-settings').is_file():
    for name, scroll in [('32-eduka-settings-lafa-configuration.png', 0.0), ('33-eduka-settings-lafa-configuration-2.png', 0.55)]:
        subprocess.run([sys.executable, str(ROOT / 'tools/eduka-settings-preview.py'), eduka_src, str(out / name), '--scroll', str(scroll)],
                       env={**os.environ, 'LAFA_QT': 'pyqt5'}, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); saved.append(name)
else:
    sys.path.insert(0, str(ROOT / 'integration'))
    from demo_eduka_settings import build_host
    with tempfile.TemporaryDirectory(prefix='lafa-host-capture-') as folder, patch.dict(os.environ, {'XDG_CONFIG_HOME': folder}):
        host = build_host(review=True); host.setStyleSheet(STYLE); host.resize(1000, 900); host.show(); save(host, '32-eduka-settings-lafa-configuration.png'); host.close()

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
compose('40-virtual-walking-on-panel.png', 'LAFA walks on the Eduka-Panel', 'When idle, LAFA walks along the real panel, then studies, reads, plays or dances.', [(walker, QPoint(640, PANEL_TOP - walker.height() + 12))])
studying = pet('studying'); bubble = balloon_for('studying', personality.CAUGHT['en']['studying'])
compose('41-virtual-hover-question.png', 'Touch LAFA with the cursor…', '…and LAFA stops, asks how it can help, and says what it was doing.', [(studying, QPoint(900, PANEL_TOP - studying.height() + 12)), (bubble, QPoint(900 + studying.width() - bubble.width() + 40, PANEL_TOP - studying.height() - bubble.height() + 40))])
party = pet('party', 'tuxedo'); bubble = balloon_for('party', personality.CAUGHT['en']['party'])
compose('42-virtual-tuxedo-party.png', 'Formal: formal activities', 'Parties, meetings, presentations, ceremonies and gala dinners.', [(party, QPoint(860, PANEL_TOP - party.height() + 12)), (bubble, QPoint(860 + party.width() - bubble.width() + 40, PANEL_TOP - party.height() - bubble.height() + 40))])
beach = pet('beach', 'casual'); bubble = balloon_for('beach', personality.CAUGHT['en']['beach'])
compose('43-virtual-casual-beach.png', 'Casual Belajar: everyday activities', 'Green shirt with a small tais collar, cream trousers and brown shoes.', [(beach, QPoint(500, PANEL_TOP - beach.height() + 12)), (bubble, QPoint(500 + beach.width() - bubble.width() + 40, PANEL_TOP - beach.height() - bubble.height() + 40))])
pet('idle'); c.introduced = False; c.show_bubble(c.introduction(9)); pump(); chat = c.grab()
c.collapse(); c.recommendation = 'Continue learning: Tais — the woven cloth of Timor-Leste'; c.introduced = True; c.toggle_bubble(); pump(); recommend = c.grab()
compose('45-virtual-recommendation.png', 'Click LAFA', 'One learning recommendation: continue where you stopped.', [(recommend, QPoint(800, PANEL_TOP - recommend.height() + 12))])
compose('44-virtual-bubble.png', 'Click LAFA', 'Search, Continue learning, Explore, Tasks, OS help — all without internet.', [(chat, QPoint(800, PANEL_TOP - chat.height() + 12))])
c.collapse()
# Walk cycle: 8 drawn frames chosen by the distance walked (lafa-walk.png), then a jump.
steps = []
c.settings.costume = 'casual'; c.apply_preferences(); c.set_state('walking'); c.pet.animated = True
for i in range(8):
    c.pet.hold = 0; c.pet.distance = i * c.pet.atlas.walk_meta['stride'] * c.pet.walk_scale() / 8 + 0.5; c.pet.motion.fade = 1.0; pump(); steps.append(c.grab())
c.set_state('talking'); c.pet.motion.t = 0; c.pet.motion.gesture = ''; c.pet.motion.play('jump')
for i in range(3):
    c.pet.motion.advance(0.15 if i == 0 else 0.2); c.pet.motion.fade = 1.0; pump(); steps.append(c.grab())
c.pet.animated = False; c.pet.motion.gesture = ''
compose('46-virtual-human-movement.png', 'LAFA moves like a person', 'Eight walk frames synced to the distance moved (no foot sliding), then a happy jump.',
        [(img, QPoint(20 + i * 112, PANEL_TOP - img.height() + 12)) for i, img in enumerate(steps)])
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
sheet('50-outfits.png', 'LAFA · three outfits', 'Tais Mane (default), Formal and Casual Belajar. Change them in Lafa-Configuration or by right-clicking LAFA.',
      [(s, o, tr('en', o), tr('en', s)) for o in outfits.OUTFITS for s in ['idle', 'talking', 'walking']], columns=3, size=210)
sheet('51-formal-activities.png', 'Formal · formal activities', 'Each activity is a pose of the outfit plus a small scene.', [(a, 'tuxedo', tr('en', a), personality.duty('en', a)) for a in outfits.FORMAL])
sheet('52-casual-activities.png', 'Casual Belajar · everyday activities', 'Beach, town, café and shopping.', [(a, 'casual', tr('en', a), personality.duty('en', a)) for a in outfits.CASUAL])
sheet('53-lafa-roles.png', "LAFA's roles · optional entertainment", 'Teacher, professor, motivator, magician, master and comedian (Settings → entertainment).',
      [(a, o, tr('en', a), tr('en', o)) for o in outfits.OUTFITS for a in outfits.ROLES], columns=6, size=170)
for o, title in [('tuxedo', 'Formal on every pose'), ('casual', 'Casual Belajar on every pose: green shirt, tais collar, cream trousers, brown shoes')]:
    sheet(f'54-{o}-all-poses.png' if o == 'tuxedo' else '55-casual-all-poses.png', title, 'Only bathing and the toilet are undressed.', [(s, o, tr('en', s), '') for s in STATES if s not in ('tebe', 'bidu')], columns=5, size=170)
sheet('56-tais-mane-activities.png', 'Tais Mane · school and daily life', 'The default outfit, including Tebe-tebe and Bidu dances.', [(a, 'traditional', tr('en', a), personality.duty('en', a)) for a in outfits.TRADITIONAL], columns=5, size=170)

with patch.dict(os.environ, {'LC_ALL': 'tet_TL.UTF-8'}):
    tet = Window(Settings(language='tet', roots=[]), review=True); tet.resize(1180, 820); tet.show(); pump(); sample_school(tet); morning(tet); save(tet, '60-home-tetun.png')
    tet.navigate('study', 'lessons'); save(tet, '61-learn-tetun.png'); tet.navigate('timor', 'atlas'); tet.timor_browser.open_article('tl.culture.tais'); save(tet, '64-timor-article-tetun.png'); tet.companion.close(); tet.close()
with tempfile.TemporaryDirectory(prefix='lafa-eduka-') as home, patch('lafa.eduka.Path.home', return_value=Path(home)):
    for part, data in [('panel/settings.json', {'height': 42}), ('desktop/settings.json', {'theme_style': 'Edukasaun-Dark', 'accent_color': '#26a69a'})]:
        path = Path(home) / '.config/eduka-desktop' / part; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(data))
    app.setStyleSheet(style_sheet(Settings()))
    dark = Window(Settings(language='en', roots=[], costume='casual'), review=True); dark.resize(1180, 820); dark.show(); pump(); morning(dark); save(dark, '62-home-eduka-dark-theme.png'); dark.navigate('timor'); save(dark, '63-timor-encyclopedia-dark-theme.png'); dark.timor_browser.open_article('tl.culture.tais'); save(dark, '65-article-dark-theme.png'); dark.navigate('study', 'encyclopedia'); dark.world_browser.open_article('w.dinosaurs.what_are_dinosaurs', 'explore'); save(dark, '66-module-dark-theme.png'); dark.companion.close(); dark.close()
    app.setStyleSheet(STYLE)
w.companion.close(); w.close()
for widget in [*reviews, *sheets]: widget.close()
temp.cleanup()
print(f'Saved {len(saved)} reproducible Qt captures to docs/screenshots.')
os._exit(0)
