"""0.2.1: encyclopedia data, navigation, interactive modules, offline pack, icons and walking."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from lafa import encyclopedia as enc, progress, icons
from lafa.config import Settings

ROOT = Path(__file__).resolve().parents[1]

class Data(unittest.TestCase):
    def test_checker_passes(self):
        out = subprocess.run([sys.executable, str(ROOT / "tools/check-encyclopedia.py")], capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr); self.assertIn("✓", out.stdout)
    def test_twelve_world_and_six_timor_categories(self):
        world = [c.key for c in enc.categories("world")]; timor = [c.key for c in enc.categories("timor")]
        self.assertEqual(len(world), 12); self.assertEqual(timor, ["history", "map", "culture", "nature", "leaders", "economy"])
        for c in enc.categories("world"):
            written = [a for a in enc.articles("world", c.key) if a.id.startswith("w.")]
            self.assertGreaterEqual(len(written), 2, c.key)
        for c in enc.categories("world") + enc.categories("timor"):
            self.assertTrue(icons.exists(c.icon), c.icon); self.assertTrue(icons.illustration_exists(c.illustration), c.illustration)
            for lang in ("en", "id", "pt", "tet"): self.assertTrue(enc.text(c.title, lang), (c.key, lang))
    def test_every_article_has_the_parts_of_a_lesson(self):
        for a in enc.all_articles():
            self.assertTrue(enc.objectives(a, "en"), a.id); self.assertTrue(a.sources, a.id)
            self.assertTrue(enc.quiz(a, "en"), a.id)
            for question, options, answer, why in enc.quiz(a, "en"):
                self.assertTrue(question); self.assertIn(answer, range(len(options))); self.assertTrue(why, a.id)
            full, summary = a.languages(); self.assertIn("en", full + summary)
    def test_all_old_atlas_material_is_reachable(self):
        from lafa import timor_atlas
        ids = {a.id for a in enc.all_articles()}
        for t in timor_atlas.TOPICS: self.assertIn("atlas:" + t.key, ids)
        self.assertIn("atlas:presidents", ids); self.assertIn("atlas:prime_ministers", ids)
    def test_search_folds_accents_and_links_areas(self):
        self.assertIn("tl.culture.tais", [a.id for a in enc.search("tais", "en")])
        self.assertTrue(enc.search("atauro", "en")); self.assertTrue(enc.search("ATAÚRO", "en"))
        self.assertEqual(enc.coverage_counts()["available"], len([a for a in enc.all_articles() if a.id.startswith(("w.", "tl."))]))
    def test_progress_scores_are_saved(self):
        with tempfile.TemporaryDirectory() as folder:
            p = progress.Progress(folder); p.record("quiz:w.earth.formation", 3, 4); p.record("quiz:w.earth.formation", 2, 4)
            again = progress.Progress(folder); r = again.result("quiz:w.earth.formation")
            self.assertEqual((r["last"], r["best"], r["total"]), (2, 3, 4))
            with self.assertRaises(ValueError): p.record("x", 5, 4)

class OfflinePack(unittest.TestCase):
    JPEG = b"\xff\xd8\xff\xe0" + b"0" * 2000
    @staticmethod
    def fake_json(url, timeout=15, **kw):
        if "list=search" in url: return {"query": {"search": [{"title": "Dinosaur"}]}}
        if "langlinks" in url: return {"query": {"pages": [{"langlinks": [{"lang": "id", "title": "Dinosaurus"}]}]}}
        if "prop=extracts" in url: return {"query": {"pages": [{"extract": "Dinosaurus adalah kelompok reptil."}]}}
        if "pageimages" in url: return {"query": {"pages": [{"pageimage": "Dino.jpg"}]}}
        if "commons" in url:
            licence = "Fair use" if "Bad" in url else "CC BY-SA 4.0"
            return {"query": {"pages": [{"imageinfo": [{"mime": "image/jpeg", "thumburl": "https://upload.wikimedia.org/x/640px-Dino.jpg",
                    "descriptionurl": "https://commons.wikimedia.org/wiki/File:Dino.jpg", "extmetadata": {"LicenseShortName": {"value": licence}, "Artist": {"value": "<a>Jane</a>"}}}]}]}}
        raise AssertionError(url)
    def test_download_everything_with_licences_and_stop(self):
        from lafa import offline_pack
        with tempfile.TemporaryDirectory() as data, patch.dict(os.environ, {"XDG_DATA_HOME": data}), \
             patch("lafa.offline_pack.json_request", side_effect=self.fake_json), patch("lafa.offline_pack.request", return_value=self.JPEG), \
             patch("lafa.memory.refresh", return_value=(1, 2, 0)), patch("lafa.memory.shared", return_value=object()):
            seen = []; info = offline_pack.Pack("id", progress=lambda d, t, n: seen.append((d, t))).run()
            self.assertFalse(info["stopped"]); self.assertGreater(info["extracts"], 20); self.assertGreater(info["images"], 20)
            self.assertEqual(seen[-1][0], seen[-1][1])
            self.assertEqual(offline_pack.extract("w.dinosaurs.fossils", "id")["text"], "Dinosaurus adalah kelompok reptil.")
            path, meta = offline_pack.image("w.dinosaurs.fossils")
            self.assertTrue(path.is_file()); self.assertEqual(meta["licence"], "CC BY-SA 4.0"); self.assertEqual(meta["author"], "Jane")
            self.assertTrue(str(path).startswith(data)); self.assertEqual(oct(path.stat().st_mode & 0o777), "0o600")
            stopped = offline_pack.Pack("en", stop=lambda: True).run(); self.assertTrue(stopped["stopped"])
    def test_non_free_pictures_are_skipped(self):
        from lafa import offline_pack
        with patch("lafa.offline_pack.json_request", side_effect=self.fake_json):
            self.assertIsNone(offline_pack.commons_info("Bad.jpg")); self.assertIsNotNone(offline_pack.commons_info("Dino.jpg"))

class UI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from lafa.qt import QApplication
        cls.app = QApplication.instance() or QApplication([])
    def setUp(self):
        from lafa.app import Window
        self.w = Window(Settings(language="en"), review=True); self.w.resize(1366, 768); self.w.show(); self.app.processEvents()
    def tearDown(self):
        self.w.companion.close(); self.w.close(); self.w.deleteLater(); self.app.processEvents()
    def test_back_restores_page_and_scroll(self):
        self.w.navigate("timor"); b = self.w.timor_browser; b.go({"kind": "home"}); b.open_category("history")
        scroller = b.page.scroll_widget() if hasattr(b.page, "scroll_widget") else b.page
        scroller.verticalScrollBar().setValue(min(200, scroller.verticalScrollBar().maximum())); kept = scroller.verticalScrollBar().value()
        b.open_article("tl.history.first_people"); self.assertEqual(b.state["kind"], "article")
        crumbs = b.nav.findChild(__import__("lafa.qt", fromlist=["QLabel"]).QLabel, "breadcrumb").text()
        self.assertIn("History", crumbs)
        b.go_back(); self.app.processEvents(); self.assertEqual(b.state, {"kind": "category", "key": "history"})
        scroller = b.page.scroll_widget() if hasattr(b.page, "scroll_widget") else b.page
        for _ in range(5): self.app.processEvents()
        self.assertEqual(scroller.verticalScrollBar().value(), kept)
    def test_cross_area_related_links_and_search(self):
        self.w.navigate("timor"); b = self.w.timor_browser; b.search("tais")
        self.assertEqual(b.state["kind"], "search")
        self.w.open_article("w.dinosaurs.fossils"); self.assertEqual(self.w.current_section(), "study")
        state = self.w.world_browser.state; self.assertEqual((state["kind"], state["id"]), ("article", "w.dinosaurs.fossils"))
    def test_dinosaur_module(self):
        from lafa import interactive
        self.w.navigate("study", "encyclopedia"); wb = self.w.world_browser; wb.open_article("w.dinosaurs.what_are_dinosaurs", "explore")
        m = wb.page.findChild(interactive.DinosaurModule); self.assertIsNotNone(m)
        m.show_hotspot(0); self.assertTrue(m.info.text()); m.show_period("jurassic"); self.assertIn("201", m.info_title.text())
        m.compare.setChecked(True); self.assertTrue(m.chart.isVisibleTo(m)); self.assertIn("12 m", m.info.text())
        for combo, period in m.match: combo.setCurrentIndex(combo.findData(period))
        with patch.object(self.w.progress, "record") as rec: m.check_match()
        rec.assert_called_once_with("activity:dinosaur_periods", len(m.match), len(m.match))
    def test_timeline_keeps_geology_and_human_history_apart(self):
        from lafa import interactive
        self.w.navigate("study", "encyclopedia"); wb = self.w.world_browser; wb.open_article("w.earth.formation", "explore")
        m = wb.page.findChild(interactive.TimelineModule); self.assertIsNotNone(m)
        self.assertEqual(m.events, interactive.GEO); m.show_event(len(m.events) - 1); self.assertTrue(m.title.text())
        m.set_scale("human"); self.assertEqual(m.events, interactive.HUMAN); m.show_event(0); self.assertTrue(m.when.text())
    def test_industry_module(self):
        from lafa import interactive
        self.w.navigate("study", "encyclopedia"); wb = self.w.world_browser; wb.open_article("w.industrial_revolution.steam_factories", "explore")
        m = wb.page.findChild(interactive.IndustryModule); self.assertIsNotNone(m)
        from lafa.qt import Qt
        years = [m.order.item(i).data(Qt.UserRole) for i in range(m.order.count())]
        for target, year in enumerate(sorted(years)):
            row = next(i for i in range(m.order.count()) if m.order.item(i).data(Qt.UserRole) == year)
            item = m.order.takeItem(row); m.order.insertItem(target, item)
        with patch.object(self.w.progress, "record") as rec: m.check_order()
        rec.assert_called_once_with("activity:inventions_order", len(years), len(years))
        for i, (_, truth, _) in enumerate(interactive.IMPACTS): m.answer_impact(i, truth)
        self.assertTrue(all(m.impact_score.values()))
    def test_pages_never_scroll_sideways_on_small_screens(self):
        self.w.resize(1024, 600)
        for area, key in (("timor", "culture"), ("world", "dinosaurs")):
            b = self.w.timor_browser if area == "timor" else self.w.world_browser
            self.w.navigate("timor") if area == "timor" else self.w.navigate("study", "encyclopedia")
            for go in (lambda: b.go({"kind": "home"}), lambda: b.open_category(key)):
                go()
                for _ in range(4): self.app.processEvents()
                page = b.page
                if hasattr(page, "widget") and page.widget(): self.assertLessEqual(page.widget().width(), page.viewport().width(), (area, b.state))
    def test_offline_pack_button_and_popup_routes(self):
        self.w.navigate("library", "sources"); self.assertTrue(self.w.pack_button.isVisibleTo(self.w))
        c = self.w.companion; self.w.desktop_action("explore"); self.assertEqual(self.w.current_section(), "timor")

class Walking(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from lafa.qt import QApplication
        cls.app = QApplication.instance() or QApplication([])
    def test_walk_frames_follow_distance_and_turns(self):
        from lafa.mascot import Atlas, Character
        meta = json.loads((ROOT / "lafa/assets/lafa-walk.json").read_text()); self.assertEqual(meta["frames"], 8)
        atlas = Atlas()
        for costume in ("casual", "tuxedo", "traditional"): self.assertEqual(len(atlas.walk_frames(costume)), 8)
        c = Character(atlas, size=176); c.animate(True); c.set_state("walking"); self.assertEqual(c.walk_index(), 0)   # start: contact pose
        c.advance(0); c.advance(0); step = meta["stride"] * c.walk_scale() / 8
        seen = []
        for _ in range(8): seen.append(c.walk_index()); c.advance(step)
        self.assertEqual(seen, list(range(8)))
        c.direction = -1; self.assertEqual(c.walk_index(), 0)   # turning plants both feet
        c.reduce_motion = True; c.hold = 0; c.distance = step * 3; self.assertEqual(c.walk_index(), 0)
        c.animate(False)
    def test_compact_window_mask_follows_the_character(self):
        from lafa.mascot import Companion, Atlas
        c = Companion(Atlas(), Settings(language="en", companion=True)); c.set_online(False); c.collapse(); c.show(); self.app.processEvents()
        region = c.pet.mask_region(); box = region.boundingRect()
        self.assertFalse(region.isEmpty()); self.assertFalse(region.contains(__import__("lafa.qt", fromlist=["QPoint"]).QPoint(1, 1)))
        self.assertLess(box.width() * box.height(), c.pet.width() * c.pet.height() * 1.3)
        c.toggle_bubble(); self.app.processEvents(); self.assertTrue(c.mask().isEmpty())
        c.input.setText("tais"); c.collapse(); self.assertEqual(c.input.text(), "tais")
        c.close()

if __name__ == "__main__": unittest.main()
