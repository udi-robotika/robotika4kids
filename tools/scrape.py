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
import time
for m in re.finditer(r'https://ssl\.gstatic\.com/atari/images/sociallinks/[\w.]+',"".join(open("raw/pages/"+f).read() for f in os.listdir("raw/pages"))):
    imgs.setdefault(m.group(0),m.group(0))
mp=json.load(open("raw/images.json")) if os.path.exists("raw/images.json") else {}
for key,u in imgs.items():
    if key in mp and os.path.exists("raw/img/"+mp[key]): continue
    h=hashlib.md5(key.encode()).hexdigest()[:12]
    r=None
    for full in ([key+"=w1600",u,key] if "googleusercontent" in key else [key]):
        for attempt in range(3):
            try: r=urllib.request.urlopen(urllib.request.Request(full,headers=UA),timeout=60); break
            except Exception as e: print("retry",attempt,full[-30:],e); time.sleep(2+attempt*3)
        if r: break
    try:
        if r is None: raise Exception("all failed")
        ct=r.headers.get("Content-Type","image/jpeg"); data=r.read()
        ext={"image/png":"png","image/gif":"gif","image/webp":"webp"}.get(ct.split(";")[0],"jpg")
        fn=f"{h}.{ext}"; open("raw/img/"+fn,"wb").write(data); mp[key]=fn
        print("img",fn,len(data))
    except Exception as e: print("IMGERR",key[:80],e)
json.dump(mp,open("raw/images.json","w"),indent=1)
