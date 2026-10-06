"""Create separate Desktop, settings and hidden virtual-role entries."""
from pathlib import Path
import json
import os
import shutil
import sys
from PySide6.QtWidgets import QApplication
from lafa.mascot import Atlas
from lafa.desktop_entry import exec_path

app=QApplication([])
exe=Path(sys.argv[1]).resolve()
if not exe.is_file():raise SystemExit('Installed LAFA executable not found.')
data=Path(os.environ.get('XDG_DATA_HOME',str(Path.home()/'.local/share')))
icon=data/'icons/hicolor/128x128/apps/lafa.png';icon.parent.mkdir(parents=True,exist_ok=True)
if not Atlas().pixmap('idle',128,'traditional').save(str(icon)):raise SystemExit('Could not save LAFA icon.')
applications=data/'applications';applications.mkdir(parents=True,exist_ok=True)
quoted=exec_path(exe)
entries=[
 ('lafa-desktop.desktop','LAFA Desktop','--window','Education;Utility;X-Edukasaun;',''),
 ('lafa-settings.desktop','LAFA Settings','--settings','Settings;DesktopSettings;X-Eduka-Settings;','X-Eduka-Settings-Page=LAFA\n'),
 ('lafa-virtual.desktop','LAFA Virtual Assistant','--virtual','Utility;','NoDisplay=true\n'),
]
for filename,name,role,categories,extra in entries:
    text=f'''[Desktop Entry]
Type=Application
Name={name}
Comment=Learning and virtual assistance from Timor-Leste
Exec={quoted} {role}
Icon=lafa
Terminal=false
Categories={categories}
StartupNotify=true
{extra}'''
    (applications/filename).write_text(text,encoding='utf-8')
legacy=applications/'lafa.desktop'
if legacy.is_file() and 'Icon=lafa' in legacy.read_text():legacy.unlink()
plugin=data/'eduka-settings/lafa';plugin.mkdir(parents=True,exist_ok=True)
(plugin/'launcher.json').write_text(json.dumps({'executable':str(exe)}),encoding='utf-8')
for name in ['eduka_lafa_settings.py','lafa-page.json']:
    shutil.copyfile(Path(__file__).resolve().parents[1]/'integration'/name,plugin/name)
print('Created LAFA Desktop and LAFA Settings launchers. The native settings hook is available for host integration.')
