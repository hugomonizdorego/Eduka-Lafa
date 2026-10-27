"""Offline store and online updates, with the network replaced by fakes."""
import hashlib
import json

import pytest

from lafa import sync, net
from lafa.kb import KnowledgeBase
from lafa.store import Store

JPEG = b"\xff\xd8\xff\xe0" + b"0" * 100

def test_store_keeps_texts_and_photos(tmp_path):
    store = Store(tmp_path)
    store.put_extract("tl.symbols.flag", "en", "Flag of Timor-Leste", "The flag…", "https://en.wikipedia.org/wiki/Flag_of_East_Timor")
    assert store.extract("tl.symbols.flag", "en")["text"] == "The flag…"
    store.put_extract("x", "en", "t", "text", "http://insecure.example")          # not https: ignored
    assert store.extract("x", "en") is None
    path = store.put_photo("tl.symbols.flag", JPEG, "jpg", {"author": "A. Person", "licence": "CC BY-SA 4.0", "source_url": "https://commons.wikimedia.org/wiki/File:X.jpg"})
    assert path.is_file() and store.photo("tl.symbols.flag")[1]["licence"] == "CC BY-SA 4.0"
    assert store.stats()["photos"] == 1
    store.clear()
    assert store.photo("tl.symbols.flag") is None and store.stats()["extracts"] == 0

def test_free_licences_only():
    meta = lambda name, nonfree="": {"LicenseShortName": {"value": name}, "NonFree": {"value": nonfree}}
    for ok in ("CC BY-SA 4.0", "CC BY 2.0", "CC0", "Public domain", "CC BY-SA 3.0 IGO"): assert sync.free_licence(meta(ok)), ok
    for bad in ("Fair use", "All rights reserved", "CC BY-NC 4.0", "CC BY-ND 4.0"): assert not sync.free_licence(meta(bad)), bad
    assert not sync.free_licence(meta("CC BY 4.0", "true"))

def test_wiki_intros_follow_normalised_and_redirected_titles(monkeypatch):
    answer = {"query": {"normalized": [{"from": "East_Timor", "to": "East Timor"}], "redirects": [{"from": "East Timor", "to": "Timor-Leste"}],
                        "pages": [{"title": "Timor-Leste", "extract": "Timor-Leste is…", "fullurl": "https://en.wikipedia.org/wiki/Timor-Leste", "pageimage": "Flag.svg"}]}}
    monkeypatch.setattr(net, "json_request", lambda url, **kw: answer)
    found = sync.wiki_intros("en", ["East_Timor"])
    assert found["East_Timor"]["title"] == "Timor-Leste" and found["East_Timor"]["image"] == "Flag.svg"

def test_download_offline_end_to_end(monkeypatch, tmp_path, base):
    def fake_json(url, **kw):
        if "commons.wikimedia.org" in url:
            return {"query": {"pages": [{"imageinfo": [{"thumburl": "https://upload.wikimedia.org/x.jpg", "descriptionurl": "https://commons.wikimedia.org/wiki/File:X.jpg",
                    "extmetadata": {"LicenseShortName": {"value": "CC BY-SA 4.0"}, "Artist": {"value": "<a>Someone</a>"}}}]}]}}
        titles = url.split("titles=")[1]
        from urllib.parse import unquote_plus
        pages = [{"title": t, "extract": f"Intro of {t}", "fullurl": "https://en.wikipedia.org/wiki/X", "pageimage": "X.jpg"} for t in unquote_plus(titles).split("|")]
        return {"query": {"pages": pages}}
    monkeypatch.setattr(net, "json_request", fake_json)
    monkeypatch.setattr(net, "request", lambda url, **kw: JPEG)
    monkeypatch.setattr(sync.time, "sleep", lambda s: None)
    store = Store(tmp_path); seen = []
    result = sync.download_offline(base, store, langs=("en",), progress=lambda d, n, t="": seen.append(d))
    assert result["texts"] > 50 and result["pictures"] > 20 and not result["errors"]
    item = next(i for i in base.all() if i.wiki().get("en"))
    assert store.extract(item.id, "en")["text"].startswith("Intro of")
    assert store.photo(item.id)[1]["author"] == "Someone"

def test_content_updates_are_verified(monkeypatch, tmp_path):
    good = json.dumps({"articles": []}).encode(); bad = b"<html>oops</html>"
    files = {"content/new.json": {"sha256": hashlib.sha256(good).hexdigest(), "size": len(good)},
             "content/bad.json": {"sha256": hashlib.sha256(bad).hexdigest(), "size": len(bad)},
             "../../etc/passwd": {"sha256": "0" * 64, "size": 1}}
    monkeypatch.setattr(net, "json_request", lambda url, **kw: {"content_version": "2099.01.01", "files": files})
    remote = sync.check_updates(tmp_path / "base", tmp_path / "updates", "2026.10.27")
    assert remote["newer"] and {p for p, _ in remote["changed"]} == {"content/new.json", "content/bad.json"}
    monkeypatch.setattr(net, "request", lambda url, **kw: good if url.endswith("new.json") else bad)
    result = sync.apply_updates(tmp_path / "base", tmp_path / "updates", remote["changed"])
    assert result["saved"] == ["content/new.json"] and (tmp_path / "updates" / "content" / "new.json").is_file()
    assert not (tmp_path / "updates" / "content" / "bad.json").exists()

def test_world_bank_indicators(monkeypatch, tmp_path, base):
    answer = [{"page": 1}, [{"date": "2023", "value": 1400000, "indicator": {"value": "Population, total"}}, {"date": "2022", "value": 1341737}, {"date": "2021", "value": None}]]
    monkeypatch.setattr(net, "json_request", lambda url, **kw: answer)
    result = sync.update_indicators(base, tmp_path)
    data = json.loads((tmp_path / "content" / "indicators.json").read_text())
    assert result["indicators"] >= 6 and data["indicators"][0]["series"] == [[2022, 1341737.0], [2023, 1400000.0]]
    assert KnowledgeBase(overrides=tmp_path).indicators[0]["licence"] == "CC BY 4.0"

def test_manifest_matches_files():
    from lafa.kb import ASSETS
    manifest = sync.make_manifest(ASSETS, "test")
    assert all(sync.ALLOWED_UPDATE.match(p) for p in manifest["files"])
