"""Ensiklopédia Timór-Leste — the knowledge base behind Lafa Desktop.

Everything is offline: articles, municipalities, tourist places, holidays,
indicators and the Tetun vocabulary are JSON files in lafa/assets/timor
(docs/CONTENT-SCHEMA.md). Newer content downloaded by the updater
(lafa/sync.py) is read from the learner's data folder and replaces the
packaged file with the same name only when it is valid and newer.

The module gives the pages one simple API: categories, items, search,
holidays for a year, the history timeline, quiz questions by difficulty and
learning paths for the school levels of the Ministry of Education.
"""
import json
import math
import re
import unicodedata
from dataclasses import dataclass, field
from datetime import date, timedelta
from functools import lru_cache
from pathlib import Path

ASSETS = Path(__file__).resolve().parent / "assets" / "timor"
# Interface and content: the official languages (Constitution, art. 13) and
# the working languages English and Bahasa Indonesia (art. 159).
LANGS = ("tet", "pt", "en", "id")
OFFICIAL = ("tet", "pt")
LANG_NAMES = {"tet": "Tetun", "pt": "Português", "en": "English", "id": "Bahasa Indonesia"}
FALLBACK = {"tet": ("tet", "pt", "en", "id"), "pt": ("pt", "tet", "en", "id"),
            "en": ("en", "pt", "tet", "id"), "id": ("id", "en", "tet", "pt")}

def L(tet, pt, en=None, id_=None):
    value = {"tet": tet, "pt": pt}
    if en is not None: value["en"] = en
    if id_ is not None: value["id"] = id_
    return value

def lang_of(locale):
    """A language code of Lafa for a locale such as "pt_PT.UTF-8" or "in" (old code of Indonesian)."""
    code = str(locale or "").split(".")[0].split("_")[0].split("-")[0].lower()
    code = {"in": "id", "tdt": "tet"}.get(code, code)
    return code if code in LANGS else "tet"

def pick(row, lang):
    """The entry for a language from a (tet, pt, en, id) tuple, with the usual fallback."""
    for code in FALLBACK.get(lang, FALLBACK["tet"]):
        i = LANGS.index(code)
        if i < len(row) and isinstance(row[i], str) and row[i].strip(): return row[i]
    return row[0] if row else ""

def text(value, lang="tet"):
    """The value in this language, falling back to a related language."""
    if isinstance(value, dict):
        for code in FALLBACK.get(lang, FALLBACK["tet"]):
            v = value.get(code)
            if isinstance(v, str) and v.strip(): return show(v, code)
        return ""
    return "" if value is None else str(value)

_APOS = re.compile(r"(?<=\w)'(?=\w)")

def show(value, lang):
    """Content uses the plain apostrophe; Tetun is shown with the typographic one (ne’e)."""
    return _APOS.sub("’", value) if lang == "tet" else value

def fold(value):
    """Lower case without accents or apostrophes, for search."""
    value = unicodedata.normalize("NFKD", str(value)).casefold().replace("’", "'")
    return "".join(c for c in value if not unicodedata.combining(c)).replace("'", "")

# Small words ignored when comparing event titles (tet, pt, id, en).
STOPWORDS = set("""iha no nia ba husi ho sira ida ne'e neebe mak sai hosi
o a os as de da do das dos e em no na nos nas um uma para por com que se ao
di dan yang ke dari untuk dengan pada oleh ini itu
the of and in to a an for on by with is as at from its""".replace("'", "").split())

TOKEN = re.compile(r"[0-9a-z฀-໿က-႟ក-៿஀-௿一-鿿]+")

def tokens(value):
    return TOKEN.findall(fold(value))

# --------------------------------------------------------------------- metadata
LEVELS = ["eb1", "eb2", "eb3", "es", "sup"]
LEVEL_NAMES = {
    "eb1": L("Ensinu Báziku – siklu 1 (klase 1–4)", "Ensino Básico – 1.º ciclo (1.º–4.º ano)", "Basic Education – cycle 1 (grades 1–4)", "Pendidikan Dasar – siklus 1 (kelas 1–4)"),
    "eb2": L("Ensinu Báziku – siklu 2 (klase 5–6)", "Ensino Básico – 2.º ciclo (5.º–6.º ano)", "Basic Education – cycle 2 (grades 5–6)", "Pendidikan Dasar – siklus 2 (kelas 5–6)"),
    "eb3": L("Ensinu Báziku – siklu 3 (klase 7–9)", "Ensino Básico – 3.º ciclo (7.º–9.º ano)", "Basic Education – cycle 3 (grades 7–9)", "Pendidikan Dasar – siklus 3 (kelas 7–9)"),
    "es": L("Ensinu Sekundáriu (klase 10–12)", "Ensino Secundário (10.º–12.º ano)", "Secondary Education (grades 10–12)", "Pendidikan Menengah (kelas 10–12)"),
    "sup": L("Ensinu Superiór no adultu", "Ensino Superior e adultos", "Higher education and adults", "Pendidikan Tinggi dan umum"),
}
LEVEL_SHORT = {"eb1": "EB 1", "eb2": "EB 2", "eb3": "EB 3", "es": "ES", "sup": "SUP"}
# Millionaire steps that suit each level (questions carry a difficulty 1–15).
LEVEL_DIFFICULTY = {"eb1": (1, 5), "eb2": (1, 7), "eb3": (3, 10), "es": (5, 13), "sup": (7, 15)}

