"""LAFA Desktop — Lafa, learning companion and Edukasaun OS assistant.

Six sections: Home, Learn, Library, Timor-Leste, My activities and OS help
(Settings and About at the bottom of the sidebar). Everything in Home,
Learn, Library (local), My activities and OS help works without internet,
login or AI key. Internet sources (Wikipedia, news, weather, websites) are
extras: they are asked for explicitly and fail independently. All network and
file work runs outside the GUI thread.
"""
import argparse
import copy
import os
from dataclasses import asdict
from pathlib import Path
from urllib.parse import urlsplit, quote, unquote, parse_qs
import html
import re
import shutil
import sys
import tempfile
import time
from datetime import datetime
from .qt import (
    QSize,QDate,QDateEdit,QDateTimeEdit,QDateTime,QTabWidget,QShortcut,QKeySequence,
    Qt,QObject,Signal,QRunnable,QThreadPool,QTimer,QUrl,QLockFile,Slot,QProcess,
    QIcon,QDesktopServices,QFont,QPalette,
    QApplication,QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QGridLayout,
    QLabel,QPushButton,QLineEdit,QComboBox,QCheckBox,QStackedWidget,QFrame,
    QScrollArea,QTextBrowser,QTableWidget,QTableWidgetItem,QHeaderView,QFormLayout,QListWidget,
    QFileDialog,QMessageBox,QDialog,QPlainTextEdit,QMenu,QSystemTrayIcon,QSpinBox,QListWidgetItem,QSizePolicy,QColor,QProgressBar,
    BINDING,run,started,prepare_application,
)
from . import VERSION_LABEL
from .config import Settings, AI_LINKS, SECTIONS as SECTION_KEYS, LEGACY_PAGES, config_path
from .i18n import tr
from .net import online_probe
from .tools import FileSearch, Source, RESOURCES, encyclopedia_search, encyclopedia_article, web_url
from .agent import Agent, Result, direct_intent, LOCAL_TOOLS, INTERNET_TOOLS
from .voice import Voice
from .mascot import Atlas, Character, Companion
from .live_info import Location,LocationChoices,WeatherReport,weather_query,forecast,weather_text,world_news,news_text
from .timor import CardDeck,Card,timor_news,NEWS_LINKS
from .learning import LessonPython,LESSONS,REFERENCES,LESSON_KEYS
from .reminders import Reminders
from .progress import Progress
from .instance import server_name,activate_existing,ActivationServer
from . import icons, encyclopedia as enc
from .encyclopedia_ui import Browser
from . import osguide, personality, eduka, outfits, school, updates, classroom, roles, timorleste, timor_atlas, livefacts, ui_kit, sources, offline, languages, platform_check, memory, curriculum, actions, search, source_meta
import random


class PackRelay(QObject):
    """Progress of the offline download, delivered on the UI thread."""
    progress=Signal(int,int,str)

class Signals(QObject):
    done=Signal(object)
    error=Signal(str)
class Delivery(QObject):
    """QObject receiver pins callback execution to the UI thread."""
    def __init__(self,window,job,callback,busy):
        super().__init__(window)
        self.window=window; self.job=job; self.callback=callback; self.busy=busy
    @Slot(object)
    def done(self,value):
        self.window.jobs.discard(self.job)
        try:self.callback(value)
        except Exception as error:
            if self.busy:self.window.set_busy(False)
            self.window.error(str(error))
        finally:self.deleteLater()
    @Slot(str)
    def report_error(self,message):
        self.failed_handler(message)
    @Slot(str)
    def failed(self,message):
        self.window.jobs.discard(self.job)
        if self.busy: self.window.set_busy(False)
        self.window.error(message)
        self.deleteLater()

class Job(QRunnable):
    def __init__(self,fn):
        super().__init__(); self.fn=fn; self.signals=Signals()
    def run(self):
        try: self.signals.done.emit(self.fn())
        except Exception as e: self.signals.error.emit(str(e))

def label(text,size=None,bold=False,muted=False):
    w=QLabel(text); w.setTextFormat(Qt.PlainText);w.setWordWrap(True)
    if size:
        w.setStyleSheet(f"font-size:{round(size*1.24)}px; font-weight:{600 if bold else 400};")
    if muted: w.setObjectName("muted")
    return w

def button(text,fn,primary=False):
    b=QPushButton(text.replace("&", "&&")); b.clicked.connect(fn)
    if primary: b.setObjectName("primary")
    return b

def page_layout():
    w=QWidget(); layout=QVBoxLayout(w); layout.setContentsMargins(0,0,0,0); layout.setSpacing(14)
    return w,layout

# LAFA Desktop has six sections. Each holds tabs; the page names used by
# LAFA 0.1.x ("classroom", "exams", "homework"…) still work as routes.
PAGES=[("home","🏠"),("study","📘"),("library","📚"),("timor","🇹🇱"),("activities","🗓"),("oshelp","🧭")]
PAGE_INDEX={key:i for i,(key,_) in enumerate(PAGES)}
SECTIONS={key:key for key,_ in PAGES}
# section -> tab keys, in order
TABS={"study":["encyclopedia","lessons","subjects","practice","languages","digital","coding"],
      "library":["search","files","saved","sources","wikipedia","favourites","external"],
      "timor":["atlas","news","weather"],   # pages of the Timor-Leste encyclopedia (not tabs)
      "activities":["tasks","reminders","results"],
      "oshelp":["guides","access","computer"]}
# old page keys -> (section, tab)
ROUTES={"home":("home",None),"chat":("home",None),"classroom":("study","lessons"),"teachers":("study","subjects"),"exams":("study","practice"),
        "languages":("study","languages"),"coding":("study","coding"),"learn":("library","search"),"files":("library","files"),"hub":("library","external"),
        "culture":("timor","atlas"),"encyclopedia":("study","encyclopedia"),"atlas":("timor","atlas"),"live":("timor","weather"),"homework":("activities","tasks"),"reminders":("activities","reminders"),
        "report":("activities","results"),"os_help":("oshelp","guides")}
TITLE_KEYS={"home":"home","study":"menu_study","library":"menu_library","timor":"menu_timor","activities":"menu_activities","oshelp":"menu_oshelp"}
SUBTITLE_KEYS={"home":"sub_home","study":"sub_study","library":"sub_library","timor":"sub_timor","activities":"sub_activities","oshelp":"sub_oshelp"}
# Theme icons (Papirus / Eduka-Icons on Edukasaun OS); emoji only as a fallback.
NAV_ICONS={"home":["user-home","go-home"],"study":["applications-education","accessories-dictionary"],"library":["bookcase","folder-documents","system-file-manager"],
           "timor":[],"activities":["x-office-calendar","office-calendar","view-calendar"],"oshelp":["help-browser","system-help","help-contents"],
           "settings":["preferences-system","configure","settings-configure"],"about":["help-about","dialog-information"]}
START_PAGES=list(SECTION_KEYS)
# 0.2.1: each menu has its own SVG icon (lafa/assets/icons, shipped with Lafa).
SVG_ICONS={"home":"home","study":"book-open","library":"bookshelf","timor":"flag-tl","activities":"calendar-check","oshelp":"monitor-help",
           "settings":"settings","about":"info"}
LABEL_KEYS={"lesson":"label_lesson","file":"label_file","saved":"label_saved","internet":"label_internet","guide":"label_guide"}
LABEL_COLOURS={"lesson":"#0b7a55","file":"#3b5bdb","saved":"#8a5a00","internet":"#5f3dc4","guide":"#0b7285"}

STYLE_TEMPLATE = """
QWidget { color:@text; font-family:'Noto Sans','DejaVu Sans',sans-serif; font-size:13px; }
QMainWindow, QDialog {background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 @bg1,stop:1 @bg2);}
QWidget#root {background:transparent;}
QFrame#sidebar {background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 @glass_top,stop:1 @glass); border:1px solid @glass_border; border-radius:24px;}
QFrame#sidebar QLabel {background:transparent;}
QFrame#sidebar QScrollArea, QWidget#navbody {background:transparent; border:0;}
QLabel#navsection {color:@muted; padding:6px 12px 2px 12px; font-size:10px; font-weight:700; letter-spacing:1px;}
QFrame#sidebar QPushButton {color:@text; background:transparent; text-align:left; border:2px solid transparent; padding:6px 11px; border-radius:11px; font-size:13px;}
QFrame#sidebar QPushButton:hover {background:@accent_soft;}
QFrame#sidebar QPushButton:focus {border-color:@focus;}
QFrame#sidebar QPushButton:checked {background:@accent_soft; color:@accent_strong; font-weight:700;}
QFrame#sidebar QPushButton#sidesettings {border:1px solid @border; text-align:center;}
QFrame#sidebar QLineEdit#sidesearch {background:@surface2; border:1px solid @border; border-radius:12px; padding:7px 10px;}
QFrame#progresscard {background:@surface2; border:1px solid @border; border-radius:14px;}
QProgressBar {background:@border; border:0; border-radius:4px; height:8px; max-height:8px; text-align:center; color:transparent;}
QProgressBar::chunk {background:@accent; border-radius:4px;}
QFrame#topbar {background:transparent;}
QPushButton#segment {background:@surface; border:2px solid @border; border-radius:0; padding:7px 14px; color:@muted; font-weight:600;}
QPushButton#segfirst {background:@surface; border:2px solid @border; border-top-left-radius:14px; border-bottom-left-radius:14px; border-top-right-radius:0; border-bottom-right-radius:0; padding:7px 14px; color:@muted; font-weight:600;}
QPushButton#seglast {background:@surface; border:2px solid @border; border-top-right-radius:14px; border-bottom-right-radius:14px; border-top-left-radius:0; border-bottom-left-radius:0; padding:7px 14px; color:@muted; font-weight:600;}
QPushButton#segment:checked, QPushButton#segfirst:checked, QPushButton#seglast:checked {background:@accent_soft; color:@accent_strong; border-color:@accent;}
QPushButton#segment:focus, QPushButton#segfirst:focus, QPushButton#seglast:focus {border-color:@focus;}
QPushButton {background:@surface; border:2px solid @border; border-radius:11px; padding:7px 13px; color:@text;}
QPushButton:hover {background:@accent_soft; border-color:@accent;}
QPushButton:focus {border-color:@focus;}
QPushButton:disabled {color:@muted; background:@surface2;}
QPushButton#primary {background:@accent_button; color:@accent_text; border:2px solid @accent_button; font-weight:700;}
QPushButton#primary:hover {background:@accent_dark; border-color:@accent_dark;}
QPushButton#primary:focus {border-color:@focus; background:@accent_dark;}
QPushButton#primary:disabled {background:@border; border-color:@border; color:@muted;}
QPushButton#iconbutton {padding:0; border-radius:10px;}
QFrame#navbar QLabel#breadcrumb {font-size:13px; background:transparent;}
QLineEdit#contextsearch {border-radius:18px; padding:7px 12px;}
QFrame#enccard, QFrame#enctile, QFrame#encrow, QFrame#factcard, QFrame#contents {background:@surface; border:2px solid @border; border-radius:16px;}
QFrame#enccard:hover, QFrame#enctile:hover, QFrame#encrow:hover {border-color:@accent;}
QFrame#enccard:focus, QFrame#enctile:focus, QFrame#encrow:focus {border-color:@focus; background:@surface2;}
QFrame#enccard QLabel, QFrame#enctile QLabel, QFrame#encrow QLabel, QFrame#factcard QLabel, QFrame#contents QLabel {background:transparent;}
QLabel#cardtitle {font-size:15px; font-weight:700;}
QLabel#rowtitle {font-size:15px; font-weight:700;}
QLabel#rowwhen {color:@muted; font-size:12px; font-family:'DejaVu Sans Mono',monospace;}
QLabel#cardcaption {color:@muted; font-size:12px;}
QLabel#pagetitle {font-size:28px; font-weight:800;}
QLabel#articletitle {font-size:27px; font-weight:800;}
QLabel#pagesub, QLabel#articlesub {color:@muted; font-size:15px;}
QLabel#grouptitle {font-size:17px; font-weight:700; padding-top:8px;}
QLabel#icontile {background:@accent_soft; border-radius:16px;}
QLabel#factvalue {font-size:17px; font-weight:700; color:@accent_strong;}
QLabel#emptytext {color:@muted; font-size:14px;}
QLabel#badge_ok {background:@accent_soft; color:@accent_strong; padding:5px 11px; border-radius:12px; font-size:12px; font-weight:700;}
QLabel#badge_net {background:@warn_soft; color:@warn_text; padding:5px 11px; border-radius:12px; font-size:12px; font-weight:700;}
QLabel#badge_info {background:@surface2; color:@muted; padding:5px 11px; border-radius:12px; font-size:12px; font-weight:700;}
QPushButton#contentslink {text-align:left; border:2px solid transparent; background:transparent; padding:5px 8px; color:@text;}
QPushButton#contentslink:hover {background:@accent_soft;}
QPushButton#contentslink:focus {border-color:@focus;}
QLabel#quizquestion {font-size:19px; font-weight:700;}
QPushButton#answer {text-align:left; padding:10px 14px; font-size:14px;}
QPushButton#answer[state="right"] {background:@accent_soft; border-color:@accent; color:@text;}
QPushButton#answer[state="wrong"] {background:@warn_soft; border-color:@warn_text; color:@text;}
QLabel#feedback {font-size:14px;}
QTextBrowser#reader {background:@surface; border:2px solid @border; border-radius:16px; padding:4px;}
QPushButton#hotspot {background:@accent_button; color:white; border:3px solid white; border-radius:17px; font-weight:800; padding:0;}
QPushButton#hotspot:hover, QPushButton#hotspot[active="true"] {background:@accent_dark;}
QPushButton#hotspot:focus {border-color:@focus;}
QPushButton#timelinedot {background:@surface; border:3px solid @accent; border-radius:13px; padding:0;}
QPushButton#timelinedot[active="true"] {background:@accent_button; border-color:@accent_strong;}
QPushButton#timelinedot:focus {border-color:@focus;}
QPushButton#periodbutton {font-weight:700;}
QPushButton#periodbutton:checked {background:@accent_button; color:white; border-color:@accent_button;}
QComboBox[state="right"] {border-color:@accent;}
QComboBox[state="wrong"] {border-color:@warn_text;}
QListWidget#orderlist::item {padding:7px; border-bottom:1px solid @border;}
QListWidget#orderlist::item:selected {background:@accent_soft; color:@text;}
QPushButton#chip {background:@accent_soft; border:1px solid @border; border-radius:15px; padding:6px 12px; color:@text;}
QPushButton#filterchip {background:@surface; border:1px solid @border; border-radius:13px; padding:5px 12px; color:@text; font-size:12px;}
QPushButton#filterchip:checked {background:@accent; border-color:@accent; color:@accent_text;}
QPushButton#tilebutton {background:rgba(255,255,255,0.26); border:1px solid rgba(255,255,255,0.45); color:white; border-radius:10px; padding:5px 12px; font-weight:600;}
QPushButton#tilebutton:hover {background:rgba(255,255,255,0.4);}
QPushButton#roundbutton {background:transparent; border:0;}
QLabel#tiletitle {color:rgba(255,255,255,0.92); background:transparent; font-size:13px; font-weight:600;}
QLabel#tilevalue {color:white; background:transparent; font-size:24px; font-weight:800;}
QLabel#tilecaption {color:rgba(255,255,255,0.88); background:transparent; font-size:12px;}
QLabel#atlastitle {color:white; background:transparent; font-size:13px; font-weight:700;}
QLabel#atlaswhen {color:rgba(255,255,255,0.85); background:transparent; font-size:11px; font-family:'DejaVu Sans Mono',monospace;}
QLabel#atlassummary {color:rgba(255,255,255,0.9); background:transparent; font-size:11px;}
QFrame#card {background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 @glass_top,stop:1 @glass); border:1px solid @glass_border; border-radius:18px;}
QFrame#card:hover {border-color:@accent;}
QFrame#card QLabel {background:transparent;}
QFrame#panel, QFrame#inspector, QFrame#sourcecard {background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 @glass_top,stop:1 @glass); border:1px solid @glass_border; border-radius:18px;}
QFrame#sourcecard:hover {border-color:@accent;}
QLabel#sourcetitle {font-size:14px; font-weight:700; background:transparent;}
QLabel#sourcehost {color:@muted; font-size:11px; font-family:'DejaVu Sans Mono',monospace; background:transparent;}
QLabel#sourcedesc {font-size:12px; background:transparent;}
QLabel#sourcedot {background:transparent; font-size:14px;}
QFrame#panel QLabel, QFrame#inspector QLabel {background:transparent;}
QFrame#hero {background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 @glass_top,stop:1 @accent_soft); border:1px solid @glass_border; border-radius:22px;}
QFrame#hero QLabel {background:transparent;}
QFrame#bubble {background:@surface; border:1px solid @border; border-radius:14px;}
QFrame#userbubble {background:@accent_soft; border:1px solid @border; border-radius:14px;}
QLineEdit,QComboBox,QSpinBox,QDateEdit,QPlainTextEdit,QListWidget {background:@surface;border:1px solid @border;border-radius:11px;padding:7px;selection-background-color:@accent_soft;selection-color:@text;color:@text;}
QLineEdit:focus,QPlainTextEdit:focus,QComboBox:focus,QSpinBox:focus,QListWidget:focus,QTableWidget:focus {border-color:@focus;}
QCheckBox:focus {color:@accent_strong;}
QComboBox QAbstractItemView {background:@surface; color:@text; selection-background-color:@accent_soft;}
QListWidget#categories {background:transparent;border:0;padding:0;}
QListWidget#categories::item {padding:10px 12px;border-radius:10px;margin:2px 0;}
QListWidget#categories::item:selected {background:@accent;color:@accent_text;}
QListWidget#guides::item {padding:8px 6px;border-radius:8px;}
QListWidget#guides::item:selected {background:@accent_soft;color:@text;}
QLabel#muted {color:@muted;}
QLabel#badge {background:@accent_soft; color:@text; padding:6px 12px; border-radius:12px; font-size:11px; font-weight:700;}
QLabel#pill {background:@accent_soft; color:@text; padding:5px 10px; border-radius:10px; font-size:11px;}
QLabel#review {color:#9a5f14; background:#fff0d4;padding:5px 9px;border-radius:8px;font-size:10px;}
QLabel#categorybadge {color:white; padding:3px 9px; border-radius:9px; font-size:11px; font-weight:700;}
QLabel#livebox {background:@surface2; border:1px dashed @border; border-radius:12px; padding:9px; color:@text;}
QTableWidget {background:@surface;border:1px solid @border;border-radius:12px;gridline-color:@border;selection-background-color:@accent_soft;selection-color:@text;color:@text;}
QHeaderView::section {background:@surface2; border:0; padding:9px; color:@muted; font-weight:700;}
QTableWidget {alternate-background-color:@surface2;}
QScrollArea {border:0;background:transparent;}
QScrollArea > QWidget > QWidget {background:transparent;}
QStackedWidget > QWidget {background:transparent;}
QTabWidget::pane {background:transparent;border:0;}
QTabBar::tab {background:@surface; color:@muted; border:1px solid @border; padding:7px 14px; margin-right:4px; border-radius:11px;}
QTabBar::tab:selected {background:@accent_soft; color:@accent_strong; border-color:@accent;}
QTabBar::tab:focus {border-color:@focus;}
QCheckBox {spacing:8px;padding:3px;}
QMenu {background:@surface; border:1px solid @border; color:@text;}
QMenu::item {padding:8px 20px;}
QMenu::item:selected {background:@accent_soft;}
QToolTip {background:@surface; color:@text; border:1px solid @border;}
QScrollBar:vertical {background:transparent; width:10px; margin:4px 2px 4px 0;}
QScrollBar::handle:vertical {background:@scroll; border-radius:4px; min-height:36px;}
QScrollBar::handle:vertical:hover {background:@accent;}
QScrollBar:horizontal {background:transparent; height:10px; margin:0 4px 2px 4px;}
QScrollBar::handle:horizontal {background:@scroll; border-radius:4px; min-width:36px;}
QScrollBar::handle:horizontal:hover {background:@accent;}
QScrollBar::add-line, QScrollBar::sub-line {width:0; height:0; border:0;}
QScrollBar::add-page, QScrollBar::sub-page {background:transparent;}
"""

def build_style(tokens):
    qss = STYLE_TEMPLATE
    for name in sorted(tokens, key=len, reverse=True):
        if isinstance(tokens[name], str): qss = qss.replace("@" + name, tokens[name])
    return qss

STYLE = build_style(ui_kit.palette())

def shade(color,factor):
    """Lighter (>1) or darker (<1) #rrggbb colour."""
    r,g,b=(int(color[i:i+2],16) for i in (1,3,5))
    return '#'+''.join(f'{max(0,min(255,int(v*factor))):02x}' for v in (r,g,b))

def theme_tokens(settings):
    """Palette from the Eduka-Desktop theme (accent colour, light or dark)."""
    if not settings.follow_eduka_theme or not eduka.installed():return ui_kit.palette()
    info=eduka.theme();return ui_kit.palette(info['accent'],info['dark'])

def style_sheet(settings):
    """LAFA style that follows the Eduka-Desktop theme and accent colour."""
    if not settings.follow_eduka_theme or not eduka.installed():return STYLE
    return build_style(theme_tokens(settings))

class ClickCard(QFrame):
    """Word-wrapping clickable card for the Home dashboard."""
    def __init__(self,title,description,callback):
        super().__init__();self.setObjectName("card");self.callback=callback;self.setCursor(Qt.PointingHandCursor)
        layout=QVBoxLayout(self);layout.setContentsMargins(14,12,14,12);layout.setSpacing(4)
        self.heading=label(title,11,True);self.body=label(description,9,muted=True);layout.addWidget(self.heading);layout.addWidget(self.body);layout.addStretch()
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Preferred);self.setMinimumHeight(84)
    def mouseReleaseEvent(self,event):
        if event.button()==Qt.LeftButton:self.callback()

def ensure_icon_theme():
    """Use the desktop's icon theme; outside LXQt fall back to an installed one
    (Papirus is recommended by Edukasaun OS)."""
    paths=QIcon.themeSearchPaths()
    for folder in (str(Path.home()/'.local/share/icons'),'/usr/local/share/icons','/usr/share/icons'):
        if folder not in paths and Path(folder).is_dir():paths.append(folder)
    QIcon.setThemeSearchPaths(paths)
    if QIcon.themeName() and QIcon.themeName()!='hicolor':return
    for name in ('Papirus','Papirus-Light','breeze','Adwaita'):
        if Path('/usr/share/icons',name).is_dir():QIcon.setThemeName(name);return

def safe_web(url):
    parts=urlsplit(url)
    if parts.scheme!="https" or not parts.hostname or parts.username or parts.password:
        raise ValueError("Only HTTPS web links are supported.")
    return QDesktopServices.openUrl(QUrl(url))

