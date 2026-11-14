# 14.11.26 (אודי): new gallery page + birthday page for robotika4kids.
# Builds thumbnails into site/img/g/ and writes site/גלריה/index.html + site/ימי-הולדת/index.html,
# reusing the header/footer of the class page. Run from repo root: python3 tools/gallery_bday.py
import os, re, html
from urllib.parse import quote
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, 'site')
IMG = os.path.join(SITE, 'img')
TH = os.path.join(IMG, 'g')
os.makedirs(TH, exist_ok=True)

# (file, category, caption)
PHOTOS = [
  ('4af269af8165.webp', 'kids', 'מלחימים ומחברים את הרובוט'),
  ('ea89be29c470.webp', 'group', 'שולחן סדנה מלא רובוטים'),
  ('3518b24b016a.jpg', 'robots', 'עכבישים רובוטיים'),
  ('b59772cd653e.jpg', 'kids', 'מרכיבים בעצמם, בורג אחרי בורג'),
  ('491845d43600.webp', 'group', 'קרב רובוטים בסוף הסדנה'),
  ('2a8311baa551.jpg', 'robots', 'רובוט מקאנום שנוסע לכל כיוון'),
  ('3834bc209b11.jpg', 'kids', 'בונים מכונית חכמה'),
  ('14abcd04ebe1.webp', 'group', 'כל הרכבים של הקבוצה'),
  ('6d8ed7903cc1.webp', 'kids', 'מתכנתים את הרובוט במחשב'),
  ('69d1d1b03571.jpg', 'robots', 'רובוט עם מצלמה'),
  ('e0205b6fd956.webp', 'group', 'עובדים יחד בקבוצה'),
  ('1d89262b99e1.webp', 'kids', 'מחווטים חיישנים ומנועים'),
  ('96f9f342a154.jpg', 'robots', 'מכוניות בשלט FLYSKY'),
  ('91b09d4436e9.jpg', 'kids', 'מתרכזים בפרטים הקטנים'),
  ('788eca196f7a.webp', 'group', 'זירת הקרבות'),
  ('6fb94c26647b.jpg', 'robots', 'עכביש חכם'),
  ('4f98b10a22a3.jpg', 'kids', 'גם הקטנים בונים לבד'),
  ('8f28d24b0824.webp', 'group', 'סדנה קבוצתית'),
  ('365aaf1738d2.jpg', 'robots', 'מדידת מרחק ותצוגה'),
  ('75f3b9e28000.jpg', 'kids', 'מרכיבים מכונית רובוטית'),
  ('5fa3bce965b6.webp', 'group', 'רובוטי קרב מוכנים'),
  ('7ba3527db3bd.webp', 'robots', 'רכב מקאנום כתום'),
  ('10deed924692.webp', 'kids', 'מתחילים מהשלדה'),
  ('9b32acbfe026.webp', 'group', 'מכוניות צבעוניות על השולחן'),
  ('3c7e153ebf27.webp', 'robots', 'רובוט קרב עם להבים'),
  ('7d3dcb7cff95.jpg', 'kids', 'גאה במכונית שבנה'),
  ('78ef448316c3.webp', 'group', 'הכנות לתחרות'),
  ('4002d2159854.jpg', 'robots', 'רובוט עם חיישן מרחק'),
  ('fdcafab3ae3d.webp', 'kids', 'הלחמה ראשונה'),
  ('e6ef638a5838.webp', 'group', 'יום קרבות'),
  ('2975f5c379b7.jpg', 'robots', 'מכונית אדומה עם חיישנים'),
  ('2a629feca707.webp', 'kids', 'בונים זרוע רובוטית'),
  ('0d568a3a1ca8.jpg', 'group', 'רובוט שעובר את המכשולים'),
  ('c5bf9386f47d.jpg', 'robots', 'רכב 4X4 חכם'),
  ('8c32adf8ec63.webp', 'kids', 'כל ילד עם רובוט משלו'),
  ('f886d45590a6.jpg', 'kids', 'מסיימים ונוסעים'),
  ('deb5cdaf8127.png', 'robots', 'עכביש כחול'),
  ('119484f8d97a.webp', 'kids', 'מכונית בלוטוס'),
  ('9af1f0691097.jpg', 'robots', 'מכונית ירוקה'),
  ('5dac21051490.webp', 'robots', 'פח אלקטרוני חכם'),
  ('3f1ad6e9414d.webp', 'robots', 'מכונית כתומה'),
  ('df3998f0e111.jpg', 'kids', 'עובדים ברצינות'),
  ('60ed1977db07.webp', 'robots', 'רובוט עם חיישן אולטרסוני'),
  ('f056af1c216f.jpg', 'robots', 'רכב אדום עם תצוגה'),
]
CATS = [('all', 'הכל'), ('kids', 'ילדים בפעולה'), ('group', 'סדנאות וקבוצות'), ('robots', 'הרובוטים שבנינו')]
SUB = [('קרבות-רובוטים', 'קרבות רובוטים'), ('סדנאות-ילדים', 'סדנאות ילדים'), ('תחרות-קבוצתית', 'תחרות קבוצתית'),
       ('פח-אלקטרוני-חכם', 'פח אלקטרוני חכם'), ('רובוט-מקאנום', 'רובוט מקאנום'),
       ('עכבישים-רובוטיים-חכמים', 'עכבישים רובוטיים'), ('מכוניות-בשלט-flysky', 'מכוניות בשלט FLYSKY')]


