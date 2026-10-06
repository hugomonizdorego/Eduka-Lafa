"""XDG configuration; API secrets are never written into configuration files."""
from dataclasses import dataclass, field, asdict
from pathlib import Path
import json
import locale
import os
import tempfile
import stat

PROVIDERS = {
    "openai": ("OpenAI", "https://api.openai.com/v1/responses", "OPENAI_API_KEY"),
    "gemini": ("Gemini", "https://generativelanguage.googleapis.com/v1beta", "GEMINI_API_KEY"),
    "anthropic": ("Claude", "https://api.anthropic.com/v1/messages", "ANTHROPIC_API_KEY"),
    "deepseek": ("DeepSeek", "https://api.deepseek.com/chat/completions", "DEEPSEEK_API_KEY"),
    "perplexity": ("Perplexity", "https://api.perplexity.ai/v1/agent", "PERPLEXITY_API_KEY"),
    # Open-source models: a local Ollama server, or any OpenAI-compatible
    # open-source server (llama.cpp, vLLM, LocalAI, a school-hosted model).
    "ollama": ("Ollama (open-source, local)", "/api/chat", "LAFA_OLLAMA_API_KEY"),
    "compatible": ("Open-source server (OpenAI-compatible)", "/chat/completions", "LAFA_COMPATIBLE_API_KEY"),
}
# Providers that work without an API key and with a user-selected endpoint.
OPEN_SOURCE = {"ollama", "compatible"}
DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434"
HUB = [
    ("ChatGPT", "https://chatgpt.com/", "hub_chat_learning"),
    ("Gemini", "https://gemini.google.com/", "hub_multimodal"),
    ("Claude", "https://claude.ai/", "hub_writing"),
    ("Copilot", "https://copilot.microsoft.com/", "hub_chat_search"),
    ("DeepSeek", "https://chat.deepseek.com/", "hub_reasoning"),
    ("Perplexity", "https://www.perplexity.ai/", "hub_research"),
    ("NotebookLM", "https://notebooklm.google.com/", "hub_notes"),
    ("Midjourney", "https://www.midjourney.com/", "hub_images"),
    ("Adobe Firefly", "https://firefly.adobe.com/", "hub_media"),
    ("ElevenLabs", "https://elevenlabs.io/", "hub_voice"),
    ("Cursor", "https://cursor.com/", "hub_code"),
    ("Lovable", "https://lovable.dev/", "hub_apps"),
]
STATES = ["idle", "reading", "thinking", "walking", "sitting", "gaming", "serious", "angry", "talking", "sleeping", "bathing", "toilet", "studying", "eating", "stretching", "tebe", "bidu"]
IDLE_ACTIVITIES = ["idle", "reading", "thinking", "walking", "sitting", "gaming", "sleeping", "bathing", "toilet", "studying", "eating", "stretching", "tebe", "bidu"]

