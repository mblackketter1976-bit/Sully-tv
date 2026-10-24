#!/usr/bin/env python3
"""Refresh Luna's public YouTube feed without an API key."""
import json
import pathlib
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

CHANNEL = "UCzl5MwPHJN0n2G0L8v4Pptw"
URL = "https://www.youtube.com/feeds/videos.xml?channel_id=" + CHANNEL
ROOT = pathlib.Path(__file__).resolve().parent
OUTPUT = ROOT / "luna-videos.json"
ns = {"atom": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015"}
request = urllib.request.Request(URL, headers={"User-Agent": "SullyTV/1.0"})
with urllib.request.urlopen(request, timeout=30) as response:
    root = ET.fromstring(response.read())
items = []
for entry in root.findall("atom:entry", ns):
    vid = entry.findtext("yt:videoId", default="", namespaces=ns)
    title = entry.findtext("atom:title", default="", namespaces=ns)
    published = entry.findtext("atom:published", default="", namespaces=ns)
    if len(vid) == 11:
        items.append({"id": vid, "title": title, "published": published,
                      "thumbnail": "https://i.ytimg.com/vi/" + vid + "/hqdefault.jpg",
                      "url": "https://www.youtube.com/watch?v=" + vid})
previous = []
if OUTPUT.exists():
    try:
        previous = json.loads(OUTPUT.read_text(encoding="utf-8")).get("videos", [])
    except (ValueError, OSError):
        pass
seen = {item["id"] for item in items}
items.extend(item for item in previous if item.get("id") not in seen)
if not items:
    raise RuntimeError("No public YouTube videos found; keeping previous catalog")
OUTPUT.write_text(json.dumps({"channelId": CHANNEL, "updatedAt": datetime.now(timezone.utc).isoformat(),
                              "videos": items}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("Saved", len(items), "videos")
