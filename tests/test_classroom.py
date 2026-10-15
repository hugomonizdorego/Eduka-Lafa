"""0.1.2: classroom lessons, quizzes/tests/exams, report card, Timor-Leste and LAFA's roles."""
from datetime import date
import json
from pathlib import Path
import random
import tempfile
import unittest
from lafa import classroom, roles, timorleste, outfits, personality
from lafa.config import Settings
from lafa.i18n import CATALOG, CLASS

ROOT = Path(__file__).resolve().parents[1]

class TimorLesteData(unittest.TestCase):
    def test_history_is_complete_and_translated(self):
        years = [e.year for e in timorleste.HISTORY]
        self.assertEqual(years, sorted(years))
        for key in (1515, 1769, 1975, 1991, 1999, 2002, 2025): self.assertIn(key, years)
        eras = {e.era for e in timorleste.HISTORY}; self.assertEqual(eras, {key for key, _, _ in timorleste.ERAS})
        for e in timorleste.HISTORY:
            for lang in ("en", "id", "pt", "tet"):
                self.assertTrue(e.title[lang] and e.text[lang], (e.year, lang))
        self.assertEqual(len(timorleste.MUNICIPALITIES), 14)
    def test_today_and_next_holiday(self):
        self.assertIn("2002 · Restoration of independence", timorleste.today_in_history(date(2030, 5, 20)))
        self.assertIn("Restoration of Independence Day", timorleste.today_in_history(date(2030, 5, 20)))
        days, when, name = timorleste.next_holiday(date(2026, 10, 6))
        self.assertEqual((days, when, name), (26, date(2026, 11, 1), "All Saints' Day"))
        self.assertEqual(timorleste.next_holiday(date(2026, 12, 31))[0], 0)
    def test_generated_questions_have_one_correct_option(self):
        for q, options, correct in timorleste.history_questions("tet", random.Random(1)):
            self.assertEqual(len(options), 4); self.assertEqual(len(set(options)), 4); self.assertIn(correct, options)

class ClassroomEngine(unittest.TestCase):
    def test_lessons_for_every_subject(self):
        for subject in classroom.SUBJECTS: self.assertTrue(classroom.lessons(subject), subject)
        history = classroom.lessons("history"); self.assertEqual(len(history), len(timorleste.ERAS))
        for lesson in classroom.lessons():
            for lang in ("en", "id", "pt", "tet"):
                self.assertTrue(classroom.text(lesson.title, lang) and classroom.text(lesson.task, lang))
                self.assertTrue(all(classroom.text(p, lang) for p in lesson.points))
    def test_questions_are_valid(self):
        rng = random.Random(3)
        for subject in classroom.SUBJECTS + ["all"]:
            items = classroom.questions(subject, "pt", 10, rng)
            # Never padded with repeats: a small bank gives fewer, different questions.
            self.assertEqual(len(items), min(10, classroom.available(subject, "pt")), subject)
            self.assertEqual(len({q.text for q in items}), len(items), subject)
            for q in items: self.assertIn(q.correct, q.options); self.assertEqual(len(q.options), 4)
    def test_limited_bank_is_announced_and_retry_uses_mistakes(self):
        exam = classroom.ExamSession("exam", "science", "en", random.Random(4))
        self.assertEqual(exam.limited, exam.total < exam.requested)
        for i in range(exam.total): exam.answer(exam.current.correct if i else "wrong")
        retry = exam.retry(); self.assertEqual(retry.total, 1); self.assertEqual(retry.items[0].text, exam.items[0].text)
    def test_exam_session_scores_and_time_limit(self):
        now = [0.0]; exam = classroom.ExamSession("exam", "all", "en", random.Random(5), clock=lambda: now[0])
        self.assertEqual(exam.total, 20); self.assertEqual(exam.time_left(), 1200)
        for i in range(5): exam.answer(exam.current.correct if i % 2 == 0 else "wrong")
        self.assertEqual(exam.score, 3); self.assertEqual(len(exam.mistakes()), 2)
        now[0] = 1201; self.assertTrue(exam.finished); self.assertIsNone(exam.current); self.assertFalse(exam.answer("x"))
        quiz = classroom.ExamSession("quiz", "math", "en", random.Random(1)); self.assertIsNone(quiz.time_left())
        while not quiz.finished: quiz.answer(quiz.current.correct)
        self.assertEqual((quiz.percent, classroom.grade(quiz.percent)), (100, "Excellent"))
        with self.assertRaises(ValueError): classroom.ExamSession("party")
        with self.assertRaises(ValueError): classroom.ExamSession("quiz", "cooking")
    def test_report_card_is_private_and_exportable(self):
        with tempfile.TemporaryDirectory() as folder:
            card = classroom.ReportCard(folder); exam = classroom.ExamSession("test", "science", "en", random.Random(2))
            while not exam.finished: exam.answer(exam.current.correct)
            card.add(exam); path = Path(folder) / "report.json"
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            again = classroom.ReportCard(folder); self.assertEqual(again.summary(), {"science": (1, 100, 100)})
            text = again.export_text("id", "Ana"); self.assertIn("Hasil Latihan · Ana", text); self.assertIn("Sains", text)
            self.assertIn("bukan rapor resmi", text); self.assertNotIn("Rapor ·", text)
            path.write_text(json.dumps([{"bad": 1}, "x"])); self.assertEqual(classroom.ReportCard(folder).entries, [])

