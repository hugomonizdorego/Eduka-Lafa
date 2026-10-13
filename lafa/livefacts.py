"""Keep LAFA's Timor-Leste atlas up to date from open sources.

When the computer is online LAFA downloads the current Wikipedia introduction
of each atlas topic, in the reader's language when that article exists
(Tetun, Portuguese, Indonesian) and otherwise in English. Results are cached
with their date in ~/.cache/lafa/live-facts.json (mode 0600) so they are still
available offline. Only plain text is kept; nothing is ever executed.
"""
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import re
import tempfile
from urllib.parse import quote, urlencode

from .net import json_request, NetworkError

LANGS = {"en", "id", "pt", "tet"}
MAX_TEXT = 1800

def cache_path():
    base = Path(os.environ.get("XDG_CACHE_HOME", str(Path.home() / ".cache")))
    return base / "lafa" / "live-facts.json"

def load():
    path = cache_path()
    try:
        if path.is_file() and not path.is_symlink() and path.stat().st_size < 2_000_000:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict): return {k: v for k, v in data.items() if valid(v)}
    except (OSError, ValueError, UnicodeError):
        pass
    return {}

def valid(entry):
    return (isinstance(entry, dict) and all(isinstance(entry.get(k), str) for k in ("lang", "title", "text", "url", "fetched"))
            and entry["lang"] in LANGS and entry["url"].startswith("https://") and ".wikipedia.org/wiki/" in entry["url"])

def save(data):
    path = cache_path(); path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".live-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream: json.dump(data, stream, ensure_ascii=False, indent=1)
        os.chmod(tmp, 0o600); os.replace(tmp, path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

def clean(text):
    text = re.sub(r"\s+\n", "\n", str(text)).strip()
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
    if len(text) > MAX_TEXT: text = text[:MAX_TEXT].rsplit(" ", 1)[0] + "…"
    return text

def _query(lang, params):
    return json_request(f"https://{lang}.wikipedia.org/w/api.php?" + urlencode({"format": "json", "formatversion": "2", **params}), timeout=15)

def fetch(title, lang="en", request=_query):
    """Introduction of an English Wikipedia article, in `lang` when the
    article exists there (via its language link), else in English."""
    lang = lang if lang in LANGS else "en"
    data = request("en", {"action": "query", "prop": "extracts|langlinks", "exintro": "1", "explaintext": "1",
                          "redirects": "1", "titles": title, "lllang": lang if lang != "en" else "pt", "lllimit": "1"})
    pages = (data.get("query") or {}).get("pages") or []
    if not pages or pages[0].get("missing"): raise NetworkError("Article not found.")
    page = pages[0]; result = ("en", page.get("title", title), page.get("extract", ""))
    links = page.get("langlinks") or []
    if lang != "en" and links and links[0].get("lang") == lang and links[0].get("title"):
        local = request(lang, {"action": "query", "prop": "extracts", "exintro": "1", "explaintext": "1", "redirects": "1", "titles": links[0]["title"]})
        lpages = (local.get("query") or {}).get("pages") or []
        if lpages and lpages[0].get("extract"):
            result = (lang, lpages[0].get("title", links[0]["title"]), lpages[0]["extract"])
    code, name, extract = result
    if not extract.strip(): raise NetworkError("Article has no introduction.")
    return {"lang": code, "title": str(name)[:200], "text": clean(extract),
            "url": f"https://{code}.wikipedia.org/wiki/" + quote(str(name).replace(" ", "_")),
            "fetched": datetime.now().strftime("%Y-%m-%d %H:%M")}

def key(topic_key, lang):
    return f"{topic_key}:{lang}"

def stale(entry, hours=24, now=None):
    try: when = datetime.strptime(entry["fetched"], "%Y-%m-%d %H:%M")
    except (KeyError, ValueError, TypeError): return True
    return (now or datetime.now()) - when >= timedelta(hours=hours)

def refresh(topics, lang="en", hours=24, request=_query, limit=60):
    """Download fresh introductions for stale topics; returns (updated, failed).
    Runs in a worker thread; keeps going when single articles fail."""
    data = load(); updated = failed = 0
    for topic in [t for t in topics if t.wiki][:limit]:
        k = key(topic.key, lang)
        if k in data and not stale(data[k], hours): continue
        try: data[k] = fetch(topic.wiki, lang, request); updated += 1
        except NetworkError: failed += 1
    if updated: save(data)
    return updated, failed

def get(topic_key, lang="en"):
    return load().get(key(topic_key, lang))
