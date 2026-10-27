"""What the Lafa Virtual Assistant tells the learner, chosen from the offline
encyclopedia and the learner's own progress (nothing is sent anywhere):

holiday   a public holiday or national day in the next days
today     this day (or month) in Timor-Leste's history
fact      a "did you know?" fact from an article
word      a Tetun word with its meaning in the learner's language
quiz      one question from the encyclopedia (answer it in the balloon)
place     a tourist place to discover
review    Tetun words waiting for revision (spaced repetition)
continue  the article the learner opened last
level     the next article for the learner's school level
streak    encouragement for days learned in a row
computer  a short tip for using the computer and Lafa

`next_tip()` rotates the kinds so the same kind does not come twice in a row.
"""
import random
from dataclasses import dataclass, field
from datetime import date

from . import kb
from .desk.texts import t, extend

extend({
    "tip_holiday_today": ("Ohin mak {name}!", "Hoje é {name}!", "Hari ini {name}!", "Today is {name}!"),
    "tip_holiday_soon": ("{when}: {name}", "{when}: {name}", "{when}: {name}", "{when}: {name}"),
    "tip_today": ("Ohin iha istória", "Neste dia na história", "Hari ini dalam sejarah", "On this day"),
    "tip_month": ("Iha fulan ne'e, iha istória", "Neste mês, na história", "Bulan ini dalam sejarah", "This month in history"),
    "tip_fact": ("Ita hatene ka lae?", "Sabia que…?", "Tahukah kamu?", "Did you know?"),
    "tip_word": ("Liafuan Tetun", "Palavra em tétum", "Kata Tetun", "Tetun word"),
    "tip_quiz": ("Kuis ki'ik", "Mini-quiz", "Kuis kecil", "Mini quiz"),
    "tip_place": ("Fatin atu vizita", "Lugar para visitar", "Tempat untuk dikunjungi", "A place to visit"),
    "tip_review": ("Repete liafuan", "Rever palavras", "Ulang kata", "Review words"),
    "tip_review_text": ("Liafuan {n} hein ita atu repete ohin. Minutu 2 de'it!", "{n} palavras esperam revisão hoje. Só 2 minutos!",
                        "{n} kata menunggu diulang hari ini. Hanya 2 menit!", "{n} words are waiting for review today. Just 2 minutes!"),
    "tip_continue": ("Kontinua lee", "Continuar a ler", "Lanjutkan membaca", "Keep reading"),
    "tip_level": ("Sujestaun ba {level}", "Sugestão para {level}", "Saran untuk {level}", "Suggestion for {level}"),
    "tip_streak": ("Loron {n} tuituir malu!", "{n} dias seguidos!", "{n} hari berturut-turut!", "{n} days in a row!"),
    "tip_streak_text": ("Di'ak tebes! Aprende buat ida foun ohin atu kontinua.", "Muito bem! Aprenda algo novo hoje para continuar.",
                        "Hebat! Pelajari satu hal baru hari ini untuk melanjutkan.", "Great! Learn one new thing today to keep it going."),
    "tip_computer": ("Ajuda komputadór", "Ajuda com o computador", "Bantuan komputer", "Computer help"),
    "act_read": ("Lee", "Ler", "Baca", "Read"),
    "act_map": ("Mapa", "Mapa", "Peta", "Map"),
    "act_words": ("Aprende liafuan", "Aprender palavras", "Belajar kata", "Learn words"),
    "act_cards": ("Repete agora", "Rever agora", "Ulang sekarang", "Review now"),
    "act_calendar": ("Kalendáriu", "Calendário", "Kalender", "Calendar"),
    "act_timeline": ("Liña tempu", "Linha do tempo", "Lini masa", "Timeline"),
    "act_quiz": ("Kuis Milionáriu", "Quiz Milionário", "Kuis Jutawan", "Millionaire quiz"),
    "act_paths": ("Nível eskola", "Níveis escolares", "Jenjang sekolah", "School levels"),
    "welcome_title": ("Bondia! Ha'u Lafa.", "Olá! Eu sou o Lafa.", "Halo! Saya Lafa.", "Hello! I'm Lafa."),
    "welcome_text": ("Ha'u ita-nia gia ba Timór-Leste no kolega estudu. Klik ha'u atu buka, halimar kuis ka aprende liafuan Tetun.",
                     "Sou o seu guia de Timor-Leste e colega de estudo. Clique em mim para pesquisar, jogar quizzes ou aprender tétum.",
                     "Saya pemandu Timor-Leste dan teman belajarmu. Klik saya untuk mencari, bermain kuis, atau belajar bahasa Tetun.",
                     "I'm your Timor-Leste guide and study buddy. Click me to search, play quizzes or learn Tetun words."),
})

