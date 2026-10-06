"""Reproducible Qt captures of the redesigned LAFA for developer review.

Review fixtures never call the internet or an AI provider and never write the
user's preferences. Run:
    QT_QPA_PLATFORM=offscreen .venv/bin/python scripts/capture-screenshots.py
Output: docs/screenshots/*.png (listed in docs/SCREENSHOTS.md).
"""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import tempfile
from unittest.mock import patch
from PySide6.QtCore import Qt,QRectF,QPoint
from PySide6.QtGui import QPainter,QLinearGradient,QColor,QFont,QPixmap
from PySide6.QtWidgets import QApplication,QWidget,QScrollArea
from lafa.app import Window,STYLE
from lafa.config import Settings,STATES
from lafa.mascot import Character,greeting_key
from lafa.tools import FileSearch,Source
from lafa.live_info import Location,WeatherReport,ForecastDay,NewsReport
from lafa.learning import LessonPython
from lafa.i18n import tr
from lafa import personality,osguide

out=Path(__file__).resolve().parents[1]/'docs/screenshots';out.mkdir(parents=True,exist_ok=True)
for old in out.glob('*.png'):old.unlink()
app=QApplication([]);app.setStyle('Fusion');app.setStyleSheet(STYLE)
saved=[]
def pump():
    for _ in range(4):app.processEvents()
def save(widget,name):pump();widget.grab().save(str(out/name));saved.append(name)
def morning(window):
    """Fixed greeting so captures do not depend on the capture time."""
    window.home_greeting.setText(tr(window.settings.locale,greeting_key(9)))

temp_config=tempfile.TemporaryDirectory(prefix='lafa-capture-');os.environ['XDG_CONFIG_HOME']=temp_config.name
settings=Settings(language='en',roots=[])
w=Window(settings=settings,review=True);w.resize(1180,820);w.show();pump();w.hero_character.animate(False)
morning(w);save(w,'01-home.png')
w.navigate('chat');w.send_message('How do I connect Wi-Fi?');w.send_message('/calc 12*7');save(w,'02-conversation.png')
w.navigate('os_help');w.show_guide(osguide.BY_KEY['apps']);save(w,'03-edukasaun-os-help.png')
with tempfile.TemporaryDirectory(prefix='lafa-review-') as temp:
    root=Path(temp)/'Documents';root.mkdir()
    for name,text in [('Lesson_Photosynthesis.txt','REVIEW SAMPLE\nPhotosynthesis.'),('Lesson_Mathematics.txt','REVIEW SAMPLE\nMultiplication.'),('Timor_Leste_Notes.md','# Review sample\nTimor-Leste.'),('Lesson_Schedule.csv','day,lesson\nMonday,Mathematics')]:
        (root/name).write_text(text,encoding='utf-8')
    settings.roots=[str(root)];w.show_files(FileSearch(settings.roots).search('','documents'))
    w.kind.setCurrentIndex(w.kind.findData('documents'));w.navigate('files');pump();w.file_table.selectRow(0)
    save(w,'04-local-files.png')
