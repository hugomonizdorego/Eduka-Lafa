"""LAFA preferences (XDG configuration, 0600).

Lafa 0.3: Lafa Desktop is the Ensiklopédia Timór-Leste (pages in SECTIONS);
older start pages map to the nearest new page (LEGACY_PAGES).

LAFA's main functions need no login, no AI key and no internet, so there are
no AI provider, model, key or credit settings. Settings files written by LAFA
0.1.x contained such fields; they are ignored now. The first time such a file
is read, LAFA keeps an untouched copy next to it (settings.json.0.1-backup)
so nothing the user saved is lost. LAFA never reads or clears the system
keyring: keys stored there by 0.1.x stay where the user put them.
"""
from dataclasses import dataclass, field, asdict
from pathlib import Path
import json
import locale
import os
import shutil
import tempfile
import stat

# Optional links in Library → External sites. They open in the user's own web
# browser; LAFA never signs in, reads accounts, cookies or sessions, and never
# sends questions or documents there.
AI_LINKS = [
    ("ChatGPT", "https://chatgpt.com/"),
    ("Claude", "https://claude.ai/"),
    ("Gemini", "https://gemini.google.com/"),
]
STATES = ["idle", "reading", "thinking", "walking", "sitting", "gaming", "serious", "angry", "talking", "sleeping", "bathing", "toilet", "studying", "eating", "stretching", "tebe", "bidu"]
IDLE_ACTIVITIES = ["idle", "reading", "thinking", "walking", "sitting", "gaming", "sleeping", "bathing", "toilet", "studying", "eating", "stretching", "tebe", "bidu"]
# Activities that are entertainment only (off unless the user enables them).
ENTERTAINMENT = {"bathing", "toilet", "magic_show", "comedian", "party", "gaming"}

# The pages of Lafa Desktop 0.3 (Ensiklopédia Timór-Leste).
SECTIONS = ["home", "encyclopedia", "map", "timeline", "places", "calendar", "quiz", "language", "paths"]
# Start pages saved by Lafa 0.1.x / 0.2.x and where they live now.
LEGACY_PAGES = {"study": "paths", "library": "encyclopedia", "timor": "encyclopedia", "activities": "home", "oshelp": "home",
                "classroom": "paths", "teachers": "paths", "exams": "quiz", "languages": "language", "coding": "home",
                "learn": "encyclopedia", "hub": "home", "chat": "home", "files": "home", "culture": "encyclopedia", "live": "home",
                "homework": "home", "reminders": "home", "report": "paths", "os_help": "home"}
LEVELS = ["eb1", "eb2", "eb3", "es", "sup"]
# Old age levels (0.2) → school levels of the Ministry of Education (0.3).
LEGACY_LEVELS = {"early": "eb1", "primary": "eb2", "middle": "eb3", "school": "eb3", "secondary": "es", "university": "sup", "adult": "sup", "senior": "sup"}
VOCAB_TARGETS = ["pt", "id", "en", "ms", "fil", "th", "vi", "km", "lo", "my", "zh", "ta", "es", "fr"]
# Fields of LAFA 0.1.x that are no longer used (AI providers and keys).
LEGACY_KEYS = {"provider", "models", "preset", "transcription_model", "ollama_url", "compatible_url"}

def default_language():
    # On Edukasaun OS LAFA follows the language chosen in Eduka-Settings.
    from . import eduka
    if eduka.installed():return eduka.language()
    raw = os.environ.get("LC_ALL") or os.environ.get("LC_MESSAGES") or os.environ.get("LANGUAGE") or os.environ.get("LANG") or locale.getlocale()[0] or "en"
    raw = raw.split(":")[0].replace("-","_").split("_")[0].split(".")[0].lower()
    return raw if raw in {"en", "id", "pt", "tet"} else "en"

