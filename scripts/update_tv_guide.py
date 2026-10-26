#!/usr/bin/env python3
"""Refresh only explicitly reviewed providers; preserve the last usable guide."""
import argparse
from datetime import datetime, timezone, timedelta
import gzip
import io
import json
import os
from pathlib import Path
import tempfile
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit
from tvmaze_guide import collect as collect_tvmaze
from sully_epg_engine import MAX_XML_BYTES, normalize, to_sully_tv_guide

ROOT = Path(__file__).resolve().parents[1]
MAX_DOWNLOAD = 5_000_000


def fetch(url):
    if urlsplit(url).scheme != 'https':
        raise ValueError('HTTPS required')
    request = urllib.request.Request(url, headers={'User-Agent': 'SullyTV-Guide/2.0'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=24) as response:
                if urlsplit(response.geturl()).scheme != 'https':
                    raise ValueError('HTTPS redirect required')
                raw = response.read(MAX_DOWNLOAD + 1)
            break
        except urllib.error.HTTPError as exc:
            if exc.code not in {429,500,502,503,504} or attempt == 2:
                raise
            exc.close()
            time.sleep(2**attempt)
    if len(raw) > MAX_DOWNLOAD:
        raise ValueError('Compressed guide exceeds byte limit')
    if raw.startswith(b'\x1f\x8b'):
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as archive:
            raw = archive.read(MAX_XML_BYTES + 1)
    if len(raw) > MAX_XML_BYTES:
        raise ValueError('XMLTV exceeds byte limit')
    return raw


def atomic_write(destination, data):
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=destination.parent,
                                         prefix='.sully-guide-', delete=False) as handle:
            temporary = Path(handle.name)
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write('\n')
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, destination)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


def update(registry, destination, fetcher=fetch, now=None):
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError('Current time must include a timezone')
    providers = registry.get('providers')
    if not isinstance(providers, list):
        raise ValueError('Provider registry requires a providers list')
    merged = {}
    attribution = {}
    reports = []
    for provider in providers:
        source = provider.get('id', 'unknown')
        if provider.get('enabled') is not True:
            continue
        rights = provider.get('rights', {})
        if not (rights.get('publicRedistribution') is True and rights.get('commercialUse') is True
                and rights.get('evidenceUrl') and rights.get('reviewedAt')):
            reports.append({'source': source, 'status': 'rights-unverified'})
            continue
        try:
            normalized = (collect_tvmaze(provider, fetcher, now) if provider.get('type') == 'tvmaze'
                          else normalize(fetcher(provider['url']), provider['channelMap'], source))
            accepted = 0
            for channel, programmes in normalized['channels'].items():
                for programme in programmes:
                    start = datetime.fromisoformat(programme['start'].replace('Z', '+00:00'))
                    stop = datetime.fromisoformat(programme['stop'].replace('Z', '+00:00'))
                    if stop <= now or start > now + timedelta(days=3):
                        continue
                    existing = merged.setdefault(channel, [])
                    # Registry order sets priority; conflicting schedules never overlap.
                    if any(start < datetime.fromisoformat(p['stop'].replace('Z', '+00:00')) and
                           stop > datetime.fromisoformat(p['start'].replace('Z', '+00:00')) for p in existing):
                        continue
                    existing.append(programme)
                    accepted += 1
            if accepted:
                attribution[source] = {'name': provider.get('name', source),
                                       'url': rights['evidenceUrl'],
                                       'attribution': rights.get('attribution', ''),
                                       'license': rights.get('license', ''),
                                       'coverage': provider.get('coverage', '')}
            reports.append({'source': source, 'status': 'accepted' if accepted else 'no-current-listings',
                            'programmes': accepted})
        except (OSError, ValueError, KeyError, EOFError, ET.ParseError) as exc:
            # Avoid publishing provider URLs, which may contain credentials.
            reports.append({'source': source, 'status': 'failed', 'error': type(exc).__name__})
    merged = {channel: sorted(programmes, key=lambda p: p['start'])
              for channel, programmes in merged.items() if programmes}
    if merged:
        output = to_sully_tv_guide({'channels': merged}, now)
        output['sources'] = attribution
        atomic_write(destination, output)
    return {'status': 'updated' if merged else 'preserved', 'channels': len(merged),
            'programmes': sum(map(len, merged.values())), 'providers': reports}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--registry', type=Path, default=ROOT / 'data/guide-sources.json')
    parser.add_argument('--output', type=Path, default=ROOT / 'data/tv-guide.json')
    args = parser.parse_args()
    print(json.dumps(update(json.loads(args.registry.read_text(encoding='utf-8')), args.output)))


if __name__ == '__main__':
    main()
