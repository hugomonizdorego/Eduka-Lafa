"""Kuis Milionáriu — "Who Wants to Be a Millionaire" about Timor-Leste.

Fifteen questions from easy to hard (each question in the encyclopedia has a
difficulty 1–15 = its step on the ladder), prizes in US dollars (Timor-Leste's
currency, just for play), safe havens at steps 5 and 10, three lifelines:
50:50, ask the audience and phone Lafa. The school level chooses which
difficulties are used. Game logic (`Game`) is separate from the screen.
"""
import random

from ...qt import Qt, QTimer, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QComboBox, QCheckBox, QLabel, QSizePolicy
from ... import kb
from ..texts import extend
from ..widgets import (Card, ClayIcon, Pill, Segmented, ProgressRing, BarChart, ResponsiveGrid, label, button, scroll, section_title,
                       clear_layout, tok_of)

extend({
    "mil_title": ("Kuis Milionáriu Timór-Leste", "Quiz Milionário de Timor-Leste", "Kuis Jutawan Timor-Leste", "Timor-Leste Millionaire Quiz"),
    "mil_sub": ("Hatán pergunta 15 kona-ba Timór-Leste, husi fásil to'o susar. Prémiu ne'e ba halimar de'it.", "Responda a 15 perguntas sobre Timor-Leste, das fáceis às difíceis. Os prémios são só a brincar.",
                "Jawab 15 pertanyaan tentang Timor-Leste, dari mudah ke sulit. Hadiahnya hanya untuk bermain.", "Answer 15 questions about Timor-Leste, from easy to hard. The prizes are just for fun."),
    "mil_rules": ("Ajuda 3: 50:50, husu públiku no telefone Lafa. Fatin seguru iha pergunta 5 ($1 000) no 10 ($32 000). Ita bele sai ho osan bainhira de'it.",
                  "3 ajudas: 50:50, perguntar ao público e telefonar ao Lafa. Patamares seguros nas perguntas 5 ($1 000) e 10 ($32 000). Pode desistir com o prémio a qualquer momento.",
                  "3 bantuan: 50:50, tanya penonton dan telepon Lafa. Titik aman di soal 5 ($1 000) dan 10 ($32 000). Kamu boleh berhenti dan membawa hadiah kapan saja.",
                  "3 lifelines: 50:50, ask the audience and phone Lafa. Safe havens at questions 5 ($1,000) and 10 ($32,000). You may walk away with your prize at any time."),
    "mil_level": ("Nível", "Nível", "Jenjang", "Level"),
    "mil_topic": ("Tema", "Tema", "Tema", "Topic"),
    "mil_all_topics": ("Tema hotu", "Todos os temas", "Semua tema", "All topics"),
    "mil_timer": ("Ho relójiu (segundu 30/45/60)", "Com relógio (30/45/60 segundos)", "Dengan waktu (30/45/60 detik)", "With a clock (30/45/60 seconds)"),
    "mil_start": ("Hahú jogu", "Começar o jogo", "Mulai main", "Start the game"),
    "mil_best": ("Prémiu di'ak liu", "Melhor prémio", "Hadiah terbaik", "Best prize"),
    "mil_games": ("Jogu", "Jogos", "Permainan", "Games"),
    "mil_wins": ("Manán milaun", "Milhões ganhos", "Menang sejuta", "Million wins"),
    "mil_not_enough": ("Pergunta seidauk to'o ba jogu ne'e ({n}/15). Hili tema ka nível seluk.", "Ainda não há perguntas suficientes ({n}/15). Escolha outro tema ou nível.",
                       "Soal belum cukup ({n}/15). Pilih tema atau jenjang lain.", "Not enough questions yet ({n}/15). Choose another topic or level."),
    "mil_question": ("Pergunta {i} husi 15", "Pergunta {i} de 15", "Soal {i} dari 15", "Question {i} of 15"),
    "mil_for": ("ba {prize}", "por {prize}", "untuk {prize}", "for {prize}"),
    "mil_fifty": ("50:50", "50:50", "50:50", "50:50"),
    "mil_audience": ("Públiku", "Público", "Penonton", "Audience"),
    "mil_phone": ("Telefone Lafa", "Ligar ao Lafa", "Telepon Lafa", "Phone Lafa"),
    "mil_walk": ("Sai ho {prize}", "Desistir com {prize}", "Berhenti dengan {prize}", "Walk away with {prize}"),
    "mil_final": ("Resposta finál?", "Resposta final?", "Jawaban akhir?", "Final answer?"),
    "mil_right": ("Loos! Ita manán {prize}.", "Certo! Ganhou {prize}.", "Benar! Kamu memenangkan {prize}.", "Correct! You have won {prize}."),
    "mil_wrong": ("La loos. Resposta loos mak {letter}.", "Errado. A resposta certa era {letter}.", "Salah. Jawaban yang benar {letter}.", "Wrong. The right answer was {letter}."),
    "mil_timeout": ("Tempu remata ona!", "Acabou o tempo!", "Waktu habis!", "Time is up!"),
    "mil_next": ("Pergunta tuir mai", "Pergunta seguinte", "Soal berikutnya", "Next question"),
    "mil_over": ("Jogu remata", "Fim do jogo", "Permainan selesai", "Game over"),
    "mil_take_home": ("Ita lori ba uma: {prize}", "Leva para casa: {prize}", "Kamu membawa pulang: {prize}", "You take home: {prize}"),
    "mil_winner": ("PARABÉNS! Ita sai milionáriu Timór-Leste nian!", "PARABÉNS! É o milionário de Timor-Leste!", "SELAMAT! Kamu jutawan Timor-Leste!", "CONGRATULATIONS! You are Timor-Leste's millionaire!"),
    "mil_again": ("Halimar fali", "Jogar outra vez", "Main lagi", "Play again"),
    "mil_learn": ("Aprende kona-ba pergunta ne'e", "Aprender sobre esta pergunta", "Pelajari soal ini", "Learn about this question"),
    "mil_lafa_says": ("Lafa dehan: “Ha'u hanoin resposta mak {letter}. Ha'u fiar {conf}%.”", "Lafa diz: “Acho que é a {letter}. Tenho {conf}% de certeza.”",
                      "Lafa berkata: “Saya kira jawabannya {letter}. Saya {conf}% yakin.”", "Lafa says: “I think it is {letter}. I am {conf}% sure.”"),
    "mil_lafa_hint": ("Hanoin kona-ba: {title}", "Pense em: {title}", "Ingat tentang: {title}", "Think about: {title}"),
    "mil_audience_says": ("Públiku nia votu", "Votos do público", "Suara penonton", "The audience votes"),
    "mil_safe": ("fatin seguru", "patamar seguro", "titik aman", "safe haven"),
    "mil_keys": ("Teklas A–D ka 1–4 · Enter: tuir mai", "Teclas A–D ou 1–4 · Enter: seguinte", "Tombol A–D atau 1–4 · Enter: lanjut", "Keys A–D or 1–4 · Enter: next"),
    "mil_seconds": ("{n} s", "{n} s", "{n} dtk", "{n} s"),
})

