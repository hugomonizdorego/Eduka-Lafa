"""LAFA as a helping agent: understands everyday requests and acts on them.

Like Voice-Command and Linubot, LAFA can *do* things, but only from a fixed,
safe list (never a shell command typed by someone):

* open an application of Edukasaun OS ("buka browser", "loke kalkuladora",
  "open the file manager", "abre o LibreOffice");
* open a page of LAFA ("buka kelas", "open exams", "loke biblioteka");
* ask the AI websites in the AI Hub ("tanya Gemini apa itu fotosintesis");
* search LAFA's memory ("cari tentang kopi");
* set a reminder ("ingatkan saya 10 menit lagi minum air").

Requests are understood in English, Indonesian, Portuguese and Tetun. The
actual launching is done by the app (QProcess, detached) with the absolute
path of an installed program found on PATH.
"""
from dataclasses import dataclass
import re
import shutil
import unicodedata

def fold(text):
    text = unicodedata.normalize("NFKD", str(text).casefold())
    return "".join(c for c in text if not unicodedata.combining(c)).strip()

@dataclass(frozen=True)
class App:
    key: str
    names: tuple          # words people use for it (folded)
    commands: tuple       # programs tried in order (first installed wins)
    icon: str = "🗔"

APPS = [
    App("browser", ("browser", "peramban", "navegador", "internet", "web", "firefox", "chromium", "chrome"), ("x-www-browser", "firefox-esr", "firefox", "chromium", "chromium-browser", "google-chrome"), "🌐"),
    App("files", ("file manager", "files", "pengelola file", "file", "berkas", "folder", "ficheiros", "arquivos", "explorador", "pasta", "ficheiru", "pcmanfm"), ("pcmanfm-qt", "pcmanfm", "thunar", "nautilus", "dolphin", "nemo"), "📁"),
    App("settings", ("settings", "pengaturan", "setelan", "configuracoes", "definicoes", "konfigurasaun", "eduka-settings", "eduka settings"), ("eduka-settings", "lxqt-config", "gnome-control-center"), "⚙"),
    App("calculator", ("calculator", "kalkulator", "calculadora", "kalkuladora"), ("galculator", "gnome-calculator", "kcalc", "qalculate-gtk", "speedcrunch"), "🧮"),
    App("editor", ("text editor", "editor", "notepad", "editor teks", "editor de texto", "featherpad"), ("featherpad", "mousepad", "gedit", "kate", "xed", "pluma"), "📝"),
    App("writer", ("libreoffice", "writer", "word", "dokumen", "documento", "dokumentu", "office", "kantor"), ("libreoffice",), "📄"),
    App("terminal", ("terminal", "konsol", "consola", "qterminal"), ("qterminal", "x-terminal-emulator", "lxterminal", "gnome-terminal", "konsole", "xterm"), "⌨"),
    App("screenshot", ("screenshot", "tangkapan layar", "captura de ecra", "captura de tela", "foto ekran", "screengrab"), ("screengrab", "flameshot", "gnome-screenshot", "spectacle"), "📸"),
    App("sound", ("volume", "sound", "suara", "audio", "som", "lian", "pavucontrol"), ("pavucontrol-qt", "pavucontrol"), "🔊"),
    App("network", ("wifi", "wi-fi", "network", "jaringan", "internet settings", "rede", "rede sem fios", "network-manager"), ("nm-connection-editor",), "📶"),
    App("printer", ("printer", "pencetak", "impressora", "imprimir", "printa"), ("system-config-printer",), "🖨"),
    App("software", ("software", "aplikasi", "app store", "aplikasaun", "programas", "discover"), ("discover", "gnome-software", "synaptic"), "🛍"),
    App("music", ("music", "musik", "musica", "muzika", "audacious", "rhythmbox"), ("audacious", "rhythmbox", "clementine", "vlc"), "🎵"),
    App("video", ("video", "vlc", "film", "filme", "videu"), ("vlc", "mpv", "totem", "celluloid"), "🎬"),
    App("paint", ("paint", "gambar", "desenho", "dezeñu", "gimp", "kolourpaint"), ("kolourpaint", "pinta", "gimp"), "🎨"),
]
APP_BY_KEY = {a.key: a for a in APPS}