w.show_sources([Source('Photosynthesis','https://en.wikipedia.org/wiki/Photosynthesis','REVIEW SAMPLE · process used by plants to convert light energy'),Source('Dili','https://en.wikipedia.org/wiki/Dili','REVIEW SAMPLE · capital of Timor-Leste')])
w.navigate('learn');save(w,'05-learn-research.png')
w.navigate('coding');w.code_lesson.setCurrentIndex(2);result=LessonPython().run(w.code_editor.toPlainText());w.code_output.setPlainText(result.output+f'\n\n{result.steps} lesson steps');save(w,'06-virtual-coding.png')
weather=WeatherReport(Location('Dili',-8.5586,125.5736,'Asia/Dili','Timor-Leste'),'SAMPLE 10:00','REVIEW SAMPLE · not live data','Asia/Dili',29,32,65,12,2,[ForecastDay('SAMPLE day 1',24,31,20,2),ForecastDay('SAMPLE day 2',24,30,40,80),ForecastDay('SAMPLE day 3',23,30,35,2)])
w.show_weather(weather);w.show_news(NewsReport([Source('Sample headline to review the news layout','https://www.bbc.com/news/world','','BBC World · SAMPLE','REVIEW SAMPLE'),Source('Open a headline on the publisher website','https://www.theguardian.com/world','','The Guardian · SAMPLE','REVIEW SAMPLE')],'REVIEW SAMPLE · not current news'))
w.navigate('live');save(w,'07-weather-news.png')
w.reminder_text.setText('Drink water and stretch');w.reminder_minutes.setValue(5);w.add_reminder();w.navigate('reminders');save(w,'08-reminders.png')
w.show_timor_news(NewsReport([Source('SAMPLE · Learning and education in Timor-Leste','https://tatoli.tl/','','Tatoli · SAMPLE','REVIEW SAMPLE'),Source('SAMPLE · Arts, culture and community life','https://timorpost.com/','','Timor Post · SAMPLE','REVIEW SAMPLE')],'REVIEW SAMPLE · not live headlines'));w.navigate('culture');save(w,'09-timor-leste.png')
w.navigate('hub');save(w,'10-ai-services.png')
w.set_online(False);w.navigate('home');morning(w);save(w,'11-offline.png');w.set_online(True)
w.open_settings();pump()
for row,name in [(0,'12-settings-virtual-assistant.png'),(2,'13-settings-personality.png'),(1,'14-settings-ai-language.png')]:
    w.settings_categories.setCurrentRow(row);save(w.settings_dialog,name)
w.settings_dialog.accept()

# Eduka-Settings host page with the full LAFA preferences (temporary config).
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'integration'))
from demo_eduka_settings import build_host
with tempfile.TemporaryDirectory(prefix='lafa-host-capture-') as folder,patch.dict(os.environ,{'XDG_CONFIG_HOME':folder}):
    host=build_host(review=True);host.setStyleSheet(STYLE);host.resize(1000,900);host.show();save(host,'15-eduka-settings-lafa-page.png');host.close()

# Virtual Assistant on an illustrated desktop with the Eduka-Panel.
w.activate_mode('enable');c=w.companion;c.animate(False);c.collapse();pump()
class DesktopReview(QWidget):
    """Actual LAFA widget pixels composited on an explicitly illustrative desktop."""
    def __init__(self,title,subtitle,layers):super().__init__();self.title=title;self.subtitle=subtitle;self.layers=layers;self.resize(1280,800)
    def paintEvent(self,event):
        p=QPainter(self);p.setRenderHint(QPainter.Antialiasing)
        gradient=QLinearGradient(0,0,1280,800);gradient.setColorAt(0,QColor('#0b4339'));gradient.setColorAt(1,QColor('#218163'));p.fillRect(self.rect(),gradient)
        p.setPen(QColor('#e9f7ef'));p.setFont(QFont('DejaVu Sans',26,QFont.Bold));p.drawText(50,80,self.title)
        p.setFont(QFont('DejaVu Sans',11));p.drawText(51,112,self.subtitle)
        p.setFont(QFont('DejaVu Sans',9));p.setPen(QColor('#bfe0cf'));p.drawText(51,136,'REVIEW · actual LAFA widgets on an illustrated desktop · target OS integration still requires testing')
        for i,(icon,name) in enumerate([('📁','Documents'),('🌐','Browser'),('📝','LibreOffice'),('🐊','LAFA Desktop')]):
            y=190+i*104;p.setPen(Qt.NoPen);p.setBrush(QColor(255,255,255,26));p.drawRoundedRect(QRectF(52,y,84,84),16,16)
            p.setPen(QColor('#ffffff'));p.setFont(QFont('Noto Color Emoji',26));p.drawText(QRectF(52,y,84,62),Qt.AlignCenter,icon);p.setFont(QFont('DejaVu Sans',9));p.drawText(QRectF(36,y+60,116,22),Qt.AlignCenter,name)
        p.setPen(Qt.NoPen);p.setBrush(QColor('#0d2d25'));p.drawRect(0,758,1280,42)
        p.setPen(QColor('#cfe6da'));p.setFont(QFont('DejaVu Sans',10));p.drawText(18,784,'☰  Eduka-Panel     LAFA Desktop     Files     Browser');p.drawText(1110,784,'📶  🔊  09:00')
        for pixmap,point in self.layers:p.drawPixmap(point,pixmap)
reviews=[]
def compose(name,title,subtitle,layers):
    review=DesktopReview(title,subtitle,layers);reviews.append(review);review.show();save(review,name)