PRIZES = [100, 200, 300, 500, 1000, 2000, 4000, 8000, 16000, 32000, 64000, 125000, 250000, 500000, 1000000]
SAFE_STEPS = (5, 10)
LETTERS = "ABCD"

def money(value):
    return "$" + f"{int(value):,}".replace(",", " ")

def time_limit(step):
    """Seconds for a question (1-based step) when the clock is on."""
    return 30 if step <= 5 else 45 if step <= 10 else 60

def pick_questions(base, level="eb3", category=None, rng=None, count=15):
    """Fifteen questions climbing in difficulty inside the level's range,
    each from a different article when possible. Returns [] if too few."""
    rng = rng or random.Random()
    lo, hi = kb.LEVEL_DIFFICULTY.get(level, (1, 15))
    pool = base.questions(category)
    if len(pool) < count: return []
    chosen = []; used = set(); used_items = set()
    for step in range(count):
        target = lo + (hi - lo) * step / max(1, count - 1)
        ranked = sorted((q for q in pool if (q["item"], q["index"]) not in used),
                        key=lambda q: (round(abs(q["difficulty"] - target) * 2) / 2, q["item"] in used_items, rng.random()))
        if not ranked: return []
        q = ranked[0]; chosen.append(q); used.add((q["item"], q["index"])); used_items.add(q["item"])
    return chosen