@dataclass(frozen=True)
class Category:
    key: str
    title: dict
    summary: dict
    icon: str
    accent: str
    illustration: str

CATEGORIES = [
    Category("land", L("Rai, Jeolojia no Klima", "Terra, geologia e clima", "Land, geology and climate", "Daratan, geologi dan iklim"),
             L("Oinsá tasi-le'un Timór moris, foho, mota no tempu.", "Como a ilha se formou, montanhas, rios e clima.", "How the island formed, mountains, rivers and climate.", "Bagaimana pulau terbentuk, gunung, sungai dan iklim."), "mountain", "peach", "island-formation"),
    Category("nature", L("Natureza no Biodiversidade", "Natureza e biodiversidade", "Nature and biodiversity", "Alam dan keanekaragaman hayati"),
             L("Manu, lafaek, tasi no ai-laran sira.", "Aves, crocodilos, mar e florestas.", "Birds, crocodiles, the sea and forests.", "Burung, buaya, laut dan hutan."), "leaf", "mint", "coral-reef"),
    Category("prehistory", L("Pre-istória", "Pré-história", "Prehistory", "Prasejarah"),
             L("Fósil, animál antigu, ema dahuluk no arte iha fatuk-kuak.", "Fósseis, animais antigos, primeiros povos e arte rupestre.", "Fossils, ancient animals, the first people and rock art.", "Fosil, hewan purba, manusia pertama dan seni cadas."), "layers", "peach", "fossil"),
    Category("history", L("Istória", "História", "History", "Sejarah"),
             L("Husi ema dahuluk to'o 2026.", "Dos primeiros povos até 2026.", "From the first people to 2026.", "Dari manusia pertama sampai 2026."), "scroll", "lilac", "prehistory"),
    Category("colonial", L("Kolonializmu no Okupasaun", "Colonialismo e ocupação", "Colonialism and occupation", "Penjajahan dan pendudukan"),
             L("Portugál, Olanda, Japaun no Indonézia.", "Portugal, Holanda, Japão e Indonésia.", "Portugal, the Netherlands, Japan and Indonesia.", "Portugal, Belanda, Jepang dan Indonesia."), "ship", "sky", "caravel"),
    Category("conflicts", L("Konflitu no Rekonsiliasaun", "Conflitos e reconciliação", "Conflict and reconciliation", "Konflik dan rekonsiliasi"),
             L("Rezisténsia, terus no dame.", "Resistência, sofrimento e paz.", "Resistance, suffering and peace.", "Perlawanan, penderitaan dan perdamaian."), "dove", "coral", "reconciliation"),
    Category("politics", L("Estadu no Polítika", "Estado e política", "State and politics", "Negara dan politik"),
             L("Lei-Inan, órgaun soberania no eleisaun sira.", "Constituição, órgãos de soberania e eleições.", "Constitution, institutions and elections.", "Konstitusi, lembaga negara dan pemilu."), "landmark", "violet", "parliament"),
    Category("institutions", L("Instituisaun Estadu", "Instituições do Estado", "State institutions", "Lembaga negara"),
             L("Ministériu sira, F-FDTL, PNTL no órgaun independente.", "Ministérios, F-FDTL, PNTL e órgãos independentes.", "Ministries, F-FDTL, PNTL and independent bodies.", "Kementerian, F-FDTL, PNTL dan lembaga independen."), "shield", "indigo", "government-palace"),
    Category("leaders", L("Prezidente no Primeiru-Ministru", "Presidentes e primeiros-ministros", "Presidents and prime ministers", "Presiden dan perdana menteri"),
             L("Lider sira husi 1975 to'o ohin.", "Líderes de 1975 até hoje.", "Leaders from 1975 to today.", "Para pemimpin dari 1975 sampai sekarang."), "user", "pink", "palace"),
    Category("symbols", L("Símbolu Nasionál", "Símbolos nacionais", "National symbols", "Lambang negara"),
             L("Bandeira, emblema, inu nasionál no osan.", "Bandeira, emblema, hino e moeda.", "Flag, emblem, anthem and currency.", "Bendera, lambang, lagu kebangsaan dan mata uang."), "flag-tl", "rose", "flag"),
    Category("geography", L("Mapa, Munisípiu no Tasi-le'un", "Mapa, municípios e ilhas", "Map, municipalities and islands", "Peta, munisipio dan pulau"),
             L("Munisípiu 14, postu administrativu no tasi-le'un sira.", "Os 14 municípios, postos e ilhas.", "The 14 municipalities, posts and islands.", "14 munisipio, pos administratif dan pulau."), "map", "teal", "tl-overview"),
    Category("culture", L("Kultura no Lisan", "Cultura e tradição", "Culture and tradition", "Budaya dan tradisi"),
             L("Tais, uma lulik, dansa, múzika no ai-han.", "Tais, uma lulik, danças, música e comida.", "Tais, sacred houses, dances, music and food.", "Tais, uma lulik, tarian, musik dan makanan."), "palette", "butter", "tais"),
    Category("sports", L("Desportu", "Desporto", "Sports", "Olahraga"),
             L("Futebol, Jogu Olímpiku, SEA Games, arte marsiál no jogu tradisionál.", "Futebol, Jogos Olímpicos, SEA Games, artes marciais e jogos tradicionais.", "Football, Olympic Games, SEA Games, martial arts and traditional games.", "Sepak bola, Olimpiade, SEA Games, bela diri dan permainan tradisional."), "medal", "green", "athletics"),
    Category("society", L("Sosiedade", "Sociedade", "Society", "Masyarakat"),
             L("Populasaun, lian, relijiaun, edukasaun no saúde.", "População, línguas, religião, educação e saúde.", "Population, languages, religion, education and health.", "Penduduk, bahasa, agama, pendidikan dan kesehatan."), "people", "indigo", "population"),
    Category("economy", L("Ekonomia", "Economia", "Economy", "Ekonomi"),
             L("Osan, esportasaun, importasaun no riku-soin naturál.", "Moeda, exportações, importações e recursos.", "Currency, exports, imports and natural resources.", "Mata uang, ekspor, impor dan sumber daya alam."), "chart", "green", "coffee"),
    Category("tourism", L("Turizmu", "Turismo", "Tourism", "Wisata"),
             L("Tasi-ibun, foho, museu no fatin istóriku.", "Praias, montanhas, museus e lugares históricos.", "Beaches, mountains, museums and heritage.", "Pantai, gunung, museum dan tempat bersejarah."), "umbrella", "cyan", "beach"),
    Category("calendar", L("Feriadu no Loron Nasionál", "Feriados e dias nacionais", "Holidays and national days", "Hari libur dan hari nasional"),
             L("Loron importante sira no saida mak ita hanoin.", "Datas importantes e o que se recorda.", "Important days and what they remember.", "Hari penting dan apa yang diperingati."), "calendar-check", "rose", "calendar"),
    Category("world", L("Timór-Leste iha Mundu", "Timor-Leste no mundo", "Timor-Leste in the world", "Timor-Leste di dunia"),
             L("ONU, CPLP, ASEAN no rai viziñu sira.", "ONU, CPLP, ASEAN e vizinhos.", "UN, CPLP, ASEAN and neighbours.", "PBB, CPLP, ASEAN dan negara tetangga."), "globe", "sky", "diplomacy"),
]
CATEGORY = {c.key: c for c in CATEGORIES}

