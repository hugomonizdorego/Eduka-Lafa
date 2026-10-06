"""Reproducible English Qt captures; review fixtures never call internet/API."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import tempfile
from unittest.mock import patch
from PySide6.QtCore import Qt,QRectF
from PySide6.QtGui import QPainter,QLinearGradient,QColor,QFont
from PySide6.QtWidgets import QApplication,QWidget,QScrollArea
from lafa.app import Window,STYLE
from lafa.config import Settings,STATES
from lafa.mascot import Character
from lafa.tools import FileSearch,Source
from lafa.live_info import Location,WeatherReport,ForecastDay,NewsReport
from lafa.timor import Card
from lafa.learning import LessonPython
from lafa.i18n import tr

out=Path(__file__).resolve().parents[1]/'docs/screenshots';out.mkdir(parents=True,exist_ok=True)
app=QApplication([]);app.setStyle('Fusion');app.setStyleSheet(STYLE)
def pump():
    for _ in range(3):app.processEvents()
def capture(name):pump();w.grab().save(str(out/name))
settings=Settings(language='en',roots=[])
w=Window(settings=settings,review=True);w.resize(1160,820);w.show();pump();w.hero_character.animate(False)
capture('01-lafa-conversation.png')
with tempfile.TemporaryDirectory(prefix='lafa-review-') as temp:
    root=Path(temp)/'Documents';root.mkdir()
    for name,text in [('Lesson_Photosynthesis.txt','REVIEW SAMPLE\nPhotosynthesis.'),('Lesson_Mathematics.txt','REVIEW SAMPLE\nMultiplication.'),('Timor_Leste_Notes.md','# Review sample\nTimor-Leste.'),('Lesson_Schedule.csv','day,lesson\nMonday,Mathematics')]:
        (root/name).write_text(text,encoding='utf-8')
    settings.roots=[str(root)];w.show_files(FileSearch(settings.roots).search('','documents'))
    w.kind.setCurrentIndex(w.kind.findData('documents'));w.navigate(1);pump();w.file_table.selectRow(0)
    capture('02-lafa-local-files.png')
w.navigate(3);capture('03-lafa-ai-services.png')
w.set_online(False);w.navigate(0);capture('04-lafa-offline.png');w.set_online(True)
w.open_settings();pump();w.settings_dialog.grab().save(str(out/'10-lafa-settings.png'));w.settings_dialog.accept()
w.activate_mode('enable');w.companion.animate(False);pump()
intro_overlay=w.companion.grab()
w.companion.show_card(Card('Did you know?\nDili is the capital of Timor-Leste.\nExplore local history at the Resistance Museum.\nSource checked: 6 October 2026','https://www.timorleste.tl/municipalities/dili/','reading','culture'));pump()
actual_overlay=w.companion.grab()

class DesktopReview(QWidget):
    """Actual companion pixels on an explicitly illustrative desktop background."""
    def __init__(self,overlay,title):super().__init__();self.overlay=overlay;self.title=title;self.resize(1280,800)
    def paintEvent(self,event):
        p=QPainter(self);p.setRenderHint(QPainter.Antialiasing)
        gradient=QLinearGradient(0,0,1280,800);gradient.setColorAt(0,QColor('#0b4339'));gradient.setColorAt(1,QColor('#218163'));p.fillRect(self.rect(),gradient)
        p.setPen(QColor('#dff5e9'));p.setFont(QFont('DejaVu Sans',28,QFont.Bold));p.drawText(50,81,self.title)
        p.setFont(QFont('DejaVu Sans',10));p.drawText(51,117,'REVIEW · actual LAFA widget on an illustrated desktop · target OS integration still requires testing')
        for i,(title,subtitle) in enumerate([('01  LAFA Desktop','Type, research, read and learn to code'),('02  LAFA Virtual Assistant','A companion from Timor-Leste, enabled in Settings'),('03  Culture and encouragement','Source-linked facts, local headlines and positive notes')]):
            y=208+i*136;p.setPen(Qt.NoPen);p.setBrush(QColor(255,255,255,22));p.drawRoundedRect(QRectF(50,y,570,105),16,16)
            p.setPen(QColor('#f1fff6'));p.setFont(QFont('DejaVu Sans',16,QFont.Bold));p.drawText(73,y+38,title);p.setFont(QFont('DejaVu Sans',10));p.drawText(73,y+72,subtitle)
        p.drawPixmap(783,206,self.overlay)
        p.setPen(QColor('#d0eedd'));p.setFont(QFont('DejaVu Sans',10));p.drawText(51,713,'Click to chat · drag to move · right click for activities · X11 walking above Eduka-Panel')
        p.setPen(Qt.NoPen);p.setBrush(QColor('#163e30'));p.drawRoundedRect(QRectF(390,758,500,30),12,12)
        p.setPen(QColor('#bfdacb'));p.setFont(QFont('DejaVu Sans',10));p.drawText(421,779,'Eduka-Panel     LAFA Desktop    Documents    Settings')
reviews=[]
for name,overlay,title in [('05-lafa-desktop-concept.png',actual_overlay,'A little companion. A world to explore.'),('14-lafa-first-activation.png',intro_overlay,'Hello from Timor-Leste.')]:
    review=DesktopReview(overlay,title);reviews.append(review);review.show();pump();review.grab().save(str(out/name))
class Poses(QWidget):
    def __init__(self,traditional=False):
        super().__init__();self.states=['idle','reading','thinking','walking','sitting','talking','studying','tebe','bidu'] if traditional else STATES
        self.resize(990,100+((len(self.states)+2)//3)*295);self.setStyleSheet('background:#f2f7f0;')
        for i,state in enumerate(self.states):
            pet=Character(w.atlas,self,220);pet.costume='traditional' if traditional else 'casual';pet.set_state(state);pet.animate(False);pet.move((i%3)*330+55,(i//3)*295+80)
    def paintEvent(self,event):
        p=QPainter(self);p.setPen(QColor('#29533a'));p.setFont(QFont('DejaVu Sans',16,QFont.Bold));p.drawText(32,40,'LAFA · traditional clothing and dance poses' if len(self.states)==9 else 'LAFA · seventeen activities')
        p.setFont(QFont('DejaVu Sans',10));p.drawText(32,66,'Illustrated mascot poses with procedural animation; dance poses are artistic interpretations.')
        p.setFont(QFont('DejaVu Sans',11,QFont.Bold))
        for i,state in enumerate(self.states):p.drawText(QRectF((i%3)*330,(i//3)*295+335,330,26),Qt.AlignCenter,tr('en',state).upper())
poses=[]
for traditional,name in [(False,'06-lafa-character-poses.png'),(True,'13-lafa-traditional-dances.png')]:
    widget=Poses(traditional);poses.append(widget);widget.show();pump();widget.grab().save(str(out/name))
weather=WeatherReport(Location('Dili',-8.5586,125.5736,'Asia/Dili','Timor-Leste'),'SAMPLE 10:00','REVIEW SAMPLE · not live data','Asia/Dili',29,32,65,12,2,[ForecastDay('SAMPLE day 1',24,31,20,2),ForecastDay('SAMPLE day 2',24,30,40,80),ForecastDay('SAMPLE day 3',23,30,35,2)])
w.show_weather(weather);w.show_news(NewsReport([Source('Sample headline to review the news layout','https://www.bbc.com/news/world','','BBC World · SAMPLE','REVIEW SAMPLE'),Source('Open a headline on the publisher website','https://www.theguardian.com/world','','The Guardian · SAMPLE','REVIEW SAMPLE')],'REVIEW SAMPLE · not current news'))
w.navigate(5);capture('07-lafa-weather-news.png')
w.navigate(2);w.resize(1160,1020)
for scroll in w.stack.widget(2).findChildren(QScrollArea):scroll.setMaximumHeight(450);scroll.setMinimumHeight(400)
capture('08-lafa-learning-sources.png')
w.reminder_text.setText('Drink water and stretch');w.reminder_minutes.setValue(5);w.add_reminder();w.navigate(6);w.resize(1160,820);capture('09-lafa-reminders.png')
w.show_timor_news(NewsReport([Source('SAMPLE · Learning and education in Timor-Leste','https://tatoli.tl/','','Tatoli · SAMPLE','REVIEW SAMPLE'),Source('SAMPLE · Arts, culture and community life','https://timorpost.com/','','Timor Post · SAMPLE','REVIEW SAMPLE'),Source('SAMPLE · Development and technology updates','https://timor-leste.gov.tl/?lang=en','','Government · SAMPLE','REVIEW SAMPLE')],'REVIEW SAMPLE · not live headlines'));w.navigate(8);capture('11-lafa-timor-leste.png')
w.navigate(7);w.code_lesson.setCurrentIndex(2);result=LessonPython().run(w.code_editor.toPlainText());w.code_output.setPlainText(result.output+f'\n\n{result.steps} lesson steps');capture('12-lafa-virtual-coding.png')
w.open_settings();w.settings_tabs.setCurrentIndex(1);pump();w.settings_dialog.grab().save(str(out/'17-lafa-ai-language-settings.png'));w.settings_dialog.accept()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'integration'))
from demo_eduka_settings import build_host
with tempfile.TemporaryDirectory(prefix='lafa-host-capture-') as folder,patch.dict(os.environ,{'XDG_CONFIG_HOME':folder}):
    host=build_host(review=True);host.setStyleSheet(STYLE);host.show();pump();host.grab().save(str(out/'15-lafa-native-settings-host.png'));host.close()
with patch.dict(os.environ,{'LC_ALL':'id_ID.UTF-8'}):
    localized=Window(Settings(language='system',roots=[]),review=True);localized.resize(1160,820);localized.show();pump();localized.grab().save(str(out/'16-lafa-system-language.png'));localized.companion.close();localized.close()
w.companion.close();w.close()
for widget in [*reviews,*poses]:widget.close()
print('Saved 17 reproducible Qt captures to docs/screenshots.')