def default_language():
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
    provider: str = "openai"
    models: dict = field(default_factory=lambda: {p: "" for p in PROVIDERS})
    roots: list = field(default_factory=default_roots)
    companion: bool = False
    roam: bool = True
    speak_answers: bool = False
    preset: str = "fast"
    transcription_model: str = "whisper-1"
    idle_seconds: int = 60
    personal_activities: bool = True
    weather_city: str = "Dili"
    weather_latitude: float = -8.5586
    weather_longitude: float = 125.5736
    weather_timezone: str = "Asia/Dili"
    costume: str = "traditional"
    cultural_cards: bool = True
    positive_messages: bool = True
    card_minutes: int = 5
    news_minutes: int = 30
    local_news_updates: bool = True
    panel_edge: str = "bottom"
    panel_height: int = 42
    panel_roam: bool = True
    ollama_url: str = DEFAULT_OLLAMA_URL
    compatible_url: str = ""
    greet_by_time: bool = True

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
        defaults=cls();values={}
        enums={'language':{'system','en','id','pt','tet'},'provider':set(PROVIDERS),'costume':{'traditional','casual'},'panel_edge':{'bottom','top'},'preset':{'fast'}}
        for name,choices in enums.items():
            value=data.get(name,getattr(defaults,name))
            values[name]=value if isinstance(value,str) and value in choices else getattr(defaults,name)
        for name in ['companion','roam','speak_answers','personal_activities','cultural_cards','positive_messages','local_news_updates','panel_roam','greet_by_time']:
            value=data.get(name,getattr(defaults,name));values[name]=value if isinstance(value,bool) else getattr(defaults,name)
        import math
        for name,lower,upper in [('panel_height',0,160),('card_minutes',1,120),('news_minutes',10,240)]:
            try:
                value=data.get(name,getattr(defaults,name))
                if isinstance(value,bool) or not isinstance(value,(int,float,str)) or not math.isfinite(float(value)):raise ValueError()
                values[name]=max(lower,min(upper,int(value)))
            except (TypeError,ValueError,OverflowError):values[name]=getattr(defaults,name)
        for name,limit in [('weather_city',120),('weather_timezone',100),('transcription_model',120)]:
            value=data.get(name,getattr(defaults,name))
            values[name]=value.strip() if isinstance(value,str) and value.strip() and len(value)<=limit and not any(ord(c)<32 for c in value) else getattr(defaults,name)
        for name,loopback in [('ollama_url',True),('compatible_url',False)]:
            value=data.get(name,getattr(defaults,name))
            values[name]=value if isinstance(value,str) and (value=='' and not loopback or valid_endpoint(value,loopback)) else getattr(defaults,name)
        roots=data.get('roots',defaults.roots)
        values['roots']=list(dict.fromkeys(p for p in roots[:100] if isinstance(p,str) and 0<len(p)<=4096 and '\x00' not in p and Path(p).is_absolute())) if isinstance(roots,list) else defaults.roots
        models=data.get('models',{})
        values['models']={p:m for p,m in models.items() if p in PROVIDERS and isinstance(m,str) and len(m)<=120 and not any(ord(c)<32 for c in m)} if isinstance(models,dict) else {}
        try:
            lat=float(data.get('weather_latitude',defaults.weather_latitude));lon=float(data.get('weather_longitude',defaults.weather_longitude))
            if not math.isfinite(lat) or not math.isfinite(lon) or not -90<=lat<=90 or not -180<=lon<=180:raise ValueError()
            values['weather_latitude'],values['weather_longitude']=lat,lon
        except (TypeError,ValueError,OverflowError):
            values['weather_latitude'],values['weather_longitude']=defaults.weather_latitude,defaults.weather_longitude
            values['weather_city'],values['weather_timezone']=defaults.weather_city,defaults.weather_timezone
        values['idle_seconds']=60
        return cls(**values)

    def save(self, path=None):
        path = Path(path) if path else config_path()
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".lafa-")
        try:
            with os.fdopen(fd, "w") as f:
                json.dump(asdict(self), f, indent=2, ensure_ascii=False)
            os.replace(tmp, path)
            path.chmod(0o600)
        finally:
            if os.path.exists(tmp): os.unlink(tmp)

    def model(self, provider=None):
        p = provider or self.provider
        return os.environ.get(f"LAFA_{p.upper()}_MODEL") or self.models.get(p, "")

def valid_endpoint(url, loopback=False):
    """Ollama must stay on this computer; other servers must use HTTPS."""
    from urllib.parse import urlsplit
    if not isinstance(url, str) or not 0 < len(url) <= 300 or any(ord(c) < 33 for c in url): return False
    try: parts = urlsplit(url); parts.port
    except ValueError: return False
    if not parts.hostname or parts.username or parts.password or parts.query or parts.fragment: return False
    if loopback: return parts.scheme in {"http", "https"} and parts.hostname in {"127.0.0.1", "localhost", "::1"}
    return parts.scheme == "https"

def config_path():
    return Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))) / "lafa" / "settings.json"

class Secrets:
    def __init__(self): self.session = {}
    def get(self, provider):
        if provider in self.session: return self.session[provider]
        key = os.environ.get(PROVIDERS[provider][2], "")
        if key: return key
        try:
            import keyring
            if secure_backend(keyring.get_keyring()):
                return keyring.get_password("lafa", provider) or ""
        except Exception: pass
        return ""
    def set(self, provider, key, persist=False):
        if persist:
            import keyring
            if not secure_backend(keyring.get_keyring()):
                raise RuntimeError("No secure system keyring is available. Use a session key or environment variable.")
            keyring.set_password("lafa", provider, key)
        self.session[provider] = key
    def clear(self, provider):
        self.session.pop(provider, None)
        try:
            import keyring
            if secure_backend(keyring.get_keyring()): keyring.delete_password("lafa", provider)
        except Exception: pass

def secure_backend(backend):
    # Explicitly reject plaintext/chained fallback backends.
    name = type(backend).__module__.lower()
    return any(s in name for s in ("secretservice", "kwallet", "macos", "windows")) and "plaintext" not in name
