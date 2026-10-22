# Re-fetch specific pages and download any of their images missing from raw/images.json
import re, os, json, hashlib, time, urllib.request, urllib.parse
BASE="https://www.robotika4kids.co.il"
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124 Safari/537.36"}
def get(u):
    for a in range(4):
        try: return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60)
        except Exception as e: print("retry",a,u[-40:],e); time.sleep(5+a*10)
mp=json.load(open("raw/images.json"))
names=[f[:-5] for f in os.listdir("raw/pages") if f.startswith(("גלריה","השאירו","צור-קשר"))]
for name in names:
    p="/"+name.replace("__","/")
    r=get(BASE+urllib.parse.quote(p))
    if not r: continue
    html=r.read().decode("utf-8"); open(f"raw/pages/{name}.html","w").write(html)
    urls=set(m.group(0).replace("&amp;","&") for m in re.finditer(r'https://lh\d(?:-[a-z]+)?\.googleusercontent\.com/[^"\'\s)\\]+',html))
    urls|=set(re.findall(r'https://ssl\.gstatic\.com/atari/images/sociallinks/[\w.]+',html))
    for u in urls:
        key=re.sub(r'=[^/=]*$','',u) if "googleusercontent" in u else u
        if key in mp and os.path.exists("raw/img/"+mp[key]): continue
        time.sleep(1.5)
        r=get(key+"=w1600" if "googleusercontent" in u else u) or get(u)
        if not r: print("FAIL",name,key[-40:]); continue
        ct=r.headers.get("Content-Type","image/jpeg"); data=r.read()
        ext={"image/png":"png","image/gif":"gif","image/webp":"webp"}.get(ct.split(";")[0],"jpg")
        fn=hashlib.md5(key.encode()).hexdigest()[:12]+"."+ext
        open("raw/img/"+fn,"wb").write(data); mp[key]=fn; print("img",name,fn,len(data))
    json.dump(mp,open("raw/images.json","w"),indent=1)
