"""Single Qt import point for LAFA.

Edukasaun OS (Debian 13) and the Eduka-Desktop suite use PyQt5, so the Debian
package depends on python3-pyqt5 and LAFA runs on it. Developers may use
PySide6 (pip). Choose explicitly with LAFA_QT=pyqt5 or LAFA_QT=pyside6;
otherwise PyQt5 is tried first, then PySide6. Every LAFA module imports Qt
names from here, never from a binding directly, so both bindings stay working.
"""
import os

_choice = os.environ.get("LAFA_QT", "").strip().casefold()
_order = {"pyqt5": ["PyQt5"], "pyside6": ["PySide6"]}.get(_choice, ["PyQt5", "PySide6"])
BINDING = None
for _name in _order:
    try:
        if _name == "PyQt5":
            from PyQt5.QtCore import *  # noqa: F401,F403
            from PyQt5.QtGui import *  # noqa: F401,F403
            from PyQt5.QtWidgets import *  # noqa: F401,F403
            from PyQt5.QtNetwork import QLocalServer, QLocalSocket  # noqa: F401
            from PyQt5.QtCore import pyqtSignal as Signal, pyqtSlot as Slot  # noqa: F401
            QT_MAJOR = 5
        else:
            from PySide6.QtCore import *  # noqa: F401,F403
            from PySide6.QtGui import *  # noqa: F401,F403
            from PySide6.QtWidgets import *  # noqa: F401,F403
            from PySide6.QtNetwork import QLocalServer, QLocalSocket  # noqa: F401
            from PySide6.QtCore import Signal, Slot  # noqa: F401
            QT_MAJOR = 6
        BINDING = _name
        break
    except ImportError:
        continue
if BINDING is None:
    raise ImportError("LAFA needs PyQt5 (Debian: apt install python3-pyqt5) or PySide6 (pip install PySide6).")

if BINDING == "PyQt5":
    import sys as _sys
    import traceback as _traceback
    if _sys.excepthook is _sys.__excepthook__:
        # PyQt5 aborts the whole process on an exception inside a Qt virtual or
        # slot unless an excepthook is set. LAFA logs it and keeps running.
        def _log_exception(kind, value, tb):
            _traceback.print_exception(kind, value, tb)
        _sys.excepthook = _log_exception

def global_point(event):
    """Global cursor position of a mouse event as an integer QPoint (Qt5 and Qt6)."""
    return event.globalPosition().toPoint() if hasattr(event, "globalPosition") else event.globalPos()

def run(obj):
    """exec() for dialogs, menus and the application on both bindings."""
    method = getattr(obj, "exec", None) or getattr(obj, "exec_")
    return method()

def started(result):
    """QProcess.startDetached returns bool (PyQt5) or (bool, pid) (PySide6)."""
    return result[0] if isinstance(result, tuple) else bool(result)

def prepare_application():
    """Call before creating QApplication: sharp text on high-DPI school screens."""
    if QT_MAJOR == 5:
        QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)  # noqa: F405
        QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)  # noqa: F405
