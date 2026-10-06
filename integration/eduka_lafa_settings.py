"""Native LAFA page for PyQt5, PyQt6 or PySide6 host settings applications.

Use the host's binding. This module does not import LAFA's Qt client. Launch
roles are fixed and settings state is checked after a detached activation.
"""
import importlib
import json
import os
from pathlib import Path
import sys
import stat
import time

BINDINGS={'PyQt5','PyQt6','PySide6'}
TEXT={
'en':('Activate LAFA Virtual Assistant in Eduka-Desktop','Open LAFA Desktop','LAFA settings','Activating LAFA…','Deactivating LAFA…','LAFA could not start. Check the installed executable.','The change was not applied. Open LAFA settings and try again.','The character appears when internet is available. Desktop and Virtual Assistant are separate.'),
'id':('Aktifkan LAFA Virtual Assistant di Eduka-Desktop','Buka LAFA Desktop','Pengaturan LAFA','Mengaktifkan LAFA…','Menonaktifkan LAFA…','LAFA tidak dapat dibuka. Periksa executable terpasang.','Perubahan belum diterapkan. Buka pengaturan LAFA dan coba lagi.','Karakter muncul saat internet tersedia. Desktop dan Asisten Virtual terpisah.'),
'pt':('Ativar o Assistente Virtual LAFA no Eduka-Desktop','Abrir LAFA Desktop','Definições LAFA','A ativar LAFA…','A desativar LAFA…','Não foi possível iniciar LAFA. Verifique o executável instalado.','A alteração não foi aplicada. Abra as definições LAFA e tente novamente.','A personagem aparece quando há internet. Desktop e Assistente Virtual são separados.'),
 'tet':('Ativa Asistente Virtuál LAFA iha Eduka-Desktop','Loke LAFA Desktop','Konfigurasaun LAFA','Ativa LAFA hela…','Desativa LAFA hela…','La bele loke LAFA. Verifika executable instaladu.','Mudansa seidauk aplika. Loke konfigurasaun LAFA no koko fali.','Karakter mosu bainhira internet disponivel. Desktop no Asistente Virtuál ketak.'),
}


def locations():
    config=Path(os.environ.get('XDG_CONFIG_HOME',str(Path.home()/'.config')))/'lafa/settings.json'
    data=Path(os.environ.get('XDG_DATA_HOME',str(Path.home()/'.local/share')))
    return config,data/'eduka-settings/lafa/launcher.json'


def read_regular(path,limit):
    fd=os.open(path,os.O_RDONLY|os.O_NONBLOCK|getattr(os,'O_NOFOLLOW',0))
    with os.fdopen(fd,'rb') as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):return b'{}'
        return stream.read(limit+1)


def preferences():
    try:
        raw=read_regular(locations()[0],65536)
        value=json.loads(raw) if len(raw)<=65536 else {}
        return value if isinstance(value,dict) else {}
    except (OSError,ValueError):return {}


def enabled():return preferences().get('companion') is True


def launch_command():
    try:
        raw=read_regular(locations()[1],4096)
        command=json.loads(raw)['executable'] if len(raw)<=4096 else None
        if isinstance(command,str) and '\x00' not in command and Path(command).is_absolute() and Path(command).is_file():return [command]
    except (OSError,ValueError,KeyError,TypeError):pass
    return ['lafa']


def language():
    selected=preferences().get('language','system')
    if not isinstance(selected,str) or selected not in {'system','en','id','pt','tet'}:selected='system'
    raw=os.environ.get('LC_ALL') or os.environ.get('LC_MESSAGES') or os.environ.get('LANGUAGE') or os.environ.get('LANG','en')
    code=raw.replace('-','_').split(':')[0].split('_')[0].split('.')[0].lower() if selected=='system' else selected
    return code if code in TEXT else 'en'


def labels():return TEXT[language()][:3]


def host_binding(binding=None):
    loaded={name for name in BINDINGS if name in sys.modules}
    if binding is None:
        if len(loaded)!=1:raise ValueError('Pass the host Qt binding explicitly; exactly one binding must be loaded.')
        binding=next(iter(loaded))
    if binding not in BINDINGS:raise ValueError('Unsupported Qt binding.')
    if loaded-{binding}:raise ValueError('Cannot mix Qt bindings. Use the existing host binding.')
    return binding


def add_lafa_group(layout,binding=None,command=None,clock=time.monotonic):
    binding=host_binding(binding);widgets=importlib.import_module(binding+'.QtWidgets');core=importlib.import_module(binding+'.QtCore')
    argv=launch_command() if command is None else command
    if not isinstance(argv,(list,tuple)) or not 1<=len(argv)<=32 or not all(isinstance(part,str) and 0<len(part)<=4096 and '\x00' not in part for part in argv):raise ValueError('Expected a fixed executable argument list.')
    group=widgets.QGroupBox('LAFA');column=widgets.QVBoxLayout(group)
    toggle=widgets.QCheckBox();toggle.setChecked(enabled());column.addWidget(toggle)
    note=widgets.QLabel();note.setWordWrap(True);column.addWidget(note)
    status=widgets.QLabel();status.setWordWrap(True);column.addWidget(status)
    row=widgets.QHBoxLayout();desktop=widgets.QPushButton();settings=widgets.QPushButton();row.addWidget(desktop);row.addWidget(settings);column.addLayout(row)
    pending={'target':None,'deadline':0}
    def translate():
        text=TEXT[language()];toggle.setText(text[0]);desktop.setText(text[1]);settings.setText(text[2]);note.setText(text[7]);return text
    def sync():
        toggle.blockSignals(True);toggle.setChecked(enabled());toggle.blockSignals(False)
    def launch(role):
        text=translate()
        try:
            result=core.QProcess.startDetached(argv[0],list(argv[1:])+[role]);success=result[0] if isinstance(result,tuple) else result
        except (TypeError,RuntimeError,OSError):success=False
        if not success:status.setText(text[5]);pending['target']=None;toggle.setEnabled(True);sync();return
        if role in {'--virtual-enable','--virtual-disable'}:
            pending.update(target=role=='--virtual-enable',deadline=clock()+10);toggle.setEnabled(False);status.setText(text[3] if pending['target'] else text[4])
    toggle.toggled.connect(lambda value:launch('--virtual-enable' if value else '--virtual-disable'))
    desktop.clicked.connect(lambda:launch('--window'));settings.clicked.connect(lambda:launch('--settings'))
    timer=core.QTimer(group);timer.setInterval(1000)
    def refresh():
        text=translate()
        if pending['target'] is not None:
            if enabled()==pending['target']:pending['target']=None;toggle.setEnabled(True);status.clear()
            elif clock()>=pending['deadline']:pending['target']=None;toggle.setEnabled(True);status.setText(text[6]);sync()
            return
        sync()
    timer.timeout.connect(refresh);timer.start();translate();layout.addWidget(group)
    group.lafa_timer=timer;group.lafa_toggle=toggle;group.lafa_status=status;group.lafa_refresh=refresh;group.lafa_pending=pending
    return group


def create_lafa_page(parent=None,binding=None,command=None):
    binding=host_binding(binding);widgets=importlib.import_module(binding+'.QtWidgets')
    page=widgets.QWidget(parent);layout=widgets.QVBoxLayout(page);layout.setContentsMargins(24,24,24,24)
    page.lafa_group=add_lafa_group(layout,binding,command);layout.addStretch();return page
