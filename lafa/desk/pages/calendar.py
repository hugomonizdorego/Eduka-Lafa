"""Kalendáriu: public holidays and national days of Timor-Leste for any year
(fixed dates, Easter-based dates and the Islamic feasts), the next holiday,
a month calendar and export to an .ics file for other calendar apps."""
from datetime import date, timedelta
from pathlib import Path

from ...qt import Qt, QWidget, QVBoxLayout, QHBoxLayout, QFileDialog
from ... import kb
from ..texts import extend
from ..widgets import Card, Clickable, ClayIcon, Pill, CalendarCard, ResponsiveGrid, label, button, scroll, section_title, clear_layout, EmptyState

extend({
    "cal_title": ("Feriadu no loron nasionál {year}", "Feriados e dias nacionais {year}", "Hari libur dan hari nasional {year}", "Holidays and national days {year}"),
    "cal_sub": ("Tuir Lei n.º 10/2005 (muda ho Lei n.º 3/2016). Governu hatoo kada tinan data ba feriadu ne'ebé muda.", "Segundo a Lei n.º 10/2005 (alterada pela Lei n.º 3/2016). O Governo publica todos os anos as datas móveis.",
                "Menurut Undang-Undang No. 10/2005 (diubah dengan UU No. 3/2016). Pemerintah mengumumkan tanggal yang berubah setiap tahun.", "Under Law No. 10/2005 (amended by Law No. 3/2016). The Government announces the moving dates every year."),
    "next_holiday": ("Feriadu tuir mai", "Próximo feriado", "Hari libur berikutnya", "Next holiday"),
    "days_left": ("loron {n} tan", "faltam {n} dias", "{n} hari lagi", "{n} days to go"),
    "export_ics": ("Esporta ba kalendáriu (.ics)", "Exportar para calendário (.ics)", "Ekspor ke kalender (.ics)", "Export to calendar (.ics)"),
    "exported": ("Rai ona: {path}", "Guardado: {path}", "Tersimpan: {path}", "Saved: {path}"),
    "prev_year": ("Tinan liubá", "Ano anterior", "Tahun sebelumnya", "Previous year"),
    "next_year": ("Tinan oin", "Ano seguinte", "Tahun berikutnya", "Next year"),
    "past": ("Liu ona", "Já passou", "Sudah lewat", "Past"),
    "calendar_notes": ("Nota", "Notas", "Catatan", "Notes"),
    "approx_islamic": ("Data Islám sira tuir lua no bele muda loron ida.", "As datas islâmicas seguem a lua e podem variar um dia.", "Tanggal hari raya Islam mengikuti bulan dan bisa bergeser sehari.", "Islamic dates follow the moon and may move by a day."),
})

def ics_text(base, year, lang="en"):
    """An iCalendar file with the holidays and national days of one year."""
    def esc(value): return str(value).replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Lafa//Ensiklopedia Timor-Leste//TET", "CALSCALE:GREGORIAN", f"X-WR-CALNAME:{esc('Timor-Leste ' + str(year))}"]
    for when, d in base.days_in_year(year):
        lines += ["BEGIN:VEVENT", f"UID:{d.id}-{year}@lafa.edukasaun", f"DTSTAMP:{date.today():%Y%m%d}T000000Z",
                  f"DTSTART;VALUE=DATE:{when:%Y%m%d}", f"DTEND;VALUE=DATE:{when + timedelta(days=1):%Y%m%d}",
                  f"SUMMARY:{esc(d.title(lang))}", f"DESCRIPTION:{esc(d.summary(lang))}",
                  f"CATEGORIES:{'HOLIDAY' if d.get('type') == 'holiday' else 'COMMEMORATION'}", "TRANSP:TRANSPARENT", "END:VEVENT"]
    lines.append("END:VCALENDAR")
    # RFC 5545: lines end with CRLF and are folded at 75 octets.
    out = []
    for line in lines:
        raw = line.encode("utf-8")
        while len(raw) > 75:
            cut = 75
            while (raw[cut] & 0xC0) == 0x80: cut -= 1
            out.append(raw[:cut].decode("utf-8")); raw = b" " + raw[cut:]
        out.append(raw.decode("utf-8"))
    return "\r\n".join(out) + "\r\n"