# History eras for the timeline (years; negative = before the common era).
ERAS = [
    ("deep_time", -300_000_000, -50000, L("Rai, fósil no animál antigu", "Terra, fósseis e animais antigos", "Land, fossils and ancient animals", "Tanah, fosil dan hewan purba"), "peach"),
    ("prehistory", -50000, 1500, L("Ema dahuluk no reinu sira", "Primeiros povos e reinos", "First peoples and kingdoms", "Manusia pertama dan kerajaan"), "lilac"),
    ("portuguese", 1515, 1941, L("Tempu Portugés", "Período português", "Portuguese period", "Masa Portugis"), "sky"),
    ("ww2", 1942, 1945, L("Funu Mundiál II", "II Guerra Mundial", "World War II", "Perang Dunia II"), "slate"),
    ("late_colonial", 1945, 1974, L("Timór Portugés ikus", "Timor Português tardio", "Late Portuguese Timor", "Akhir Timor Portugis"), "teal"),
    ("decolonisation", 1974, 1975, L("Dekolonizasaun", "Descolonização", "Decolonisation", "Dekolonisasi"), "butter"),
    ("occupation", 1975, 1999, L("Okupasaun no rezisténsia", "Ocupação e resistência", "Occupation and resistance", "Pendudukan dan perlawanan"), "coral"),
    ("transition", 1999, 2002, L("Tranzisaun ONU", "Transição da ONU", "UN transition", "Transisi PBB"), "indigo"),
    ("state", 2002, 2026, L("Estadu independente", "Estado independente", "Independent State", "Negara merdeka"), "green"),
]

# Where each era begins (year, month, day); an event belongs to the last era that began before it.
ERA_STARTS = [("deep_time", (-10 ** 10, 0, 0)), ("prehistory", (-50000, 0, 0)), ("portuguese", (1515, 0, 0)), ("ww2", (1942, 2, 0)), ("late_colonial", (1945, 9, 0)),
              ("decolonisation", (1974, 4, 25)), ("occupation", (1975, 12, 7)), ("transition", (1999, 10, 25)), ("state", (2002, 5, 20))]

def era_of(key):
    era = ERA_STARTS[0][0]
    for name, start in ERA_STARTS:
        if key >= start: era = name
    return era

