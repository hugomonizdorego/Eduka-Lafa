"""Jogu Istória — games with the dates of Timor-Leste's history.

Three games use the dated events of the encyclopedia (the same events as the
timeline): "Which came first?" (two events), "Put them in order" (four events)
and "Which year?" (four years to choose from). Three levels: easy events are
far apart in time, hard ones close together and may come from prehistory.
Ten rounds per game; the result is kept with the learner's quiz results.
The game logic (`HistoryGame`) is separate from the screen so it can be tested.
"""
import random

from ...qt import Qt, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from ... import kb, icons
from ..texts import extend
from ..widgets import (Card, Clickable, ClayIcon, Pill, Segmented, ProgressLine, ResponsiveGrid, label, button, scroll, section_title,
                       clear_layout, rounded, clip)

extend({
    "hg_title": ("Jogu Istória", "Jogo da História", "History Game", "Permainan Sejarah"),
    "hg_sub": ("Halimar ho data istória Timór-Leste nian: husi ema dahuluk to'o 2026. Ronda 10, fásil to'o susar.",
               "Jogue com as datas da história de Timor-Leste: dos primeiros povos até 2026. Dez rondas, do fácil ao difícil.",
               "Play with the dates of Timor-Leste's history, from the first people to 2026. Ten rounds, from easy to hard.",
               "Bermain dengan tanggal-tanggal sejarah Timor-Leste, dari manusia pertama hingga 2026. Sepuluh ronde, dari mudah sampai sulit."),
    "hg_choose": ("Hili jogu", "Escolha o jogo", "Choose a game", "Pilih permainan"),
    "hg_first": ("Saida mak uluk?", "O que veio primeiro?", "Which came first?", "Mana yang lebih dulu?"),
    "hg_first_text": ("Eventu rua: hili ida ne'ebé akontese uluk.", "Dois acontecimentos: escolha o que aconteceu primeiro.",
                      "Two events: pick the one that happened first.", "Dua peristiwa: pilih yang terjadi lebih dulu."),
    "hg_order": ("Hatuur tuir orden", "Pôr por ordem", "Put them in order", "Urutkan"),
    "hg_order_text": ("Eventu haat: klik sira husi uluk liu to'o foin daudaun.", "Quatro acontecimentos: clique do mais antigo ao mais recente.",
                      "Four events: click them from the oldest to the newest.", "Empat peristiwa: klik dari yang paling lama ke yang paling baru."),
    "hg_year": ("Tinan saida?", "Em que ano?", "Which year?", "Tahun berapa?"),
    "hg_year_text": ("Eventu ida no tinan haat: hili tinan loos.", "Um acontecimento e quatro anos: escolha o ano certo.",
                     "One event and four years: pick the right year.", "Satu peristiwa dan empat tahun: pilih tahun yang benar."),
    "hg_level": ("Nível", "Nível", "Level", "Tingkat"),
    "hg_easy": ("Fásil", "Fácil", "Easy", "Mudah"),
    "hg_medium": ("Médiu", "Médio", "Medium", "Sedang"),
    "hg_hard": ("Susar", "Difícil", "Hard", "Sulit"),
    "hg_start": ("Hahú", "Começar", "Start", "Mulai"),
    "hg_best": ("Rezultadu di'ak liu: {best}/{total}", "Melhor resultado: {best}/{total}", "Best result: {best}/{total}", "Hasil terbaik: {best}/{total}"),
    "hg_round": ("Ronda {i}/{n}", "Ronda {i}/{n}", "Round {i}/{n}", "Ronde {i}/{n}"),
    "hg_points": ("Pontu {n}", "{n} pontos", "{n} points", "{n} poin"),
    "hg_streak": ("Loos dala {n} tuir malu", "{n} certas seguidas", "{n} right in a row", "{n} benar berturut-turut"),
    "hg_q_first": ("Eventu ida-ne'ebé mak akontese uluk?", "Qual destes aconteceu primeiro?", "Which of these happened first?", "Mana yang terjadi lebih dulu?"),
    "hg_q_order": ("Klik eventu sira husi uluk liu to'o foin daudaun.", "Clique nos acontecimentos do mais antigo ao mais recente.",
                   "Click the events from the oldest to the newest.", "Klik peristiwa dari yang paling lama ke yang paling baru."),
    "hg_q_year": ("Eventu ida-ne'e akontese iha tinan saida?", "Em que ano aconteceu isto?", "In which year did this happen?", "Pada tahun berapa ini terjadi?"),
    "hg_check": ("Verifika", "Verificar", "Check", "Periksa"),
    "hg_clear": ("Hamoos", "Limpar", "Clear", "Hapus"),
    "hg_right": ("Loos!", "Certo!", "Right!", "Benar!"),
    "hg_wrong": ("La loos. Haree data sira iha okos.", "Errado. Veja as datas abaixo.", "Not quite. Look at the dates below.", "Kurang tepat. Lihat tanggalnya di bawah."),
    "hg_next": ("Tuir mai", "Seguinte", "Next", "Lanjut"),
    "hg_finish": ("Haree rezultadu", "Ver o resultado", "See the result", "Lihat hasil"),
    "hg_done": ("Jogu remata!", "Fim do jogo!", "Game over!", "Permainan selesai!"),
    "hg_score": ("Ita hatán loos {n} husi {total}.", "Acertou {n} de {total}.", "You got {n} out of {total} right.", "Kamu menjawab benar {n} dari {total}."),
    "hg_praise_3": ("Di'ak tebes! Ita matenek istória.", "Excelente! Conhece bem a história.", "Excellent! You know your history.", "Luar biasa! Kamu menguasai sejarah."),
    "hg_praise_2": ("Di'ak! Lee tan atu hetan pontu tomak.", "Bom! Leia mais para acertar tudo.", "Good! Read a little more to get them all.", "Bagus! Baca lagi supaya benar semua."),
    "hg_praise_1": ("Kontinua aprende — liña tempu bele ajuda.", "Continue a aprender — a linha do tempo ajuda.", "Keep learning — the timeline can help.", "Terus belajar — lini masa bisa membantu."),
    "hg_again": ("Halimar fali", "Jogar outra vez", "Play again", "Main lagi"),
    "hg_other": ("Hili jogu seluk", "Escolher outro jogo", "Choose another game", "Pilih permainan lain"),
    "hg_review": ("Eventu sira iha jogu ne'e", "Os acontecimentos deste jogo", "The events of this game", "Peristiwa dalam permainan ini"),
    "hg_read": ("Lee", "Ler", "Read", "Baca"),
    "hg_timeline": ("Loke liña tempu", "Abrir a linha do tempo", "Open the timeline", "Buka lini masa"),
    "hg_too_few": ("Eventu seidauk to'o ba nível ida-ne'e.", "Ainda não há acontecimentos suficientes para este nível.",
                   "There are not enough events for this level yet.", "Belum cukup peristiwa untuk tingkat ini."),
})

