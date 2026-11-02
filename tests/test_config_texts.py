"""Settings migration and the interface words."""
import json
import re

from lafa.config import Settings
from lafa.desk import texts

def test_old_settings_move_to_the_new_pages(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text(json.dumps({"start_page": "study", "learner_level": "secondary", "text_scale": 115, "language": "tet", "provider": "openrouter"}))
    s = Settings.load(path)
    assert s.start_page == "paths" and s.school_level == "es" and s.text_scale == 115 and s.language == "tet"
    assert (tmp_path / "settings.json.0.1-backup").exists()
    s.save(path); assert Settings.load(path).school_level == "es"

def test_invalid_values_fall_back(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text(json.dumps({"text_scale": 999, "vocab_lang": "xx", "theme": "neon", "school_level": "phd", "card_minutes": -5}))
    s = Settings.load(path)
    assert s.text_scale == 160 and s.vocab_lang == "pt" and s.theme == "auto" and s.school_level == "eb3" and s.card_minutes == 1

def test_interface_languages_are_tetun_and_portuguese(tmp_path, monkeypatch):
    from lafa import config, eduka
    path = tmp_path / "settings.json"
    for old in ("en", "id"):
        path.write_text(json.dumps({"language": old}))
        assert Settings.load(path).language == "system"          # 0.2 choices English/Indonesian follow the system again
    monkeypatch.setattr(eduka, "installed", lambda: False)
    for env, expected in (("pt_PT.UTF-8", "pt"), ("pt_BR.UTF-8", "pt"), ("en_US.UTF-8", "tet"), ("id_ID.UTF-8", "tet"), ("C", "tet")):
        for var in ("LC_ALL", "LC_MESSAGES", "LANGUAGE"): monkeypatch.delenv(var, raising=False)
        monkeypatch.setenv("LANG", env)
        assert config.default_language() == expected, env

def test_every_interface_text_has_tetun_and_portuguese():
    import lafa.app  # noqa: F401  (loads every page's words)
    from lafa.desk.pages import MODULES, page_class
    for route in MODULES: page_class(route)
    import lafa.assistant, lafa.tips  # noqa: F401,E401
    for key, row in texts.T.items():
        assert len(row) == 2 and all(isinstance(v, str) and v.strip() for v in row), key

def test_tetun_interface_words():
    import lafa.app, lafa.assistant  # noqa: F401,E401
    from lafa.desk.pages import MODULES, page_class
    for route in MODULES: page_class(route)
    bad = re.compile(r"\b(dan|yang|untuk|sudah|tetapi|dengan|adalah|fatus|fontes)\b", re.I)
    for key, row in texts.T.items():
        assert not bad.search(row[0]), (key, row[0])
    assert texts.t("tet", "back") == "Fila" and texts.t("pt", "back") == "Voltar" and texts.t("xx", "back") == "Fila"
    assert texts.t("tet", "my_progress") == "Ha’u-nia progresu"      # Tetun is shown with the typographic apostrophe
