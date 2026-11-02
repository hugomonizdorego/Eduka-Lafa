"""Download for offline use and update the database when there is internet.

* Wikipedia (tet, pt): the introduction of each item's page (TextExtracts,
  CC BY-SA 4.0); the names of its lead picture and, optionally, of more
  photos on the page (en and pt pages, which have the most pictures).
* Wikimedia Commons: the picture's licence; only free licences (CC0, public
  domain, CC BY, CC BY-SA) are downloaded, with author and licence saved.
* World Bank Open Data (CC BY 4.0): fresh series for the indicators.
* Lafa content updates: manifest.json in the project's public GitHub
  repository lists the content files with their SHA-256; changed files are
  downloaded, checked (hash, size, JSON shape) and saved in updates/.

Only HTTPS, fixed hosts, no redirects, size limits, data only (never code).
Every function takes `progress(done, total, text)` and `cancelled()`.
"""
import hashlib
import json
import os
import re
import time
import urllib.parse
from html import unescape
from pathlib import Path

from . import net

REPO_RAW = "https://raw.githubusercontent.com/hugomonizdorego/Eduka-Lafa/main/lafa/assets/timor/"
WIKI_LANGS = ("tet", "pt")                 # introductions: the languages of Lafa
PICTURE_LANGS = ("en", "pt")               # pages searched for pictures
GALLERY_EXT = re.compile(r"\.(jpe?g|png|webp)$", re.I)
GALLERY_SKIP = re.compile(r"(flag[_ ]of|coat[_ ]of[_ ]arms|emblem[_ ]of|locator|location|[_ ]map\b|\bmap[_ ]|map[_ ]of|icon|logo|symbol|"
                          r"commons-|wiki(quote|source|tionary|voyage|data|books|news)|edit-clear|question[_ ]book|ambox|disambig|padlock|"
                          r"portal|blank|signature|audio|speaker|button|arrow|pictogram)", re.I)
FREE_LICENCE = re.compile(r"^(cc0|cc[ -]?zero|public domain|pd\b|pd-|cc by(-sa)?( \d(\.\d)?)?( [a-z]{2,})?$|cc-by(-sa)?-\d)", re.I)
INDICATORS = ["SP.POP.TOTL", "SP.POP.GROW", "NY.GDP.MKTP.CD", "NY.GDP.PCAP.CD", "SP.DYN.LE00.IN", "EG.ELC.ACCS.ZS", "IT.NET.USER.ZS",
              "SP.URB.TOTL.IN.ZS", "SE.PRM.ENRR", "SH.DYN.MORT"]
MAX_IMAGE = 6_000_000
MAX_CONTENT = 8_000_000
ALLOWED_UPDATE = re.compile(r"^(content|vocab|map)/[a-z0-9_]+\.json$")

def _noop_progress(done, total, text=""): pass
def _never(): return False

def strip_html(value):
    return " ".join(unescape(re.sub(r"<[^>]+>", " ", str(value or ""))).split())

def free_licence(meta):
    """True for CC0 / public domain / CC BY / CC BY-SA files that are not marked non-free."""
    if str((meta.get("NonFree") or {}).get("value", "")).lower() == "true": return False
    name = strip_html((meta.get("LicenseShortName") or {}).get("value", ""))
    return bool(FREE_LICENCE.match(name.strip()))

# ------------------------------------------------------------------ Wikipedia
def wiki_api(lang, params, timeout=30):
    query = urllib.parse.urlencode({"format": "json", "formatversion": "2", **params})
    return net.json_request(f"https://{lang}.wikipedia.org/w/api.php?{query}", timeout=timeout)

def wiki_intros(lang, titles, chars=2400):
    """{requested title: {"title", "text", "url", "image"}} for up to 20 titles (one request)."""
    data = wiki_api(lang, {"action": "query", "redirects": "1", "prop": "extracts|pageimages|info", "exintro": "1", "explaintext": "1",
                           "exchars": str(chars), "exlimit": "20", "piprop": "name", "inprop": "url", "titles": "|".join(titles[:20])})
    q = data.get("query") or {}
    back = {}
    for step in (q.get("normalized") or []) + (q.get("redirects") or []):
        back[step.get("to")] = back.get(step.get("from"), step.get("from"))
    out = {}
    for page in q.get("pages") or []:
        if page.get("missing") or not page.get("extract"): continue
        requested = back.get(page.get("title"), page.get("title"))
        out[requested] = {"title": page.get("title", ""), "text": page["extract"].strip(), "url": page.get("fullurl", ""), "image": page.get("pageimage", "")}
    return out