def thumb(f):
    out = os.path.splitext(f)[0] + '.webp'
    p = os.path.join(TH, out)
    im = Image.open(os.path.join(IMG, f)).convert('RGB')
    im.thumbnail((640, 640))
    if not os.path.exists(p):
        im.save(p, 'WEBP', quality=78)
    return '/img/g/' + out, im.size


base = open(os.path.join(SITE, 'חוג-רובוטיקה', 'index.html'), encoding='utf-8').read()
HEAD_END = base.index('<main')
FOOT = base[base.index('</main>'):]
head = base[:HEAD_END].replace(' class="active"', '')


def page(title, desc, path, og, body, style, active_href):
    url = 'https://www.robotika4kids.co.il/' + quote(path)
    h = head
    h = re.sub(r'<title>.*?</title>', '<title>' + html.escape(title) + '</title>', h)
    h = re.sub(r'(<meta name="description" content=")[^"]*', r'\g<1>' + html.escape(desc), h)
    h = re.sub(r'(<meta property="og:title" content=")[^"]*', r'\g<1>' + html.escape(title), h)
    h = re.sub(r'(<meta property="og:description" content=")[^"]*', r'\g<1>' + html.escape(desc), h)
    h = re.sub(r'(<link rel="canonical" href=")[^"]*', r'\g<1>' + url, h)
    h = re.sub(r'(<meta property="og:url" content=")[^"]*', r'\g<1>' + url, h)
    h = re.sub(r'(<meta property="og:image" content=")[^"]*', r'\g<1>https://www.robotika4kids.co.il' + og, h)
    h = h.replace('</head>', '<style>' + style + '</style>\n</head>')
    h = h.replace('href="' + active_href + '"', 'href="' + active_href + '" class="active"', 1)
    out = os.path.join(SITE, path)
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, 'index.html'), 'w', encoding='utf-8').write(h + '<main id="main">\n' + body + '\n' + FOOT)


