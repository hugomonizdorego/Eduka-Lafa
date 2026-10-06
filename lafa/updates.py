"""Keep LAFA's learning sources up to date without a LAFA server.

The source catalog (learning links, teacher resources, Timor-Leste cards, tips
and desktop tool names) is plain JSON published in LAFA's open-source
repository: lafa/assets/catalog.json. Installed copies download it over HTTPS
every few hours, validate every field (data only, never code), cache it in
~/.cache/lafa and merge it with what was shipped. Developers improve sources by
editing that file and increasing "revision"; nobody has to reinstall LAFA.
New LAFA releases are announced from the GitHub releases of the repository.
"""
import json
import os
import re
import tempfile
import time
from pathlib import Path
from urllib.parse import urlsplit
from . import __version__
from .net import request, json_request, NetworkError

REPOSITORY = "hugomonizdorego/Eduka-Lafa"
CATALOG_URL = f"https://raw.githubusercontent.com/{REPOSITORY}/main/lafa/assets/catalog.json"
RELEASES_URL = f"https://api.github.com/repos/{REPOSITORY}/releases/latest"
SHIPPED = Path(__file__).parent / "assets" / "catalog.json"
LANGS = ("en", "id", "pt", "tet")

def cache_path():
    return Path(os.environ.get("XDG_CACHE_HOME", str(Path.home() / ".cache"))) / "lafa" / "catalog.json"

class CatalogError(ValueError):
    pass

def _url(value):
    if not isinstance(value, str) or not 10 <= len(value) <= 400: raise CatalogError("bad URL")
    parts = urlsplit(value)
    if parts.scheme != "https" or not parts.hostname or parts.username or parts.password or any(ord(c) < 33 for c in value):
        raise CatalogError("Only plain HTTPS links are allowed.")
    return value

def _text(value, limit):
    if not isinstance(value, str) or not value.strip() or len(value) > limit or any(ord(c) < 32 and c not in "\n" for c in value):
        raise CatalogError("bad text")
    return value.strip()

def _translations(value, limit=400):
    if not isinstance(value, dict) or "en" not in value: raise CatalogError("translations need English")
    return {lang: _text(value[lang], limit) for lang in LANGS if lang in value}

def _links(value, limit=40):
    if not isinstance(value, list): raise CatalogError("links must be a list")
    return [(_text(item[0], 80), _url(item[1])) for item in value[:limit] if isinstance(item, list) and len(item) == 2]

def validate(data):
    """Strict schema check. Returns a clean catalog or raises CatalogError."""
    if not isinstance(data, dict): raise CatalogError("catalog must be an object")
    revision = data.get("revision")
    if not isinstance(revision, int) or isinstance(revision, bool) or not 0 < revision < 10**12: raise CatalogError("bad revision")
    clean = {"revision": revision, "resources": _links(data.get("resources", []), 60), "teachers": {}, "cards": [], "tips": {}, "tools": {}}
    teachers = data.get("teachers", {})
    if not isinstance(teachers, dict): raise CatalogError("teachers must be an object")
    for key, links in list(teachers.items())[:20]:
        if re.fullmatch(r"[a-z]{2,20}", str(key)): clean["teachers"][key] = _links(links, 12)
    for card in data.get("cards", [])[:200]:
        if not isinstance(card, dict): continue
        if not re.fullmatch(r"[a-z0-9_-]{2,40}", str(card.get("id", ""))) or card.get("category") not in {"places", "culture", "food", "nature", "history", "positive"}: continue
        checked = str(card.get("checked_on", ""))
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", checked): continue
        clean["cards"].append({"id": card["id"], "category": card["category"], "source": _url(card["source"]) if card.get("source") else "",
                               "checked_on": checked, "text": _translations(card.get("text"))})
    tips = data.get("tips", {})
    if isinstance(tips, dict):
        for lang in LANGS:
            if isinstance(tips.get(lang), list): clean["tips"][lang] = [_text(t, 200) for t in tips[lang][:30]]
    tools = data.get("tools", {})
    if isinstance(tools, dict):
        for key, names in list(tools.items())[:40]:
            if re.fullmatch(r"[a-z_]{2,20}", str(key)) and isinstance(names, list):
                clean["tools"][key] = [n for n in names[:8] if isinstance(n, str) and re.fullmatch(r"[a-z0-9][a-z0-9.-]{1,40}", n)]
    return clean

