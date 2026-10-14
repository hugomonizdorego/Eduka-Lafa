"""One search box for lessons, knowledge and files — local first.

LAFA does not generate answers. It looks things up:

* "Apa itu fotosintesis?"       → LAFA's lessons and atlas (Materi lokal),
                                  with the lesson it comes from;
* "Cari file tugas matematika"  → file names in the folders chosen in
                                  Settings (File lokal);
* "Bagaimana mengganti wallpaper?" → the Edukasaun OS guide;
* "12 * (3 + 4)"               → the safe calculator;
* pages saved earlier for offline use (Materi tersimpan) and the catalogue
  of learning websites (Sumber internet, only listed — never fetched here).

When nothing matches well, LAFA says so and offers choices instead of a
"sure" answer. Searching the internet is a separate button; nothing typed
here is sent anywhere automatically.
"""
from dataclasses import dataclass, field
import re

from . import memory as memory_module, osguide
from .calculator import calculate

LABELS = ("lesson", "file", "saved", "internet", "guide")
FILE_INTENT = re.compile(r"^(?:cari(?:kan)?|search(?: for)?|find|buka|open|procura(?:r)?|pesquisa(?:r)?|buka hela)\s+(?:the\s+|my\s+|ha'u-nia\s+)?"
                         r"(?:file|files|berkas|dokumen|document|documents|ficheiru|ficheiro|ficheiros|arquivo|arquivos|folder)\s+(.+)$", re.I)
CALC = re.compile(r"^(?:/calc\s+|/hitung\s+|/kalkula\s+)?([\d\s.,+\-*/×÷^()%]+)$")
QUESTION_WORDS = re.compile(r"^(?:apa itu|apakah|what is|what are|o que é|o que sao|saida mak|saida maka|siapa|who is|quem é|se mak)\s+", re.I)

@dataclass
class Item:
    label: str          # lesson, file, saved, internet, guide
    title: str
    detail: str
    target: str         # lafa://…, a file path, or an https:// address
    source: str = ""
    score: float = 0.0

@dataclass
class Outcome:
    query: str
    mode: str                       # answer, choices, none, calc, guide, files
    items: list = field(default_factory=list)
    calc: str = ""
    guide: object = None
    limited: bool = False           # file search stopped early

def topic_words(query):
    """The topic of a question ("Apa itu fotosintesis?" → "fotosintesis")."""
    text = query.strip().strip("?!. ")
    return QUESTION_WORDS.sub("", text).strip() or text

def understand(query):
    """(kind, value): files, calc, guide or topic."""
    text = query.strip()
    m = FILE_INTENT.match(text.rstrip("?!. "))
    if m: return "files", m.group(1).strip()
    m = CALC.match(text)
    if m and re.search(r"\d\s*[+\-*/×÷^%]\s*[\d(]", m.group(1)): return "calc", m.group(1).replace("×", "*").replace("÷", "/")
    guide = osguide.find(text)
    if guide: return "guide", guide
    return "topic", topic_words(text)

LABEL_OF = {"lesson": "lesson", "atlas": "lesson", "history": "lesson", "guide": "guide", "web": "saved", "news": "saved", "wiki": "saved", "source": "internet"}

def memory_items(query, lang, store, k=12):
    """Items from LAFA's memory; the first ones are the most relevant."""
    hits = [h for h in store.search(query, lang, k=k) if h.snippet]
    return [Item(LABEL_OF.get(h.doc.kind, "lesson"), h.doc.title, h.snippet, h.doc.url, h.doc.site, h.score) for h in hits], hits

def confident(hits, query):
    """True when the best local material really is about the query."""
    words = memory_module.tokens(query)
    best = next((h for h in hits if h.doc.kind != "source"), None)
    if not best or not words: return False
    if best.coverage < 1.0: return False
    return best.titled or (len(words) >= 2 and best.score >= 6.0)

def file_items(query, roots, file_search=None, limit=20):
    from .tools import FileSearch
    finder = (file_search or FileSearch)(roots)
    results = finder.search(query, "all", limit=limit, seconds=4)
    return [Item("file", hit.name, hit.path.rsplit("/", 1)[0], hit.path, "", 0.0) for hit in results.hits], results.limited

def search(query, lang="en", roots=(), store=None, with_files=True, file_search=None):
    """Search everything local. Never uses the network."""
    query = str(query).strip()[:300]
    if not query: return Outcome(query, "none")
    kind, value = understand(query)
    if kind == "calc":
        try: return Outcome(query, "calc", calc=calculate(value))
        except (ValueError, ZeroDivisionError, OverflowError, SyntaxError, TypeError): kind, value = "topic", query
    if kind == "files":
        items, limited = file_items(value, roots, file_search) if roots else ([], False)
        return Outcome(value, "files", items, limited=limited)
    if kind == "guide":
        store = store or memory_module.shared()
        items, _ = memory_items(topic_words(query), lang, store, k=6)
        return Outcome(query, "guide", [i for i in items if i.label == "lesson"][:4], guide=value)
    store = store or memory_module.shared()
    items, hits = memory_items(value, lang, store)
    limited = False
    if with_files and roots and len(value) >= 3:
        found, limited = file_items(value, roots, file_search, limit=8)
        items += found
    local = [i for i in items if i.label != "internet"]
    if not local and not items: return Outcome(value, "none")
    if confident(hits, value):
        return Outcome(value, "answer", items, limited=limited)
    return Outcome(value, "choices" if items else "none", items, limited=limited)

def summary(outcome, lang, tr):
    """Short text for the Virtual Assistant's bubble."""
    if outcome.mode == "calc": return f"🧮 {outcome.query} = {outcome.calc}"
    if outcome.mode == "guide": return outcome.guide.text(lang)
    if outcome.mode == "files":
        if not outcome.items: return tr(lang, "files_none").replace("{q}", outcome.query)
        return tr(lang, "files_found").replace("{n}", str(len(outcome.items))) + "\n" + "\n".join("📄 " + i.title for i in outcome.items[:5])
    if outcome.mode == "answer":
        best = next(i for i in outcome.items if i.label != "internet")
        return f"📗 {best.title}\n{best.detail}\n\n{tr(lang, 'from_material')}: {best.source}"
    if outcome.mode == "choices":
        return tr(lang, "search_choices").replace("{q}", outcome.query) + "\n" + "\n".join("• " + i.title for i in outcome.items[:5])
    return tr(lang, "search_none").replace("{q}", outcome.query)