MODES = ("first", "order", "year")
MODE_ICONS = {"first": ("timeline", "peach"), "order": ("tasks", "mint"), "year": ("calendar-check", "sky")}
ROUNDS = 10
# Easy: events at least 50 years apart since 1500; medium: 10 years; hard: any distinct dates, prehistory included.
LEVELS = {"easy": {"gap": 50, "since": 1500, "near": (25, 90)},
          "medium": {"gap": 10, "since": 1500, "near": (4, 25)},
          "hard": {"gap": 1, "since": -100000, "near": (1, 6)}}


class HistoryGame:
    """Ten rounds of one game; questions come from the dated events of the timeline."""

    def __init__(self, events, mode="first", level="easy", rng=None, rounds=ROUNDS):
        if mode not in MODES or level not in LEVELS: raise ValueError("unknown game or level")
        self.mode, self.level, self.rounds = mode, level, rounds
        self.rng = rng or random.Random()
        cfg = LEVELS[level]
        since = max(cfg["since"], 1500) if mode == "year" else cfg["since"]   # "which year" needs a real calendar year
        pool, seen = [], set()
        for e in events:
            y = e["key"][0]
            if y < since or y > 2100 or not e.get("title") or len(e["title"]) > 150: continue
            if e["title"] in seen: continue
            seen.add(e["title"]); pool.append(e)
        self.pool = pool
        self.round = 0; self.score = 0; self.streak = 0; self.best_streak = 0
        self.used = set(); self.played = []; self.question = None; self.answered = False; self.last_correct = None

    def can_play(self):
        return len(self.pool) >= {"first": 8, "order": 12, "year": 8}[self.mode]

    def finished(self): return self.round >= self.rounds and self.answered

    # ----------------------------------------------------------- questions
    def _fresh(self):
        fresh = [e for e in self.pool if e["title"] not in self.used]
        return fresh if len(fresh) >= 6 else list(self.pool)

    def _far_apart(self, chosen, e):
        gap = LEVELS[self.level]["gap"]
        return all(e["key"] != c["key"] and abs(e["key"][0] - c["key"][0]) >= gap for c in chosen)

    def _pick(self, n):
        for _ in range(200):
            candidates = self._fresh(); self.rng.shuffle(candidates); chosen = []
            for e in candidates:
                if self._far_apart(chosen, e): chosen.append(e)
                if len(chosen) == n: return chosen
        raise ValueError("not enough events")

    def next_question(self):
        if self.round >= self.rounds: return None
        self.round += 1; self.answered = False; self.last_correct = None
        if self.mode == "first":
            a, b = self._pick(2)
            self.question = {"events": [a, b], "answer": 0 if a["key"] < b["key"] else 1}
        elif self.mode == "order":
            events = self._pick(4)
            self.question = {"events": events, "answer": sorted(range(4), key=lambda i: events[i]["key"])}
        else:
            e = self._pick(1)[0]; year = e["key"][0]; lo, hi = LEVELS[self.level]["near"]
            options = {year}
            while len(options) < 4:
                guess = year + self.rng.choice((-1, 1)) * self.rng.randint(lo, hi)
                if 1400 <= guess <= 2026: options.add(guess)
            options = sorted(options)
            self.question = {"events": [e], "options": options, "answer": options.index(year)}
        for e in self.question["events"]: self.used.add(e["title"])
        return self.question

    def answer(self, choice):
        """choice: an index (first, year) or the list of event indices in the learner's order (order)."""
        if self.question is None or self.answered: return self.last_correct
        q = self.question
        correct = list(choice) == q["answer"] if self.mode == "order" else choice == q["answer"]
        self.answered = True; self.last_correct = correct
        if correct:
            self.score += 1; self.streak += 1; self.best_streak = max(self.best_streak, self.streak)
        else:
            self.streak = 0
        self.played.extend(q["events"])
        return correct

    def points(self):
        """10 points for each right answer and a bonus for streaks (shown during the game)."""
        return self.score * 10 + max(0, self.best_streak - 2) * 5


