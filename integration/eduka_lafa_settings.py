"""Lafa-Configuration: LAFA's native page in Eduka-Settings.

Works with PyQt5 (Eduka-Settings), PyQt6 or PySide6 host settings apps.

Use the host's binding. This module does not import LAFA's Qt client. Launch
roles are fixed and settings state is checked after a detached activation.

The page uses Eduka-Settings' own structure and object names (pageTitle,
card, settingRow, rowTitle, rowLine, fieldHint), so Eduka's stylesheet and
theme style it like every other page. Changes apply live, like Eduka-Settings.

The page holds every LAFA preference (Eduka-Settings → LAFA): activation,
Virtual Assistant behaviour, personality, AI provider/model, language, files
and weather. Saving writes ~/.config/lafa/settings.json atomically and asks a
running LAFA to reload. API keys are never written here; "API keys…" opens
LAFA's own secure dialog (session memory or system keyring).
"""
import importlib
import json
import os
from pathlib import Path
import sys
import stat
import tempfile
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


def eduka_language():
    """Tetun when chosen in Eduka-Settings → Language, else None."""
    try:
        path=Path.home()/'.config/eduka-desktop/menu/settings.json'
        data=json.loads(read_regular(path,65536)) if path.is_file() else {}
        return 'tet' if isinstance(data,dict) and data.get('language')=='tet' else None
    except (OSError,ValueError):return None


def language():
    selected=preferences().get('language','system')
    if not isinstance(selected,str) or selected not in {'system','en','id','pt','tet'}:selected='system'
    if selected=='system' and (eduka_language() or os.environ.get('EDUKA_LOGIN_LANGUAGE')=='tet'):return 'tet'
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


def add_lafa_group(layout,binding=None,command=None,clock=time.monotonic,card=False):
    binding=host_binding(binding);widgets=importlib.import_module(binding+'.QtWidgets');core=importlib.import_module(binding+'.QtCore')
    argv=launch_command() if command is None else command
    if not isinstance(argv,(list,tuple)) or not 1<=len(argv)<=32 or not all(isinstance(part,str) and 0<len(part)<=4096 and '\x00' not in part for part in argv):raise ValueError('Expected a fixed executable argument list.')
    if card:
        # Eduka-Settings card look (QFrame#card + QLabel#cardTitle).
        group=widgets.QFrame();group.setObjectName('card');column=widgets.QVBoxLayout(group);column.setContentsMargins(18,14,18,14)
        heading=widgets.QLabel('LAFA');heading.setObjectName('cardTitle');column.addWidget(heading);group.title=lambda:'LAFA'
    else:
        group=widgets.QGroupBox('LAFA');column=widgets.QVBoxLayout(group)
    toggle=widgets.QCheckBox();toggle.setChecked(enabled());column.addWidget(toggle)
    note=widgets.QLabel();note.setObjectName('fieldHint');note.setWordWrap(True);column.addWidget(note)
    status=widgets.QLabel();status.setObjectName('fieldHint');status.setWordWrap(True);column.addWidget(status)
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


