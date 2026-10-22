# Converts the scraped Google Sites pages (raw/) into a clean static site (site/)
import re, os, json, glob, shutil, urllib.parse, html
from bs4 import BeautifulSoup, NavigableString, Comment
from PIL import Image

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW=os.path.join(ROOT,"raw"); OUT=os.path.join(ROOT,"site")
DOMAIN="https://www.robotika4kids.co.il"
WIDTH={"uQSCkd":12,"II5mzb":4,"qWD73c":6,"c5RTEf":3,"ibL1re":2,"OiUrBf":8,"R6PoUb":1,"OwsYgb":7,"wNfPc":5,"EehZO":10}
SECTION={"lQAHbd":"s-accent","qeLZfd":"s-light","WxWicb":"s-tight"}
TEXTCLS={"duRjpb":"h-title","JYVBee":"h-heading","OmQG5e":"h-sub","zfr3Q":"t","jgG6ef":"big","iwQgFb":"divider"}
KEEP_ATTR={"href","src","dir","style","target","alt","colspan","rowspan","allowfullscreen","title"}

imgmap=json.load(open(f"{RAW}/images.json"))
shutil.rmtree(OUT,ignore_errors=True); os.makedirs(f"{OUT}/img")

# --- images: copy, shrink big photos to webp
outname={}
for key,fn in imgmap.items():
    src=f"{RAW}/img/{fn}"; base=fn.rsplit(".",1)[0]
    try:
        im=Image.open(src)
        if os.path.getsize(src)>250_000 and not (fn.endswith("png") and im.mode in("RGBA","P","LA")):
            im=im.convert("RGB")
            if im.width>1600: im=im.resize((1600,round(im.height*1600/im.width)))
            im.save(f"{OUT}/img/{base}.webp","WEBP",quality=80); outname[key]=f"{base}.webp"; continue
    except Exception as e: print("img?",fn,e)
    shutil.copy(src,f"{OUT}/img/{fn}"); outname[key]=fn

ICONS=set()
for fn in os.listdir(f"{OUT}/img"):
    try:
        w,h=Image.open(f"{OUT}/img/{fn}").size
        if max(w,h)<=230: ICONS.add("/img/"+fn)
    except Exception: pass

def local_img(u):
    k=re.sub(r'=[^/=]*$','',u.replace("&amp;","&"))
    return "/img/"+outname[k] if k in outname else u

def fix_href(h):
    if not h: return h
    if "google.com/url" in h:
        q=urllib.parse.parse_qs(urllib.parse.urlparse(h).query).get("q")
        if q: h=q[0]
    for p in (DOMAIN,"https://robotika4kids.co.il","http://www.robotika4kids.co.il"):
        if h.startswith(p): h=h[len(p):] or "/"
    return h

def clean(el):
    for c in el.find_all(string=lambda t:isinstance(t,Comment)): c.extract()
    for a in el.select('[aria-label="Copy heading link"]'):
        w=a.find_parent(class_="PPhIP") or a; w.decompose()
    for t in el.find_all(True):
        cls=t.get("class",[]) or []
        new=[TEXTCLS[c] for c in cls if c in TEXTCLS]
        if "FKF6mc" in cls: new.append("btn")
        if t.name=="img" and t.get("src"):
            t["src"]=local_img(t["src"]); t["loading"]="lazy"; t["alt"]=t.get("alt","")
            if t["src"] in ICONS: new.append("ico")
        if t.name=="a": t["href"]=fix_href(t.get("href"))
        if t.name=="iframe":
            src=t.get("src","")
            if "youtube.com/embed" in src: src=src.split("?")[0]
            t.attrs={"src":src,"style":t.get("style",""),"loading":"lazy","allowfullscreen":"","frameborder":"0"}
            continue
        for k in list(t.attrs):
            if k not in KEEP_ATTR: del t[k]
        if t.get("style"):
            st=re.sub(r"font-family:\s*'Open Sans',\s*Arial;?","",t["style"])
            st=re.sub(r"(vertical-align: baseline|font-variant: normal|background-color: transparent|border-(bottom|top|left|right): none|padding-(bottom|top|left|right): 0\.0pt);?","",st)
            st=re.sub(r"\s+"," ",st).strip(" ;")
            if st: t["style"]=st
            else: del t["style"]
        if new: t["class"]=new
    for h in el.find_all(["h1","h2","h3","h4","h5","h6","p"]):
        for d in h.find_all("div"): d.unwrap()
    # unwrap meaningless wrappers
    for t in el.find_all(["div","span"]):
        if not t.attrs and t.name=="div" and t.parent and len(t.find_all(True,recursive=False))<=1 and not t.get_text(strip=True) and not t.find(["img","iframe","a"]): 
            if not t.contents: t.decompose()
    return el

