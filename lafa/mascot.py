"""Lafa's character: the drawings (Atlas) and the animated figure (Character).

The Virtual Assistant that uses them (popup, tips, walking on the
Eduka-Panel) is in lafa/assistant.py. Poses come from sprite sheets per
outfit; the waving poses are cut from the owner's character sheet
(tools/make-poses.py). Movement is procedural (motion.py) and is drawn at
up to 60 frames a second with cached, pre-scaled pictures.
"""
from pathlib import Path
import json
import time
from .qt import Qt,QTimer,QPointF,QRectF,QRect,Signal,QPixmap,QPainter,QColor,QCursor,QRegion,QWidget
from .config import STATES
from . import outfits
from .motion import Motion

ASSET=Path(__file__).parent/'assets'/'lafa-atlas.png'
GREETING={'greeting','waving'}

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
        # Waving poses cut from the owner's character sheet (tools/make-poses.py).
        self.wave={}
        try:
            meta=json.loads(ASSET.with_name('lafa-poses.json').read_text());sheet=QPixmap(str(ASSET.with_name('lafa-poses.png')))
            if not sheet.isNull():
                for outfit,rect in meta['rects'].items():self.wave[outfit]=sheet.copy(*rect)
        except (OSError,ValueError,KeyError):self.wave={}
        self._scaled={}
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
        """A pose scaled into a size×size box (cached: painting 60 times a second must not rescale)."""
        pose=outfits.pose_of(state);key=(pose,int(size),costume)
        cached=self._scaled.get(key)
        if cached is not None:return cached
        if pose in GREETING and self.wave.get(costume) is not None:
            # The waving drawing is scaled to the body height of the standing pose.
            idle=self.pixmap('idle',size,costume);t,b,_l,_r=self.extent(idle);src=self.wave[costume]
            h=max(1,b-t);w=max(1,round(src.width()*h/src.height()))
            body=src.scaled(w,h,Qt.KeepAspectRatio,Qt.SmoothTransformation)
            result=QPixmap(max(int(size),w),int(size));result.fill(Qt.transparent)
            painter=QPainter(result);painter.drawPixmap((result.width()-body.width())//2,t,body);painter.end()
        else:
            poses=self.outfits.get(costume) or self.poses
            if pose not in poses:poses=self.traditional if pose in self.traditional else self.poses
            result=poses.get(pose,self.poses.get(pose,self.poses['idle'])).scaled(int(size),int(size),Qt.KeepAspectRatio,Qt.SmoothTransformation)
        if len(self._scaled)>400:self._scaled.clear()
        self._scaled[key]=result;return result
    def pose_pixmap(self,costume='casual',size=180):
        """The waving pose of an outfit (the owner's design), for headers and the greeting."""
        src=self.wave.get(costume)
        if src is None:return self.pixmap('idle',size,costume)
        key=('wave-full',int(size),costume)
        if key not in self._scaled:self._scaled[key]=src.scaled(int(size),int(size),Qt.KeepAspectRatio,Qt.SmoothTransformation)
        return self._scaled[key]

class Character(QWidget):
    """LAFA drawn with human-like movement (see motion.py)."""
    clicked=Signal()
    FRAME_MS=16
    def __init__(self,atlas,parent=None,size=190):
        super().__init__(parent);self.atlas=atlas;self.state='idle';self.costume='casual';self.phase=0;self.animated=True;self.direction=1;self.rate=1.0
        self.motion=Motion();self.previous=None
        self.distance=0.0;self.moved_at=0.0;self.hold=0   # walk cycle: travelled pixels, last move, contact-pose ticks
        self.setFixedSize(size,size+16);self.setMouseTracking(True);self.last_tick=time.monotonic();self.slow_frames=0
        self.timer=QTimer(self);self.timer.setTimerType(Qt.PreciseTimer);self.timer.timeout.connect(self.tick);self.timer.start(self.FRAME_MS)
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
        state=state if state in STATES or state in outfits.ACTIVITIES or state in GREETING else 'idle'
        if state=='walking' and self.state!='walking':self.distance=0.0;self.hold=2   # start from the contact pose
        if state!=self.state and self.animated and self.timer.isActive():
            self.previous=(self.state,self.costume);self.motion.changed()
            if state in {'talking','greeting'} and self.state in {'idle','sitting'}:self.motion.play('wave')
        self.state=state;self.update()
    @property
    def pose(self):return outfits.pose_of(self.state)
    def animate(self,enabled):
        self.animated=enabled
        if enabled:self.last_tick=time.monotonic();self.timer.start(self.FRAME_MS)
        else:self.timer.stop()
        self.update()
    def tick(self):
        # Real elapsed time keeps the speed right even when a frame is late; slow
        # computers fall back to 30 frames a second.
        now=time.monotonic();elapsed=min(0.1,max(0.0,now-self.last_tick));self.last_tick=now
        if elapsed>0.028:self.slow_frames+=1
        else:self.slow_frames=max(0,self.slow_frames-1)
        if self.slow_frames>45 and self.timer.interval()<33:self.timer.setInterval(33)
        seconds=elapsed*self.rate;self.phase+=1.55*seconds
        self.motion.advance(seconds)
        # A walking LAFA that is not being moved (Desktop preview, Wayland) walks on the spot at a calm pace.
        if self.state=='walking' and now-self.moved_at>0.4 and not getattr(self,'reduce_motion',False):
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
