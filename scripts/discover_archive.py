#!/usr/bin/env python3
"""Index explicitly openly licensed Internet Archive films, without copying media files."""
import json,re,time,urllib.parse,urllib.request
from pathlib import Path
OUT=Path("data/archive-titles.json")
HEAD={"User-Agent":"SullyTVCatalog/1.0 (github.com/mblackketter1976-bit/Sully-tv)"}
QUERIES=[
 'mediatype:movies AND licenseurl:*creativecommons.org/licenses/by/*',
 'mediatype:movies AND licenseurl:*creativecommons.org/publicdomain/zero/*',
 'mediatype:movies AND licenseurl:*creativecommons.org/publicdomain/mark/*',
]
def get(url):
 req=urllib.request.Request(url,headers=HEAD)
 with urllib.request.urlopen(req,timeout=35) as r:return json.load(r)
def license_ok(url):
 u=str(url or "").lower().replace("http:","https:")
 return bool(re.match(r"https://creativecommons.org/(?:licenses/(?:by|by-sa)/[234]\\.0|publicdomain/(?:zero|mark)/1\\.0)(?:/|$)",u))
def genre(text):
 rules={"Comedy":r"comedy|comic|funny|humor","Horror":r"horror|scary|monster|vampire","Action":r"action|martial|adventure","Romance":r"romance|romantic|love","Western":r"western|cowboy","Sci-Fi":r"sci.fi|science fiction|space|alien","Animation":r"animat|cartoon","Documentary":r"documentary|nonfiction","History":r"history|historical|silent|vintage","Nature":r"nature|wildlife|animal","Science":r"science|technology|experiment","Sports":r"sport|football|baseball","Crime":r"crime|mystery|detective","Music":r"music|concert"}
 return [g for g,p in rules.items() if re.search(p,text,re.I)]
def main():
 data=json.loads(OUT.read_text()) if OUT.exists() else {"items":[]}
 found={x["id"]:x for x in data["items"]}
 added=0
 for query in QUERIES:
  for page in range(1,4):
   try:
    args=[("q",query),("output","json"),("rows","100"),("page",str(page))]
    args += [("fl[]",k) for k in ("identifier","title","year","description","subject","licenseurl","mediatype")]
    docs=get("https://archive.org/advancedsearch.php?"+urllib.parse.urlencode(args)).get("response",{}).get("docs",[])
   except Exception as e:
    print("Search failed",str(e));continue
   for d in docs:
    ident=str(d.get("identifier",""))
    lic=d.get("licenseurl","")
    if isinstance(lic,list):lic=lic[0] if lic else ""
    if not ident or not license_ok(lic):continue
    title=d.get("title","")
    if isinstance(title,list):title=title[0] if title else ""
    if not title:continue
    year=str(d.get("year",""))[:4]
    subject=d.get("subject",[])
    if isinstance(subject,str):subject=[subject]
    desc=d.get("description","")
    if isinstance(desc,list):desc=" ".join(map(str,desc))
    tags=genre(" ".join([str(title),str(desc)[:300],*map(str,subject[:12])]))
    kind="show" if re.search(r"television|tv series|episode",str(title)+" "+str(desc),re.I) else "movie"
    entry={"id":"archive-"+ident,"title":str(title)[:180],"year":year,"kind":kind,"genres":tags,"provider":"Internet Archive","access":"Free (open license; verify item)","url":"https://archive.org/details/"+urllib.parse.quote(ident,safe=""),"licenseUrl":lic}
    if entry["id"] not in found:found[entry["id"]]=entry;added+=1
   time.sleep(1)
 data={"updated":time.strftime("%Y-%m-%d"),"description":"Open-license metadata index. Watch on source site; licensing assertions are uploader-provided and require review before rehosting.","items":list(found.values())[:5000]}
 OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")
 print("New indexed titles:",added,"Total:",len(data["items"]))
if __name__=="__main__":main()
