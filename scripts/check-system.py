#!/usr/bin/env python3
"""Read-only LAFA readiness checks, with no folder paths or personal data.

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
    bindings=[name for name in ('PyQt5','PySide6') if importlib.util.find_spec(name) is not None]
    qt_available=bool(bindings)
    add('Qt dependency','pass' if qt_available else 'fail',' + '.join(bindings)+' available' if qt_available else 'Install python3-pyqt5 (Debian) or PySide6')
    if qt_available:
        try:
            result=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--qt-probe'],capture_output=True,text=True,timeout=12,check=False)
            if result.returncode:raise RuntimeError()
            detail=json.loads(result.stdout)
            add('Character assets','pass',f"{detail['activities']} activity poses; {detail['traditional']} traditional poses")
            add('Panel movement','pass' if detail['backend']=='xcb' else 'warning','X11 movement available' if detail['backend']=='xcb' else 'Offscreen/Wayland needs target placement testing')
        except (RuntimeError,ValueError,KeyError,OSError,subprocess.TimeoutExpired):add('Qt rendering','fail','Qt initialization failed in an isolated probe; check display and runtime dependencies')
    for name,command in [('Read aloud','espeak-ng')]:
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
    from lafa.kb import KnowledgeBase
    base=KnowledgeBase();stats=base.stats()
    add('Encyclopedia content','pass' if stats['articles'] else 'fail',f"{stats['articles']} articles, {stats['places']} places, {stats['days']} days, {stats['words']} words, {stats['questions']} quiz questions")
    if network:
        from lafa import sync
        for name,operation in [('Wikipedia',lambda:sync.wiki_intros('en',['Timor-Leste'])),('World Bank',lambda:sync.net.json_request('https://api.worldbank.org/v2/country/TLS?format=json',timeout=20)),
                               ('Lafa content updates',lambda:sync.check_updates(Path(sync.__file__).parent/'assets'/'timor',Path(tempfile.gettempdir())/'lafa-check-updates'))]:
            try:operation();add(name,'pass','Public request completed; no account or key used')
            except Exception:add(name,'warning','Public request failed; check internet/service availability')
    return {'lafa_version':__version__,'network_requested':network,'checks':results,'private_data_included':False}


def qt_probe():
    if not os.environ.get('DISPLAY') and not os.environ.get('WAYLAND_DISPLAY'):os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
    from lafa.qt import QApplication
    from lafa.qt import QGuiApplication
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