c.set_state('walking');pet=c.grab()
compose('16-virtual-walking-on-panel.png','LAFA walks on the Eduka-Panel','When idle, LAFA patrols the panel, then studies, reads, plays or dances.',[(pet,QPoint(640,758-pet.height()+1))])
c.set_state('studying');pump();pet=c.grab()
with patch('lafa.personality.hover_line',return_value=personality.CAUGHT['en']['studying']):c.on_hover(True)
c.balloon.adjustSize();balloon=c.balloon.grab();c.hide_balloon();c.hovered=False
compose('17-virtual-hover-question.png','Touch LAFA with the cursor…','…and LAFA stops, asks how it can help, and says what it was doing.',[(pet,QPoint(900,758-pet.height()+1)),(balloon,QPoint(900+pet.width()-balloon.width()+40,758-pet.height()-balloon.height()+30))])
c.set_state('bathing');pump();pet=c.grab()
with patch('lafa.personality.hover_line',return_value=personality.CAUGHT['en']['bathing']):c.on_hover(True)
balloon=c.balloon.grab();c.hide_balloon();c.hovered=False
compose('18-virtual-funny-activity.png','Innocent, clever and funny','Caught in the bath — but still ready to help.',[(pet,QPoint(380,758-pet.height()+1)),(balloon,QPoint(380+pet.width()-balloon.width()+40,758-pet.height()-balloon.height()+30))])
c.introduced=False;c.set_state('idle');c.settings.companion=True;c.show_bubble(c.introduction(9));pump();bubble=c.grab()
compose('19-virtual-chat-bubble.png','Click LAFA to chat','Quick help for Edukasaun OS, weather, Timor-Leste news, focus and jokes.',[(bubble,QPoint(800,758-bubble.height()+1))])
c.collapse()

class Activities(QWidget):
    """Every pose with the assistant job it represents."""
    def __init__(self,traditional=False):
        super().__init__();self.traditional=traditional;self.states=['idle','reading','thinking','walking','sitting','talking','studying','tebe','bidu'] if traditional else STATES
        self.resize(1050,110+((len(self.states)+2)//3)*300);self.setStyleSheet('background:#f3f6f2;')
        for i,state in enumerate(self.states):
            pet=Character(w.atlas,self,210);pet.costume='traditional' if traditional else 'casual';pet.set_state(state);pet.animate(False);pet.move((i%3)*350+70,(i//3)*300+86)
    def paintEvent(self,event):
        p=QPainter(self);p.setPen(QColor('#0f5a46'));p.setFont(QFont('DejaVu Sans',16,QFont.Bold))
        p.drawText(32,40,'LAFA · traditional clothing and dance poses' if self.traditional else 'LAFA · activities as a virtual assistant\'s working day')
        p.setFont(QFont('DejaVu Sans',10));p.setPen(QColor('#56705f'));p.drawText(32,66,'Pose name and the assistant duty LAFA shows on hover. Dance poses are artistic interpretations.')
        for i,state in enumerate(self.states):
            x=(i%3)*350;y=(i//3)*300+318
            p.setPen(QColor('#1f3530'));p.setFont(QFont('DejaVu Sans',11,QFont.Bold));p.drawText(QRectF(x,y,350,22),Qt.AlignCenter,tr('en',state).upper())
            p.setPen(QColor('#8a6d2b'));p.setFont(QFont('DejaVu Sans',9));p.drawText(QRectF(x,y+20,350,20),Qt.AlignCenter,personality.duty('en',state))
poses=[]
for traditional,name in [(False,'20-character-activities.png'),(True,'21-traditional-dances.png')]:
    widget=Activities(traditional);poses.append(widget);widget.show();save(widget,name)

for lang,name in [('id','22-home-indonesian.png'),('tet','23-home-tetun.png')]:
    localized=Window(Settings(language=lang,roots=[]),review=True);localized.resize(1180,820);localized.show();pump();localized.hero_character.animate(False);morning(localized)
    save(localized,name);localized.companion.close();localized.close()
w.companion.close();w.close()
for widget in [*reviews,*poses]:widget.close()
temp_config.cleanup()
print(f'Saved {len(saved)} reproducible Qt captures to docs/screenshots.')
