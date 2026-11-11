"""The history game (logic and page) and the State institutions catalog."""
import random

import pytest

from lafa import kb
from lafa.desk.pages.history_game import HistoryGame, LEVELS, MODES
from tests.test_ui import pump, window, close, errors  # noqa: F401  (fixtures and helpers)


@pytest.fixture(scope="module")
def events():
    return kb.shared().timeline("tet")


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("level", list(LEVELS))
def test_every_game_can_be_played_to_the_end(events, mode, level):
    g = HistoryGame(events, mode, level, rng=random.Random(7))
    assert g.can_play()
    titles = []
    while not g.finished():
        q = g.next_question()
        assert q is not None and len({e["title"] for e in q["events"]}) == len(q["events"])
        titles += [e["title"] for e in q["events"]]
        keys = [e["key"] for e in q["events"]]
        if mode == "first":
            assert keys[q["answer"]] == min(keys) and len(set(keys)) == 2
            if level == "easy": assert abs(keys[0][0] - keys[1][0]) >= 50
        elif mode == "order":
            assert [keys[i] for i in q["answer"]] == sorted(keys) and len(set(keys)) == 4
        else:
            assert len(set(q["options"])) == 4 and q["options"][q["answer"]] == keys[0][0] and keys[0][0] >= 1500
        g.answer(q["answer"])
    assert g.score == g.rounds and g.best_streak == g.rounds and g.points() > g.rounds * 10
    assert len(titles) == len(set(titles)), "an event came back in the same game"


def test_wrong_answers_break_the_streak(events):
    g = HistoryGame(events, "first", "medium", rng=random.Random(3))
    q = g.next_question(); assert g.answer(q["answer"]) is True and g.streak == 1
    q = g.next_question(); assert g.answer(1 - q["answer"]) is False and g.streak == 0 and g.score == 1
    assert g.answer(q["answer"]) is False          # a second answer to the same question is ignored
    with pytest.raises(ValueError): HistoryGame(events, "chess")


def test_history_game_and_institutions_pages(qapp, errors):
    w = window(qapp)
    w.open("history_game", mode="order", level="easy"); pump(qapp)
    page = w.pages["history_game"]; page.start(); pump(qapp)
    q = page.game.question
    for i in q["answer"]: page.toggle_order(i)
    page.check_order(); pump(qapp); assert page.game.last_correct is True
    while not page.game.finished():
        page.advance(); pump(qapp)
        if page.game.finished(): break
        for i in page.game.question["answer"]: page.toggle_order(i)
        page.check_order()
    page.advance(); pump(qapp)
    assert w.progress.result("game.history.order.easy")["best"] == 10
    w.open("history_game", mode="year", level="hard"); pump(qapp); page.start(); page.choose(page.game.question["answer"]); pump(qapp)
    assert page.game.score == 1
    w.open("institutions"); pump(qapp)
    texts = " ".join(lbl.text() for lbl in w.pages["institutions"].findChildren(type(w.brand_name)))
    assert "Prezidente Repúblika" in texts and "Parlamentu Nasionál" in texts
    for lang in ("pt", "en", "id"):
        w.settings = w.settings.__class__(**{**w.settings.__dict__, "language": lang}); w.rebuild(); pump(qapp)
        w.open("institutions"); w.open("history_game"); pump(qapp)
    assert not errors
    close(w)
