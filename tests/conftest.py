"""Shared test setup: really delete Qt widgets between tests.

processEvents() does not run deferred deletes, so windows closed with
deleteLater() would pile up for the whole run and slow every later test."""
import pytest

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