def _back_titles(q):
    back = {}
    for step in (q.get("normalized") or []) + (q.get("redirects") or []):
        back[step.get("to")] = back.get(step.get("from"), step.get("from"))
    return back

def wiki_lead_images(lang, titles):
    """{requested title: file name} of the lead picture (PageImages names free files only), up to 20 titles."""
    data = wiki_api(lang, {"action": "query", "redirects": "1", "prop": "pageimages", "piprop": "name", "titles": "|".join(titles[:20])})
    q = data.get("query") or {}; back = _back_titles(q)
    return {back.get(p.get("title"), p.get("title")): p["pageimage"] for p in q.get("pages") or [] if p.get("pageimage")}

def wiki_page_images(lang, title, limit=50):
    """Photos shown on one Wikipedia page (no maps, flags, logos or icons), in page order."""
    data = wiki_api(lang, {"action": "query", "redirects": "1", "prop": "images", "imlimit": str(limit), "titles": title})
    names = []
    for page in (data.get("query") or {}).get("pages") or []:
        for image in page.get("images") or []:
            name = str(image.get("title", "")).split(":", 1)[-1]
            if GALLERY_EXT.search(name) and not GALLERY_SKIP.search(name) and name not in names: names.append(name)
    return names

def commons_info(file_name, width=1280):
    """Licence and download URL of a Commons file, or None when it is not on Commons."""
    query = urllib.parse.urlencode({"action": "query", "format": "json", "formatversion": "2", "prop": "imageinfo",
                                    "iiprop": "url|extmetadata|size|mime", "iiurlwidth": str(width), "titles": "File:" + file_name})
    data = net.json_request("https://commons.wikimedia.org/w/api.php?" + query, timeout=30)
    pages = (data.get("query") or {}).get("pages") or []
    if not pages or pages[0].get("missing") or not pages[0].get("imageinfo"): return None
    info = pages[0]["imageinfo"][0]; meta = info.get("extmetadata") or {}
    return {"url": info.get("thumburl") or info.get("url"), "mime": info.get("mime", ""), "width": info.get("thumbwidth") or info.get("width", 0),
            "height": info.get("thumbheight") or info.get("height", 0), "free": free_licence(meta),
            "licence": strip_html((meta.get("LicenseShortName") or {}).get("value", "")), "licence_url": strip_html((meta.get("LicenseUrl") or {}).get("value", "")),
            "author": strip_html((meta.get("Artist") or {}).get("value", ""))[:200] or strip_html((meta.get("Credit") or {}).get("value", ""))[:200],
            "source_url": info.get("descriptionurl", ""), "title": file_name}

def image_kind(data):
    if data[:3] == b"\xff\xd8\xff": return "jpg"
    if data[:8] == b"\x89PNG\r\n\x1a\n": return "png"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP": return "webp"
    return None

def _download_picture(name, width=1280):
    """(bytes, extension, credit) of a free Commons picture, or None."""
    info = commons_info(name, width)
    if not info or not info["free"] or not str(info.get("url", "")).startswith("https://upload.wikimedia.org/"): return None
    data = net.request(info["url"], timeout=60, limit=MAX_IMAGE); ext = image_kind(data)
    return (data, ext, info) if ext else None