GSTYLE = """
.gl-top{max-width:1180px;margin:0 auto;padding:1.2rem 1rem .4rem}
.gl-top h1{margin:0 0 .3rem;font-size:clamp(1.6rem,4vw,2.4rem)}
.gl-top p{margin:0;color:#3a4565;font-size:1.05rem}
.gl-chips{display:flex;flex-wrap:wrap;gap:.45rem;margin:.9rem 0 .2rem}
.gl-chips button{font:inherit;border:2px solid #0F1B3D;background:#fff;color:#0F1B3D;border-radius:2rem;padding:.35rem .95rem;font-weight:700;cursor:pointer}
.gl-chips button.on{background:#0F1B3D;color:#FFC21A}
.gl-sub{display:flex;flex-wrap:wrap;gap:.4rem;margin:.6rem 0 0;font-size:.92rem}
.gl-sub a{background:#FFF4CC;color:#0F1B3D;border-radius:1rem;padding:.2rem .7rem;text-decoration:none;font-weight:600}
.gl-sub a:hover{background:#FFC21A}
.gl-grid{max-width:1180px;margin:0 auto;padding:.8rem 1rem 1.5rem;columns:4 240px;column-gap:.7rem}
.gl-grid figure{break-inside:avoid;margin:0 0 .7rem;position:relative;border-radius:.8rem;overflow:hidden;cursor:zoom-in;background:#eef1f7;box-shadow:0 2px 8px rgba(15,27,61,.12)}
.gl-grid img{display:block;width:100%;height:auto;transition:transform .35s}
.gl-grid figure:hover img{transform:scale(1.04)}
.gl-grid figcaption{position:absolute;inset:auto 0 0 0;padding:1.4rem .7rem .5rem;color:#fff;font-weight:700;font-size:.92rem;background:linear-gradient(transparent,rgba(15,27,61,.85))}
.gl-grid figure.hide{display:none}
.gl-cta{max-width:1180px;margin:0 auto 2rem;padding:1.2rem 1rem;display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:.8rem}
.gl-cta a{display:block;text-decoration:none;color:#0F1B3D;background:#FFC21A;border-radius:.9rem;padding:1rem 1.1rem;font-weight:800;font-size:1.1rem}
.gl-cta a span{display:block;font-weight:500;font-size:.92rem;margin-top:.2rem}
.lb{position:fixed;inset:0;z-index:60;background:rgba(10,16,35,.94);display:none;align-items:center;justify-content:center;flex-direction:column}
.lb.on{display:flex}
.lb img{max-width:94vw;max-height:80vh;border-radius:.6rem}
.lb p{color:#fff;font-weight:700;margin:.7rem 0 0}
.lb button{position:absolute;background:rgba(255,255,255,.15);color:#fff;border:0;font-size:2rem;width:3rem;height:3rem;border-radius:50%;cursor:pointer}
.lb .x{top:1rem;left:1rem}.lb .nx{left:1rem;top:50%}.lb .pv{right:1rem;top:50%}
"""

LB_JS = """<script>
(function(){var figs=[].slice.call(document.querySelectorAll('.gl-grid figure')),lb=document.getElementById('lb'),im=lb.querySelector('img'),cap=lb.querySelector('p'),cur=0;
function vis(){return figs.filter(function(f){return !f.classList.contains('hide')})}
function show(f){var v=vis();cur=v.indexOf(f);im.src=f.dataset.full;cap.textContent=f.querySelector('figcaption').textContent;lb.classList.add('on')}
function step(d){var v=vis();cur=(cur+d+v.length)%v.length;show(v[cur])}
figs.forEach(function(f){f.onclick=function(){show(f)}});
lb.querySelector('.x').onclick=function(){lb.classList.remove('on')};
lb.querySelector('.nx').onclick=function(e){e.stopPropagation();step(1)};
lb.querySelector('.pv').onclick=function(e){e.stopPropagation();step(-1)};
lb.onclick=function(e){if(e.target===lb)lb.classList.remove('on')};
document.addEventListener('keydown',function(e){if(!lb.classList.contains('on'))return;if(e.key==='Escape')lb.classList.remove('on');if(e.key==='ArrowLeft')step(1);if(e.key==='ArrowRight')step(-1)});
[].forEach.call(document.querySelectorAll('.gl-chips button'),function(b){b.onclick=function(){[].forEach.call(document.querySelectorAll('.gl-chips button'),function(x){x.classList.toggle('on',x===b)});figs.forEach(function(f){f.classList.toggle('hide',b.dataset.c!=='all'&&f.dataset.c!==b.dataset.c)})}});
})();
</script>"""


def grid(items, chips=True):
    figs = []
    for f, c, cap in items:
        t, (w, h) = thumb(f)
        figs.append('<figure data-c="%s" data-full="/img/%s"><img src="%s" alt="%s" width="%d" height="%d" loading="lazy"><figcaption>%s</figcaption></figure>' % (c, f, t, html.escape(cap), w, h, html.escape(cap)))
    return '<div class="gl-grid">' + ''.join(figs) + '</div>'


LB = '<div class="lb" id="lb" role="dialog" aria-label="תמונה מוגדלת"><button class="x" aria-label="סגירה">×</button><button class="pv" aria-label="הקודמת">›</button><button class="nx" aria-label="הבאה">‹</button><img alt=""><p></p></div>'

