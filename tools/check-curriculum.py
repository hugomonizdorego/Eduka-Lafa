#!/usr/bin/env python3
"""Validate lafa/assets/curriculum/*.json (lessons for ages 5–100).

    python3 tools/check-curriculum.py [file.json ...]

Every text is a dict with en, id, pt and tet; every subject has one lesson per
age level; every question has one answer and three different wrong options.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LANGS = ("en", "id", "pt", "tet")
LEVELS = ("early", "primary", "middle", "secondary", "university", "adult", "senior")

def text(value, where, errors, limit=400):
    if not isinstance(value, dict) or set(value) != set(LANGS):
        errors.append(f"{where}: needs exactly {LANGS}"); return
    for lang in LANGS:
        item = value[lang]
        if not isinstance(item, str) or not item.strip(): errors.append(f"{where}.{lang}: empty")
        elif len(item) > limit: errors.append(f"{where}.{lang}: longer than {limit}")
    if value.get("tet") and value["tet"] == value.get("en") and len(value["en"]) > 25:
        errors.append(f"{where}.tet: copied from English")

def check(path):
    errors = []
    try: data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as error: return [f"{path}: {error}"]
    if not isinstance(data, dict) or not isinstance(data.get("subject"), str): return [f"{path}: needs subject"]
    if data["subject"] != Path(path).stem: errors.append(f"{path}: subject must match file name")
    text(data.get("name"), "name", errors, 40)
    if not isinstance(data.get("icon"), str) or not data["icon"]: errors.append("icon missing")
    lessons = data.get("lessons")
    if not isinstance(lessons, list): return errors + ["lessons missing"]
    levels = [lesson.get("level") for lesson in lessons if isinstance(lesson, dict)]
    for level in LEVELS:
        if level not in levels: errors.append(f"no lesson for level {level}")
    for i, lesson in enumerate(lessons):
        where = f"lessons[{i}]"
        if not isinstance(lesson, dict): errors.append(f"{where}: not an object"); continue
        if lesson.get("level") not in LEVELS: errors.append(f"{where}: bad level {lesson.get('level')!r}")
        text(lesson.get("title"), where + ".title", errors, 80)
        points = lesson.get("points")
        if not isinstance(points, list) or not 3 <= len(points) <= 5: errors.append(f"{where}.points: 3–5 needed")
        else:
            for j, point in enumerate(points): text(point, f"{where}.points[{j}]", errors)
        text(lesson.get("task"), where + ".task", errors)
        questions = lesson.get("questions")
        if not isinstance(questions, list) or not 3 <= len(questions) <= 5: errors.append(f"{where}.questions: 3–5 needed"); continue
        for j, q in enumerate(questions):
            qw = f"{where}.questions[{j}]"
            if not isinstance(q, dict): errors.append(qw + ": not an object"); continue
            text(q.get("q"), qw + ".q", errors, 250); text(q.get("answer"), qw + ".answer", errors, 120)
            wrong = q.get("wrong")
            if not isinstance(wrong, list) or len(wrong) != 3: errors.append(qw + ".wrong: exactly 3"); continue
            for k, w in enumerate(wrong): text(w, f"{qw}.wrong[{k}]", errors, 120)
            for lang in LANGS:
                options = [q.get("answer", {}).get(lang)] + [w.get(lang) if isinstance(w, dict) else None for w in wrong]
                if len(set(options)) != 4: errors.append(f"{qw}: options not distinct in {lang}")
    return errors

def main(paths):
    paths = paths or sorted(str(p) for p in (ROOT / "lafa/assets/curriculum").glob("*.json"))
    failed = False
    for path in paths:
        errors = check(path)
        print(("✗ " if errors else "✓ ") + path + (f" — {len(errors)} problem(s)" if errors else ""))
        for error in errors[:40]: print("   ", error)
        failed |= bool(errors)
    return 1 if failed else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
