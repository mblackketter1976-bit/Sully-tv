import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from tvmaze_guide import normalize, collect
from update_tv_guide import update

PROVIDER={'id':'tvmaze-test','url':'https://api.tvmaze.com/schedule','type':'tvmaze','country':'US',
          'channelMap':{'40':'CNN.us'},'networkNames':{'40':'CNN'},'enabled':True,
          'rights':{'publicRedistribution':True,'commercialUse':True,'evidenceUrl':'https://www.tvmaze.com/api',
                    'reviewedAt':'2026-10-25','license':'https://creativecommons.org/licenses/by-sa/4.0/'}}
EPISODE={'runtime':60,'airstamp':'2026-10-25T18:00:00-04:00','name':'Episode',
         'url':'https://www.tvmaze.com/episodes/123/fixture',
         'show':{'name':'Fixture Show','network':{'id':40,'name':'CNN','country':{'code':'US'}}}}

class TestTVmaze(unittest.TestCase):
    def test_exact_mapping_timezone_and_link_preserved(self):
        p=normalize([EPISODE,EPISODE],PROVIDER)['channels']['CNN.us']
        self.assertEqual(len(p),1)
        self.assertEqual(p[0]['start'],'2026-10-25T22:00:00Z')
        self.assertEqual(p[0]['stop'],'2026-10-25T23:00:00Z')
        self.assertEqual(p[0]['url'],EPISODE['url'])

    def test_no_guessed_duration_timezone_or_network(self):
        variants=[]
        for field,value in [('runtime',None),('runtime',0),('runtime',float('nan')),('airstamp','2026-10-25T18:00:00')]:
            e=copy.deepcopy(EPISODE);e[field]=value;variants.append(e)
        for field,value in [('id',41),('name','CNN International'),('country',{'code':'CA'})]:
            e=copy.deepcopy(EPISODE);e['show']['network'][field]=value;variants.append(e)
        self.assertEqual(normalize(variants,PROVIDER)['channels'],{})

    def test_four_bounded_dates_and_no_empty_day_fabrication(self):
        calls=[]
        def fetcher(url): calls.append(url);return b'[]'
        self.assertEqual(collect(PROVIDER,fetcher,datetime(2026,10,25,tzinfo=timezone.utc))['channels'],{})
        self.assertEqual(len(calls),4)
        self.assertTrue(calls[0].endswith('date=2026-10-24'))
        self.assertTrue(calls[-1].endswith('date=2026-10-27'))

    def test_integration_exports_license_and_episode_link(self):
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder)/'guide.json'
            report=update({'providers':[PROVIDER]},output,lambda _:json.dumps([EPISODE]).encode(),datetime(2026,10,25,20,tzinfo=timezone.utc))
            self.assertEqual(report['programmes'],1)
            data=json.loads(output.read_text())
            self.assertEqual(data['sources']['tvmaze-test']['license'],PROVIDER['rights']['license'])
            self.assertEqual(data['channels']['CNN.us'][0]['url'],EPISODE['url'])

    def test_failed_refresh_preserves_last_file(self):
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder)/'guide.json';output.write_bytes(b'previous')
            report=update({'providers':[PROVIDER]},output,lambda _:b'{}',datetime(2026,10,25,tzinfo=timezone.utc))
            self.assertEqual(report['status'],'preserved')
            self.assertEqual(output.read_bytes(),b'previous')
