"""The Constitution reader, the national anthem with timed lyrics and the audio player."""
import pytest

from lafa import anthem, constitution
from lafa.audio import Player, external_command
from tests.test_ui import pump, window, close, errors  # noqa: F401  (fixtures and helpers)

def test_constitution_has_every_article_in_both_languages():
    con = constitution.load()
    assert [a["n"] for a in con.articles] == list(range(1, 171))
    assert con.stats()["parts"] == 7 and len(con.preamble("tet")) == len(con.preamble("pt")) >= 10
    for a in con.articles:
        for lang in ("tet", "pt"):
            assert con.article_title(a, lang), (a["n"], lang)
            assert con.blocks(a, lang) and all(b["text"] or b["items"] for b in con.blocks(a, lang)), (a["n"], lang)
    assert "bandeira" in con.plain(con.article(15), "tet").lower() and con.plain(con.article(15), "pt").startswith("Artigo 15.º")

@pytest.mark.parametrize("query,expected", [("15", 15), ("art. 15", 15), ("Artigu 59", 59), ("artigo 166.º", 166), ("a13", 13), ("171", None), ("Timor", None)])
def test_article_references(query, expected):
    assert constitution.parse_ref(query) == expected

@pytest.mark.parametrize("query,lang,first", [("bandeira", "tet", 15), ("línguas oficiais", "pt", 13), ("lian ofisial", "tet", 13), ("Provedor", "pt", 27),
                                              ('"liberdade de imprensa"', "pt", 41), ("hino", "pt", 166), ("edukasaun", "tet", 59)])
def test_constitution_search(query, lang, first):
    found = constitution.load().search(query, lang)
    assert found and found[0][0]["n"] == first, [a["n"] for a, _s, _x in found[:5]]

def test_search_highlight_ignores_accents_but_not_word_parts():
    pattern = constitution.highlight_pattern(["lingua", "de"])
    assert pattern.search("Línguas oficiais") and not pattern.search("compreende")

def test_anthem_cues_are_ordered_and_inside_the_recording():
    data = anthem.load()
    assert len(data["lines"]) == 12 and data["lines"][0]["pt"].startswith("Pátria, Pátria")
    cues = data["cues"]; ends = [c[1] for c in cues]
    assert all(a[1] <= b[0] for a, b in zip(cues, cues[1:])) and max(ends) <= data["duration"]
    assert anthem.at(data, 5.0) == (None, 0.0, "intro") and anthem.at(data, 110.0)[2] == "interlude"
    line, progress, section = anthem.at(data, 30.0); assert line == 1 and 0 < progress < 1 and section is None
    assert anthem.next_time(data, 2, 60.0) == 166.4 and anthem.clock(204.4) == "3:24"

def test_player_without_backend_reports_it(qapp):
    p = Player(anthem.load()["path"], 204.4, backend="none"); seen = []
    p.failed.connect(seen.append); p.play()
    assert not p.available and seen == ["no-audio"] and p.state == "stopped"
    p.seek(30.0); assert p.position() == 30.0

def test_external_player_command_starts_at_the_position(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda name: "/usr/bin/" + name if name == "mpv" else None)
    assert external_command("/tmp/a.mp3", 12.5)[:4] == ["mpv", "--no-video", "--really-quiet", "--start=12.50"]
    monkeypatch.setattr("shutil.which", lambda name: None)
    assert external_command("/tmp/a.mp3") is None

def test_constitution_and_symbols_pages(qapp, errors):
    w = window(qapp)
    w.open("constitution", article=14); pump(qapp)
    page = w.pages["constitution"]; assert page.current == 14 and "14" in page.crumb.text() + page.text.toPlainText()
    page.search.setText("edukasaun"); page.run_search(); pump(qapp)
    assert page.results.count() >= 1 and page.current == 59
    page.lang_switch.select("both", emit=True); page.show_preamble(); page.step(1); pump(qapp)
    page.copy(); assert "Artigu" in qapp.clipboard().text() or "Artigo" in qapp.clipboard().text()
    w.open("search", q="Provedor"); pump(qapp)
    w.open("symbols"); pump(qapp)
    sym = w.pages["symbols"]; sym.on_position(58.0)
    assert sym.karaoke.text.startswith("Glória") and sym.current_line == 3
    sym.on_position(5.0); assert sym.current_line is None
    assert not errors, errors
    close(w)

def test_article_text_links_constitution_references(qapp):
    from lafa.desk.pages.article import link_constitution
    linked = link_constitution("O artigo 15.º da Constituição descreve a bandeira.")
    assert "href='lafa://constitution/15'" in linked
    assert link_constitution("Lei n.º 10/2005, artigo 3, fixa os feriados.") == "Lei n.º 10/2005, artigo 3, fixa os feriados."
    assert "constitution/200" not in link_constitution("Konstituisaun no artigu 200.")
