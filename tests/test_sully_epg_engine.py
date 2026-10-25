"""Offline tests: no external feeds, credentials or API calls."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from sully_epg_engine import normalize, parse_timestamp

class TestSullyEPG(unittest.TestCase):
    def test_timezone_conversion(self):
        self.assertEqual(parse_timestamp("20261025180000 -0700"), "2026-10-26T01:00:00Z")
        self.assertEqual(parse_timestamp("20261026010000 +0000"), "2026-10-26T01:00:00Z")

    def test_normalize_and_deduplicate(self):
        xml = b'''<tv><channel id="example.us"><display-name>Example</display-name></channel>
        <programme channel="example.us" start="20261025180000 -0700" stop="20261025190000 -0700"><title>Local News</title></programme>
        <programme channel="example.us" start="20261025180000 -0700" stop="20261025190000 -0700"><title>Local News</title></programme>
        <programme channel="unknown" start="20261025180000 -0700" stop="20261025190000 -0700"><title>Unknown</title></programme></tv>'''
        result = normalize(xml, {"example.us": "sully-news"}, "synthetic-test")
        self.assertEqual(result["matched_channels"], 1)
        self.assertEqual(result["programmes"], 1)
        self.assertEqual(result["channels"]["sully-news"][0]["title"], "Local News")

    def test_rejects_missing_timezone(self):
        with self.assertRaises(ValueError):
            parse_timestamp("20261025180000")

    def test_rejects_entity_declaration(self):
        with self.assertRaises(ValueError):
            normalize(b'<!DOCTYPE tv [<!ENTITY x "bad">]><tv/>', {}, "test")

    def test_skips_invalid_programme(self):
        xml = b'<tv><programme channel="a" start="invalid" stop="invalid"><title>Bad</title></programme></tv>'
        self.assertEqual(normalize(xml, {"a": "A"}, "test")["programmes"], 0)

    def test_rejects_implausibly_long_programme(self):
        xml = b'<tv><programme channel="a" start="20261025010000 +0000" stop="20261027020000 +0000"><title>Impossible</title></programme></tv>'
        self.assertEqual(normalize(xml, {"a": "A"}, "test")["programmes"], 0)

    def test_cli_writes_valid_json_and_preserves_previous_on_empty(self):
        import json
        import tempfile
        from sully_epg_engine import main
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            source = base / "guide.xml"
            mapping = base / "mapping.json"
            target = base / "out.json"
            mapping.write_text('{"a":"A"}', encoding="utf-8")
            source.write_text('<tv><programme channel="a" start="20261025180000 -0700" stop="20261025190000 -0700"><title>News</title></programme></tv>', encoding="utf-8")
            self.assertEqual(main(["engine", str(source), str(mapping), "fixture", str(target)]), 0)
            self.assertEqual(json.loads(target.read_text(encoding="utf-8"))["programmes"], 1)
            original = target.read_bytes()
            source.write_text("<tv/>", encoding="utf-8")
            self.assertEqual(main(["engine", str(source), str(mapping), "fixture", str(target)]), 1)
            self.assertEqual(target.read_bytes(), original)

    def test_rejects_large_xml(self):
        with self.assertRaises(ValueError):
            normalize(b"x" * (5_000_001), {}, "test")

if __name__ == "__main__":
    unittest.main()