# ---------------------------------------------------------------------------
# Lafa-Configuration. Labels: (English, Indonesian, Portuguese, Tetun).
LANG_INDEX={'en':0,'id':1,'pt':2,'tet':3}
SPEEDS={'slow':('Slow','Pelan','Lento','Neineik'),'normal':('Normal','Normal','Normal','Normál'),'fast':('Fast','Cepat','Rápido','Lalais')}
SECTIONS=[
 ('virtual',('LAFA Virtual Assistant','LAFA Asisten Virtual','Assistente Virtual LAFA','LAFA Asistente Virtuál'),[
  ('costume','enum',{'traditional':('Tais Mane (default)','Tais Mane (bawaan)','Tais Mane (predefinido)','Tais Mane (padraun)'),'tuxedo':('Tuxedo (formal)','Tuksedo (resmi)','Smoking (formal)','Tuxedo (formál)'),'casual':('Casual (summer)','Kasual (musim panas)','Informal (verão)','Kazuál (bai-loron)')},('Outfit','Pakaian','Traje','Hatais')),
  ('character_size','enum',{'small':('Small','Kecil','Pequeno','Ki’ik'),'normal':('Normal','Normal','Normal','Normál'),'large':('Large','Besar','Grande','Boot')},('Character size','Ukuran karakter','Tamanho da personagem','Tamañu karakter')),
  ('walk_speed','enum',SPEEDS,('Walking speed','Kecepatan berjalan','Velocidade a caminhar','Velosidade la’o')),
  ('animation_speed','enum',SPEEDS,('Animation speed','Kecepatan animasi','Velocidade da animação','Velosidade animasaun')),
  ('roam','bool',None,('Walk on the desktop when idle','Berjalan di desktop saat santai','Caminhar quando inativo','La’o iha desktop bainhira la uza')),
  ('follow_eduka_panel','bool',None,('Follow Eduka-Panel position and size','Ikuti posisi dan ukuran Eduka-Panel','Seguir a posição do Eduka-Panel','Tuir pozisaun Eduka-Panel')),
  ('panel_roam','bool',None,('Walk back and forth above the Eduka-Panel','Berjalan bolak-balik di atas Eduka-Panel','Caminhar junto ao Eduka-Panel','La’o ba-mai iha Eduka-Panel leten')),
  ('panel_edge','enum',{'bottom':('Bottom','Bawah','Inferior','Kraik'),'top':('Top','Atas','Superior','Leten')},('Panel edge (manual)','Sisi panel (manual)','Posição do painel (manual)','Pozisaun painel (manuál)')),
  ('panel_height','int',(0,160),('Panel height in px (manual)','Tinggi panel px (manual)','Altura do painel px (manual)','Altura painel px (manuál)')),
  ('greet_by_time','bool',None,('Greet by time of day','Sapa sesuai waktu','Saudar conforme a hora','Kumprimenta tuir oras')),
  ('start_with_session','bool',None,('Start with Eduka-Desktop when activated','Mulai bersama Eduka-Desktop saat aktif','Iniciar com o Eduka-Desktop','Hahú ho Eduka-Desktop')),
 ]),
 ('personality',('Personality & activities','Kepribadian & aktivitas','Personalidade e atividades','Karakter no atividade'),[
  ('hover_questions','bool',None,('Ask “Can I help?” when the cursor touches LAFA','Tanya “Bisa saya bantu?” saat kursor menyentuh LAFA','Perguntar “Posso ajudar?” ao tocar no LAFA','Husu “Ha’u bele ajuda?” bainhira kursór kona LAFA')),
  ('chatter','bool',None,('LAFA talks about what it is doing','LAFA bercerita tentang kegiatannya','O LAFA comenta o que está a fazer','LAFA koalia kona-ba ninia atividade')),
  ('fun_messages','bool',None,('Jokes and fun messages','Lelucon dan pesan lucu','Piadas e mensagens divertidas','Anedota no mensajen kmanek')),
  ('personal_activities','bool',None,('Include bathing / toilet activities','Sertakan aktivitas mandi / toilet','Incluir banho / casa de banho','Inklui hariis / toalete')),
  ('positive_messages','bool',None,('Positive messages','Pesan positif','Mensagens positivas','Mensajen pozitivu')),
  ('cultural_cards','bool',None,('Timor-Leste knowledge cards','Kartu pengetahuan Timor-Leste','Cartões sobre Timor-Leste','Karta koñesimentu Timor-Leste')),
  ('local_news_updates','bool',None,('Timor-Leste news updates','Pembaruan berita Timor-Leste','Notícias de Timor-Leste','Atualizasaun notísia Timor-Leste')),
  ('idle_seconds','int',(20,600),('Change activity after (seconds)','Ganti aktivitas setelah (detik)','Mudar de atividade após (segundos)','Troka atividade depois (segundu)')),
  ('balloon_seconds','int',(3,20),('Speech balloon time (seconds)','Lama balon bicara (detik)','Tempo do balão (segundos)','Tempu balaun (segundu)')),
  ('card_minutes','int',(1,120),('Cards / messages every (minutes)','Kartu / pesan setiap (menit)','Cartões a cada (minutos)','Karta kada (minutu)')),
  ('news_minutes','int',(10,240),('News every (minutes)','Berita setiap (menit)','Notícias a cada (minutos)','Notísia kada (minutu)')),
 ]),
 ('desktop',('LAFA Desktop','LAFA Desktop','LAFA Desktop','LAFA Desktop'),[
  ('start_page','enum',{'home':('Home','Beranda','Início','Uma'),'teachers':('Teachers','Guru','Professores','Mestre sira'),'homework':('Homework & timetable','PR & jadwal','Trabalhos e horário','TPC no orariu'),'chat':('Conversation','Percakapan','Conversa','Konversa'),'os_help':('Edukasaun OS help','Bantuan Edukasaun OS','Ajuda do Edukasaun OS','Ajuda Edukasaun OS')},('Start page','Halaman awal','Página inicial','Pájina inisiál')),
  ('follow_eduka_theme','bool',None,('Use the Eduka-Desktop theme and accent colour','Pakai tema dan warna aksen Eduka-Desktop','Usar o tema e a cor do Eduka-Desktop','Uza tema no kór Eduka-Desktop')),
  ('notifications','bool',None,('Reminders as Eduka-Panel notifications','Pengingat sebagai notifikasi Eduka-Panel','Lembretes como notificações do Eduka-Panel','Lembransa hanesan notifikasaun Eduka-Panel')),
  ('auto_update','bool',None,('Keep learning sources up to date automatically','Perbarui sumber belajar otomatis','Atualizar as fontes automaticamente','Atualiza fonte aprende automátiku')),
  ('update_hours','int',(1,168),('Check for updates every (hours)','Periksa pembaruan setiap (jam)','Verificar atualizações a cada (horas)','Verifika atualizasaun kada (oras)')),
  ('speak_answers','bool',None,('Read answers aloud','Bacakan jawaban','Ler respostas em voz alta','Lee resposta ho lian')),
  ('speech_rate','int',(80,260),('Reading speed (words/min)','Kecepatan membaca (kata/menit)','Velocidade de leitura','Velosidade lee')),
 ]),
 ('ai',('AI & language','AI & bahasa','IA e idioma','IA no lian'),[
  ('language','enum',{'system':('Follow Eduka-Desktop','Ikuti Eduka-Desktop','Seguir o Eduka-Desktop','Tuir Eduka-Desktop'),'en':('English',)*4,'tet':('Tetun',)*4,'pt':('Português',)*4,'id':('Bahasa Indonesia',)*4},('LAFA language','Bahasa LAFA','Idioma do LAFA','Lian LAFA')),
  ('provider','enum',{'ollama':('Ollama (open-source, local)',)*4,'compatible':('Open-source server (OpenAI-compatible)',)*4,'openai':('OpenAI',)*4,'gemini':('Gemini',)*4,'anthropic':('Claude',)*4,'deepseek':('DeepSeek',)*4,'perplexity':('Perplexity',)*4},('AI provider','Penyedia AI','Fornecedor de IA','Provedor IA')),
  ('model','model',120,('Model ID for this provider','ID model untuk penyedia ini','ID do modelo','ID modelu')),
  ('ollama_url','text',300,('Ollama address (this computer)','Alamat Ollama (komputer ini)','Endereço do Ollama','Enderesu Ollama')),
  ('compatible_url','text',300,('Open-source server (https://…/v1)','Server open-source (https://…/v1)','Servidor open-source (https://…/v1)','Servidór open-source (https://…/v1)')),
 ]),
 ('files',('Files & weather','File & cuaca','Ficheiros e tempo','Ficheiru no tempu'),[
  ('weather_city','text',120,('Home city','Kota utama','Cidade principal','Sidade prinsipál')),
  ('weather_latitude','float',(-90,90),('Latitude','Lintang','Latitude','Latitude')),
  ('weather_longitude','float',(-180,180),('Longitude','Bujur','Longitude','Longitude')),
  ('weather_timezone','text',100,('Time zone','Zona waktu','Fuso horário','Zona oras')),
  ('roots','paths',100,('Folders LAFA may search (one per line)','Folder yang boleh dicari LAFA (satu per baris)','Pastas que o LAFA pode pesquisar (uma por linha)','Pasta ne’ebé LAFA bele buka (ida kada liña)')),
 ]),
]
PAGE_TEXT={'title':('Lafa-Configuration','Lafa-Configuration','Lafa-Configuration','Lafa-Configuration'),
 'hint':('Settings for LAFA Desktop and the LAFA Virtual Assistant. Changes apply at once.','Pengaturan LAFA Desktop dan LAFA Asisten Virtual. Perubahan langsung berlaku.','Definições do LAFA Desktop e do Assistente Virtual LAFA. As alterações aplicam-se logo.','Konfigurasaun LAFA Desktop no LAFA Asistente Virtuál. Mudansa aplika kedas.'),
 'save':('Apply now','Terapkan sekarang','Aplicar agora','Aplika agora'),'keys':('API keys…','API key…','Chaves API…','Xave API…'),
 'reset':('Recommended settings','Pengaturan yang disarankan','Definições recomendadas','Konfigurasaun rekomendadu'),
 'saved':('Saved. LAFA applies the changes now.','Tersimpan. LAFA langsung menerapkan perubahan.','Guardado. O LAFA aplica as alterações.','Rai ona. LAFA aplika mudansa agora.'),
 'failed':('Could not save LAFA settings.','Pengaturan LAFA gagal disimpan.','Não foi possível guardar.','La bele rai konfigurasaun LAFA.'),
 'keys_note':('API keys are kept by LAFA in memory or the secure keyring, never in this page.','API key disimpan LAFA di memori atau keyring aman, tidak di halaman ini.','As chaves API ficam no LAFA (memória ou porta-chaves), nunca nesta página.','Xave API LAFA rai iha memória ka keyring seguru, la iha pájina ne’e.')}