class CalendarPage(QWidget):
    route = "calendar"
    def __init__(self, win):
        super().__init__(); self.win = win; self.year = date.today().year; self.month = None
        outer = QVBoxLayout(self); outer.setContentsMargins(0, 0, 0, 0)
        self.body = QWidget(); self.col = QVBoxLayout(self.body); self.col.setContentsMargins(0, 0, 8, 16); self.col.setSpacing(16)
        outer.addWidget(scroll(self.body))
    def show_route(self, params):
        month = params.get("month")
        if month:
            try: d = date.fromisoformat(str(month)[:10]); self.year = d.year; self.month = d.replace(day=1)
            except ValueError: pass
        self.render()
    def render(self):
        clear_layout(self.col); win = self.win; t = win.t; lang = win.lang; base = win.kb; today = date.today()
        days = base.days_in_year(self.year)
        head = Card(20, 24); row = QHBoxLayout(); row.setSpacing(14); row.addWidget(ClayIcon("calendar-check", "rose", 60))
        c = QVBoxLayout(); c.setSpacing(2); c.addWidget(label(t("cal_title", year=self.year), "h1", wrap=True)); c.addWidget(label(t("cal_sub"), "muted", wrap=True)); row.addLayout(c, 1)
        prev = button("", lambda: self.go(-1), "icon", "back", t("prev_year")); prev.setFixedSize(40, 40); row.addWidget(prev)
        year = label(str(self.year), "h2"); row.addWidget(year)
        nxt = button("", lambda: self.go(1), "icon", "chevron-right", t("next_year")); nxt.setFixedSize(40, 40); row.addWidget(nxt)
        head.box.addLayout(row)
        actions = QHBoxLayout(); actions.addWidget(button(t("export_ics"), self.export, None, "download")); actions.addStretch(); head.box.addLayout(actions)
        self.col.addWidget(head)
        if not days:
            self.col.addWidget(EmptyState("calendar-check", t("empty_content"), t("empty_content_text"))); self.col.addStretch(); return
        upcoming = base.upcoming(today, 1, holidays_only=True)
        if upcoming:
            when, d = upcoming[0]; delta = (when - today).days
            hero = Clickable(20, 26, gradient=(win.tok["nav_a"], win.tok["primary"], win.tok["nav_b"]))
            hrow = QHBoxLayout(); hrow.setSpacing(16); hrow.addWidget(ClayIcon("star", "butter", 64))
            hc = QVBoxLayout(); hc.setSpacing(2)
            for text_, name, style in ((t("next_holiday").upper(), "eyebrow", "color:rgba(255,255,255,0.85);"), (d.title(lang), "h1", "color:white;"),
                                       (kb.format_date(when, lang), "h3", "color:white;")):
                l = label(text_, name, wrap=True); l.setStyleSheet(style); hc.addWidget(l)
            hrow.addLayout(hc, 1)
            big = label(t("today") if delta == 0 else t("tomorrow") if delta == 1 else t("days_left", n=delta), "h2"); big.setStyleSheet("color:white; background:rgba(255,255,255,0.18); border-radius:16px; padding:10px 18px;")
            hrow.addWidget(big, 0, Qt.AlignVCenter); hero.box.addLayout(hrow); hero.clicked.connect(lambda i=d.id: win.open_item(i)); self.col.addWidget(hero)
        two = ResponsiveGrid(380, 2, 16)
        cal_card = Card(18, 24); cal_card.box.addLayout(section_title(t("nav_calendar")))
        cal = CalendarCard(lang); cal.setMinimumHeight(330)
        cal.month = self.month if self.month and self.month.year == self.year else (today.replace(day=1) if today.year == self.year else date(self.year, 1, 1))
        marks = {when: ("rose" if d.get("type") == "holiday" else "violet", d.title(lang)) for when, d in days}
        cal.set_marks(marks); cal.day_clicked.connect(self.open_day); cal_card.box.addWidget(cal)
        legend = QHBoxLayout(); legend.addWidget(Pill(t("holiday"), "rose")); legend.addWidget(Pill(t("commemorative"), "violet")); legend.addStretch(); cal_card.box.addLayout(legend)
        notes = kb.text(base.days_notes, lang) if base.days_notes else ""
        cal_card.box.addWidget(label(notes or t("approx_islamic"), "caption", wrap=True)); cal_card.box.addStretch()
        two.add(cal_card)
        lst = Card(16, 24); lst.box.addLayout(section_title(t("cal_title", year=self.year)))
        current_month = None
        for when, d in days:
            if when.month != current_month:
                current_month = when.month; lst.box.addWidget(label(kb.month_name(when.month, lang).upper(), "eyebrow"))
            r = Clickable(8, 16); line = QHBoxLayout(); line.setSpacing(12)
            badge = label(f"{when.day:02d}", "h2"); badge.setFixedWidth(44); badge.setAlignment(Qt.AlignCenter); line.addWidget(badge)
            cc = QVBoxLayout(); cc.setSpacing(0); cc.addWidget(label(d.title(lang), "h3", wrap=True))
            cc.addWidget(label(kb.WEEKDAYS.get(lang, kb.WEEKDAYS["en"])[when.weekday()] + (" · " + (t("holiday") if d.get("type") == "holiday" else t("commemorative"))), "caption"))
            line.addLayout(cc, 1); delta = (when - today).days
            if delta < 0: line.addWidget(Pill(t("past"), "slate"))
            elif delta <= 60: line.addWidget(Pill(t("today") if delta == 0 else t("tomorrow") if delta == 1 else t("in_days", n=delta), "rose" if delta <= 7 else "butter"))
            if delta < 0: r.setWindowOpacity(0.7)
            r.box.addLayout(line); r.clicked.connect(lambda i=d.id: win.open_item(i)); lst.box.addWidget(r)
        two.add(lst); self.col.addWidget(two); self.col.addStretch()
    def go(self, step): self.year += step; self.month = None; self.render()
    def open_day(self, when):
        for d in self.win.kb.days():
            if self.win.kb.day_date(d, when.year) == when: self.win.open_item(d.id); return
    def export(self):
        win = self.win; default = str(Path.home() / f"Timor-Leste-{self.year}.ics")
        path, _ = QFileDialog.getSaveFileName(self, win.t("export_ics"), default, "iCalendar (*.ics)")
        if not path: return
        try:
            Path(path).write_text(ics_text(win.kb, self.year, win.lang), encoding="utf-8"); win.toast.show_text(win.t("exported", path=path))
        except OSError as e: win.toast.show_text(str(e))
    def retranslate(self): self.render()
