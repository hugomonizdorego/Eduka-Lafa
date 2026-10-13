"""Automatic source updates: strict catalog validation, caching, merging, releases."""
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from lafa import updates, tools, school, osguide
from lafa.net import NetworkError

GOOD = {"revision": 2099010101, "resources": [["Open textbook", "https://example.org/book"]],
        "teachers": {"math": [["Fractions", "https://example.org/fractions"]], "BAD KEY": [["x", "https://example.org/x"]]},
        "cards": [{"id": "new-card", "category": "nature", "source": "https://example.org/c", "checked_on": "2026-10-07", "text": {"en": "Fact", "tet": "Faktu"}},
                  {"id": "bad", "category": "spam", "checked_on": "2026-10-07", "text": {"en": "x"}}],
        "tips": {"en": ["New tip"]}, "tools": {"wifi": ["nm-applet", "rm -rf"]}}

class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.env = patch.dict(os.environ, {"XDG_CACHE_HOME": self.temp.name}); self.env.start()
    def tearDown(self):
        self.env.stop(); self.temp.cleanup()
    def test_shipped_catalog_is_valid(self):
        data = updates.validate(json.loads(updates.SHIPPED.read_text()))
        self.assertGreater(data["revision"], 2026000000); self.assertTrue(data["cards"])
    def test_validation_rejects_unsafe_content(self):
        clean = updates.validate(GOOD)
        self.assertNotIn("BAD KEY", clean["teachers"]); self.assertEqual([c["id"] for c in clean["cards"]], ["new-card"])
        self.assertEqual(clean["tools"]["wifi"], ["nm-applet"])
        for bad in [{"revision": "1"}, {"revision": 5, "resources": [["x", "http://plain.example/x"]]},
                    {"revision": 5, "resources": [["x", "https://user:pw@example.org/x"]]}, {"revision": 5, "teachers": []}, []]:
            with self.assertRaises(updates.CatalogError): updates.validate(bad)
    def test_check_caches_newer_revision_only(self):
        changed, revision = updates.check(lambda: json.dumps(GOOD).encode(), now=100.0)
        self.assertTrue(changed); self.assertEqual(revision, GOOD["revision"]); self.assertEqual(updates.current()["revision"], GOOD["revision"])
        self.assertEqual(updates.last_check(), 100.0); self.assertFalse(updates.due(24, now=100.0 + 3600)); self.assertTrue(updates.due(1, now=100.0 + 3601))
        older = dict(GOOD, revision=3)
        self.assertEqual(updates.check(lambda: json.dumps(older).encode()), (False, GOOD["revision"]))
        with self.assertRaises(NetworkError): updates.check(lambda: b"<html>not json</html>")
        self.assertEqual(updates.current()["revision"], GOOD["revision"])
    def test_apply_merges_without_duplicates(self):
        catalog = updates.validate(GOOD)
        before_tools = osguide.BY_KEY["wifi"].tools
        try:
            first = updates.apply(catalog); second = updates.apply(catalog)
            self.assertGreater(first, 0); self.assertEqual(second, 0)
            self.assertIn(("Open textbook", "https://example.org/book"), tools.RESOURCES)
            self.assertIn(("Fractions", "https://example.org/fractions"), school.BY_KEY["math"].resources)
            self.assertIn("nm-applet", osguide.BY_KEY["wifi"].tools); self.assertIn("New tip", osguide.TIPS["en"])
        finally:
            tools.RESOURCES[:] = [r for r in tools.RESOURCES if r[1] != "https://example.org/book"]
            school.BY_KEY["math"].resources[:] = [r for r in school.BY_KEY["math"].resources if r[1] != "https://example.org/fractions"]
            osguide.BY_KEY["wifi"].tools = before_tools; osguide.TIPS["en"].remove("New tip")
    def test_cards_from_catalog_join_the_deck(self):
        updates.check(lambda: json.dumps(GOOD).encode())
        from lafa.timor import CardDeck
        self.assertIn("new-card", [c["id"] for c in CardDeck().cards])

class ReleaseTests(unittest.TestCase):
    def test_version_ordering(self):
        k = updates.version_key
        self.assertLess(k("0.1.0a1"), k("0.1.0")); self.assertLess(k("0.1.0"), k("0.1.1a1")); self.assertLess(k("0.1.1"), k("0.2.0")); self.assertLess(k("0.9.9"), k("0.10.0"))
    def test_newer_release(self):
        with patch("lafa.updates.__version__", "0.1.1"):
            self.assertEqual(updates.newer_release(lambda: {"tag_name": "v0.1.2"}), "0.1.2")
            self.assertIsNone(updates.newer_release(lambda: {"tag_name": "v0.1.1"}))
            self.assertIsNone(updates.newer_release(lambda: {"tag_name": "latest; rm -rf"}))

if __name__ == "__main__": unittest.main()
