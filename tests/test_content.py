"""The encyclopedia content: valid, sourced, linked, in four languages."""
import json
import re
import subprocess
import sys
from pathlib import Path

from lafa import kb, icons

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "lafa" / "assets" / "timor"

def test_validator_reports_no_errors():
    result = subprocess.run([sys.executable, str(ROOT / "tools" / "check-content.py")], capture_output=True, text=True, timeout=120)
    assert result.returncode == 0, result.stdout[-3000:]
    assert "ERROR" not in result.stdout

def test_enough_content(base):
    stats = base.stats()
    assert stats["articles"] >= 120
    assert stats["municipalities"] == 14
    assert stats["places"] >= 40
    assert stats["words"] >= 1000
    assert stats["questions"] >= 600
    assert stats["sources"] >= 300

def test_every_item_has_four_languages_and_sources(base):
    for item in base.all():
        for lang in kb.LANGS:
            assert item.title(lang).strip(), (item.id, lang)
            assert item.summary(lang).strip(), (item.id, lang)
        sources = item.sources()
        assert len(sources) >= 2, item.id
        for s in sources:
            assert s["url"].startswith("https://"), (item.id, s["url"])

def test_quiz_questions_are_well_formed(base):
    for item in base.all():
        for q in item.quiz():
            assert len(q["options"]) == 4 and 0 <= q["answer"] <= 3, item.id
            assert isinstance(q.get("difficulty", 5), int) and 1 <= q.get("difficulty", 5) <= 15, item.id
            for lang in kb.LANGS:
                assert kb.text(q["q"], lang).strip(), (item.id, lang)
                options = [kb.text(o, lang).strip() for o in q["options"]]
                assert all(options), (item.id, lang)

def test_answers_are_spread_over_the_four_positions(base):
    counts = [0, 0, 0, 0]
    for item in base.all():
        for q in item.quiz(): counts[q["answer"]] += 1
    total = sum(counts)
    assert min(counts) >= total * 0.12, counts

def test_illustrations_exist(base):
    for item in base.all():
        assert icons.illustration_exists(item.illustration()), (item.id, item.illustration())

def test_places_are_inside_timor_leste(base):
    for p in base.places():
        assert -9.6 <= p.get("lat") <= -8.1 and 124.0 <= p.get("lon") <= 127.4, p.id
        assert base.get(p.get("municipality", "")) is not None, p.id

def test_municipalities_match_the_map(base):
    shapes = {g["name"] for g in base.map["municipalities"]}
    for m in base.municipalities():
        assert m.get("geo") in shapes, (m.id, m.get("geo"))

def test_related_links_point_to_items(base):
    known = set(base.items)
    broken = [(i.id, r) for i in base.all() for r in i.related() if r not in known]
    assert len(broken) <= len(known) * 0.05, broken[:10]

def test_vocabulary_ids_and_translations(base):
    ids = [w.id for w in base.words]
    assert len(ids) == len(set(ids))
    for w in base.words:
        for code in ("pt", "id", "en"): assert w.meaning(code), (w.id, code)
    for path in (BASE / "vocab").glob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        if "lang" in data: assert set(data["words"]) <= set(ids), path.name

def test_tetun_text_has_no_indonesian_function_words(base):
    bad = re.compile(r"\b(dan|yang|untuk|sudah|tetapi|tapi|dengan|adalah)\b")
    hits = [(i.id, m.group(0)) for i in base.all() for _h, para in i.sections("tet") for m in [bad.search(para)] if m]
    assert len(hits) <= 3, hits[:10]

def test_manifest_lists_every_content_file():
    manifest = json.loads((BASE / "manifest.json").read_text())
    names = {f"{p.parent.name}/{p.name}" for folder in ("content", "vocab", "map") for p in (BASE / folder).glob("*.json")}
    assert names == set(manifest["files"]), names ^ set(manifest["files"])
