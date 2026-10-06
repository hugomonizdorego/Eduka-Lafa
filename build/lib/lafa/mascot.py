"""Floating assistant bubble and illustrated activity renderer."""
from pathlib import Path
import json
import math
import random
import time
from datetime import datetime
from PySide6.QtCore import Qt,QTimer,QPointF,QEvent,Signal
from PySide6.QtGui import QPixmap,QPainter,QGuiApplication,QPolygonF,QColor
from PySide6.QtWidgets import QWidget,QMenu,QFrame,QVBoxLayout,QHBoxLayout,QLabel,QLineEdit,QPushButton,QPlainTextEdit,QApplication
from .config import STATES,IDLE_ACTIVITIES
from .i18n import tr

ASSET=Path(__file__).parent/'assets'/'lafa-atlas.png'

def greeting_key(hour):
    """Local time-of-day greeting used by the Virtual Assistant."""
    return 'greet_morning' if 4<=hour<11 else 'greet_afternoon' if 11<=hour<18 else 'greet_evening'

class Atlas:
    def __init__(self):
        self.poses={};self.traditional={}
        self.sheet=QPixmap(str(ASSET))
        for image,manifest in [(ASSET,'atlas.json'),(ASSET.with_name('lafa-activities.png'),'activities.json'),(ASSET.with_name('lafa-traditional.png'),'traditional.json')]:
            sheet=QPixmap(str(image))
            if sheet.isNull():raise RuntimeError('LAFA character atlas is missing.')
            metadata=json.loads(image.with_name(manifest).read_text());size=metadata['canvas']
            for state in metadata['states']:
                crop=sheet.copy(*metadata['rects'][state]);pose=QPixmap(size,size);pose.fill(Qt.transparent)
                painter=QPainter(pose);painter.drawPixmap((size-crop.width())//2,(size-crop.height())//2,crop);painter.end()
                if manifest=='traditional.json':self.traditional[state]=pose
                else:self.poses[state]=pose
        for state in ['tebe','bidu']:self.poses[state]=self.traditional[state]
        if set(STATES)-self.poses.keys():raise RuntimeError('A LAFA pose is missing.')
    def pixmap(self,state='idle',size=180,costume='casual'):
        poses=self.traditional if costume=='traditional' and state in self.traditional else self.poses
        return poses.get(state,poses.get('idle',self.poses['idle'])).scaled(size,size,Qt.KeepAspectRatio,Qt.SmoothTransformation)

class Character(QWidget):
    clicked=Signal()
    def __init__(self,atlas,parent=None,size=190):
        super().__init__(parent);self.atlas=atlas;self.state='idle';self.costume='casual';self.phase=0;self.animated=True;self.hop_phase=0.0
        self.setFixedSize(size,size+16)
        self.timer=QTimer(self);self.timer.timeout.connect(self.tick);self.timer.start(90)
    def set_state(self,state):self.state=state if state in STATES else 'idle';self.update()
    def animate(self,enabled):
        self.animated=enabled
        if enabled:self.timer.start(90)
        else:self.timer.stop()
        self.update()
    def tick(self):
        self.phase+=0.14
        if self.hop_phase>0:self.hop_phase=max(0.0,self.hop_phase-0.12)
        self.update()
    def hop(self):
        """Short happy jump when LAFA answers; skipped while animation is paused."""
        if self.animated:self.hop_phase=1.0
    def paintEvent(self,event):
        painter=QPainter(self);painter.setRenderHint(QPainter.SmoothPixmapTransform)
        amplitude=1 if self.state=='sleeping' else 6 if self.state in {'tebe','bidu'} else 2.6
        bob=math.sin(self.phase)*amplitude if self.animated else 0
        if self.animated and self.hop_phase>0:bob-=math.sin(self.hop_phase*math.pi)*14
        angle=math.sin(self.phase)*(5 if self.state in {'tebe','bidu'} else 1.7) if self.animated and self.state in {'walking','gaming','talking','stretching','tebe','bidu'} else 0
        painter.translate(self.width()/2,self.height()/2+bob);painter.rotate(angle)
        if self.state=='walking' and getattr(self,'direction',1)<0:painter.scale(-1,1)
        pix=self.atlas.pixmap(self.state,self.width()-10,self.costume)
        painter.drawPixmap(-pix.width()//2,-pix.height()//2,pix)
    def mouseReleaseEvent(self,event):
        if event.button()==Qt.LeftButton:self.clicked.emit()

class Companion(QWidget):
    open_requested=Signal()
    quit_requested=Signal()
    user_request=Signal(str)
    action_requested=Signal(str)
    public_search_requested=Signal(str)
    activity_changed=Signal(str)
    voice_requested=Signal()
    settings_requested=Signal()
    source_requested=Signal(str)
    card_requested=Signal()
    def __init__(self,atlas,settings,clock=time.monotonic):
        super().__init__();self.settings=settings;self.clock=clock
        self.online=False;self.paused=False;self._busy=False;self.drag=None;self.moved=False;self.direction=1
        self.last_activity=clock();self.last_idle_change=clock();self.last_card=clock();self.introduced=False;self.current_source="";self.popup_deadline=0
        self.setWindowFlags(Qt.Tool|Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle('LAFA Virtual Assistant')
        self.setToolTip(tr(settings.locale,'pet_help'))
        layout=QVBoxLayout(self);layout.setContentsMargins(8,8,8,8);layout.setSpacing(12)
        self.bubblebox=QFrame();self.bubblebox.setObjectName('speech')
        self.bubblebox.setStyleSheet('QFrame#speech {background:#fffffb;border:1px solid #d6e8d8;border-radius:16px;}')
        self.bubblebox.setFixedHeight(324)
        col=QVBoxLayout(self.bubblebox);col.setContentsMargins(16,12,16,12);col.setSpacing(7)
        header=QHBoxLayout();name=QLabel('LAFA');name.setStyleSheet('font-size:19px;font-weight:600;color:#28613b;');header.addWidget(name);header.addStretch()
        self.status=QLabel();self.status.setStyleSheet('font-size:10px;color:#64816b;');header.addWidget(self.status)
        close=QPushButton('×');close.setFixedWidth(28);close.setStyleSheet('border:0;background:transparent;font-size:17px;padding:2px;');close.clicked.connect(self.collapse);header.addWidget(close);col.addLayout(header)
        self.message=QPlainTextEdit();self.message.setReadOnly(True);self.message.setFixedHeight(86);self.message.setStyleSheet('border:0;background:transparent;font-size:13px;padding:0;');col.addWidget(self.message)
        quick=QHBoxLayout();self.quick_buttons=[]
        for key in ['weather','news','focus']:
            b=QPushButton();b.setStyleSheet('font-size:11px;padding:6px 8px;');b.clicked.connect(lambda checked=False,k=key:self.action_requested.emit(k));quick.addWidget(b);self.quick_buttons.append((key,b))
        col.addLayout(quick)
        row=QHBoxLayout();self.input=QLineEdit();self.input.returnPressed.connect(self.submit);self.send_button=QPushButton('➤');self.send_button.setFixedWidth(42);self.send_button.clicked.connect(self.submit)
        row.addWidget(self.input,1);row.addWidget(self.send_button);col.addLayout(row)
        self.public_button=QPushButton();self.public_button.setStyleSheet('font-size:10px;padding:4px 8px;');self.public_button.clicked.connect(self.submit_public);col.addWidget(self.public_button)
        footer=QHBoxLayout();self.full_button=QPushButton();self.full_button.setStyleSheet('padding:5px 8px;font-size:10px;');self.full_button.clicked.connect(self.open_requested.emit);footer.addWidget(self.full_button)
        self.voice_button=QPushButton();self.voice_button.setStyleSheet('padding:5px 8px;font-size:10px;');self.voice_button.clicked.connect(self.voice_requested.emit);footer.addWidget(self.voice_button);self.source_button=QPushButton();self.source_button.setStyleSheet('padding:5px 8px;font-size:10px;');self.source_button.clicked.connect(lambda:self.source_requested.emit(self.current_source));self.source_button.hide();footer.addWidget(self.source_button);footer.addStretch();col.addLayout(footer)
        layout.addWidget(self.bubblebox)
        self.pet=Character(atlas,self,size=176);self.pet.costume=settings.costume;self.pet.clicked.connect(self.toggle_bubble);layout.addWidget(self.pet,0,Qt.AlignRight)
        self.idle_timer=QTimer(self);self.idle_timer.setInterval(1000);self.idle_timer.timeout.connect(self.choose_idle)
        self.walk_timer=QTimer(self);self.walk_timer.setInterval(120);self.walk_timer.timeout.connect(self.walk)
        self.bubblebox.hide();self.setFixedSize(192,208);self.animate(False)
        self.retranslate();self.message.setPlainText(tr(settings.locale,'welcome_desktop'))
        rect=QGuiApplication.primaryScreen().availableGeometry();self.move(rect.right()-self.width()-20,rect.bottom()-self.height()-30)
        QApplication.instance().installEventFilter(self)
        self.pet.installEventFilter(self)
    @property
    def timer(self):return self.pet.timer
    @property
    def state(self):return self.pet.state
    @property
    def busy(self):return self._busy
    @busy.setter
    def busy(self,value):
        if self._busy!=bool(value):self.mark_activity()
        self._busy=bool(value);self.update_controls()
    def animate(self,enabled):self.pet.animate(enabled)
    def set_state(self,state):self.pet.set_state(state);self.activity_changed.emit(self.pet.state)
    def retranslate(self):
        lang=self.settings.locale
        self.setToolTip(tr(lang,'pet_help'))
        self.input.setPlaceholderText(tr(lang,'ask'));self.full_button.setText(tr(lang,'desktop'));self.voice_button.setText(tr(lang,'listen'))
        for key,b in self.quick_buttons:b.setText(tr(lang,'timor_news' if key=='news' else key))
        self.status.setText(tr(lang,'online') if self.online else tr(lang,'offline'));self.source_button.setText(tr(lang,'source'));self.public_button.setText(tr(lang,'public_search'))
    def mark_activity(self):self.popup_deadline=0;self.last_activity=self.clock();self.last_idle_change=self.last_activity
    def eventFilter(self,obj,event):
        # Observe only this application's input events, never other desktop apps.
        if event.type() in {QEvent.MouseButtonPress,QEvent.KeyPress,QEvent.TouchBegin}:
            self.mark_activity()
        if obj is self.pet:
            if event.type()==QEvent.MouseButtonPress and event.button()==Qt.LeftButton:
                self.drag=event.globalPosition().toPoint()-self.pos();self.moved=False;return True
            if event.type()==QEvent.MouseMove and self.drag is not None and event.buttons()&Qt.LeftButton:
                self.moved=True
                if QGuiApplication.platformName().startswith('wayland'):
                    if self.windowHandle():self.windowHandle().startSystemMove()
                else:self.move(event.globalPosition().toPoint()-self.drag)
                return True
            if event.type()==QEvent.MouseButtonRelease and event.button()==Qt.LeftButton:
                if not self.moved:self.toggle_bubble()
                self.drag=None;return True
        return super().eventFilter(obj,event)
    def set_online(self,online):
        changed=self.online!=bool(online);self.online=bool(online);self.pet.costume=self.settings.costume
        self.retranslate();self.update_controls()
        if self.online and self.settings.companion:
            self.show();self.animate(not self.paused)
            if not self.paused:
                if not self.idle_timer.isActive():self.idle_timer.start()
                if not self.walk_timer.isActive():self.walk_timer.start()
                if changed:self.mark_activity()
                if not self.introduced:
                    self.introduced=True;self.set_state('idle');self.show_bubble(self.introduction());self.popup_deadline=self.clock()+18
            else:self.idle_timer.stop();self.walk_timer.stop()
        else:
            self.hide();self.animate(False);self.idle_timer.stop();self.walk_timer.stop()
            if not self.settings.companion:self.introduced=False
    def introduction(self,hour=None):
        lang=self.settings.locale;text=tr(lang,'welcome_virtual')
        if getattr(self.settings,'greet_by_time',True):text=tr(lang,greeting_key(datetime.now().hour if hour is None else hour))+' '+text
        return text
    def update_controls(self):
        if not hasattr(self,'send_button'):return
        enabled=self.online and not self._busy
        self.public_button.setEnabled(enabled);self.send_button.setEnabled(enabled);self.input.setEnabled(enabled);self.voice_button.setEnabled(enabled)
        for _,b in self.quick_buttons:b.setEnabled(enabled)
    def choose_idle(self):
        now=self.clock()
        if not self.online or self.paused or self.busy or self.drag:return
        if self.popup_deadline and now>=self.popup_deadline:
            self.popup_deadline=0
            if not self.input.text().strip():self.collapse()
        if self.bubblebox.isVisible() or self.input.text().strip():return
        if (self.settings.cultural_cards or self.settings.positive_messages) and now-self.last_activity>=60 and now-self.last_card>=self.settings.card_minutes*60:
            self.last_card=now;self.card_requested.emit();return
        if now-max(self.last_activity,self.last_idle_change)<60:return
        choices=[s for s in IDLE_ACTIVITIES if s!=self.state and (self.settings.personal_activities or s not in {'bathing','toilet'})]
        self.set_state(random.choice(choices));self.last_idle_change=now
    def walk(self):
        if not self.online or self.paused or not self.settings.companion or self.state!='walking' or self.busy or not self.settings.roam or self.drag or self.bubblebox.isVisible():return
        if QGuiApplication.platformName()!='xcb':return
        screen=QGuiApplication.screenAt(self.pos()) or QGuiApplication.primaryScreen();rect=screen.geometry() if self.settings.panel_roam else screen.availableGeometry()
        nx=self.x()+self.direction*3
        if nx<rect.left() or nx+self.width()>rect.right()+1:
            self.direction*=-1;nx=self.x()+self.direction*3
        self.pet.direction=self.direction
        y=self.y()
        if self.settings.panel_roam:
            y=rect.bottom()-self.settings.panel_height-self.height()+1 if self.settings.panel_edge=='bottom' else rect.top()+self.settings.panel_height
        self.move(max(rect.left(),min(nx,rect.right()-self.width()+1)),y)
    def resize_overlay(self,expanded):
        anchor=self.geometry().bottomRight()
        self.bubblebox.setVisible(expanded);self.setFixedSize(440 if expanded else 192,544 if expanded else 208)
        if QGuiApplication.platformName()=='xcb':
            rect=(QGuiApplication.screenAt(anchor) or QGuiApplication.primaryScreen()).availableGeometry()
            self.move(max(rect.left(),min(anchor.x()-self.width(),rect.right()-self.width())),max(rect.top(),min(anchor.y()-self.height(),rect.bottom()-self.height())))
        self.update()
    def show_bubble(self,text=None):
        if not self.online or not self.settings.companion:return
        if text is not None:self.message.setPlainText(text);self.current_source="";self.source_button.hide()
        self.resize_overlay(True);self.mark_activity();self.show();self.raise_()
    def can_auto_popup(self):
        return self.online and self.settings.companion and not self.paused and not self.busy and self.drag is None and not self.bubblebox.isVisible() and not self.input.text().strip() and self.clock()-self.last_activity>=60
    def show_card(self,card,automatic=False):
        if not self.online or not self.settings.companion or self.busy or (automatic and not self.can_auto_popup()):return
        self.set_state(card.mood);self.show_bubble(card.text);self.current_source=card.source
        self.source_button.setVisible(bool(card.source));self.popup_deadline=self.clock()+15
    def toggle_bubble(self):
        if self.bubblebox.isVisible():self.collapse()
        else:self.show_bubble()
    def collapse(self):self.resize_overlay(False);self.mark_activity()
    def show_answer(self,text):
        self.current_source="";self.source_button.hide();self.popup_deadline=0
        self.message.setPlainText(text)
        if self.bubblebox.isVisible():self.message.verticalScrollBar().setValue(0)
    def submit_public(self):
        text=self.input.text().strip()
        if text and self.online and not self.busy:self.public_search_requested.emit(text)
    def submit(self):
        text=self.input.text().strip()
        if text and self.online and not self.busy:
            self.input.clear();self.mark_activity();self.user_request.emit(text)
    def paintEvent(self,event):
        if not self.bubblebox.isVisible():return
        p=QPainter(self);p.setRenderHint(QPainter.Antialiasing);p.setPen(Qt.NoPen);p.setBrush(QColor('#fffffb'))
        y=self.bubblebox.geometry().bottom()-1;x=self.width()-76
        p.drawPolygon(QPolygonF([QPointF(x-12,y),QPointF(x+12,y),QPointF(x,y+14)]))
    def contextMenuEvent(self,event):
        self.mark_activity();menu=QMenu(self);lang=self.settings.locale
        menu.addAction(tr(lang,'open_settings'),self.settings_requested.emit);menu.addAction(tr(lang,'virtual'),self.show_bubble);menu.addAction(tr(lang,'fullwindow'),self.open_requested.emit)
        for key in ['weather','news','focus']:menu.addAction(tr(lang,'timor_news' if key=='news' else key),lambda checked=False,k=key:self.action_requested.emit(k))
        moods=menu.addMenu(tr(lang,'mood'))
        for state in STATES:moods.addAction(tr(lang,state),lambda checked=False,s=state:self.set_state(s))
        pause=menu.addAction(tr(lang,'pause'));pause.setCheckable(True);pause.setChecked(self.paused);pause.triggered.connect(self.toggle_pause)
        menu.addSeparator();menu.addAction(tr(lang,'quit'),self.quit_requested.emit);menu.exec(event.globalPos())
    def toggle_pause(self,paused):self.paused=paused;self.set_online(self.online)
