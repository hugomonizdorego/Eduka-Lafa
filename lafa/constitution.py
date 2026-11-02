"""The Constitution of the Democratic Republic of Timor-Leste (2002), offline.

Data: lafa/assets/timor/constitution.json (built by tools/make-constitution.py
from the official Tetun and Portuguese texts). This module finds articles by
number ("15", "art. 15", "artigu 15.º") and by words, in Tetun and
Portuguese, without accents or apostrophes mattering.
"""
import json
import re
from functools import lru_cache

from . import kb

PATH = kb.ASSETS / "constitution.json"
REF = re.compile(r"^\s*(?:(?:art(?:igu|igo)?|a)\s*\.?\s*)?(\d{1,3})\s*(?:\.?\s*[º°o])?\s*$", re.I)

def parse_ref(query):
    """Article number for "15", "art 15", "art. 15", "artigu 15", "artigo 15.º"; else None."""
    m = REF.match(str(query or ""))
    if not m: return None
    n = int(m.group(1))
    return n if 1 <= n <= 170 else None

def paragraph_text(block):
    """One paragraph with its lettered items, as plain text."""
    head = (block["n"] + ". " if block.get("n") else "") + block.get("text", "")
    return "\n".join([head.strip()] + [f"{letter}) {text}" for letter, text in block.get("items", [])]).strip()

class Constitution:
    def __init__(self, data):
        self.data = data; self.headings = data.get("headings", []); self.articles = data.get("articles", [])
        self.by_number = {a["n"]: a for a in self.articles}
        self._index = {}
    # ---------------------------------------------------------------- text
    def title(self, lang): return kb.text(self.data.get("title"), lang)
    def preamble(self, lang): return self.data.get("preamble", {}).get(lang) or self.data.get("preamble", {}).get("pt", [])
    def article(self, n): return self.by_number.get(int(n)) if str(n).isdigit() else None
    def article_title(self, a, lang): return kb.text(a.get("title"), lang)
    def blocks(self, a, lang): return a.get("text", {}).get(lang) or a.get("text", {}).get("pt", [])
    def plain(self, a, lang):
        """The article as plain text with its reference (for copying and reading aloud)."""
        word = "Artigu" if lang == "tet" else "Artigo"
        body = "\n".join(paragraph_text(b) for b in self.blocks(a, lang))
        return kb.show(f"{word} {a['n']}.º — {self.article_title(a, lang)}\n{body}", lang)
    def heading_title(self, h, lang): return kb.text(h.get("title"), lang)
    def heading_label(self, h, lang):
        names = {"part": ("Parte", "Parte"), "title": ("Títulu", "Título"), "chapter": ("Kapítulu", "Capítulo"), "section": ("Seksaun", "Secção")}
        return f"{names[h['kind']][1 if lang == 'pt' else 0]} {h['num']}"
    def path(self, a): return [self.headings[i] for i in a.get("path", []) if 0 <= i < len(self.headings)]
    def group(self, a):
        """The articles that share the deepest heading of this article (one chapter or title)."""
        key = tuple(a.get("path", []))
        return [x for x in self.articles if tuple(x.get("path", [])) == key]
    def neighbours(self, n): return self.article(n - 1), self.article(n + 1)
    # -------------------------------------------------------------- search
    def index(self, lang):
        if lang not in self._index:
            rows = []
            for a in self.articles:
                title = kb.fold(self.article_title(a, lang))
                body = kb.fold(" ".join(paragraph_text(b).replace("\n", " ") for b in self.blocks(a, lang)))
                rows.append((a, title, body))
            self._index[lang] = rows
        return self._index[lang]
    def search(self, query, lang, limit=60):
        """[(article, score, snippet)] for words in titles and texts (all words must appear)."""
        n = parse_ref(query)
        if n is not None:
            a = self.article(n)
            return [(a, 1000, self.snippet(a, lang, []))] if a else []
        q = kb.fold(query).strip()
        if len(q) < 2: return []
        phrase = q.strip('"') if q.startswith('"') and q.endswith('"') and len(q) > 2 else None
        words = [w for w in re.split(r"[^\w-]+", phrase or q) if len(w) >= 2]
        if len(words) > 1: words = [w for w in words if w not in kb.STOPWORDS] or words     # "liberdade de imprensa": de is not needed
        if not words: return []
        out = []
        for a, title, body in self.index(lang):
            if phrase:
                if phrase not in title and phrase not in body: continue
                score = 20 * title.count(phrase) + body.count(phrase)
            else:
                if not all(w in title or w in body for w in words): continue
                score = sum(12 * title.count(w) + body.count(w) for w in words)
                if " ".join(words) in body or " ".join(words) in title: score += 8
            out.append((a, score, self.snippet(a, lang, [phrase] if phrase else words)))
        out.sort(key=lambda r: (-r[1], r[0]["n"]))
        return out[:limit]
    def snippet(self, a, lang, words, width=150):
        text = " ".join(paragraph_text(b).replace("\n", " ") for b in self.blocks(a, lang))
        folded = kb.fold(text)
        if len(folded) != len(text): folded = None       # rare: folding changed the length
        pos = min((folded.find(w) for w in words if folded and folded.find(w) >= 0), default=0) if words else 0
        start = max(0, pos - width // 3)
        cut = text[start:start + width].strip()
        return kb.show(("…" if start else "") + cut + ("…" if start + width < len(text) else ""), lang)
    def stats(self):
        return {"articles": len(self.articles), "headings": len(self.headings),
                "parts": sum(1 for h in self.headings if h["kind"] == "part")}

def highlight_pattern(words):
    """A regex that finds the search words in the original text, ignoring case and accents."""
    variants = {"a": "aáàâãä", "e": "eéèêë", "i": "iíìîï", "o": "oóòôõö", "u": "uúùûü", "c": "cç", "n": "nñ"}
    parts = []
    for w in words:
        w = kb.fold(w)
        if len(w) < 2 or (len(words) > 1 and w in kb.STOPWORDS): continue
        parts.append("".join(f"[{variants[ch]}]" if ch in variants else re.escape(ch) for ch in w))
    return re.compile(r"(?<!\w)(" + "|".join(parts) + ")", re.I) if parts else None     # words and word beginnings only

@lru_cache(maxsize=1)
def load():
    try: data = json.loads(PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError): data = {"articles": [], "headings": []}
    return Constitution(data)
