"""LAFA's core memory: a small search engine on this computer.

Like Google or Bing, but for LAFA's own sources. It indexes:

* LAFA's built-in knowledge: lessons for every age, the Timor-Leste atlas and
  history, Edukasaun OS guides and the descriptions of all learning and
  Timor-Leste media sources;
* public pages of the 130 learning and Timor-Leste sources, read when online
  (front page, a few linked pages and news feeds; robots.txt is respected,
  Facebook pages are only linked, never read);
* Wikipedia articles LAFA has opened, so they stay available offline.

Search ranks documents with BM25 (the classic search-engine formula), shows a
title, the address and a snippet for every result, and LAFA answers with
numbered citations [1] [2] pointing to those websites. With an AI provider the
best passages are given to the model as references. Everything is stored in
~/.cache/lafa/memory (private to the user, 0600).
"""
from collections import Counter
from dataclasses import dataclass, field
from html.parser import HTMLParser
import json
import math
import os
import re
import tempfile
import threading
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
import xml.etree.ElementTree as ET

from . import __version__

USER_AGENT = f"LAFA/{__version__} (Edukasaun OS learning assistant; +https://github.com/hugomonizdorego/Eduka-Lafa)"
MAX_TEXT = 6000            # characters kept per page
MAX_WEB_DOCS = 3000        # pages kept in memory
PAGE_LIMIT = 1_500_000     # bytes read per page
SKIP_HOSTS = ("facebook.com", "fb.com", "instagram.com", "x.com", "twitter.com", "tiktok.com", "youtube.com")

STOP = set("""a an and are as at be by for from has have in is it its of on or that the this to was were will with what who how why when where which
yang dan di ke dari untuk dengan ini itu adalah atau pada dalam juga akan apa siapa bagaimana mengapa kapan dimana tentang
o a os as de do da dos das em no na nos nas um uma uns umas e é para por com que como qual quem porque quando onde sobre
no ne'e nia iha ba ho husi mak ka atu sira ne'ebé saida se oinsá tanba bainhira iha-ne'ebé kona-ba la""".split())

# Words that mean the same thing in LAFA's four languages, so "buku" also
# finds "livro", "book" and "livru".
SYNONYMS = [
    "book books buku livro livros livru", "water air água bee", "sun matahari sol loro loromatan", "moon bulan lua fulan",
    "planet planets planeta planetas", "star stars bintang estrela estrelas fitun", "earth bumi terra rai",
    "atom atoms átomo átomos atomu átomu", "nuclear nuklir", "energy energi energia enerjia",
    "computer computers komputer computador komputadór", "internet web", "health kesehatan saúde",
    "medicine kedokteran obat medicina medisina aimoruk", "doctor dokter médico doutór", "disease penyakit doença moras",
    "history sejarah história istória", "school sekolah escola eskola", "teacher guru professor profesór",
    "coffee kopi café kafé", "rice beras padi nasi arroz hare etu", "fish ikan peixe", "sea laut mar tasi",
    "mountain gunung montanha foho", "island pulau ilha illa", "money uang dinheiro osan", "news berita notícias notísia",
    "radio rádio", "television televisi tv televisão televizaun", "newspaper koran jornal", "language bahasa língua lian",
    "mathematics math matematika matemática matemátika", "physics fisika física fízika",
    "chemistry kimia química kímika", "biology biologi biologia biolojia", "geography geografi geografia jeografia",
    "technology teknologi tecnologia teknolojia", "economy ekonomi economia ekonomia", "music musik música múzika",
    "president presiden presidente prezidente", "independence kemerdekaan independência independénsia",
    "solar surya", "climate iklim clima klima", "forest hutan floresta ai-laran", "food makanan comida ai-han hahán",
    "plant tanaman planta ai-horis", "animal hewan binatang animal animál", "communication komunikasi comunicação komunikasaun",
    "constitution konstitusi constituição konstituisaun", "election pemilu eleição eleisaun", "law hukum direito lei",
]

def fold(text):
    """Lowercase without accents: 'Ataúro' and 'ataúro' and 'atauro' match."""
    text = unicodedata.normalize("NFKD", str(text).casefold())
    return "".join(c for c in text if not unicodedata.combining(c))

