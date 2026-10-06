#!/usr/bin/env python3
"""Read-only LAFA readiness checks, with no secrets, folder paths or chat output.

--network explicitly checks public services. The default check is local only.
JSON output is suitable for a GitHub issue without exposing private paths.
"""
import argparse
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import platform
import shutil
import socket
import subprocess
import sys
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from lafa import __version__
from lafa.config import Settings


def checks(network=False):
    results=[]
    def add(name,status,detail):results.append({'check':name,'status':status,'detail':detail})
    add('Python','pass' if sys.version_info>=(3,11) else 'fail',platform.python_version())
    add('Platform','pass' if sys.platform.startswith('linux') else 'warning',platform.system())
    qt_available=importlib.util.find_spec('PySide6') is not None
    add('Qt dependency','pass' if qt_available else 'fail','PySide6 available' if qt_available else 'Install project dependencies')
    if qt_available:
        try:
            result=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--qt-probe'],capture_output=True,text=True,timeout=12,check=False)
            if result.returncode:raise RuntimeError()
            detail=json.loads(result.stdout)
            add('Character assets','pass',f"{detail['activities']} activity poses; {detail['traditional']} traditional poses")
            add('Panel movement','pass' if detail['backend']=='xcb' else 'warning','X11 movement available' if detail['backend']=='xcb' else 'Offscreen/Wayland needs target placement testing')
        except (RuntimeError,ValueError,KeyError,OSError,subprocess.TimeoutExpired):add('Qt rendering','fail','Qt initialization failed in an isolated probe; check display and runtime dependencies')
    for name,command in [('PDF reading','pdftotext'),('Read aloud','espeak-ng'),('Microphone recording','arecord')]:
        present=bool(shutil.which(command));add(name,'pass' if present else 'warning',command+' available' if present else 'Optional command missing: '+command)
    try:
        with tempfile.TemporaryDirectory(prefix='lafa-ipc-check-') as folder:
            with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as peer:peer.bind(str(Path(folder)/'probe.sock'));peer.listen(1)
        add('Local activation','pass','AF_UNIX binding available')
    except (OSError,AttributeError):add('Local activation','warning','Local sockets unavailable in this environment; test on Edukasaun OS')
    settings=Settings.load();add('Preferences','pass',f'Language: {settings.locale}; virtual enabled: {settings.companion}; selected folders: {len(settings.roots)}')
    data=Path(os.environ.get('XDG_DATA_HOME',str(Path.home()/'.local/share')))
    for name,filename in [('Desktop launcher','lafa-desktop.desktop'),('Settings launcher','lafa-settings.desktop')]:
        installed=(data/'applications'/filename).is_file();add(name,'pass' if installed else 'warning','Installed' if installed else 'Run scripts/install-user.sh from a stable source location')
    if network:
        from lafa.tools import encyclopedia_search
        from lafa.timor import timor_news
        from lafa.live_info import forecast,Location
        for name,operation in [('Wikipedia',lambda:encyclopedia_search('Dili','en')),('Dili weather',lambda:forecast(Location('Dili',-8.5586,125.5736,'Asia/Dili'))),('Timor-Leste feeds',timor_news)]:
            try:operation();add(name,'pass','Public request completed; no AI credentials used')
            except Exception:add(name,'warning','Public request failed; check internet/service availability')
    return {'lafa_version':__version__,'network_requested':network,'checks':results,'private_data_included':False}


def qt_probe():
    if not os.environ.get('DISPLAY') and not os.environ.get('WAYLAND_DISPLAY'):os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
    from PySide6.QtWidgets import QApplication
    from PySide6.QtGui import QGuiApplication
    from lafa.mascot import Atlas
    app=QApplication([]);atlas=Atlas()
    print(json.dumps({'activities':len(atlas.poses),'traditional':len(atlas.traditional),'backend':QGuiApplication.platformName()}));return 0


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--qt-probe',action='store_true',help=argparse.SUPPRESS);parser.add_argument('--network',action='store_true');parser.add_argument('--json',action='store_true');args=parser.parse_args()
    if args.qt_probe:return qt_probe()
    report=checks(args.network)
    if args.json:print(json.dumps(report,indent=2))
    else:
        print('LAFA '+__version__+' readiness check')
        for item in report['checks']:print(f"{item['status'].upper():7} {item['check']}: {item['detail']}")
    return 1 if any(item['status']=='fail' for item in report['checks']) else 0

if __name__=='__main__':raise SystemExit(main())
