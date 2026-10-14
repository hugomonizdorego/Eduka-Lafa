"""LAFA Virtual Assistant: the animated character that lives on the Eduka-Panel.

Behaviour cycle while nobody needs help:
    walk to a new spot on the panel  ->  do an activity (study, read, game, bath…)
    ->  walk again  ->  …
Touching LAFA with the cursor stops the walk and shows a speech balloon with a
curious "can I help?" question. Clicking opens the full chat bubble. Busy work,
an open chat, an unsent draft, dragging, pause and offline state suppress the
cycle. Only events inside LAFA's own windows are observed.
"""
from pathlib import Path
import json
import math
import random
import time
from datetime import datetime
from .qt import Qt,QTimer,QPointF,QRectF,QRect,QEvent,Signal,QPixmap,QPainter,QGuiApplication,QPolygonF,QColor,QPainterPath,QPen,QCursor
from .qt import QWidget,QMenu,QFrame,QVBoxLayout,QHBoxLayout,QLabel,QLineEdit,QPushButton,QPlainTextEdit,QApplication,global_point,run
from .config import STATES,IDLE_ACTIVITIES,ENTERTAINMENT
from .i18n import tr
from . import personality, eduka, outfits, roles
from .motion import Motion

ASSET=Path(__file__).parent/'assets'/'lafa-atlas.png'
COMPACT=(192,208)
EXPANDED=(440,544)
PET_SIZES={'small':132,'normal':176,'large':220}
WALK_STEPS={'slow':2,'normal':3,'fast':5}
ANIMATION_RATES={'slow':0.6,'normal':1.0,'fast':1.6}

BUBBLE_QSS='''
QFrame#speech {background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 rgba(255,255,255,250),stop:1 rgba(236,248,242,246)); border:1px solid rgba(0,168,121,0.28); border-radius:22px;}
QLabel#bubblename {font-size:19px; font-weight:800; color:#0f5a46; background:transparent;}
QLabel#bubbleduty {font-size:10px; color:#6b7f78; background:transparent; padding-left:4px;}
QLabel#bubblestatus {font-size:10px; color:#0f5a46; background:rgba(0,168,121,0.12); border-radius:9px; padding:3px 8px;}
QPushButton#bubbleclose {border:0; background:transparent; font-size:17px; padding:2px; color:#5b6f68;}
QPushButton#bubbleclose:hover {color:#c92a2a;}
QPlainTextEdit#bubbletext {border:0; background:rgba(255,255,255,0.75); border-radius:14px; font-size:13px; padding:8px 10px; color:#1d3b31;}
QPushButton {border-radius:12px; padding:6px 8px; font-size:11px; font-weight:600; color:white; border:0;}
QPushButton#chip_continue {background:#0f7a5c;}
QPushButton#chip_tasks {background:#0b7285;}
QPushButton#chip_focus {background:#f2c14e; color:#3b2a00;}
QPushButton#chip_os {background:#3b5bdb;}
QPushButton:hover {padding-top:5px; padding-bottom:7px;}
QPushButton:disabled {background:#dfe7e3; color:#8a9a94;}
QLineEdit#bubbleinput {background:white; border:1px solid #cfe3d9; border-radius:14px; padding:8px 10px; font-size:13px; color:#1d3b31;}
QLineEdit#bubbleinput:focus {border-color:#00a879;}
QPushButton#bubblesend {background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #20c997,stop:1 #00a879); border-radius:14px; font-size:15px;}
QPushButton#footchip {background:white; color:#1d3b31; border:1px solid #d7e6de; font-weight:500; font-size:10px; padding:5px 9px;}
QPushButton#footchip:hover {background:#eefaf4; border-color:#00a879;}
'''

# Bubble quick buttons (all offline): key -> label key.
QUICK={'continue':'continue_learning','tasks':'tasks_short','focus':'focus_short','os':'os_short'}
ROLE_OF={activity:role for role,(activity,*_) in roles.ROLES.items() if activity in outfits.ROLES}

def greeting_key(hour):
    """Local time-of-day greeting used by the Virtual Assistant."""
    return 'greet_morning' if 4<=hour<11 else 'greet_afternoon' if 11<=hour<18 else 'greet_evening'

