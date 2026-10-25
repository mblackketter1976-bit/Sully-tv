#!/usr/bin/env python3
"""Sully TV independent XMLTV normalization engine (stdlib only).

No network requests, no unverified schedule fabrication, no publication.
"""
from __future__ import annotations
from datetime import datetime, timezone, timedelta
import json
import os
import tempfile
import re
import sys
import xml.etree.ElementTree as ET

MAX_XML_BYTES = 5_000_000
MAX_PROGRAMMES = 20000
STAMP = re.compile(r"^(\d{12}|\d{14})(?:\s*([+-]\d{4}|Z))?$")


def parse_timestamp(raw: str) -> str:
    """Parse XMLTV local-offset timestamps to UTC ISO8601."""
    match = STAMP.fullmatch((raw or "").strip())
    if not match:
        raise ValueError("Invalid XMLTV timestamp")
    digits, offset = match.groups()
    fmt = "%Y%m%d%H%M%S" if len(digits) == 14 else "%Y%m%d%H%M"
    if offset is None:
        raise ValueError("XMLTV timestamp must include an explicit timezone")
    dt = datetime.strptime(digits, fmt)
    if offset == "Z":
        minutes = 0
    else:
        sign = 1 if offset[0] == "+" else -1
        hours, mins = int(offset[1:3]), int(offset[3:5])
        if hours > 23 or mins > 59:
            raise ValueError("Invalid timezone offset")
        minutes = sign * (hours * 60 + mins)
    return (dt.replace(tzinfo=timezone(timedelta(minutes=minutes)))
            .astimezone(timezone.utc).isoformat().replace("+00:00", "Z"))


def normalize(xml_bytes: bytes, channel_map: dict[str, str], source_id: str) -> dict:
    if not isinstance(xml_bytes, bytes) or len(xml_bytes) > MAX_XML_BYTES:
        raise ValueError("XMLTV input exceeds safe byte limit or is not bytes")
    if not source_id or not isinstance(source_id, str):
        raise ValueError("Source identifier required")
    if not isinstance(channel_map, dict):
        raise ValueError("Channel mapping required")
    # Expat rejects entity expansion, and the explicit declaration check avoids
    # accepting DTD-based input even if parser behavior changes.
    if b"<!DOCTYPE" in xml_bytes.upper() or b"<!ENTITY" in xml_bytes.upper():
        raise ValueError("DTD/entity declarations are not accepted")
    root = ET.fromstring(xml_bytes)
    if root.tag != "tv":
        raise ValueError("Expected XMLTV <tv> root")
    result = {}
    count = 0
    for item in root.iter("programme"):
        count += 1
        if count > MAX_PROGRAMMES:
            raise ValueError("Too many programmes")
        original_id = item.get("channel", "")
        channel = channel_map.get(original_id)
        if not channel:
            continue
        title_element = item.find("title")
        title = "".join(title_element.itertext()).strip() if title_element is not None else ""
        if not title or len(title) > 250:
            continue
        try:
            start = parse_timestamp(item.get("start", ""))
            stop = parse_timestamp(item.get("stop", ""))
        except ValueError:
            continue
        if stop <= start:
            continue
        start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
        stop_dt = datetime.fromisoformat(stop.replace("Z", "+00:00"))
        if stop_dt - start_dt > timedelta(hours=24):
            continue
        programme = {"title": title, "start": start, "stop": stop, "source": source_id}
        result.setdefault(channel, []).append(programme)
    for programmes in result.values():
        unique = {(p["start"], p["stop"], p["title"]): p for p in programmes}
        programmes[:] = sorted(unique.values(), key=lambda p: (p["start"], p["stop"], p["title"]))
    return {"schema": 1, "source": source_id, "channels": result,
            "matched_channels": len(result), "programmes": sum(map(len, result.values()))}



def to_sully_tv_guide(normalized: dict, generated_at: datetime | None = None) -> dict:
    """Convert normalized XMLTV output to Sully TV's current JSON contract."""
    if not isinstance(normalized, dict) or not isinstance(normalized.get("channels"), dict):
        raise ValueError("Invalid normalized guide")
    generated_at = generated_at or datetime.now(timezone.utc)
    if generated_at.tzinfo is None:
        raise ValueError("Generation time must include a timezone")
    channels = {}
    for channel_id, programmes in normalized["channels"].items():
        if not isinstance(programmes, list):
            raise ValueError("Invalid programme list")
        valid = []
        for programme in programmes:
            if not all(isinstance(programme.get(k), str) and programme[k] for k in ("title", "start", "stop", "source")):
                continue
            valid.append({"title": programme["title"], "start": programme["start"],
                          "end": programme["stop"], "source": programme["source"]})
            if isinstance(programme.get("url"), str):
                valid[-1]["url"] = programme["url"]
        if valid:
            channels[channel_id] = valid
    sources = {}
    for programmes in channels.values():
        for programme in programmes:
            sources[programme["source"]] = sources.get(programme["source"], 0) + 1
    return {"updated": generated_at.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
            "channels": channels, "sourceCounts": sources}

def main(argv: list[str]) -> int:
    if len(argv) != 5:
        print("Usage: python scripts/sully_epg_engine.py INPUT.xml MAPPING.json SOURCE_ID OUTPUT.json", file=sys.stderr)
        return 2
    from pathlib import Path
    xml_path, mapping_path, source_id, output_path = map(str, argv[1:])
    if Path(xml_path).stat().st_size > MAX_XML_BYTES:
        raise ValueError("XMLTV file exceeds size cap")
    data = normalize(Path(xml_path).read_bytes(),
                     json.loads(Path(mapping_path).read_text(encoding="utf-8")), source_id)
    if not data["programmes"]:
        print("No verified mapped programmes; refusing empty output", file=sys.stderr)
        return 1
    data = to_sully_tv_guide(data)
    # Write completely before replacing the destination; never publish partial JSON.
    destination = Path(output_path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=destination.parent,
                                         prefix=".sully-guide-", suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            json.dump(data, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, destination)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
    print(f"Validated {sum(len(p) for p in data['channels'].values())} programmes across {len(data['channels'])} channels")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