def block_html(tyj):
    cls=tyj.get("class",[])
    if "KUB40b" in cls:  # spacer
        d=tyj.find("div"); h=(d.get("style","") if d else "")
        return f'<div class="spacer" style="{h}"></div>'
    if "N0neUc" in cls:  # button
        a=tyj.find("a"); txt=a.get_text(" ",strip=True)
        tgt=' target="_blank" rel="noopener"' if a.get("target") else ""
        return f'<div class="btn-wrap"><a class="btn" href="{html.escape(fix_href(a["href"]))}"{tgt}>{html.escape(txt)}</a></div>'
    if "OWlOyc" in cls or tyj.find("iframe"):
        f=tyj.find("iframe"); src=f.get("src") or f.get("data-src","")
        if "youtube.com/embed" in src: src=src.split("?")[0]; return f'<div class="video"><iframe src="{src}" loading="lazy" allowfullscreen frameborder="0"></iframe></div>'
        st=f.get("style","height: 600px")
        return f'<iframe class="embed" src="{html.escape(src)}" style="{st}" loading="lazy" frameborder="0"></iframe>'
    inner=clean(tyj)
    return "".join(str(c) for c in inner.contents)

def render_section(sec):
    cls=[SECTION[c] for c in sec.get("class",[]) if c in SECTION]
    bgdiv=sec.find(class_="IFuOkc"); style=""
    if bgdiv and "background-image" in bgdiv.get("style",""):
        m=re.search(r'url\(([^)]+)\)',bgdiv["style"]); style=f' style="background-image:url({local_img(m.group(1))})"'; cls.append("s-bg")
    rows=[]
    for r in sec.find_all(class_="LS81yb"):
        cols=[]
        for c in r.find_all(recursive=False):
            m=re.search(r'hJDwNd-AhqUyc-(\w+)'," ".join(c.get("class",[])))
            w=WIDTH.get(m.group(1),12) if m else 12
            blocks=[block_html(b) for b in c.find_all(class_="tyJCtd")]
            body="".join(blocks).strip()
            cols.append(f'<div class="col{"" if body else " empty"}" style="--w:{w}">{body}</div>')
        rows.append('<div class="row">'+"".join(cols)+'</div>')
    if not any('class="col"' in r or "class=\"col\"" in r for r in rows): cls.append("s-empty")
    return f'<section class="{" ".join(["sec"]+cls)}"{style}><div class="wrap">'+"".join(rows)+'</div></section>'

# --- navigation from home page
home=BeautifulSoup(open(f"{RAW}/pages/_home.html").read(),"html.parser")
nav=[]
for li in home.select("nav ul.jYxBte > li"):
    a=li.find("a",attrs={"data-level":"1"})
    kids=[(x.get_text(strip=True),x["href"]) for x in li.find_all("a",attrs={"data-level":"2"})]
    nav.append((a.get_text(strip=True),a["href"],kids))

