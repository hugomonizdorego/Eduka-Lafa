"""Captures at 150 % scaling (QT_SCALE_FACTOR=1.5) on the smallest supported
window (1024×600 logical, 1536×900 pixels) — run after capture-screenshots.py:
    python3 scripts/capture-scaled.py
"""
import os
os.environ['QT_QPA_PLATFORM'] = os.environ.get('QT_QPA_PLATFORM', 'offscreen'); os.environ['QT_SCALE_FACTOR'] = '1.5'
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from lafa.qt import QApplication, prepare_application
prepare_application()
from lafa.app import Window, STYLE
from lafa.config import Settings
app = QApplication([]); app.setStyle('Fusion'); app.setStyleSheet(STYLE)
out = ROOT / 'docs/screenshots'
def pump():
    for _ in range(6): app.processEvents()
w = Window(Settings(language='id', roots=[]), review=True); w.resize(1024, 600); w.show(); pump()
w.navigate('timor', 'atlas'); w.timor_browser.go({'kind': 'home'}); pump(); w.grab().save(str(out / '83-150pct-timor-leste.png'))
w.timor_browser.open_article('tl.culture.tais'); pump(); w.grab().save(str(out / '84-150pct-article.png'))
w.navigate('study', 'encyclopedia'); w.world_browser.open_article('w.dinosaurs.what_are_dinosaurs', 'explore'); pump(); w.grab().save(str(out / '85-150pct-module.png'))
w.companion.close(); w.close(); print('Saved 3 captures at 150 %.'); os._exit(0)
