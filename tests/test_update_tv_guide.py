import gzip
import json
from pathlib import Path
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import update_tv_guide as updater

NOW = datetime(2026, 10, 25, 18, tzinfo=timezone.utc)
XML = b'<tv><programme channel="a" start="20261025180000 +0000" stop="20261025190000 +0000"><title>Fixture News</title></programme></tv>'
PROVIDER = {'id': 'fixture', 'url': 'https://example.invalid/guide.xml', 'enabled': True,
            'channelMap': {'a': 'A'}, 'rights': {'publicRedistribution': True, 'commercialUse': True,
            'evidenceUrl': 'https://example.invalid/terms', 'reviewedAt': '2026-10-25'}}

class TestUpdate(unittest.TestCase):
    def run_update(self, providers, raw=XML):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'guide.json'
            target.write_text('{"previous":true}')
            report = updater.update({'providers': providers}, target, lambda _: raw, NOW)
            return report, json.loads(target.read_text())

    def test_normalizes_authorized_source_and_keeps_attribution(self):
        report, data = self.run_update([PROVIDER])
        self.assertEqual(report['status'], 'updated')
        self.assertEqual(data['channels']['A'][0]['end'], '2026-10-25T19:00:00Z')
        self.assertIn('fixture', data['sources'])

    def test_missing_rights_prevents_network_and_preserves_file(self):
        provider = dict(PROVIDER, rights={})
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'guide.json'
            target.write_bytes(b'original')
            def forbidden(_):
                self.fail('Unapproved source must never be fetched')
            report = updater.update({'providers': [provider]}, target, forbidden, NOW)
            self.assertEqual(report['status'], 'preserved')
            self.assertEqual(target.read_bytes(), b'original')

    def test_empty_registry_preserves_last_guide(self):
        report, data = self.run_update([])
        self.assertEqual(report['status'], 'preserved')
        self.assertEqual(data, {'previous': True})

    def test_expired_data_does_not_replace_last_guide(self):
        report, data = self.run_update([PROVIDER], XML.replace(b'20261025', b'20261024'))
        self.assertEqual(report['status'], 'preserved')
        self.assertEqual(data, {'previous': True})

    def test_malformed_providers_preserve_previous(self):
        with tempfile.TemporaryDirectory() as folder:
            report = updater.update({'providers': [dict(PROVIDER, id='bad'), PROVIDER]},
                                    Path(folder) / 'guide.json',
                                    lambda _: b'<broken', NOW)
            self.assertEqual(report['status'], 'preserved')
            self.assertTrue(all(p['status'] == 'failed' for p in report['providers']))

    def test_priority_sources_do_not_duplicate_or_overlap(self):
        report, data = self.run_update([PROVIDER, dict(PROVIDER, id='second')])
        self.assertEqual(report['programmes'], 1)
        self.assertEqual(data['channels']['A'][0]['source'], 'fixture')

    def test_gzip_is_decoded_and_expansion_is_bounded(self):
        class Response:
            def __init__(self, raw): self.raw = raw
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self, size): return self.raw[:size]
            def geturl(self): return 'https://example.invalid/guide.xml'
        with patch.object(updater.urllib.request, 'urlopen', return_value=Response(gzip.compress(XML))):
            self.assertEqual(updater.fetch(PROVIDER['url']), XML)
        with patch.object(updater.urllib.request, 'urlopen', return_value=Response(gzip.compress(b'x' * (updater.MAX_XML_BYTES + 1)))):
            with self.assertRaises(ValueError): updater.fetch(PROVIDER['url'])

    def test_failed_provider_does_not_prevent_working_fallback(self):
        with tempfile.TemporaryDirectory() as folder:
            calls = []
            def fetcher(url):
                calls.append(url)
                if len(calls) == 1: raise OSError('offline')
                return XML
            report = updater.update({'providers': [dict(PROVIDER, id='bad'), PROVIDER]},
                                    Path(folder) / 'guide.json', fetcher, NOW)
            self.assertEqual(report['status'], 'updated')
            self.assertEqual(report['programmes'], 1)