TOKEN = re.compile(r"[a-z0-9]+(?:['’-][a-z0-9]+)*")
_SYN = {}
for _group in SYNONYMS:
    _words = [fold(w) for w in _group.split()]
    for _w in _words: _SYN.setdefault(_w, set()).update(_words)

def tokens(text):
    return [t for t in TOKEN.findall(fold(text)) if len(t) > 1 and t not in STOP]

def expand(words):
    out = []
    for w in words:
        for item in [w, *sorted(_SYN.get(w, set()) - {w})]:
            if item not in out: out.append(item)
    return out

@dataclass
class Doc:
    id: str
    title: str
    url: str
    site: str
    kind: str            # lesson, atlas, history, guide, source, web, news, wiki
    text: str
    lang: str = ""
    fetched: float = 0.0
    keywords: str = ""   # extra search words (not shown)

@dataclass
class Hit:
    doc: Doc
    score: float
    snippet: str
    terms: list = field(default_factory=list)
    coverage: float = 1.0      # share of the query words found
    titled: bool = False       # every query word is in the title

# ------------------------------------------------------------ built-in docs
def builtin_docs(lang):
    """LAFA's own knowledge in one language (rebuilt on demand, never stored)."""
    from . import curriculum, classroom, timor_atlas, timorleste, osguide, sources
    docs = []
    for lesson in curriculum.lessons():
        docs.append(Doc(f"age:{lesson.subject}:{lesson.level}", curriculum.text(lesson.title, lang), f"lafa://classroom/{lesson.subject}/{lesson.level}",
                        "LAFA · " + curriculum.subject_name(lesson.subject, lang) + " · " + curriculum.level_name(lesson.level, lang), "lesson",
                        "\n".join(curriculum.text(p, lang) for p in lesson.points) + "\n" + curriculum.text(lesson.task, lang), lang))
    for i, lesson in enumerate(classroom.lessons()):
        body = "\n".join(classroom.text(p, lang) for p in lesson.points) + "\n" + classroom.text(lesson.task, lang)
        docs.append(Doc(f"lesson:{i}", classroom.text(lesson.title, lang), f"lafa://classroom/{lesson.subject}", "LAFA · " + classroom.subject_name(lesson.subject, lang), "lesson", body, lang))
    for topic in timor_atlas.TOPICS:
        body = timor_atlas.text(topic.summary, lang)
        if topic.body and (lang != "tet" or "tet" in topic.body): body += "\n" + timor_atlas.text(topic.body, lang)
        facts = "\n".join(f"{timor_atlas.text(k, lang)}: {timor_atlas.text(v, lang)}" for k, v in topic.facts)
        docs.append(Doc(f"atlas:{topic.key}", timor_atlas.text(topic.title, lang), f"lafa://atlas/{topic.key}", "LAFA · Timor-Leste", "atlas", body + ("\n" + facts if facts else ""), lang))
    for i, event in enumerate(timorleste.HISTORY):
        docs.append(Doc(f"history:{i}", f"{event.when(lang)} · {timorleste.text(event.title, lang)}", "lafa://atlas/history", "LAFA · Timor-Leste", "history", timorleste.text(event.text, lang), lang))
    for guide in osguide.GUIDES:
        docs.append(Doc(f"guide:{guide.key}", guide.title.get(lang, guide.title["en"]), f"lafa://os/{guide.key}", "LAFA · Edukasaun OS", "guide",
                        "\n".join(guide.steps.get(lang, guide.steps["en"])), lang, keywords=" ".join(guide.keywords)))
    names = {key: sources.text(name, lang) for key, name, _ in sources.SOURCE_CATEGORIES}
    for category, name, url, description in sources.SOURCES:
        texts = list(dict.fromkeys([sources.text(description, lang), sources.text(description, "en")]))
        docs.append(Doc(f"source:{url}", name, url, names.get(category, category), "source", "\n".join(texts), lang, keywords=names.get(category, "")))
    return docs

