"""One button: download every source for offline use.

When the learner presses "Download all sources for offline use" (Library →
Internet sources), Lafa saves, in the learner's Lafa folder
(~/.local/share/lafa/offline, or $XDG_DATA_HOME/lafa/offline):

* the front page and news feed of every learning and Timor-Leste source
  (into Lafa's local search memory; robots.txt respected, no whole sites);
* for every encyclopedia topic, the Wikipedia introduction in the learner's
  language (English when that language has no article, labelled), and
* one freely licensed picture per topic from Wikimedia Commons, with its
  licence, author and source page — only CC0, public-domain and Creative
  Commons licences are accepted; anything else is skipped;
* the current Wikipedia text of the Timor-Leste atlas topics.

Nothing is sent except the requests for these public pages. The download is
bounded (time, size per item, total size), can be stopped at any time and
keeps what it already saved. Lafa never downloads programs.
"""
import json
import os
import re
import tempfile
import time
from datetime import datetime
from html import unescape
from pathlib import Path
from urllib.parse import quote, urlencode

from .net import json_request, request, NetworkError

MAX_TOTAL = 250 * 1024 * 1024      # never use more than this
MAX_IMAGE = 900 * 1024             # one picture
MAX_TEXT = 4000                    # characters kept per extract
IMAGE_WIDTH = 640
FREE = re.compile(r"(^|\b)(cc0|cc[- ]by(-sa)?([- ]\d(\.\d)?)?|public domain|pd|no restrictions)(\b|$)", re.I)

def folder():
    base = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local/share")
    return base / "lafa" / "offline"

def _read(path, default):
    try:
        if path.stat().st_size > 20 * 1024 * 1024: return default
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, type(default)) else default
    except (OSError, ValueError, UnicodeError):
        return default

def _write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".offline-")
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle: json.dump(data, handle, ensure_ascii=False, indent=1)
        os.replace(tmp, path)
    except BaseException:
        try: os.unlink(tmp)
        except OSError: pass
        raise

def _safe(name):
    return re.sub(r"[^a-z0-9_.-]+", "_", name.casefold())[:120]

def plain(value):
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", str(value or "")))).strip()

# ------------------------------------------------------------------ reading
def manifest():
    return _read(folder() / "manifest.json", {})

def extract(article_id, lang):
    """The saved Wikipedia text for an article in this language, or None."""
    item = _read(folder() / "extracts.json", {}).get(lang, {}).get(article_id)
    if isinstance(item, dict) and isinstance(item.get("text"), str) and str(item.get("url", "")).startswith("https://"): return item
    return None

def image(article_id):
    """(path, metadata) of the saved picture for an article, or None."""
    meta = _read(folder() / "images.json", {}).get(article_id)
    if not isinstance(meta, dict): return None
    path = folder() / "images" / str(meta.get("file", ""))
    if path.parent != folder() / "images" or not path.is_file(): return None
    return path, meta

def size_mb():
    total = 0
    for path in folder().rglob("*"):
        try:
            if path.is_file(): total += path.stat().st_size
        except OSError: pass
    return round(total / 1024 / 1024, 1)

# --------------------------------------------------------------- Wikipedia
def _api(lang, params, timeout=15):
    return json_request(f"https://{lang}.wikipedia.org/w/api.php?" + urlencode({**params, "format": "json", "formatversion": "2"}), timeout=timeout)

def find_title(query, lang="en"):
    data = _api(lang, {"action": "query", "list": "search", "srsearch": query[:200], "srlimit": "1"})
    hits = data.get("query", {}).get("search", [])
    return hits[0]["title"] if hits else None

def lang_title(en_title, lang):
    if lang == "en": return en_title
    data = _api("en", {"action": "query", "titles": en_title, "prop": "langlinks", "lllang": lang})
    for page in data.get("query", {}).get("pages", []):
        for link in page.get("langlinks", []):
            if link.get("lang") == lang and link.get("title"): return link["title"]
    return None

def intro(title, lang):
    data = _api(lang, {"action": "query", "prop": "extracts", "explaintext": "1", "exintro": "1", "titles": title, "redirects": "1"})
    pages = data.get("query", {}).get("pages", [])
    text = "\n".join(p.get("extract", "") for p in pages if isinstance(p, dict)).strip()
    return text[:MAX_TEXT]

def page_image(en_title):
    data = _api("en", {"action": "query", "titles": en_title, "prop": "pageimages", "piprop": "name", "redirects": "1"})
    for page in data.get("query", {}).get("pages", []):
        if page.get("pageimage"): return page["pageimage"]
    return None