class Game:
    """State of one game. Steps are 1-based (the question being asked)."""
    def __init__(self, questions, rng=None):
        self.questions = questions; self.rng = rng or random.Random(); self.step = 1
        self.used = set(); self.hidden = set(); self.over = False; self.won = False; self.walked = False; self.last_answer = None
    @property
    def current(self): return self.questions[self.step - 1]
    @property
    def answer(self): return self.current["q"]["answer"]
    @property
    def banked(self):
        """Prize already won (all questions before this one were right)."""
        return PRIZES[self.step - 2] if self.step > 1 else 0
    @property
    def guaranteed(self):
        safe = [s for s in SAFE_STEPS if s < self.step]
        return PRIZES[max(safe) - 1] if safe else 0
    def choose(self, option):
        """Lock in an answer: True when right. A wrong answer ends the game with the safe prize."""
        if self.over: raise ValueError("game over")
        self.last_answer = option; right = option == self.answer
        if right:
            if self.step == len(PRIZES): self.over = True; self.won = True
        else: self.over = True
        return right
    def advance(self):
        if not self.over: self.step += 1; self.hidden = set()
    def walk_away(self):
        self.over = True; self.walked = True
    def timeout(self):
        self.over = True
    @property
    def prize(self):
        """What the player takes home now."""
        if self.won: return PRIZES[-1]
        if self.walked: return self.banked
        if self.over: return self.guaranteed
        return self.banked
    @property
    def reached(self):
        """Number of questions answered right."""
        return len(PRIZES) if self.won else self.step - 1
    # ------------------------------------------------------------ lifelines
    def fifty(self):
        if "fifty" in self.used or self.over: return set()
        self.used.add("fifty"); wrong = [i for i in range(4) if i != self.answer]
        self.hidden = set(self.rng.sample(wrong, 2)); return self.hidden
    def audience(self):
        """Votes in percent for A–D; the right answer is likelier on easy questions."""
        if "audience" in self.used or self.over: return []
        self.used.add("audience"); d = self.current["difficulty"]
        base = 0.72 if d <= 5 else 0.52 if d <= 10 else 0.38
        p_right = max(0.2, min(0.92, base + self.rng.uniform(-0.12, 0.12)))
        open_ = [i for i in range(4) if i not in self.hidden]
        weights = {i: self.rng.uniform(0.2, 1.0) for i in open_ if i != self.answer}
        total = sum(weights.values()) or 1; votes = [0.0] * 4
        votes[self.answer] = p_right
        for i, w in weights.items(): votes[i] = (1 - p_right) * w / total
        pct = [round(v * 100) for v in votes]; pct[self.answer] += 100 - sum(pct)
        return pct
    def phone(self):
        """Lafa's guess (index, confidence %): usually right, less on hard questions."""
        if "phone" in self.used or self.over: return None
        self.used.add("phone"); d = self.current["difficulty"]
        p = 0.95 if d <= 5 else 0.82 if d <= 10 else 0.66
        open_ = [i for i in range(4) if i not in self.hidden]
        guess = self.answer if self.rng.random() < p else self.rng.choice([i for i in open_ if i != self.answer] or [self.answer])
        conf = int(round((p * 100 if guess == self.answer else 45) + self.rng.uniform(-8, 6)))
        return guess, max(30, min(99, conf))