# ------------------------------------------------------------ the index
class Index:
    """BM25 over a list of documents (title words count three times)."""
    K1, B = 1.4, 0.72
    def __init__(self, docs):
        self.docs = list(docs); self.tf = []; self.df = Counter(); self.lengths = []
        for doc in self.docs:
            words = tokens(doc.title) * 3 + tokens(doc.site) + tokens(doc.text) + tokens(doc.keywords)
            counts = Counter(words); self.tf.append(counts); self.lengths.append(len(words)); self.df.update(counts.keys())
        self.avg = (sum(self.lengths) / len(self.lengths)) if self.lengths else 1.0
    def idf(self, term):
        n = len(self.docs); df = self.df.get(term, 0)
        return math.log(1 + (n - df + 0.5) / (df + 0.5))
    def search(self, query, k=8, kinds=None):
        words = tokens(query)
        if not words: return []
        terms = expand(words)
        weight = {t: (1.0 if t in words else 0.6) for t in terms}
        scores = []
        for i, counts in enumerate(self.tf):
            doc = self.docs[i]
            if kinds and doc.kind not in kinds: continue
            score = 0.0; matched = set()
            for term in terms:
                f = counts.get(term)
                if not f: continue
                origin = term if term in words else next((w for w in words if term in _SYN.get(w, ())), term)
                matched.add(origin)
                score += weight[term] * self.idf(term) * f * (self.K1 + 1) / (f + self.K1 * (1 - self.B + self.B * self.lengths[i] / self.avg))
            if not score: continue
            coverage = len(matched) / len(words)
            score *= coverage ** 1.5      # prefer pages that contain every word
            title = set(tokens(doc.title)); titled = all(w in title or _SYN.get(w, set()) & title for w in words)
            if titled: score *= 1.6
            scores.append((score, i, coverage, titled))
        scores.sort(reverse=True)
        return [Hit(self.docs[i], s, snippet(self.docs[i].text, terms), terms, c, t) for s, i, c, t in scores[:k]]

SENTENCE = re.compile(r"(?<=[.!?…])\s+|\n+")

def snippet(text, terms, size=260):
    """The sentences that best match the query, like a search-result snippet."""
    parts = [p.strip(" •\t") for p in SENTENCE.split(text) if len(p.strip()) > 2]
    if not parts: return ""
    best, best_score = 0, -1
    for i, part in enumerate(parts):
        words = set(tokens(part)); score = sum(1 for t in terms if t in words)
        if score > best_score: best, best_score = i, score
    out = parts[best]
    for extra in parts[best + 1:best + 3]:
        if len(out) + len(extra) > size: break
        out += " " + extra
    return out if len(out) <= size else out[:size - 1].rsplit(" ", 1)[0] + "…"

# ------------------------------------------------------------ storage
def folder():
    root = os.environ.get("XDG_CACHE_HOME") or os.path.join(os.path.expanduser("~"), ".cache")
    return os.path.join(root, "lafa", "memory")

