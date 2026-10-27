"""Shared test setup.

* Lafa's settings, progress and downloads go to a temporary folder.
* Qt widgets are really deleted between tests (processEvents() does not run
  deferred deletes, so closed windows would pile up and slow later tests).
"""
import os
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

@pytest.fixture(autouse=True)
def private_folders(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    yield

@pytest.fixture(autouse=True)
def flush_deleted_widgets():
    yield
    try:
        from lafa.qt import QApplication, QEvent
    except ImportError:
        return
    app = QApplication.instance()
    if app is not None:
        app.sendPostedEvents(None, QEvent.DeferredDelete); app.processEvents()

@pytest.fixture(scope="session")
def qapp():
    from lafa.qt import QApplication
    app = QApplication.instance() or QApplication([])
    app.setStyle("Fusion")
    from lafa.desk import theme
    theme.load_fonts(); app.setFont(theme.app_font())
    return app

@pytest.fixture(scope="session")
def base():
    from lafa.kb import KnowledgeBase
    return KnowledgeBase()
