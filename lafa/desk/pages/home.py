"""Pájina inisiál — the dashboard (greeting, stats, calendar, word of the day,
today in history, charts, place of the week and achievements)."""
from datetime import date, datetime

from ...qt import Qt, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QSizePolicy, QPixmap
from ... import kb, icons
from ..texts import extend
from ..theme import ACCENTS, accent
from ..widgets import (Card, Clickable, ClayIcon, StatCard, CourseCard, CalendarCard, Donut, AreaChart, ProgressRing, Pill,
                       ResponsiveGrid, Banner, label, button, legend, scroll, section_title, clear_layout, EmptyState)
from ...progress import ACHIEVEMENTS

extend({
    "shuffle": ("Seluk", "Outro", "Lainnya", "Another"),
    "learn_word": ("Aprende liafuan", "Aprender palavras", "Belajar kata", "Learn words"),
    "open_calendar": ("Loke kalendáriu", "Abrir calendário", "Buka kalender", "Open calendar"),
    "unit_progress": ("{done} husi {n} lee ona", "{done} de {n} lidos", "{done} dari {n} dibaca", "{done} of {n} read"),
    "group_history": ("Istória", "História", "Sejarah", "History"),
    "group_state": ("Estadu no mundu", "Estado e mundo", "Negara dan dunia", "State and world"),
    "group_land": ("Rai no natureza", "Terra e natureza", "Daratan dan alam", "Land and nature"),
    "group_culture": ("Kultura no sosiedade", "Cultura e sociedade", "Budaya dan masyarakat", "Culture and society"),
    "group_economy": ("Ekonomia no turizmu", "Economia e turismo", "Ekonomi dan wisata", "Economy and tourism"),
    "items_total": ("pájina", "páginas", "halaman", "pages"),
    "ach_first_read": ("Lee dahuluk", "Primeira leitura", "Bacaan pertama", "First read"),
    "ach_reader_10": ("Lee-na'in", "Leitor", "Pembaca", "Reader"),
    "ach_reader_50": ("Matenek-na'in", "Sábio", "Cendekia", "Scholar"),
    "ach_explorer": ("Esploradór", "Explorador", "Penjelajah", "Explorer"),
    "ach_municipalities": ("Munisípiu hotu", "Todos os municípios", "Semua munisipio", "All municipalities"),
    "ach_words_50": ("Liafuan 50", "50 palavras", "50 kata", "50 words"),
    "ach_words_200": ("Liafuan 200", "200 palavras", "200 kata", "200 words"),
    "ach_quiz_perfect": ("Kuis perfeitu", "Quiz perfeito", "Kuis sempurna", "Perfect quiz"),
    "ach_millionaire_safe": ("Fatin seguru", "Patamar seguro", "Titik aman", "Safe haven"),
    "ach_millionaire_win": ("Milionáriu!", "Milionário!", "Jutawan!", "Millionaire!"),
    "ach_streak_7": ("Semana ida tomak", "Uma semana seguida", "Seminggu penuh", "7-day streak"),
})

ACH_ICON = {"first_read": ("book-open", "violet"), "reader_10": ("scroll", "pink"), "reader_50": ("graduation", "lilac"), "explorer": ("umbrella", "cyan"),
            "municipalities": ("map", "teal"), "words_50": ("translate", "mint"), "words_200": ("chat", "green"), "quiz_perfect": ("target", "coral"),
            "millionaire_safe": ("shield", "sky"), "millionaire_win": ("trophy", "butter"), "streak_7": ("sun", "peach")}
GROUPS = [("group_history", ("history", "colonial", "conflicts"), "lilac"), ("group_state", ("politics", "leaders", "symbols", "world"), "violet"),
          ("group_land", ("land", "nature", "geography"), "mint"), ("group_culture", ("culture", "society", "calendar"), "butter"),
          ("group_economy", ("economy", "tourism"), "sky")]

def achievement_title(lang, key):
    from ..texts import t
    return t(lang, "ach_" + key) if not key.startswith("unit:") else key

def greeting_key(hour):
    return "greet_morning" if 4 <= hour < 12 else "greet_afternoon" if 12 <= hour < 18 else "greet_evening"

def word_of_day(base, when=None):
    words = [w for w in base.words if w.level <= 2] or base.words
    if not words: return None
    when = when or date.today()
    return words[(when.toordinal() * 7 + 3) % len(words)]

def facts_pool(base, lang):
    """Short "did you know" lines: article facts with a value, or summaries."""
    out = []
    for item in base.all():
        for f in item.get("facts") or []:
            if isinstance(f, dict) and f.get("label") and f.get("value"):
                value = kb.text(f["value"], lang) if isinstance(f["value"], dict) else str(f["value"])
                out.append((item, f"{kb.text(f['label'], lang)}: {value}"))
    return out