def _read(path):
    try:
        if path.is_file() and not path.is_symlink() and path.stat().st_size <= 600_000:
            return validate(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, ValueError, KeyError, TypeError, IndexError):
        pass
    return None

def current():
    """Newest valid catalog: the downloaded cache if newer than the shipped one."""
    shipped, cached = _read(SHIPPED), _read(cache_path())
    if cached and (not shipped or cached["revision"] > shipped["revision"]): return cached
    return shipped

def last_check():
    try: return json.loads((cache_path().parent / "update-state.json").read_text()).get("checked", 0.0)
    except (OSError, ValueError, AttributeError): return 0.0

def _write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".lafa-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream: json.dump(value, stream, ensure_ascii=False, indent=1)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

def check(fetch=None, now=None):
    """Download, validate and cache the catalog. Returns (updated, revision)."""
    fetch = fetch or (lambda: request(CATALOG_URL, timeout=20, limit=600_000))
    known = current(); revision = known["revision"] if known else 0
    try:
        data = validate(json.loads(fetch()))
    except (ValueError, UnicodeError) as error:
        raise NetworkError("The online source catalog is not valid; LAFA keeps its current sources.") from error
    finally:
        _write(cache_path().parent / "update-state.json", {"checked": now or time.time()})
    if data["revision"] > revision:
        _write(cache_path(), data); return True, data["revision"]
    return False, revision

def due(hours, now=None):
    return (now or time.time()) - last_check() >= hours * 3600

def apply(catalog=None):
    """Merge a catalog into LAFA's running data (links are added, never removed)."""
    catalog = catalog or current()
    if not catalog: return 0
    from . import tools, school, osguide
    added = 0
    known = {url for _, url in tools.RESOURCES}
    for title, url in catalog["resources"]:
        if url not in known: tools.RESOURCES.append((title, url)); known.add(url); added += 1
    for key, links in catalog["teachers"].items():
        teacher = school.BY_KEY.get(key)
        if not teacher: continue
        urls = {url for _, url in teacher.resources}
        for title, url in links:
            if url not in urls: teacher.resources.append((title, url)); urls.add(url); added += 1
    for lang, tips in catalog["tips"].items():
        current_tips = osguide.TIPS.setdefault(lang, [])
        for tip in tips:
            if tip not in current_tips: current_tips.append(tip); added += 1
    for key, names in catalog["tools"].items():
        guide = osguide.BY_KEY.get(key)
        if guide:
            merged = tuple(dict.fromkeys(list(guide.tools) + names))
            if merged != guide.tools: guide.tools = merged; added += 1
    return added

def extra_cards(catalog=None):
    catalog = catalog or current()
    return catalog["cards"] if catalog else []

def newer_release(fetch=None):
    """Version string of a newer LAFA release on GitHub, or None."""
    data = (fetch or (lambda: json_request(RELEASES_URL, headers={"Accept": "application/vnd.github+json"}, timeout=15)))()
    tag = str(data.get("tag_name", "")).lstrip("vV") if isinstance(data, dict) else ""
    if not re.fullmatch(r"\d+(\.\d+){1,3}([ab]\d+)?", tag): return None
    return tag if version_key(tag) > version_key(__version__) else None

def version_key(text):
    match = re.fullmatch(r"(\d+)\.(\d+)(?:\.(\d+))?(?:\.(\d+))?(?:([ab])(\d+))?", text)
    if not match: return (0,)
    major, minor, patch, extra, stage, number = match.groups()
    # Final releases sort after alpha/beta of the same version.
    stage_rank = {"a": 0, "b": 1, None: 2}[stage]
    return (int(major), int(minor), int(patch or 0), int(extra or 0), stage_rank, int(number or 0))