# Recommended values (also LAFA's defaults).
DEFAULTS={'costume':'traditional','character_size':'normal','walk_speed':'normal','animation_speed':'normal','roam':True,'follow_eduka_panel':True,'panel_roam':True,'panel_edge':'bottom','panel_height':42,'greet_by_time':True,'start_with_session':True,
 'hover_questions':True,'chatter':True,'fun_messages':True,'personal_activities':True,'positive_messages':True,'cultural_cards':True,'local_news_updates':True,'idle_seconds':60,'balloon_seconds':6,'card_minutes':5,'news_minutes':30,
 'start_page':'home','follow_eduka_theme':True,'notifications':True,'auto_update':True,'update_hours':24,'speak_answers':False,'speech_rate':155,
 'language':'system','provider':'openai','ollama_url':'http://127.0.0.1:11434','compatible_url':'','weather_city':'Dili','weather_latitude':-8.5586,'weather_longitude':125.5736,'weather_timezone':'Asia/Dili'}

def pick(labels):return labels[LANG_INDEX.get(language(),0)] if len(labels)>1 else labels[0]

def write_preferences(changes):
    """Merge changes into LAFA's settings file atomically (0600, no secrets)."""
    path=locations()[0];path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    data=preferences();data.update(changes)
    fd,tmp=tempfile.mkstemp(dir=path.parent,prefix='.lafa-')
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as stream:json.dump(data,stream,indent=2,ensure_ascii=False)
        os.chmod(tmp,0o600);os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)
    return data