# Stable key of a Timor-Leste school lesson (subject.title-in-English).
lesson_key = memory.school_key


def fit_small_screen(page):
    """Keep a tab usable at 1024×600 and with large text: long drop-down lists
    shrink to a short width, and a page taller or wider than the window scrolls."""
    for box in page.findChildren(QComboBox):
        box.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon);box.setMinimumContentsLength(10)
    if isinstance(page,Browser):return page   # it scrolls each of its pages itself (no nested scrolling)
    scroll=QScrollArea();scroll.setObjectName("tabscroll");scroll.setWidgetResizable(True);scroll.setFrameShape(QFrame.NoFrame)
    scroll.setWidget(page);return scroll

class QuickCard(QFrame):
    """A calm Home shortcut: theme icon, title, one line. Keyboard: Tab + Enter."""
    def __init__(self,icon,title,description,callback):
        super().__init__();self.setObjectName("quick");self.callback=callback;self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.StrongFocus);self.setAccessibleName(title);self.setAccessibleDescription(description)
        layout=QHBoxLayout(self);layout.setContentsMargins(14,12,14,12);layout.setSpacing(12)
        mark=QLabel();mark.setObjectName("quickicon")
        if isinstance(icon,QIcon) and not icon.isNull():mark.setPixmap(icon.pixmap(30,30))
        else:mark.setText(str(icon));mark.setStyleSheet("font-size:24px;")
        mark.setFixedWidth(36);layout.addWidget(mark,0,Qt.AlignTop)
        text=QVBoxLayout();text.setSpacing(2);self.heading=label(title,12,True);self.body=label(description,9,muted=True)
        text.addWidget(self.heading);text.addWidget(self.body);layout.addLayout(text,1)
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Preferred);self.setMinimumHeight(72)
    def mouseReleaseEvent(self,event):
        if event.button()==Qt.LeftButton:self.callback()
    def keyPressEvent(self,event):
        if event.key() in (Qt.Key_Return,Qt.Key_Enter,Qt.Key_Space):self.callback()
        else:super().keyPressEvent(event)

def theme_icon(names,fallback=""):
    for name in names:
        icon=QIcon.fromTheme(name)
        if not icon.isNull():return icon
    return fallback