class Ladder(QWidget):
    """The prize ladder: 15 at the top, the current step highlighted."""
    def __init__(self, parent=None):
        super().__init__(parent); self.step = 1; self.done = 0; self.col = QVBoxLayout(self); self.col.setContentsMargins(0, 0, 0, 0); self.col.setSpacing(3)
        self.rows = []
        for i in range(len(PRIZES), 0, -1):
            row = QLabel(); row.setMinimumHeight(30); self.col.addWidget(row); self.rows.append((i, row))
        self.refresh()
    def set_state(self, step, done): self.step = step; self.done = done; self.refresh()
    def refresh(self):
        t = tok_of(self)
        for i, row in self.rows:
            safe = i in SAFE_STEPS or i == len(PRIZES)
            row.setText(f"  {i:>2}   {'✓ ' if i <= self.done else '◆ ' if safe else '   '}{money(PRIZES[i - 1])}")
            if i == self.step:
                css = f"background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {t['nav_a']}, stop:1 {t['nav_b']}); color:white; font-weight:800; border-radius:12px; padding:4px 8px;"
            elif i <= self.done: css = f"background:{t['ok_soft']}; color:{t['text']}; border-radius:12px; padding:4px 8px; font-weight:700;"
            else: css = f"color:{t['primary'] if safe else t['text2']}; font-weight:{800 if safe else 600}; padding:4px 8px;"
            row.setStyleSheet(css + " font-family: 'Nunito', monospace;")