def _card(widgets,layout,title):
    """Eduka-Settings card: QFrame#card with a QLabel#cardTitle."""
    card=widgets.QFrame();card.setObjectName('card');lay=widgets.QVBoxLayout(card);lay.setContentsMargins(18,14,18,14);lay.setSpacing(0)
    heading=widgets.QLabel(title);heading.setObjectName('cardTitle');lay.addWidget(heading);layout.addWidget(card);return lay

def _row(widgets,core,card,label,control,first):
    """Eduka-Settings row: title on the left, control on the right, thin line between rows."""
    if not first:
        line=widgets.QFrame();line.setObjectName('rowLine');card.addWidget(line)
    row=widgets.QFrame();row.setObjectName('settingRow');h=widgets.QHBoxLayout(row);h.setContentsMargins(2,10,2,10);h.setSpacing(16)
    if label:
        title=widgets.QLabel(label);title.setObjectName('rowTitle');title.setFixedWidth(210);title.setWordWrap(True);h.addWidget(title)
    h.addWidget(control,1);card.addWidget(row)

def add_lafa_preferences(layout,binding=None,command=None,live=True,clock=None):
    """Grouped Lafa-Configuration controls for every non-secret LAFA preference."""
    binding=host_binding(binding);widgets=importlib.import_module(binding+'.QtWidgets');core=importlib.import_module(binding+'.QtCore')
    argv=launch_command() if command is None else list(command)
    prefs=preferences();controls={}
    container=widgets.QWidget();column=widgets.QVBoxLayout(container);column.setContentsMargins(0,0,0,0);column.setSpacing(12)
    for key,title,fields in SECTIONS:
        card=_card(widgets,column,pick(title));first=True
        for name,kind,extra,labels in fields:
            text=pick(labels);label=text
            if kind=='bool':
                control=widgets.QCheckBox(text);control.setChecked(prefs.get(name,DEFAULTS[name]) is True);label=''
            elif kind=='enum':
                control=widgets.QComboBox()
                for value,names in extra.items():control.addItem(pick(names),value)
                current=prefs.get(name,DEFAULTS[name]);index=control.findData(current);control.setCurrentIndex(index if index>=0 else control.findData(DEFAULTS[name]))
            elif kind=='int':
                control=widgets.QSpinBox();control.setRange(*extra);value=prefs.get(name,DEFAULTS[name]);control.setValue(value if isinstance(value,int) and not isinstance(value,bool) else DEFAULTS[name])
            elif kind=='float':
                control=widgets.QDoubleSpinBox();control.setDecimals(4);control.setRange(*extra);value=prefs.get(name,DEFAULTS[name]);control.setValue(float(value) if isinstance(value,(int,float)) and not isinstance(value,bool) else DEFAULTS[name])
            elif kind=='model':
                models=prefs.get('models',{}) if isinstance(prefs.get('models'),dict) else {}
                provider=prefs.get('provider',DEFAULTS['provider']);control=widgets.QLineEdit(models.get(provider,'') if isinstance(models.get(provider,''),str) else '');control.setMaxLength(extra)
            elif kind=='paths':
                roots=prefs.get('roots',[]);control=widgets.QPlainTextEdit('\n'.join(r for r in roots if isinstance(r,str)) if isinstance(roots,list) else '');control.setMaximumHeight(110)
            else:
                value=prefs.get(name,DEFAULTS.get(name,''));control=widgets.QLineEdit(value if isinstance(value,str) else DEFAULTS.get(name,''));control.setMaxLength(extra)
            _row(widgets,core,card,label,control,first);first=False;controls[name]=(kind,control)
    provider_box=controls['provider'][1];model_box=controls['model'][1];state={'provider':provider_box.currentData(),'models':dict(prefs.get('models',{})) if isinstance(prefs.get('models'),dict) else {},'loading':False}
    def provider_changed(*_):
        state['models'][state['provider']]=model_box.text().strip();state['provider']=provider_box.currentData()
        value=state['models'].get(state['provider'],'');state['loading']=True;model_box.setText(value if isinstance(value,str) else '');state['loading']=False
    provider_box.currentIndexChanged.connect(provider_changed)
    row=widgets.QHBoxLayout();save=widgets.QPushButton(pick(PAGE_TEXT['save']));save.setObjectName('primary');reset=widgets.QPushButton(pick(PAGE_TEXT['reset']));keys=widgets.QPushButton(pick(PAGE_TEXT['keys']))
    row.addWidget(save);row.addWidget(reset);row.addWidget(keys);row.addStretch();column.addLayout(row)
    note=widgets.QLabel(pick(PAGE_TEXT['keys_note']));note.setObjectName('fieldHint');note.setWordWrap(True);column.addWidget(note)
    status=widgets.QLabel();status.setObjectName('fieldHint');status.setWordWrap(True);column.addWidget(status)
    def collect():
        changes={}
        for name,(kind,control) in controls.items():
            if kind=='bool':changes[name]=control.isChecked()
            elif kind=='enum':changes[name]=control.currentData()
            elif kind in {'int','float'}:changes[name]=control.value()
            elif kind=='paths':changes['roots']=[line.strip() for line in control.toPlainText().splitlines() if line.strip()][:100]
            elif kind=='model':pass
            else:changes[name]=control.text().strip()
        models=dict(state['models']);models[provider_box.currentData()]=model_box.text().strip();changes['models']=models
        return changes
    def launch(role):
        try:
            result=core.QProcess.startDetached(argv[0],list(argv[1:])+[role]);return result[0] if isinstance(result,tuple) else result
        except (TypeError,RuntimeError,OSError):return False
    def save_clicked():
        try:write_preferences(collect())
        except (OSError,ValueError,TypeError):status.setText(pick(PAGE_TEXT['failed']));return
        launch('--reload');status.setText(pick(PAGE_TEXT['saved']))
    def reset_clicked():
        """Recommended values for LAFA's behaviour; AI, folders and weather stay."""
        timer.stop()
        for name,(kind,control) in controls.items():
            if name not in DEFAULTS or name in {'provider','ollama_url','compatible_url','weather_city','weather_latitude','weather_longitude','weather_timezone','language'}:continue
            if kind=='bool':control.setChecked(DEFAULTS[name])
            elif kind=='enum':control.setCurrentIndex(control.findData(DEFAULTS[name]))
            elif kind in {'int','float'}:control.setValue(DEFAULTS[name])
        save_clicked()
    # Live apply like Eduka-Settings: a short pause, then save and reload LAFA.
    timer=core.QTimer(container);timer.setSingleShot(True);timer.setInterval(700);timer.timeout.connect(save_clicked)
    if live:
        def kick(*_):
            if not state['loading']:timer.start()
        for kind,control in controls.values():
            if kind=='bool':control.toggled.connect(kick)
            elif kind=='enum':control.currentIndexChanged.connect(kick)
            elif kind in {'int','float'}:control.valueChanged.connect(kick)
            elif kind=='paths':control.textChanged.connect(lambda:timer.start(1200))
            else:control.textChanged.connect(lambda *_:None if state['loading'] else timer.start(1200))
    save.clicked.connect(save_clicked);reset.clicked.connect(reset_clicked);keys.clicked.connect(lambda:launch('--settings'))
    layout.addWidget(container)
    container.lafa_controls=controls;container.lafa_save=save_clicked;container.lafa_reset=reset_clicked;container.lafa_status=status;container.lafa_collect=collect;container.lafa_timer=timer
    return container


def create_lafa_page(parent=None,binding=None,command=None):
    """Page for Eduka-Settings (descriptor: lafa-page.json, key 'lafa')."""
    binding=host_binding(binding);widgets=importlib.import_module(binding+'.QtWidgets')
    page=widgets.QWidget(parent);outer=widgets.QVBoxLayout(page);outer.setContentsMargins(26,22,26,10);outer.setSpacing(12)
    title=widgets.QLabel(pick(PAGE_TEXT['title']));title.setObjectName('pageTitle');outer.addWidget(title)
    hint=widgets.QLabel(pick(PAGE_TEXT['hint']));hint.setObjectName('pageHint');hint.setWordWrap(True);outer.addWidget(hint)
    page.lafa_group=add_lafa_group(outer,binding,command,card=True)
    page.lafa_preferences=add_lafa_preferences(outer,binding,command);outer.addStretch(1)
    page.eduka_apply=page.lafa_preferences.lafa_save
    return page
