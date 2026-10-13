"""Shared test setup: really delete Qt widgets between tests.

processEvents() does not run deferred deletes, so windows closed with
deleteLater() would pile up for the whole run and slow every later test."""
import os
import pytest

# Web views start a Chromium process; tests check the AI Hub without them
# unless LAFA_NO_WEBENGINE=0 is set.
os.environ.setdefault("LAFA_NO_WEBENGINE", "1")

@pytest.fixture(autouse=True)
def private_memory(tmp_path, monkeypatch):
    """LAFA's memory and AI Hub profile go to a temporary folder in tests."""
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
    from lafa import memory
    memory._shared = None
    yield
    memory._shared = None

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