# LAFA pages people may ask for.
PAGES = {
    "home": ("home", "beranda", "inicio", "uma", "lobby"),
    "classroom": ("classroom", "class", "kelas", "lesson", "lessons", "pelajaran", "aula", "aulas", "sala", "lisaun", "klase"),
    "exams": ("exam", "exams", "ujian", "quiz", "kuis", "teste", "exame", "ezame"),
    "report": ("report card", "rapor", "boletim", "relatoriu"),
    "teachers": ("teacher", "teachers", "guru", "professor", "professores", "profesor"),
    "languages": ("language school", "sekolah bahasa", "escola de linguas", "eskola lian", "kursus bahasa"),
    "culture": ("timor-leste", "timor", "atlas", "sejarah timor", "istoria"),
    "learn": ("library", "perpustakaan", "biblioteca", "biblioteka", "lafa search", "pencarian"),
    "hub": ("ai hub", "hub ai", "ai", "kecerdasan buatan", "inteligencia artificial", "intelijensia artifisial"),
    "live": ("notice board", "papan pengumuman", "noticias", "weather", "cuaca", "tempo", "berita"),
    "coding": ("computer lab", "lab komputer", "laboratorio", "coding", "python", "programming", "pemrograman"),
    "files": ("my files", "file saya", "meus ficheiros", "ha'u-nia ficheiru"),
    "reminders": ("reminders", "pengingat", "lembretes", "lembrete", "fó-hanoin"),
    "os_help": ("help desk", "bantuan os", "ajuda os", "ajuda edukasaun"),
}

OPEN = r"(?:open|launch|start|show|buka|bukakan|jalankan|tampilkan|abre|abrir|abra|mostra|loke|hatudu|hahu)"
ASK_AI = r"(?:ask|tanya|tanyakan|pergunta|perguntar|husu)"

@dataclass
class Action:
    kind: str             # app, page, ask_ai, search, remind
    target: str = ""
    text: str = ""
    minutes: int = 0

def which_app(app, which=shutil.which):
    for command in app.commands:
        path = which(command)
        if path: return path
    return None

def _match_name(words, names):
    return max((len(n) for n in names if re.search(r"(?<![\w-])" + re.escape(n) + r"(?![\w-])", words)), default=0)

def parse(message):
    """An Action for an everyday request, or None for ordinary conversation."""
    original = str(message).strip().rstrip(" ?!.")
    prefix = r"^(?:(?:lafa[,!]?|tolong|please|por favor|favor|bele|hey|halo)\s+)+"
    original = re.sub(prefix, "", original, flags=re.I).strip()
    text = fold(original)
    if not text or len(text) > 300: return None
    def keep(m, group):
        """The user's own words (accents and capitals kept) for a matched part."""
        return original[m.start(group):m.end(group)].strip() if len(original) == len(text) else m.group(group).strip()
    # Ask the signed-in AI websites: "tanya gemini apa itu atom".
    m = re.match(ASK_AI + r"\s+(gemini|chatgpt|claude|copilot|deepseek|perplexity|le chat|mistral|qwen|kimi|grok|meta ai|huggingchat|semua ai|all ais?|ai hotu|todas as ias?)\s*[:,]?\s+(.+)$", text)
    if m:
        name = m.group(1).replace(" ", "")
        target = {"lechat": "mistral", "metaai": "meta", "semuaai": "all", "allai": "all", "allais": "all", "aihotu": "all", "todasasia": "all", "todasasias": "all"}.get(name, name)
        return Action("ask_ai", target, keep(m, 2))
    # Reminders: "ingatkan saya 10 menit lagi minum air", "remind me in 5 minutes to stretch".
    m = re.match(r"(?:remind me|ingatkan(?: saya| aku)?|lembra-me|lembrar|fo-hanoin ha'u|fó-hanoin ha'u)\s+(?:in |dalam |em |iha )?(\d{1,4})\s*(?:minutes?|mins?|menit|minutos?|minutu)\s*(?:lagi|again)?\s*(?:to |untuk |para |atu )?(.*)$", text)
    if m:
        return Action("remind", "", keep(m, 2) or "LAFA", max(1, min(1440, int(m.group(1)))))
    # Search LAFA's memory: "cari tentang kopi", "search for atoms".
    m = re.match(r"(?:search(?: for)?|find information about|cari(?:kan)?(?: tentang| informasi tentang)?|procura(?:r)?(?: sobre)?|pesquisa(?:r)?(?: sobre)?|buka informasaun kona-ba|buka kona-ba)\s+(.+)$", text)
    if m and not re.match(r"(?:file|files|dokumen|document|musik|music|video|ficheiru)\b", m.group(1)):
        return Action("search", "", keep(m, 1))
    m = re.match(OPEN + r"\s+(?:the |a |an |aplikasi |aplikasaun |o |a aplicacao |halaman |pajina |page |menu )?(.+)$", text)
    if not m: return None
    what = m.group(1).strip()
    matches = [a for a in APPS if _match_name(what, a.names)]
    # "settings for wifi" means the Wi-Fi settings: the more specific app wins.
    if len(matches) > 1: matches = [a for a in matches if a.key != "settings"]
    best = max(matches or APPS, key=lambda a: _match_name(what, a.names))
    page = max(PAGES, key=lambda k: _match_name(what, PAGES[k]))
    app_score, page_score = _match_name(what, best.names), _match_name(what, PAGES[page])
    if not app_score and not page_score: return None
    # A LAFA page wins when it names a school word ("kelas", "ujian"); an app otherwise.
    if page_score > app_score: return Action("page", page)
    return Action("app", best.key)
