#!/usr/bin/env python3
"""Conservative Commons video discovery for Sully TV. Stores URLs, not binary files."""
import json, os, re, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path
PATH=Path("data/legal-library.json")
API="https://commons.wikimedia.org/w/api.php"
HEADERS={"User-Agent":"SullyTV-LegalCatalog/1.0 (GitHub project; metadata-only; respects Commons licensing)"}
ALLOWED={"cc0","cc-by-4.0","cc-by-3.0","cc-by-sa-4.0","cc-by-sa-3.0","pd","public domain"}
def request(params):
    url=API+"?"+urllib.parse.urlencode(params)
    with urllib.request.urlopen(urllib.request.Request(url,headers=HEADERS),timeout=35) as r:return json.load(r)
def clean(value):
    return re.sub("<[^>]+>","",value or "").strip()
def main():
    data=json.loads(PATH.read_text(encoding="utf8"))
    items=data.get("items",[])
    known={i["id"] for i in items}
    today=datetime.now(timezone.utc).date().isoformat()
    # Query file namespace for video files, rotating categories across runs.
    terms=["NASA","nature","animation","science","history","documentary"]
    offset=int(os.environ.get("GITHUB_RUN_NUMBER","0"))%len(terms)
    query=terms[offset]+" filetype:video"
    found=request({"action":"query","generator":"search","gsrsearch":query,"gsrnamespace":6,"gsrlimit":50,"prop":"imageinfo","iiprop":"url|size|mime|extmetadata","iiextmetadatafilter":"LicenseShortName|LicenseUrl|Artist|UsageTerms|Copyrighted","format":"json","formatversion":2})
    added=0
    for page in found.get("query",{}).get("pages",[]):
        infos=page.get("imageinfo") or []
        if not infos:continue
        info=infos[0];meta=info.get("extmetadata") or {}
        get=lambda key:clean((meta.get(key) or {}).get("value",""))
        license_name=get("LicenseShortName").lower().replace(" ","-")
        if license_name not in ALLOWED:continue
        if get("Copyrighted").lower()=="true" and license_name in {"pd","public domain"}:continue
        mime=info.get("mime","")
        if mime not in {"video/webm","video/mp4","video/ogg"}:continue
        url=info.get("url","")
        if not url.startswith("https://upload.wikimedia.org/"):continue
        pid="commons:"+str(page["pageid"])
        if pid in known:continue
        title=page.get("title","").removeprefix("File:").rsplit(".",1)[0].replace("_"," ")
        pageurl="https://commons.wikimedia.org/wiki/"+urllib.parse.quote(page["title"].replace(" ","_"),safe=":/")
        items.append({"id":pid,"title":title,"kind":"other","year":"","genres":[],"description":"Openly licensed video from Wikimedia Commons","poster":"","playback":{"type":"direct","url":url},"rights":{"basis":license_name,"source":pageurl,"licenseUrl":get("LicenseUrl"),"attribution":get("Artist")[:500],"verifiedAt":today,"notes":"Machine-readable Commons license; verify any third-party material before redistribution"},"lastChecked":today,"status":"verified"})
        known.add(pid);added+=1
    data["items"]=items[:3000]
    data["lastDiscovery"]=today
    PATH.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("Query:",query,"Added",added,"videos; total",len(items))
if __name__=="__main__":main()