def default_roots():
    home = Path.home()
    roots = [home / p for p in ("Desktop", "Documents", "Downloads", "Music", "Videos", "Pictures")]
    # Follow translated XDG directory names without evaluating shell expressions.
    xdg = Path(os.environ.get("XDG_CONFIG_HOME", str(home / ".config"))) / "user-dirs.dirs"
    if xdg.is_file():
        for line in xdg.read_text(errors="replace").splitlines():
            if line.startswith("XDG_") and "_DIR=" in line:
                value = line.split("=", 1)[1].strip().strip('"').replace("$HOME", str(home))
                p = Path(value)
                if p.is_absolute() and "$" not in value:
                    roots.append(p)
    return list(dict.fromkeys(str(p) for p in roots if p.is_dir()))

@dataclass
class Settings:
    language: str = "system"
    roots: list = field(default_factory=default_roots)
    companion: bool = False
    roam: bool = True
    speak_answers: bool = False
    idle_seconds: int = 60
    personal_activities: bool = True
    weather_city: str = "Dili"
    weather_latitude: float = -8.5586
    weather_longitude: float = 125.5736
    weather_timezone: str = "Asia/Dili"
    costume: str = "traditional"
    cultural_cards: bool = True
    positive_messages: bool = True
    card_minutes: int = 15
    news_minutes: int = 60
    local_news_updates: bool = False
    panel_edge: str = "bottom"
    panel_height: int = 42
    panel_roam: bool = True
    greet_by_time: bool = True
    hover_questions: bool = True
    chatter: bool = True
    fun_messages: bool = True
    # Lafa-Configuration (Eduka-Settings): Eduka-Desktop compatibility and tuning.
    follow_eduka_panel: bool = True
    follow_eduka_theme: bool = True
    notifications: bool = True
    walk_speed: str = "normal"
    animation_speed: str = "normal"
    character_size: str = "normal"
    balloon_seconds: int = 6
    speech_rate: int = 155
    auto_update: bool = True
    update_hours: int = 24
    start_with_session: bool = True
    start_page: str = "home"
    click_recommendations: bool = True
    smooth_scrolling: bool = True
    depth_effects: bool = False
    # Classroom: "school" (Timor-Leste school lessons) or an age level (5–100).
    learner_level: str = "school"
    # Virtual Assistant: calm by default.
    quiet_mode: bool = False          # no spontaneous messages at all
    reduce_motion: bool = False       # no walking, gestures or fades
    entertainment: bool = False       # magician, mind reader, jokes, bathing/toilet scenes
    messages_per_hour: int = 4        # limit for spontaneous messages
    # Lafa 0.3 — Ensiklopédia Timór-Leste
    learner_name: str = ""            # shown in the greeting; empty = the system user's first name
    school_level: str = "eb3"         # eb1 eb2 eb3 es sup (Ministry of Education levels)
    theme: str = "auto"               # light | dark | auto (auto follows Eduka-Settings)
    text_scale: int = 100             # 100 / 115 / 130 / 150 %
    vocab_lang: str = "pt"            # target language in "Aprende lian"
    quiz_timer: bool = False          # millionaire quiz with a timer per question
    knowledge_tips: bool = True       # the Virtual Assistant shares facts, words and holidays

    @property
    def locale(self):return default_language() if self.language=="system" else self.language

    @classmethod
    def load(cls,path=None):
        path=Path(path) if path else config_path()
        try:
            fd=os.open(path,os.O_RDONLY|os.O_NONBLOCK|getattr(os,'O_NOFOLLOW',0))
            with os.fdopen(fd,'rb') as stream:
                info=os.fstat(stream.fileno())
                if not stat.S_ISREG(info.st_mode):return cls()
                raw=stream.read(65537)
            if len(raw)>65536:return cls()
            data=json.loads(raw)
            if not isinstance(data,dict):return cls()
        except (OSError,ValueError,UnicodeError):return cls()
        if LEGACY_KEYS & set(data):backup_legacy(path)
        defaults=cls();values={}
        start=data.get('start_page')
        if isinstance(start,str) and start in LEGACY_PAGES:data=dict(data,start_page=LEGACY_PAGES[start])
        level=data.get('school_level')
        if not isinstance(level,str) or level not in LEVELS:data=dict(data,school_level=LEGACY_LEVELS.get(data.get('learner_level'),'eb3'))
        enums={'school_level':set(LEVELS),'theme':{'light','dark','auto'},'vocab_lang':set(VOCAB_TARGETS),'language':{'system','en','id','pt','tet'},'costume':{'traditional','tuxedo','casual'},'walk_speed':{'slow','normal','fast'},'animation_speed':{'slow','normal','fast'},'character_size':{'small','normal','large'},'start_page':set(SECTIONS),'panel_edge':{'bottom','top'},'learner_level':{'school','early','primary','middle','secondary','university','adult','senior'}}
        for name,choices in enums.items():
            value=data.get(name,getattr(defaults,name))
            values[name]=value if isinstance(value,str) and value in choices else getattr(defaults,name)
        for name in ['companion','roam','speak_answers','personal_activities','cultural_cards','positive_messages','local_news_updates','panel_roam','greet_by_time','hover_questions','chatter','fun_messages','follow_eduka_panel','follow_eduka_theme','notifications','auto_update','start_with_session','click_recommendations','smooth_scrolling','depth_effects','quiet_mode','reduce_motion','entertainment','quiz_timer','knowledge_tips']:
            value=data.get(name,getattr(defaults,name));values[name]=value if isinstance(value,bool) else getattr(defaults,name)
        import math
        for name,lower,upper in [('panel_height',0,160),('card_minutes',1,120),('news_minutes',10,240),('idle_seconds',20,600),('balloon_seconds',3,20),('speech_rate',80,260),('update_hours',6,168),('messages_per_hour',0,20)]:
            try:
                value=data.get(name,getattr(defaults,name))
                if isinstance(value,bool) or not isinstance(value,(int,float,str)) or not math.isfinite(float(value)):raise ValueError()
                values[name]=max(lower,min(upper,int(value)))
            except (TypeError,ValueError,OverflowError):values[name]=getattr(defaults,name)
        scale=data.get('text_scale',100)
        values['text_scale']=scale if isinstance(scale,int) and not isinstance(scale,bool) and scale in (100,115,130,150) else 100
        name_value=data.get('learner_name','')
        values['learner_name']=name_value.strip()[:40] if isinstance(name_value,str) and not any(ord(c)<32 for c in name_value) else ''
        for name,limit in [('weather_city',120),('weather_timezone',100)]:
            value=data.get(name,getattr(defaults,name))
            values[name]=value.strip() if isinstance(value,str) and value.strip() and len(value)<=limit and not any(ord(c)<32 for c in value) else getattr(defaults,name)
        roots=data.get('roots',defaults.roots)
        values['roots']=list(dict.fromkeys(p for p in roots[:100] if isinstance(p,str) and 0<len(p)<=4096 and '\x00' not in p and Path(p).is_absolute())) if isinstance(roots,list) else defaults.roots
        try:
            lat=float(data.get('weather_latitude',defaults.weather_latitude));lon=float(data.get('weather_longitude',defaults.weather_longitude))
            if not math.isfinite(lat) or not math.isfinite(lon) or not -90<=lat<=90 or not -180<=lon<=180:raise ValueError()
            values['weather_latitude'],values['weather_longitude']=lat,lon
        except (TypeError,ValueError,OverflowError):
            values['weather_latitude'],values['weather_longitude']=defaults.weather_latitude,defaults.weather_longitude
            values['weather_city'],values['weather_timezone']=defaults.weather_city,defaults.weather_timezone
        return cls(**values)

    def save(self, path=None):
        path = Path(path) if path else config_path()
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".lafa-")
        try:
            os.fchmod(fd, 0o600)
            with os.fdopen(fd, "w") as f:
                json.dump(asdict(self), f, indent=2, ensure_ascii=False)
            os.replace(tmp, path)
        finally:
            if os.path.exists(tmp): os.unlink(tmp)

def backup_legacy(path):
    """Keep the user's 0.1.x settings file once, untouched, before it is rewritten."""
    backup = Path(str(path) + ".0.1-backup")
    if backup.exists(): return
    try:
        fd = os.open(backup, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "wb") as out, open(path, "rb") as source: shutil.copyfileobj(source, out)
    except OSError:
        pass

def config_path():
    return Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))) / "lafa" / "settings.json"

def data_dir():
    """The learner's Lafa folder (~/.local/share/lafa): progress, downloads, updates."""
    return Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local" / "share"))) / "lafa"