chips = '<div class="gl-chips">' + ''.join('<button type="button" data-c="%s"%s>%s</button>' % (k, ' class="on"' if k == 'all' else '', v) for k, v in CATS) + '</div>'
sub = '<div class="gl-sub"><b>עוד גלריות:</b>' + ''.join('<a href="/גלריה/%s">%s</a>' % (p, t) for p, t in SUB) + '</div>'
gbody = ('<section class="gl-top"><h1>הגלריה שלנו</h1><p>ככה זה נראה אצלנו: ילדים שבונים, מחווטים ומתכנתים רובוטים אמיתיים, ויוצאים עם חיוך ענק 🤖</p>'
         + chips + sub + '</section>' + grid(PHOTOS) +
         '<section class="gl-cta"><a href="/חוג-רובוטיקה">חוג רובוטיקה שבועי<span>פעם בשבוע, כל השנה, גילאי 7–12</span></a>'
         '<a href="/ימי-הולדת">🎉 יום הולדת רובוטי<span>אנחנו מגיעים אליכם עם כל הציוד</span></a>'
         '<a href="/סדנאות-יומיות">סדנה חד-פעמית<span>שעתיים של בנייה, יוצאים עם פרויקט שעובד</span></a></section>'
         + LB + LB_JS)
page('גלריה – רובוטים שילדים בנו | Robotika4Kids', 'תמונות מהחוגים, הסדנאות וימי ההולדת של Robotika4Kids ברמת גן: ילדים בונים, מחווטים ומתכנתים רובוטים, מכוניות חכמות ועכבישים רובוטיים.',
     'גלריה', '/img/ea89be29c470.webp', gbody, GSTYLE, '/גלריה')

