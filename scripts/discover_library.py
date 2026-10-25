#!/usr/bin/env python3
"""Discover directly playable, freely licensed Wikimedia Commons videos.
Runs in GitHub Actions; standard library only. Existing catalog entries are preserved.
"""
import html
import json
import os
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

CATALOG = Path("data/legal-library.json")
API = "https://commons.wikimedia.org/w/api.php"
HEADERS = {"User-Agent": "SullyTVLibraryDiscovery/1.0 (GitHub project mblackketter1976-bit/Sully-tv; contact via GitHub)", "Accept": "application/json"}
SEARCHES = [
    "filetype:video documentary", "filetype:video short film",
    "filetype:video public domain film", "filetype:video historical film",
    "filetype:video nature wildlife", "filetype:video science",
    "filetype:video space NASA", "filetype:video travel",
    "filetype:video comedy film", "filetype:video animation",
    "filetype:video silent film", "filetype:video educational film",
    "filetype:video western film", "filetype:video romantic comedy",
    "filetype:video horror film", "filetype:video action film",
    "filetype:video sports documentary", "filetype:video true crime",
    "filetype:video cartoons", "filetype:video space documentary",
]
ALLOWED = {"cc0", "public-domain", "pd", "cc-by-4.0", "cc-by-3.0", "cc-by-sa-4.0", "cc-by-sa-3.0"}
VIDEO_EXT = (".webm", ".ogv", ".ogg", ".mp4")
LIMIT_PER_RUN = 60

def request(params):
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=35) as response:
        return json.load(response)

def plain(value):
    return re.sub(r"<[^>]*>", "", html.unescape(str(value or ""))).strip()

def classify(title, description):
    text = (title + " " + description).lower()
    if re.search(r"documentary|nature film|historical film|science film|educational film", text):
        return "documentary"
    if re.search(r"short film|short movie|shortfilm", text):
        return "short"
    if re.search(r"feature film|full movie|silent film|motion picture", text):
        return "movie"
    if re.search(r"episode|television series|tv show", text):
        return "show"
    return "other"

def worthwhile(title, description, kind):
    text=(title+" "+description).lower()
    junk=r"test footage|logo|sample clip|animation test|loop animation|render test|tutorial demo|test animation|screensaver|stock footage"
    if re.search(junk,text):return False
    if kind in ("movie","show","short","documentary"):return True
    return bool(re.search(r"nasa|astronomy|wildlife|nature documentary|space mission|history of|science documentary|educational film|animated short",text))

def discover():
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    items = data.setdefault("items", [])
    seen = {str(x.get("id")) for x in items}
    added = 0
    for search in SEARCHES:
        if added >= LIMIT_PER_RUN:
            break
        try:
            result = request({"action":"query","generator":"search","gsrsearch":search,"gsrnamespace":6,
                              "gsrlimit":40,"prop":"imageinfo","iiprop":"url|extmetadata|mime",
                              "format":"json","formatversion":2})
            pages = result.get("query",{}).get("pages",[])
        except Exception as exc:
            print("Search failed:", search, exc)
            continue
        for page in pages:
            if added >= LIMIT_PER_RUN:
                break
            pid = page.get("pageid")
            key = "commons:" + str(pid)
            if not pid or key in seen:
                continue
            title = str(page.get("title","")).removeprefix("File:")
            if not title.lower().endswith(VIDEO_EXT):
                continue
            info = (page.get("imageinfo") or [{}])[0]
            url = info.get("url","")
            if not url.startswith("https://") or not info.get("mime","").startswith("video/"):
                continue
            metadata = info.get("extmetadata") or {}
            def field(name):
                return plain((metadata.get(name) or {}).get("value",""))
            license_code = re.sub(r"\\s+", "-", field("LicenseShortName").lower().strip())
            license_url = field("LicenseUrl")
            if license_code not in ALLOWED:
                continue
            # Require a source and a recognizable license; do not assume all Commons uploads are free.
            if license_code not in {"cc0","pd","public-domain"} and not license_url.startswith("https://"):
                continue
            description = field("ImageDescription")
            attribution = field("Artist") or field("Credit")
            source = "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(page["title"].replace(" ","_"),safe=":/_()")
            clean_title = re.sub(r"\\.(webm|ogv|ogg|mp4)$","",title,flags=re.I).replace("_"," ").strip()
            if not clean_title:
                continue
            kind=classify(clean_title,description)
            if not worthwhile(clean_title,description,kind):
                continue
            item = {"id":key,"title":clean_title,"kind":kind,
                    "year":"","genres":genres_for(clean_title,description),"description":description[:450] or "Freely licensed video on Wikimedia Commons",
                    "poster":"","playback":{"type":"direct","url":url},
                    "rights":{"basis":license_code,"source":source,"licenseUrl":license_url,
                              "attribution":attribution,"notes":"License metadata from Wikimedia Commons; review third-party rights for redistribution"},
                    "status":"verified","lastChecked":time.strftime("%Y-%m-%d")}
            items.append(item)
            seen.add(key)
            added += 1
        time.sleep(1)
    if added:
        CATALOG.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\\n",encoding="utf-8")
    print("Added",added,"new videos; total",len(items))

if __name__ == "__main__":
    discover()
