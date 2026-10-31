"""Discovery must write a readable catalog, preserve entries and deduplicate."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('discovery', Path(__file__).resolve().parents[1] / 'scripts/discover_library.py')
discovery = importlib.util.module_from_spec(spec)
spec.loader.exec_module(discovery)


def video(pid, license_name='CC BY 4.0'):
    return {'pageid': pid, 'title': 'File:Nature_documentary.webm', 'imageinfo': [{
        'url': 'https://upload.wikimedia.org/example.webm', 'mime': 'video/webm',
        'extmetadata': {key: {'value': value} for key, value in {
            'LicenseShortName': license_name, 'LicenseUrl': 'https://creativecommons.org/licenses/by/4.0/',
            'ImageDescription': 'A nature documentary', 'Artist': '<b>Filmmaker</b>'}.items()}}]}


class DiscoveryTests(unittest.TestCase):
    def test_roundtrip_and_repeat_run(self):
        with tempfile.TemporaryDirectory() as folder:
            catalog = Path(folder) / 'catalog.json'
            original = {'id': 'existing', 'title': 'Existing title'}
            catalog.write_text(json.dumps({'items': [original]}))
            result = {'query': {'pages': [video(1), video(2, 'All rights reserved'), video(3, 'Public domain')]}}
            with patch.object(discovery, 'CATALOG', catalog), patch.object(discovery, 'SEARCHES', ['fixture']), patch.object(discovery, 'request', return_value=result), patch.object(discovery.time, 'sleep'):
                discovery.discover()
                first_bytes = catalog.read_bytes()
                data = json.loads(first_bytes)
                self.assertEqual(data['items'][0], original)
                self.assertEqual(len(data['items']), 3)
                item = data['items'][1]
                self.assertEqual(item['title'], 'Nature documentary')
                self.assertEqual(item['status'], 'pending-playback')
                self.assertNotIn('lastChecked', item)
                self.assertEqual(item['genres'], ['Documentary', 'Nature'])
                self.assertEqual(item['rights']['basis'], 'cc-by-4.0')
                self.assertEqual(item['rights']['attribution'], 'Filmmaker')
                self.assertEqual(data['items'][2]['rights']['basis'], 'public-domain')
                discovery.discover()
                self.assertEqual(catalog.read_bytes(), first_bytes)

    def test_upstream_failure_preserves_catalog(self):
        with tempfile.TemporaryDirectory() as folder:
            catalog = Path(folder) / 'catalog.json'
            catalog.write_text('{"items":[]}\n')
            before = catalog.read_bytes()
            with patch.object(discovery, 'CATALOG', catalog), patch.object(discovery, 'SEARCHES', ['fixture']), patch.object(discovery, 'request', side_effect=OSError('offline')):
                discovery.discover()
            self.assertEqual(catalog.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