# ---------- birthday page ----------
BSTYLE = GSTYLE + """
.bd-hero{background:linear-gradient(135deg,#FFC21A,#FFE27A);}
.bd-in{max-width:1180px;margin:0 auto;padding:1.4rem 1rem;display:grid;grid-template-columns:1.1fr .9fr;gap:1.4rem;align-items:center}
.bd-in h1{margin:.2rem 0 .5rem;font-size:clamp(1.8rem,4.5vw,2.8rem);color:#0F1B3D;line-height:1.15}
.bd-in .lead{font-size:1.15rem;color:#0F1B3D;margin:0 0 .8rem}
.bd-in ul{margin:0 0 1rem;padding:0;list-style:none;display:flex;flex-wrap:wrap;gap:.4rem}
.bd-in ul li{background:#fff;border-radius:2rem;padding:.25rem .8rem;font-weight:700;color:#0F1B3D}
.bd-pics{display:grid;grid-template-columns:1fr 1fr;gap:.5rem}
.bd-pics img{width:100%;aspect-ratio:1;object-fit:cover;border-radius:.9rem;box-shadow:0 4px 14px rgba(15,27,61,.25)}
.bd-pics img:first-child{grid-column:1/3;aspect-ratio:16/9}
.bd-sec{max-width:1180px;margin:0 auto;padding:1.4rem 1rem .4rem}
.bd-sec h2{margin:0 0 .8rem;font-size:1.6rem}
.bd-cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:.8rem}
.bd-cards div{background:#fff;border:2px solid #0F1B3D;border-radius:1rem;padding:1rem}
.bd-cards b{display:block;font-size:1.15rem;margin-bottom:.3rem;color:#0F1B3D}
.bd-cards .big{font-size:2rem}
.bd-steps{counter-reset:s;list-style:none;padding:0;margin:0;display:grid;gap:.6rem}
.bd-steps li{counter-increment:s;background:#FFF4CC;border-radius:.8rem;padding:.7rem 1rem .7rem 1rem;position:relative;padding-right:3.2rem}
.bd-steps li::before{content:counter(s);position:absolute;right:.8rem;top:.6rem;width:1.8rem;height:1.8rem;border-radius:50%;background:#0F1B3D;color:#FFC21A;display:grid;place-items:center;font-weight:800}
.bd-q{background:#0F1B3D;color:#fff;border-radius:1rem;padding:1.2rem;margin:1.2rem auto 1.5rem;max-width:1148px}
.bd-q h2{color:#FFC21A;margin:0 0 .5rem}
.bd-q ul{margin:.3rem 0 1rem;padding-inline-start:1.2rem}
.bd-q a.b{display:inline-block;background:#25D366;color:#fff;font-weight:800;border-radius:2rem;padding:.6rem 1.3rem;text-decoration:none;font-size:1.1rem;margin-inline-end:.5rem}
.bd-q a.b2{background:#FFC21A;color:#0F1B3D}
.gl-grid.bd{columns:4 200px}
@media(max-width:820px){.bd-in{grid-template-columns:1fr}}
"""
WA = 'https://wa.me/972545639120?text=' + quote('היי! אשמח לשמוע על יום הולדת רובוטי 🎉\nתאריך ושעה: \nמספר ילדים וגיל: \nאיפה (עיר, דירה/בית פרטי): ')
bpics = [('ea89be29c470.webp', 'group', 'שולחן סדנה מלא רובוטים'), ('3834bc209b11.jpg', 'kids', 'בונים מכונית חכמה'), ('491845d43600.webp', 'group', 'קרב רובוטים בסוף הסדנה')]
bbody = ('<section class="bd-hero"><div class="bd-in"><div>'
         '<h1>🎉 יום הולדת רובוטי</h1>'
         '<p class="lead">מסיבת יום הולדת שהילדים לא ישכחו: כל ילד בונה רובוט או מכונית חכמה, מפעיל אותם בעצמו, ובסוף כולם נכנסים לתחרות או לקרב רובוטים.</p>'
         '<ul><li>מגיל 7 ומעלה</li><li>שעה וחצי או שעתיים</li><li>מגיעים אליכם, או אצלנו ברמת גן</li><li>כל הציוד עלינו</li></ul>'
         '<a class="b b-pri lp-cta" href="' + WA + '" target="_blank" rel="noopener">לבדיקת תאריך והצעת מחיר</a>'
         '</div><div class="bd-pics">' + ''.join('<img src="/img/%s" alt="%s">' % (f, c) for f, _, c in bpics) + '</div></div></section>'
         '<section class="bd-sec"><h2>מה יש בפעילות</h2><div class="bd-cards">'
         '<div><span class="big">🔧</span><b>בונים בידיים</b>כל ילד מרכיב ומחווט רובוט או מכונית חכמה, עם ליווי של מדריך מנוסה.</div>'
         '<div><span class="big">🎮</span><b>מפעילים ונוסעים</b>מחברים לשלט או לטלפון, ויוצאים לנסיעת מבחן ראשונה.</div>'
         '<div><span class="big">🏆</span><b>תחרות וקרב רובוטים</b>מסיימים בתחרות קבוצתית או בקרב רובוטים, וחתן או כלת השמחה במרכז.</div>'
         '<div><span class="big">📍</span><b>אצלכם או אצלנו</b>מגיעים אליכם הביתה (דירה, בית פרטי או גינה) או מארחים במרכז שלנו ברמת גן, צמוד למגדלי ב.ס.ר.</div>'
         '</div></section>'
         '<section class="bd-sec"><h2>איך זה עובד</h2><ol class="bd-steps">'
         '<li>שולחים לנו תאריך, שעה, מספר ילדים וגיל, ואיפה החגיגה.</li>'
         '<li>בוחרים: פעילות של שעה וחצי או של שעתיים, ואיזה רובוט בונים.</li>'
         '<li>מקבלים הצעת מחיר מסודרת ושומרים את התאריך.</li>'
         '<li>ביום ההולדת אנחנו מגיעים עם כל הציוד, ואתם רק נהנים 🎂</li>'
         '</ol></section>'
         '<section class="bd-sec"><h2>מימי הולדת וסדנאות שלנו</h2></section>' + grid([p for p in PHOTOS if p[1] in ('group', 'kids')][:12]).replace('gl-grid', 'gl-grid bd') +
         '<section class="bd-q"><h2>רוצים יום הולדת רובוטי?</h2><p>שלחו לנו בוואטסאפ:</p><ul><li>תאריך ושעה</li><li>כמה ילדים ובאיזה גיל</li><li>איפה (עיר, דירה או בית פרטי)</li><li>שעה וחצי או שעתיים</li></ul>'
         '<a class="b" href="' + WA + '" target="_blank" rel="noopener">וואטסאפ</a><a class="b b2" href="tel:+972545639120">054-5639120</a></section>'
         + LB + LB_JS.replace("document.querySelectorAll('.gl-chips button')", "[]"))
page('יום הולדת רובוטי לילדים | Robotika4Kids', 'יום הולדת רובוטיקה לילדים: כל ילד בונה ומפעיל רובוט או מכונית חכמה, עם תחרות וקרב רובוטים. מגיעים אליכם או אצלנו ברמת גן. שעה וחצי או שעתיים.',
     'ימי-הולדת', '/img/ea89be29c470.webp', bbody, BSTYLE, '/ימי-הולדת')
print('ok')
