import re, os, json, hashlib, urllib.request, urllib.parse
BASE="https://www.robotika4kids.co.il"
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124 Safari/537.36"}
def get(u):
    return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60).read()
os.makedirs("raw/pages",exist_ok=True); os.makedirs("raw/img",exist_ok=True)
seen=set(); queue=["/"]; imgs={}
while queue:
    p=queue.pop(0)
    if p in seen: continue
    seen.add(p)
    try: html=get(BASE+urllib.parse.quote(p)).decode("utf-8")
    except Exception as e: print("ERR",p,e); continue
    name=urllib.parse.unquote(p).strip("/").replace("/","__") or "_home"
    open(f"raw/pages/{name}.html","w").write(html)
    print("page",p,len(html))
    for m in re.finditer(r'href="(?:https://www\.robotika4kids\.co\.il)?(/[^"#?]*)"',html):
        q=urllib.parse.unquote(m.group(1))
        if q.startswith(("/u/","/_","/view")) or "." in q.split("/")[-1]: continue
        if q not in seen: queue.append(q)
    for m in re.finditer(r'https://lh\d(?:-[a-z]+)?\.googleusercontent\.com/[^"\'\s)\\]+',html):
        u=m.group(0).replace("&amp;","&")
        key=re.sub(r'=[^/=]*$','',u)
        imgs.setdefault(key,u)
mp={}
for key,u in imgs.items():
    h=hashlib.md5(key.encode()).hexdigest()[:12]
    full=key+"=w1600"
    try:
        r=urllib.request.urlopen(urllib.request.Request(full,headers=UA),timeout=60)
        ct=r.headers.get("Content-Type","image/jpeg"); data=r.read()
        ext={"image/png":"png","image/gif":"gif","image/webp":"webp"}.get(ct.split(";")[0],"jpg")
        fn=f"{h}.{ext}"; open("raw/img/"+fn,"wb").write(data); mp[key]=fn
        print("img",fn,len(data))
    except Exception as e: print("IMGERR",key[:80],e)
json.dump(mp,open("raw/images.json","w"),indent=1)