def download_offline(kb, store, langs=WIKI_LANGS, photos=True, gallery=0, progress=_noop_progress, cancelled=_never):
    """Download Wikipedia introductions, a free lead picture and (gallery > 0) up to `gallery`
    more free pictures for every item that names a Wikipedia page."""
    items = [i for i in kb.all() if i.wiki()]
    jobs = []
    for lang in langs:
        titled = [(i, i.wiki().get(lang)) for i in items if i.wiki().get(lang)]
        for n in range(0, len(titled), 20): jobs.append((lang, titled[n:n + 20]))
    picture_jobs = []
    if photos:
        for lang in PICTURE_LANGS:
            titled = [(i, i.wiki().get(lang)) for i in items if i.wiki().get(lang) and not store.photo(i.id)]
            for n in range(0, len(titled), 20): picture_jobs.append((lang, titled[n:n + 20]))
    picture_items = {i.id: i for i in items} if photos else {}
    gallery_items = [i for i in items if any(i.wiki().get(l) for l in PICTURE_LANGS)] if gallery > 0 else []
    total = len(jobs) + len(picture_jobs) + len(picture_items) + len(gallery_items); done = 0; errors = []; texts = 0; pictures = 0; extra = 0; images = {}
    for lang, batch in jobs:
        if cancelled(): break
        progress(done, total, f"Wikipedia ({lang}) …")
        try:
            found = wiki_intros(lang, [t for _, t in batch])
            for item, title in batch:
                page = found.get(title) or found.get(title.replace("_", " "))
                if not page: continue
                store.put_extract(item.id, lang, page["title"], page["text"], page["url"], f"Wikipedia ({lang})", "CC BY-SA 4.0"); texts += 1
                if page.get("image"): images.setdefault(item.id, page["image"])   # PageImages only names free pictures
        except net.NetworkError as e: errors.append(f"{lang}: {e}")
        done += 1; time.sleep(0.2)
    for lang, batch in picture_jobs:
        if cancelled(): break
        progress(done, total, f"Wikipedia ({lang}) …")
        try:
            found = wiki_lead_images(lang, [t for _, t in batch])
            for item, title in batch:
                name = found.get(title) or found.get(title.replace("_", " "))
                if name: images.setdefault(item.id, name)
        except net.NetworkError as e: errors.append(f"{lang}: {e}")
        done += 1; time.sleep(0.2)
    for item_id, item in picture_items.items():
        if cancelled(): break
        done += 1; progress(done, total, item.title("pt"))
        name = item.get("commons") if isinstance(item.get("commons"), str) else images.get(item_id)
        if not name or store.photo(item_id): continue
        try:
            got = _download_picture(name)
            if got: store.put_photo(item_id, *got); pictures += 1
        except (net.NetworkError, OSError) as e: errors.append(f"{item_id}: {e}")
        time.sleep(0.2)
    for item in gallery_items:
        if cancelled(): break
        done += 1; progress(done, total, item.title("pt"))
        have = store.gallery(item.id)
        if len(have) >= gallery: continue
        skip = store.gallery_titles(item.id) | {images.get(item.id, "")}
        if isinstance(item.get("commons"), str): skip.add(item.get("commons"))
        try:
            names = []
            for lang in PICTURE_LANGS:
                title = item.wiki().get(lang)
                if title and len(names) < 12: names += [n for n in wiki_page_images(lang, title) if n not in names and n not in skip]
            n = max([info.get("n", 0) for _p, info in have] or [0])
            for name in names[:10]:
                if len(store.gallery(item.id)) >= gallery or cancelled(): break
                got = _download_picture(name, 1024)
                if got: n += 1; store.put_gallery(item.id, n, *got); extra += 1
                time.sleep(0.2)
        except (net.NetworkError, OSError) as e: errors.append(f"{item.id}: {e}")
    store.set_meta("offline_download", time.strftime("%Y-%m-%d %H:%M"))
    return {"texts": texts, "pictures": pictures, "gallery": extra, "errors": errors[:20], "cancelled": cancelled()}