class Roles(unittest.TestCase):
    def test_every_role_speaks_every_language(self):
        self.assertEqual(set(roles.ORDER), set(roles.ROLES))
        for role in roles.ORDER:
            for lang in ("en", "id", "pt", "tet"): self.assertTrue(roles.line(role, lang, random.Random(1)))
    def test_mind_reader_finds_every_number(self):
        reader = roles.MindReader()
        for n in range(1, 64):
            self.assertEqual(reader.guess([i for i in range(reader.CARDS) if n in reader.card(i)]), n)
    def test_role_activities_everywhere(self):
        for outfit in outfits.OUTFITS: self.assertTrue(set(outfits.ROLES) <= set(outfits.activities_for(outfit)))
        self.assertEqual(outfits.hat_of("magic_show"), "top_hat"); self.assertEqual(outfits.hat_of("professor"), "mortarboard")
        for lang in ("en", "id", "pt", "tet"):
            for activity in outfits.ROLES: self.assertTrue(personality.activity_name(lang, activity)); self.assertNotEqual(personality.duty(lang, activity), personality.duty(lang, "idle"))
    def test_daily_items_are_stable(self):
        self.assertEqual(roles.daily(roles.MOTIVATION, date(2026, 1, 1)), roles.daily(roles.MOTIVATION, date(2026, 1, 1)))

class Translations(unittest.TestCase):
    def test_new_keys_in_all_languages(self):
        for lang in ("id", "pt", "tet"): self.assertEqual(set(CLASS[lang]), set(CLASS["en"]), lang)
        for key in ("classroom", "exams", "report_card", "roles", "today_in_history"): self.assertNotEqual(CATALOG["tet"][key], key)

class OutfitArt(unittest.TestCase):
    """The committed sheets from tools/make-outfits.py (checked with Qt, so no numpy)."""
    @classmethod
    def setUpClass(cls):
        from lafa.qt import QApplication
        cls.app = QApplication.instance() or QApplication([])
    @staticmethod
    def crops(image, manifest):
        from lafa.qt import QImage
        sheet = QImage(str(ROOT / "lafa/assets" / image)); meta = json.loads((ROOT / "lafa/assets" / manifest).read_text())
        return {state: sheet.copy(*meta["rects"][state]) for state in meta["states"]}
    def test_every_activity_dressed_except_bathing_and_toilet(self):
        base = {**self.crops("lafa-atlas.png", "atlas.json"), **self.crops("lafa-activities.png", "activities.json")}
        for name in ("tuxedo", "casual"):
            dressed = self.crops(f"lafa-{name}.png", f"{name}.json"); self.assertEqual(set(dressed), set(base), name)
            for state, image in dressed.items():
                self.assertEqual(image.size(), base[state].size(), (name, state))
                self.assertEqual(image == base[state], state in ("bathing", "toilet"), (name, state))
        tais = self.crops("lafa-tais.png", "tais.json")
        self.assertIn("sleeping", tais); self.assertFalse(tais["sleeping"] == base["sleeping"])