# ----------------------------------------------------------------- the items
@dataclass
class Item:
    kind: str            # article | municipality | place | day
    id: str
    data: dict
    def get(self, key, default=None): return self.data.get(key, default)
    @property
    def category(self):
        if self.kind == "article": return self.data.get("category", "history")
        return {"municipality": "geography", "place": "tourism", "day": "calendar"}[self.kind]
    def title(self, lang): return text(self.data.get("title") or self.data.get("name"), lang)
    def summary(self, lang): return text(self.data.get("summary"), lang)
    def levels(self):
        lv = self.data.get("levels")
        if isinstance(lv, list) and lv: return [x for x in lv if x in LEVELS]
        return {"place": ["eb2", "eb3", "es", "sup"], "municipality": ["eb1", "eb2", "eb3", "es", "sup"], "day": ["eb1", "eb2", "eb3", "es", "sup"]}.get(self.kind, ["eb3", "es", "sup"])
    def sections(self, lang):
        out = []
        for s in self.data.get("sections") or []:
            if isinstance(s, dict): out.append((text(s.get("heading"), lang), text(s.get("text"), lang)))
        if self.kind == "place":
            if self.data.get("text"): out.insert(0, ("", text(self.data["text"], lang)))
        return out
    def illustration(self):
        fig = self.data.get("figure")
        if isinstance(fig, dict) and fig.get("illustration"): return fig["illustration"]
        return self.data.get("illustration") or CATEGORY.get(self.category, CATEGORIES[0]).illustration
    def caption(self, lang):
        fig = self.data.get("figure"); return text(fig.get("caption"), lang) if isinstance(fig, dict) else ""
    def image(self):
        """A picture packaged with Lafa for this item (figure.image), or None."""
        fig = self.data.get("figure")
        if not isinstance(fig, dict) or not isinstance(fig.get("image"), str): return None
        path = (ASSETS / fig["image"]).resolve()
        return path if path.is_file() and ASSETS.resolve() in path.parents else None
    def image_credit(self, lang):
        fig = self.data.get("figure"); return text(fig.get("credit"), lang) if isinstance(fig, dict) else ""
    def quiz(self):
        return [q for q in self.data.get("quiz") or [] if isinstance(q, dict) and isinstance(q.get("options"), list) and len(q["options"]) == 4]
    def sources(self):
        return [s for s in self.data.get("sources") or [] if isinstance(s, dict) and str(s.get("url", "")).startswith("https://")]
    def tags(self): return [t for t in self.data.get("tags") or [] if isinstance(t, str)]
    def related(self): return [r for r in self.data.get("related") or [] if isinstance(r, str)]
    def wiki(self): w = self.data.get("wiki"); return w if isinstance(w, dict) else {}
    def review_status(self): r = self.data.get("review"); return r.get("status", "draft") if isinstance(r, dict) else "draft"

@dataclass
class Word:
    id: str
    tet: str
    cat: str
    pos: str
    level: int
    tr: dict = field(default_factory=dict)      # lang -> translation
    ex: dict = field(default_factory=dict)
    rom: dict = field(default_factory=dict)     # lang -> reading in Latin letters (non-Latin scripts)
    def meaning(self, lang): return self.tr.get(lang, "")
    def reading(self, lang): return self.rom.get(lang, "")
    def example(self, lang): return self.ex.get(lang, "") if isinstance(self.ex.get(lang), str) else ""

VOCAB_LANGS = ["pt", "id", "en", "ms", "fil", "th", "vi", "km", "lo", "my", "zh", "ta", "es", "fr"]
VOCAB_LANG_NAMES = {
    "pt": "Português", "id": "Bahasa Indonesia", "en": "English", "ms": "Bahasa Melayu", "fil": "Filipino", "th": "ไทย (Thai)",
    "vi": "Tiếng Việt", "km": "ខ្មែរ (Khmer)", "lo": "ລາວ (Lao)", "my": "မြန်မာ (Burmese)", "zh": "中文 (Chinese)", "ta": "தமிழ் (Tamil)",
    "es": "Español", "fr": "Français"}