# ----------------------------------------------------------------- World Bank
def update_indicators(kb, updates, progress=_noop_progress, cancelled=_never):
    """Fresh World Bank series for Timor-Leste, saved as updates/content/indicators.json."""
    known = {i.get("id"): i for i in kb.indicators if isinstance(i, dict) and i.get("id")}
    codes = list(dict.fromkeys(list(known) + INDICATORS)); out = []; errors = []
    for n, code in enumerate(codes):
        if cancelled(): break
        progress(n, len(codes), code)
        try:
            data = net.json_request(f"https://api.worldbank.org/v2/country/TLS/indicator/{urllib.parse.quote(code)}?format=json&per_page=100", timeout=30)
        except net.NetworkError as e: errors.append(f"{code}: {e}"); continue
        if not isinstance(data, list) or len(data) < 2 or not isinstance(data[1], list): continue
        series = sorted([int(r["date"]), float(r["value"])] for r in data[1] if r.get("value") is not None and str(r.get("date", "")).isdigit())
        if not series: continue
        name = known.get(code, {}).get("name") or {lang: (data[1][0].get("indicator") or {}).get("value", code) for lang in ("tet", "pt")}
        entry = dict(known.get(code, {})); entry.update({"id": code, "name": name, "series": series, "source": "World Bank WDI",
                                                         "url": f"https://data.worldbank.org/indicator/{code}?locations=TL", "licence": "CC BY 4.0",
                                                         "accessed": time.strftime("%Y-%m-%d")})
        out.append(entry)
    if out:
        folder = Path(updates) / "content"; folder.mkdir(parents=True, exist_ok=True)
        write_atomic(folder / "indicators.json", json.dumps({"indicators": out}, ensure_ascii=False, indent=1).encode("utf-8"))
    return {"indicators": len(out), "errors": errors[:10]}

# ------------------------------------------------------------- content updates
def sha256(data): return hashlib.sha256(data).hexdigest()

def local_hash(base, updates, path):
    for folder in (Path(updates), Path(base)):
        f = folder / path
        if f.is_file():
            try: return sha256(f.read_bytes())
            except OSError: return ""
    return ""

def valid_content(path, data):
    """JSON of the right shape for its folder (content, vocab or map)."""
    try: obj = json.loads(data.decode("utf-8"))
    except (ValueError, UnicodeError): return False
    if not isinstance(obj, dict): return False
    if path.startswith("content/"): return any(isinstance(obj.get(k), list) for k in ("articles", "municipalities", "places", "days", "indicators"))
    if path.startswith("vocab/"): return isinstance(obj.get("words"), (list, dict))
    if path.startswith("map/"): return isinstance(obj.get("municipalities") or obj.get("posts"), list)
    return False

def check_updates(base, updates, current_version=""):
    """The remote manifest and the files that differ from what this computer has."""
    manifest = net.json_request(REPO_RAW + "manifest.json", timeout=30)
    files = manifest.get("files") if isinstance(manifest, dict) else None
    if not isinstance(files, dict): raise net.NetworkError("The update list is not valid.")
    changed = []
    for path, meta in files.items():
        if not ALLOWED_UPDATE.match(path) or not isinstance(meta, dict): continue
        if not re.fullmatch(r"[0-9a-f]{64}", str(meta.get("sha256", ""))) or int(meta.get("size", 0)) > MAX_CONTENT: continue
        if local_hash(base, updates, path) != meta["sha256"]: changed.append((path, meta))
    return {"version": str(manifest.get("content_version", "")), "min_app": str(manifest.get("min_app", "")), "changed": changed,
            "newer": str(manifest.get("content_version", "")) > str(current_version or "")}

def apply_updates(base, updates, changed, progress=_noop_progress, cancelled=_never):
    """Download changed files, verify them and save them in updates/ (atomic)."""
    saved = []; errors = []
    for n, (path, meta) in enumerate(changed):
        if cancelled(): break
        progress(n, len(changed), path)
        try:
            data = net.request(REPO_RAW + path, timeout=60, limit=MAX_CONTENT)
            if sha256(data) != meta["sha256"]: errors.append(f"{path}: hash"); continue
            if not valid_content(path, data): errors.append(f"{path}: format"); continue
            target = Path(updates) / path; target.parent.mkdir(parents=True, exist_ok=True); write_atomic(target, data); saved.append(path)
        except (net.NetworkError, OSError) as e: errors.append(f"{path}: {e}")
    return {"saved": saved, "errors": errors[:10]}

def write_atomic(path, data):
    tmp = Path(str(path) + ".part"); tmp.write_bytes(data); os.replace(tmp, path)

def make_manifest(base, version):
    """Used by tools/make-manifest.py at release time."""
    files = {}
    for folder in ("content", "vocab", "map"):
        for f in sorted((Path(base) / folder).glob("*.json")):
            data = f.read_bytes(); files[f"{folder}/{f.name}"] = {"sha256": sha256(data), "size": len(data)}
    return {"content_version": version, "min_app": "0.3.0", "files": files}