class MillionairePage(QWidget):
    route = "quiz"
    def __init__(self, win):
        super().__init__(); self.win = win; self.game = None; self.level = win.settings.school_level if win.settings.school_level in kb.LEVELS else "eb3"
        self.category = ""; self.locked = False; self.remaining = 0
        outer = QVBoxLayout(self); outer.setContentsMargins(0, 0, 0, 0)
        self.body = QWidget(); self.col = QVBoxLayout(self.body); self.col.setContentsMargins(0, 0, 8, 16); self.col.setSpacing(16)
        outer.addWidget(scroll(self.body))
        self.clock = QTimer(self); self.clock.setInterval(1000); self.clock.timeout.connect(self.tick)
        self.setFocusPolicy(Qt.StrongFocus)
    def show_route(self, params):
        if params.get("category") in kb.CATEGORY: self.category = params["category"]
        if self.game is None or self.game.over: self.render_start()
    # ------------------------------------------------------------ start screen
    def render_start(self):
        self.clock.stop(); clear_layout(self.col); win = self.win; t = win.t; lang = win.lang; base = win.kb; m = win.progress.millionaire
        hero = Card(24, 28, gradient=(win.tok["nav_a"], win.tok["primary"], win.tok["nav_b"]))
        row = QHBoxLayout(); row.setSpacing(18); row.addWidget(ClayIcon("trophy", "butter", 96), 0, Qt.AlignTop)
        c = QVBoxLayout(); c.setSpacing(6)
        for text_, name, style in ((t("mil_title"), "h1", "color:white;"), (t("mil_sub"), None, "color:rgba(255,255,255,0.94); font-size:16px;"),
                                   (t("mil_rules"), "caption", "color:rgba(255,255,255,0.9);")):
            l = label(text_, name, wrap=True); l.setStyleSheet(style); c.addWidget(l)
        row.addLayout(c, 1); hero.box.addLayout(row); self.col.addWidget(hero)
        setup = Card(20, 24); setup.box.addLayout(section_title(t("mil_start")))
        lv = QHBoxLayout(); lv.addWidget(label(t("mil_level"), "h3")); lv.addSpacing(8)
        seg = Segmented([(k, kb.LEVEL_SHORT[k]) for k in kb.LEVELS], self.level); seg.changed.connect(self.set_level); lv.addWidget(seg); lv.addStretch(); setup.box.addLayout(lv)
        setup.box.addWidget(label(kb.text(kb.LEVEL_NAMES[self.level], lang), "caption"))
        tp = QHBoxLayout(); tp.addWidget(label(t("mil_topic"), "h3")); self.topic = QComboBox(); self.topic.addItem(t("mil_all_topics"), "")
        for cat in kb.CATEGORIES:
            n = len(base.questions(cat.key))
            if n >= 15: self.topic.addItem(f"{kb.text(cat.title, lang)} ({n})", cat.key)
        self.topic.setCurrentIndex(max(0, self.topic.findData(self.category))); self.topic.currentIndexChanged.connect(lambda i: setattr(self, "category", self.topic.itemData(i) or ""))
        tp.addWidget(self.topic, 1); setup.box.addLayout(tp)
        self.timer_box = QCheckBox(t("mil_timer")); self.timer_box.setChecked(bool(win.settings.quiz_timer)); setup.box.addWidget(self.timer_box)
        go = button(t("mil_start"), self.start, "primary", "play"); go.setMinimumHeight(48); setup.box.addWidget(go, 0, Qt.AlignLeft)
        self.start_note = label("", "caption", wrap=True); setup.box.addWidget(self.start_note)
        two = ResponsiveGrid(360, 2, 16); two.add(setup)
        stats = Card(20, 24); stats.box.addLayout(section_title(t("my_progress")))
        grid = QGridLayout(); grid.setSpacing(12)
        for i, (icon_name, acc, title, value) in enumerate((("trophy", "butter", t("mil_best"), money(m.get("best_prize", 0))),
                                                           ("target", "violet", t("mil_games"), str(m.get("games", 0))),
                                                           ("crown", "pink", t("mil_wins"), str(m.get("wins", 0))))):
            box = QHBoxLayout(); box.addWidget(ClayIcon(icon_name, acc, 48)); cc = QVBoxLayout(); cc.setSpacing(0)
            cc.addWidget(label(title, "muted")); cc.addWidget(label(value, "kpi")); box.addLayout(cc, 1); grid.addLayout(box, i, 0)
        stats.box.addLayout(grid)
        ladder = Ladder(); ladder.set_state(0, 0); stats.box.addWidget(label(t("mil_safe").capitalize() + ": " + money(PRIZES[4]) + " · " + money(PRIZES[9]), "caption"))
        stats.box.addStretch(); two.add(stats); self.col.addWidget(two); self.col.addStretch()
    def set_level(self, key): self.level = key; self.render_start()
    def start(self):
        win = self.win; questions = pick_questions(win.kb, self.level, self.category or None)
        if not questions:
            self.start_note.setText(win.t("mil_not_enough", n=len(win.kb.questions(self.category or None)))); return
        win.settings.quiz_timer = self.timer_box.isChecked(); win.save_quietly()
        self.game = Game(questions); self.render_game(); self.setFocus()
    # ------------------------------------------------------------- game screen
    def render_game(self):
        self.clock.stop(); clear_layout(self.col); win = self.win; t = win.t; lang = win.lang; g = self.game; q = g.current["q"]
        self.locked = False; self.revealed = False
        grid = QHBoxLayout(); grid.setSpacing(16)
        main = Card(22, 26); main.box.setSpacing(12)
        head = QHBoxLayout(); head.addWidget(Pill(t("mil_question", i=g.step), "violet")); head.addWidget(Pill(t("mil_for", prize=money(PRIZES[g.step - 1])), "butter"))
        cat = kb.CATEGORY.get(g.current["category"])
        if cat: head.addWidget(Pill(kb.text(cat.title, lang), cat.accent))
        head.addStretch()
        self.ring = None
        if win.settings.quiz_timer:
            self.remaining = time_limit(g.step); self.ring = ProgressRing(1.0, 64, 7, t("mil_seconds", n=self.remaining)); head.addWidget(self.ring)
        main.box.addLayout(head)
        qtext = label(kb.text(q["q"], lang), "h2", wrap=True); qtext.setAlignment(Qt.AlignCenter); qtext.setMinimumHeight(80)
        qtext.setStyleSheet(f"background:{win.tok['primary_soft']}; border-radius:22px; padding:18px 22px;"); main.box.addWidget(qtext)
        answers = QGridLayout(); answers.setSpacing(12); self.buttons = []
        for j, option in enumerate(q["options"]):
            b = button(f"{LETTERS[j]}:  {kb.text(option, lang)}", lambda checked=False, k=j: self.choose(k), "answer"); b.setMinimumHeight(58)
            b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            if j in g.hidden: b.setProperty("state", "hidden"); b.setEnabled(False)
            answers.addWidget(b, j // 2, j % 2); self.buttons.append(b)
        main.box.addLayout(answers)
        life = QHBoxLayout(); life.setSpacing(10)
        self.life_buttons = {}
        for key, icon_name, text_ in (("fifty", "scales", t("mil_fifty")), ("audience", "people", t("mil_audience")), ("phone", "phone", t("mil_phone"))):
            b = button(text_, lambda checked=False, k=key: self.lifeline(k), "chip", icon_name); b.setEnabled(key not in g.used); b.setMinimumHeight(40)
            life.addWidget(b); self.life_buttons[key] = b
        life.addStretch()
        self.walk = button(t("mil_walk", prize=money(g.banked)), self.walk_away, "ghost", "exit"); self.walk.setEnabled(g.step > 1); life.addWidget(self.walk)
        main.box.addLayout(life)
        self.help_box = QVBoxLayout(); main.box.addLayout(self.help_box)
        self.feedback = label("", wrap=True); self.feedback.hide(); main.box.addWidget(self.feedback)
        self.next_button = button(t("mil_next"), self.next_question, "primary", "arrow-right"); self.next_button.hide(); main.box.addWidget(self.next_button, 0, Qt.AlignRight)
        main.box.addWidget(label(t("mil_keys"), "caption"))
        grid.addWidget(main, 3)
        side = Card(14, 24); side.setMinimumWidth(230); side.setMaximumWidth(300); side.box.addWidget(label(t("nav_quiz"), "h3"))
        self.ladder = Ladder(); self.ladder.set_state(g.step, g.step - 1); side.box.addWidget(self.ladder); side.box.addStretch()
        grid.addWidget(side, 1); self.col.addLayout(grid); self.col.addStretch()
        if self.ring: self.clock.start()
    def tick(self):
        if not self.game or self.game.over or self.locked: self.clock.stop(); return
        self.remaining -= 1
        if self.ring: self.ring.set_value(self.remaining / time_limit(self.game.step), self.win.t("mil_seconds", n=max(0, self.remaining)))
        if self.remaining <= 0:
            self.clock.stop(); self.game.timeout(); self.reveal(None)
    def choose(self, k):
        g = self.game
        if not g or g.over or self.locked or k in g.hidden: return
        self.locked = True; self.clock.stop()
        for j, b in enumerate(self.buttons):
            b.setEnabled(False)
            if j == k: b.setProperty("state", "locked"); b.style().unpolish(b); b.style().polish(b)
        for b in self.life_buttons.values(): b.setEnabled(False)
        self.walk.setEnabled(False)
        self.feedback.setText(self.win.t("mil_final")); self.feedback.setStyleSheet(f"background:{self.win.tok['warn_soft']}; border-radius:14px; padding:10px 14px; font-weight:800;"); self.feedback.show()
        delay = 0 if self.win.settings.reduce_motion else 1100
        QTimer.singleShot(delay, lambda game=g, step=g.step: self.reveal(k) if self.game is game and game.step == step and not self.revealed else None)
    def reveal(self, k):
        g = self.game; win = self.win; t = win.t; lang = win.lang; q = g.current["q"]; self.revealed = True
        right = g.choose(k) if k is not None and not g.over else False
        for j, b in enumerate(self.buttons):
            b.setEnabled(False)
            state = "right" if j == g.answer else "wrong" if j == k else ("hidden" if j in g.hidden else "")
            b.setProperty("state", state); b.style().unpolish(b); b.style().polish(b)
        why = kb.text(q.get("why"), lang)
        if right:
            text_ = t("mil_right", prize=money(PRIZES[g.step - 1])); color = win.tok["ok_soft"]
        else:
            text_ = (t("mil_timeout") + " " if k is None else "") + t("mil_wrong", letter=LETTERS[g.answer]); color = win.tok["bad_soft"]
        self.feedback.setText(f"<b>{text_}</b><br>{why}"); self.feedback.setStyleSheet(f"background:{color}; border-radius:14px; padding:10px 14px;"); self.feedback.show()
        try: win.progress.record(f"millionaire:{g.current['item']}:{g.current['index']}", 1 if right else 0, 1)
        except ValueError: pass
        if right and not g.over:
            self.ladder.set_state(g.step, g.step); self.next_button.show(); self.next_button.setFocus()
        else:
            QTimer.singleShot(0 if win.settings.reduce_motion else 1600, self.finish)
    def next_question(self):
        if not self.game or self.game.over or not self.revealed: return
        self.game.advance(); self.render_game(); self.setFocus()
    def walk_away(self):
        if not self.game or self.game.over or self.locked: return
        self.game.walk_away(); self.finish()
    def lifeline(self, key):
        g = self.game; win = self.win; t = win.t; lang = win.lang
        if not g or g.over or self.locked or key in g.used: return
        clear_layout(self.help_box)
        if key == "fifty":
            for j in g.fifty():
                b = self.buttons[j]; b.setProperty("state", "hidden"); b.setEnabled(False); b.style().unpolish(b); b.style().polish(b)
        elif key == "audience":
            votes = g.audience(); box = Card(12, 18); box.box.addWidget(label(t("mil_audience_says"), "h3"))
            chart = BarChart([(LETTERS[i], votes[i]) for i in range(4)], height=150, fmt=lambda v: f"{v:.0f}%"); box.box.addWidget(chart)
            box.box.addWidget(label("   ".join(f"{LETTERS[i]}: {votes[i]}%" for i in range(4) if i not in g.hidden), "caption")); self.help_box.addWidget(box)
        elif key == "phone":
            guess, conf = g.phone(); box = Card(12, 18); row = QHBoxLayout(); face = QLabel()
            face.setPixmap(win.atlas.pixmap("talking", 72, win.settings.costume)); row.addWidget(face)
            item = win.kb.get(g.current["item"]); cc = QVBoxLayout()
            cc.addWidget(label(t("mil_lafa_says", letter=LETTERS[guess], conf=conf), "h3", wrap=True))
            if item: cc.addWidget(label(t("mil_lafa_hint", title=item.title(lang)), "caption", wrap=True))
            row.addLayout(cc, 1); box.box.addLayout(row); self.help_box.addWidget(box)
        self.life_buttons[key].setEnabled(False)
    def finish(self):
        self.clock.stop(); g = self.game; win = self.win; t = win.t; lang = win.lang
        prize = g.prize; reached = g.reached
        new = win.progress.millionaire_game(reached, prize, g.won); win.announce(new); win.update_profile()
        clear_layout(self.col)
        card = Card(26, 28, gradient=(win.tok["nav_a"], win.tok["primary"], win.tok["nav_b"]) if g.won or prize else None)
        card.box.setAlignment(Qt.AlignHCenter)
        card.box.addWidget(ClayIcon("crown" if g.won else "trophy" if prize else "target", "butter", 110), 0, Qt.AlignHCenter)
        title = label(t("mil_winner") if g.won else t("mil_over"), "h1", wrap=True); title.setAlignment(Qt.AlignCenter); card.box.addWidget(title)
        amount = label(t("mil_take_home", prize=money(prize)), "h2"); amount.setAlignment(Qt.AlignCenter); card.box.addWidget(amount)
        if g.won or prize:
            for l in (title, amount): l.setStyleSheet("color:white;")
        row = QHBoxLayout(); row.addStretch(); row.addWidget(button(t("mil_again"), self.start_again, "primary", "refresh"))
        item = win.kb.get(g.current["item"])
        if item: row.addWidget(button(t("mil_learn"), lambda i=item.id: win.open_item(i), None, "book-open"))
        row.addStretch(); card.box.addLayout(row); self.col.addWidget(card)
        ladder_card = Card(16, 24); ladder = Ladder(); ladder.set_state(0, reached); ladder_card.box.addWidget(ladder); self.col.addWidget(ladder_card)
        self.col.addStretch()
    def start_again(self): self.game = None; self.render_start()
    def keyPressEvent(self, e):
        keys = {Qt.Key_1: 0, Qt.Key_2: 1, Qt.Key_3: 2, Qt.Key_4: 3, Qt.Key_A: 0, Qt.Key_B: 1, Qt.Key_C: 2, Qt.Key_D: 3}
        if self.game and not self.game.over and e.key() in keys: self.choose(keys[e.key()]); return
        if e.key() in (Qt.Key_Return, Qt.Key_Enter) and self.game and not self.game.over and getattr(self, "next_button", None) and self.next_button.isVisible():
            self.next_question(); return
        super().keyPressEvent(e)
    def hideEvent(self, e):
        self.clock.stop(); super().hideEvent(e)
    def showEvent(self, e):
        super().showEvent(e)
        if self.game and not self.game.over and not self.locked and getattr(self, "ring", None): self.clock.start()
    def retranslate(self):
        if self.game and not self.game.over: self.render_game()
        else: self.render_start()
