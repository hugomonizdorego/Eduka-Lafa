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
from .qt import Qt,QTimer,QPointF,QRectF,QRect,QEvent,Signal,QPixmap,QPainter,QGuiApplication,QPolygonF,QColor,QPainterPath,QPen,QCursor,QRegion
from .qt import QWidget,QMenu,QFrame,QVBoxLayout,QHBoxLayout,QGridLayout,QLabel,QLineEdit,QPushButton,QPlainTextEdit,QApplication,QSize,global_point,run
from .config import STATES,IDLE_ACTIVITIES,ENTERTAINMENT
from .i18n import tr
from . import personality, eduka, outfits, roles, icons
import shutil
from .motion import Motion

ASSET=Path(__file__).parent/'assets'/'lafa-atlas.png'
COMPACT=(192,208)
EXPANDED=(440,544)
PET_SIZES={'small':132,'normal':176,'large':220}
WALK_STEPS={'slow':2,'normal':3,'fast':5}
ANIMATION_RATES={'slow':0.6,'normal':1.0,'fast':1.6}

BUBBLE_QSS='''
QFrame#speech {background:#ffffff; border:2px solid #dbe8e1; border-radius:22px;}
QFrame#speech QLabel {background:transparent; color:#17322b;}
QLabel#bubblename {font-size:20px; font-weight:800; color:#0b4f3c;}
QLabel#bubbleduty {font-size:11px; color:#5b6f68;}
QLabel#bubblestatus {font-size:11px; font-weight:700; color:#0a6047; background:#e3f4ec; border-radius:11px; padding:4px 10px;}
QPushButton#bubbleclose {border:2px solid transparent; background:transparent; padding:2px; border-radius:10px;}
QPushButton#bubbleclose:hover {background:#f1f5f2;}
QPushButton#bubbleclose:focus {border-color:#0a7350;}
QLineEdit#bubbleinput {background:#ffffff; border:2px solid #dbe8e1; border-radius:14px; padding:8px 10px; font-size:13px; color:#17322b;}
QLineEdit#bubbleinput:focus {border-color:#0a7350;}
QPushButton#quicktile {background:#eef7f2; color:#17322b; border:2px solid #eef7f2; border-radius:16px; font-size:13px; font-weight:700; padding:10px 6px;}
QPushButton#quicktile:hover {border-color:#00a879;}
QPushButton#quicktile:focus {border-color:#0a7350;}
QPushButton#quicktile[tone="sand"] {background:#fdf3dc; border-color:#fdf3dc;}
QPushButton#quicktile[tone="sky"] {background:#e8f1fb; border-color:#e8f1fb;}
QPushButton#quicktile[tone="sand"]:hover, QPushButton#quicktile[tone="sky"]:hover {border-color:#00a879;}
QPushButton#quicktile[tone="sand"]:focus, QPushButton#quicktile[tone="sky"]:focus {border-color:#0a7350;}
QFrame#resultcard {background:#f6faf7; border:2px solid #e7efea; border-radius:14px;}
QPlainTextEdit#bubbletext {border:0; background:transparent; font-size:13px; color:#17322b;}
QPushButton#footchip {background:transparent; color:#17322b; border:2px solid transparent; font-weight:600; font-size:12px; padding:6px 8px; border-radius:10px;}
QPushButton#footchip:hover {background:#eef7f2;}
QPushButton#footchip:focus {border-color:#0a7350;}
QPushButton#footchip:checked {background:#e3f4ec; color:#0a6047;}
QPushButton#footchip:disabled {color:#8a9a94;}
'''