class SchoolPages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from lafa.qt import QApplication
        cls.app = QApplication.instance() or QApplication([])
    def setUp(self):
        from lafa.app import Window
        self.w = Window(Settings(language="en"), review=True); self.w.show(); self.app.processEvents()
    def tearDown(self):
        if getattr(self.w, "mind_dialog", None): self.w.mind_dialog.close()
        self.w.companion.close(); self.w.close(); self.w.deleteLater(); self.app.processEvents()
    def test_sidebar_sections(self):
        from lafa.app import PAGES
        self.assertEqual([k for k, _ in PAGES], ["home", "study", "library", "timor", "activities", "oshelp"])
        self.assertEqual(self.w.page_title("study"), "Learn"); self.assertEqual(self.w.t("report_card"), "Practice results")
        # An average score is labelled as such, never as "completed".
        self.w.navigate("report"); header = [self.w.report_summary.horizontalHeaderItem(i).text() for i in range(5)]
        self.assertIn("Average score", header); self.assertFalse(any("complete" in h.lower() for h in header))
    def test_lesson_to_quiz_to_report(self):
        self.w.navigate("classroom"); self.w.class_subject.setCurrentIndex(self.w.class_subject.findData("science"))
        self.assertIn("water", self.w.lesson_title.text().lower())
        self.w.quiz_current_lesson(); self.assertEqual(self.w.exam.subject, "science"); self.assertEqual(self.w.exam.kind, "quiz")
        while not self.w.exam.finished:
            q = self.w.exam.current; self.w.answer_exam(next(i for i, b in enumerate(self.w.exam_buttons) if b.property("option") == q.correct)); self.w.show_exam_question()
        self.w.finish_exam(); self.assertIn("5/5", self.w.exam_question.text())
        self.assertEqual(self.w.report_summary.rowCount(), 1); self.assertEqual(self.w.report_summary.item(0, 2).text(), "100%")
        self.assertTrue(str(self.w.report.path).startswith(str(self.w.planner.folder)))
    def test_exam_timer_ends_exam(self):
        self.w.start_exam("exam", "all"); self.assertTrue(self.w.exam_timer.isActive())
        self.w.exam.started -= 2000; self.w.tick_exam(); self.assertFalse(self.w.exam_timer.isActive()); self.assertIn("0/20", self.w.exam_question.text())
    def test_entertainment_is_optional(self):
        self.assertFalse(hasattr(self.w, "role_pet")); self.assertNotIn("fun", [self.w.section_tabs["study"].tabText(i) for i in range(self.w.section_tabs["study"].count())])
        from lafa.app import Window
        self.w.companion.close(); self.w.close(); self.w.deleteLater(); self.app.processEvents()
        self.w = Window(Settings(language="en", entertainment=True), review=True)
        self.w.play_role("magician"); self.assertEqual(self.w.role_pet.state, "magic_show"); self.assertFalse(self.w.mind_button.isHidden())
        self.w.open_mind_reader()
        for i in range(6): self.w.mind_dialog.mind_answer(i in (1, 3))
        self.app.processEvents(); self.assertIn("10", "".join(l.text() for l in self.w.mind_dialog.findChildren(type(self.w.role_text))))
        self.w.companion.play_role("motivator"); self.assertEqual(self.w.companion.state, "motivator")
    def test_timor_page(self):
        self.w.navigate("culture"); b = self.w.timor_browser
        # Six illustrated categories, then News and Weather as separate "needs internet" entries.
        self.assertEqual(len(__import__("lafa.encyclopedia", fromlist=["x"]).categories("timor")), 6)
        b.open_article("atlas:history_17")
        from lafa.qt import QLabel
        self.assertEqual(b.page.findChild(QLabel, "articletitle").text(), "Restoration of independence")
        self.w.navigate("timor", "news"); self.assertEqual(b.state["kind"], "special")
        # Home stays calm: news and entertainment are not shown there.
        self.assertFalse(hasattr(self.w, "home_news"))

if __name__ == "__main__": unittest.main()
