#!/usr/bin/env python3
"""Fetch sourced XMLTV schedules for Sully TV. No inferred programs."""
import datetime as dt
import gzip
import io
import json
import os
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API = "https://iptv-org.github.io/api/"
NOW = dt.datetime.now(dt.timezone.utc)
UA = {"User-Agent": "SullyTV-Guide/1.0 (public XMLTV integration)"}

def fetch(url, max_bytes=12_000_000):
    if not url.startswith("https://"):
        raise ValueError("HTTPS required")
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=24) as response:
        data = response.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise ValueError("Guide exceeds size limit")
    return gzip.decompress(data) if data[:2] == b"\\x1f\\x8b" else data

def json_api(path):
    return json.loads(fetch(API + path, 8_000_000))

def xmltv_time(raw):
    try:
        raw = raw.strip()
        stamp = dt.datetime.strptime(raw[:14], "%Y%m%d%H%M%S")
        offset = raw[14:].strip()
        if offset and len(offset) == 5 and offset[0] in "+-":
            sign = 1 if offset[0] == "+" else -1
            mins = sign * (int(offset[1:3]) * 60 + int(offset[3:]))
            return stamp.replace(tzinfo=dt.timezone(dt.timedelta(minutes=mins)))
        return stamp.replace(tzinfo=dt.timezone.utc)
    except (ValueError, TypeError, AttributeError):
        return None

def main():
    streams = json.loads(fetch(API + "streams.json", 32_000_000))
    live = {x.get("channel") for x in streams if x.get("channel") and x.get("url")}
    guides = json.loads(fetch(API + "guides.json", 32_000_000))
    print("DIAGNOSTIC: stream records =", len(streams), "live channel IDs =", len(live), "guide records =", len(guides), flush=True)
    if guides:
        print("DIAGNOSTIC: first guide keys =", sorted(guides[0].keys()), flush=True)
    by_url = defaultdict(set)
    for g in guides:
        channel = g.get("channel")
        if channel not in live:
            continue
        for source in g.get("sources") or []:
            url = source.get("url", "")
            if url.startswith("https://") and source.get("format", "XML").upper() in ("XML", "XMLTV"):
                by_url[url].add(channel)
    # Prefer sources covering the most live stations, avoid a large global download.
    choices = sorted(by_url, key=lambda u: len(by_url[u]), reverse=True)[:12]
    print("DIAGNOSTIC: matching guide URLs =", len(by_url), "selected =", len(choices), flush=True)
    results = defaultdict(list)
    sources = {}
    for url in choices:
        try:
            raw = fetch(url)
            if len(raw) > 28_000_000:
                continue
            root = ET.fromstring(raw)
            if root.tag != "tv":
                continue
            expected = by_url[url]
            added = 0
            for p in root.iter("programme"):
                channel = p.get("channel", "")
                if channel not in expected:
                    continue
                start, end = xmltv_time(p.get("start")), xmltv_time(p.get("stop"))
                if not start or not end or end <= start or end < NOW or start > NOW + dt.timedelta(days=3):
                    continue
                title = p.findtext("title", "").strip()
                if not title or len(title) > 220 or (end-start)>dt.timedelta(hours=12):
                    continue
                entry = {"title": title, "start": start.isoformat(), "end": end.isoformat(), "source": url}
                if entry not in results[channel]:
                    results[channel].append(entry)
                    added += 1
            if added:
                sources[url] = added
        except (OSError, ValueError, ET.ParseError, TimeoutError, EOFError) as exc:
            print("Skipping source:", url, str(exc)[:120])
    output = {"updated": NOW.isoformat(), "channels": {k: sorted(v, key=lambda p: p["start"])[:160] for k,v in results.items()}, "sourceCounts": sources}
    destination = ROOT / "data/tv-guide.json"
    # Keep last valid data if upstream sources are all down. The UI will mark it stale.
    if not results and destination.exists():
        print("No fresh listings; preserving prior file")
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(output, ensure_ascii=False, separators=(",", ":"))+"\\n", encoding="utf-8")
    print("Updated", len(results), "channels with", sum(map(len, results.values())), "program listings")

if __name__ == "__main__":
    main()