COMPUTER_TIPS = [
    ("Iha Lafa Desktop, Ctrl+F loke buka. Alt+1 to'o Alt+9 loke menu sira.", "No Lafa Desktop, Ctrl+F abre a pesquisa. Alt+1 a Alt+9 abrem os menus.",
     "Di Lafa Desktop, Ctrl+F membuka pencarian. Alt+1 sampai Alt+9 membuka menu.", "In Lafa Desktop, Ctrl+F opens search. Alt+1 to Alt+9 open the menus."),
    ("Atu muda lian Lafa nian, loke Konfigurasaun → Lian aplikasaun nian.", "Para mudar a língua do Lafa, abra Definições → Língua da aplicação.",
     "Untuk mengganti bahasa Lafa, buka Pengaturan → Bahasa aplikasi.", "To change Lafa's language, open Settings → App language."),
    ("Download “Pakote offline” bainhira iha internet: depois ita bele lee testu no haree foto la ho internet.", "Descarregue o “Pacote offline” quando tiver internet: depois lê textos e vê fotos sem internet.",
     "Unduh “Paket luring” saat ada internet: nanti kamu bisa membaca teks dan melihat foto tanpa internet.", "Download the “Offline pack” when you are online: later you can read texts and see photos without internet."),
    ("Klik-loos iha Lafa atu hili hatais: Kazuál, Tais Mane ka Formál.", "Clique com o botão direito no Lafa para escolher a roupa: Casual, Tais Mane ou Formal.",
     "Klik kanan pada Lafa untuk memilih pakaian: Santai, Tais Mane atau Formal.", "Right-click Lafa to choose an outfit: Casual, Tais Mane or Formal."),
    ("Rai ita-nia servisu beibeik (Ctrl+S) no halo kópia iha USB ka nuvem.", "Guarde o seu trabalho muitas vezes (Ctrl+S) e faça cópias numa pen ou na nuvem.",
     "Simpan pekerjaanmu sering-sering (Ctrl+S) dan buat salinan di USB atau awan.", "Save your work often (Ctrl+S) and keep a copy on a USB stick or in the cloud."),
    ("Modu kalma: klik-loos iha Lafa → “Modu kalma” atu Lafa la ko'alia mesak.", "Modo calmo: clique com o botão direito no Lafa → “Modo calmo” para o Lafa não falar sozinho.",
     "Mode tenang: klik kanan Lafa → “Mode tenang” agar Lafa tidak berbicara sendiri.", "Quiet mode: right-click Lafa → “Quiet mode” so Lafa does not talk by itself."),
    ("Ekrã naroman liu ka nakukun liu? Muda tema iha Konfigurasaun → Tema.", "Ecrã muito claro ou escuro? Mude o tema em Definições → Tema.",
     "Layar terlalu terang atau gelap? Ganti tema di Pengaturan → Tema.", "Screen too bright or too dark? Change the theme in Settings → Theme."),
]

@dataclass
class Tip:
    kind: str
    icon: str
    accent: str
    title: str
    text: str
    actions: list = field(default_factory=list)       # [(label, route, item_id)]
    quiz: dict = None                                  # {"q", "options", "answer", "why", "item"}
    def speech(self):
        return f"{self.title}. {self.text}" + (f" {self.quiz['q']}" if self.quiz else "")

KINDS = {"holiday": 3, "today": 2, "fact": 3, "word": 3, "quiz": 4, "place": 2, "review": 2, "continue": 1, "level": 2, "streak": 1, "computer": 1}

def _lang(lang): return lang if lang in kb.LANGS else "en"