class Memory:
    """Built-in knowledge + pages read from the web, searchable offline."""
    def __init__(self, path=None):
        self.path = path or os.path.join(folder(), "web.json")
        self.lock = threading.Lock(); self.web = {}; self._indexes = {}
        self.load()
    def load(self):
        try:
            with open(self.path, encoding="utf-8") as handle: raw = json.load(handle)
        except (OSError, ValueError): raw = []
        web = {}
        for item in raw if isinstance(raw, list) else []:
            try: doc = Doc(**{k: item[k] for k in ("id", "title", "url", "site", "kind", "text", "lang", "fetched")})
            except (KeyError, TypeError): continue
            if isinstance(doc.url, str) and doc.url.startswith("https://") and isinstance(doc.text, str):
                web[doc.url] = doc
        with self.lock: self.web = web; self._indexes = {}
    def save(self):
        with self.lock: items = [doc.__dict__ for doc in self.web.values()]
        os.makedirs(os.path.dirname(self.path), mode=0o700, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=os.path.dirname(self.path), prefix=".web-")
        try:
            os.fchmod(fd, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as handle: json.dump(items, handle, ensure_ascii=False)
            os.replace(tmp, self.path)
        except BaseException:
            try: os.unlink(tmp)
            except OSError: pass
            raise
    def add(self, docs, save=True):
        """Remember web pages (newest kept when the memory is full)."""
        changed = False
        with self.lock:
            for doc in docs:
                if not doc.url.startswith("https://") or not doc.text.strip(): continue
                doc.text = doc.text[:MAX_TEXT]; doc.fetched = doc.fetched or time.time()
                self.web[doc.url] = doc; changed = True
            if len(self.web) > MAX_WEB_DOCS:
                for url, _ in sorted(self.web.items(), key=lambda kv: kv[1].fetched)[:len(self.web) - MAX_WEB_DOCS]: del self.web[url]
            if changed: self._indexes = {}
        if changed and save: self.save()
        return changed
    def index(self, lang):
        with self.lock:
            if lang not in self._indexes:
                self._indexes[lang] = Index(builtin_docs(lang) + list(self.web.values()))
            return self._indexes[lang]
    def search(self, query, lang="en", k=8, kinds=None):
        return self.index(lang).search(query, k, kinds)
    def stats(self):
        with self.lock: web = list(self.web.values())
        return {"pages": len(web), "sites": len({urllib.parse.urlsplit(d.url).hostname for d in web}),
                "news": sum(d.kind == "news" for d in web), "updated": max((d.fetched for d in web), default=0)}
    def page_age(self, url):
        doc = self.web.get(url)
        return time.time() - doc.fetched if doc else None

_shared = None
def shared():
    global _shared
    if _shared is None: _shared = Memory()
    return _shared

# ------------------------------------------------------------ answers
CITE = {"en": "Sources", "id": "Sumber", "pt": "Fontes", "tet": "Fonte sira"}
FOUND = {"en": "From LAFA's memory", "id": "Dari memori LAFA", "pt": "Da memória do LAFA", "tet": "Husi memória LAFA nian"}

def answer(query, lang="en", memory=None, k=4, strict=True):
    """An answer built from the best results, with numbered sources, or None.

    Returns (text, hits). Only results that contain every word of a short
    query (most words of a long one) count as facts; with strict=True a one-
    or two-word query must also name the result's title, so "livru" is not
    answered by a lesson that merely mentions books (Wikipedia does better).
    Directory entries of LAFA's sources are listed as sites to visit."""
    memory = memory or shared()
    words = tokens(query)
    hits = [h for h in memory.search(query, lang, k=12) if h.snippet]
    if not hits or not words: return None
    need = 1.0 if len(words) <= 3 else 0.75
    facts = [h for h in hits if h.doc.kind != "source" and h.coverage >= need and (h.titled or not strict or len(words) > 2)]
    if facts:
        top = facts[0].score; facts = [h for h in facts if h.score >= top * 0.35][:k]
    sites = [h for h in hits if h.doc.kind == "source" and h.coverage >= need][:3]
    if not facts and not sites: return None
    lines = []
    if facts:
        lines.append(f"🧠 {FOUND.get(lang, FOUND['en'])}: {query.strip()}")
        for n, hit in enumerate(facts, 1): lines.append(f"• {hit.snippet} [{n}]")
        lines.append("\n" + CITE.get(lang, CITE["en"]) + ":")
        for n, hit in enumerate(facts, 1): lines.append(f"[{n}] {hit.doc.title} — {hit.doc.site}" + (f"\n    {hit.doc.url}" if hit.doc.url.startswith("https://") else ""))
    if sites:
        from .i18n import tr
        lines.append(("\n" if lines else "") + tr(lang, "related_sites"))
        lines += [f"• {h.doc.title} — {h.doc.url}" for h in sites]
    return "\n".join(lines), facts + sites

def context(query, lang="en", memory=None, k=5, limit=3500):
    """The best passages as numbered references for an AI model (RAG)."""
    memory = memory or shared(); out = []; used = 0
    for n, hit in enumerate([h for h in memory.search(query, lang, k=k * 2) if h.doc.kind != "source"][:k], 1):
        passage = snippet(hit.doc.text, hit.terms, 700)
        if used + len(passage) > limit: break
        out.append((n, hit, passage)); used += len(passage)
    return out

# ------------------------------------------------------------ reading the web
class PageParser(HTMLParser):
    SKIP = {"script", "style", "noscript", "svg", "nav", "footer", "header", "form", "button", "iframe", "aside"}
    BLOCK = {"p", "h1", "h2", "h3", "h4", "li", "article", "section", "div", "br", "td", "blockquote", "figcaption"}
    def __init__(self, base):
        super().__init__(convert_charrefs=True); self.base = base; self.skip = 0
        self.title = ""; self.description = ""; self.parts = []; self.links = []; self.feeds = []; self._title = False; self.lang = ""
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html": self.lang = (a.get("lang") or "")[:5]
        if tag in self.SKIP: self.skip += 1
        if tag == "title": self._title = True
        if tag == "meta" and (a.get("name") or a.get("property") or "").lower() in {"description", "og:description"} and not self.description:
            self.description = (a.get("content") or "").strip()
        if tag == "link" and "alternate" in (a.get("rel") or "").lower() and "rss" in (a.get("type") or "") + (a.get("href") or ""):
            if a.get("href"): self.feeds.append(urllib.parse.urljoin(self.base, a["href"]))
        if tag == "a" and a.get("href"): self.links.append(urllib.parse.urljoin(self.base, a["href"]).split("#")[0])
        if tag in self.BLOCK: self.parts.append("\n")
    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip: self.skip -= 1
        if tag == "title": self._title = False
        if tag in self.BLOCK: self.parts.append("\n")
    def handle_data(self, data):
        if self._title: self.title += data
        elif not self.skip: self.parts.append(data)
    def text(self):
        lines = [re.sub(r"\s+", " ", line).strip() for line in "".join(self.parts).split("\n")]
        # Menu items and buttons are short; keep real sentences.
        lines = [line for line in lines if len(line) >= 40 or (len(line) >= 20 and line.endswith((".", "!", "?", ":")))]
        return "\n".join(dict.fromkeys(lines))

def parse_page(raw, url):
    html = raw.decode("utf-8", "replace") if isinstance(raw, bytes) else raw
    parser = PageParser(url)
    try: parser.feed(html); parser.close()
    except Exception: pass
    return parser

def parse_feed(raw):
    """(title, link, summary, date) from RSS or Atom."""
    try: root = ET.fromstring(raw)
    except ET.ParseError: return []
    items = []
    for node in root.iter():
        tag = node.tag.rsplit("}", 1)[-1]
        if tag not in {"item", "entry"}: continue
        get = lambda name: next((c for c in node if c.tag.rsplit("}", 1)[-1] == name), None)
        title = (get("title").text or "").strip() if get("title") is not None else ""
        link = get("link"); link = (link.text or link.get("href") or "").strip() if link is not None else ""
        summary = get("description") if get("description") is not None else get("summary")
        summary = re.sub(r"<[^>]+>", " ", summary.text or "") if summary is not None else ""
        when = get("pubDate") if get("pubDate") is not None else get("updated")
        items.append((title, link, re.sub(r"\s+", " ", summary).strip(), (when.text or "").strip() if when is not None else ""))
    return items

def site_of(host):
    parts = (host or "").lower().split(".")
    return ".".join(parts[-2:]) if len(parts) >= 2 else host

class SameSiteRedirect(urllib.request.HTTPRedirectHandler):
    max_redirections = 3
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        old, new = urllib.parse.urlsplit(req.full_url), urllib.parse.urlsplit(newurl)
        if new.scheme != "https" or site_of(new.hostname) != site_of(old.hostname): return None
        return super().redirect_request(req, fp, code, msg, headers, newurl)

_opener = urllib.request.build_opener(SameSiteRedirect())

def fetch(url, timeout=12):
    """(final url, bytes, content type) for a public HTTPS page."""
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or not parts.hostname or parts.username or parts.password: raise ValueError("HTTPS only")
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml,application/rss+xml,application/xml;q=0.9"})
    with _opener.open(request, timeout=timeout) as response:
        final = response.geturl()
        if not final.startswith("https://"): raise ValueError("left HTTPS")
        return final, response.read(PAGE_LIMIT), response.headers.get("Content-Type", "")

class Robots:
    def __init__(self, fetch=fetch): self.fetch = fetch; self.cache = {}
    def allowed(self, url):
        parts = urllib.parse.urlsplit(url); key = parts.hostname
        if key not in self.cache:
            parser = urllib.robotparser.RobotFileParser()
            try:
                _, raw, _ = self.fetch(f"https://{parts.hostname}/robots.txt", 8)
                parser.parse(raw.decode("utf-8", "replace").splitlines())
            except urllib.error.HTTPError as error:
                parser.parse([] if error.code >= 400 and error.code != 401 and error.code != 403 else ["User-agent: *", "Disallow: /"])
            except Exception:
                parser.parse([])
            self.cache[key] = parser
        return self.cache[key].can_fetch("LAFA", url)

def skip_host(url):
    host = (urllib.parse.urlsplit(url).hostname or "").lower()
    return any(host == h or host.endswith("." + h) for h in SKIP_HOSTS)

def read_site(name, url, category_name, fetch=fetch, robots=None, per_site=4):
    """Pages (Doc) from one source: its front page, a few linked pages, its feed."""
    robots = robots or Robots(fetch)
    if skip_host(url) or not robots.allowed(url): return []
    final, raw, kind = fetch(url)
    docs = []
    if "xml" in kind and b"<rss" in raw[:500] or b"<feed" in raw[:500]:
        return feed_docs(name, raw, final)
    page = parse_page(raw, final)
    body = "\n".join(x for x in (page.description, page.text()) if x)
    if body: docs.append(Doc("web:" + final, (page.title or name).strip()[:160], final, name, "web", body, page.lang))
    host = urllib.parse.urlsplit(final).hostname
    links = [l for l in dict.fromkeys(page.links) if l.startswith("https://") and urllib.parse.urlsplit(l).hostname == host
             and l.rstrip("/") != final.rstrip("/") and not re.search(r"\.(jpg|jpeg|png|gif|pdf|zip|mp3|mp4|webp|svg)$|/(login|signin|signup|register|cart|account|wp-admin)", l, re.I)]
    # Prefer article-like addresses (several path parts, or dated).
    links.sort(key=lambda l: (-(urllib.parse.urlsplit(l).path.count("/")) - (3 if re.search(r"/20\d\d/", l) else 0), len(l)))
    for link in links[:per_site - 1]:
        try:
            if not robots.allowed(link): continue
            got, raw, kind = fetch(link)
            if "html" not in kind: continue
            sub = parse_page(raw, got); text = sub.text()
            if len(text) >= 120: docs.append(Doc("web:" + got, (sub.title or name).strip()[:160], got, name, "web", "\n".join(x for x in (sub.description, text) if x), sub.lang))
        except Exception: continue
    for feed in page.feeds[:1]:
        try:
            if robots.allowed(feed):
                _, raw, _ = fetch(feed); docs += feed_docs(name, raw, feed)
        except Exception: pass
    return docs

def feed_docs(name, raw, feed_url, limit=12):
    docs = []
    for title, link, summary, when in parse_feed(raw)[:limit]:
        if link.startswith("https://") and title:
            docs.append(Doc("news:" + link, title[:200], link, name, "news", (summary or title) + (f"\n{when}" if when else "")))
    return docs

def refresh(memory=None, items=None, max_age_hours=24, budget=60, fetch=fetch, stop=None):
    """Read sources whose pages are older than max_age_hours (news: 1 hour).

    Returns (sites read, pages remembered, failed). Runs in a worker thread."""
    from . import sources
    memory = memory or shared(); items = items if items is not None else sources.SOURCES
    names = {key: sources.text(label, "en") for key, label, _ in sources.SOURCE_CATEGORIES}
    robots = Robots(fetch); read = pages = failed = 0
    timor_first = sorted(items, key=lambda s: (not s[0].startswith("tl_"), s[1]))
    for category, name, url, _ in timor_first:
        if stop and stop(): break
        if read >= budget: break
        if skip_host(url): continue
        age = memory.page_age(url) if hasattr(memory, "page_age") else None
        limit = 3600 if category in ("tl_news", "tl_papers") else max_age_hours * 3600
        if age is not None and age < limit: continue
        try:
            docs = read_site(name, url, names.get(category, category), fetch, robots)
            # Remember the source address too, so its age is known next time.
            if docs and docs[0].url != url: docs.append(Doc("web:" + url, docs[0].title, url, name, "web", docs[0].text, docs[0].lang))
            memory.add(docs, save=False); read += 1; pages += len(docs)
        except Exception:
            failed += 1
    if read: memory.save()
    return read, pages, failed

def remember_article(title, url, text, lang="", memory=None):
    """Keep a Wikipedia article LAFA showed, for offline use later."""
    memory = memory or shared()
    if url.startswith("https://") and text:
        memory.add([Doc("wiki:" + url, title, url, "Wikipedia", "wiki", text, lang)])
