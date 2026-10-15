#!/usr/bin/env python3
"""Validate lafa/assets/encyclopedia/**/*.json (Lafa's encyclopedia articles).

    python3 tools/check-encyclopedia.py [file.json ...]

One file per category: {"area", "category", "articles": [...], "coverage": [...]}.
Every article has an id, four-language title and summary, learning objectives,
3–6 sections, sources (HTTPS, publisher, year), related ids, tags, a quiz with
explanations and review metadata (version, review date, status, licence and the
languages that have the full text). Full text must exist in English and
Indonesian; Portuguese and Tetun may have only title, summary and objectives —
the reader shows that honestly.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "lafa/assets/encyclopedia"
LANGS = ("en", "id", "pt", "tet")
FULL = ("en", "id")
AREAS = {"world": ["earth", "dinosaurs", "human_origins", "civilizations", "inventions", "colonialism",
                   "industrial_revolution", "world_wars", "geography_oceans", "life_environment",
                   "science_space", "culture_arts"],
         "timor": ["history", "map", "culture", "nature", "leaders", "economy"]}
STATUS = ("available", "review", "planned")
ID = re.compile(r"^(w|tl)\.[a-z_]+\.[a-z0-9_]+$")

def texts(value, where, errors, langs=LANGS, limit=2000, optional=()):
    if not isinstance(value, dict):
        errors.append(f"{where}: must be an object of languages"); return
    for lang in langs:
        item = value.get(lang)
        if lang in optional and item in (None, ""): continue
        if not isinstance(item, str) or not item.strip(): errors.append(f"{where}.{lang}: empty")
        elif len(item) > limit: errors.append(f"{where}.{lang}: longer than {limit}")
    extra = set(value) - set(LANGS)
    if extra: errors.append(f"{where}: unknown languages {sorted(extra)}")
    if value.get("tet") and value.get("en") and value["tet"] == value["en"] and len(value["en"]) > 25:
        errors.append(f"{where}.tet: copied from English")

def lists(value, where, errors, langs, n=None):
    if not isinstance(value, dict): errors.append(f"{where}: must be an object of languages"); return
    for lang in langs:
        items = value.get(lang)
        if not isinstance(items, list) or not items or not all(isinstance(i, str) and i.strip() for i in items):
            errors.append(f"{where}.{lang}: needs a list of texts"); continue
        if n and len(items) != n: errors.append(f"{where}.{lang}: needs {n} items")

def check_article(a, area, category, errors, ids):
    where = f"article {a.get('id', '?')}"
    if not isinstance(a.get("id"), str) or not ID.match(a["id"]): errors.append(f"{where}: id must look like w.<category>.<name> or tl.<category>.<name>"); return
    prefix = "w" if area == "world" else "tl"
    if not a["id"].startswith(f"{prefix}.{category}."): errors.append(f"{where}: id must start with {prefix}.{category}.")
    if a["id"] in ids: errors.append(f"{where}: duplicate id")
    ids.add(a["id"])
    texts(a.get("title"), where + ".title", errors, limit=90)
    texts(a.get("summary"), where + ".summary", errors, limit=400)
    lists(a.get("objectives"), where + ".objectives", errors, LANGS)
    sections = a.get("sections")
    if not isinstance(sections, list) or not 3 <= len(sections) <= 7: errors.append(f"{where}.sections: 3–7 needed")
    else:
        for i, s in enumerate(sections):
            texts(s.get("heading") if isinstance(s, dict) else None, f"{where}.sections[{i}].heading", errors, FULL, 90, ())
            texts(s.get("body") if isinstance(s, dict) else None, f"{where}.sections[{i}].body", errors, FULL, 1600, ())
    sources = a.get("sources")
    if not isinstance(sources, list) or not sources: errors.append(f"{where}.sources: at least one source")
    else:
        for i, s in enumerate(sources):
            if not isinstance(s, dict): errors.append(f"{where}.sources[{i}]: object needed"); continue
            if not str(s.get("url", "")).startswith("https://"): errors.append(f"{where}.sources[{i}].url: HTTPS needed")
            for key in ("title", "publisher", "year"):
                if not isinstance(s.get(key), str) or not s[key].strip(): errors.append(f"{where}.sources[{i}].{key} missing")
    for key in ("related", "tags"):
        if not isinstance(a.get(key), list) or not all(isinstance(x, str) for x in a[key]): errors.append(f"{where}.{key}: list of texts")
    for i, f in enumerate(a.get("facts", [])):
        texts(f.get("label") if isinstance(f, dict) else None, f"{where}.facts[{i}].label", errors, FULL, 80)
        texts(f.get("value") if isinstance(f, dict) else None, f"{where}.facts[{i}].value", errors, FULL, 160)
        if not isinstance(f, dict) or not isinstance(f.get("year"), str): errors.append(f"{where}.facts[{i}].year: text ('' if timeless)")
    quiz = a.get("quiz")
    if not isinstance(quiz, list) or len(quiz) < 2: errors.append(f"{where}.quiz: at least two questions")
    else:
        for i, q in enumerate(quiz):
            w = f"{where}.quiz[{i}]"
            if not isinstance(q, dict): errors.append(w + ": object needed"); continue
            texts(q.get("q"), w + ".q", errors, FULL, 240)
            lists(q.get("options"), w + ".options", errors, FULL, 4)
            if q.get("answer") not in (0, 1, 2, 3): errors.append(w + ".answer: 0–3")
            texts(q.get("explain"), w + ".explain", errors, FULL, 400)
            for lang in FULL:
                opts = (q.get("options") or {}).get(lang) or []
                if len(set(opts)) != len(opts): errors.append(f"{w}.options.{lang}: repeated option")
    review = a.get("review")
    if not isinstance(review, dict): errors.append(f"{where}.review missing")
    else:
        if not isinstance(review.get("version"), int) or review["version"] < 1: errors.append(f"{where}.review.version")
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(review.get("reviewed", ""))): errors.append(f"{where}.review.reviewed: YYYY-MM-DD")
        for key in ("status", "licence"):
            if not isinstance(review.get(key), str) or not review[key].strip(): errors.append(f"{where}.review.{key} missing")
        full = review.get("langs_full")
        if not isinstance(full, list) or not set(FULL) <= set(full) or not set(full) <= set(LANGS): errors.append(f"{where}.review.langs_full must include en and id")
        else:
            for lang in set(full) - set(FULL):
                for i, s in enumerate(sections or []):
                    if not (s.get("body") or {}).get(lang): errors.append(f"{where}: langs_full lists {lang} but sections[{i}] has no {lang} text")

def check(path, ids=None):
    ids = ids if ids is not None else set()
    errors = []
    try: data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as error: return [f"{path}: {error}"]
    area = data.get("area"); category = data.get("category")
    if area not in AREAS: return [f"{path}: area must be one of {sorted(AREAS)}"]
    if category not in AREAS[area]: errors.append(f"{path}: unknown category {category!r}")
    if Path(path).stem != category: errors.append(f"{path}: file name must be <category>.json")
    articles = data.get("articles")
    if not isinstance(articles, list): return errors + [f"{path}: articles missing"]
    for a in articles:
        if isinstance(a, dict): check_article(a, area, category, errors, ids)
        else: errors.append(f"{path}: article must be an object")
    for i, c in enumerate(data.get("coverage", [])):
        if not isinstance(c, dict) or c.get("status") not in STATUS: errors.append(f"{path}.coverage[{i}].status: one of {STATUS}"); continue
        texts(c.get("topic"), f"{path}.coverage[{i}].topic", errors, FULL, 120)
    return [f"{Path(path).name}: {e}" for e in errors]

def main(argv):
    files = [Path(p) for p in argv] or sorted(FOLDER.glob("*/*.json"))
    ids = set(); errors = []; articles = []
    for path in files:
        errors += check(path, ids)
        try: articles += json.loads(path.read_text(encoding="utf-8")).get("articles", [])
        except (OSError, ValueError, AttributeError): pass
    if not argv:
        for a in articles:
            for rel in a.get("related", []) if isinstance(a, dict) else []:
                if rel not in ids and not rel.startswith(("lesson:", "atlas:")): errors.append(f"{a.get('id')}: related {rel!r} does not exist")
    for e in errors: print("✗", e)
    if not errors: print(f"✓ {len(files)} files, {len(ids)} articles")
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