class HomePage(QWidget):
    route = "home"
    def __init__(self, win):
        super().__init__(); self.win = win; self.fact_offset = 0
        outer = QVBoxLayout(self); outer.setContentsMargins(0, 0, 0, 0)
        self.body = QWidget(); self.col = QVBoxLayout(self.body); self.col.setContentsMargins(0, 0, 8, 12); self.col.setSpacing(16)
        outer.addWidget(scroll(self.body))
    def show_route(self, params):
        clear_layout(self.col); win = self.win; lang = win.lang; base = win.kb; t = win.t; prog = win.progress
        today = date.today()
        # 1. Hero: greeting with Lafa (gradient card, reference image 3).
        hero = Card(22, 26, gradient=(win.tok["nav_a"], win.tok["primary"], win.tok["nav_b"]))
        row = QHBoxLayout(); row.setSpacing(18); text_col = QVBoxLayout(); text_col.setSpacing(6)
        name = win.settings.learner_name or __import__("lafa.app", fromlist=["first_name"]).first_name() or t("learner")
        hi = label(f"{t(greeting_key(datetime.now().hour))}, {name}! 👋", "h1", wrap=True); hi.setStyleSheet("color:white;")
        sub = label(t("home_sub"), wrap=True); sub.setStyleSheet("color:rgba(255,255,255,0.92); font-size:16px;")
        text_col.addWidget(hi); text_col.addWidget(sub); text_col.addSpacing(8)
        buttons = QHBoxLayout(); buttons.setSpacing(10)
        b1 = button(t("start_learning"), lambda: win.open("paths"), None, "graduation"); b1.setStyleSheet("background:white; color:#3b2a8f; border:2px solid white; border-radius:16px; padding:10px 18px;")
        b2 = button(t("play_quiz"), lambda: win.open("quiz"), None, "trophy"); b2.setStyleSheet("background:rgba(255,255,255,0.18); color:white; border:2px solid rgba(255,255,255,0.7); border-radius:16px; padding:10px 18px;")
        from ..widgets import refresh_icon
        refresh_icon(b1, "#3b2a8f"); refresh_icon(b2, "#ffffff"); buttons.addWidget(b1); buttons.addWidget(b2); buttons.addStretch(); text_col.addLayout(buttons)
        streak = prog.streak
        if streak > 1:
            s = label("🔥 " + t("streak", n=streak)); s.setStyleSheet("color:white; font-weight:800;"); text_col.addWidget(s)
        row.addLayout(text_col, 1)
        pic = QLabel(); pic.setPixmap(win.atlas.pose_pixmap(win.settings.costume, 170) if hasattr(win.atlas, "pose_pixmap") else win.atlas.pixmap("idle", 170, win.settings.costume))
        pic.setAlignment(Qt.AlignBottom | Qt.AlignRight); row.addWidget(pic, 0, Qt.AlignBottom)
        hero.box.addLayout(row); self.col.addWidget(hero)
        # 2. Stats.
        stats = base.stats(); read = prog.read
        grid = ResponsiveGrid(230, 4)
        for icon_name, acc, key, value, note, route in (
                ("book-open", "violet", "stat_articles", stats["articles"], t("stat_articles_note", n=sum(1 for k in read if k.startswith("tl."))), "encyclopedia"),
                ("map", "mint", "stat_municipalities", stats["municipalities"] or 14, t("stat_municipalities_note", n=sum(1 for k in read if k.startswith("mun."))), "map"),
                ("umbrella", "butter", "stat_places", stats["places"], t("stat_places_note", n=sum(1 for k in read if k.startswith("place."))), "places"),
                ("translate", "coral", "stat_words", stats["words"], t("stat_words_note", n=prog.words_learned()), "language")):
            card = StatCard(icon_name, acc, t(key), value, note, animate=not win.settings.reduce_motion); card.clicked.connect(lambda r=route: win.open(r)); grid.add(card)
        self.col.addWidget(grid)
        # 3. Continue learning + calendar.
        two = ResponsiveGrid(420, 2, 16)
        learn = Card(18, 24); learn.box.addLayout(section_title(t("continue_learning"), button(t("see_all"), lambda: win.open("paths"), "ghost")))
        units = base.path(win.settings.school_level) if base.all("article") else []
        shown = 0
        for unit in units:
            items = unit["items"]; done = sum(1 for i in items if prog.is_read(i.id))
            if done >= len(items) and shown < 1 and len(units) > 3: continue
            cat = kb.CATEGORY[unit["category"]]
            card = CourseCard(cat.icon, cat.accent, kb.text(cat.title, lang), t("unit_progress", done=done, n=len(items)), done / max(1, len(items)))
            card.clicked.connect(lambda c=unit["category"]: win.open("paths", category=c)); learn.box.addWidget(card); shown += 1
            if shown >= 3: break
        if shown == 0: learn.box.addWidget(EmptyState("book-open", t("empty_content"), t("empty_content_text")))
        learn.box.addStretch(); two.add(learn)
        cal = Card(18, 24); cal.box.addLayout(section_title(t("upcoming_days"), button(t("open_calendar"), lambda: win.open("calendar"), "ghost")))
        calendar = CalendarCard(lang); marks = {}
        for when, d in base.days_in_year(today.year) + base.days_in_year(today.year + 1):
            marks[when] = ("rose" if d.get("type") == "holiday" else "violet", d.title(lang))
        calendar.set_marks(marks); calendar.day_clicked.connect(lambda when: self.open_day(when)); cal.box.addWidget(calendar)
        for when, d in base.upcoming(today, 3):
            delta = (when - today).days
            r = Clickable(8, 16); line = QHBoxLayout(); line.setSpacing(10)
            line.addWidget(ClayIcon("calendar-check", "rose" if d.get("type") == "holiday" else "violet", 36))
            c2 = QVBoxLayout(); c2.setSpacing(0); c2.addWidget(label(d.title(lang), "h3", wrap=True)); c2.addWidget(label(kb.format_date(when, lang), "caption")); line.addLayout(c2, 1)
            line.addWidget(Pill(t("today") if delta == 0 else t("tomorrow") if delta == 1 else t("in_days", n=delta), "rose" if delta <= 7 else "slate"))
            r.box.addLayout(line); r.clicked.connect(lambda i=d.id: win.open_item(i)); cal.box.addWidget(r)
        two.add(cal); self.col.addWidget(two)
        # 4. Today in history · word of the day · did you know.
        three = ResponsiveGrid(300, 3, 16)
        hist = Card(18, 24); events = base.today_in_history(today, lang)
        title = t("today_history")
        if not events:
            events = [e for e in base.timeline(lang) if str(e["date"])[5:7] == f"{today.month:02d}" and len(str(e["date"])) >= 7]; title = t("this_month_history")
        hist.box.addLayout(section_title(title)); hist.box.addWidget(ClayIcon("scroll", "lilac", 44))
        for e in events[:3]:
            r = Clickable(6, 14); c2 = QVBoxLayout(); c2.setSpacing(0)
            c2.addWidget(label(kb.format_when(e["date"], lang), "eyebrow")); c2.addWidget(label(e["title"], wrap=True)); r.box.addLayout(c2)
            r.clicked.connect(lambda i=e["item"]: win.open_item(i)); hist.box.addWidget(r)
        if not events: hist.box.addWidget(label(t("empty_content_text"), "muted", wrap=True))
        hist.box.addStretch(); three.add(hist)
        word = word_of_day(base, today); wc = Card(18, 24); wc.box.addLayout(section_title(t("word_of_day")))
        if word:
            big = label(kb.show(word.tet, "tet"), "h1", wrap=True); wc.box.addWidget(big)
            target = win.settings.vocab_lang
            for code in dict.fromkeys([target, "pt", "id", "en"]):
                if word.meaning(code):
                    line = QHBoxLayout(); line.addWidget(Pill(code.upper(), "mint" if code == target else "slate")); line.addWidget(label(word.meaning(code), wrap=True), 1); wc.box.addLayout(line)
            ex = word.ex.get("tet") if isinstance(word.ex, dict) else None
            if ex: wc.box.addWidget(label(f"“{kb.show(ex, 'tet')}”", "muted", wrap=True))
        else: wc.box.addWidget(label(t("empty_content_text"), "muted", wrap=True))
        wc.box.addStretch(); wc.box.addWidget(button(t("learn_word"), lambda: win.open("language"), "ghost", "translate")); three.add(wc)
        facts = facts_pool(base, lang); fc = Card(18, 24)
        more = button(t("shuffle"), self.next_fact, "ghost", "shuffle"); fc.box.addLayout(section_title(t("did_you_know"), more))
        if facts:
            item, line_text = facts[(today.toordinal() + self.fact_offset * 17) % len(facts)]
            fc.box.addWidget(Banner(lambda w, h, k=item.illustration(): icons.illustration(k, w, h), 120, 18))
            fc.box.addWidget(label(line_text, "h3", wrap=True)); fc.box.addWidget(label(item.title(lang), "caption", wrap=True))
            fc.box.addStretch(); fc.box.addWidget(button(t("read_more"), lambda i=item.id: win.open_item(i), "ghost", "arrow-right"))
        else: fc.box.addWidget(label(t("empty_content_text"), "muted", wrap=True))
        three.add(fc); self.col.addWidget(three)
        # 5. Charts: population (World Bank), content by theme, my progress.
        charts = ResponsiveGrid(320, 3, 16)
        pop = next((i for i in base.indicators if i.get("id") == "SP.POP.TOTL"), None)
        pc = Card(18, 24); pc.box.addLayout(section_title(t("population_chart")))
        if pop and len(pop.get("series", [])) >= 2:
            series = sorted((int(y), float(v)) for y, v in pop["series"] if isinstance(v, (int, float)))
            chart = AreaChart([(y, v) for y, v in series], win.tok["primary"]); pc.box.addWidget(chart)
            pc.box.addWidget(label(f"{t('source_label')}: {pop.get('source', 'World Bank')} · {pop.get('licence', 'CC BY 4.0')}", "caption", wrap=True))
        else: pc.box.addWidget(label(t("empty_content_text"), "muted", wrap=True))
        charts.add(pc)
        counts = base.category_counts(); segments = []
        for key, cats, acc in GROUPS: segments.append((t(key), sum(counts.get(c, 0) for c in cats), accent(acc)[0]))
        dc = Card(18, 24); dc.box.addLayout(section_title(t("content_chart")))
        drow = QHBoxLayout(); total = sum(v for _, v, _ in segments)
        donut = Donut(segments, str(total), t("items_total"), 160); drow.addWidget(donut); drow.addWidget(legend(segments, lambda v: f"{v:g}"), 1); dc.box.addLayout(drow)
        charts.add(dc)
        mc = Card(18, 24); mc.box.addLayout(section_title(t("my_progress")))
        done = len([k for k in read if k in base.items]); allc = max(1, len(base.items))
        ring = ProgressRing(done / allc, 150, 14, caption=t("progress_caption")); mc.box.addWidget(ring, 0, Qt.AlignHCenter)
        mc.box.addWidget(label(t("xp_level", n=prog.level_name, xp=prog.xp), "h3"), 0, Qt.AlignHCenter)
        charts.add(mc); self.col.addWidget(charts)
        # 6. Place of the week.
        places = base.places()
        if places:
            place = places[(today.isocalendar()[1] * 5) % len(places)]
            pw = Clickable(14, 24); pw.box.addLayout(section_title(t("place_of_week")))
            prow = QHBoxLayout(); prow.setSpacing(16)
            banner = Banner(lambda w, h, k=place.illustration(): icons.illustration(k, w, h), 170, 20); banner.setMinimumWidth(260); prow.addWidget(banner, 2)
            pcol = QVBoxLayout(); pcol.addWidget(label(place.title(lang), "h2", wrap=True))
            mun = base.get(place.get("municipality", "")); tags = QHBoxLayout()
            if mun: tags.addWidget(Pill(mun.title(lang), "teal"))
            tags.addWidget(Pill(str(place.get("type", "")).replace("_", " "), "cyan")); tags.addStretch(); pcol.addLayout(tags)
            pcol.addWidget(label(place.summary(lang), "muted", wrap=True)); pcol.addStretch()
            brow = QHBoxLayout(); brow.addWidget(button(t("read_more"), lambda i=place.id: win.open_item(i), "primary")); brow.addWidget(button(t("show_on_map"), lambda i=place.id: win.open("map", place=i), None, "map")); brow.addStretch()
            pcol.addLayout(brow); prow.addLayout(pcol, 3); pw.box.addLayout(prow); pw.clicked.connect(lambda i=place.id: win.open_item(i))
            self.col.addWidget(pw)
        # 7. Achievements (reference image 3: "UNLOCKED").
        ac = Card(18, 24); ac.box.addLayout(section_title(t("achievements")))
        grid2 = ResponsiveGrid(150, 6, 12)
        for key, _test in ACHIEVEMENTS:
            got = key in prog.achievements; icon_name, acc = ACH_ICON.get(key, ("star", "violet"))
            tile = Card(10, 18, tint=None); tile.box.setAlignment(Qt.AlignHCenter)
            ic = ClayIcon(icon_name, acc if got else "slate", 52); tile.box.addWidget(ic, 0, Qt.AlignHCenter)
            name_l = label(achievement_title(lang, key), "h3", wrap=True); name_l.setAlignment(Qt.AlignCenter); tile.box.addWidget(name_l)
            badge = Pill(t("unlocked") if got else t("locked"), "green" if got else "slate"); tile.box.addWidget(badge, 0, Qt.AlignHCenter)
            if not got: tile.setGraphicsEffect(None); ic.setEnabled(False)
            grid2.add(tile)
        ac.box.addWidget(grid2); self.col.addWidget(ac)
        self.col.addStretch()
    def next_fact(self):
        self.fact_offset += 1; self.show_route({})
    def open_day(self, when):
        for d in self.win.kb.days():
            if self.win.kb.day_date(d, when.year) == when: self.win.open_item(d.id); return
        self.win.open("calendar", month=when.isoformat())
    def retranslate(self): self.show_route({})
