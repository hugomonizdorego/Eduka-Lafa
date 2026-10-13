"""Learning for every age, from 5 to 100 years old.

Each subject (mathematics, physics, chemistry, biology, health and medicine,
environment, planets and the solar system, atoms and nuclear science,
geography, computers, IT and the internet, technology, history,
communication, economics, agriculture, civics, arts) has one lesson for each
of seven age levels, with study points, a task and three questions, in
English, Indonesian, Portuguese and Tetun. The lessons live in
lafa/assets/curriculum/<subject>.json (checked by tools/check-curriculum.py)
so teachers can improve them without touching code. Everything works offline.
"""
from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path
import random

ASSETS = Path(__file__).resolve().parent / "assets" / "curriculum"
LANGS = ("en", "id", "pt", "tet")

def L(en, id_, pt, tet):
    return {"en": en, "id": id_, "pt": pt, "tet": tet}

# key, (youngest, oldest), name
LEVELS = [
    ("early", (5, 7), L("Ages 5–7 · First steps", "Usia 5–7 · Langkah pertama", "5–7 anos · Primeiros passos", "Tinan 5–7 · Pasu dahuluk")),
    ("primary", (8, 11), L("Ages 8–11 · Primary", "Usia 8–11 · Sekolah dasar", "8–11 anos · Ensino básico", "Tinan 8–11 · Eskola primária")),
    ("middle", (12, 14), L("Ages 12–14 · Pre-secondary", "Usia 12–14 · SMP", "12–14 anos · Pré-secundário", "Tinan 12–14 · Pre-sekundáriu")),
    ("secondary", (15, 18), L("Ages 15–18 · Secondary", "Usia 15–18 · SMA", "15–18 anos · Secundário", "Tinan 15–18 · Sekundáriu")),
    ("university", (19, 25), L("Ages 19–25 · University", "Usia 19–25 · Universitas", "19–25 anos · Universidade", "Tinan 19–25 · Universidade")),
    ("adult", (26, 59), L("Ages 26–59 · Adults", "Usia 26–59 · Dewasa", "26–59 anos · Adultos", "Tinan 26–59 · Adultu")),
    ("senior", (60, 100), L("Ages 60–100 · Seniors", "Usia 60–100 · Lansia", "60–100 anos · Seniores", "Tinan 60–100 · Ferik no katuas")),
]
LEVEL_KEYS = [key for key, _, _ in LEVELS]
ORDER = ["math", "physics", "chemistry", "biology", "medicine", "environment", "astronomy", "atoms", "geography",
         "computers", "it", "technology", "history", "communication", "economics", "agriculture", "civics", "arts"]

def text(value, lang):
    if isinstance(value, dict): return value.get(lang) or value.get("en") or ""
    return value or ""

@dataclass(frozen=True)
class AgeLesson:
    subject: str
    level: str
    title: dict
    points: tuple
    task: dict
    questions: tuple     # (question, answer, (wrong, wrong, wrong))

@dataclass(frozen=True)
class Subject:
    key: str
    icon: str
    name: dict

def _valid_text(value):
    return isinstance(value, dict) and all(isinstance(value.get(lang), str) and value[lang].strip() for lang in LANGS)

def _parse(data):
    """A subject file, or None when it does not follow the format."""
    if not isinstance(data, dict) or not isinstance(data.get("subject"), str) or not _valid_text(data.get("name")): return None
    subject = Subject(data["subject"], str(data.get("icon") or "📘")[:4], data["name"])
    lessons = []
    for item in data.get("lessons") or []:
        if not isinstance(item, dict) or item.get("level") not in LEVEL_KEYS: continue
        if not _valid_text(item.get("title")) or not _valid_text(item.get("task")): continue
        points = tuple(p for p in item.get("points") or [] if _valid_text(p))
        questions = []
        for q in item.get("questions") or []:
            wrong = q.get("wrong") if isinstance(q, dict) else None
            if isinstance(wrong, list) and len(wrong) == 3 and all(map(_valid_text, wrong)) and _valid_text(q.get("q")) and _valid_text(q.get("answer")):
                questions.append((q["q"], q["answer"], tuple(wrong)))
        if points: lessons.append(AgeLesson(subject.key, item["level"], item["title"], points, item["task"], tuple(questions)))
    return subject, lessons

@lru_cache(maxsize=1)
def _load(folder=str(ASSETS)):
    subjects, lessons = {}, []
    for path in sorted(Path(folder).glob("*.json")):
        try: parsed = _parse(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, ValueError): parsed = None
        if parsed:
            subjects[parsed[0].key] = parsed[0]; lessons += parsed[1]
    order = {key: i for i, key in enumerate(ORDER)}
    keys = sorted(subjects, key=lambda k: (order.get(k, len(order)), k))
    lessons.sort(key=lambda l: (order.get(l.subject, len(order)), LEVEL_KEYS.index(l.level)))
    return [subjects[k] for k in keys], lessons

def subjects():
    return _load()[0]

def subject(key):
    return next((s for s in subjects() if s.key == key), None)

def lessons(subject=None, level=None):
    return [l for l in _load()[1] if subject in (None, l.subject) and level in (None, l.level)]

def level_for_age(age):
    """Level key for an age in years (clamped to 5–100)."""
    try: age = max(5, min(100, int(age)))
    except (TypeError, ValueError): return "primary"
    return next(key for key, (low, high), _ in LEVELS if low <= age <= high)

def level_name(level, lang):
    return text(next((name for key, _, name in LEVELS if key == level), level), lang)

def subject_name(key, lang):
    item = subject(key)
    return text(item.name, lang) if item else key

def lesson_text(lesson, lang):
    """A lesson as plain text, used by search and read aloud."""
    lines = [f"{subject_name(lesson.subject, lang)} · {level_name(lesson.level, lang)}", text(lesson.title, lang)]
    lines += ["• " + text(p, lang) for p in lesson.points]
    return "\n".join(lines + ["✎ " + text(lesson.task, lang)])

def questions(subject=None, level=None, lang="en", count=10, rng=None):
    """Multiple-choice questions as classroom.Question objects."""
    from .classroom import Question
    rng = rng or random.Random()
    pool = []
    for lesson in lessons(subject, level):
        for q, answer, wrong in lesson.questions:
            options = [text(answer, lang)] + [text(w, lang) for w in wrong]
            if len(set(options)) < 4: continue
            correct = options[0]; rng.shuffle(options)
            pool.append(Question(text(q, lang), options, correct, lesson.subject))
    rng.shuffle(pool)
    return pool[:count]
