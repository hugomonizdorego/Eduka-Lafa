#!/usr/bin/env python3
"""Validate the Ensiklopédia Timór-Leste content (docs/CONTENT-SCHEMA.md).

    python3 tools/check-content.py                 # everything
    python3 tools/check-content.py content/x.json  # one file (paths relative to lafa/assets/timor)
    python3 tools/check-content.py --strict        # warnings count as errors

Exit status 0 when there are no errors. Warnings point at things a reviewer
should look at (Indonesian words in Tetun text, missing difficulty levels…).
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "lafa" / "assets" / "timor"
LANGS = ("tet", "pt", "id", "en")
LEVELS = {"eb1", "eb2", "eb3", "es", "sup"}
PLACE_TYPES = {"beach", "island", "mountain", "viewpoint", "church", "statue", "museum", "monument", "memorial", "lake", "cave",
               "hot_spring", "waterfall", "fort", "market", "park", "reef", "village", "town", "garden", "river"}
ILLUSTRATIONS = set("""
tl-overview island-formation geology mountain mountain-ramelau river lake sea-coast beach coral-reef whale climate flood earthquake forest
mangrove sandalwood crocodile birds animals national-park environment cave
prehistory austronesian-boat kingdom trade-ships caravel fort colonial-town treaty revolt ww2 carnation proclamation resistance memorial
nobel ballot un-peace independence constitution camp reconciliation maritime asean diplomacy church-crowd
parliament palace government-palace justice police military village-council
flag emblem anthem currency languages dili-city
tais uma-lulik dance likurai music legend food crafts adornment church mosque procession football literature festival people
oil-gas fund exports imports coffee rice maize crops livestock fishing minerals tourism port road electricity bank plan workers
population school university health youth women media city
island viewpoint statue museum monument hot-spring waterfall market village town garden diving trekking calendar new-year veterans labour
christmas easter eid heroes""".split())
VOCAB_LANGS = ("ms", "fil", "th", "vi", "km", "lo", "my", "zh", "ta", "es", "fr")
# Words that betray Indonesian (or English) in a Tetun text.
NOT_TETUN = re.compile(r"\b(tapi|sudah|dan|yang|untuk|dengan|adalah|karena|tetapi|juga|dari|pada|akan|bisa|telah|the|and|of)\b", re.I)
DATE = re.compile(r"^-?\d{1,6}(-\d{2}(-\d{2})?)?$")

class Report:
    def __init__(self): self.errors = []; self.warnings = []
    def err(self, where, msg): self.errors.append(f"{where}: {msg}")
    def warn(self, where, msg): self.warnings.append(f"{where}: {msg}")

def l4(r, where, value, name, required=True, minimum=1):
    if not isinstance(value, dict):
        if required or value is not None: r.err(where, f"{name} must be an object with {', '.join(LANGS)}")
        return
    for lang in LANGS:
        text = value.get(lang)
        if not isinstance(text, str) or len(text.strip()) < minimum:
            r.err(where, f"{name}.{lang} is missing or empty")
    tet = value.get("tet") or ""
    if isinstance(tet, str):
        bad = sorted({m.group(0).lower() for m in NOT_TETUN.finditer(tet)})
        if bad: r.warn(where, f"{name}.tet contains non-Tetun words: {', '.join(bad)}")
        if "’" in tet: r.warn(where, f"{name}.tet: use the plain apostrophe ' in content files")
        if re.search(r"\bTimor-Leste\b", tet) and not re.search(r"https?://", tet):
            r.warn(where, f"{name}.tet: write Timór-Leste (Konstituisaun spelling)")

def sources(r, where, items):
    if not isinstance(items, list) or len(items) < 2:
        r.err(where, "needs at least two sources"); return
    for s in items:
        if not isinstance(s, dict) or not str(s.get("url", "")).startswith("https://"):
            r.err(where, f"source without an https url: {s!r}"[:200]); continue
        if not s.get("title") or not s.get("publisher"): r.err(where, f"source needs title and publisher: {s.get('url')}")
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(s.get("accessed", ""))): r.err(where, f"source needs accessed YYYY-MM-DD: {s.get('url')}")

def quiz(r, where, items, required=True, minimum=4):
    if not items:
        if required: r.err(where, "needs quiz questions")
        return
    if not isinstance(items, list): r.err(where, "quiz must be a list"); return
    if required and len(items) < minimum: r.warn(where, f"only {len(items)} quiz questions (aim for {minimum}–6)")
    levels = set()
    for i, q in enumerate(items):
        w = f"{where} quiz[{i}]"
        if not isinstance(q, dict): r.err(w, "must be an object"); continue
        l4(r, w, q.get("q"), "q"); l4(r, w, q.get("why"), "why")
        opts = q.get("options")
        if not isinstance(opts, list) or len(opts) != 4: r.err(w, "needs exactly four options"); opts = []
        for j, o in enumerate(opts): l4(r, w, o, f"options[{j}]")
        if q.get("answer") not in (0, 1, 2, 3): r.err(w, "answer must be 0–3")
        d = q.get("difficulty")
        if not isinstance(d, int) or not 1 <= d <= 15: r.err(w, "difficulty must be 1–15")
        else: levels.add("easy" if d <= 5 else "medium" if d <= 10 else "hard")
        for lang in LANGS:
            texts = [o.get(lang, "").strip().casefold() for o in opts if isinstance(o, dict)]
            if len(texts) == 4 and len(set(texts)) < 4: r.err(w, f"options repeat in {lang}")
    if required and len(levels) < 3: r.warn(where, f"quiz covers only {sorted(levels)} (want easy, medium and hard)")

def sections(r, where, items, minimum=3):
    if not isinstance(items, list) or len(items) < minimum:
        r.err(where, f"needs at least {minimum} sections"); return
    for i, s in enumerate(items):
        l4(r, f"{where} sections[{i}]", s.get("heading") if isinstance(s, dict) else None, "heading")
        l4(r, f"{where} sections[{i}]", s.get("text") if isinstance(s, dict) else None, "text", minimum=40)

def facts(r, where, items):
    for i, f in enumerate(items or []):
        w = f"{where} facts[{i}]"
        if not isinstance(f, dict): r.err(w, "must be an object"); continue
        l4(r, w, f.get("label"), "label")
        v = f.get("value")
        if isinstance(v, dict): l4(r, w, v, "value")
        elif not isinstance(v, (str, int, float)) or v == "": r.err(w, "value must be text, a number or L4")
        if "year" in f and not isinstance(f["year"], int): r.err(w, "year must be a number")

def common(r, where, item, known, kind):
    fig = item.get("figure")
    if fig is not None:
        if not isinstance(fig, dict) or fig.get("illustration") not in ILLUSTRATIONS: r.err(where, f"unknown figure illustration {fig!r}"[:160])
        elif "caption" in fig: l4(r, where, fig["caption"], "figure.caption")
    if "illustration" in item and item["illustration"] not in ILLUSTRATIONS: r.err(where, f"unknown illustration {item['illustration']!r}")
    for rel in item.get("related", []) or []:
        if rel not in known: r.warn(where, f"related id not found (yet): {rel}")
    wiki = item.get("wiki")
    if wiki is not None and (not isinstance(wiki, dict) or any(k not in LANGS for k in wiki)): r.err(where, "wiki must map tet/pt/id/en to page titles")
    rev = item.get("review")
    if not isinstance(rev, dict) or rev.get("status") not in ("draft", "reviewed"): r.err(where, "review.status must be draft or reviewed")
    for t in item.get("timeline", []) or []:
        if not isinstance(t, dict) or not DATE.match(str(t.get("date", ""))): r.err(where, f"bad timeline date {t!r}"[:160])
        else: l4(r, where, t.get("title"), "timeline.title")

def check_article(r, where, a, plan, known):
    if not re.match(r"^tl\.[a-z_]+\.[a-z0-9_]+$", str(a.get("id", ""))): r.err(where, "bad id"); return
    if a.get("category") not in plan["categories"]: r.err(where, f"unknown category {a.get('category')}")
    elif a["id"].split(".")[1] != a["category"]: r.warn(where, "id category differs from category")
    for c in a.get("also", []) or []:
        if c not in plan["categories"]: r.err(where, f"unknown 'also' category {c}")
    l4(r, where, a.get("title"), "title"); l4(r, where, a.get("summary"), "summary", minimum=30)
    levels = a.get("levels")
    if not isinstance(levels, list) or not levels or not set(levels) <= LEVELS: r.err(where, f"levels must be from {sorted(LEVELS)}")
    sections(r, where, a.get("sections")); facts(r, where, a.get("facts"))
    quiz(r, where, a.get("quiz")); sources(r, where, a.get("sources")); common(r, where, a, known, "article")

def check_municipality(r, where, m, known):
    if not re.match(r"^mun\.[a-z]+$", str(m.get("id", ""))): r.err(where, "bad id")
    for key in ("name", "capital", "summary", "languages", "products"): l4(r, where, m.get(key), key)
    if not isinstance(m.get("area_km2"), (int, float)): r.err(where, "area_km2 must be a number")
    pop = m.get("population")
    if not isinstance(pop, dict) or not isinstance(pop.get("value"), int) or not isinstance(pop.get("year"), int): r.err(where, "population needs value and year")
    if not isinstance(m.get("posts"), list) or not m["posts"]: r.err(where, "posts must list the administrative posts")
    if not m.get("geo"): r.err(where, "geo (map shape name) missing")
    sections(r, where, m.get("sections")); facts(r, where, m.get("facts")); quiz(r, where, m.get("quiz"))
    sources(r, where, m.get("sources")); common(r, where, m, known, "municipality")

def check_place(r, where, p, known):
    if not re.match(r"^place\.[a-z0-9_]+$", str(p.get("id", ""))): r.err(where, "bad id")
    for key in ("name", "summary"): l4(r, where, p.get(key), key)
    l4(r, where, p.get("text"), "text", minimum=60); l4(r, where, p.get("tips"), "tips", minimum=10)
    if p.get("type") not in PLACE_TYPES: r.err(where, f"unknown type {p.get('type')}")
    if p.get("municipality") not in known: r.err(where, f"unknown municipality {p.get('municipality')}")
    lat, lon = p.get("lat"), p.get("lon")
    if not (isinstance(lat, (int, float)) and isinstance(lon, (int, float)) and -9.6 <= lat <= -8.0 and 124.0 <= lon <= 127.4):
        r.err(where, f"coordinates outside Timor-Leste: {lat}, {lon}")
    quiz(r, where, p.get("quiz"), required=False); sources(r, where, p.get("sources")); common(r, where, p, known, "place")

def check_day(r, where, d, known):
    if not re.match(r"^day\.[a-z_]+$", str(d.get("id", ""))): r.err(where, "bad id")
    date = str(d.get("date", ""))
    if not (re.match(r"^\d{2}-\d{2}$", date) or re.match(r"^easter[+-]\d+$", date) or date in ("islamic:eid_al_fitr", "islamic:eid_al_adha")):
        r.err(where, f"bad date rule {date}")
    if d.get("type") not in ("holiday", "commemorative"): r.err(where, "type must be holiday or commemorative")
    for key in ("name", "summary"): l4(r, where, d.get(key), key)
    sections(r, where, d.get("sections"), minimum=2); quiz(r, where, d.get("quiz"), minimum=2)
    sources(r, where, d.get("sources")); common(r, where, d, known, "day")

def check_vocab(r, path=None):
    main = path is None
    paths = [path] if path else [BASE / "vocab" / "words.json"] + sorted((BASE / "vocab").glob("words_*.json"))
    if not paths[0].exists(): r.warn("vocab", f"vocab/{paths[0].name} not written yet"); return 0
    words = []
    for one in paths: words += json.loads(one.read_text(encoding="utf-8")).get("words", [])
    ids = set(); seen = {}
    for w in words:
        where = f"vocab {w.get('id')}"
        if not re.match(r"^w\d{4,5}$", str(w.get("id", ""))): r.err(where, "bad id")
        if w.get("id") in ids: r.err(where, "duplicate id")
        ids.add(w.get("id"))
        for key in ("tet", "en", "pt", "ind", "cat", "pos"):
            if not isinstance(w.get(key), str) or not w[key].strip(): r.err(where, f"{key} missing")
        if not isinstance(w.get("level"), int) or w["level"] not in (1, 2, 3): r.err(where, "level must be 1, 2 or 3")
        key = (str(w.get("tet", "")).casefold(), str(w.get("en", "")).casefold())
        if key in seen: r.warn(where, f"same word as {seen[key]}")
        seen[key] = w.get("id")
    if not main: return len(words)
    if len(words) < 1000: r.warn("vocab", f"only {len(words)} words (goal: 1000+)")
    for lang in VOCAB_LANGS:
        p = BASE / "vocab" / f"{lang}.json"
        if not p.exists(): r.warn("vocab", f"{lang}.json not written yet"); continue
        tr = json.loads(p.read_text(encoding="utf-8"))
        missing = [i for i in ids if not str(tr.get("words", {}).get(i, "")).strip()]
        extra = [i for i in tr.get("words", {}) if i not in ids]
        if missing: r.warn("vocab", f"{lang}: {len(missing)} words without translation")
        if extra: r.err("vocab", f"{lang}: unknown ids {extra[:5]}")
    return len(words)

def load_all(files):
    items = []
    for f in files:
        try: data = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e: items.append(("error", f, str(e))); continue
        for kind in ("articles", "municipalities", "places", "days"):
            for it in data.get(kind, []) if isinstance(data, dict) else []: items.append((kind, f, it))
        if isinstance(data, dict) and "indicators" in data: items.append(("indicators", f, data["indicators"]))
    return items

def main(argv):
    strict = "--strict" in argv; args = [a for a in argv if not a.startswith("--")]
    plan = json.loads((BASE / "plan.json").read_text(encoding="utf-8"))
    every = sorted((BASE / "content").glob("*.json"))
    chosen = [BASE / a if not Path(a).is_absolute() else Path(a) for a in args] or every
    vocab_files = [p for p in chosen if p.parent.name == "vocab"]
    chosen = [p for p in chosen if p.parent.name != "vocab"]
    r = Report(); all_items = load_all(every)
    known = set(plan["articles"]) | set(plan["municipalities"]) | set(plan["days"])
    ids = {}
    for kind, f, it in all_items:
        if kind in ("articles", "municipalities", "places", "days") and isinstance(it, dict) and it.get("id"):
            if it["id"] in ids and ids[it["id"]] != (f, kind): r.err(f"{f.name} {it['id']}", f"duplicate id (also in {ids[it['id']][0].name})")
            ids[it["id"]] = (f, kind); known.add(it["id"])
    counts = {}
    for kind, f, it in load_all(chosen):
        if kind == "error": r.err(f.name, f"invalid JSON: {it}"); continue
        counts[kind] = counts.get(kind, 0) + (1 if kind != "indicators" else len(it))
        where = f"{f.name} {it.get('id') if isinstance(it, dict) else ''}"
        if kind == "articles": check_article(r, where, it, plan, known)
        elif kind == "municipalities": check_municipality(r, where, it, known)
        elif kind == "places": check_place(r, where, it, known)
        elif kind == "days": check_day(r, where, it, known)
        elif kind == "indicators":
            for ind in it:
                w = f"{f.name} {ind.get('id')}"; l4(r, w, ind.get("name"), "name")
                if not isinstance(ind.get("series"), list) or not ind["series"]: r.err(w, "series missing")
                if not str(ind.get("url", "")).startswith("https://"): r.err(w, "url missing")
    if not args: counts["words"] = check_vocab(r)
    for p in vocab_files: counts["words"] = counts.get("words", 0) + check_vocab(r, p)
    if not args:
        written = {i for i, (f, k) in ids.items() if k == "articles"}
        missing = sorted(set(plan["articles"]) - written)
        if missing: r.warn("plan", f"{len(missing)} planned articles not written yet")
    for w in r.warnings: print("warning:", w)
    for e in r.errors: print("ERROR:", e)
    print(("✗" if r.errors or (strict and r.warnings) else "✓"), ", ".join(f"{v} {k}" for k, v in counts.items()),
          f"· {len(r.errors)} errors · {len(r.warnings)} warnings")
    return 1 if r.errors or (strict and r.warnings) else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
