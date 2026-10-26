#!/usr/bin/env python3
"""Read-only local integrity checks. Run: python3 scripts/check_static.py"""
from pathlib import Path
import json
import sys

root = Path(__file__).resolve().parent.parent
errors = []
warnings = []

for name in ("index.html", "manifest.webmanifest", "sw.js"):
    if not (root / name).is_file():
        errors.append("Missing: " + name)

if not errors:
    html = (root / "index.html").read_text(encoding="utf-8")
    manifest = json.loads((root / "manifest.webmanifest").read_text(encoding="utf-8"))
    sw = (root / "sw.js").read_text(encoding="utf-8")
    for marker in ("manifest.webmanifest", "<video", "Sully TV"):
        if marker not in html:
            errors.append("Missing HTML marker: " + marker)
    for icon in manifest.get("icons", []):
        source = icon.get("src", "")
        if source.startswith("./") and not (root / source[2:]).is_file():
            errors.append("Missing manifest icon: " + source)
    for name in ("index.html", "manifest.webmanifest"):
        if name not in sw:
            warnings.append("Worker may not precache: " + name)
    if "cdn.jsdelivr.net" in html:
        warnings.append("External CDN dependency detected")
    if "captureStream(" in html:
        warnings.append("Browser recording detected; not server DVR")
for message in errors:
    print("FAIL:", message)
for message in warnings:
    print("WARN:", message)
print("Static checks:", "FAILED" if errors else "PASSED", "|", len(errors), "errors", len(warnings), "warnings")
print("Does not verify playback, devices, browser install or remote availability.")
sys.exit(bool(errors))