class HistoryGamePage(QWidget):
    route = "history_game"

    def __init__(self, win):
        super().__init__(); self.win = win; self.mode = "first"; self.level = "easy"; self.game = None; self.order = []; self.choice = None
        outer = QVBoxLayout(self); outer.setContentsMargins(0, 0, 0, 0)
        self.body = QWidget(); self.col = QVBoxLayout(self.body); self.col.setContentsMargins(0, 0, 8, 16); self.col.setSpacing(16)
        outer.addWidget(scroll(self.body))

    def show_route(self, params):
        if params.get("mode") in MODES: self.mode = params["mode"]
        if params.get("level") in LEVELS: self.level = params["level"]
        self.game = None; self.render()

    def retranslate(self): self.render()

    def key(self): return f"game.history.{self.mode}.{self.level}"

    def events(self): return self.win.kb.timeline(self.win.lang)

    # ------------------------------------------------------------------ ui
    def hero(self):
        win = self.win; t = win.t
        hero = Card(20, 26, gradient=(win.tok["nav_a"], win.tok["primary"], win.tok["nav_b"]))
        row = QHBoxLayout(); row.setSpacing(18); col = QVBoxLayout(); col.setSpacing(6)
        title = label(t("hg_title"), "h1", wrap=True); title.setStyleSheet("color:white;"); col.addWidget(title)
        sub = label(t("hg_sub"), wrap=True); sub.setStyleSheet("color:rgba(255,255,255,0.92); font-size:15px;"); col.addWidget(sub)
        row.addLayout(col, 1)
        pic = QLabel(); pic.setPixmap(rounded(icons.illustration("independence", 260, 130), 18)); row.addWidget(pic, 0, Qt.AlignVCenter)
        hero.box.addLayout(row); return hero

    def render(self):
        clear_layout(self.col); self.col.addWidget(self.hero())
        if self.game is None: self.render_setup()
        elif self.game.finished(): self.render_result()
        else: self.render_round()
        self.col.addStretch()

    def render_setup(self):
        win = self.win; t = win.t; prog = win.progress
        self.col.addLayout(section_title(t("hg_choose")))
        grid = ResponsiveGrid(250, 3, 14)
        for mode in MODES:
            icon, acc = MODE_ICONS[mode]
            card = Clickable(16, 22); card.set_selected(mode == self.mode)
            top = QHBoxLayout(); top.setSpacing(12); top.addWidget(ClayIcon(icon, acc, 52))
            cc = QVBoxLayout(); cc.setSpacing(2); cc.addWidget(label(t("hg_" + mode), "h3", wrap=True)); cc.addWidget(label(t(f"hg_{mode}_text"), "caption", wrap=True))
            top.addLayout(cc, 1); card.box.addLayout(top)
            best = prog.result(f"game.history.{mode}.{self.level}") if prog else None
            if best: card.box.addWidget(Pill(t("hg_best", best=best["best"], total=best["total"]), acc), 0, Qt.AlignLeft)
            card.clicked.connect(lambda m=mode: self.choose_mode(m)); grid.add(card)
        self.col.addWidget(grid)
        bar = QHBoxLayout(); bar.setSpacing(12); bar.addWidget(label(t("hg_level"), "h3"))
        seg = Segmented([(lv, t("hg_" + lv)) for lv in LEVELS], self.level); seg.changed.connect(self.choose_level); bar.addWidget(seg)
        bar.addStretch(); start = button(t("hg_start"), self.start, "primary", "play"); start.setMinimumHeight(48); bar.addWidget(start)
        self.col.addLayout(bar)
        if not HistoryGame(self.events(), self.mode, self.level).can_play():
            self.col.addWidget(label(t("hg_too_few"), "muted", wrap=True))

    def choose_mode(self, mode): self.mode = mode; self.render()
    def choose_level(self, level): self.level = level; self.render()

    def start(self):
        game = HistoryGame(self.events(), self.mode, self.level)
        if not game.can_play(): self.win.toast.show_text(self.win.t("hg_too_few")); return
        self.game = game; game.next_question(); self.order = []; self.choice = None; self.render()

    def status_bar(self):
        win = self.win; t = win.t; g = self.game
        bar = QHBoxLayout(); bar.setSpacing(10)
        bar.addWidget(Pill(t("hg_round", i=g.round, n=g.rounds), "lilac")); bar.addWidget(Pill(t("hg_points", n=g.points()), "butter"))
        if g.streak >= 2: bar.addWidget(Pill(t("hg_streak", n=g.streak), "coral"))
        bar.addStretch(); return bar

    def event_card(self, e, i, state=None, number=None, show_date=False):
        """One event as a card: state None / 'right' / 'wrong' / 'picked'."""
        win = self.win; lang = win.lang
        tint = {"right": win.tok.get("ok_soft", "#dff7e6"), "wrong": win.tok.get("danger_soft", "#ffe4e7")}.get(state)
        card = Clickable(14, 20, tint=tint); card.set_selected(state == "picked")
        row = QHBoxLayout(); row.setSpacing(12)
        badge = label(str(number) if number else str(i + 1), "h3"); badge.setFixedSize(30, 30); badge.setAlignment(Qt.AlignCenter)
        badge.setStyleSheet(f"background:{win.tok['primary'] if number else win.tok['line']}; color:{'white' if number else win.tok['text']}; border-radius:15px;")
        row.addWidget(badge, 0, Qt.AlignTop)
        cc = QVBoxLayout(); cc.setSpacing(3); cc.addWidget(label(kb.show(e["title"], lang), "h3", wrap=True))
        cat = kb.CATEGORY.get(e.get("category"))
        if cat: cc.addWidget(label(kb.text(cat.title, lang), "caption"))
        if show_date:
            d = label(kb.format_when(e["date"], lang), "h3"); d.setStyleSheet(f"color:{win.tok['primary']}; font-size:17px;"); cc.addWidget(d)
        row.addLayout(cc, 1); card.box.addLayout(row)
        return card

    def render_round(self):
        win = self.win; t = win.t; g = self.game; q = g.question
        card = Card(18, 24); card.box.addLayout(self.status_bar())
        card.box.addWidget(ProgressLine((g.round - (0 if g.answered else 1)) / g.rounds, 8))
        card.box.addWidget(label(t({"first": "hg_q_first", "order": "hg_q_order", "year": "hg_q_year"}[g.mode]), "h2", wrap=True))
        if g.mode == "first":
            grid = ResponsiveGrid(280, 2, 14)
            for i, e in enumerate(q["events"]):
                state = None
                if g.answered: state = "right" if i == q["answer"] else ("wrong" if i == self.choice else None)
                c = self.event_card(e, i, state, show_date=g.answered)
                if not g.answered: c.clicked.connect(lambda i=i: self.choose(i))
                grid.add(c)
            card.box.addWidget(grid)
        elif g.mode == "order":
            grid = ResponsiveGrid(280, 2, 14)
            right_place = {idx: pos for pos, idx in enumerate(q["answer"])}
            for i, e in enumerate(q["events"]):
                number = (self.order.index(i) + 1) if i in self.order else None
                state = "picked" if number and not g.answered else None
                if g.answered: state = "right" if number and number - 1 == right_place[i] else "wrong"
                c = self.event_card(e, i, state, number=(right_place[i] + 1) if g.answered else number, show_date=g.answered)
                if not g.answered: c.clicked.connect(lambda i=i: self.toggle_order(i))
                grid.add(c)
            card.box.addWidget(grid)
            if not g.answered:
                row = QHBoxLayout(); row.addStretch()
                row.addWidget(button(t("hg_clear"), self.clear_order, "ghost", "refresh"))
                check = button(t("hg_check"), self.check_order, "primary", "check"); check.setEnabled(len(self.order) == 4); row.addWidget(check)
                card.box.addLayout(row)
        else:
            e = q["events"][0]
            card.box.addWidget(self.event_card(e, 0, show_date=g.answered))
            opts = ResponsiveGrid(150, 4, 12)
            for i, year in enumerate(q["options"]):
                b = button(str(year), (lambda checked=False, i=i: self.choose(i)), "primary" if g.answered and i == q["answer"] else None)
                b.setMinimumHeight(56)
                if g.answered:
                    b.setEnabled(i == q["answer"] or i == self.choice)
                    if i == self.choice and i != q["answer"]: b.setStyleSheet(f"background:{win.tok.get('danger_soft', '#ffe4e7')};")
                opts.add(b)
            card.box.addWidget(opts)
        if g.answered:
            fb = label(t("hg_right") if g.last_correct else t("hg_wrong"), "h2")
            fb.setStyleSheet(f"color:{win.tok.get('ok', '#1f9d55') if g.last_correct else win.tok.get('danger', '#d62839')};"); card.box.addWidget(fb)
            row = QHBoxLayout(); row.addStretch()
            last = g.round >= g.rounds
            nxt = button(t("hg_finish") if last else t("hg_next"), self.advance, "primary", "arrow-right"); nxt.setMinimumHeight(46); row.addWidget(nxt)
            card.box.addLayout(row)
        self.col.addWidget(card)

    def choose(self, i):
        if self.game is None or self.game.answered: return
        self.choice = i; correct = self.game.answer(i); self.after_answer(correct)

    def toggle_order(self, i):
        if self.game is None or self.game.answered: return
        if i in self.order: self.order.remove(i)
        elif len(self.order) < 4: self.order.append(i)
        self.render()

    def clear_order(self): self.order = []; self.render()

    def check_order(self):
        if len(self.order) == 4: self.after_answer(self.game.answer(list(self.order)))

    def after_answer(self, correct):
        self.render()

    def advance(self):
        g = self.game
        if g.round >= g.rounds:
            prog = self.win.progress
            if prog:
                try: prog.record(self.key(), g.score, g.rounds)
                except (ValueError, OSError): pass
        else:
            g.next_question(); self.order = []; self.choice = None
        self.render()

    def render_result(self):
        win = self.win; t = win.t; lang = win.lang; g = self.game
        card = Card(20, 26); top = QHBoxLayout(); top.setSpacing(16)
        top.addWidget(ClayIcon("trophy", "butter", 72))
        cc = QVBoxLayout(); cc.setSpacing(4); cc.addWidget(label(t("hg_done"), "h1"))
        cc.addWidget(label(t("hg_score", n=g.score, total=g.rounds), "h2"))
        ratio = g.score / max(1, g.rounds)
        cc.addWidget(label(t("hg_praise_3" if ratio >= 0.8 else "hg_praise_2" if ratio >= 0.5 else "hg_praise_1"), "muted", wrap=True))
        pills = QHBoxLayout(); pills.addWidget(Pill(t("hg_points", n=g.points()), "butter"))
        if g.best_streak >= 2: pills.addWidget(Pill(t("hg_streak", n=g.best_streak), "coral"))
        pills.addStretch(); cc.addLayout(pills); top.addLayout(cc, 1); card.box.addLayout(top)
        row = QHBoxLayout(); row.addWidget(button(t("hg_again"), self.start, "primary", "refresh"))
        row.addWidget(button(t("hg_other"), self.back_to_setup, "ghost", "grid"))
        row.addWidget(button(t("hg_timeline"), lambda: win.open("timeline"), "ghost", "timeline")); row.addStretch(); card.box.addLayout(row)
        self.col.addWidget(card)
        # Review: every event of the game with its date, oldest first, and a link to its article.
        rc = Card(16, 24); rc.box.addLayout(section_title(t("hg_review")))
        seen = set()
        for e in sorted(g.played, key=lambda e: e["key"]):
            if e["title"] in seen: continue
            seen.add(e["title"])
            r = QHBoxLayout(); r.setSpacing(10)
            d = label(kb.format_when(e["date"], lang), "h3"); d.setMinimumWidth(150); d.setStyleSheet(f"color:{win.tok['primary']};"); r.addWidget(d, 0, Qt.AlignTop)
            r.addWidget(label(clip(kb.show(e["title"], lang), 160), wrap=True), 1)
            if e.get("item"): r.addWidget(button(t("hg_read"), lambda checked=False, i=e["item"]: win.open_item(i), "ghost"), 0, Qt.AlignTop)
            rc.box.addLayout(r)
        self.col.addWidget(rc)

    def back_to_setup(self): self.game = None; self.render()

    def keyPressEvent(self, e):
        g = self.game
        if g is not None and not g.finished():
            k = e.key()
            if g.answered and k in (Qt.Key_Return, Qt.Key_Enter): self.advance(); return
            if not g.answered and g.mode in ("first", "year") and Qt.Key_1 <= k <= Qt.Key_4:
                i = k - Qt.Key_1
                if i < (2 if g.mode == "first" else 4): self.choose(i); return
        super().keyPressEvent(e)