# Languages written in their own script: the word lists give a reading in Latin letters.
VOCAB_SCRIPTS = ("th", "km", "lo", "my", "zh", "ta")
VOCAB_GROUPS = {"cplp": ["pt", "es", "fr"], "asean": ["id", "ms", "fil", "th", "vi", "km", "lo", "my", "en", "zh", "ta"]}
VOCAB_CATEGORIES = {
    "greetings": L("Kumprimentu", "Cumprimentos", "Greetings", "Salam"), "numbers": L("Númeru", "Números", "Numbers", "Angka"),
    "time": L("Tempu no kalendáriu", "Tempo e calendário", "Time and calendar", "Waktu dan kalender"),
    "people": L("Família no ema", "Família e pessoas", "Family and people", "Keluarga dan orang"), "body": L("Isin", "Corpo", "Body", "Tubuh"),
    "health": L("Saúde", "Saúde", "Health", "Kesehatan"), "food": L("Ai-han no hemu", "Comida e bebida", "Food and drink", "Makanan dan minuman"),
    "home": L("Uma no sasán", "Casa e objetos", "Home and objects", "Rumah dan benda"), "clothes": L("Hatais", "Roupa", "Outfit", "Pakaian"),
    "colours": L("Kór", "Cores", "Colours", "Warna"), "animals": L("Animál", "Animais", "Animals", "Hewan"),
    "plants": L("Ai-horis no to'os", "Plantas e agricultura", "Plants and farming", "Tumbuhan dan pertanian"),
    "nature": L("Natureza no tempu", "Natureza e tempo", "Nature and weather", "Alam dan cuaca"),
    "places": L("Fatin no dalan", "Lugares e direções", "Places and directions", "Tempat dan arah"), "transport": L("Transporte", "Transportes", "Transport", "Transportasi"),
    "school": L("Eskola", "Escola", "School", "Sekolah"), "work": L("Servisu", "Trabalho", "Work", "Pekerjaan"),
    "state": L("Estadu no sidadania", "Estado e cidadania", "State and citizenship", "Negara dan kewarganegaraan"),
    "culture": L("Kultura no lisan", "Cultura e tradição", "Culture and tradition", "Budaya dan adat"), "religion": L("Relijiaun", "Religião", "Religion", "Agama"),
    "money": L("Osan no merkadu", "Dinheiro e mercado", "Money and market", "Uang dan pasar"), "verbs": L("Verbu", "Verbos", "Verbs", "Kata kerja"),
    "adjectives": L("Adjetivu", "Adjetivos", "Adjectives", "Kata sifat"), "pronouns": L("Pronome no pergunta", "Pronomes e perguntas", "Pronouns and questions", "Kata ganti dan tanya"),
    "function": L("Liafuan ki'ik", "Palavras pequenas", "Small words", "Kata tugas"), "feelings": L("Sentimentu", "Sentimentos", "Feelings", "Perasaan"),
    "sports": L("Desportu", "Desporto", "Sports", "Olahraga"), "technology": L("Teknolojia", "Tecnologia", "Technology", "Teknologi"),
    "sea": L("Tasi no peska", "Mar e pesca", "Sea and fishing", "Laut dan perikanan"), "phrases": L("Fraze útil", "Frases úteis", "Useful phrases", "Kalimat berguna"),
}

def _read_json(path):
    try:
        if path.stat().st_size > 30 * 1024 * 1024: return None
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError):
        return None

