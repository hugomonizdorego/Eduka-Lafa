#!/usr/bin/env python3
"""Working native Qt integration test host; not the installed Eduka-Settings app.

Normal mode uses the installed LAFA launcher. --review disables launch controls
and uses temporary preferences, so rendering never modifies the user's settings.
"""
import argparse
import os
from pathlib import Path
import sys
import tempfile
import importlib
BINDING=os.environ.get('LAFA_QT_HOST','PyQt5')
try:importlib.import_module(BINDING)
except ImportError:BINDING='PySide6'
_w=importlib.import_module(BINDING+'.QtWidgets')
QApplication,QWidget,QHBoxLayout,QVBoxLayout,QListWidget,QStackedWidget,QLabel=(_w.QApplication,_w.QWidget,_w.QHBoxLayout,_w.QVBoxLayout,_w.QListWidget,_w.QStackedWidget,_w.QLabel)
from eduka_lafa_settings import create_lafa_page


def build_host(review=False):
    window=QWidget();window.setWindowTitle('LAFA · native settings integration test host');window.resize(1000,860)
    root=QVBoxLayout(window);notice=QLabel('INTEGRATION TEST HOST · native Qt widgets · not the current Eduka-Settings application');notice.setWordWrap(True);root.addWidget(notice)
    row=QHBoxLayout();menu=QListWidget();menu.addItems(['General','LAFA']);menu.setFixedWidth(180);row.addWidget(menu)
    stack=QStackedWidget();general=QLabel('Register the LAFA factory as a dedicated page in the target settings menu.');general.setWordWrap(True);stack.addWidget(general)
    page=create_lafa_page(binding=BINDING);stack.addWidget(page);row.addWidget(stack,1);root.addLayout(row,1)
    menu.currentRowChanged.connect(stack.setCurrentIndex);menu.setCurrentRow(1)
    if review:
        for button in page.findChildren(QWidget):
            if button.inherits('QAbstractButton'):button.setEnabled(False)
        root.addWidget(QLabel('REVIEW: launching is disabled; temporary preferences are used.'))
    window.lafa_page=page;return window


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--review',action='store_true');args=parser.parse_args()
    temporary=tempfile.TemporaryDirectory(prefix='lafa-host-review-') if args.review else None
    if temporary:os.environ['XDG_CONFIG_HOME']=temporary.name
    app=QApplication(sys.argv);app.setStyle('Fusion');window=build_host(args.review);window.show();result=(app.exec_() if hasattr(app,'exec_') else app.exec())
    if temporary:temporary.cleanup()
    return result

if __name__=='__main__':raise SystemExit(main())