class Atlas:
    """Character poses for every outfit.

    base         original atlas + activity sheet (no clothes)
    traditional  Tais Mane drawings + generated Tais wrap for the other poses
    tuxedo/casual generated outfit sheets (tools/make-outfits.py)
    A sheet's json may give one canvas size or a size per pose.
    """
    SHEETS=[('lafa-atlas.png','atlas.json','base'),('lafa-activities.png','activities.json','base'),
            ('lafa-traditional.png','traditional.json','traditional'),('lafa-tais.png','tais.json','traditional'),
            ('lafa-tuxedo.png','tuxedo.json','tuxedo'),('lafa-casual.png','casual.json','casual')]
    def __init__(self):
        self.outfits={'base':{},'traditional':{},'tuxedo':{},'casual':{}}
        self.sheet=QPixmap(str(ASSET))
        for image,manifest,outfit in self.SHEETS:
            path=ASSET.with_name(image)
            if outfit!='base' and image!='lafa-traditional.png' and not path.is_file():continue
            sheet=QPixmap(str(path))
            if sheet.isNull():raise RuntimeError('LAFA character atlas is missing.')
            metadata=json.loads(path.with_name(manifest).read_text())
            for state in metadata['states']:
                canvas=metadata['canvas'];size=canvas[state] if isinstance(canvas,dict) else canvas
                crop=sheet.copy(*metadata['rects'][state]);pose=QPixmap(size,size);pose.fill(Qt.transparent)
                painter=QPainter(pose);painter.drawPixmap((size-crop.width())//2,(size-crop.height())//2,crop);painter.end()
                # Hand-drawn traditional art wins over the generated Tais wrap.
                if outfit=='traditional' and state in self.outfits['traditional'] and manifest=='tais.json':continue
                self.outfits[outfit][state]=pose
        self.poses=self.outfits['base'];self.traditional=self.outfits['traditional']
        for state in ['tebe','bidu']:self.poses[state]=self.traditional[state]
        if set(STATES)-self.poses.keys():raise RuntimeError('A LAFA pose is missing.')
    def head(self,pose):
        """(x, y) of the top of LAFA's head as fractions of the pose canvas."""
        cache=self.__dict__.setdefault('_heads',{})
        if pose not in cache:
            image=self.poses.get(pose,self.poses['idle']).toImage().scaled(96,96,Qt.KeepAspectRatio,Qt.SmoothTransformation)
            top=None;xs=[]
            for y in range(image.height()):
                row=[x for x in range(image.width()) if QColor(image.pixel(x,y)).alpha()>120] if image.hasAlphaChannel() else []
                if top is None and len(row)>=3:top=y
                if top is not None:
                    xs+=row
                    if y>top+8:break
            cache[pose]=(sum(xs)/len(xs)/image.width(),top/image.height()) if xs else (0.5,0.1)
        return cache[pose]
    def pixmap(self,state='idle',size=180,costume='casual'):
        pose=outfits.pose_of(state)
        poses=self.outfits.get(costume) or self.poses
        if pose not in poses:poses=self.traditional if pose in self.traditional else self.poses
        return poses.get(pose,self.poses.get(pose,self.poses['idle'])).scaled(size,size,Qt.KeepAspectRatio,Qt.SmoothTransformation)

class Character(QWidget):
    """LAFA drawn with human-like movement (see motion.py)."""
    clicked=Signal()
    FRAME_MS=40
    def __init__(self,atlas,parent=None,size=190):
        super().__init__(parent);self.atlas=atlas;self.state='idle';self.costume='casual';self.phase=0;self.animated=True;self.direction=1;self.rate=1.0
        self.motion=Motion();self.previous=None
        self.setFixedSize(size,size+16);self.setMouseTracking(True)
        self.timer=QTimer(self);self.timer.timeout.connect(self.tick);self.timer.start(self.FRAME_MS)
    @property
    def hop_phase(self):return 1.0 if self.motion.gesture=="jump" else 0.0
    def set_state(self,state):
        state=state if state in STATES or state in outfits.ACTIVITIES else 'idle'
        if state!=self.state and self.animated and self.timer.isActive():
            self.previous=(self.state,self.costume);self.motion.changed()
            if state in {'talking','greeting'} and self.state in {'idle','sitting'}:self.motion.play('wave')
        self.state=state;self.update()
    @property
    def pose(self):return outfits.pose_of(self.state)
    def animate(self,enabled):
        self.animated=enabled
        if enabled:self.timer.start(self.FRAME_MS)
        else:self.timer.stop()
        self.update()
    def tick(self):
        seconds=self.FRAME_MS/1000*self.rate;self.phase+=0.14*self.rate*self.FRAME_MS/90
        self.motion.advance(seconds)
        # Look towards the pointer when it is near (attention, like a person).
        try:
            pos=self.mapFromGlobal(QCursor.pos());near=-120<pos.x()<self.width()+120 and -160<pos.y()<self.height()+60
            self.motion.attend((pos.x()-self.width()/2)/(self.width()) if near else 0.0)
        except RuntimeError:pass
        self.update()
    def hop(self):
        """Happy jump with anticipation when LAFA answers; skipped while paused."""
        if self.animated and not getattr(self,'reduce_motion',False):self.motion.play('jump')
    def gesture(self,name):
        if self.animated and not getattr(self,'reduce_motion',False):self.motion.play(name)
    def paintEvent(self,event):
        painter=QPainter(self);painter.setRenderHint(QPainter.SmoothPixmapTransform);painter.setRenderHint(QPainter.Antialiasing)
        pose=self.pose;scene=outfits.scene_of(self.state)
        if scene:outfits.paint_background(painter,scene,self.width(),self.height(),self.phase)
        f=self.motion.frame(pose,self.animated and not getattr(self,'reduce_motion',False))
        pix=self.atlas.pixmap(self.state,self.width()-10,self.costume)
        ground=self.height()/2+pix.height()/2-4
        if not scene and pose not in {'sleeping'}:
            # Soft shadow under the feet keeps LAFA on the ground.
            painter.setPen(Qt.NoPen);painter.setBrush(QColor(0,0,0,int(38*f.shadow)))
            w=pix.width()*0.42*f.shadow;painter.drawEllipse(QPointF(self.width()/2+f.dx,ground),w/2,w/9)
        if not self.timer.isActive():self.motion.fade=1.0;self.previous=None   # paused: no half-faded pictures
        if self.previous and self.motion.fade<1.0:
            painter.setOpacity(1.0-self.motion.fade);old=self.atlas.pixmap(self.previous[0],self.width()-10,self.previous[1])
            painter.drawPixmap(int(self.width()/2-old.width()/2),int(self.height()/2-old.height()/2),old);painter.setOpacity(self.motion.fade)
        flip=pose=='walking' and self.direction<0
        painter.save();painter.translate(self.width()/2+f.dx,self.height()/2+pix.height()/2+f.dy)   # feet
        painter.rotate(f.tilt);painter.scale(-f.sx if flip else f.sx,f.sy)
        w,h=pix.width(),pix.height();hip=int(h*0.70)
        if f.split:
            painter.save();painter.translate(0,-(h-hip));painter.shear(f.step,0)
            # The two parts overlap by a few pixels so no seam shows at the hips.
            painter.drawPixmap(QRectF(-w/2,-6,w,h-hip+6),pix,QRectF(0,hip-6,w,h-hip+6));painter.restore()
            painter.translate(0,-(h-hip));painter.rotate(f.lean)
            painter.drawPixmap(QRectF(-w/2,-hip,w,hip+3),pix,QRectF(0,0,w,hip+3))
            top=-hip
        else:
            painter.drawPixmap(QRectF(-w/2,-h,w,h),pix,QRectF(0,0,w,h));top=-h
        hat=outfits.hat_of(self.state)
        if hat:
            hx,hy=self.atlas.head(pose);outfits.paint_hat(painter,hat,-w/2+hx*w,top+(hy+0.15)*h,w)
        painter.restore();painter.setOpacity(1.0)
        if self.motion.fade>=1.0:self.previous=None
        if scene:outfits.paint_foreground(painter,scene,self.width(),self.height(),self.phase)
    def mouseReleaseEvent(self,event):
        if event.button()==Qt.LeftButton:self.clicked.emit()

class Balloon(QWidget):
    """Small speech balloon above LAFA's head for hover questions and self-talk."""
    clicked=Signal()
    def __init__(self):
        super().__init__(None,Qt.ToolTip|Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint|Qt.WindowDoesNotAcceptFocus)
        self.setAttribute(Qt.WA_TranslucentBackground);self.setAttribute(Qt.WA_ShowWithoutActivating)
        layout=QVBoxLayout(self);layout.setContentsMargins(14,10,14,22);layout.setSpacing(3)
        self.text=QLabel();self.text.setWordWrap(True);self.text.setStyleSheet('color:#1d3b31;font-size:13px;background:transparent;')
        self.caption=QLabel();self.caption.setWordWrap(True);self.caption.setStyleSheet('color:#7b6a3a;font-size:10px;background:transparent;')
        layout.addWidget(self.text);layout.addWidget(self.caption);self.setFixedWidth(250);self.kind=''
    def present(self,text,caption,anchor,kind):
        """Show above anchor (global top-centre of the character)."""
        self.kind=kind;self.text.setText(text);self.caption.setText(caption);self.caption.setVisible(bool(caption))
        self.adjustSize();self.setFixedHeight(self.sizeHint().height())
        screen=(QGuiApplication.screenAt(anchor) or QGuiApplication.primaryScreen()).availableGeometry()
        x=max(screen.left()+4,min(anchor.x()-self.width()+70,screen.right()-self.width()-4));y=max(screen.top()+4,anchor.y()-self.height()+6)
        self.move(x,y);self.show();self.raise_()
    def paintEvent(self,event):
        p=QPainter(self);p.setRenderHint(QPainter.Antialiasing)
        body=QRectF(1,1,self.width()-2,self.height()-16);path=QPainterPath();path.addRoundedRect(body,14,14)
        tail=QPainterPath();x=self.width()-70;tail.moveTo(x-10,body.bottom()-1);tail.lineTo(x+10,body.bottom()-1);tail.lineTo(x+2,self.height()-2);tail.closeSubpath()
        path=path.united(tail);p.setPen(QPen(QColor(0,168,121,90),1.2));p.setBrush(QColor(250,253,251,248));p.drawPath(path)
    def mouseReleaseEvent(self,event):
        if event.button()==Qt.LeftButton:self.clicked.emit()

class Companion(QWidget):
    open_requested=Signal()
    quit_requested=Signal()
    user_request=Signal(str)
    action_requested=Signal(str)
    activity_changed=Signal(str)
    read_requested=Signal()
    settings_requested=Signal()
    source_requested=Signal(str)
    card_requested=Signal()
    outfit_requested=Signal(str)
    settings_changed=Signal()
    def __init__(self,atlas,settings,clock=time.monotonic):
        super().__init__();self.settings=settings;self.clock=clock
        self.online=False;self.paused=False;self._busy=False;self.drag=None;self.moved=False;self.direction=1;self.hovered=False;self.walk_target=None
        self.last_activity=clock();self.last_idle_change=clock();self.last_card=clock();self.introduced=False;self.current_source="";self.popup_deadline=0
        self.spontaneous=[];self.fullscreen_ahead=False
        self.setWindowFlags(Qt.Tool|Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle('LAFA Virtual Assistant')
        layout=QVBoxLayout(self);layout.setContentsMargins(8,8,8,8);layout.setSpacing(12)
        self.bubblebox=QFrame();self.bubblebox.setObjectName('speech')
        # Aero glass bubble: soft white glass, Eduka green accents, colourful chips.
        self.bubblebox.setStyleSheet(BUBBLE_QSS)
        self.bubblebox.setFixedHeight(344)
        col=QVBoxLayout(self.bubblebox);col.setContentsMargins(16,12,14,12);col.setSpacing(8)
        header=QHBoxLayout();name=QLabel('LAFA');name.setObjectName('bubblename');header.addWidget(name)
        self.duty_label=QLabel();self.duty_label.setObjectName('bubbleduty');header.addWidget(self.duty_label,1)
        self.status=QLabel();self.status.setObjectName('bubblestatus');header.addWidget(self.status)
        close=QPushButton('×');close.setObjectName('bubbleclose');close.setFixedWidth(28);close.clicked.connect(self.collapse);header.addWidget(close);col.addLayout(header)
        self.message=QPlainTextEdit();self.message.setObjectName('bubbletext');self.message.setReadOnly(True);self.message.setFixedHeight(128);col.addWidget(self.message)
        quick=QHBoxLayout();quick.setSpacing(6);self.quick_buttons=[]
        # Offline helpers: continue learning, tasks and reminders, focus, OS help.
        for key in QUICK:
            b=QPushButton();b.setObjectName('chip_'+key);b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(lambda checked=False,k=key:self.action_requested.emit(k));quick.addWidget(b);self.quick_buttons.append((key,b))
        col.addLayout(quick)
        row=QHBoxLayout();row.setSpacing(6);self.input=QLineEdit();self.input.setObjectName('bubbleinput');self.input.returnPressed.connect(self.submit)
        self.send_button=QPushButton('➤');self.send_button.setObjectName('bubblesend');self.send_button.setFixedSize(40,38);self.send_button.clicked.connect(self.submit)
        row.addWidget(self.input,1);row.addWidget(self.send_button);col.addLayout(row)
        footer=QHBoxLayout();footer.setSpacing(6)
        self.full_button=QPushButton();self.full_button.setObjectName('footchip');self.full_button.clicked.connect(self.open_requested.emit);footer.addWidget(self.full_button)
        self.voice_button=QPushButton();self.voice_button.setObjectName('footchip');self.voice_button.clicked.connect(self.read_requested.emit);footer.addWidget(self.voice_button)
        self.quiet_button=QPushButton();self.quiet_button.setObjectName('footchip');self.quiet_button.setCheckable(True);self.quiet_button.toggled.connect(self.set_quiet);footer.addWidget(self.quiet_button)
        self.joke_button=QPushButton('😄');self.joke_button.setObjectName('footchip');self.joke_button.clicked.connect(self.tell_joke);footer.addWidget(self.joke_button)
        self.source_button=QPushButton();self.source_button.setObjectName('footchip');self.source_button.clicked.connect(lambda:self.source_requested.emit(self.current_source));self.source_button.hide();footer.addWidget(self.source_button);footer.addStretch();col.addLayout(footer)
        layout.addWidget(self.bubblebox)
        self.pet=Character(atlas,self,size=PET_SIZES.get(settings.character_size,176));self.pet.costume=settings.costume;self.pet.clicked.connect(self.toggle_bubble);layout.addWidget(self.pet,0,Qt.AlignRight)
        self.balloon=Balloon();self.balloon.clicked.connect(self.accept_balloon)
        self.balloon_timer=QTimer(self);self.balloon_timer.setSingleShot(True);self.balloon_timer.timeout.connect(self.hide_balloon)
        self.idle_timer=QTimer(self);self.idle_timer.setInterval(1000);self.idle_timer.timeout.connect(self.choose_idle)
        self.walk_timer=QTimer(self);self.walk_timer.setInterval(120);self.walk_timer.timeout.connect(self.walk)
        self.fullscreen_timer=QTimer(self);self.fullscreen_timer.setInterval(10_000);self.fullscreen_timer.timeout.connect(self.check_fullscreen)
        self.bubblebox.hide();self.setFixedSize(*self.compact_size());self.animate(False);self.apply_preferences()
        self.retranslate();self.message.setPlainText(tr(settings.locale,'welcome_desktop'))
        rect=QGuiApplication.primaryScreen().availableGeometry();self.move(rect.right()-self.width()-20,rect.bottom()-self.height()-30)
        QApplication.instance().installEventFilter(self)
        self.pet.installEventFilter(self)
    def compact_size(self):
        size=self.pet.width();return (size+16,self.pet.height()+16)
    def expanded_size(self):
        return (max(EXPANDED[0],self.pet.width()+16),324+12+self.pet.height()+16)
    def apply_preferences(self):
        """Lafa-Configuration: size, animation speed and outfit, applied live."""
        size=PET_SIZES.get(self.settings.character_size,176)
        if self.pet.width()!=size:self.pet.setFixedSize(size,size+16)
        self.pet.rate=ANIMATION_RATES.get(self.settings.animation_speed,1.0);self.pet.reduce_motion=self.settings.reduce_motion
        if self.pet.costume!=self.settings.costume:
            self.pet.costume=self.settings.costume
            # A new outfit starts with one of its own activities.
            if self.state not in outfits.activities_for(self.settings.costume)+['walking','talking','idle']:self.set_state(outfits.activities_for(self.settings.costume)[0])
        self.setFixedSize(*(self.expanded_size() if self.bubblebox.isVisible() else self.compact_size()))
        if self.isVisible() and not self.bubblebox.isVisible():self.snap_to_panel()
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
    @property
    def lang(self):return self.settings.locale
    def animate(self,enabled):self.pet.animate(enabled)
    def set_state(self,state):
        self.pet.set_state(state);self.duty_label.setText('· '+personality.duty(self.lang,self.pet.state));self.activity_changed.emit(self.pet.state)
    def retranslate(self):
        lang=self.lang
        self.setToolTip('')
        self.input.setPlaceholderText(tr(lang,'search_box'));self.input.setAccessibleName(tr(lang,'search_box'));self.full_button.setText(tr(lang,'desktop'));self.voice_button.setText('🔊 '+tr(lang,'speak'));self.joke_button.setToolTip(tr(lang,'tell_joke'))
        self.quiet_button.blockSignals(True);self.quiet_button.setChecked(self.settings.quiet_mode);self.quiet_button.blockSignals(False);self.quiet_button.setText('🤫 '+tr(lang,'quiet_short'));self.quiet_button.setToolTip(tr(lang,'quiet_mode'))
        self.joke_button.setVisible(self.settings.entertainment)
        for key,b in self.quick_buttons:b.setText(tr(lang,QUICK[key]))
        self.status.setText(tr(lang,'online') if self.online else tr(lang,'local_ready'));self.source_button.setText(tr(lang,'source'))
        self.duty_label.setText('· '+personality.duty(lang,self.pet.state))
    def mark_activity(self):self.popup_deadline=0;self.last_activity=self.clock();self.last_idle_change=self.last_activity
    # ----- input -------------------------------------------------------------
    def eventFilter(self,obj,event):
        # Observe only this application's input events, never other desktop apps.
        if not hasattr(self,'pet'):return False  # being destroyed
        if event.type() in {QEvent.MouseButtonPress,QEvent.KeyPress,QEvent.TouchBegin}:
            self.mark_activity()
        if obj is self.pet:
            if event.type()==QEvent.Enter:self.on_hover(True)
            elif event.type()==QEvent.Leave:self.on_hover(False)
            if event.type()==QEvent.MouseButtonPress and event.button()==Qt.LeftButton:
                self.drag=global_point(event)-self.pos();self.moved=False;return True
            if event.type()==QEvent.MouseMove and self.drag is not None and event.buttons()&Qt.LeftButton:
                self.moved=True;self.hide_balloon()
                if QGuiApplication.platformName().startswith('wayland'):
                    if self.windowHandle():self.windowHandle().startSystemMove()
                else:self.move(global_point(event)-self.drag)
                return True
            if event.type()==QEvent.MouseButtonRelease and event.button()==Qt.LeftButton:
                if not self.moved:self.toggle_bubble()
                self.drag=None;return True
        return super().eventFilter(obj,event)
    def on_hover(self,inside):
        """Cursor touches LAFA: stop walking and ask, in character, how to help."""
        self.hovered=inside
        if inside:
            self.walk_target=None
            if not self.paused and not self.bubblebox.isVisible() and self.drag is None and self.settings.hover_questions and not self.settings.quiet_mode:
                self.show_balloon(personality.hover_line(self.lang,self.state),personality.duty(self.lang,self.state),'hover',0)
                self.pet.gesture('wave')
        elif self.balloon.isVisible() and self.balloon.kind=='hover':
            self.balloon_timer.start(1600)
    # ----- balloon -----------------------------------------------------------
    def show_balloon(self,text,caption='',kind='thought',seconds=6):
        if not self.settings.companion or not self.isVisible():return
        top=self.pet.mapToGlobal(self.pet.rect().topLeft());anchor=top+self.pet.rect().topRight()-self.pet.rect().topLeft()
        self.balloon.present(text,caption,anchor,kind)
        if seconds:self.balloon_timer.start(int(seconds*1000))
        else:self.balloon_timer.stop()
    def hide_balloon(self):self.balloon_timer.stop();self.balloon.hide()
    def accept_balloon(self):
        """Clicking the question opens the chat with that question as LAFA's line."""
        text=self.balloon.text.text();self.hide_balloon();self.show_bubble(text);self.input.setFocus()
    def tell_joke(self):
        text=personality.joke(self.lang);self.set_state('talking')
        if self.bubblebox.isVisible():self.show_answer(text);self.pet.hop()
        else:self.show_balloon(text,'',"joke",9);self.pet.hop()
    # ----- state -------------------------------------------------------------
    def can_roam(self):
        return QGuiApplication.platformName()=='xcb' and self.settings.roam and self.settings.companion and not self.settings.reduce_motion
    def eduka_panel(self):
        return eduka.panel() if self.settings.follow_eduka_panel else None
    def panel_rect(self):
        """Where LAFA may walk: along the Eduka-Panel (its real width), or the screen."""
        screen=QGuiApplication.screenAt(self.geometry().center()) or QGuiApplication.primaryScreen()
        info=self.eduka_panel();geometry=screen.geometry()
        if info and info['edge'] in {'bottom','top'}:
            x0,x1=eduka.panel_span(geometry.left(),geometry.width(),info)
            return QRect(x0,geometry.top(),max(self.width(),x1-x0),geometry.height())
        return geometry if self.settings.panel_roam else screen.availableGeometry()
    def panel_y(self,rect=None):
        """Top edge for LAFA's feet to stand on the Eduka-Panel."""
        rect=rect or self.panel_rect();info=self.eduka_panel()
        if info:
            if info['edge']=='bottom':return rect.bottom()+1-info['gap']-info['height']-self.height()
            if info['edge']=='top':return rect.top()+info['gap']+info['height']
            available=(QGuiApplication.screenAt(self.geometry().center()) or QGuiApplication.primaryScreen()).availableGeometry()
            return available.bottom()+1-self.height()
        if self.settings.panel_edge=='bottom':return rect.bottom()-self.settings.panel_height-self.height()+1
        return rect.top()+self.settings.panel_height
    def snap_to_panel(self):
        """Stand on the Eduka-Panel edge (X11). Wayland keeps compositor placement."""
        if QGuiApplication.platformName()!='xcb' or not self.settings.panel_roam or self.bubblebox.isVisible():return
        rect=self.panel_rect();self.move(max(rect.left(),min(self.x(),rect.right()-self.width()+1)),self.panel_y(rect))
    def set_online(self,online):
        changed=self.online!=bool(online);self.online=bool(online);self.pet.costume=self.settings.costume
        self.retranslate();self.update_controls()
        # LAFA stays on the desktop offline too, with its offline features.
        if self.settings.companion:
            was_visible=self.isVisible();self.show();self.animate(not self.paused)
            if not was_visible:self.snap_to_panel()
            if not self.paused:
                if not self.idle_timer.isActive():self.idle_timer.start()
                if not self.walk_timer.isActive():self.walk_timer.start()
                if QGuiApplication.platformName()=='xcb' and not self.fullscreen_timer.isActive():self.fullscreen_timer.start()
                if changed:self.mark_activity()
                if not self.introduced:
                    self.introduced=True;self.set_state('idle');self.show_bubble(self.introduction());self.popup_deadline=self.clock()+18
            else:self.idle_timer.stop();self.walk_timer.stop();self.hide_balloon()
        else:
            self.hide();self.hide_balloon();self.animate(False);self.idle_timer.stop();self.walk_timer.stop();self.fullscreen_timer.stop()
            if not self.settings.companion:self.introduced=False
    def introduction(self,hour=None):
        lang=self.lang;text=tr(lang,'welcome_virtual')
        if getattr(self.settings,'greet_by_time',True):text=tr(lang,greeting_key(datetime.now().hour if hour is None else hour))+' '+text
        return text
    def update_controls(self):
        if not hasattr(self,'send_button'):return
        # Everything in the bubble works offline.
        free=not self._busy
        self.send_button.setEnabled(free);self.input.setEnabled(free)
        for key,b in self.quick_buttons:b.setEnabled(free)
    def activity_choices(self):
        excluded={self.state}|({'walking'} if self.can_roam() else set())|(set() if self.settings.personal_activities else {'bathing','toilet'})
        if not self.settings.entertainment:excluded|=ENTERTAINMENT
        if self.settings.reduce_motion:excluded|={'tebe','bidu','walking','stretching'}
        return [s for s in outfits.activities_for(self.settings.costume) if s not in excluded]
    def play_role(self,role):
        """Switch into one of LAFA's roles and say something in that role."""
        activity=roles.ROLES[role][0];self.walk_target=None;self.set_state(activity);self.last_idle_change=self.clock()
        self.show_bubble(roles.line(role,self.lang));self.popup_deadline=self.clock()+20
    def start_activity(self):
        """Pick a new job for the assistant; sometimes LAFA comments on it."""
        self.walk_target=None;self.set_state(random.choice(self.activity_choices()));self.last_idle_change=self.clock()
        if self.settings.chatter and self.can_auto_popup() and random.random()<0.35:
            self.spoke()
            role=ROLE_OF.get(self.state)
            line=roles.line(role,self.lang) if role and random.random()<0.5 else personality.thought(self.lang,self.state)
            self.show_balloon(line,personality.duty(self.lang,self.state),'thought',self.settings.balloon_seconds)
    def start_walk(self):
        self.snap_to_panel();rect=self.panel_rect();left,right=rect.left(),rect.right()-self.width()
        if right-left<60:self.start_activity();return
        target=random.randint(left,right)
        if abs(target-self.x())<120:target=left if self.x()-left>right-self.x() else right
        self.walk_target=target;self.direction=1 if target>self.x() else -1;self.pet.direction=self.direction
        self.set_state('walking');self.last_idle_change=self.clock()
    def choose_idle(self):
        now=self.clock()
        if self.paused or self.busy or self.drag:return
        if self.popup_deadline and now>=self.popup_deadline:
            self.popup_deadline=0
            if not self.input.text().strip():self.collapse()
        if self.bubblebox.isVisible() or self.input.text().strip() or self.hovered:return
        if (self.settings.cultural_cards or self.settings.positive_messages or self.settings.fun_messages) and self.can_auto_popup() and now-self.last_card>=self.settings.card_minutes*60:
            self.last_card=now;self.card_requested.emit();return
        if self.walk_target is not None:return
        if now-max(self.last_activity,self.last_idle_change)<self.settings.idle_seconds:return
        if self.can_roam() and self.state!='walking':self.start_walk()
        else:self.start_activity()
    def walk(self):
        if self.paused or not self.settings.companion or self.state!='walking' or self.busy or not self.settings.roam or self.drag or self.hovered or self.bubblebox.isVisible():return
        if QGuiApplication.platformName()!='xcb':return
        rect=self.panel_rect();step=WALK_STEPS.get(self.settings.walk_speed,3)
        if self.walk_target is None:
            nx=self.x()+self.direction*step
            if nx<rect.left() or nx+self.width()>rect.right()+1:self.direction*=-1;nx=self.x()+self.direction*step
        else:
            self.direction=1 if self.walk_target>self.x() else -1;nx=self.x()+self.direction*min(step,abs(self.walk_target-self.x()))
        self.pet.direction=self.direction
        y=self.panel_y(rect) if self.settings.panel_roam else self.y()
        self.move(max(rect.left(),min(nx,rect.right()-self.width()+1)),y)
        if self.balloon.isVisible():self.hide_balloon()
        if self.walk_target is not None and abs(self.x()-self.walk_target)<=1:self.start_activity()
    # ----- chat bubble -------------------------------------------------------
    def resize_overlay(self,expanded):
        anchor=self.geometry().bottomRight()
        self.bubblebox.setVisible(expanded);self.setFixedSize(*(self.expanded_size() if expanded else self.compact_size()))
        if expanded:self.hide_balloon()
        if QGuiApplication.platformName()=='xcb':
            rect=(QGuiApplication.screenAt(anchor) or QGuiApplication.primaryScreen()).availableGeometry()
            self.move(max(rect.left(),min(anchor.x()-self.width(),rect.right()-self.width())),max(rect.top(),min(anchor.y()-self.height(),rect.bottom()-self.height())))
            if not expanded:self.snap_to_panel()
        self.update()
    def show_bubble(self,text=None):
        if not self.settings.companion:return
        if text is not None:self.message.setPlainText(text);self.current_source="";self.source_button.hide()
        self.walk_target=None
        if self.state=='walking':self.set_state('talking')
        self.resize_overlay(True);self.mark_activity();self.show();self.raise_()
    def can_auto_popup(self):
        """Spontaneous messages: never in quiet mode, while paused, while a fullscreen
        app is in front, while the learner types, or above the hourly limit."""
        if self.settings.quiet_mode or self.fullscreen_ahead:return False
        recent=[t for t in self.spontaneous if self.clock()-t<3600];self.spontaneous=recent
        if len(recent)>=self.settings.messages_per_hour:return False
        return self.settings.companion and not self.paused and not self.busy and self.drag is None and not self.hovered and not self.bubblebox.isVisible() and not self.input.text().strip() and self.clock()-self.last_activity>=60
    def spoke(self):
        """Count a spontaneous message for the hourly limit."""
        self.spontaneous.append(self.clock())
    def set_quiet(self,quiet):
        """Quiet mode: no spontaneous messages, hover questions or self-talk."""
        self.settings.quiet_mode=bool(quiet);self.hide_balloon();self.settings_changed.emit()
    def check_fullscreen(self):
        """X11: pause while another application is fullscreen (e.g. a video or a test)."""
        ahead=eduka.fullscreen_active() if self.settings.companion and QGuiApplication.platformName()=='xcb' else False
        if ahead!=self.fullscreen_ahead:
            self.fullscreen_ahead=ahead
            if ahead:self.hide_balloon();self.hide()
            elif self.settings.companion:self.show();self.snap_to_panel()
    def show_card(self,card,automatic=False):
        if not self.settings.companion or self.busy or (automatic and not self.can_auto_popup()):return
        if automatic:self.spoke()
        self.set_state(card.mood);self.show_bubble(card.text);self.current_source=card.source
        self.source_button.setVisible(bool(card.source));self.popup_deadline=self.clock()+15
    def toggle_bubble(self):
        if self.bubblebox.isVisible():self.collapse()
        elif getattr(self.settings,'click_recommendations',True):self.recommend()
        else:self.show_bubble(self.introduction())
    def recommend(self):
        """Click on LAFA: a free-software (GPL) tip and, online, a learning website."""
        from . import recommendations
        text,url=recommendations.pick(self.lang,self.online)
        self.show_bubble(tr(self.lang,'recommend_title')+'\n\n'+text)
        self.current_source=url;self.source_button.setVisible(bool(url))
    def collapse(self):self.resize_overlay(False);self.mark_activity()
    def show_answer(self,text):
        self.current_source="";self.source_button.hide();self.popup_deadline=0
        self.pet.gesture('nod')
        self.message.setPlainText(text)
        if self.bubblebox.isVisible():self.message.verticalScrollBar().setValue(0)
    def submit(self):
        text=self.input.text().strip()
        if text and not self.busy:
            self.input.clear();self.mark_activity();self.user_request.emit(text)
    def paintEvent(self,event):
        if not self.bubblebox.isVisible():return
        p=QPainter(self);p.setRenderHint(QPainter.Antialiasing);p.setPen(Qt.NoPen);p.setBrush(QColor(250,253,251,246))
        y=self.bubblebox.geometry().bottom()-1;x=self.width()-76
        p.drawPolygon(QPolygonF([QPointF(x-12,y),QPointF(x+12,y),QPointF(x,y+14)]))
    def contextMenuEvent(self,event):
        self.mark_activity();self.hide_balloon();menu=QMenu(self);lang=self.lang
        menu.addAction(tr(lang,'virtual'),self.show_bubble);menu.addAction(tr(lang,'fullwindow'),self.open_requested.emit)
        if self.settings.entertainment:menu.addAction(tr(lang,'tell_joke'),self.tell_joke)
        for key in QUICK:menu.addAction(tr(lang,QUICK[key]),lambda checked=False,k=key:self.action_requested.emit(k))
        quiet=menu.addAction(tr(lang,'quiet_mode'));quiet.setCheckable(True);quiet.setChecked(self.settings.quiet_mode);quiet.triggered.connect(self.set_quiet)
        if self.settings.entertainment:
            # Entertainment (magician, comedian…) is optional, never part of the main flow.
            hats=menu.addMenu(tr(lang,'roles'))
            for role in roles.ORDER:hats.addAction(roles.text(roles.ROLES[role][2],lang),lambda checked=False,r=role:self.play_role(r))
        moods=menu.addMenu(tr(lang,'mood'))
        for state in outfits.activities_for(self.settings.costume):moods.addAction(tr(lang,state)+' · '+personality.duty(lang,state),lambda checked=False,s=state:self.set_state(s))
        wardrobe=menu.addMenu(tr(lang,'costume'))
        for outfit in outfits.OUTFITS:
            action=wardrobe.addAction(tr(lang,outfit));action.setCheckable(True);action.setChecked(self.settings.costume==outfit)
            action.triggered.connect(lambda checked=False,o=outfit:self.outfit_requested.emit(o))
        pause=menu.addAction(tr(lang,'pause'));pause.setCheckable(True);pause.setChecked(self.paused);pause.triggered.connect(self.toggle_pause)
        menu.addSeparator();menu.addAction(tr(lang,'open_settings'),self.settings_requested.emit);menu.addAction(tr(lang,'quit'),self.quit_requested.emit);menu.exec_(event.globalPos()) if hasattr(menu,"exec_") else menu.exec(event.globalPos())
    def toggle_pause(self,paused):self.paused=paused;self.set_online(self.online)
    def hideEvent(self,event):self.hide_balloon();super().hideEvent(event)
    def closeEvent(self,event):
        app=QApplication.instance()
        if app:app.removeEventFilter(self)
        self.hide_balloon();self.balloon.close();super().closeEvent(event)