class KnowledgeBase:
    """All offline content, loaded once. `overrides` is a folder with newer
    content files (same relative names) downloaded by the updater."""
    def __init__(self, base=ASSETS, overrides=None):
        self.base = Path(base); self.overrides = Path(overrides) if overrides else None
        self.items = {}; self.order = []; self.words = []; self.word_by_id = {}; self.indicators = []
        self.islamic = {}; self.days_notes = {}; self.plan = _read_json(self.base / "plan.json") or {}
        self.map = _read_json(self.base / "map" / "municipalities.json") or {"municipalities": [], "bbox": [124, -9.5, 127.4, -8.1]}
        self.posts = _read_json(self.base / "map" / "posts.json") or {"posts": []}
        self.content_version = ""
        self._load()
        self._index = None
    # ---------------------------------------------------------------- loading
    def _files(self, folder):
        found = {}
        for path in sorted((self.base / folder).glob("*.json")): found[path.name] = path
        if self.overrides and (self.overrides / folder).is_dir():
            for path in sorted((self.overrides / folder).glob("*.json")):
                data = _read_json(path)
                if data is not None: found[path.name] = path
        return list(found.values())
    def _load(self):
        manifest = _read_json(self.base / "manifest.json") or {}
        self.content_version = str(manifest.get("content_version", ""))
        for path in self._files("content"):
            data = _read_json(path)
            if not isinstance(data, dict): continue
            for kind, key in (("article", "articles"), ("municipality", "municipalities"), ("place", "places"), ("day", "days")):
                for raw in data.get(key, []) or []:
                    if isinstance(raw, dict) and isinstance(raw.get("id"), str) and (raw.get("title") or raw.get("name")):
                        if raw["id"] not in self.items: self.order.append(raw["id"])
                        self.items[raw["id"]] = Item(kind, raw["id"], raw)
            if isinstance(data.get("indicators"), list): self.indicators = [i for i in data["indicators"] if isinstance(i, dict)]
            if isinstance(data.get("islamic_dates"), dict): self.islamic = data["islamic_dates"]
            if isinstance(data.get("notes"), dict) and data.get("days"): self.days_notes = data["notes"]
        word_files = [p for p in self._files("vocab") if p.name == "words.json" or p.name.startswith("words_")]
        for path in sorted(word_files, key=lambda p: (p.name != "words.json", p.name)):
            vocab = _read_json(path)
            if not isinstance(vocab, dict): continue
            for w in vocab.get("words", []):
                if not isinstance(w, dict) or not isinstance(w.get("id"), str) or not w.get("tet") or w["id"] in self.word_by_id: continue
                # `id` is the word id; the Indonesian meaning is `ind`.
                tr = {k: w[src] for k, src in (("pt", "pt"), ("id", "ind"), ("en", "en")) if isinstance(w.get(src), str)}
                word = Word(w["id"], w["tet"], w.get("cat", "phrases"), w.get("pos", ""), int(w.get("level", 2)) if str(w.get("level", "2")).isdigit() else 2,
                            tr, w.get("ex") if isinstance(w.get("ex"), dict) else {})
                self.words.append(word); self.word_by_id[word.id] = word
        if self.words:
            for path in self._files("vocab"):
                if path in word_files: continue
                data = _read_json(path)
                if not isinstance(data, dict) or data.get("lang") not in VOCAB_LANGS: continue
                for wid, value in (data.get("words") or {}).items():
                    if wid in self.word_by_id and isinstance(value, str) and value.strip(): self.word_by_id[wid].tr[data["lang"]] = value.strip()
                for wid, value in (data.get("rom") or {}).items() if isinstance(data.get("rom"), dict) else ():
                    if wid in self.word_by_id and isinstance(value, str) and value.strip(): self.word_by_id[wid].rom[data["lang"]] = value.strip()
    # ------------------------------------------------------------------ access
    def get(self, item_id): return self.items.get(item_id)
    def plan_rank(self, item_id):
        """Position in plan.json (the editorial order), unplanned items last."""
        if not hasattr(self, "_rank"):
            ids = list((self.plan.get("articles") or {}).keys()) + list((self.plan.get("municipalities") or {}).keys()) + list((self.plan.get("days") or {}).keys())
            self._rank = {i: n for n, i in enumerate(ids)}
        return self._rank.get(item_id, 10 ** 5 + self.order.index(item_id) if item_id in self.items else 10 ** 6)
    def all(self, kind=None): return [self.items[i] for i in self.order if kind is None or self.items[i].kind == kind]
    def articles(self, category=None, level=None):
        out = []
        for item in self.all():
            cats = {item.category} | set(item.get("also") or [])
            if category and category not in cats: continue
            if level and level not in item.levels(): continue
            out.append(item)
        return out
    def municipalities(self): return sorted(self.all("municipality"), key=lambda m: fold(m.title("pt")))
    def places(self, municipality=None, kind=None):
        return [p for p in self.all("place") if (not municipality or p.get("municipality") == municipality) and (not kind or p.get("type") == kind)]
    def days(self): return self.all("day")
    def category_counts(self):
        counts = {c.key: 0 for c in CATEGORIES}
        for item in self.all():
            counts[item.category] = counts.get(item.category, 0) + 1
        return counts
    def stats(self):
        return {"articles": len(self.all("article")), "municipalities": len(self.all("municipality")), "places": len(self.all("place")),
                "days": len(self.all("day")), "words": len(self.words), "questions": sum(len(i.quiz()) for i in self.all()),
                "sources": len(self.sources())}
    def related(self, item):
        out = [self.items[r] for r in item.related() if r in self.items and r != item.id]
        if item.kind == "municipality": out += [p for p in self.places(item.id)][:12]
        if item.kind == "place" and item.get("municipality") in self.items: out.insert(0, self.items[item.get("municipality")])
        seen = set(); unique = []
        for o in out:
            if o.id not in seen: seen.add(o.id); unique.append(o)
        return unique
    # --------------------------------------------------------------- sources
    def sources(self):
        """Every source used, once, with the items that use it (Fontes page)."""
        by_url = {}
        for item in self.all():
            for s in item.sources():
                entry = by_url.setdefault(s["url"], {"url": s["url"], "title": s.get("title", s["url"]), "publisher": s.get("publisher", ""),
                                                      "licence": s.get("licence", ""), "accessed": s.get("accessed", ""), "items": []})
                entry["items"].append(item.id)
        for ind in self.indicators:
            if str(ind.get("url", "")).startswith("https://"):
                entry = by_url.setdefault(ind["url"], {"url": ind["url"], "title": text(ind.get("name"), "pt") or ind.get("id", ""), "publisher": ind.get("source", "World Bank"),
                                                        "licence": ind.get("licence", "CC BY 4.0"), "accessed": ind.get("accessed", ""), "items": []})
                entry["items"].append("indicators")
        return sorted(by_url.values(), key=lambda s: (fold(s["publisher"]), fold(s["title"])))
    # ---------------------------------------------------------------- search
    def _build_index(self):
        docs = {}; df = {}
        for item in self.all():
            terms = {}
            def add(value, weight):
                for t in tokens(value): terms[t] = terms.get(t, 0) + weight
            for lang in LANGS:
                add(text(item.data.get("title") or item.data.get("name"), lang), 6)
                add(text(item.data.get("summary"), lang), 2)
                for s in item.data.get("sections") or []:
                    if isinstance(s, dict): add(text(s.get("heading"), lang), 2); add(text(s.get("text"), lang), 1)
                if item.kind == "place": add(text(item.data.get("text"), lang), 1)
            for t in item.tags(): add(t, 3)
            if item.kind == "municipality":
                for p in item.get("posts") or []: add(p, 3)
            docs[item.id] = terms
            for t in terms: df[t] = df.get(t, 0) + 1
        lengths = {i: sum(t.values()) for i, t in docs.items()}
        avg = (sum(lengths.values()) / len(lengths)) if lengths else 1
        self._index = (docs, df, lengths, avg)
    def search(self, query, lang="tet", limit=40, kinds=None):
        """BM25 over all four languages; the last word also matches as a prefix (search as you type)."""
        if self._index is None: self._build_index()
        docs, df, lengths, avg = self._index
        q = tokens(query)
        if not q: return []
        n = max(1, len(docs)); scores = {}
        vocab = df.keys()
        for pos, term in enumerate(q):
            variants = [term]
            if pos == len(q) - 1 and len(term) >= 2: variants = [v for v in vocab if v.startswith(term)][:40] or [term]
            for v in variants:
                idf = math.log(1 + (n - df.get(v, 0) + 0.5) / (df.get(v, 0) + 0.5))
                for doc_id, terms in docs.items():
                    tf = terms.get(v)
                    if not tf: continue
                    k = 1.2 * (0.25 + 0.75 * lengths[doc_id] / avg)
                    scores[doc_id] = scores.get(doc_id, 0) + idf * tf * 2.2 / (tf + k) * (1.0 if v == term else 0.7)
        # Titles matter most: a title that contains the whole query comes first.
        phrase = fold(query).strip()
        if phrase:
            for doc_id in list(scores):
                data = self.items[doc_id].data; name = data.get("title") or data.get("name")
                # The title in the reader's language counts most; the other languages
                # add a little. A query that covers more of the title ranks higher
                # ("Xanana" → "Xanana Gusmão" before "Xanana Gusmão Reading Room").
                own = fold(text(name, lang))
                others = [fold(text(name, l)) for l in LANGS if l != lang]
                if own.startswith(phrase): scores[doc_id] += 8
                elif phrase in own: scores[doc_id] += 5
                if any(t.startswith(phrase) for t in others): scores[doc_id] += 2
                elif any(phrase in t for t in others): scores[doc_id] += 1
                close = max((len(phrase) / len(t) for t in [own, *others] if t and phrase in t), default=0)
                scores[doc_id] += 4 * close
        hits = sorted(scores.items(), key=lambda kv: -kv[1])
        out = []
        for doc_id, score in hits:
            item = self.items[doc_id]
            if kinds and item.kind not in kinds: continue
            out.append((item, score))
            if len(out) >= limit: break
        return out
    def search_words(self, query, lang="tet", limit=60):
        q = fold(query).strip()
        if not q: return []
        exact, starts, inside = [], [], []
        for w in self.words:
            values = [fold(w.tet)] + [fold(w.tr.get(k, "")) for k in ("pt", "id", "en", lang)]
            if q in values: exact.append(w)
            elif any(v.startswith(q) for v in values if v): starts.append(w)
            elif any(q in v for v in values if v): inside.append(w)
        return (exact + starts + inside)[:limit]
    # -------------------------------------------------------------- calendar
    def day_date(self, day, year):
        rule = str(day.get("date", ""))
        try:
            if re.match(r"^\d{2}-\d{2}$", rule): return date(year, int(rule[:2]), int(rule[3:]))
            m = re.match(r"^easter([+-]\d+)$", rule)
            if m: return easter(year) + timedelta(days=int(m.group(1)))
            if rule.startswith("islamic:"):
                value = (self.islamic.get(rule.split(":", 1)[1]) or {}).get(str(year))
                if value: return date(year, int(value[:2]), int(value[3:5]))
        except ValueError: return None
        return None
    def days_in_year(self, year):
        out = []
        for d in self.days():
            when = self.day_date(d, year)
            if when: out.append((when, d))
        return sorted(out, key=lambda x: x[0])
    def upcoming(self, today, count=5, holidays_only=False):
        out = []
        for year in (today.year, today.year + 1):
            for when, d in self.days_in_year(year):
                if when >= today and (not holidays_only or d.get("type") == "holiday"): out.append((when, d))
        return out[:count]
    # -------------------------------------------------------------- timeline
    def timeline(self, lang="tet"):
        events = []
        for item in self.all():
            for t in item.get("timeline") or []:
                if not isinstance(t, dict): continue
                key = parse_when(t.get("date"))
                if key is None: continue
                events.append({"key": key, "date": t.get("date"), "title": text(t.get("title"), lang), "item": item.id, "category": item.category})
        unique = []; by_key = {}
        for e in sorted(events, key=lambda e: e["key"]):
            words = set(tokens(e["title"])) - STOPWORDS
            # The same event told by two articles: keep the first.
            if any(len(words & w) >= max(2, 0.6 * min(len(words), len(w))) for w in by_key.get(e["key"], [])): continue
            by_key.setdefault(e["key"], []).append(words); unique.append(e)
        return unique
    def today_in_history(self, today, lang="tet"):
        out = []
        for e in self.timeline(lang):
            d = str(e["date"])
            if re.match(r"^\d{4}-\d{2}-\d{2}$", d) and int(d[5:7]) == today.month and int(d[8:10]) == today.day: out.append(e)
        return out
    # ------------------------------------------------------------------ quiz
    def questions(self, category=None, low=1, high=15):
        out = []
        for item in self.all():
            if category and item.category != category and category not in (item.get("also") or []): continue
            for i, q in enumerate(item.quiz()):
                d = q.get("difficulty", 5)
                if isinstance(d, int) and low <= d <= high: out.append({"item": item.id, "index": i, "q": q, "difficulty": d, "category": item.category})
        return out
    # ------------------------------------------------------- learning paths
    def path(self, level):
        """Units for one school level: articles grouped by category, simple first."""
        order = {"eb1": ["symbols", "geography", "calendar", "culture", "nature", "tourism", "history"],
                 "eb2": ["symbols", "geography", "history", "culture", "nature", "calendar", "society", "tourism"],
                 "eb3": ["history", "colonial", "geography", "symbols", "politics", "culture", "society", "economy", "nature", "land", "calendar"],
                 "es": ["history", "colonial", "conflicts", "politics", "leaders", "economy", "society", "world", "land", "culture"],
                 "sup": ["history", "colonial", "conflicts", "politics", "leaders", "world", "economy", "society", "land", "nature", "culture", "tourism"]}[level]
        units = []; seen = set()
        for cat in order:
            items = [a for a in self.articles(cat, level) if a.kind == "article" and a.category == cat]
            items += [a for a in self.articles(cat, level) if a.kind == "article" and a.category != cat and a.id not in seen and a not in items]
            items = sorted(items, key=lambda a, c=cat: self.reading_key(a, c))
            seen.update(a.id for a in items)
            if items: units.append({"category": cat, "items": items})
        return units
    def reading_key(self, item, unit=None):
        """Chronological for history topics (period start), editorial order otherwise."""
        if (unit or item.category) in ("history", "colonial", "conflicts", "leaders"):
            p = item.get("period") if isinstance(item.get("period"), dict) else {}
            if isinstance(p.get("from"), (int, float)): return (0, p["from"], self.plan_rank(item.id))
        return (1, 0, self.plan_rank(item.id))