class Window(QMainWindow):
    COMPACT_WIDTH=1100     # below this width the sidebar shows icons only
    def __init__(self,settings=None,review=False):
        super().__init__()
        self.settings=settings or Settings.load(); self.review=review
        self.atlas=Atlas(); self.voice=Voice(); self.pool=QThreadPool(self); self.pool.setMaxThreadCount(4)
        self.online=False; self.busy=False; self.probing=False; self.jobs=set(); self.history=[]
        self.settings_dialog=None;self.card_deck=CardDeck();self.news_inflight=False;self.last_local_news=time.monotonic();self.pending_mode=""
        self.news_items=[]; self.locations=[]; self.compact=None
        self.last_answer=""; self.current_files=[]; self.current_sources=[]; self.generation=0
        updates.apply()  # sources downloaded earlier (validated cache)
        self.agent=Agent(self.settings)
        ensure_icon_theme()
        # Review mode keeps homework, reminders and progress in a temporary folder, never the user's data.
        self.planner=school.Planner(tempfile.mkdtemp(prefix='lafa-review-') if review else None)
        self.reminders=Reminders(self.planner.folder);self.progress=Progress(self.planner.folder);self.focus_until=0
        self.teacher_history={};self.scores={}
        self.setWindowTitle("LAFA"); self.resize(1120,720); self.setMinimumSize(720,480)
        self.setWindowIcon(QIcon(self.atlas.pixmap("idle",128)))
        self.companion=Companion(self.atlas,self.settings)
        self.companion.open_requested.connect(self.reveal)
        self.companion.quit_requested.connect(self.exit_app)
        self.companion.user_request.connect(self.companion_request)
        self.companion.action_requested.connect(self.desktop_action)
        self.companion.read_requested.connect(self.speak_last)
        self.companion.settings_requested.connect(self.open_configuration)
        self.companion.source_requested.connect(self.open_web)
        self.companion.card_requested.connect(self.show_cultural_card)
        self.companion.outfit_requested.connect(self.change_outfit)
        self.companion.settings_changed.connect(self.save_quiet_preference)
        self.tray=None
        self.build_ui()
        self.reminder_timer=QTimer(self); self.reminder_timer.timeout.connect(self.poll_reminders); self.reminder_timer.start(1000)
        self.culture_timer=QTimer(self);self.culture_timer.timeout.connect(self.check_local_updates);self.culture_timer.start(60_000)
        # Validated source catalogue (data only), at most once per update_hours.
        self.update_timer=QTimer(self);self.update_timer.timeout.connect(self.check_updates);self.update_timer.start(30*60_000);self.updating=False
        if not review:
            self.setup_tray()
            # Only for the "internet sources" badge: local features never wait for it.
            self.probe_timer=QTimer(self); self.probe_timer.timeout.connect(self.probe); self.probe_timer.start(60_000)
            QTimer.singleShot(50,self.probe)
            QTimer.singleShot(1500,self.show_missed_reminders)
        else:
            self.set_online(True)
    def t(self,key): return tr(self.settings.locale,key)
    def page_title(self,key):
        if key in TITLE_KEYS:return self.t(TITLE_KEYS[key])
        section,tab=ROUTES.get(key,(key,None))
        return self.t("tab_"+tab) if tab else self.t(TITLE_KEYS.get(section,section))
    def nav_icon(self,key):
        """Lafa's own SVG icons (packaged; no icon theme needed)."""
        tok=getattr(self,"tokens",None) or theme_tokens(self.settings)
        return icons.icon(SVG_ICONS.get(key,"info"),tok["text"],tok["accent_strong"])
    # ------------------------------------------------------------------ shell
    def build_ui(self):
        self.tokens=theme_tokens(self.settings)
        # Links in labels, readers and modules use the accent colour, not the default blue.
        pal=self.palette();pal.setColor(QPalette.Link,QColor(self.tokens["accent_strong"]));pal.setColor(QPalette.LinkVisited,QColor(self.tokens["accent_strong"]));self.setPalette(pal)
        root=QWidget(); root.setObjectName("root"); root_layout=QHBoxLayout(root); root_layout.setContentsMargins(10,10,0,10); root_layout.setSpacing(0)
        # Sidebar: brand, the six sections, then Settings and About at the bottom.
        sidebar=QFrame(); sidebar.setObjectName("sidebar"); self.sidebar=sidebar
        side=QVBoxLayout(sidebar); side.setContentsMargins(10,14,10,12); side.setSpacing(4)
        brand=QHBoxLayout();brand.setSpacing(8);icon=QLabel();icon.setPixmap(self.atlas.pixmap("idle",40,self.settings.costume));icon.setAccessibleName("LAFA");brand.addWidget(icon)
        self.brand_name=label("Lafa",18,True);brand.addWidget(self.brand_name,1);side.addLayout(brand);side.addSpacing(8)
        self.nav=[]
        for index,(key,glyph) in enumerate(PAGES):
            b=button("",lambda checked=False,i=index:self.navigate(i));b.setCheckable(True);b.setObjectName("navbutton")
            ic=self.nav_icon(key)
            if not ic.isNull():b.setIcon(ic);b.setIconSize(QSize(22,22))
            b.setProperty("glyph",glyph if ic.isNull() else "");b.setProperty("full",self.page_title(key))
            b.setToolTip(self.page_title(key)+f"  (Alt+{index+1})");b.setAccessibleName(self.page_title(key))
            side.addWidget(b);self.nav.append(b)
            QShortcut(QKeySequence(f"Alt+{index+1}"),root,activated=lambda i=index:self.navigate(i))
        side.addStretch()
        self.settings_button=button("",self.open_configuration);self.settings_button.setObjectName("navbutton");self.settings_button.setProperty("full",self.t("settings"));self.settings_button.setProperty("glyph","⚙")
        self.settings_button.setToolTip(self.t("settings_in_eduka"));self.settings_button.setAccessibleName(self.t("settings"))
        self.settings_button.setIcon(self.nav_icon("settings"));self.settings_button.setIconSize(QSize(20,20));self.settings_button.setProperty("glyph","")
        self.about_button=button("",self.open_about);self.about_button.setObjectName("navbutton");self.about_button.setProperty("full",self.t("about"));self.about_button.setProperty("glyph","ℹ")
        self.about_button.setAccessibleName(self.t("about"))
        self.about_button.setIcon(self.nav_icon("about"));self.about_button.setIconSize(QSize(20,20));self.about_button.setProperty("glyph","")
        side.addWidget(self.settings_button);side.addWidget(self.about_button)
        root_layout.addWidget(sidebar)
        content=QWidget(); col=QVBoxLayout(content); col.setContentsMargins(18,4,18,4); col.setSpacing(10)
        # Top bar: page title, a calm connection note and status messages. No second menu.
        top=QHBoxLayout(); titlecol=QVBoxLayout(); titlecol.setSpacing(1); self.title=label(self.t("home"),19,True)
        self.subtitle=label("",10,muted=True)
        titlecol.addWidget(self.title); titlecol.addWidget(self.subtitle); top.addLayout(titlecol,1)
        self.badge=label(self.t("local_ready")); self.badge.setObjectName("badge"); self.badge.setAccessibleName(self.t("connection"));top.addWidget(self.badge,0,Qt.AlignVCenter)
        col.addLayout(top)
        if self.review:
            reviewlabel=label(self.t("review_banner"));reviewlabel.setObjectName("review"); col.addWidget(reviewlabel)
        elif not platform_check.is_edukasaun():
            preview=label(self.t("edukasaun_only")); preview.setObjectName("review"); col.addWidget(preview)
        self.stack=QStackedWidget();self.section_tabs={}
        builders={"home":self.build_home,"study":self.build_study,"library":self.build_library,"timor":self.build_timor,"activities":self.build_activities,"oshelp":self.build_oshelp}
        for key,_ in PAGES:self.stack.addWidget(builders[key]())
        col.addWidget(self.stack,1)
        self.chat_status=label("",9,muted=True);self.chat_status.setObjectName("status");self.chat_status.setAccessibleName(self.t("status"));col.addWidget(self.chat_status)
        root_layout.addWidget(content,1)
        self.setCentralWidget(root); self.apply_depth(); self.apply_compact(force=True)
        self.navigate(self.settings.start_page if not hasattr(self,'_built') else "home");self._built=True
    def apply_compact(self,force=False):
        """Small screens (1024×600, 125–150 % scaling): icon-only sidebar."""
        compact=self.width()<self.COMPACT_WIDTH
        if compact==self.compact and not force:return
        self.compact=compact;self.sidebar.setFixedWidth(64 if compact else 212);self.brand_name.setVisible(not compact)
        for b in self.nav+[self.settings_button,self.about_button]:
            full=b.property("full") or "";glyph=b.property("glyph") or ""
            b.setText((glyph or "") if compact else ("  "+(glyph+"  " if glyph else "")+full))
    def resizeEvent(self,event):
        super().resizeEvent(event)
        if hasattr(self,"sidebar"):self.apply_compact()
    def apply_depth(self):
        """Subtle shadows only when enabled; smooth scrolling everywhere."""
        dark=self.tokens["dark"];depth=self.settings.depth_effects
        for frame in self.centralWidget().findChildren(QFrame) if depth else []:
            if frame.objectName() in {"panel","quick","sidebar"} and frame.graphicsEffect() is None:ui_kit.soft_shadow(frame,14,3,18,dark)
        for area in self.centralWidget().findChildren(QScrollArea) if self.settings.smooth_scrolling else []:
            if not hasattr(area,"smooth_wheel"):ui_kit.smooth_scroll(area)
    def tabs(self,section,pages):
        """A section's tabs: [(tab key, widget)]."""
        tabs=QTabWidget();tabs.setDocumentMode(True);tabs.setObjectName("sectiontabs")
        for key,widget in pages:tabs.addTab(fit_small_screen(widget),self.t("tab_"+key).replace("&","&&"))
        tabs.setUsesScrollButtons(True);self.section_tabs[section]=tabs;return tabs
    def navigate(self,page,tab=None):
        """Open a section (or a 0.1.x page name, which is routed to its tab)."""
        if isinstance(page,int):key=PAGES[page][0]
        elif page in PAGE_INDEX:key=page
        else:key,tab=ROUTES.get(page,("home",None))[0],ROUTES.get(page,("home",None))[1] or tab
        self.stack.setCurrentIndex(PAGE_INDEX[key])
        if tab and key in self.section_tabs and tab in TABS.get(key,[]):self.section_tabs[key].setCurrentIndex(TABS[key].index(tab))
        if key=="timor" and tab in ("news","weather"):self.timor_browser.open_special(tab)
        elif key=="timor" and tab=="atlas" and self.timor_browser.state.get("kind")=="special":self.timor_browser.go({"kind":"home"})
        self.title.setText(self.page_title(key));self.subtitle.setText(self.t(SUBTITLE_KEYS[key]));self.update_header()
        for i,b in enumerate(self.nav):b.setChecked(i==PAGE_INDEX[key])
        if key=="home":self.refresh_home()
        if key=="activities":self.render_reminders()
    def current_section(self):return PAGES[self.stack.currentIndex()][0]
    def update_header(self,*_):
        """Encyclopedia pages carry their own big title and breadcrumb; the window
        title would only repeat it (and cost height on 1024×600 screens)."""
        key=self.current_section();tabs=self.section_tabs.get("study")
        own=key=="timor" or (key=="study" and tabs is not None and tabs.currentIndex()==TABS["study"].index("encyclopedia"))
        self.title.setVisible(not own);self.subtitle.setVisible(not own)
    # ------------------------------------------------------------------ home
    def build_home(self):
        w,layout=page_layout();scroll=QScrollArea();scroll.setWidgetResizable(True);scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        body=QWidget();col=QVBoxLayout(body);col.setContentsMargins(0,0,6,0);col.setSpacing(12)
        greet=QHBoxLayout();greet.setSpacing(10)
        self.home_face=QLabel();self.home_face.setPixmap(self.atlas.pixmap("idle",56,self.settings.costume));self.home_face.setAccessibleName("Lafa");greet.addWidget(self.home_face,0,Qt.AlignTop)
        hello=QVBoxLayout();hello.setSpacing(0);self.home_greeting=label("",15,True);self.home_date=label("",9,muted=True);hello.addWidget(self.home_greeting);hello.addWidget(self.home_date);greet.addLayout(hello,1)
        col.addLayout(greet)
        col.addWidget(self.build_search_panel("home"))
        grid=QGridLayout();grid.setSpacing(10);self.home_quick=[]
        quick=[("start_learning",["applications-education"],"📘",lambda:self.navigate("study","lessons"),"quick_learn_d"),
               ("find_knowledge",["system-search","edit-find"],"🔎",lambda:self.focus_search("home"),"quick_find_d"),
               ("tasks_schedule",["x-office-calendar","office-calendar"],"🗓",lambda:self.navigate("activities","tasks"),"quick_tasks_d"),
               ("os_help",["help-browser","system-help"],"🧭",lambda:self.navigate("oshelp","guides"),"quick_os_d")]
        for i,(key,names,glyph,callback,desc) in enumerate(quick):
            card=QuickCard(theme_icon(names,glyph),self.t(key),self.t(desc),callback);grid.addWidget(card,i//2,i%2);self.home_quick.append(card)
        self.home_grid=grid;col.addLayout(grid)
        row=QHBoxLayout();row.setSpacing(10)
        recent=QFrame();recent.setObjectName("panel");rv=QVBoxLayout(recent);rv.setContentsMargins(14,10,14,10)
        rv.addWidget(label(self.t("recent_material"),11,True));self.home_recent=label("",10);rv.addWidget(self.home_recent)
        self.continue_button=button(self.t("continue_learning"),self.continue_learning,True);rv.addWidget(self.continue_button,0,Qt.AlignLeft);rv.addStretch();row.addWidget(recent,1)
        nxt=QFrame();nxt.setObjectName("panel");nv=QVBoxLayout(nxt);nv.setContentsMargins(14,10,14,10)
        nv.addWidget(label(self.t("next_activity"),11,True));self.home_next=label("",10);nv.addWidget(self.home_next)
        nv.addWidget(button(self.t("menu_activities"),lambda:self.navigate("activities")),0,Qt.AlignLeft);nv.addStretch();row.addWidget(nxt,1)
        col.addLayout(row)
        self.home_virtual=label("",9,muted=True);col.addWidget(self.home_virtual);col.addStretch(1)
        scroll.setWidget(body);layout.addWidget(scroll,1)
        if hasattr(self,"progress"):self.refresh_home()
        return w
    def refresh_home(self):
        last=self.progress.last if hasattr(self,"progress") else None
        if hasattr(self,"companion"):self.companion.recommendation=self.t("popup_continue_with").format(t=last["title"]) if last else self.t("popup_recommend")
        if not hasattr(self,"home_greeting"):return
        from .mascot import greeting_key
        self.home_greeting.setText(self.t(greeting_key(time.localtime().tm_hour)))
        self.home_date.setText(datetime.now().strftime("%d/%m/%Y")+"  ·  "+self.today_text().split("\n")[0])
        last=self.progress.last
        self.home_recent.setText(last["title"] if last else self.t("no_recent"));self.continue_button.setVisible(bool(last))
        items=[]
        nxt=self.reminders.next()
        if nxt:items.append("⏰ "+datetime.fromtimestamp(nxt.due).strftime("%d/%m %H:%M")+" · "+nxt.text)
        for h in self.planner.due_soon(7)[:3]:items.append(f"📝 {h.due} · {self.subject_name(h.subject)} · {h.title}")
        classes=self.planner.today()
        if classes:items.append("🏫 "+" · ".join(classes))
        self.home_next.setText("\n".join(items) if items else self.t("nothing_planned"))
        # The Virtual Assistant is switched on in Eduka-Settings, never from here.
        self.home_virtual.setText(("🐊 "+self.t("virtual_on")) if self.settings.companion else self.t("virtual_where"))
        grid=self.home_grid;columns=1 if self.width()<900 else 2
        for i,card in enumerate(self.home_quick):grid.addWidget(card,i//columns,i%columns)
    def focus_search(self,name):
        self.navigate("home" if name=="home" else "library","search" if name!="home" else None)
        box=self.search_panels[name]["input"];box.setFocus();box.selectAll()
    def continue_learning(self):
        last=self.progress.last
        if last:self.open_target(last["key"])
    # --------------------------------------------------------------- search
    def build_search_panel(self,name):
        """The search box: lessons, knowledge and files — local first."""
        if not hasattr(self,"search_panels"):self.search_panels={}
        w=QWidget();v=QVBoxLayout(w);v.setContentsMargins(0,0,0,0);v.setSpacing(8)
        row=QHBoxLayout();box=QLineEdit();box.setObjectName("searchbig");box.setMaxLength(300);box.setPlaceholderText(self.t("search_box"))
        box.setAccessibleName(self.t("search_box"));box.returnPressed.connect(lambda:self.run_search(name))
        row.addWidget(box,1);go=button(self.t("find"),lambda:self.run_search(name),True);go.setAccessibleName(self.t("find"));row.addWidget(go);v.addLayout(row)
        results=QTextBrowser();results.setObjectName("results");results.setOpenLinks(False);results.document().setDefaultStyleSheet("a {color:%s;}"%("#7ee0bf" if self.tokens["dark"] else "#00704f"));results.anchorClicked.connect(lambda url,n=name:self.open_link(url,n))
        results.setAccessibleName(self.t("results"));results.setMinimumHeight(140 if name=="home" else 220);v.addWidget(results,1)
        actions_row=QHBoxLayout();internet=button("🌐  "+self.t("search_internet"),lambda:self.internet_search(name));internet.setToolTip(self.t("search_internet_note"))
        actions_row.addWidget(internet);note=label("",9,muted=True);actions_row.addWidget(note,1);v.addLayout(actions_row)
        self.search_panels[name]={"input":box,"results":results,"internet":internet,"note":note,"query":"","outcome":None,"wiki":[]}
        if name=="home":results.hide();internet.hide()
        else:results.setHtml(self.search_welcome())
        if name=="home":QShortcut(QKeySequence("Ctrl+F"),w,activated=lambda:self.focus_search("home"))
        return w
    def search_welcome(self):
        tips=" · ".join(html.escape(t) for t in self.t("search_examples").split("|"))
        return f"<div style='padding:12px'><p>{html.escape(self.t('search_intro'))}</p><p style='color:#5c7a70'>{tips}</p></div>"
    def run_search(self,name,text=None):
        panel=self.search_panels[name];box=panel["input"]
        text=(text if isinstance(text,str) else box.text()).strip()
        if not text:self.hint(box,self.t("type_first"));return
        box.setText(text);panel["query"]=text;panel["wiki"]=[];panel["results"].show()
        # Requests that *do* something (open an app or page, set a reminder).
        action=None if direct_intent(text) else actions.parse(text)
        if action and action.kind!="search":
            result=self.perform_action(action);self.show_message(name,result.text);return
        intent=direct_intent(text)
        if intent and intent.tool not in LOCAL_TOOLS|INTERNET_TOOLS:intent=None
        if intent and intent.tool in INTERNET_TOOLS and not self.online:
            self.show_message(name,self.t("needs_internet_calm"));return
        if intent:
            self.work(lambda:self.agent.execute(intent),lambda r,n=name:self.show_result(n,r));return
        query=action.text if action else text;roots=list(self.settings.roots);lang=self.settings.locale
        panel["note"].setText(self.t("searching"))
        self.work(lambda:search.search(query,lang,roots),lambda outcome,n=name:self.show_outcome(n,outcome))
    def show_message(self,name,text):
        panel=self.search_panels[name];panel["results"].show()
        panel["results"].setHtml(f"<div style='padding:10px;white-space:pre-wrap'>{html.escape(text)}</div>");panel["note"].setText("")
        self.last_answer=text
    def show_result(self,name,result):
        """A command's result (calculator, OS guide, weather, Wikipedia…)."""
        if result.reminder is not None:
            try:self.reminders.add(*result.reminder);self.render_reminders()
            except ValueError as error:result=Result(str(error),"serious")
        if result.weather is not None:self.show_weather(result.weather)
        if result.news is not None:
            if result.timor:self.show_timor_news(result.news)
            else:self.show_news(result.news)
        if result.guide is not None:self.show_guide(result.guide,navigate=False)
        self.show_message(name,result.text);self.set_mood(result.mood)
    def label_html(self,kind):
        return f"<span style='background:{LABEL_COLOURS[kind]};color:white;border-radius:6px;padding:1px 6px;font-size:11px'>&nbsp;{html.escape(self.t(LABEL_KEYS[kind]))}&nbsp;</span>"
    def item_link(self,item):
        if item.label=="file":return QUrl.fromLocalFile(item.target).toString()
        return item.target
    def fav_link(self,kind,key,title):
        star="★" if self.progress.is_favourite(kind,key) else "☆"
        return f"<a href='lafa://fav?kind={quote(kind)}&key={quote(key,safe='')}&title={quote(title[:150],safe='')}' style='text-decoration:none'>{star} {html.escape(self.t('favourite'))}</a>"
    def item_html(self,item):
        esc=html.escape;link=self.item_link(item)
        extra=""
        if item.label=="file":
            extra=f" · <a href='lafa://read?path={quote(item.target,safe='')}'>{esc(self.t('read'))}</a>"
        elif item.label in {"lesson","guide"}:extra=" · "+self.fav_link("lesson" if item.label=="lesson" else "guide",item.target,item.title)
        elif item.label in {"internet","saved"}:extra=" · "+self.fav_link("source" if item.label=="internet" else "saved",item.target,item.title)
        where=esc(item.source) if item.label!="file" else esc(item.detail)
        meta=""
        if item.label=="internet":
            m=source_meta.meta(item.target);access=self.t("access_"+m["access"])
            meta=f"<br><span style='color:#6b7f78;font-size:11px'>{esc(access)} · {esc(', '.join(m['langs']))}"+("" if m["academic"] else " · "+esc(self.t("not_academic")))+"</span>"
        detail="" if item.label=="file" else f"<br>{esc(item.detail)}"
        return (f"<div style='margin:0 0 12px 0'>{self.label_html(item.label)} <a href='{esc(link)}' style='font-weight:600;text-decoration:none'>{esc(item.title)}</a>"
                f"<br><span style='color:#6b7f78;font-size:11px'>{where}</span>{extra}{detail}{meta}</div>")
    def show_outcome(self,name,outcome):
        """Render a local search outcome with labelled results."""
        panel=self.search_panels[name];panel["outcome"]=outcome;panel["note"].setText("");esc=html.escape;q=esc(outcome.query)
        rows=[]
        if outcome.mode=="calc":
            rows.append(f"<h3>🧮 {q} = {esc(str(outcome.calc))}</h3>");self.last_answer=f"{outcome.query} = {outcome.calc}"
        elif outcome.mode=="guide":
            guide=outcome.guide;lang=self.settings.locale;self.show_guide(guide,navigate=False)
            steps="".join(f"<li>{esc(s)}</li>" for s in guide.steps.get(lang,guide.steps["en"]))
            rows.append(f"{self.label_html('guide')} <b>{esc(guide.icon+'  '+guide.title.get(lang,guide.title['en']))}</b><ol>{steps}</ol>"
                        f"<p><a href='lafa://os/{esc(guide.key)}'>{esc(self.t('open_guide'))}</a></p>")
            self.last_answer=guide.text(lang)
        elif outcome.mode=="files":
            rows.append(f"<p>{esc(self.t('files_found').replace('{n}',str(len(outcome.items))))}</p>" if outcome.items else f"<p>{esc(self.t('files_none').replace('{q}',outcome.query))}</p>")
            if not self.settings.roots:rows.append(f"<p>{esc(self.t('files_no_folders'))}</p>")
            rows+=[self.item_html(i) for i in outcome.items]
        elif outcome.mode=="answer":
            best=next(i for i in outcome.items if i.label!="internet")
            rows.append(f"<div style='border-left:4px solid {LABEL_COLOURS[best.label]};padding:4px 10px;margin-bottom:10px'>{self.label_html(best.label)}"
                        f" <a href='{esc(self.item_link(best))}' style='font-size:15px;font-weight:700;text-decoration:none'>{esc(best.title)}</a><br>{esc(best.detail)}"
                        f"<br><span style='color:#6b7f78;font-size:11px'>{esc(self.t('from_material'))}: {esc(best.source)}</span></div>")
            others=[i for i in outcome.items if i is not best]
            if others:rows.append(f"<p style='color:#6b7f78'>{esc(self.t('more_results'))}</p>")
            rows+=[self.item_html(i) for i in others[:12]]
            self.last_answer=best.title+". "+best.detail
        elif outcome.mode=="choices":
            rows.append(f"<p>{esc(self.t('search_choices').replace('{q}',outcome.query))}</p>")
            rows+=[self.item_html(i) for i in outcome.items[:14]]
        else:
            rows.append(f"<p>{esc(self.t('search_none').replace('{q}',outcome.query))}</p><ul><li>{esc(self.t('try_other_words'))}</li>"
                        f"<li><a href='lafa://go/study/lessons'>{esc(self.t('browse_lessons'))}</a></li><li>{esc(self.t('try_internet_button'))}</li></ul>")
        if outcome.limited:rows.append(f"<p style='color:#6b7f78'>{esc(self.t('limited'))}</p>")
        for source in panel["wiki"]:rows.append(self.wiki_html(source))
        panel["results"].setHtml("<div style='padding:6px 10px'>"+"".join(rows)+"</div>")
        panel["internet"].setVisible(True);panel["internet"].setEnabled(self.online)
        panel["note"].setText("" if self.online else self.t("internet_later"))
        self.set_mood("reading" if outcome.mode in {"answer","guide","files"} else "thinking")
    def internet_search(self,name):
        """Search Wikipedia — only when the learner presses the button."""
        panel=self.search_panels[name];query=search.topic_words(panel["query"] or panel["input"].text())
        if not query:self.hint(panel["input"],self.t("type_first"));return
        if not self.online:panel["note"].setText(self.t("needs_internet_calm"));return
        if self.review:panel["note"].setText(self.t("preview_only"));return
        panel["note"].setText(self.t("searching_internet"));panel["internet"].setEnabled(False);lang=self.settings.locale
        def done(found,n=name):
            p=self.search_panels[n];p["internet"].setEnabled(self.online);p["wiki"]=found or [];p["note"].setText("" if found else self.t("no_public_results"))
            if p["outcome"] is not None:self.show_outcome(n,p["outcome"])
            else:p["results"].setHtml("<div style='padding:6px 10px'>"+"".join(self.wiki_html(s) for s in p["wiki"])+"</div>")
        job=Job(lambda:encyclopedia_search(query,lang));self.jobs.add(job);delivery=Delivery(self,job,done,False);job.signals.done.connect(delivery.done)
        def failed(message,n=name):
            p=self.search_panels[n];p["internet"].setEnabled(self.online);p["note"].setText(self.t("internet_failed"));self.jobs.discard(job);delivery.deleteLater()
        delivery.failed_handler=failed;job.signals.error.connect(delivery.report_error);self.pool.start(job)
    def wiki_html(self,source):
        esc=html.escape;url=esc(source.url)
        return (f"<div style='margin:0 0 12px 0'>{self.label_html('internet')} <a href='{url}' style='font-weight:600;text-decoration:none'>{esc(source.title)}</a>"
                f"<br><span style='color:#6b7f78;font-size:11px'>Wikipedia · {esc(urlsplit(source.url).hostname or '')}</span><br>{esc(source.text)}"
                f"<br><a href='lafa://extract?url={quote(source.url,safe='')}&title={quote(source.title,safe='')}'>{esc(self.t('show_extract'))}</a> · <a href='{url}'>{esc(self.t('open_browser'))}</a></div>")
    def open_link(self,url,panel=None):
        value=url.toString()
        if value.startswith("file://"):self.open_local(unquote(url.toLocalFile()));return
        self.open_target(value,panel)
    def open_target(self,value,panel=None):
        """Open a search result or a saved favourite."""
        if value.startswith("https://"):self.open_web(value);return
        if value.startswith("/"):self.open_local(value);return
        parts=urlsplit(value);args={k:v[0] for k,v in parse_qs(parts.query).items()};path=[unquote(p) for p in parts.path.strip("/").split("/") if p]
        host=parts.netloc
        if host=="fav":
            try:state=self.progress.toggle_favourite(args.get("kind",""),args.get("key",""),args.get("title",""))
            except ValueError as error:self.error(str(error));return
            self.chat_status.setText(self.t("favourite_added" if state else "favourite_removed"));self.render_favourites()
            if panel and self.search_panels[panel]["outcome"] is not None:self.show_outcome(panel,self.search_panels[panel]["outcome"])
            return
        if host=="read":self.read_path(args.get("path",""));return
        if host=="extract":self.show_extract(args.get("url",""),args.get("title",""));return
        if host=="go":self.navigate(path[0] if path else "home",path[1] if len(path)>1 else None);return
        if host=="lesson" or host=="classroom":self.open_lesson_target(host,path);return
        if host=="atlas":
            if path and enc.get("atlas:"+path[0]):self.open_article("atlas:"+path[0])
            else:self.navigate("timor","atlas")
            return
        if host=="article":
            if path and enc.get(path[0]):self.open_article(path[0])
            return
        if host=="os":
            guide=osguide.BY_KEY.get(path[0]) if path else None
            if guide:self.show_guide(guide)
            else:self.navigate("oshelp","guides")
    def open_lesson_target(self,host,path):
        """lafa://lesson/age/<id>, lafa://lesson/school/<n> (and 0.1.x lafa://classroom/…)."""
        self.navigate("study","lessons")
        if host=="classroom":path=["age",f"{path[0]}.{path[1]}"] if len(path)>=2 else ["school",path[0] if path else ""]
        if len(path)<2:return
        if path[0]=="age":
            lesson=curriculum.lesson(path[1])
            if not lesson:return
            self.age_level.setCurrentIndex(max(0,self.age_level.findData(lesson.level)));self.class_subject.setCurrentIndex(max(0,self.class_subject.findData(lesson.subject)))
            row=next((i for i,l in enumerate(self.class_lessons) if getattr(l,"id","")==lesson.id),0);self.lesson_list.setCurrentRow(row)
        elif path[0]=="school":
            self.age_level.setCurrentIndex(0);self.class_subject.setCurrentIndex(0)
            try:index=int(path[1])
            except ValueError:
                index=next((i for i,l in enumerate(self.class_lessons) if lesson_key(l)==path[1]),0)
            if 0<=index<len(self.class_lessons):self.lesson_list.setCurrentRow(index)
        self.show_lesson()  # opened from a search result or "continue": it counts as opened
    def open_local(self,path):
        """Open a local file found by the search (inside the chosen folders only)."""
        search_=FileSearch(self.settings.roots)
        if not path or not search_.allowed(path):self.error(self.t("outside_folders"));return
        if not QDesktopServices.openUrl(QUrl.fromLocalFile(path)):self.error(self.t("no_app_for_file"))
    def read_path(self,path):
        if self.busy:return
        if not path or not FileSearch(self.settings.roots).allowed(path):self.error(self.t("outside_folders"));return
        self.set_busy(True,"reading");name=Path(path).name
        self.work(lambda:FileSearch(self.settings.roots).read(path),lambda text:self.show_document(name,text),busy=True)
    def show_extract(self,url,title):
        """A Wikipedia extract, clearly labelled (not Lafa's own explanation)."""
        if not url.startswith("https://"):return
        if not self.online:self.chat_status.setText(self.t("needs_internet_calm"));return
        source=Source(title or url,url,"")
        self.set_busy(True,"reading")
        def show(text):
            self.set_busy(False);self.show_document(f"{self.t('article_extract')} · {source.title}",text,public=True,url=url)
        self.work(lambda:encyclopedia_article(source),show,busy=True)
    # ------------------------------------------------------------- sections
    def build_study(self):
        page,outer=page_layout()
        self.world_browser=Browser(self,"world")
        pages=[("encyclopedia",self.world_browser),("lessons",self.build_classroom()),("subjects",self.build_teachers()),("practice",self.build_exams()),("languages",self.build_languages()),
               ("digital",self.build_digital()),("coding",self.build_coding())]
        outer.addWidget(self.tabs("study",pages),1);self.section_tabs["study"].currentChanged.connect(self.update_header)
        if self.settings.entertainment:
            # Optional entertainment: LAFA's roles and the mind reader.
            fun=QWidget();fv=QVBoxLayout(fun);self.build_roles_panel(fv);fv.addStretch();self.section_tabs["study"].addTab(fun,self.t("tab_fun"))
        return page
    def build_library(self):
        page,outer=page_layout()
        pages=[("search",self.build_search_panel("library")),("files",self.build_files()),("saved",self.build_saved()),("sources",self.build_sources()),
               ("wikipedia",self.build_learn()),("favourites",self.build_favourites()),("external",self.build_external())]
        tabs=self.tabs("library",pages);self.library_tabs=tabs;outer.addWidget(tabs,1)
        tabs.currentChanged.connect(lambda i:self.on_library_tab(TABS["library"][i]))
        return page
    def on_library_tab(self,key):
        if key=="sources":QTimer.singleShot(400,lambda:self.check_sources(False))
        if key=="saved":self.render_saved()
        if key=="favourites":self.render_favourites()
    def build_timor(self):
        page,outer=page_layout()
        # Timor-Leste is an encyclopedia: six illustrated categories → topics → article,
        # with News and Weather as separate pages marked "needs internet".
        self.timor_browser=Browser(self,"timor");self.timor_browser.preload_specials();outer.addWidget(self.timor_browser,1);return page
    def build_activities(self):
        page,outer=page_layout()
        pages=[("tasks",self.build_homework()),("reminders",self.build_reminders()),("results",self.build_report())]
        outer.addWidget(self.tabs("activities",pages),1);return page
    def build_oshelp(self):
        page,outer=page_layout()
        pages=[("guides",self.build_os()),("access",self.build_access()),("computer",self.build_computer())]
        outer.addWidget(self.tabs("oshelp",pages),1);return page
    # ------------------------------------------------------- digital literacy
    def build_digital(self):
        """Digital literacy: computers, the internet and safe use (local lessons)."""
        w,layout=page_layout();layout.addWidget(label(self.t("digital_intro"),10,muted=True))
        self.digital_list=QListWidget();self.digital_list.setObjectName("guides");self.digital_list.setWordWrap(True);lang=self.settings.locale
        for subject in ("computers","it","communication"):
            for lesson in curriculum.lessons(subject):
                item=QListWidgetItem(f"{curriculum.subject_name(subject,lang)} · {curriculum.level_name(lesson.level,lang).split(' · ')[0]} · {curriculum.text(lesson.title,lang)}")
                item.setData(Qt.UserRole,"lafa://lesson/age/"+lesson.id);self.digital_list.addItem(item)
        for i,lesson in enumerate(classroom.lessons("ict")):
            item=QListWidgetItem(f"{classroom.subject_name('ict',lang)} · {classroom.text(lesson.title,lang)}");item.setData(Qt.UserRole,"lafa://lesson/school/"+lesson_key(lesson));self.digital_list.addItem(item)
        self.digital_list.itemActivated.connect(lambda item:self.open_target(item.data(Qt.UserRole)))
        layout.addWidget(self.digital_list,1)
        row=QHBoxLayout();row.addWidget(button(self.t("open"),lambda:self.digital_list.currentItem() and self.open_target(self.digital_list.currentItem().data(Qt.UserRole)),True))
        row.addWidget(button(self.t("menu_oshelp"),lambda:self.navigate("oshelp")));row.addStretch();layout.addLayout(row);return w
    # ------------------------------------------------------------ library
    def build_saved(self):
        """Material saved for offline use (Wikipedia extracts, source pages)."""
        w,layout=page_layout();layout.addWidget(label(self.t("saved_intro"),10,muted=True))
        self.saved_list=QListWidget();self.saved_list.setObjectName("guides");self.saved_list.setWordWrap(True);self.saved_list.itemActivated.connect(self.open_saved);layout.addWidget(self.saved_list,1)
        row=QHBoxLayout();row.addWidget(button(self.t("open"),lambda:self.saved_list.currentItem() and self.open_saved(self.saved_list.currentItem()),True))
        self.saved_update=button("⟳  "+self.t("update_saved"),self.update_saved);row.addWidget(self.saved_update);row.addWidget(button(self.t("delete"),self.delete_saved))
        self.saved_status=label("",9,muted=True);row.addWidget(self.saved_status,1);layout.addLayout(row);self.render_saved();return w
    def render_saved(self):
        if not hasattr(self,"saved_list"):return
        self.saved_list.clear();docs=sorted(memory.shared().web.values(),key=lambda d:d.fetched,reverse=True)
        for doc in docs:
            when=datetime.fromtimestamp(doc.fetched).strftime("%d/%m/%Y") if doc.fetched else "—"
            item=QListWidgetItem(f"{doc.title}\n{doc.site} · {self.t('saved_on')} {when} · {urlsplit(doc.url).hostname or ''}");item.setData(Qt.UserRole,doc.url);self.saved_list.addItem(item)
        stats=memory.shared().stats();self.saved_status.setText(self.t("saved_count").replace("{n}",str(stats["pages"])) if docs else self.t("saved_none"))
    def open_saved(self,item):
        doc=memory.shared().web.get(item.data(Qt.UserRole))
        if doc:
            when=datetime.fromtimestamp(doc.fetched).strftime("%d/%m/%Y %H:%M") if doc.fetched else "—"
            self.show_document(doc.title,f"{doc.site} · {doc.url}\n{self.t('saved_on')} {when} · {self.t('cache_label')}\n\n{doc.text}",public=True,url=doc.url,saved=True)
    def delete_saved(self):
        item=self.saved_list.currentItem()
        if not item:self.hint(self.saved_list,self.t("choose_first"));return
        store=memory.shared()
        with store.lock:store.web.pop(item.data(Qt.UserRole),None);store._indexes={}
        try:store.save()
        except OSError as error:self.error(str(error))
        self.render_saved()
    def update_saved(self):
        """Update saved source pages (only those the learner saved)."""
        if not self.online:self.saved_status.setText(self.t("needs_internet_calm"));return
        if self.review:self.saved_status.setText(self.t("preview_only"));return
        self.saved_update.setEnabled(False);self.saved_status.setText(self.t("working"))
        def done(result):self.saved_update.setEnabled(True);self.render_saved();self.saved_status.setText(self.saved_status.text()+" · "+self.t("memory_done").replace("{sites}",str(result[0])).replace("{pages}",str(result[1])).replace("{failed}",str(result[2])))
        job=Job(lambda:memory.refresh(max_age_hours=1));self.jobs.add(job);delivery=Delivery(self,job,done,False);job.signals.done.connect(delivery.done)
        def failed(message):self.saved_update.setEnabled(True);self.jobs.discard(job);self.saved_status.setText(self.t("internet_failed"));delivery.deleteLater()
        delivery.failed_handler=failed;job.signals.error.connect(delivery.report_error);self.pool.start(job)
    def save_source_offline(self,url):
        """Save one source's front page and news feed (when the learner asks)."""
        item=next((s for s in sources.SOURCES if s[2]==url),None)
        if not item or memory.skip_host(url):self.chat_status.setText(self.t("cannot_save"));return
        if not self.online:self.chat_status.setText(self.t("needs_internet_calm"));return
        if self.review:self.chat_status.setText(self.t("preview_only"));return
        self.chat_status.setText(self.t("working"))
        def done(result):self.chat_status.setText(self.t("saved_offline") if result[1] else self.t("cannot_save"));self.render_saved()
        job=Job(lambda:memory.refresh(items=[item],max_age_hours=0,budget=1));self.jobs.add(job);delivery=Delivery(self,job,done,False);job.signals.done.connect(delivery.done)
        def failed(message):self.jobs.discard(job);self.chat_status.setText(self.t("internet_failed"));delivery.deleteLater()
        delivery.failed_handler=failed;job.signals.error.connect(delivery.report_error);self.pool.start(job)
    def build_favourites(self):
        w,layout=page_layout();layout.addWidget(label(self.t("favourites_intro"),10,muted=True))
        self.favourite_list=QListWidget();self.favourite_list.setObjectName("guides");self.favourite_list.setWordWrap(True)
        self.favourite_list.itemActivated.connect(lambda item:self.open_target(item.data(Qt.UserRole)));layout.addWidget(self.favourite_list,1)
        row=QHBoxLayout();row.addWidget(button(self.t("open"),lambda:self.favourite_list.currentItem() and self.open_target(self.favourite_list.currentItem().data(Qt.UserRole)),True))
        row.addWidget(button(self.t("remove_favourite"),self.remove_favourite));row.addStretch();layout.addLayout(row);self.render_favourites();return w
    def render_favourites(self):
        if not hasattr(self,"favourite_list"):return
        self.favourite_list.clear();icons={"lesson":"📗","guide":"🧭","source":"🌐","saved":"💾","atlas":"🇹🇱"}
        for entry in self.progress.favourites:
            item=QListWidgetItem(f"{icons.get(entry['kind'],'★')}  {entry['title']}");item.setData(Qt.UserRole,entry["key"]);item.setData(Qt.UserRole+1,entry["kind"]);self.favourite_list.addItem(item)
        if not self.progress.favourites:self.favourite_list.addItem(QListWidgetItem(self.t("no_favourites")))
    def remove_favourite(self):
        item=self.favourite_list.currentItem()
        if not item or not item.data(Qt.UserRole):self.hint(self.favourite_list,self.t("choose_first"));return
        self.progress.toggle_favourite(item.data(Qt.UserRole+1),item.data(Qt.UserRole),item.text());self.render_favourites()
    def build_external(self):
        """External sites: open in the web browser. No login inside LAFA."""
        w,layout=page_layout();scroll=QScrollArea();scroll.setWidgetResizable(True);body=QWidget();v=QVBoxLayout(body);v.setSpacing(10)
        v.addWidget(label(self.t("external_intro"),10,muted=True))
        kiwix=QFrame();kiwix.setObjectName("panel");kv=QVBoxLayout(kiwix);kv.setContentsMargins(14,10,14,10);kv.addWidget(label("📦  Kiwix · "+self.t("kiwix_title"),12,True))
        tool=shutil.which("kiwix-desktop")
        kv.addWidget(label(self.t("kiwix_ready") if tool else self.t("kiwix_missing"),10,muted=True))
        if tool:kv.addWidget(button(self.t("open"),lambda:self.launch(tool),True),0,Qt.AlignLeft)
        v.addWidget(kiwix)
        v.addWidget(label(self.t("references"),12,True));grid=QGridLayout()
        for i,(name,url) in enumerate(RESOURCES):grid.addWidget(button(name,lambda checked=False,u=url:self.open_web(u)),i//3,i%3)
        v.addLayout(grid)
        ai=QFrame();ai.setObjectName("panel");av=QVBoxLayout(ai);av.setContentsMargins(14,10,14,10)
        av.addWidget(label(self.t("ai_links_title"),12,True));av.addWidget(label(self.t("ai_links_note"),9,muted=True))
        row=QHBoxLayout()
        for name,url in AI_LINKS:
            b=button(f"{name} · {self.t('open_in_browser')}",lambda checked=False,u=url:self.open_web(u));b.setToolTip(url);b.setProperty("ai_link",url);row.addWidget(b)
        row.addStretch();av.addLayout(row);v.addWidget(ai)
        v.addWidget(label(self.t("community_title"),12,True));v.addWidget(label(self.t("community_note"),9,muted=True))
        lang="id" if self.settings.locale in ("id","tet") else "en"
        for name,url,note_en,note_id in source_meta.COMMUNITY_RESOURCES:
            row=QHBoxLayout();row.addWidget(button(name,lambda checked=False,u=url:self.open_web(u)));row.addWidget(label(note_id if lang=="id" else note_en,9,muted=True),1);v.addLayout(row)
        v.addStretch();scroll.setWidget(body);layout.addWidget(scroll,1);return w
    def launch(self,path,args=None):
        """Start an installed program (fixed path, no shell)."""
        if self.review:self.chat_status.setText(self.t("preview_only"));return False
        ok=started(QProcess.startDetached(path,list(args or [])))
        self.chat_status.setText(self.t("opening" if ok else "open_failed").replace("{name}",Path(path).name));return ok
    # ------------------------------------------------------------ OS help
    def build_access(self):
        """Accessibility: tools that are installed, and how to get the others."""
        w,layout=page_layout();layout.addWidget(label(self.t("access_intro"),10,muted=True))
        tools=[("screen_reader","orca",["orca"],"sudo apt install orca"),("onscreen_keyboard","onboard",["onboard","florence"],"sudo apt install onboard"),
               ("magnifier","kmag",["kmag","magnus","xzoom"],"sudo apt install kmag"),("text_size","lxqt-config-appearance",["lxqt-config-appearance","eduka-settings"],"Eduka-Settings → Appearance")]
        for key,_,names,hint in tools:
            frame=QFrame();frame.setObjectName("panel");row=QHBoxLayout(frame);row.setContentsMargins(14,8,14,8)
            path=next((shutil.which(n) for n in names if shutil.which(n)),None)
            row.addWidget(label(self.t(key),11,True),1);row.addWidget(label(self.t("installed") if path else self.t("not_installed")+" · "+hint,9,muted=True),1)
            b=button(self.t("open"),lambda checked=False,p=path:self.launch(p) if p else None);b.setEnabled(bool(path));row.addWidget(b);layout.addWidget(frame)
        layout.addWidget(label(self.t("access_tips"),10));layout.addStretch();return w
    def build_computer(self):
        """Computer check (read-only) and apps LAFA can open."""
        w,layout=page_layout();panel=QFrame();panel.setObjectName("panel");v=QVBoxLayout(panel);v.setContentsMargins(16,12,16,12)
        v.addWidget(label("🩺  "+self.t("syscheck"),12,True));self.os_system=label("",10);v.addWidget(self.os_system);v.addWidget(button(self.t("refresh_check"),self.refresh_system),0,Qt.AlignLeft)
        layout.addWidget(panel);layout.addWidget(label(self.t("apps_title"),12,True));grid=QGridLayout()
        for i,app in enumerate(actions.APPS):
            path=actions.which_app(app);b=button(f"{app.icon}  {self.t('app_'+app.key)}",lambda checked=False,p=path:self.launch(p) if p else None)
            b.setEnabled(bool(path));b.setToolTip(path or self.t("not_installed"));grid.addWidget(b,i//3,i%3)
        layout.addLayout(grid);layout.addWidget(label(self.t("updates_via_eus"),9,muted=True));layout.addStretch();self.refresh_system();return w
    # ------------------------------------------------------------- kept pages
    def build_roles_panel(self,col):
        col.addWidget(label(self.t("roles"),13,True));col.addWidget(label(self.t("roles_sub"),10,muted=True))
        panel=QFrame();panel.setObjectName("panel");row=QHBoxLayout(panel);row.setContentsMargins(14,10,14,10)
        self.role_pet=Character(self.atlas,size=118);self.role_pet.costume=self.settings.costume;self.role_pet.set_state("lecture");row.addWidget(self.role_pet)
        right=QVBoxLayout();buttons=QGridLayout();buttons.setSpacing(8);self.role_buttons={}
        for i,role in enumerate(roles.ORDER):
            b=button(roles.text(roles.ROLES[role][2],self.settings.locale),lambda checked=False,r=role:self.play_role(r));b.setObjectName("chip");b.setToolTip(roles.text(roles.ROLES[role][3],self.settings.locale))
            for name in roles.ROLES[role][1]:
                icon=QIcon.fromTheme(name)
                if not icon.isNull():b.setIcon(icon);break
            buttons.addWidget(b,i//4,i%4);self.role_buttons[role]=b
        right.addLayout(buttons);self.role_text=label("",12);self.role_text.setMinimumHeight(48);right.addWidget(self.role_text)
        self.mind_button=button(self.t("mind_reader"),self.open_mind_reader);self.mind_button.hide();right.addWidget(self.mind_button,0,Qt.AlignLeft)
        row.addLayout(right,1);col.addWidget(panel);self.role_text.setText(roles.text(roles.ROLES["teacher"][3],self.settings.locale))
    def play_role(self,role):
        """LAFA switches into a role here and, when visible, on the desktop too."""
        if not hasattr(self,"role_pet"):self.companion.play_role(role);return
        self.role_pet.set_state(roles.ROLES[role][0]);self.role_pet.hop();self.role_text.setText(roles.line(role,self.settings.locale))
        self.mind_button.setVisible(role=="magician")
        if role=="teacher":self.role_text.setText(self.role_text.text()+"\n→ "+self.t("classroom"))
    def open_mind_reader(self):
        dialog=QDialog(self);dialog.setWindowTitle("LAFA · "+self.t("mind_reader"));v=QVBoxLayout(dialog);reader=roles.MindReader();chosen=[];step=[0]
        intro=label(self.t("mind_intro"),11);v.addWidget(intro);title=label("",12,True);v.addWidget(title);numbers=label("",13);numbers.setStyleSheet("font-family:'DejaVu Sans Mono',monospace;font-size:15px;");v.addWidget(numbers)
        row=QHBoxLayout();yes=button(self.t("yes"),lambda:answer(True),True);no=button(self.t("no"),lambda:answer(False));row.addWidget(yes);row.addWidget(no);v.addLayout(row)
        def show():
            if step[0]>=reader.CARDS:
                title.setText(self.t("mind_result").replace("{n}",str(reader.guess(chosen))));numbers.setText("");yes.hide();no.hide();return
            title.setText(self.t("mind_question").replace("{n}",str(step[0]+1)))
            values=reader.card(step[0]);numbers.setText("\n".join("  ".join(f"{n:2d}" for n in values[i:i+8]) for i in range(0,len(values),8)))
        def answer(present):
            if present:chosen.append(step[0])
            step[0]+=1;show()
        dialog.mind_answer=answer;self.mind_dialog=dialog;show();dialog.resize(460,360);dialog.show()
    # ------------------------------------------------------- language school
    def build_languages(self):
        w,layout=page_layout();row=QHBoxLayout();row.setSpacing(14);lang=self.settings.locale
        left=QFrame();left.setObjectName("panel");left.setFixedWidth(250);lv=QVBoxLayout(left);lv.setContentsMargins(12,12,12,12)
        lv.addWidget(label(self.t("choose_language"),10,True));lv.addWidget(label(self.t("phrases_note"),9,muted=True));self.course_list=QListWidget();self.course_list.setObjectName("guides");self.course_list.setWordWrap(True);self.course_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        for code,(name,_,region,_) in languages.COURSES.items():
            item=QListWidgetItem(f"{languages.text(name,lang)}  ·  {languages.text(languages.REGIONS[region],lang)}");item.setData(Qt.UserRole,code);self.course_list.addItem(item)
        lv.addWidget(self.course_list,1);lv.addWidget(label(self.t("continue_online"),9,True))
        links=QGridLayout();links.setSpacing(6);by_name={s[1]:s[2] for s in sources.SOURCES}
        for i,name in enumerate(languages.ONLINE_COURSES):
            b=ui_kit.chip(name,checkable=False);b.clicked.connect(lambda checked=False,u=by_name.get(name,""):self.open_web(u));links.addWidget(b,i//2,i%2)
        lv.addLayout(links);row.addWidget(left)
        right=QVBoxLayout();right.setSpacing(12)
        head=QFrame();head.setObjectName("hero");hl=QHBoxLayout(head);hl.setContentsMargins(14,8,18,8)
        self.course_pet=Character(self.atlas,size=96);self.course_pet.costume=self.settings.costume;self.course_pet.set_state("lecture");hl.addWidget(self.course_pet)
        hv=QVBoxLayout();self.course_title=label("",18,True);hv.addWidget(self.course_title);hv.addWidget(label(self.t("course_intro"),10,muted=True));hl.addLayout(hv,1);right.addWidget(head)
        self.course_units=QTabWidget();self.course_tables={}
        for key,name,_ in languages.UNITS:
            t=QTableWidget(0,3);t.setHorizontalHeaderLabels([self.t("meaning"),self.t("phrase"),self.t("pronunciation")]);t.verticalHeader().hide();t.setEditTriggers(QTableWidget.NoEditTriggers);t.setSelectionBehavior(QTableWidget.SelectRows)
            t.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch);t.setShowGrid(False);t.setAlternatingRowColors(True);t.cellDoubleClicked.connect(lambda r,c,k=key:self.say_phrase(k,r));self.course_tables[key]=t;self.course_units.addTab(t,languages.text(name,lang))
        right.addWidget(self.course_units,1)
        quiz=QFrame();quiz.setObjectName("panel");qv=QVBoxLayout(quiz);qv.setContentsMargins(16,12,16,12)
        top=QHBoxLayout();top.addWidget(label(self.t("language_quiz"),12,True),1);self.lang_score=label("",10,muted=True);top.addWidget(self.lang_score);top.addWidget(button("🔊 "+self.t("speak"),self.say_selected));qv.addLayout(top)
        self.lang_question=label("",18,True);self.lang_say=label("",10,muted=True);qv.addWidget(self.lang_question);qv.addWidget(self.lang_say)
        grid=QGridLayout();self.lang_buttons=[]
        for i in range(4):
            b=button("",lambda checked=False,i=i:self.answer_language(i));b.setMinimumHeight(40);grid.addWidget(b,i//2,i%2);self.lang_buttons.append(b)
        qv.addLayout(grid);self.lang_feedback=label("",11);qv.addWidget(self.lang_feedback);right.addWidget(quiz)
        row.addLayout(right,1);layout.addLayout(row,1)
        self.course_list.currentRowChanged.connect(self.show_course);self.course_list.setCurrentRow(0);return w
    def current_course(self):
        item=self.course_list.currentItem();return item.data(Qt.UserRole) if item else "tet"
    def show_course(self,*_):
        code=self.current_course();lang=self.settings.locale;self.course_title.setText(languages.text(languages.COURSES[code][0],lang))
        for key,table in self.course_tables.items():
            rows=languages.phrases(code,key);table.setRowCount(len(rows))
            for r,(concept,text,say) in enumerate(rows):
                for c,value in enumerate([languages.text(languages.MEANINGS[concept],lang),text,say]):table.setItem(r,c,QTableWidgetItem(value))
        self.language_quiz=languages.LanguageQuiz(code,lang);self.lang_score.setText("");self.new_language_question()
    def new_language_question(self):
        text,say,options=self.language_quiz.new();self.lang_question.setText(text);self.lang_say.setText(say);self.lang_feedback.clear()
        for b,option in zip(self.lang_buttons,options):b.setText(option.replace("&","&&"));b.setProperty("option",option)
    def answer_language(self,i):
        quiz=self.language_quiz;ok=quiz.check(self.lang_buttons[i].property("option"))
        self.lang_score.setText(f'{self.t("score")}: {quiz.right}/{quiz.total}')
        self.lang_feedback.setText(self.t("correct") if ok else f'{self.t("try_again")} {quiz.correct}')
        if ok:self.course_pet.hop();QTimer.singleShot(900,self.new_language_question)
    def say_phrase(self,unit,row):
        rows=languages.phrases(self.current_course(),unit)
        if 0<=row<len(rows):self.speak_text(rows[row][1].replace("…",""),languages.COURSES[self.current_course()][1])
    def say_selected(self):
        self.speak_text(self.lang_question.text().replace("…",""),languages.COURSES[self.current_course()][1])
    # --------------------------------------------------------------- classroom
    def build_classroom(self):
        """Classroom: Timor-Leste school lessons, or lessons for every age (5–100)."""
        w,layout=page_layout();row=QHBoxLayout();row.setSpacing(16);lang=self.settings.locale
        left=QFrame();left.setObjectName("panel");left.setFixedWidth(320);lv=QVBoxLayout(left);lv.setContentsMargins(12,12,12,12);lv.setSpacing(8)
        lv.addWidget(label("🎂  "+self.t("learner_age"),10,True))
        self.age_level=QComboBox();self.age_level.addItem("🇹🇱  "+self.t("school_lessons"),"school")
        for key,_,name in curriculum.LEVELS:self.age_level.addItem(curriculum.text(name,lang),key)
        self.age_level.setCurrentIndex(max(0,self.age_level.findData(self.settings.learner_level)));lv.addWidget(self.age_level)
        self.class_subject=QComboBox();self.age_subject=self.class_subject;lv.addWidget(self.class_subject)
        self.lesson_list=QListWidget();self.lesson_list.setObjectName("guides");self.lesson_list.setWordWrap(True);self.lesson_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff);lv.addWidget(self.lesson_list,1);row.addWidget(left)
        scroll=QScrollArea();scroll.setWidgetResizable(True);scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff);panel=QFrame();panel.setObjectName("panel");v=QVBoxLayout(panel);v.setContentsMargins(22,18,22,18);v.setSpacing(10)
        head=QHBoxLayout();self.lesson_pet=QLabel();head.addWidget(self.lesson_pet);names=QVBoxLayout();self.lesson_subject=label("",10,muted=True);self.lesson_title=label("",18,True);names.addWidget(self.lesson_subject);names.addWidget(self.lesson_title);head.addLayout(names,1);v.addLayout(head)
        self.lesson_body=label("",12);self.lesson_body.setTextFormat(Qt.PlainText);v.addWidget(self.lesson_body)
        task=QFrame();task.setObjectName("hero");tl=QVBoxLayout(task);tl.addWidget(label(self.t("lesson_task"),11,True));self.lesson_task=label("",12);tl.addWidget(self.lesson_task);v.addWidget(task)
        actions=QHBoxLayout();actions.addWidget(button(self.t("practice_subject"),self.quiz_current_lesson,True));actions.addWidget(button(self.t("open_teacher"),self.teacher_for_lesson));actions.addStretch();v.addLayout(actions)
        more=QHBoxLayout();more.addWidget(button(self.t("speak"),self.read_lesson));more.addWidget(button("🔎 "+self.t("learn_more"),self.lesson_more));self.lesson_star=button("☆ "+self.t("favourite"),self.toggle_lesson_favourite);more.addWidget(self.lesson_star);more.addStretch();v.addLayout(more);v.addStretch()
        scroll.setWidget(panel);row.addWidget(scroll,1);layout.addLayout(row,1)
        self.age_level.currentIndexChanged.connect(self.level_changed);self.class_subject.currentIndexChanged.connect(self.fill_lessons);self.lesson_list.currentRowChanged.connect(self.show_lesson)
        self.fill_subjects();return w
    def level(self):
        return self.age_level.currentData() if hasattr(self,"age_level") else "school"
    def level_changed(self,*_):
        level=self.level()
        if level!=self.settings.learner_level:
            self.settings.learner_level=level
            if not self.review:
                try:self.settings.save()
                except OSError:pass
        self.fill_subjects()
    def fill_subjects(self):
        lang=self.settings.locale;current=self.class_subject.currentData();self.class_subject.blockSignals(True);self.class_subject.clear()
        self.class_subject.addItem(self.t("all_subjects"),None)
        if self.level()=="school":
            for key in classroom.SUBJECTS:self.class_subject.addItem(classroom.subject_name(key,lang),key)
        else:
            for item in curriculum.subjects():self.class_subject.addItem(item.icon+"  "+curriculum.text(item.name,lang),item.key)
        self.class_subject.setCurrentIndex(max(0,self.class_subject.findData(current)));self.class_subject.blockSignals(False);self.fill_lessons()
    def fill_lessons(self,*_):
        lang=self.settings.locale;level=self.level();subject=self.class_subject.currentData();self.lesson_list.clear()
        if level=="school":
            self.class_lessons=classroom.lessons(subject)
            for lesson in self.class_lessons:self.lesson_list.addItem(classroom.subject_name(lesson.subject,lang)+" · "+classroom.text(lesson.title,lang))
        else:
            self.class_lessons=curriculum.lessons(subject,level)
            for lesson in self.class_lessons:
                item=curriculum.subject(lesson.subject);self.lesson_list.addItem(f"{item.icon if item else '📘'}  {curriculum.subject_name(lesson.subject,lang)} · {curriculum.text(lesson.title,lang)}")
        # Showing the first lesson of a list is not "opening" it: only a lesson the
        # learner picks counts as the last material on Home.
        self.lesson_autoselect=True
        try:self.lesson_list.setCurrentRow(0)
        finally:self.lesson_autoselect=False
    def current_lesson(self):
        row=self.lesson_list.currentRow();return self.class_lessons[row] if 0<=row<len(getattr(self,"class_lessons",[])) else None
    def show_lesson(self,*_):
        lesson=self.current_lesson();lang=self.settings.locale
        if not lesson:return
        self.lesson_pet.setPixmap(self.atlas.pixmap("lecture",84,self.settings.costume))
        if isinstance(lesson,curriculum.AgeLesson):
            self.lesson_subject.setText(curriculum.subject_name(lesson.subject,lang)+" · "+curriculum.level_name(lesson.level,lang));text=curriculum.text
        else:
            self.lesson_subject.setText(classroom.subject_name(lesson.subject,lang));text=classroom.text
        self.lesson_title.setText(text(lesson.title,lang))
        self.lesson_body.setText("\n\n".join("•  "+text(point,lang) for point in lesson.points));self.lesson_task.setText(text(lesson.task,lang))
        key=self.lesson_target(lesson)
        if not getattr(self,"lesson_autoselect",False):self.progress.opened("lesson",key,self.lesson_subject.text()+" · "+self.lesson_title.text())
        self.lesson_star.setText(("★ " if self.progress.is_favourite("lesson",key) else "☆ ")+self.t("favourite"))
    def lesson_exam_subject(self,lesson):
        return f"age:{lesson.subject}:{lesson.level}" if isinstance(lesson,curriculum.AgeLesson) else lesson.subject
    def quiz_current_lesson(self):
        lesson=self.current_lesson()
        if lesson:self.navigate("exams");self.start_exam("quiz",self.lesson_exam_subject(lesson))
    def teacher_for_lesson(self):
        lesson=self.current_lesson()
        if lesson:
            key={"physics":"science","chemistry":"science","biology":"science","astronomy":"science","atoms":"science","environment":"science","medicine":"health","computers":"ict","it":"ict","technology":"ict","communication":"languages","economics":"civics","agriculture":"science"}.get(lesson.subject,lesson.subject)
            self.navigate("teachers");self.teacher_list.setCurrentRow(next((i for i,t in enumerate(school.TEACHERS) if t.key==key),0))
            if hasattr(self,"teacher_input"):self.teacher_input.setText(self.lesson_title.text())
    def lesson_more(self):
        """Search LAFA's memory (and the sources it read) for the lesson topic."""
        if not self.current_lesson():return
        self.navigate("library","search");self.run_search("library",self.lesson_title.text())
    def read_lesson(self):
        lesson=self.current_lesson()
        if lesson:self.last_answer=self.lesson_title.text()+". "+self.lesson_body.text().replace("•","");self.speak_last()
    # --------------------------------------------------------------- exam hall
    def build_exams(self):
        w,layout=page_layout();top=QFrame();top.setObjectName("panel");t=QHBoxLayout(top);t.setContentsMargins(14,10,14,10)
        self.exam_kind=QComboBox()
        for kind in classroom.KINDS:self.exam_kind.addItem(self.t(kind)+" — "+self.t(kind+"_d"),kind)
        self.exam_subject=QComboBox();self.exam_subject.addItem(self.t("all_subjects"),"all")
        for key in classroom.SUBJECTS:self.exam_subject.addItem(classroom.subject_name(key,self.settings.locale),key)
        for item in curriculum.subjects():self.exam_subject.addItem(item.icon+"  "+curriculum.text(item.name,self.settings.locale)+" · "+self.t("every_age"),"age:"+item.key)
        self.exam_level=QComboBox();self.exam_level.addItem(self.t("all_ages"),"")
        for key,_,name in curriculum.LEVELS:self.exam_level.addItem(curriculum.text(name,self.settings.locale).split(" · ")[0],key)
        t.addWidget(self.exam_kind,2);t.addWidget(self.exam_subject,1);t.addWidget(self.exam_level,1);t.addWidget(button(self.t("start_exam"),lambda:self.start_exam(),True));layout.addWidget(top)
        sheet=QFrame();sheet.setObjectName("panel");v=QVBoxLayout(sheet);v.setContentsMargins(22,16,22,16);v.setSpacing(12)
        status=QHBoxLayout();self.exam_progress=label(self.t("start_hint"),10,muted=True);status.addWidget(self.exam_progress,1);self.exam_timer_label=label("",11,True);status.addWidget(self.exam_timer_label);v.addLayout(status)
        self.exam_question=label("",16,True);v.addWidget(self.exam_question);grid=QGridLayout();grid.setSpacing(10);self.exam_buttons=[]
        for i in range(4):
            b=button("",lambda checked=False,i=i:self.answer_exam(i));b.setMinimumHeight(46);b.setEnabled(False);grid.addWidget(b,i//2,i%2);self.exam_buttons.append(b)
        v.addLayout(grid);self.exam_feedback=label("",12);v.addWidget(self.exam_feedback)
        self.exam_info=label("",9,muted=True);v.addWidget(self.exam_info)
        retry=QHBoxLayout();self.exam_retry=button(self.t("retry_mistakes"),self.retry_mistakes,True);self.exam_retry.hide();retry.addWidget(self.exam_retry);retry.addStretch();v.addLayout(retry)
        self.exam_result=QPlainTextEdit();self.exam_result.setReadOnly(True);self.exam_result.setMinimumHeight(150);self.exam_result.hide();v.addWidget(self.exam_result,1);v.addStretch()
        layout.addWidget(sheet,1);self.exam=getattr(self,'exam',None)
        if not hasattr(self,'report'):self.report=classroom.ReportCard(self.planner.folder)
        # A rebuilt page (new language or theme) must not leave the old timer ticking.
        if getattr(self,"exam_timer",None):self.exam_timer.stop();self.exam_timer.deleteLater()
        self.exam_timer=QTimer(self);self.exam_timer.timeout.connect(self.tick_exam)
        if self.exam is not None and self.exam.limit and not self.exam.finished:self.exam_timer.start(1000)
        return w
    def start_exam(self,kind=None,subject=None):
        if kind:self.exam_kind.setCurrentIndex(self.exam_kind.findData(kind))
        level=""
        if subject and str(subject).startswith("age:"):
            parts=(subject.split(":")+["",""])[:3];subject="age:"+parts[1];level=parts[2]
            self.exam_level.setCurrentIndex(max(0,self.exam_level.findData(level)))
        if subject:self.exam_subject.setCurrentIndex(self.exam_subject.findData(subject))
        chosen=self.exam_subject.currentData();level=self.exam_level.currentData()
        if level:
            # An age level uses the lessons for that age (same subject when it exists).
            key=chosen[4:] if str(chosen).startswith("age:") else chosen if curriculum.subject(chosen) else ""
            chosen=f"age:{key}:{level}"
        self.exam=classroom.ExamSession(self.exam_kind.currentData(),chosen,self.settings.locale)
        self.exam_result.hide();self.exam_feedback.clear();self.exam_retry.hide()
        self.exam_info.setText(self.t("bank_limited").replace("{n}",str(self.exam.total)).replace("{want}",str(self.exam.requested)) if self.exam.limited else "")
        for b in self.exam_buttons:b.show()
        self.show_exam_question()
        if self.exam.limit:self.exam_timer.start(1000)
        self.tick_exam()
    def show_exam_question(self):
        exam=self.exam
        if exam is None:return
        if exam.finished:self.finish_exam();return
        q=exam.current;self.exam_progress.setText(self.t(exam.kind)+" · "+classroom.subject_name(exam.subject,self.settings.locale)+" · "+self.t("question_n").replace("{n}",str(exam.index+1)).replace("{total}",str(exam.total)))
        self.exam_question.setText(q.text)
        for b,option in zip(self.exam_buttons,q.options):b.setText(option.replace("&","&&"));b.setProperty("option",option);b.setEnabled(True)
    def answer_exam(self,i):
        exam=self.exam
        if exam is None or exam.finished:return
        q=exam.current;choice=self.exam_buttons[i].property("option");ok=exam.answer(choice)
        if exam.kind=="quiz":
            why=(f"\n💡 {q.explanation}" if q.explanation else "")+(f"\n📘 {self.t('related_lesson')}: {q.related}" if q.related and not ok else "")
            self.exam_feedback.setText((self.t("correct") if ok else f'{self.t("try_again")} {q.correct}')+why);self.set_mood("talking" if ok else "thinking")
            for b in self.exam_buttons:b.setEnabled(False)
            QTimer.singleShot(2200 if q.explanation and not ok else 900,self.show_exam_question)
        else:self.show_exam_question()
    def tick_exam(self):
        exam=self.exam
        if exam is None or not exam.limit:self.exam_timer_label.setText("");return
        left=exam.time_left();self.exam_timer_label.setText(f'⏱ {self.t("time_left")}: {left//60:02d}:{left%60:02d}')
        if left==0:self.finish_exam()
    def finish_exam(self):
        exam=self.exam;self.exam_timer.stop()
        if exam is None or getattr(exam,"saved",False):return
        exam.saved=True;lang=self.settings.locale
        for b in self.exam_buttons:b.setEnabled(False);b.hide()
        if not getattr(exam,"retry_session",False):self.report.add(exam)
        grade=classroom.grade(exam.percent,lang)
        summary=self.t("exam_done").replace("{score}",str(exam.score)).replace("{total}",str(exam.total)).replace("{percent}",str(exam.percent)).replace("{grade}",grade)
        self.exam_question.setText(summary);self.exam_feedback.setText(self.t("saved_report"));self.exam_progress.setText(self.t("result"))
        lines=[summary,""]
        mistakes=exam.mistakes()
        if mistakes:
            lines.append(self.t("mistakes")+":")
            for q,choice in mistakes:
                lines.append(f"• {q.text}\n   ✗ {choice}   ✓ {self.t('correct_answer')}: {q.correct}")
                if q.explanation:lines.append(f"   💡 {q.explanation}")
                if q.related:lines.append(f"   📗 {self.t('related_lesson')}: {q.related}")
        self.exam_result.setPlainText("\n".join(lines));self.exam_result.show();self.exam_retry.setVisible(bool(mistakes));self.set_mood("motivator" if exam.percent>=60 else "thinking")
        self.render_report()
    # ------------------------------------------------------------- report card
    def build_report(self):
        w,layout=page_layout();lang=self.settings.locale;layout.addWidget(label(self.t("results_personal"),10,muted=True))
        self.report_summary=QTableWidget(0,5);self.report_summary.setHorizontalHeaderLabels([self.t("subject"),self.t("attempts"),self.t("average"),self.t("best"),self.t("grade")])
        self.report_summary.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch);self.report_summary.verticalHeader().hide();self.report_summary.setEditTriggers(QTableWidget.NoEditTriggers);layout.addWidget(self.report_summary,1)
        layout.addWidget(label(self.t("history_label"),12,True))
        self.report_history=QTableWidget(0,4);self.report_history.setHorizontalHeaderLabels([self.t("date"),self.t("kind"),self.t("subject"),self.t("score")])
        self.report_history.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch);self.report_history.verticalHeader().hide();self.report_history.setEditTriggers(QTableWidget.NoEditTriggers);layout.addWidget(self.report_history,1)
        row=QHBoxLayout();self.report_status=label("",10,muted=True);row.addWidget(self.report_status,1);row.addWidget(button(self.t("tab_practice"),lambda:self.navigate("study","practice")));row.addWidget(button(self.t("export_report"),self.export_report,True));layout.addLayout(row)
        if not hasattr(self,"report"):self.report=classroom.ReportCard(self.planner.folder)
        self.render_report();return w
    def render_report(self):
        if not hasattr(self,"report_summary"):return
        lang=self.settings.locale;summary=sorted(self.report.summary().items());self.report_summary.setRowCount(len(summary))
        for r,(subject,(attempts,best,average)) in enumerate(summary):
            for c,value in enumerate([classroom.subject_name(subject,lang),str(attempts),f"{average}%",f"{best}%",classroom.grade(average,lang)]):self.report_summary.setItem(r,c,QTableWidgetItem(value))
        entries=list(reversed(self.report.entries[-200:]));self.report_history.setRowCount(len(entries))
        for r,e in enumerate(entries):
            for c,value in enumerate([e["when"],self.t(e["kind"]),classroom.subject_name(e["subject"],lang),f'{e["score"]}/{e["total"]}']):self.report_history.setItem(r,c,QTableWidgetItem(value))
        self.report_status.setText("" if entries else self.t("no_results"))
    def export_report(self):
        path,_=QFileDialog.getSaveFileName(self,self.t("export_report"),str(Path.home()/"lafa-report-card.txt"),"Text (*.txt)")
        if not path:return
        try:Path(path).write_text(self.report.export_text(self.settings.locale),encoding="utf-8")
        except OSError as error:self.error(str(error));return
        self.report_status.setText(self.t("saved_to")+" "+path)
    # ------------------------------------------------------------- Timor-Leste
    # ----------------------------------------------------- Timor-Leste atlas
    # ------------------------------------------------------------ encyclopedia
    def open_article(self,article_id,tab="read"):
        """Open an encyclopedia article in its own section (World → Learn, Timor-Leste)."""
        article=enc.get(article_id)
        if article is None:return
        if article.area=="world":self.navigate("study","encyclopedia");self.world_browser.open_article(article_id,tab)
        else:self.navigate("timor");self.timor_browser.open_article(article_id,tab)
    def voice_available(self):
        return bool(shutil.which("espeak-ng") or shutil.which("espeak"))
    def saved_extract(self,article):
        """Text saved from the internet for an article (offline pack or atlas refresh), or None."""
        lang=self.settings.locale
        try:
            from . import offline_pack
            found=offline_pack.extract(article.id,lang)
            if found:return found
        except ImportError:pass
        if article.id.startswith("atlas:") and article.wiki:
            live=livefacts.get(article.id[6:],lang)
            if live:return {"lang":live["lang"],"fetched":live["fetched"],"text":live["text"],"url":live.get("url",""),"source":"Wikipedia"}
        return None
    def today_text(self,when=None):
        lang=self.settings.locale;events=timorleste.today_in_history(when,lang)
        if events:return "\n".join(events)
        nxt=timorleste.next_holiday(when,lang)
        return self.t("next_holiday").replace("{name}",nxt[2]).replace("{days}",str(nxt[0])).replace("{date}",nxt[1].strftime("%d/%m")) if nxt else ""
    def build_os(self):
        w,layout=page_layout();layout.addWidget(label(self.t("os_intro"),10,muted=True))
        row=QHBoxLayout();row.setSpacing(14)
        self.os_list=QListWidget();self.os_list.setObjectName("guides");self.os_list.setFixedWidth(300);self.os_list.setWordWrap(True);self.os_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        for guide in osguide.GUIDES:
            item=QListWidgetItem(guide.icon+"  "+guide.title.get(self.settings.locale,guide.title["en"]));item.setData(Qt.UserRole,guide.key);self.os_list.addItem(item)
        row.addWidget(self.os_list)
        detail=QFrame();detail.setObjectName("panel");d=QVBoxLayout(detail);d.setContentsMargins(22,18,22,18);d.setSpacing(12)
        self.os_title=label("",16,True);d.addWidget(self.os_title);self.os_steps=label("",12);self.os_steps.setTextInteractionFlags(Qt.TextSelectableByMouse);d.addWidget(self.os_steps)
        actions=QHBoxLayout();self.os_open=button(self.t("open_tool"),self.open_guide_tool,True);actions.addWidget(self.os_open);actions.addWidget(button(self.t("speak"),lambda:self.speak_text(self.os_steps.text())));actions.addStretch();d.addLayout(actions)
        self.os_tool_status=label("",9,muted=True);d.addWidget(self.os_tool_status);d.addStretch()
        row.addWidget(detail,1);layout.addLayout(row,1)
        self.os_list.currentRowChanged.connect(self.show_guide_row);self.os_list.setCurrentRow(0);return w
    def show_guide_row(self,row):
        if 0<=row<len(osguide.GUIDES):self.show_guide(osguide.GUIDES[row],navigate=False)
    def show_guide(self,guide,navigate=True):
        lang=self.settings.locale;self.current_guide=guide
        self.os_title.setText(guide.icon+"  "+guide.title.get(lang,guide.title["en"]))
        self.os_steps.setText("\n\n".join(f"{i}.  {step}" for i,step in enumerate(guide.steps.get(lang,guide.steps["en"]),1)))
        tool=osguide.available_tool(guide);self.os_open.setEnabled(bool(tool));self.os_tool_status.setText(Path(tool).name if tool else self.t("tool_missing"))
        row=next((i for i,g in enumerate(osguide.GUIDES) if g.key==guide.key),-1)
        if self.os_list.currentRow()!=row:self.os_list.blockSignals(True);self.os_list.setCurrentRow(row);self.os_list.blockSignals(False)
        if navigate:self.navigate("oshelp","guides")
    def open_guide_tool(self,guide=None):
        guide=guide or getattr(self,"current_guide",None)
        if not guide:return
        tool=osguide.available_tool(guide)
        if not tool:self.error(self.t("tool_missing"));return
        if self.review:self.error(self.t("preview_only"));return
        # Fixed allowlisted executable, no arguments and no shell.
        result=QProcess.startDetached(tool,[])
        if not started(result):self.error(self.t("tool_missing"))
        else:self.set_mood("talking");self.companion.show_answer(guide.title.get(self.settings.locale,guide.title["en"]))
    def refresh_system(self):
        text="\n".join(f'{self.t(k)}: {v}'+(" ⚠" if state=="warn" else "") for k,v,state in osguide.system_report().items)
        if hasattr(self,"os_system"):self.os_system.setText(text)
    # ------------------------------------------------------------- school
    def subject_name(self,key):
        teacher=school.BY_KEY.get(key);return teacher.text('name',self.settings.locale) if teacher else self.t('other')
    def build_teachers(self):
        w,layout=page_layout();row=QHBoxLayout();row.setSpacing(14)
        self.teacher_list=QListWidget();self.teacher_list.setObjectName("guides");self.teacher_list.setFixedWidth(260);self.teacher_list.setIconSize(QSize(44,44))
        for teacher in school.TEACHERS:
            item=QListWidgetItem(QIcon(self.atlas.pixmap(teacher.pose,88,self.settings.costume)),teacher.text('name',self.settings.locale));item.setData(Qt.UserRole,teacher.key);self.teacher_list.addItem(item)
        row.addWidget(self.teacher_list)
        scroll=QScrollArea();scroll.setWidgetResizable(True);scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        panel=QFrame();panel.setObjectName("panel");v=QVBoxLayout(panel);v.setContentsMargins(20,16,20,16);v.setSpacing(10)
        head=QHBoxLayout();self.teacher_face=QLabel();head.addWidget(self.teacher_face);names=QVBoxLayout();self.teacher_name=label("",16,True);self.teacher_intro=label("",10,muted=True)
        names.addWidget(self.teacher_name);names.addWidget(self.teacher_intro);head.addLayout(names,1);v.addLayout(head)
        v.addWidget(label(self.t("practice"),12,True))
        self.practice_stack=QStackedWidget();self.practice_stack.setMinimumHeight(250);v.addWidget(self.practice_stack)
        # Maths
        math=QWidget();m=QVBoxLayout(math);top=QHBoxLayout();self.math_level=QComboBox()
        for level in (1,2,3):self.math_level.addItem(f'{self.t("level")} {level}',level)
        top.addWidget(self.math_level);top.addStretch();self.math_score=label("",10,muted=True);top.addWidget(self.math_score);m.addLayout(top)
        self.math_question=label("",20,True);m.addWidget(self.math_question);answer=QHBoxLayout();self.math_answer=QLineEdit();self.math_answer.returnPressed.connect(self.check_math)
        answer.addWidget(self.math_answer,1);answer.addWidget(button(self.t("check"),self.check_math,True));answer.addWidget(button(self.t("new_question"),self.new_math));m.addLayout(answer)
        self.math_feedback=label("",11);m.addWidget(self.math_feedback);self.math=school.MathPractice();self.practice_stack.addWidget(math)
        # Vocabulary
        vocab=QWidget();vv=QVBoxLayout(vocab);top=QHBoxLayout();self.vocab_from=QComboBox();self.vocab_to=QComboBox()
        for code,name in [('en','English'),('tet','Tetun'),('pt','Português'),('id','Bahasa Indonesia')]:self.vocab_from.addItem(name,code);self.vocab_to.addItem(name,code)
        self.vocab_from.setCurrentIndex(self.vocab_from.findData('en'));self.vocab_to.setCurrentIndex(self.vocab_to.findData('tet' if self.settings.locale!='tet' else 'pt'))
        top.addWidget(label(self.t("translate_from"),10,muted=True));top.addWidget(self.vocab_from);top.addWidget(label(self.t("translate_to"),10,muted=True));top.addWidget(self.vocab_to);top.addStretch()
        self.vocab_score=label("",10,muted=True);top.addWidget(self.vocab_score);vv.addLayout(top)
        self.vocab_word=label("",20,True);vv.addWidget(self.vocab_word);grid=QGridLayout();self.vocab_buttons=[]
        for i in range(4):
            b=button("",lambda checked=False,i=i:self.answer_vocab(i));b.setMinimumHeight(42);grid.addWidget(b,i//2,i%2);self.vocab_buttons.append(b)
        vv.addLayout(grid);self.vocab_feedback=label("",11);vv.addWidget(self.vocab_feedback);vv.addWidget(button(self.t("new_question"),self.new_vocab))
        self.vocab=school.VocabPractice();self.vocab_from.currentIndexChanged.connect(self.new_vocab);self.vocab_to.currentIndexChanged.connect(self.new_vocab);self.practice_stack.addWidget(vocab)
        # Quiz
        quiz=QWidget();q=QVBoxLayout(quiz);self.quiz_score=label("",10,muted=True);q.addWidget(self.quiz_score);self.quiz_question=label("",14,True);q.addWidget(self.quiz_question)
        grid=QGridLayout();self.quiz_buttons=[]
        for i in range(4):
            b=button("",lambda checked=False,i=i:self.answer_quiz(i));b.setMinimumHeight(42);grid.addWidget(b,i//2,i%2);self.quiz_buttons.append(b)
        q.addLayout(grid);self.quiz_feedback=label("",11);q.addWidget(self.quiz_feedback);q.addWidget(button(self.t("new_question"),self.new_quiz));self.quiz=None;self.practice_stack.addWidget(quiz)
        # Counsellor tips
        tips=QWidget();tv=QVBoxLayout(tips);tv.addWidget(label(self.t("counsellor_tip"),11,True,muted=True));self.tip_text=label("",14);tv.addWidget(self.tip_text);tv.addWidget(button(self.t("next_tip"),self.next_tip));self.tip_index=0;self.practice_stack.addWidget(tips)
        v.addWidget(label(self.t("find_material"),12,True))
        ask=QHBoxLayout();self.teacher_input=QLineEdit();self.teacher_input.setPlaceholderText(self.t("search_box"));self.teacher_input.returnPressed.connect(self.ask_teacher)
        self.teacher_send=button(self.t("find"),self.ask_teacher,True);ask.addWidget(self.teacher_input,1);ask.addWidget(self.teacher_send);v.addLayout(ask)
        self.teacher_answer=QPlainTextEdit();self.teacher_answer.setReadOnly(True);self.teacher_answer.setMinimumHeight(110);v.addWidget(self.teacher_answer)
        v.addWidget(label(self.t("resources"),12,True));self.teacher_links=QGridLayout();v.addLayout(self.teacher_links);v.addStretch()
        scroll.setWidget(panel);row.addWidget(scroll,1);layout.addLayout(row,1)
        self.teacher_list.currentRowChanged.connect(self.show_teacher);self.teacher_list.setCurrentRow(0);return w
    def current_teacher(self):
        row=self.teacher_list.currentRow();return school.TEACHERS[row] if 0<=row<len(school.TEACHERS) else school.TEACHERS[0]
    def show_teacher(self,row):
        if not 0<=row<len(school.TEACHERS):return
        teacher=school.TEACHERS[row];lang=self.settings.locale
        self.teacher_face.setPixmap(self.atlas.pixmap(teacher.pose,110,self.settings.costume));self.teacher_name.setText(teacher.text('name',lang));self.teacher_intro.setText(teacher.text('intro',lang))
        self.teacher_answer.setPlainText(self.t('subject_guide_note'))
        while self.teacher_links.count():
            item=self.teacher_links.takeAt(0)
            if item.widget():item.widget().deleteLater()
        for i,(title,url) in enumerate(teacher.resources):self.teacher_links.addWidget(button(title,lambda checked=False,u=url:self.open_web(u)),i//2,i%2)
        kind={'math':0,'vocab':1,'quiz':2,'tips':3}[teacher.practice];self.practice_stack.setCurrentIndex(kind)
        if kind==0:self.new_math()
        elif kind==1:self.new_vocab()
        elif kind==2:self.quiz=school.QuizPractice(school.TEACHER_QUIZ[teacher.key]);self.new_quiz()
        else:self.next_tip()
    def score(self,key,correct):
        right,total=self.scores.get(key,(0,0));self.scores[key]=(right+int(correct),total+1)
        return f'{self.t("score")}: {self.scores[key][0]}/{self.scores[key][1]}'
    def new_math(self,*_):self.math_question.setText(self.math.new(self.math_level.currentData()));self.math_answer.clear();self.math_feedback.clear()
    def check_math(self):
        if not self.math_answer.text().strip():self.hint(self.math_answer,self.t('type_first'));return
        correct=self.math.check(self.math_answer.text());self.math_score.setText(self.score('math',correct))
        self.math_feedback.setText(self.t('correct') if correct else f'{self.t("try_again")} {self.math.answer}')
        self.set_mood('talking' if correct else 'thinking')
        if correct:QTimer.singleShot(900,self.new_math)
    def new_vocab(self,*_):
        word,options=self.vocab.new(self.vocab_from.currentData(),self.vocab_to.currentData());self.vocab_word.setText(word);self.vocab_feedback.clear()
        for b,option in zip(self.vocab_buttons,options):b.setText(option.replace('&','&&'));b.setProperty('option',option)
    def answer_vocab(self,i):
        choice=self.vocab_buttons[i].property('option');correct=self.vocab.check(choice);self.vocab_score.setText(self.score('vocab',correct))
        self.vocab_feedback.setText(self.t('correct') if correct else f'{self.t("try_again")} {self.vocab.correct}')
        if correct:QTimer.singleShot(900,self.new_vocab)
    def new_quiz(self,*_):
        if not self.quiz:return
        question,options=self.quiz.new(self.settings.locale);self.quiz_question.setText(question);self.quiz_feedback.clear()
        for b,option in zip(self.quiz_buttons,options):b.setText(option.replace('&','&&'));b.setProperty('option',option)
    def answer_quiz(self,i):
        if not self.quiz:return
        choice=self.quiz_buttons[i].property('option');correct=self.quiz.check(choice);self.quiz_score.setText(self.score(self.current_teacher().key,correct))
        self.quiz_feedback.setText(self.t('correct') if correct else f'{self.t("try_again")} {self.quiz.correct}')
        if correct:QTimer.singleShot(1100,self.new_quiz)
    def next_tip(self):
        tip=school.TIPS[self.tip_index%len(school.TIPS)];self.tip_index+=1;self.tip_text.setText(tip.get(self.settings.locale,tip['en']))
    def build_homework(self):
        w,layout=page_layout();tabs=QTabWidget();layout.addWidget(tabs,1)
        work=QWidget();v=QVBoxLayout(work);row=QHBoxLayout();self.hw_subject=QComboBox()
        for teacher in school.TEACHERS:
            if teacher.key!='counsellor':self.hw_subject.addItem(teacher.text('name',self.settings.locale),teacher.key)
        self.hw_subject.addItem(self.t('other'),'other');self.hw_title=QLineEdit();self.hw_title.setMaxLength(200);self.hw_title.setPlaceholderText(self.t('homework_title'))
        self.hw_due=QDateEdit(QDate.currentDate().addDays(1));self.hw_due.setCalendarPopup(True);self.hw_due.setDisplayFormat('yyyy-MM-dd')
        self.hw_add=button(self.t('add_homework'),self.add_homework,True);row.addWidget(self.hw_subject);row.addWidget(self.hw_title,1);row.addWidget(self.hw_due);row.addWidget(self.hw_add);v.addLayout(row)
        self.hw_agenda=QCheckBox(self.t('to_agenda'));self.hw_agenda.setChecked(eduka.installed());v.addWidget(self.hw_agenda)
        self.hw_table=QTableWidget(0,4);self.hw_table.setHorizontalHeaderLabels([self.t('subject'),self.t('homework_title'),self.t('due'),self.t('done')])
        self.hw_table.horizontalHeader().setSectionResizeMode(1,QHeaderView.Stretch);self.hw_table.verticalHeader().hide();self.hw_table.setSelectionBehavior(QTableWidget.SelectRows);self.hw_table.setEditTriggers(QTableWidget.NoEditTriggers)
        v.addWidget(self.hw_table,1);actions=QHBoxLayout();actions.addWidget(button(self.t('done'),self.toggle_homework));actions.addWidget(button(self.t('delete'),self.delete_homework));actions.addStretch()
        self.hw_status=label("",9,muted=True);actions.addWidget(self.hw_status);v.addLayout(actions);tabs.addTab(work,self.t('homework').split(' & ')[0])
        table=QWidget();tv=QVBoxLayout(table);days=self.t('days').split(',')
        self.timetable=QTableWidget(school.Planner.PERIODS,school.Planner.DAYS);self.timetable.setHorizontalHeaderLabels(days[:school.Planner.DAYS])
        self.timetable.setVerticalHeaderLabels([f'{self.t("period")} {i+1}' for i in range(school.Planner.PERIODS)]);self.timetable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        for day in range(school.Planner.DAYS):
            for period in range(school.Planner.PERIODS):self.timetable.setItem(period,day,QTableWidgetItem(self.planner.timetable[day][period]))
        self.timetable.itemChanged.connect(lambda item:self.planner.set_cell(item.column(),item.row(),item.text()))
        tv.addWidget(self.timetable,1);tabs.addTab(table,self.t('timetable'));self.render_homework();return w
    def render_homework(self):
        items=sorted(self.planner.homework,key=lambda h:(h.done,h.due));self.hw_items=items;self.hw_table.setRowCount(len(items))
        for r,h in enumerate(items):
            for c,value in enumerate([self.subject_name(h.subject),h.title,h.due,'✔' if h.done else '']):self.hw_table.setItem(r,c,QTableWidgetItem(value))
    def add_homework(self):
        try:item=self.planner.add(self.hw_subject.currentData(),self.hw_title.text(),self.hw_due.date().toString('yyyy-MM-dd'))
        except ValueError as error:self.error(str(error));return
        self.hw_title.clear();self.render_homework();self.hw_status.setText('')
        if self.hw_agenda.isChecked() and not self.review:
            try:eduka.add_agenda(item.due,'07:00',f'{self.subject_name(item.subject)}: {item.title}');self.hw_status.setText(self.t('saved_agenda'))
            except (OSError,ValueError) as error:self.hw_status.setText(str(error))
        self.refresh_home()
    def selected_homework(self):
        row=self.hw_table.currentRow();return self.hw_items[row] if 0<=row<len(getattr(self,'hw_items',[])) else None
    def toggle_homework(self):
        item=self.selected_homework()
        if not item:self.hint(self.hw_table,self.t('choose_first'));return
        if item:self.planner.toggle(item.id);self.render_homework();self.refresh_home()
    def delete_homework(self):
        item=self.selected_homework()
        if not item:self.hint(self.hw_table,self.t('choose_first'));return
        if item:self.planner.remove(item.id);self.render_homework();self.refresh_home()
    def build_files(self):
        w,layout=page_layout(); layout.addWidget(label(self.t("formats")+" "+self.t("files_private"),10,muted=True))
        row=QHBoxLayout(); self.file_query=QLineEdit(); self.file_query.setPlaceholderText(self.t("filename")); self.file_query.returnPressed.connect(self.search_files)
        self.kind=QComboBox()
        for key in ["all","documents","music","videos","pictures"]: self.kind.addItem(self.t(key),key)
        self.file_search_button=button(self.t("find"),self.search_files,True)
        row.addWidget(self.file_query,1); row.addWidget(self.kind); row.addWidget(self.file_search_button); layout.addLayout(row)
        self.file_table=QTableWidget(0,3); self.file_table.setHorizontalHeaderLabels([self.t("filename").replace("…",""),self.t("file_type"),self.t("folder")])
        self.file_table.horizontalHeader().setSectionResizeMode(0,QHeaderView.Stretch); self.file_table.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeToContents); self.file_table.horizontalHeader().setSectionResizeMode(2,QHeaderView.Stretch)
        self.file_table.setSelectionBehavior(QTableWidget.SelectRows); self.file_table.setEditTriggers(QTableWidget.NoEditTriggers); self.file_table.verticalHeader().hide(); self.file_table.cellDoubleClicked.connect(lambda r,c:self.open_file())
        layout.addWidget(self.file_table,1); self.file_status=label(self.t("ready"),10,muted=True); layout.addWidget(self.file_status)
        actions=QHBoxLayout(); actions.addWidget(button(self.t("open"),self.open_file)); actions.addWidget(button(self.t("read"),self.read_file)); actions.addStretch(); layout.addLayout(actions)
        return w
    def search_files(self):
        if self.busy: return
        query=self.file_query.text(); kind=self.kind.currentData(); roots=list(self.settings.roots)
        self.set_busy(True,"reading")
        self.work(lambda:FileSearch(roots).search(query,kind),self.finish_files,busy=True)
    def finish_files(self,results):
        self.set_busy(False); self.show_files(results)
    def show_files(self,results):
        self.current_files=results.hits; self.file_table.setRowCount(len(results.hits))
        for r,hit in enumerate(results.hits):
            for c,value in enumerate([hit.name, self.t(hit.kind), str(Path(hit.path).parent)]):
                self.file_table.setItem(r,c,QTableWidgetItem(value))
            self.file_table.setRowHeight(r,52)
        self.file_status.setText(f'{self.t("results")}: {len(results.hits)}  ·  {results.scanned} {self.t("scanned")}'+("  ·  "+self.t("limited") if results.limited else "")+("  ·  "+self.t("empty") if not results.hits else ""))
    def selected_file(self):
        row=self.file_table.currentRow()
        return self.current_files[row] if 0<=row<len(self.current_files) else None
    def open_file(self):
        hit=self.selected_file()
        if not hit:self.hint(self.file_table,self.t('choose_first'));return
        if hit:
            search=FileSearch(self.settings.roots)
            if not search.allowed(hit.path): self.error("File is outside the selected folders."); return
            if not QDesktopServices.openUrl(QUrl.fromLocalFile(hit.path)): self.error("No application could open this file.")
    def read_file(self):
        if self.busy: return
        hit=self.selected_file()
        if not hit:self.hint(self.file_table,self.t('choose_first'));return
        if hit:
            self.set_busy(True,"reading")
            self.work(lambda:FileSearch(self.settings.roots).read(hit.path),lambda text:self.show_document(hit.name,text),busy=True)
    def show_document(self,title,text,public=False,url="",saved=False):
        """Show a document or an extract. Local files never leave this computer."""
        self.set_busy(False);self.set_mood("reading")
        dialog=QDialog(self); dialog.setWindowTitle(self.t("preview")+" · "+title); dialog.resize(760,560)
        layout=QVBoxLayout(dialog); layout.addWidget(label(title,15,True))
        layout.addWidget(label(self.t("extract_note") if public else self.t("local_document_note"),9,muted=True))
        editor=QPlainTextEdit(); editor.setPlainText(text); editor.setReadOnly(True); editor.setAccessibleName(title); layout.addWidget(editor,1)
        row=QHBoxLayout(); row.addWidget(button(self.t("speak"),lambda:self.speak_text(editor.textCursor().selectedText() or text)))
        if public and url and not saved:row.addWidget(button("💾  "+self.t("save_offline"),lambda:self.save_extract(title,url,text)))
        if url:row.addWidget(button(self.t("open_browser"),lambda:self.open_web(url)))
        row.addStretch();row.addWidget(button(self.t("close"),dialog.accept,True)); layout.addLayout(row); self.document_dialog=dialog;dialog.show()
    def save_extract(self,title,url,text):
        try:memory.remember_article(title.split(" · ",1)[-1],url,text,self.settings.locale)
        except (OSError,ValueError) as error:self.error(str(error));return
        self.chat_status.setText(self.t("saved_offline"));self.render_saved()
    def build_offline_pack(self):
        """The one button that saves every source for offline use (lafa/offline_pack.py)."""
        from . import offline_pack
        box=QFrame();box.setObjectName("factcard");v=QVBoxLayout(box);v.setContentsMargins(16,12,16,12);v.setSpacing(8)
        head=QHBoxLayout();mark=QLabel();mark.setPixmap(icons.pixmap("download",self.tokens["accent_strong"],26));head.addWidget(mark)
        title=label(self.t("offline_pack_title"),12,True);head.addWidget(title,1)
        self.pack_button=button(self.t("offline_pack_button"),self.start_offline_pack,True);self.pack_button.setIcon(icons.icon("download","#ffffff"));head.addWidget(self.pack_button)
        self.pack_stop=button(self.t("offline_pack_stop"),self.stop_offline_pack);self.pack_stop.hide();head.addWidget(self.pack_stop);v.addLayout(head)
        v.addWidget(label(self.t("offline_pack_note").format(mb=offline_pack.MAX_TOTAL//(1024*1024),path=str(offline_pack.folder())),9,muted=True))
        self.pack_bar=QProgressBar();self.pack_bar.hide();v.addWidget(self.pack_bar)
        self.pack_status=label("",9,muted=True);v.addWidget(self.pack_status);self.update_pack_status()
        self.pack_running=getattr(self,"pack_running",False);self.update_buttons();return box
    def update_pack_status(self,text=None):
        from . import offline_pack
        if not hasattr(self,"pack_status"):return
        if text:self.pack_status.setText(text);return
        info=offline_pack.manifest()
        self.pack_status.setText(self.t("offline_pack_last").format(date=info["date"],size=info.get("size_mb",0)) if info.get("date") else self.t("offline_pack_never"))
    def start_offline_pack(self):
        if getattr(self,"pack_running",False):return
        if self.review:self.update_pack_status(self.t("preview_only"));return
        if not self.online:self.update_pack_status(self.t("needs_internet_calm"));return
        from . import offline_pack
        import threading
        self.pack_running=True;self.pack_cancel=threading.Event();self.pack_button.hide();self.pack_stop.show();self.pack_bar.show();self.pack_bar.setValue(0)
        relay=PackRelay(self);relay.progress.connect(self.offline_pack_progress)
        cancel=self.pack_cancel;lang=self.settings.locale
        def run():return offline_pack.Pack(lang,progress=lambda d,t,n:relay.progress.emit(d,t,str(n)),stop=cancel.is_set).run()
        def done(info):
            self.pack_running=False;self.pack_button.show();self.pack_stop.hide();self.pack_bar.hide();memory.reset_shared() if hasattr(memory,"reset_shared") else None
            text=self.t("offline_pack_done").format(pages=info["pages"],extracts=info["extracts"],images=info["images"],failed=info["failed"],date=info["date"])
            self.update_pack_status(self.t("offline_pack_stopped")+" "+text if info.get("stopped") else text);relay.deleteLater()
        job=Job(run);self.jobs.add(job);delivery=Delivery(self,job,done,False);job.signals.done.connect(delivery.done)
        def failed(message):
            self.pack_running=False;self.pack_button.show();self.pack_stop.hide();self.pack_bar.hide();self.jobs.discard(job);self.update_pack_status(message);delivery.deleteLater();relay.deleteLater()
        delivery.failed_handler=failed;job.signals.error.connect(delivery.report_error);self.pool.start(job)
    def stop_offline_pack(self):
        if getattr(self,"pack_cancel",None):self.pack_cancel.set();self.pack_stop.setEnabled(False)
    def offline_pack_progress(self,done,total,name):
        if not hasattr(self,"pack_bar"):return
        self.pack_bar.setMaximum(max(1,total));self.pack_bar.setValue(done);self.pack_stop.setEnabled(True)
        self.pack_status.setText(self.t("offline_pack_running").format(done=done,total=total,name=name[:60]))
    def build_sources(self):
        w=QWidget();v=QVBoxLayout(w);v.setContentsMargins(0,8,0,0);v.setSpacing(10);lang=self.settings.locale
        v.addWidget(self.build_offline_pack())
        top=QHBoxLayout();self.source_query=QLineEdit();self.source_query.setPlaceholderText("🔍  "+self.t("search_sources"));self.source_query.textChanged.connect(lambda *_:self.fill_sources())
        top.addWidget(self.source_query,1);self.source_status=label("",9,muted=True);top.addWidget(self.source_status);self.source_check_button=button("⟳  "+self.t("check_now"),lambda:self.check_sources(True));top.addWidget(self.source_check_button);v.addLayout(top)
        v.addWidget(label(self.t("sources_note"),9,muted=True))
        chipbox=QWidget();row=QHBoxLayout(chipbox);row.setContentsMargins(0,0,0,0);row.setSpacing(6);self.source_chips=[]
        everything=ui_kit.chip(f'{self.t("all_topics")} ({len(sources.SOURCES)})');everything.clicked.connect(lambda:self.fill_sources(None));row.addWidget(everything);self.source_chips.append((None,everything))
        for key,name,colour in sources.SOURCE_CATEGORIES:
            c=ui_kit.chip(f"{sources.text(name,lang)} ({len(sources.by_category(key))})",colour);c.clicked.connect(lambda checked=False,k=key:self.fill_sources(k));row.addWidget(c);self.source_chips.append((key,c))
        row.addStretch();chipscroll=ui_kit.smooth_scroll(QScrollArea());chipscroll.setWidget(chipbox);chipscroll.setWidgetResizable(True);chipscroll.setFixedHeight(46);chipscroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff);v.addWidget(chipscroll)
        self.source_scroll=ui_kit.smooth_scroll(QScrollArea());self.source_scroll.setWidgetResizable(True);self.source_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        body=QWidget();self.source_grid=QGridLayout(body);self.source_grid.setSpacing(12);self.source_grid.setContentsMargins(4,4,10,4);self.source_scroll.setWidget(body);v.addWidget(self.source_scroll,1)
        self.source_category=None;self.source_cards={};self.fill_sources(None);self.update_source_status();return w
    def fill_sources(self,category="keep"):
        if category!="keep":self.source_category=category
        for key,c in self.source_chips:c.setCheckable(True);c.setChecked(key==self.source_category)
        while self.source_grid.count():
            item=self.source_grid.takeAt(0)
            if item.widget():item.widget().hide();item.widget().deleteLater()
        lang=self.settings.locale;colours={k:c for k,_,c in sources.SOURCE_CATEGORIES};status=sources.load_status();self.source_cards={}
        query=self.source_query.text().strip() if hasattr(self,"source_query") else ""
        items=[s for s in (sources.search(query,lang) if query else sources.SOURCES) if self.source_category in (None,s[0])]
        for i,(category,name,url,description) in enumerate(items):
            m=source_meta.meta(url);facts=" · ".join([self.t("access_"+m["access"]),", ".join(m["langs"])]+([] if m["academic"] else [self.t("not_academic")]))
            card=ui_kit.SourceCard(name,url,sources.text(description,lang)+"\n"+facts,colours[category],status.get(url,{}).get("state"))
            card.setToolTip(m["reason"].get("id" if lang in ("id","tet") else "en",""))
            if self.settings.depth_effects:ui_kit.soft_shadow(card,16,4,26,self.tokens["dark"])
            card.opened.connect(self.open_web);self.source_grid.addWidget(card,i//3,i%3);self.source_cards[name]=card
        for c in range(3):self.source_grid.setColumnStretch(c,1)
        self.source_grid.setRowStretch(len(items)//3+1,1)
    def update_source_status(self,message=None):
        if not hasattr(self,"source_status"):return
        if message:self.source_status.setText(message);return
        status=sources.load_status();checked=sorted(v["checked"] for v in status.values())
        counts={s:sum(1 for v in status.values() if v["state"]==s) for s in sources.STATES}
        self.source_status.setText(self.t("sources_status").replace("{ok}",str(counts["ok"])).replace("{restricted}",str(counts["restricted"])).replace("{missing}",str(counts["not_found"])).replace("{unknown}",str(counts["unknown"])).replace("{date}",checked[-1] if checked else "—"))
    def check_sources(self,force=False):
        """Check availability when needed: the sources shown (cached for a day),
        or the whole list with "Check now". Reachable never means correct."""
        if getattr(self,"sources_running",False) or not hasattr(self,"source_cards"):return
        if self.review:self.update_source_status(self.t("preview_only"));return
        if not self.online:self.update_source_status(self.t("needs_internet_calm"));return
        items=sources.SOURCES if force else [s for s in sources.SOURCES if s[1] in self.source_cards]
        self.sources_running=True;self.source_check_button.setEnabled(False);self.update_source_status(self.t("working"))
        def done(result):
            self.sources_running=False;self.source_check_button.setEnabled(True);self.update_source_status()
            status=sources.load_status()
            for name,card in self.source_cards.items():card.set_state(status.get(card.url,{}).get("state"))
        job=Job(lambda:sources.check(items,force=force));self.jobs.add(job);delivery=Delivery(self,job,done,False);job.signals.done.connect(delivery.done)
        def failed(message):self.sources_running=False;self.source_check_button.setEnabled(True);self.jobs.discard(job);self.update_source_status(self.t("internet_failed"));delivery.deleteLater()
        delivery.failed_handler=failed;job.signals.error.connect(delivery.report_error);self.pool.start(job)
    def build_learn(self):
        """Wikipedia: searched only when the learner asks (internet)."""
        w,layout=page_layout(); layout.addWidget(label(self.t("wikipedia_note"),10,muted=True))
        row=QHBoxLayout(); self.topic=QLineEdit(); self.topic.setPlaceholderText(self.t("topic")); self.topic.returnPressed.connect(self.search_learn)
        self.learn_button=button(self.t("find"),self.search_learn,True); row.addWidget(self.topic,1); row.addWidget(self.learn_button); layout.addLayout(row)
        self.source_table=QTableWidget(0,2); self.source_table.setHorizontalHeaderLabels([self.t("source_title"),self.t("summary")]); self.source_table.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeToContents); self.source_table.horizontalHeader().setSectionResizeMode(1,QHeaderView.Stretch); self.source_table.verticalHeader().hide(); self.source_table.setSelectionBehavior(QTableWidget.SelectRows); self.source_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.source_table.cellDoubleClicked.connect(lambda r,c:self.read_source())
        layout.addWidget(self.source_table,1); action=QHBoxLayout(); action.addWidget(button(self.t("show_extract"),self.read_source,True)); action.addWidget(button(self.t("open_browser"),self.open_source)); action.addStretch(); layout.addLayout(action)
        self.learn_status=label(self.t("ready"),9,muted=True); layout.addWidget(self.learn_status); return w
    def search_learn(self):
        if not self.topic.text().strip():self.hint(self.topic,self.t("type_first"));return
        if self.busy or not self.require_online(): return
        query,lang=self.topic.text().strip(),self.settings.locale
        self.set_busy(True,"reading")
        self.work(lambda:encyclopedia_search(query,lang),self.finish_sources,busy=True)
    def finish_sources(self,sources):
        self.set_busy(False)
        if self.online: self.show_sources(sources)
    def show_sources(self,sources):
        self.current_sources=sources; self.source_table.setRowCount(len(sources))
        for r,source in enumerate(sources):
            self.source_table.setItem(r,0,QTableWidgetItem(source.title)); self.source_table.setItem(r,1,QTableWidgetItem(source.text)); self.source_table.setRowHeight(r,68)
        self.learn_status.setText(self.t("results")+": "+str(len(sources))+" · "+self.t("article_hint"))
    def selected_source(self):
        i=self.source_table.currentRow()
        return self.current_sources[i] if 0<=i<len(self.current_sources) else None
    def open_source(self):
        s=self.selected_source()
        if not s:self.hint(self.source_table,self.t("choose_first"));return
        self.open_web(s.url)
    def read_source(self):
        if self.busy or not self.require_online(): return
        s=self.selected_source()
        if s:
            self.set_busy(True,"reading")
            self.work(lambda:encyclopedia_article(s),lambda text:self.show_document(self.t("article_extract")+" · "+s.title,text,True,url=s.url),busy=True)
    def build_live(self):
        w,layout=page_layout()
        row=QHBoxLayout(); self.city_query=QLineEdit(self.settings.weather_city); self.city_query.setPlaceholderText(self.t('city')); self.city_query.returnPressed.connect(self.fetch_weather)
        self.weather_button=button(self.t('weather'),self.fetch_weather,True)
        row.addWidget(self.city_query,1); row.addWidget(self.weather_button); layout.addLayout(row)
        choices=QHBoxLayout(); self.city_choices=QComboBox(); self.city_confirm=button(self.t('choosecity'),self.fetch_chosen_city)
        choices.addWidget(self.city_choices,1); choices.addWidget(self.city_confirm); layout.addLayout(choices)
        self.city_choices.hide(); self.city_confirm.hide()
        self.weather_panel=QPlainTextEdit(); self.weather_panel.setReadOnly(True); self.weather_panel.setPlainText(self.t('weather')+' · Open-Meteo\n'+self.t('city')+': '+self.settings.weather_city); self.weather_panel.setMinimumHeight(180)
        layout.addWidget(self.weather_panel,1)
        row=QHBoxLayout(); self.news_query=QLineEdit(); self.news_query.setPlaceholderText(self.t('filter_headlines')); self.news_button=button(self.t('news'),self.fetch_news,True)
        row.addWidget(self.news_query,1); row.addWidget(self.news_button); layout.addLayout(row)
        self.news_table=QTableWidget(0,3); self.news_table.setHorizontalHeaderLabels([self.t('headline'),self.t('publisher'),self.t('published')]); self.news_table.horizontalHeader().setSectionResizeMode(0,QHeaderView.Stretch); self.news_table.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeToContents); self.news_table.horizontalHeader().setSectionResizeMode(2,QHeaderView.ResizeToContents); self.news_table.verticalHeader().hide(); self.news_table.setSelectionBehavior(QTableWidget.SelectRows); self.news_table.setEditTriggers(QTableWidget.NoEditTriggers); self.news_table.cellDoubleClicked.connect(lambda r,c:self.open_news())
        layout.addWidget(self.news_table,1)
        row=QHBoxLayout(); self.live_status=label('BBC World · The Guardian World · '+self.t('ready'),9,muted=True); row.addWidget(self.live_status,1); row.addWidget(button(self.t('open'),self.open_news)); layout.addLayout(row)
        return w
    def fetch_weather(self):
        if self.busy or not self.require_online():return
        if self.review:self.error(self.t('preview_only'));return
        query=self.city_query.text().strip(); self.set_busy(True,'thinking')
        self.work(lambda:weather_query(query,self.settings),self.finish_weather,busy=True)
    def fetch_chosen_city(self):
        if self.busy or not self.require_online() or self.review:return
        index=self.city_choices.currentIndex()
        if not 0<=index<len(self.locations):return
        location=self.locations[index]; self.set_busy(True,'thinking')
        self.work(lambda:forecast(location),self.finish_weather,busy=True)
    def finish_weather(self,report):
        self.set_busy(False)
        if not self.online:return
        self.show_weather(report)
        if isinstance(report,WeatherReport):
            self.last_answer=weather_text(report,self.settings.locale); self.companion.show_answer(self.last_answer); self.set_mood('thinking')
    def show_weather(self,report):
        if isinstance(report,LocationChoices):
            self.locations=report.locations; self.city_choices.clear()
            for location in report.locations:self.city_choices.addItem(location.label+f' · {location.latitude:g}, {location.longitude:g}')
            self.city_choices.setCurrentIndex(-1); self.city_choices.show(); self.city_confirm.show(); self.weather_panel.setPlainText(self.t('choosecity'))
            self.navigate("live"); self.reveal(); return
        self.locations=[]; self.city_choices.hide(); self.city_confirm.hide(); self.weather_panel.setPlainText(weather_text(report,self.settings.locale)); self.city_query.setText(report.location.name)
    def fetch_news(self):
        if self.busy or not self.require_online():return
        if self.review:self.error(self.t('preview_only'));return
        query=self.news_query.text().strip(); self.set_busy(True,'reading')
        self.work(lambda:world_news(query),self.finish_news,busy=True)
    def finish_news(self,report):
        self.set_busy(False)
        if not self.online:return
        self.show_news(report); self.last_answer=news_text(report,self.settings.locale); self.companion.show_answer(self.last_answer); self.set_mood('reading')
    def show_news(self,report):
        self.news_items=report.sources; self.news_table.setRowCount(len(report.sources))
        for r,source in enumerate(report.sources):
            for c,value in enumerate([source.title,source.publisher,source.published]):self.news_table.setItem(r,c,QTableWidgetItem(value))
            self.news_table.setRowHeight(r,48)
        self.live_status.setText(self.t('retrieved')+': '+report.retrieved_at+((' · '+self.t('unavailable')+': '+', '.join(report.failures)) if report.failures else '')+(' · '+self.t('no_headlines') if not report.sources else ''))
    def open_news(self):
        index=self.news_table.currentRow()
        if not 0<=index<len(self.news_items):self.hint(self.news_table,self.t('choose_first') if self.news_items else self.t('load_news_first'));return
        if 0<=index<len(self.news_items):self.open_web(self.news_items[index].url)
    def build_coding(self):
        w,layout=page_layout();layout.addWidget(label(self.t('lesson_mode'),11,muted=True))
        row=QHBoxLayout();self.code_language=QComboBox();self.code_language.addItems(list(LESSONS));self.code_lesson=QComboBox()
        row.addWidget(self.code_language);row.addWidget(self.code_lesson,1);row.addWidget(button(self.t('source'),lambda:self.open_web(REFERENCES[self.code_language.currentText()])));layout.addLayout(row)
        self.code_editor=QPlainTextEdit();self.code_editor.setFont(QFont('DejaVu Sans Mono',11));layout.addWidget(self.code_editor,1)
        self.code_output=QPlainTextEdit();self.code_output.setReadOnly(True);self.code_output.setMaximumHeight(140);self.code_output.setPlaceholderText(self.t('learning_ready'));layout.addWidget(self.code_output)
        actions=QHBoxLayout();self.code_run=button(self.t('run_lesson'),self.run_lesson,True);actions.addWidget(self.code_run);actions.addWidget(button(self.t('save_code'),self.export_code));actions.addStretch();layout.addLayout(actions)
        self.code_language.currentTextChanged.connect(self.change_code_language);self.code_lesson.currentIndexChanged.connect(self.load_lesson);self.change_code_language();return w
    def change_code_language(self,*_):
        self.code_lesson.blockSignals(True);self.code_lesson.clear();self.code_lesson.addItems([self.t(LESSON_KEYS[name]) for name,code in LESSONS[self.code_language.currentText()]]);self.code_lesson.blockSignals(False)
        self.code_run.setEnabled(self.code_language.currentText()=='Python');self.load_lesson()
    def load_lesson(self,*_):
        index=self.code_lesson.currentIndex()
        if index>=0:self.code_editor.setPlainText(LESSONS[self.code_language.currentText()][index][1]);self.code_output.clear()
    def run_lesson(self):
        if self.busy:return
        if self.code_language.currentText()!='Python':return
        code=self.code_editor.toPlainText();self.set_busy(True,'studying')
        def finished(result):
            self.set_busy(False);self.set_mood('studying');self.code_output.setPlainText(result.output+f'\n\n{result.steps} {self.t('lesson_steps')}')
        self.work(lambda:LessonPython().run(code),finished,busy=True)
    def export_code(self):
        suffix={'Python':'py','JavaScript':'js','HTML':'html','CSS':'css'}[self.code_language.currentText()]
        path,_=QFileDialog.getSaveFileName(self,self.t('save_code'),'lafa-lesson.'+suffix,'Code (*.'+suffix+')')
        if path:
            try:Path(path).write_text(self.code_editor.toPlainText(),encoding='utf-8')
            except OSError as error:self.error(str(error))
    def open_timor_headline(self,*_):
        row=self.timor_table.currentRow()
        if 0<=row<len(getattr(self,'timor_items',[])):self.open_web(self.timor_items[row].url)
    def refresh_timor_news(self,automatic=False):
        if self.news_inflight or (not automatic and self.busy) or not self.online:return
        if self.review:self.timor_status.setText(self.t('preview_only'));return
        topic='priority' if automatic else self.timor_topic.currentData();self.news_inflight=True;self.timor_button.setEnabled(False)
        def fetched(report):
            self.news_inflight=False;self.show_timor_news(report);self.timor_button.setEnabled(self.online and not self.busy)
            if automatic and report.sources and self.companion.can_auto_popup():
                item=report.sources[0];self.companion.show_card(Card(self.t('timor_news')+'\n'+item.title+'\n'+item.publisher+' · '+item.published,item.url,'reading','news'),automatic=True)
        def fetch():
            try:return timor_news(topic)
            except Exception:
                raise
        job=Job(fetch);self.jobs.add(job)
        delivery=Delivery(self,job,fetched,False);job.signals.done.connect(delivery.done)
        def failed(message):
            self.news_inflight=False;self.jobs.discard(job);self.timor_button.setEnabled(self.online and not self.busy);self.timor_status.setText(message);delivery.deleteLater()
        # A QObject-bound error delivery preserves GUI thread affinity.
        delivery.failed_handler=failed
        job.signals.error.connect(delivery.report_error);self.pool.start(job)
    def show_timor_news(self,report):
        self.timor_items=report.sources;self.timor_table.setRowCount(len(report.sources))
        for row,item in enumerate(report.sources):
            for column,value in enumerate([item.title,item.publisher,item.published]):self.timor_table.setItem(row,column,QTableWidgetItem(value))
            self.timor_table.setRowHeight(row,58)
        self.timor_status.setText(f'{len(report.sources)} {self.t("headlines")} · {self.t("retrieved")}: {report.retrieved_at}'+(' · '+self.t('unavailable')+': '+', '.join(report.failures) if report.failures else '')+(' · '+self.t('no_topic_news') if not report.sources else ''))
    def check_local_updates(self):
        if self.review or not self.online or not self.settings.companion or not self.settings.local_news_updates or self.companion.paused:return
        if time.monotonic()-self.last_local_news>=self.settings.news_minutes*60:
            self.last_local_news=time.monotonic();self.refresh_timor_news(True)
    def show_cultural_card(self):
        card=self.card_deck.next(self.settings.locale,self.settings.cultural_cards,self.settings.positive_messages)
        # Jokes keep LAFA entertaining between knowledge cards.
        if self.settings.entertainment and self.settings.fun_messages and (card is None or random.random()<0.3):card=Card(personality.joke(self.settings.locale),'','talking','fun')
        if card:self.companion.show_card(card,automatic=True)
    def preview_card(self):
        card=self.card_deck.next(self.settings.locale,self.settings.cultural_cards,self.settings.positive_messages)
        if card:
            dialog=QDialog(self);dialog.setWindowTitle('LAFA · Timor-Leste');layout=QVBoxLayout(dialog);text=label(card.text,13);text.setTextFormat(Qt.PlainText);layout.addWidget(text);layout.addWidget(button(self.t('source'),lambda:self.open_web(card.source)) if card.source else label('LAFA'));dialog.resize(480,270);run(dialog)
    def activate_mode(self,mode):
        if mode=='virtual-start':return  # login: show only the character, no window
        if mode=='desktop':self.reveal()
        elif mode=='settings':self.open_settings()
        elif mode=='configure':self.open_configuration()
        elif mode=='virtual':self.activate_desktop()
        elif mode=='reload':self.reload_settings()
        elif mode in {'enable','disable'}:
            # Used by Eduka-Settings → Lafa-Configuration (the only place to switch it).
            self.settings.companion=mode=='enable'
            if not self.review:self.settings.save()
            self.companion.set_online(self.online)
            if self.settings_dialog:self.companion_check.setChecked(self.settings.companion)
            self.refresh_home()
            if mode=='disable' and not self.isVisible() and not self.settings_dialog and not self.tray and not self.review:self.exit_app()
    def open_configuration(self):
        """Lafa-Configuration lives in Eduka-Settings; LAFA's window is the fallback."""
        if not self.review and eduka.settings_page_available() and eduka.open_settings_page():return
        self.open_settings()
    def open_settings(self):
        if self.settings_dialog is not None:
            self.settings_dialog.show();self.settings_dialog.raise_();return
        dialog=QDialog(self);self.settings_dialog=dialog;dialog.setWindowTitle('Eduka-Settings · LAFA');dialog.resize(900,700)
        layout=QVBoxLayout(dialog);layout.setContentsMargins(22,18,22,18);header=QHBoxLayout();face=QLabel();face.setPixmap(self.atlas.pixmap('idle',52,self.settings.costume));header.addWidget(face)
        names=QVBoxLayout();names.setSpacing(0);names.addWidget(label(self.t('lafa_settings'),20,True));names.addWidget(label(self.t('eduka_settings_note'),9,muted=True));header.addLayout(names,1);layout.addLayout(header)
        layout.addWidget(self.build_settings(),1)
        dialog.finished.connect(lambda:self.close_settings());dialog.show()
    def close_settings(self):
        dialog=self.settings_dialog;self.settings_dialog=None
        if dialog:dialog.deleteLater()
        if not self.isVisible() and not self.settings.companion and not self.tray and not self.review:self.exit_app()
    def add_root(self):
        path=QFileDialog.getExistingDirectory(self,self.t("addfolder"),str(Path.home()))
        if path and not any(self.roots.item(i).text()==path for i in range(self.roots.count())): self.roots.addItem(path)
    def remove_root(self): self.roots.takeItem(self.roots.currentRow())
    def change_outfit(self,outfit):
        """Wardrobe menu on the character: change outfit and remember it."""
        if outfit not in outfits.OUTFITS or outfit==self.settings.costume:return
        new=copy.deepcopy(self.settings);new.costume=outfit
        if not self.review:
            try:new.save()
            except OSError as error:self.error(str(error));return
        self.apply_settings(new)
    def reload_settings(self):
        """Eduka-Settings wrote new preferences; re-read them (never secrets)."""
        if self.busy or self.settings_dialog is not None:return
        self.apply_settings(Settings.load())
    def open_web(self,url):
        if not self.require_online(): return
        try:
            if not safe_web(url): self.error("No browser could open this link.")
        except Exception as e: self.error(str(e))
    def work(self,fn,callback,busy=False):
        job=Job(fn); self.jobs.add(job)
        delivery=Delivery(self,job,callback,busy)
        job.signals.done.connect(delivery.done); job.signals.error.connect(delivery.failed); self.pool.start(job)
    def speak_last(self):
        if self.last_answer: self.speak_text(self.last_answer)
        else:self.hint(self.search_panels["home"]["input"],self.t('nothing_to_read'))
    def speak_text(self,text,voice=None):
        # espeak-ng runs on this computer, so reading aloud also works offline.
        if self.busy:return
        self.set_busy(True,"talking"); self.companion.show_answer(text); lang=voice or self.settings.locale
        def finished(_):self.set_busy(False); self.set_mood("idle")
        rate=self.settings.speech_rate;self.work(lambda:self.voice.speak(text,lang,rate),finished,busy=True)
    def hint(self,widget,text):
        """Gentle feedback for a button that has nothing to work on yet."""
        self.chat_status.setText(text)
        try:
            from .qt import QToolTip
            QToolTip.showText(widget.mapToGlobal(widget.rect().center()),text,widget)
            widget.setFocus()
        except RuntimeError:pass
    def setup_tray(self):
        if not QSystemTrayIcon.isSystemTrayAvailable(): return
        self.tray=QSystemTrayIcon(self.windowIcon(),self); menu=QMenu()
        menu.addAction(self.t('fullwindow'),self.reveal);menu.addAction(self.t('virtual'),self.activate_desktop);menu.addAction(self.t('lafa_settings'),self.open_configuration)
        for key,text in [('continue','continue_learning'),('tasks','tasks_short'),('focus','focus_short'),('os','os_short')]:menu.addAction(self.t(text),lambda checked=False,k=key:self.desktop_action(k))
        menu.addAction(self.t("quit"),self.exit_app); self.tray.setContextMenu(menu)
        self.tray.activated.connect(lambda reason:self.activate_desktop() if reason==QSystemTrayIcon.Trigger else None); self.tray.show()
    def reveal(self): self.showNormal(); self.raise_(); self.activateWindow()
    def closeEvent(self,event):
        if not self.review:
            if self.tray or self.settings.companion or self.settings_dialog:
                self.hide();event.ignore()
            else:self.exit_app();event.accept()
        else:
            self.voice.stop(); self.companion.close(); event.accept()
    def exit_app(self):
        self.voice.stop(); self.companion.hide(); QApplication.instance().quit()
    def lesson_target(self,lesson):
        return "lafa://lesson/age/"+lesson.id if isinstance(lesson,curriculum.AgeLesson) else "lafa://lesson/school/"+lesson_key(lesson)
    def toggle_lesson_favourite(self):
        lesson=self.current_lesson()
        if not lesson:return
        try:state=self.progress.toggle_favourite("lesson",self.lesson_target(lesson),self.lesson_subject.text()+" · "+self.lesson_title.text())
        except ValueError as error:self.error(str(error));return
        self.lesson_star.setText(("★ " if state else "☆ ")+self.t("favourite"));self.render_favourites()
    def retry_mistakes(self):
        """Practise again only the questions answered wrongly (not saved as a result)."""
        if not self.exam or not self.exam.mistakes():return
        retry=self.exam.retry();retry.retry_session=True;self.exam=retry
        self.exam_result.hide();self.exam_feedback.clear();self.exam_retry.hide();self.exam_info.setText(self.t("retry_note"))
        for b in self.exam_buttons:b.show()
        self.show_exam_question()
    def ask_teacher(self):
        """Subject guides search LAFA's local material (no AI)."""
        text=self.teacher_input.text().strip()
        if not text:self.hint(self.teacher_input,self.t('type_first'));return
        outcome=search.search(text,self.settings.locale,(),with_files=False)
        self.teacher_answer.setPlainText(search.summary(outcome,self.settings.locale,tr));self.last_answer=self.teacher_answer.toPlainText()
    # ------------------------------------------------------- reminders & focus
    def build_reminders(self):
        w,layout=page_layout();layout.addWidget(label(self.t("reminders_note"),10,muted=True))
        row=QHBoxLayout();self.reminder_text=QLineEdit();self.reminder_text.setMaxLength(240);self.reminder_text.setPlaceholderText(self.t("remindertext"));self.reminder_text.setAccessibleName(self.t("remindertext"))
        self.reminder_when=QDateTimeEdit(QDateTime.currentDateTime().addSecs(3600));self.reminder_when.setCalendarPopup(True);self.reminder_when.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.reminder_when.setAccessibleName(self.t("when"));self.reminder_add=button(self.t("addreminder"),self.add_reminder,True)
        row.addWidget(self.reminder_text,1);row.addWidget(self.reminder_when);row.addWidget(self.reminder_add);layout.addLayout(row)
        quick=QHBoxLayout();quick.addWidget(label(self.t("in_minutes"),9,muted=True))
        for minutes in (5,15,30,60):quick.addWidget(button(f"+{minutes} min",lambda checked=False,m=minutes:self.add_reminder(m)))
        self.reminder_minutes=QSpinBox();self.reminder_minutes.setRange(1,1440);self.reminder_minutes.setValue(25);self.reminder_minutes.setSuffix(" min");quick.addStretch();layout.addLayout(quick)
        self.reminder_table=QTableWidget(0,3);self.reminder_table.setHorizontalHeaderLabels([self.t("remindertext"),self.t("when"),self.t("remaining")])
        self.reminder_table.horizontalHeader().setSectionResizeMode(0,QHeaderView.Stretch);self.reminder_table.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeToContents);self.reminder_table.horizontalHeader().setSectionResizeMode(2,QHeaderView.ResizeToContents)
        self.reminder_table.verticalHeader().hide();self.reminder_table.setSelectionBehavior(QTableWidget.SelectRows);self.reminder_table.setEditTriggers(QTableWidget.NoEditTriggers);layout.addWidget(self.reminder_table,1)
        row=QHBoxLayout();row.addWidget(button(self.t("cancelreminder"),self.cancel_reminder));row.addStretch();layout.addLayout(row)
        focus=QFrame();focus.setObjectName("panel");fv=QVBoxLayout(focus);fv.setContentsMargins(14,10,14,10)
        top=QHBoxLayout();top.addWidget(label("🎯  "+self.t("focus_title"),12,True),1);self.focus_label=label("",11,True);top.addWidget(self.focus_label);fv.addLayout(top)
        fv.addWidget(label(self.t("focus_session_only"),9,muted=True))
        frow=QHBoxLayout();self.focus_button=button(self.t("focus_start"),self.start_focus,True);frow.addWidget(self.focus_button);frow.addWidget(button(self.t("focus_stop"),self.stop_focus));frow.addStretch();fv.addLayout(frow)
        layout.addWidget(focus);self.render_reminders();return w
    def add_reminder(self,minutes=None):
        text=self.reminder_text.text().strip()
        if not text:self.hint(self.reminder_text,self.t("type_first"));return
        try:
            if isinstance(minutes,int) and not isinstance(minutes,bool):self.reminders.add(minutes,text)
            else:self.reminders.add_at(self.reminder_when.dateTime().toSecsSinceEpoch(),text)
        except (ValueError,OSError) as error:self.error(str(error));return
        self.reminder_text.clear();self.render_reminders();self.chat_status.setText(self.t("reminder_saved"))
    def start_focus(self,minutes=25):
        """A focus timer for this session only (it is not saved)."""
        minutes=minutes if isinstance(minutes,int) and not isinstance(minutes,bool) else 25
        for r in list(self.reminders.items):
            if r.session and not r.fired:self.reminders.cancel(r.id)
        self.reminders.add(minutes,self.t("focus_done"),session=True);self.focus_until=time.time()+minutes*60
        self.render_reminders();self.set_mood("studying");self.chat_status.setText(self.t("focus_started").replace("{n}",str(minutes)))
    def stop_focus(self):
        for r in list(self.reminders.items):
            if r.session:self.reminders.cancel(r.id)
        self.focus_until=0;self.render_reminders()
    def cancel_reminder(self):
        row=self.reminder_table.currentRow();items=[r for r in self.reminders.pending if not r.session]
        if not 0<=row<len(items):self.hint(self.reminder_table,self.t("choose_first"));return
        self.reminders.cancel(items[row].id);self.render_reminders()
    def render_reminders(self):
        if not hasattr(self,"reminder_table"):return
        items=[r for r in self.reminders.pending if not r.session];self.reminder_table.setRowCount(len(items))
        for r,item in enumerate(items):
            seconds=self.reminders.remaining(item);left=f"{seconds//3600}h {seconds%3600//60:02d}m" if seconds>=3600 else f"{seconds//60:02d}:{seconds%60:02d}"
            for c,value in enumerate([item.text,datetime.fromtimestamp(item.due).strftime("%Y-%m-%d %H:%M"),left]):self.reminder_table.setItem(r,c,QTableWidgetItem(value))
        focus=next((r for r in self.reminders.pending if r.session),None)
        if hasattr(self,"focus_label"):
            seconds=self.reminders.remaining(focus) if focus else 0
            self.focus_label.setText(f"⏱ {seconds//60:02d}:{seconds%60:02d}" if focus else "")
    def ring(self,text,missed=False):
        """A reminder fires: bubble, Eduka-Panel notification, tray and a sound."""
        title=self.t("missed_reminder" if missed else "reminders")
        if self.settings.companion:self.companion.show_bubble(title+"\n"+text)
        else:self.chat_status.setText(title+": "+text)
        self.set_mood("serious")
        if self.settings.notifications and not self.review:eduka.notify("LAFA · "+title,text)
        if self.tray:self.tray.showMessage("LAFA",title+"\n"+text,QSystemTrayIcon.Information,10_000)
        if not self.review:
            player=shutil.which("canberra-gtk-play")
            if player:QProcess.startDetached(player,["-i","alarm-clock-elapsed"])
            else:QApplication.beep()
    def poll_reminders(self):
        """Every second, online or offline."""
        try:due=self.reminders.due()
        except OSError:due=[]
        for item in due:self.ring(item.text,item.missed)
        if due:self.focus_until=0 if any(r.session for r in due) else self.focus_until;self.refresh_home()
        if self.current_section()=="activities" or due:self.render_reminders()
    def show_missed_reminders(self):
        """Reminders whose time passed while LAFA was closed: shown once."""
        try:missed=self.reminders.missed()
        except OSError:missed=[]
        if missed:self.ring("\n".join("• "+r.text+" ("+datetime.fromtimestamp(r.due).strftime("%d/%m %H:%M")+")" for r in missed),True);self.render_reminders()
    # --------------------------------------------------------- Timor-Leste news
    def build_timor_news(self):
        w=QWidget();layout=QVBoxLayout(w);layout.setContentsMargins(0,8,0,0)
        layout.addWidget(label(self.t("news_note"),9,muted=True))
        actions_row=QHBoxLayout();self.timor_topic=QComboBox()
        for topic in ['education','arts_culture','technology','development','priority']:self.timor_topic.addItem(self.t(topic),topic)
        actions_row.addWidget(self.timor_topic,1);self.timor_button=button(self.t('refresh'),lambda:self.refresh_timor_news(),True);actions_row.addWidget(self.timor_button);actions_row.addWidget(button(self.t('culture_cards'),self.preview_card));layout.addLayout(actions_row)
        self.timor_table=QTableWidget(0,3);self.timor_table.setHorizontalHeaderLabels([self.t('timor_news'),self.t('publisher'),self.t('published')]);self.timor_table.horizontalHeader().setSectionResizeMode(0,QHeaderView.Stretch)
        self.timor_table.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeToContents);self.timor_table.horizontalHeader().setSectionResizeMode(2,QHeaderView.ResizeToContents);self.timor_table.verticalHeader().hide();self.timor_table.setSelectionBehavior(QTableWidget.SelectRows);self.timor_table.setEditTriggers(QTableWidget.NoEditTriggers);self.timor_table.cellDoubleClicked.connect(self.open_timor_headline);layout.addWidget(self.timor_table,1)
        self.timor_status=label(self.t('source_dates'),9,muted=True);layout.addWidget(self.timor_status);links=QHBoxLayout()
        for name,url in NEWS_LINKS:links.addWidget(button(name,lambda checked=False,u=url:self.open_web(u)))
        links.addStretch();layout.addLayout(links);return w
    # ------------------------------------------------------------ assistant
    def companion_request(self,text):
        """Text typed in the Virtual Assistant's bubble: the same local search."""
        if self.busy:return
        action=None if direct_intent(text) else actions.parse(text)
        if action and action.kind!="search":self.companion.show_answer(self.perform_action(action).text);return
        query=action.text if action else text
        self.set_busy(True,"reading")
        def done(result):
            self.set_busy(False);self.last_answer=result.text;self.set_mood(result.mood)
            # A short result in the popup; the full list waits in Lafa Desktop (same window, never a second one).
            short=result.text if len(result.text)<=420 else result.text[:417].rsplit(" ",1)[0]+"…"
            if result.outcome is not None and result.outcome.items:short+="\n\n"+self.t("popup_found").format(n=len(result.outcome.items))
            self.companion.show_answer(short)
            if result.reminder is not None:
                try:self.reminders.add(*result.reminder);self.render_reminders()
                except ValueError as error:self.companion.show_answer(str(error))
            if result.outcome is not None:self.search_panels["home"]["input"].setText(query);self.show_outcome("home",result.outcome);self.navigate("home")
            if self.settings.speak_answers:self.speak_last()
        self.work(lambda:self.agent.run(query,online=self.online),done,busy=True)
    def perform_action(self,action):
        """Carry out an allowlisted action and say what LAFA did."""
        if action.kind=="app":
            app=actions.APP_BY_KEY[action.target];path=actions.which_app(app)
            if not path:return Result(self.t("app_missing").replace("{name}",app.icon+" "+self.t("app_"+action.target)),"thinking")
            if self.review:return Result(app.icon+" "+self.t("opening").replace("{name}",Path(path).name),"talking")
            ok=started(QProcess.startDetached(path,["--writer"] if action.target=="writer" else []))
            return Result(app.icon+" "+self.t("opening" if ok else "open_failed").replace("{name}",Path(path).name),"talking" if ok else "serious")
        if action.kind=="page":
            self.navigate(action.target)
            if self.isHidden():self.reveal()
            return Result("📂 "+self.t("opening").replace("{name}",self.page_title(action.target)),"talking")
        if action.kind=="search":
            self.navigate("library","search");self.run_search("library",action.text);return Result(self.t("searching"),"reading")
        if action.kind=="remind":
            try:self.reminders.add(action.minutes,action.text);self.render_reminders()
            except ValueError as error:return Result(str(error),"serious")
            return Result("⏰ "+self.t("reminder_set").replace("{minutes}",str(action.minutes)).replace("{text}",action.text),"talking")
        return Result(self.t("try_topic"),"thinking")
    def desktop_action(self,key):
        """Bubble quick buttons and tray menu — all work offline."""
        if key=="os":self.navigate("oshelp","guides");self.reveal()
        elif key=="explore":self.navigate("timor","atlas");self.reveal()
        elif key=="focus":self.start_focus();self.companion.show_answer(self.t("focus_started").replace("{n}","25"))
        elif key=="tasks":
            nxt=self.reminders.next();due=self.planner.due_soon(7)
            lines=[("⏰ "+datetime.fromtimestamp(nxt.due).strftime("%d/%m %H:%M")+" · "+nxt.text)] if nxt else []
            lines+=[f"📝 {h.due} · {h.title}" for h in due[:4]]
            self.companion.show_answer("\n".join(lines) if lines else self.t("nothing_planned"))
        elif key=="continue":
            if self.progress.last:self.continue_learning();self.reveal()
            else:self.navigate("study","lessons");self.reveal()
        elif key=="weather":self.navigate("timor","weather");self.reveal()
        elif key=="news":self.navigate("timor","news");self.reveal()
    def activate_desktop(self):
        """Launcher "Virtual Assistant": show it when enabled; otherwise explain
        that it is switched on in Eduka-Settings → Lafa-Configuration."""
        if self.settings.companion:self.companion.set_online(self.online);self.companion.show_bubble()
        else:self.open_configuration()
    def save_quiet_preference(self):
        if not self.review:
            try:self.settings.save()
            except OSError as error:self.error(str(error))
    # ------------------------------------------------------------- settings & about
    def open_about(self):
        dialog=QDialog(self);dialog.setWindowTitle(self.t("about"));v=QVBoxLayout(dialog);v.setContentsMargins(22,18,22,18)
        head=QHBoxLayout();face=QLabel();face.setPixmap(self.atlas.pixmap("idle",64,self.settings.costume));head.addWidget(face)
        names=QVBoxLayout();names.addWidget(label("Lafa  "+VERSION_LABEL,16,True));names.addWidget(label(self.t("product_name"),10,muted=True));head.addLayout(names,1);v.addLayout(head)
        v.addWidget(label(self.t("about_text"),10));v.addWidget(label(self.t("about_limits"),10,muted=True));v.addWidget(label(self.t("eduka_settings_note"),9,muted=True))
        v.addWidget(button(self.t("close"),dialog.accept,True),0,Qt.AlignRight);dialog.resize(520,380);self.about_dialog=dialog;dialog.show()
    def check_updates(self,force=False):
        """The validated source catalogue (data only) — APT/EUS updates LAFA itself."""
        if self.review or self.updating or not self.online or not self.settings.auto_update:return
        if not force and not updates.due(self.settings.update_hours):return
        self.updating=True
        def finished(value):
            self.updating=False;changed,_=value
            if changed and updates.apply():self.chat_status.setText(self.t('sources_updated'))
        job=Job(updates.check);self.jobs.add(job);delivery=Delivery(self,job,finished,False);job.signals.done.connect(delivery.done)
        def failed(message):self.updating=False;self.jobs.discard(job);delivery.deleteLater()
        delivery.failed_handler=failed;job.signals.error.connect(delivery.report_error);self.pool.start(job)
    def require_online(self):
        """Internet features only: a calm note, never a popup."""
        if not self.online:self.chat_status.setText(self.t("needs_internet_calm"));return False
        return True
    def probe(self):
        if self.probing: return
        self.probing=True
        def finished(value): self.probing=False; self.set_online(value)
        job=Job(online_probe);self.jobs.add(job);delivery=Delivery(self,job,finished,False);job.signals.done.connect(delivery.done)
        def failed(message):self.probing=False;self.jobs.discard(job);self.set_online(False);delivery.deleteLater()
        delivery.failed_handler=failed;job.signals.error.connect(delivery.report_error);self.pool.start(job)
    def set_online(self,value):
        changed=self.online!=bool(value); self.online=bool(value)
        # A calm note: local features are always there; internet only adds sources.
        self.badge.setText(self.t("online") if value else self.t("local_ready"))
        self.badge.setToolTip(self.t("online_note") if value else self.t("offline_intro")+"\n• "+"\n• ".join(offline.offline_features(self.settings.locale)))
        if changed and value and not self.review:QTimer.singleShot(8000,self.check_updates)
        self.companion.set_online(bool(value)); self.update_buttons()
    def update_buttons(self):
        net=self.online
        for name,panel in getattr(self,"search_panels",{}).items():panel["internet"].setEnabled(net)
        if hasattr(self,"pack_button"):self.pack_button.setEnabled(net and not getattr(self,"pack_running",False))
        for attr in ("learn_button","weather_button","news_button","city_confirm","timor_button","saved_update"):
            b=getattr(self,attr,None)
            if b is not None:b.setEnabled(net and not (attr=="timor_button" and self.news_inflight))
        if self.settings_dialog:self.settings_save_button.setEnabled(not self.busy)
        if hasattr(self,"code_run"):self.code_run.setEnabled(not self.busy and self.code_language.currentText()=='Python')
    def set_busy(self,value,mood="thinking"):
        self.busy=value; self.companion.busy=value
        self.chat_status.setText(self.t("working") if value else ""); self.update_buttons()
        if value: self.set_mood(mood)
    def set_mood(self,state):
        self.companion.set_state(state)
    def error(self,text):
        """Errors appear in the status line and the bubble — no popups."""
        self.chat_status.setText(str(text));self.chat_status.setToolTip(str(text))
        if self.settings.companion:self.companion.show_answer(str(text))
    def build_settings(self):
        w=QWidget();outer=QVBoxLayout(w);outer.setContentsMargins(0,0,0,0);row=QHBoxLayout();row.setSpacing(16);outer.addLayout(row,1)
        self.settings_categories=QListWidget();self.settings_categories.setObjectName('categories');self.settings_categories.setFixedWidth(210);self.settings_categories.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff);self.settings_categories.setWordWrap(True)
        self.settings_tabs=QStackedWidget();row.addWidget(self.settings_categories);row.addWidget(self.settings_tabs,1)
        self.settings_categories.currentRowChanged.connect(self.settings_tabs.setCurrentIndex)
        def section(title,glyph):
            body=QWidget();form=QFormLayout(body);form.setContentsMargins(18,16,18,12);form.setSpacing(10);form.addRow(label(glyph+'  '+self.t(title),15,True))
            # Labels above their fields: nothing is cut off on small screens or in long languages.
            form.setRowWrapPolicy(QFormLayout.WrapAllRows);form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
            panel=QFrame();panel.setObjectName('panel');pl=QVBoxLayout(panel);pl.setContentsMargins(0,0,0,0)
            scroll=QScrollArea();scroll.setWidgetResizable(True);scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff);scroll.setWidget(body);pl.addWidget(scroll)
            self.settings_tabs.addWidget(panel);self.settings_categories.addItem(glyph+'  '+self.t(title));return form
        def checks(form,items):
            for attr,key,value in items:
                check=QCheckBox(self.t(key));check.setChecked(value);setattr(self,attr,check);form.addRow('',check)
        def choice(form,attr,key,values,current):
            box=QComboBox()
            for value in values:box.addItem(self.t(value) if not isinstance(value,tuple) else value[1],value if not isinstance(value,tuple) else value[0])
            box.setCurrentIndex(max(0,box.findData(current)));setattr(self,attr,box);form.addRow(self.t(key),box)
        def number(form,attr,key,low,high,current,step=1):
            box=QSpinBox();box.setRange(low,high);box.setSingleStep(step);box.setValue(current);setattr(self,attr,box);form.addRow(self.t(key),box)
        virtual=section('virtual_settings','🐊')
        self.companion_check=QCheckBox(self.t('activate_virtual'));self.companion_check.setChecked(self.settings.companion);virtual.addRow('',self.companion_check)
        virtual.addRow('',label(self.t('virtual_settings_note'),9,muted=True))
        self.costume_select=QComboBox()
        for name in outfits.OUTFITS:self.costume_select.addItem(self.t(name),name)
        self.costume_select.setCurrentIndex(self.costume_select.findData(self.settings.costume));virtual.addRow(self.t('costume'),self.costume_select)
        choice(virtual,'size_select','character_size',['small','normal','large'],self.settings.character_size)
        choice(virtual,'walk_select','walk_speed',['slow','normal','fast'],self.settings.walk_speed)
        choice(virtual,'animation_select','animation_speed',['slow','normal','fast'],self.settings.animation_speed)
        checks(virtual,[('quiet_check','quiet_mode',self.settings.quiet_mode),('motion_check','reduce_motion',self.settings.reduce_motion),('fun_mode_check','entertainment_setting',self.settings.entertainment),
                        ('roam_check','roam',self.settings.roam),('eduka_panel_check','follow_eduka_panel',self.settings.follow_eduka_panel),('panel_check','panel_walk',self.settings.panel_roam),('greet_check','greet_by_time',self.settings.greet_by_time),('session_check','start_with_session',self.settings.start_with_session)])
        number(virtual,'messages_interval','messages_per_hour',0,20,self.settings.messages_per_hour)
        self.panel_select=QComboBox()
        for edge in ['bottom','top']:self.panel_select.addItem(self.t(edge),edge)
        self.panel_select.setCurrentIndex(self.panel_select.findData(self.settings.panel_edge));virtual.addRow(self.t('panel_edge'),self.panel_select)
        self.panel_height=QSpinBox();self.panel_height.setRange(0,160);self.panel_height.setValue(self.settings.panel_height);virtual.addRow(self.t('panel_height'),self.panel_height)
        virtual.addRow('',label(self.t('wayland_note'),9,muted=True))
        persona=section('personality_settings','😄')
        checks(persona,[('hover_check','hover_questions',self.settings.hover_questions),('chatter_check','chatter',self.settings.chatter),('fun_check','fun_messages',self.settings.fun_messages),('personal_check','personal',self.settings.personal_activities),('positive_check','positive',self.settings.positive_messages),('culture_check','culture_cards',self.settings.cultural_cards),('local_news_check','local_updates',self.settings.local_news_updates)])
        self.activity_interval=QSpinBox();self.activity_interval.setRange(20,600);self.activity_interval.setSingleStep(10);self.activity_interval.setValue(self.settings.idle_seconds);persona.addRow(self.t('activity_seconds'),self.activity_interval)
        number(persona,'balloon_interval','balloon_seconds',3,20,self.settings.balloon_seconds)
        self.card_interval=QSpinBox();self.card_interval.setRange(1,120);self.card_interval.setValue(self.settings.card_minutes);persona.addRow(self.t('card_interval'),self.card_interval)
        self.news_interval=QSpinBox();self.news_interval.setRange(10,240);self.news_interval.setValue(self.settings.news_minutes);persona.addRow(self.t('news_interval'),self.news_interval)
        general=section('language_sources','🌐');self.language=QComboBox()
        for name,code in [(self.t('system_language'),'system'),('English','en'),('Tetun','tet'),('Português','pt'),('Bahasa Indonesia','id')]:self.language.addItem(name,code)
        self.language.setCurrentIndex(self.language.findData(self.settings.language));general.addRow(self.t('language'),self.language)
        self.auto_read=QCheckBox(self.t('autoread'));self.auto_read.setChecked(self.settings.speak_answers);general.addRow('',self.auto_read)
        number(general,'speech_interval','speech_rate',80,260,self.settings.speech_rate,5)
        checks(general,[('update_check','auto_update',self.settings.auto_update)])
        number(general,'update_interval','update_hours',6,168,self.settings.update_hours)
        general.addRow('',label(self.t('no_ai_note'),9,muted=True))
        desk=section('desktop_settings','🏫')
        choice(desk,'start_select','start_page',[(key,self.page_title(key)) for key in START_PAGES],self.settings.start_page)
        checks(desk,[('eduka_theme_check','follow_eduka_theme',self.settings.follow_eduka_theme),('notify_check','notifications',self.settings.notifications),('smooth_check','smooth_scrolling',self.settings.smooth_scrolling),('depth_check','depth_effects',self.settings.depth_effects)])
        folders=section('files_weather','📁');self.home_city=QLineEdit(self.settings.weather_city);self.home_city.setMaxLength(120);folders.addRow(self.t('city'),self.home_city)
        self.home_coords=QLineEdit(f'{self.settings.weather_latitude}, {self.settings.weather_longitude}');folders.addRow(self.t('coords'),self.home_coords)
        self.home_timezone=QLineEdit(self.settings.weather_timezone);self.home_timezone.setMaxLength(100);folders.addRow(self.t('timezone'),self.home_timezone)
        self.roots=QListWidget();self.roots.addItems(self.settings.roots);self.roots.setMaximumHeight(200);folders.addRow(self.t('files'),self.roots)
        row=QHBoxLayout();row.addWidget(button(self.t('addfolder'),self.add_root));row.addWidget(button(self.t('removefolder'),self.remove_root));folders.addRow('',row)
        self.settings_categories.setCurrentRow(0)
        actions_row=QHBoxLayout();self.settings_save_button=button(self.t('save'),self.save_settings,True);self.settings_save_button.setEnabled(not self.busy);actions_row.addWidget(self.settings_save_button);actions_row.addStretch();outer.addLayout(actions_row);return w
    def save_settings(self):
        if self.busy: return
        try:
            latitude,longitude=[float(v.strip()) for v in self.home_coords.text().split(',')]
            location=Location(self.home_city.text().strip(),latitude,longitude,self.home_timezone.text().strip() or 'auto'); location.validate()
            if not location.name:raise ValueError(self.t('need_city'))
            draft=copy.deepcopy(self.settings)
            draft.language=self.language.currentData();draft.greet_by_time=self.greet_check.isChecked()
            draft.companion=self.companion_check.isChecked(); draft.roam=self.roam_check.isChecked(); draft.speak_answers=self.auto_read.isChecked(); draft.roots=[self.roots.item(i).text() for i in range(self.roots.count())]
            draft.costume=self.costume_select.currentData();draft.positive_messages=self.positive_check.isChecked();draft.cultural_cards=self.culture_check.isChecked();draft.local_news_updates=self.local_news_check.isChecked()
            draft.card_minutes=self.card_interval.value();draft.news_minutes=self.news_interval.value();draft.panel_roam=self.panel_check.isChecked();draft.panel_edge=self.panel_select.currentData();draft.panel_height=self.panel_height.value()
            draft.personal_activities=self.personal_check.isChecked(); draft.idle_seconds=self.activity_interval.value()
            draft.hover_questions=self.hover_check.isChecked();draft.chatter=self.chatter_check.isChecked();draft.fun_messages=self.fun_check.isChecked()
            draft.character_size=self.size_select.currentData();draft.walk_speed=self.walk_select.currentData();draft.animation_speed=self.animation_select.currentData()
            draft.follow_eduka_panel=self.eduka_panel_check.isChecked();draft.start_with_session=self.session_check.isChecked();draft.balloon_seconds=self.balloon_interval.value()
            draft.quiet_mode=self.quiet_check.isChecked();draft.reduce_motion=self.motion_check.isChecked();draft.entertainment=self.fun_mode_check.isChecked();draft.messages_per_hour=self.messages_interval.value()
            draft.start_page=self.start_select.currentData();draft.follow_eduka_theme=self.eduka_theme_check.isChecked();draft.notifications=self.notify_check.isChecked()
            draft.smooth_scrolling=self.smooth_check.isChecked();draft.depth_effects=self.depth_check.isChecked()
            draft.auto_update=self.update_check.isChecked();draft.update_hours=self.update_interval.value();draft.speech_rate=self.speech_interval.value()
            draft.weather_city=location.name; draft.weather_latitude=latitude; draft.weather_longitude=longitude; draft.weather_timezone=location.timezone
            if not self.review:draft.save()
            self.apply_settings(draft)
            if self.settings_dialog:self.settings_dialog.accept()
        except Exception as e: self.error(str(e))
    def apply_settings(self,new):
        """Apply saved preferences live; keep lesson code and the current section."""
        previous=self.current_section();was_enabled=self.settings.companion
        old_code=self.code_editor.toPlainText();old_code_language=self.code_language.currentText();old_lesson=self.code_lesson.currentIndex();old_output=self.code_output.toPlainText()
        old_search=self.search_panels["home"]["input"].text()
        for field,value in asdict(new).items():setattr(self.settings,field,value)
        self.generation+=1
        self.build_ui()
        self.code_language.setCurrentText(old_code_language);self.code_lesson.setCurrentIndex(old_lesson);self.code_editor.setPlainText(old_code);self.code_output.setPlainText(old_output)
        self.search_panels["home"]["input"].setText(old_search)
        app=QApplication.instance();qss=style_sheet(self.settings)
        # Re-styling every widget is costly; only do it when the theme really changed.
        if app and app.styleSheet()!=qss:app.setStyleSheet(qss)
        self.navigate(previous);self.companion.apply_preferences();self.companion.retranslate();self.set_online(self.online)
        if not was_enabled and self.settings.companion:self.last_local_news=time.monotonic()

def main():
    parser=argparse.ArgumentParser(description='LAFA Desktop and LAFA Virtual Assistant')
    parser.add_argument('--review',action='store_true',help='Visual review; no network calls or saved settings')
    roles=parser.add_mutually_exclusive_group()
    roles.add_argument('--window',action='store_true',help='Open LAFA Desktop (default)')
    roles.add_argument('--settings',action='store_true',help='Open the dedicated LAFA settings surface')
    roles.add_argument('--virtual',action='store_true',help='Show the enabled virtual assistant, or open Settings')
    roles.add_argument('--virtual-enable',action='store_true',help='Enable the virtual assistant; used by Eduka-Settings')
    roles.add_argument('--virtual-disable',action='store_true',help='Disable the virtual assistant; used by Eduka-Settings')
    roles.add_argument('--configure',action='store_true',help='Open Lafa-Configuration in Eduka-Settings (or LAFA settings)')
    roles.add_argument('--reload',action='store_true',help='Re-read preferences saved by Eduka-Settings')
    roles.add_argument('--autostart',action='store_true',help='Session start: run only when the Virtual Assistant is enabled')
    args=parser.parse_args()
    eduka.prefer_xwayland()
    if args.autostart:
        startup=Settings.load()
        if not (startup.companion and startup.start_with_session):return 0
    mode='virtual-start' if args.autostart else 'configure' if args.configure else 'settings' if args.settings else 'virtual' if args.virtual else 'enable' if args.virtual_enable else 'disable' if args.virtual_disable else 'reload' if args.reload else 'desktop'
    prepare_application()
    app=QApplication(sys.argv);app.setApplicationName('LAFA');app.setOrganizationName('Edukasaun');app.setStyle('Fusion');app.setStyleSheet(style_sheet(Settings.load()) if not args.review else STYLE)
    lock=None;activation=None
    if not args.review:
        config_path().parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        lock=QLockFile(str(config_path().parent/'instance.lock'));lock.setStaleLockTime(0)
        if not lock.tryLock(100):
            if mode=='virtual-start':return 0  # already running
            if not activate_existing(server_name(config_path().parent),mode):QMessageBox.information(None,'LAFA','LAFA is starting. Try the app icon again in a few seconds.')
            return 0
    if mode=='reload' and lock:
        lock.unlock();return 0  # Not running: preferences load at the next start.
    app.setQuitOnLastWindowClosed(args.review)
    window=Window(review=args.review);window.activate_mode(mode)
    if mode=='disable' and not args.review:
        lock.unlock();return 0
    if not args.review:
        try:
            activation=ActivationServer(server_name(config_path().parent),window);activation.activated.connect(window.activate_mode);app.aboutToQuit.connect(activation.close)
        except RuntimeError:window.chat_status.setText('Local launcher activation unavailable; use LAFA Settings or the tray.')
    app.aboutToQuit.connect(window.voice.stop)
    code=run(app)
    if lock:lock.unlock()
    if BINDING=='PyQt5':
        # PyQt5 may crash while Python destroys Qt objects in arbitrary order
        # at shutdown (Eduka-Desktop does the same); state is already saved.
        sys.stdout.flush();sys.stderr.flush();os._exit(int(code or 0))
    return code

if __name__=='__main__':raise SystemExit(main())