def tip_of(kind, base, progress, settings, lang, today=None, rng=None):
    """A tip of one kind, or None when there is nothing to say for it now."""
    lang = _lang(lang); today = today or date.today(); rng = rng or random.Random(); tr = lambda key, **v: t(lang, key, **v)
    if kind == "holiday":
        for when, d in base.upcoming(today, 3):
            delta = (when - today).days
            if delta > 10: break
            name = d.title(lang)
            title = tr("tip_holiday_today", name=name) if delta == 0 else tr("tip_holiday_soon", name=name, when=tr("tomorrow") if delta == 1 else tr("in_days", n=delta).capitalize())
            return Tip("holiday", "calendar-check", "rose", title, d.summary(lang), [(tr("act_read"), "item", d.id), (tr("act_calendar"), "calendar", "")])
        return None
    if kind == "today":
        events = base.today_in_history(today, lang); title = tr("tip_today")
        if not events:
            events = [e for e in base.timeline(lang) if len(str(e["date"])) >= 7 and str(e["date"])[5:7] == f"{today.month:02d}"]; title = tr("tip_month")
        if not events: return None
        e = rng.choice(events)
        return Tip("today", "scroll", "lilac", title, f"{kb.format_when(e['date'], lang)} — {e['title']}", [(tr("act_read"), "item", e["item"]), (tr("act_timeline"), "timeline", "")])
    if kind == "fact":
        facts = []
        for item in base.all("article"):
            for f in item.get("facts") or []:
                if isinstance(f, dict) and f.get("label") and f.get("value"):
                    value = kb.text(f["value"], lang) if isinstance(f["value"], dict) else str(f["value"])
                    facts.append((item, f"{kb.text(f['label'], lang)}: {value}" + (f" ({f['year']})" if f.get("year") else "")))
        if not facts: return None
        item, line = rng.choice(facts)
        return Tip("fact", "lightbulb", "butter", tr("tip_fact"), f"{line}\n— {item.title(lang)}", [(tr("act_read"), "item", item.id)])
    if kind == "word":
        words = [w for w in base.words if w.level <= 2] or base.words
        if not words: return None
        w = rng.choice(words); code = getattr(settings, "vocab_lang", "pt") or "pt"
        meaning = w.meaning(code) or w.meaning("en"); others = ", ".join(w.meaning(c) for c in ("pt", "id", "en") if c != code and w.meaning(c))
        ex = kb.show(w.ex.get("tet", ""), "tet") if isinstance(w.ex, dict) and w.ex.get("tet") else ""
        text_ = f"{kb.show(w.tet, 'tet')} = {meaning}" + (f"  ({others})" if others else "") + (f"\n“{ex}”" if ex else "")
        return Tip("word", "translate", "mint", tr("tip_word"), text_, [(tr("act_words"), "language", "")])
    if kind == "quiz":
        level = getattr(settings, "school_level", "eb3"); lo, hi = kb.LEVEL_DIFFICULTY.get(level, (1, 15))
        pool = base.questions(None, lo, hi) or base.questions()
        if not pool: return None
        q = rng.choice(pool); raw = q["q"]
        quiz = {"q": kb.text(raw["q"], lang), "options": [kb.text(o, lang) for o in raw["options"]], "answer": raw["answer"], "why": kb.text(raw.get("why"), lang), "item": q["item"]}
        return Tip("quiz", "trophy", "violet", tr("tip_quiz"), "", [(tr("act_read"), "item", q["item"]), (tr("act_quiz"), "quiz", "")], quiz)
    if kind == "place":
        places = base.places()
        if not places: return None
        p = rng.choice(places); mun = base.get(p.get("municipality", ""))
        return Tip("place", "umbrella", "cyan", tr("tip_place") + (f" · {mun.title(lang)}" if mun else ""), f"{p.title(lang)} — {p.summary(lang)}",
                   [(tr("act_read"), "item", p.id), (tr("act_map"), "map", p.id)])
    if kind == "review":
        if not progress or not base.words: return None
        ids = [w.id for w in base.words]; due = [i for i in progress.due_words(ids, 10 ** 6) if i in progress.words]
        if len(due) < 3: return None
        return Tip("review", "cards", "mint", tr("tip_review"), tr("tip_review_text", n=len(due)), [(tr("act_cards"), "language", "cards")])
    if kind == "continue":
        last = progress.last if progress else None
        if not last or not base.get(last.get("key", "")): return None
        item = base.get(last["key"])
        return Tip("continue", "book-open", "violet", tr("tip_continue"), f"{item.title(lang)} — {item.summary(lang)}", [(tr("act_read"), "item", item.id)])
    if kind == "level":
        level = getattr(settings, "school_level", "eb3")
        for unit in base.path(level):
            for item in unit["items"]:
                if progress and progress.is_read(item.id): continue
                return Tip("level", "graduation", "pink", tr("tip_level", level=kb.LEVEL_SHORT.get(level, "")), f"{item.title(lang)} — {item.summary(lang)}",
                           [(tr("act_read"), "item", item.id), (tr("act_paths"), "paths", "")])
        return None
    if kind == "streak":
        n = progress.streak if progress else 0
        if n < 2: return None
        return Tip("streak", "star", "peach", tr("tip_streak", n=n), tr("tip_streak_text"), [(tr("act_quiz"), "quiz", "")])
    if kind == "computer":
        row = rng.choice(COMPUTER_TIPS)
        return Tip("computer", "monitor-help", "sky", tr("tip_computer"), kb.show(row[kb.LANGS.index(lang)], lang), [])
    return None

def welcome(lang):
    lang = _lang(lang)
    return Tip("welcome", "sparkle", "violet", t(lang, "welcome_title"), t(lang, "welcome_text"), [(t(lang, "act_quiz"), "quiz", ""), (t(lang, "act_words"), "language", "")])

class TipChooser:
    """Rotates the kinds of tips; holidays come first on the day before and the day itself."""
    def __init__(self, rng=None):
        self.rng = rng or random.Random(); self.recent = []; self.holiday_shown = ""
    def next(self, base, progress, settings, lang, today=None):
        today = today or date.today()
        if self.holiday_shown != today.isoformat():
            soon = [d for when, d in base.upcoming(today, 2) if (when - today).days <= 1]
            if soon:
                tip = tip_of("holiday", base, progress, settings, lang, today, self.rng)
                if tip: self.holiday_shown = today.isoformat(); self.recent = (self.recent + ["holiday"])[-4:]; return tip
        kinds = [k for k in KINDS if k not in self.recent[-2:]]
        for _ in range(12):
            kind = self.rng.choices(kinds, weights=[KINDS[k] for k in kinds])[0]
            tip = tip_of(kind, base, progress, settings, lang, today, self.rng)
            if tip:
                self.recent = (self.recent + [kind])[-4:]; return tip
        return welcome(lang)