# Popup quick access (2×2, all offline): key -> (label key, icon, tone).
TILES=[('continue','popup_continue','book-open',''),('explore','popup_explore','compass',''),('tasks','popup_tasks','tasks','sand'),('os','popup_os','monitor-help','sky')]
# Right-click menu shortcuts (also offline).
QUICK={'continue':'continue_learning','explore':'popup_explore','tasks':'tasks_short','focus':'focus_short','os':'os_short'}
POPUP_WIDTH=360
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
        # Walk cycle: 8 frames per outfit (tools/make-walk.py), facing right.
        self.walk={};self.walk_meta={}
        path=ASSET.with_name('lafa-walk.png')
        try:
            meta=json.loads(path.with_name('lafa-walk.json').read_text());sheet=QPixmap(str(path))
            if not sheet.isNull():
                fw,fh=meta['frame']
                for r,row in enumerate(meta['rows']):self.walk['traditional' if row=='tais' else row]=[sheet.copy(c*fw,r*fh,fw,fh) for c in range(meta['frames'])]
                self.walk_meta=meta
        except (OSError,ValueError,KeyError):self.walk={}
    def extent(self,pix):
        """(top, bottom, left, right) of the opaque part of a pixmap, cached."""
        cache=self.__dict__.setdefault('_extent',{});key=(pix.cacheKey(),pix.width(),pix.height())
        if key not in cache:
            image=pix.toImage();w,h=image.width(),image.height();rows=[]
            step=max(1,w//64)
            for y in range(h):
                if any(QColor(image.pixel(x,y)).alpha()>100 for x in range(0,w,step)):rows.append(y)
            cols=[x for x in range(0,w,step) if any(QColor(image.pixel(x,y)).alpha()>100 for y in range(0,h,max(1,h//64)))]
            cache[key]=(rows[0],rows[-1],cols[0],cols[-1]) if rows and cols else (0,h-1,0,w-1)
        return cache[key]
    def walk_frames(self,costume):
        return self.walk.get(costume) or self.walk.get('casual') or []
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
        self.distance=0.0;self.moved_at=0.0;self.hold=0   # walk cycle: travelled pixels, last move, contact-pose ticks
        self.setFixedSize(size,size+16);self.setMouseTracking(True)
        self.timer=QTimer(self);self.timer.timeout.connect(self.tick);self.timer.start(self.FRAME_MS)
    @property
    def hop_phase(self):return 1.0 if self.motion.gesture=="jump" else 0.0
    @property
    def direction(self):return self.__dict__.get('_direction',1)
    @direction.setter
    def direction(self,value):
        value=1 if value>=0 else -1
        # Turning: plant both feet (contact pose) for a moment, then walk the other way.
        if value!=self.__dict__.get('_direction',1) and self.state=='walking':self.hold=3
        self._direction=value
    def advance(self,pixels):
        """The window moved this many pixels: the feet follow the distance (no sliding)."""
        self.distance+=abs(pixels);self.moved_at=time.monotonic()
        if self.hold>0:self.hold-=1
        self.update()
    def walk_index(self):
        frames=self.atlas.walk_frames(self.costume)
        if not frames or self.hold>0 or not self.animated or getattr(self,'reduce_motion',False):return 0
        stride=self.atlas.walk_meta.get('stride',120)*self.walk_scale()
        return int(self.distance/(stride/len(frames))+1e-6)%len(frames)
    def walk_scale(self):
        """Walk frames are drawn at the same body height as the standing pose."""
        idle=self.atlas.pixmap('idle',self.width()-10,self.costume);t,b,_l,_r=self.atlas.extent(idle)
        frames=self.atlas.walk_frames(self.costume)
        if not frames:return 1.0
        ft,fb,_fl,_fr=self.atlas.extent(frames[0])
        return (b-t)/max(1,fb-ft)
    def ground_y(self):
        idle=self.atlas.pixmap('idle',self.width()-10,self.costume);_t,b,_l,_r=self.atlas.extent(idle)
        return self.height()/2-idle.height()/2+b
    def mask_region(self):
        """Where LAFA is drawn (with room for jumps and the shadow); clicks elsewhere go to other windows."""
        key=(self.state,self.costume,self.direction,self.width(),self.height())
        if getattr(self,'_mask_key',None)!=key:
            if self.pose=='walking' and self.atlas.walk_frames(self.costume):
                sc=self.walk_scale();fw,fh=self.atlas.walk_meta['frame'];ax=self.atlas.walk_meta['anchor_x'];base=self.atlas.walk_meta['baseline']
                ft,fb,fl,fr=self.atlas.extent(self.atlas.walk_frames(self.costume)[0])
                x0=self.width()/2+(fl-ax)*sc if self.direction>0 else self.width()/2-(fr-ax)*sc
                region=QRegion(QRect(int(x0)-14,int(self.ground_y()-(base-ft)*sc)-6,int((fr-fl)*sc)+28,int((base-ft)*sc)+14))
            else:
                pix=self.atlas.pixmap(self.state,self.width()-10,self.costume)
                bits=QRegion(pix.mask()) if not pix.mask().isNull() else QRegion(0,0,pix.width(),pix.height())
                bits.translate(int(self.width()/2-pix.width()/2),int(self.height()/2-pix.height()/2))
                region=QRegion(bits)
                for dx,dy in ((-8,0),(8,0),(0,-26),(0,6)):region=region.united(bits.translated(dx,dy))   # sway, jump, shadow
            self._mask_key=key;self._mask=region
        return self._mask
    def set_state(self,state):
        state=state if state in STATES or state in outfits.ACTIVITIES else 'idle'
        if state=='walking' and self.state!='walking':self.distance=0.0;self.hold=2   # start from the contact pose
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
        # A walking LAFA that is not being moved (Desktop preview, Wayland) walks on the spot at a calm pace.
        if self.state=='walking' and time.monotonic()-self.moved_at>0.4 and not getattr(self,'reduce_motion',False):
            self.distance+=40*seconds
            if self.hold>0:self.hold-=1
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
        frames=self.atlas.walk_frames(self.costume) if pose=='walking' and not scene else []
        if frames:
            # Drawn walk cycle: same body height, foot line and anchor in every frame.
            if self.previous and self.motion.fade<1.0:
                painter.setOpacity(1.0-self.motion.fade);old=self.atlas.pixmap(self.previous[0],self.width()-10,self.previous[1])
                painter.drawPixmap(int(self.width()/2-old.width()/2),int(self.height()/2-old.height()/2),old);painter.setOpacity(self.motion.fade)
            frame=frames[self.walk_index()];sc=self.walk_scale();meta=self.atlas.walk_meta
            painter.save();painter.translate(self.width()/2,self.ground_y())
            painter.scale(sc*self.direction,sc)
            painter.drawPixmap(QPointF(-meta['anchor_x'],-meta['baseline']),frame)
            painter.restore();painter.setOpacity(1.0)
            if self.motion.fade>=1.0:self.previous=None
            return
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
        col=QVBoxLayout(self.bubblebox);col.setContentsMargins(16,14,14,14);col.setSpacing(10)
        # Header: LAFA, local status and close.
        header=QHBoxLayout();header.setSpacing(8)
        logo=QLabel();logo.setPixmap(atlas.pixmap('idle',36,settings.costume));logo.setFixedSize(38,38);header.addWidget(logo)
        names=QVBoxLayout();names.setSpacing(0);name=QLabel('LAFA');name.setObjectName('bubblename');names.addWidget(name)
        self.duty_label=QLabel();self.duty_label.setObjectName('bubbleduty');names.addWidget(self.duty_label);header.addLayout(names,1)
        self.status=QLabel();self.status.setObjectName('bubblestatus');header.addWidget(self.status,0,Qt.AlignTop)
        close=QPushButton();close.setObjectName('bubbleclose');close.setFixedSize(30,30);close.setIcon(icons.icon('close','#17322b'));close.clicked.connect(self.collapse);self.close_button=close
        header.addWidget(close,0,Qt.AlignTop);col.addLayout(header)
        # Search ("Cari materi atau file…"); the draft stays when the popup closes.
        self.input=QLineEdit();self.input.setObjectName('bubbleinput');self.input.returnPressed.connect(self.submit);self.input.setClearButtonEnabled(True)
        self.input.addAction(icons.icon('search','#5b6f68'),QLineEdit.LeadingPosition);col.addWidget(self.input)
        self.send_button=QPushButton();self.send_button.hide()   # kept for older callers; Enter searches
        # 2×2 quick access.
        grid=QGridLayout();grid.setSpacing(8);self.quick_buttons=[]
        for i,(key,label_key,icon_name,tone) in enumerate(TILES):
            b=QPushButton();b.setObjectName('quicktile');b.setCursor(Qt.PointingHandCursor);b.setProperty('tone',tone)
            b.setIcon(icons.icon(icon_name,'#0a6047'));b.setIconSize(QSize(26,26));b.setMinimumHeight(64)
            b.clicked.connect(lambda checked=False,k=key:self.action_requested.emit(k));grid.addWidget(b,i//2,i%2);self.quick_buttons.append((key,b))
        col.addLayout(grid)
        # One recommendation or a short result.
        card=QFrame();card.setObjectName('resultcard');cv=QHBoxLayout(card);cv.setContentsMargins(10,8,10,8);cv.setSpacing(8)
        mark=QLabel();mark.setPixmap(icons.pixmap('book-open','#0a6047',22));cv.addWidget(mark,0,Qt.AlignTop)
        self.message=QPlainTextEdit();self.message.setObjectName('bubbletext');self.message.setReadOnly(True);self.message.setFrameShape(QFrame.NoFrame)
        self.message.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded);self.message.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff);self.message.textChanged.connect(self.fit_message)
        cv.addWidget(self.message,1);col.addWidget(card)
        # Footer: open Desktop, read aloud (only with a local voice), quiet mode.
        footer=QHBoxLayout();footer.setSpacing(4)
        self.full_button=QPushButton();self.full_button.setObjectName('footchip');self.full_button.setIcon(icons.icon('monitor','#17322b'));self.full_button.clicked.connect(self.open_requested.emit);footer.addWidget(self.full_button)
        self.voice_button=QPushButton();self.voice_button.setObjectName('footchip');self.voice_button.setIcon(icons.icon('speaker','#17322b'));self.voice_button.clicked.connect(self.read_requested.emit);footer.addWidget(self.voice_button)
        self.voice_button.setVisible(bool(shutil.which('espeak-ng') or shutil.which('espeak')))
        footer.addStretch()
        self.quiet_button=QPushButton();self.quiet_button.setObjectName('footchip');self.quiet_button.setIcon(icons.icon('moon','#17322b'));self.quiet_button.setCheckable(True);self.quiet_button.toggled.connect(self.set_quiet);footer.addWidget(self.quiet_button)
        self.joke_button=QPushButton('😄');self.joke_button.setObjectName('footchip');self.joke_button.clicked.connect(self.tell_joke);footer.addWidget(self.joke_button)
        self.source_button=QPushButton();self.source_button.setObjectName('footchip');self.source_button.clicked.connect(lambda:self.source_requested.emit(self.current_source));self.source_button.hide();footer.addWidget(self.source_button)
        col.addLayout(footer)
        self.bubblebox.setFixedWidth(POPUP_WIDTH)
        layout.addWidget(self.bubblebox)
        self.pet=Character(atlas,self,size=PET_SIZES.get(settings.character_size,176));self.pet.costume=settings.costume;self.pet.clicked.connect(self.toggle_bubble);layout.addWidget(self.pet,0,Qt.AlignRight)
        self.balloon=Balloon();self.balloon.clicked.connect(self.accept_balloon)
        self.balloon_timer=QTimer(self);self.balloon_timer.setSingleShot(True);self.balloon_timer.timeout.connect(self.hide_balloon)
        self.idle_timer=QTimer(self);self.idle_timer.setInterval(1000);self.idle_timer.timeout.connect(self.choose_idle)
        self.walk_timer=QTimer(self);self.walk_timer.setInterval(60);self.walk_timer.timeout.connect(self.walk)
        self.fullscreen_timer=QTimer(self);self.fullscreen_timer.setInterval(10_000);self.fullscreen_timer.timeout.connect(self.check_fullscreen)
        self.bubblebox.hide();self.setFixedSize(*self.compact_size());self.animate(False);self.apply_preferences()
        self.retranslate();self.message.setPlainText(tr(settings.locale,'welcome_desktop'))
        rect=QGuiApplication.primaryScreen().availableGeometry();self.move(rect.right()-self.width()-20,rect.bottom()-self.height()-30)
        QApplication.instance().installEventFilter(self)
        self.pet.installEventFilter(self)
    def compact_size(self):
        size=self.pet.width();return (size+16,self.pet.height()+16)
    def expanded_size(self):
        """Fit the popup to its content and to the monitor (never a fixed height that cuts text)."""
        screen=(self.screen() if hasattr(self,'screen') and self.screen() else QGuiApplication.primaryScreen()).availableGeometry()
        self.bubblebox.adjustSize();height=self.bubblebox.sizeHint().height()
        total=height+12+self.pet.height()+16
        if total>screen.height()-8:
            # Small screen: the message area scrolls instead of the popup leaving the screen.
            spare=total-(screen.height()-8);self.message.setFixedHeight(max(48,self.message.height()-spare));self.bubblebox.adjustSize()
            total=min(screen.height()-8,self.bubblebox.sizeHint().height()+12+self.pet.height()+16)
        return (max(POPUP_WIDTH+16,self.pet.width()+16),total)
    def fit_message(self):
        """The message area grows with its text (up to a limit, then it scrolls)."""
        doc=self.message.document();doc.setTextWidth(max(120,POPUP_WIDTH-80))
        height=int(doc.size().height())+10
        self.message.setFixedHeight(max(44,min(height,220)))
        if self.bubblebox.isVisible():self.setFixedSize(*self.expanded_size())
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
        self.update_mask()
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
    def update_mask(self):
        """Compact LAFA only takes clicks on the character itself; transparent
        corners pass clicks through to the windows below. The popup is a full window."""
        if self.bubblebox.isVisible() or not hasattr(self,'pet'):self.clearMask();return
        region=self.pet.mask_region().translated(self.pet.pos())
        if region.isEmpty():self.clearMask()
        else:self.setMask(region)
    def set_state(self,state):
        self.pet.set_state(state);self.update_mask();self.duty_label.setText('· '+personality.duty(self.lang,self.pet.state));self.activity_changed.emit(self.pet.state)
    def retranslate(self):
        lang=self.lang
        self.setToolTip('')
        self.input.setPlaceholderText(tr(lang,'popup_search'));self.input.setAccessibleName(tr(lang,'popup_search'));self.full_button.setText(tr(lang,'popup_open_desktop'))
        self.voice_button.setText(tr(lang,'read_aloud_btn'));self.joke_button.setToolTip(tr(lang,'tell_joke'));self.close_button.setToolTip(tr(lang,'close'));self.close_button.setAccessibleName(tr(lang,'close'))
        self.quiet_button.blockSignals(True);self.quiet_button.setChecked(self.settings.quiet_mode);self.quiet_button.blockSignals(False);self.quiet_button.setText(tr(lang,'quiet_short'));self.quiet_button.setToolTip(tr(lang,'quiet_mode'))
        self.joke_button.setVisible(self.settings.entertainment)
        for key,b in self.quick_buttons:
            text=tr(lang,dict((k,l) for k,l,_,_ in TILES)[key]);b.setText(text);b.setAccessibleName(text)
        self.status.setText('● '+tr(lang,'popup_ready'));self.status.setToolTip(tr(lang,'online') if self.online else tr(lang,'local_ready'));self.source_button.setText(tr(lang,'source'))
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
            # Never close while the learner is typing (text or focus in the search field).
            if not self.input.text().strip() and not self.input.hasFocus():self.collapse()
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
            # Slow down for the last steps, then stop on both feet.
            left=abs(self.walk_target-self.x());step=min(step,max(1,math.ceil(left/8)))
            self.direction=1 if self.walk_target>self.x() else -1;nx=self.x()+self.direction*min(step,left)
        self.pet.direction=self.direction
        y=self.panel_y(rect) if self.settings.panel_roam else self.y()
        old=self.x();self.move(max(rect.left(),min(nx,rect.right()-self.width()+1)),y)
        self.pet.advance(self.x()-old);self.update_mask()
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
        self.update_mask();self.update()
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
        """Click on Lafa: the quick-access popup with one learning recommendation
        (continue the last material, or start with a topic)."""
        if self.bubblebox.isVisible():self.collapse()
        elif not self.introduced and not getattr(self,'recommendation',''):self.show_bubble(self.introduction())
        else:self.show_bubble(getattr(self,'recommendation','') or tr(self.lang,'popup_recommend'))
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
        p=QPainter(self);p.setRenderHint(QPainter.Antialiasing);p.setPen(Qt.NoPen);p.setBrush(QColor(255,255,255))
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