def commons_info(file_name):
    params = {"action": "query", "titles": "File:" + file_name, "prop": "imageinfo", "iiprop": "url|extmetadata|mime|size", "iiurlwidth": str(IMAGE_WIDTH),
              "format": "json", "formatversion": "2"}
    data = json_request("https://commons.wikimedia.org/w/api.php?" + urlencode(params), timeout=15)
    for page in data.get("query", {}).get("pages", []):
        info = (page.get("imageinfo") or [None])[0]
        if not info: continue
        meta = info.get("extmetadata", {})
        licence = plain(meta.get("LicenseShortName", {}).get("value", ""))
        if not licence or not FREE.search(licence) or "non-free" in licence.casefold() or "fair use" in licence.casefold(): return None
        if info.get("mime") not in ("image/jpeg", "image/png"): return None
        url = info.get("thumburl") or info.get("url")
        if not str(url).startswith("https://upload.wikimedia.org/"): return None
        return {"url": url, "licence": licence, "licence_url": plain(meta.get("LicenseUrl", {}).get("value", "")),
                "author": plain(meta.get("Artist", {}).get("value", ""))[:200] or "Wikimedia Commons",
                "source": info.get("descriptionurl", "https://commons.wikimedia.org/wiki/File:" + quote(file_name.replace(" ", "_"))),
                "description": plain(meta.get("ImageDescription", {}).get("value", ""))[:300]}
    return None

def image_bytes(url):
    raw = request(url, timeout=25, limit=MAX_IMAGE)
    if raw[:3] == b"\xff\xd8\xff": return raw, ".jpg"
    if raw[:8] == b"\x89PNG\r\n\x1a\n": return raw, ".png"
    raise NetworkError("Not a JPEG or PNG picture.")

# ------------------------------------------------------------------- the pack
class Pack:
    """Download everything; call run() in a worker thread.

    progress(done, total, name) is called after each step; stop() → True ends
    the download early (what was saved stays)."""
    def __init__(self, lang="en", progress=None, stop=None, clock=time.time):
        self.lang = lang if lang in ("en", "id", "pt", "tet") else "en"
        self.progress = progress or (lambda *a: None); self.stop = stop or (lambda: False); self.clock = clock
        self.root = folder(); self.used = 0
    def _room(self, extra=0):
        return self.used + extra < MAX_TOTAL
    def steps(self):
        from . import sources, encyclopedia
        steps = [("source", s) for s in sources.SOURCES]
        steps += [("article", a) for a in encyclopedia.all_articles() if a.id.startswith(("w.", "tl.")) or a.wiki]
        return steps
    def run(self):
        from . import memory, encyclopedia
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700); (self.root / "images").mkdir(exist_ok=True, mode=0o700)
        self.used = int(size_mb() * 1024 * 1024)
        extracts = _read(self.root / "extracts.json", {}); images = _read(self.root / "images.json", {})
        mine = extracts.setdefault(self.lang, {})
        steps = self.steps(); total = len(steps); counts = {"pages": 0, "extracts": 0, "images": 0, "failed": 0}; stopped = False
        shared = memory.shared()
        for done, (kind, item) in enumerate(steps, 1):
            if self.stop() or not self._room(): stopped = True; break
            try:
                if kind == "source":
                    name = item[1]
                    read, pages, failed = memory.refresh(shared, items=[item], max_age_hours=0, budget=1)
                    counts["pages"] += pages; counts["failed"] += failed
                else:
                    name = encyclopedia.text(item.title, self.lang)
                    self.article(item, mine, images, counts)
            except (NetworkError, ValueError, KeyError, OSError):
                counts["failed"] += 1
            self.progress(done, total, name)
            if done % 10 == 0:
                _write(self.root / "extracts.json", extracts); _write(self.root / "images.json", images)
        _write(self.root / "extracts.json", extracts); _write(self.root / "images.json", images)
        info = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "lang": self.lang, **counts, "stopped": stopped, "size_mb": size_mb()}
        _write(self.root / "manifest.json", info)
        return info
    def article(self, a, mine, images, counts):
        from . import encyclopedia
        en_title = a.wiki or find_title(encyclopedia.text(a.title, "en"))
        if not en_title: counts["failed"] += 1; return
        title = lang_title(en_title, self.lang); text_lang = self.lang
        if not title: title, text_lang = en_title, "en"
        text = intro(title, text_lang)
        if text and self._room(len(text) * 2):
            mine[a.id] = {"text": text, "lang": text_lang, "url": f"https://{text_lang}.wikipedia.org/wiki/" + quote(title.replace(" ", "_")),
                          "fetched": datetime.now().strftime("%Y-%m-%d"), "source": f"Wikipedia ({text_lang}) · CC BY-SA 4.0", "title": title}
            self.used += len(text) * 2; counts["extracts"] += 1
        if a.id in images and (self.root / "images" / images[a.id].get("file", "")).is_file(): return
        name = page_image(en_title)
        if not name: return
        info = commons_info(name)
        if not info: return
        raw, ext = image_bytes(info["url"])
        if not self._room(len(raw)): return
        file_name = _safe(a.id) + ext; path = self.root / "images" / file_name
        fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".img-")
        try:
            os.fchmod(fd, 0o600)
            with os.fdopen(fd, "wb") as handle: handle.write(raw)
            os.replace(tmp, path)
        except BaseException:
            try: os.unlink(tmp)
            except OSError: pass
            raise
        images[a.id] = {"file": file_name, "title": name, **{k: info[k] for k in ("licence", "licence_url", "author", "source", "description")}}
        self.used += len(raw); counts["images"] += 1