def easter(year):
    """Western (Gregorian) Easter Sunday — anonymous Gregorian algorithm."""
    a = year % 19; b, c = divmod(year, 100); d, e = divmod(b, 4); f = (b + 8) // 25; g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30; i, k = divmod(c, 4); l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451; month, day = divmod(h + l - 7 * m + 114, 31)
    return date(year, month, day + 1)

def parse_when(value):
    """Sortable key for "1975-11-28", "1975-11", "1975", "-42000"."""
    m = re.match(r"^(-?\d{1,10})(?:-(\d{2}))?(?:-(\d{2}))?$", str(value or "").strip())
    if not m: return None
    return (int(m.group(1)), int(m.group(2) or 0), int(m.group(3) or 0))

def format_when(value, lang="tet"):
    key = parse_when(value)
    if key is None: return str(value or "")
    y, mo, d = key
    lang = lang if lang in LANGS else "tet"
    if y <= -1_000_000:
        # Geological time: millions of years ago.
        m = -y / 1_000_000; n = f"{m:.1f}".rstrip("0").rstrip(".")
        comma = n.replace(".", ",")
        return {"tet": f"tinan tokon {comma} liubá", "pt": f"há {comma} {'milhão' if m == 1 else 'milhões'} de anos",
                "en": f"{n} million years ago", "id": f"{comma} juta tahun lalu"}[lang]
    if y <= -10000:
        # Deep time is told as "years ago" (the difference to BCE does not matter there).
        years = f"{-y:,}"
        return {"tet": f"tinan {years.replace(',', ' ')} liubá", "pt": f"há {years.replace(',', ' ')} anos",
                "en": f"{years} years ago", "id": f"{years.replace(',', '.')} tahun lalu"}[lang]
    if y < 0:
        return {"tet": f"tinan {-y} molok Kristu", "pt": f"{-y} a.C.", "en": f"{-y} BC", "id": f"{-y} SM"}[lang]
    if d: return f"{d} {month_name(mo, lang)} {y}"
    if mo: return f"{month_name(mo, lang)} {y}"
    return str(y)

MONTHS = {
    "tet": ["Janeiru", "Fevereiru", "Marsu", "Abríl", "Maiu", "Juñu", "Jullu", "Agostu", "Setembru", "Outubru", "Novembru", "Dezembru"],
    "pt": ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"],
    "en": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
    "id": ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"],
}
WEEKDAYS = {
    "tet": ["Segunda", "Tersa", "Kuarta", "Kinta", "Sesta", "Sábadu", "Domingu"],
    "pt": ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"],
    "en": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    "id": ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"],
}

def month_name(month, lang="tet"):
    return MONTHS.get(lang, MONTHS["tet"])[max(1, min(12, month)) - 1]

def format_date(value, lang="tet"):
    return f"{value.day} {month_name(value.month, lang)} {value.year}"

_shared = None

def shared(overrides=None):
    global _shared
    if _shared is None: _shared = KnowledgeBase(overrides=overrides)
    return _shared

def reload(overrides=None):
    global _shared
    _shared = KnowledgeBase(overrides=overrides); return _shared