LABEL={"רובוטיקה-ילדים-נוער":"בית","summer-2026":"קיץ 2026"}
def lbl(t): return LABEL.get(t,t.replace("-"," "))
def nav_html(cur):
    out=[]
    for t,h,kids in nav:
        t=lbl(t)
        if h=="/רובוטיקה-ילדים-נוער": h="/"
        act=' class="active"' if h==cur else ""
        if kids:
            open_=" cur" if cur==h or any(k[1]==cur for k in kids) else ""
            sub="".join(f'<li><a href="{kh}"{" class=\"active\"" if kh==cur else ""}>{kt}</a></li>' for kt,kh in kids)
            out.append(f'<li class="has-sub{open_}"><div class="nav-row"><a href="{h}"{act}>{t}</a><button class="exp" aria-label="פתח תת-תפריט" aria-expanded="false"><svg viewBox="0 0 24 24" width="22" height="22"><path d="M7.41 8.59 12 13.17l4.59-4.58L18 10l-6 6-6-6z" fill="currentColor"/></svg></button></div><ul>{sub}</ul></li>')
        else: out.append(f'<li><a href="{h}"{act}>{t}</a></li>')
    return "<ul>"+"".join(out)+"</ul>"

TPL=open(os.path.join(ROOT,"tools","template.html")).read()
HOME=open(os.path.join(ROOT,"tools","home.html")).read()
FORM=open(os.path.join(ROOT,"tools","form.html")).read()
import hashlib; VER=hashlib.md5(open(os.path.join(ROOT,"tools","style.css"),"rb").read()).hexdigest()[:8]
shutil.copytree(os.path.join(ROOT,"tools","fonts"),f"{OUT}/fonts")
footer=None; pages=[]
for f in sorted(glob.glob(f"{RAW}/pages/*.html")):
    name=os.path.basename(f)[:-5]
    path="/" if name=="_home" else "/"+name.replace("__","/")
    s=BeautifulSoup(open(f).read(),"html.parser")
    foot=s.find("footer",class_="yxgWrb")
    if foot and footer is None: footer="".join(render_section(x) for x in foot.find_all("section"))
    if foot: foot.decompose()
    if path in ("/","/רובוטיקה-ילדים-נוער"): body=HOME; bodycls="home"
    elif path=="/השאירו-פרטים": body=FORM; bodycls="form"
    else: body='<div class="legacy">'+"".join(render_section(x) for x in s.find_all("section"))+'</div>'; bodycls="page"
    title=s.title.get_text() if s.title else "Robotika4Kids"
    og=lambda p:(s.find("meta",attrs={"property":p}) or {}).get("content","")
    desc=og("og:description")
    if path=="/השאירו-פרטים": desc="השאירו פרטים ונחזור אליכם עם חוג, סדנה או קורס רובוטיקה שמתאימים לילד או לילדה."
    ogimg=local_img(og("og:image")) if og("og:image") else ""
    navcur="/" if path=="/רובוטיקה-ילדים-נוער" else path
    page=(TPL.replace("{{TITLE}}",html.escape(title)).replace("{{DESC}}",html.escape(desc))
          .replace("{{OGIMG}}",("https://www.robotika4kids.co.il"+ogimg) if ogimg.startswith("/") else ogimg)
          .replace("{{CANON}}","https://www.robotika4kids.co.il"+urllib.parse.quote(path))
          .replace("{{NAV}}",nav_html(navcur)).replace("{{BODYCLS}}",bodycls).replace("{{VER}}",VER).replace("{{BODY}}",body).replace("{{FOOTER}}",footer or ""))
    d=OUT+(path if path!="/" else "/"); os.makedirs(d,exist_ok=True)
    open(os.path.join(d,"index.html"),"w").write(page); pages.append(path)
shutil.copy(os.path.join(ROOT,"tools","style.css"),f"{OUT}/style.css")
# sitemap
open(f"{OUT}/sitemap.xml","w").write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+"".join(f"<url><loc>https://www.robotika4kids.co.il{urllib.parse.quote(p)}</loc></url>" for p in pages)+"</urlset>")
open(f"{OUT}/robots.txt","w").write("User-agent: *\nAllow: /\nSitemap: https://www.robotika4kids.co.il/sitemap.xml\n")
print("built",len(pages),"pages")
