#!/usr/bin/env python3
"""
w42: new page /blog/tokyo-station-guide + offline /tokyo-pocket (neutral, plain-English station guide for Tokyo Station, station pilot page #1 in the plan).
Built from the Haneda generator (w31) pattern, adapted from the Kyoto station generator (w39).

Run from the repo root (after w35, w36, w38, w39 and w41):  python3 tools/w42_tokyo_station_page.py

What it does (idempotent):
  1. Builds public/blog/tokyo-station-guide.html from the site template taken from
     public/blog/japan-travel-packing-guide.html (head, CSS, nav, footer, tracking scripts)
     plus new body content, the Airalo eSIM block (copied from the Japan guide, placement id renamed to *-tokyo-station).
  2. Builds public/tokyo-pocket.html (offline pocket guide), tokyo-sw.js and tokyo-pocket.webmanifest.
  3. Adds one sentence linking to the new page in the Japan guide (marker: tokyo-station-guide link).
  4. Adds the page to public/sitemap.xml and bumps the Japan guide's lastmod.
It does NOT touch public/blog.html (no card on the blog index; the Travel Essentials hub card comes from w43).
Aborts without writing anything if an expected anchor is missing.
"""
import os, re, sys, json, html
from urllib.parse import quote

ROOT = os.getcwd()
BLOG = os.path.join(ROOT, "public", "blog")
SITEMAP = os.path.join(ROOT, "public", "sitemap.xml")
TEMPLATE = os.path.join(BLOG, "japan-travel-packing-guide.html")
OUT = os.path.join(BLOG, "tokyo-station-guide.html")
SITE = "https://www.packsmartapp.com"
SLUG = "tokyo-station-guide"
URL = "%s/blog/%s" % (SITE, SLUG)
TODAY = "2026-11-19"

TITLE = "Tokyo Station Guide 2026: Marunouchi vs Yaesu, Platforms & Luggage | PackSmart"
H1 = "Tokyo Station Guide 2026: Marunouchi vs Yaesu, Platforms and Luggage"
DESC = ("Plain-English Tokyo Station guide: Marunouchi vs Yaesu side, Shinkansen platforms, Narita Express, "
        "local trains and Metro, luggage, IC cards and food.")
KEYWORDS = ("Tokyo Station guide, Tokyo Station Marunouchi exit, Tokyo Station Yaesu exit, Tokyo Station Shinkansen platforms, "
            "Narita Express platform Tokyo Station, Tokyo Station luggage, Tokyo Station coin lockers, Tokyo Ramen Street, Tokyo Station to Disney, Welcome Suica Tokyo Station")
def die(msg):
    print("ABORT: " + msg)
    sys.exit(1)


if not os.path.isfile(TEMPLATE):
    die("template not found: " + TEMPLATE)
t = open(TEMPLATE, encoding="utf-8").read().split("\n")


def line(n):
    return t[n - 1]


# ---- sanity checks on the template anchors (1-indexed lines)
checks = [
    (25, 'rel="preconnect" href="https://fonts.googleapis.com"'),
    (28, "fonts.googleapis.com/css2"),
    (29, "googletagmanager.com/gtag/js"),
    (85, "<style>"),
    (454, "</style>"),
]
for n, needle in checks:
    if needle not in line(n):
        die("template line %d does not contain %r (template changed?)" % (n, needle))
NAV0 = next((i for i, l in enumerate(t) if '<nav class="nav" id="nav">' in l), None)
if NAV0 is None:
    die("nav not found in template")
NAV1 = next((i for i in range(NAV0, len(t)) if "</nav>" in t[i]), None)
if NAV1 is None:
    die("nav end not found in template")
FOOT = next((i for i, l in enumerate(t) if '<footer class="footer">' in l), None)
if FOOT is None:
    die("footer not found in template")
if "</html>" not in "\n".join(t[-3:]):
    die("template does not end with </html>")


# ---- helper: extract a placement block by id (balanced <div>)
def block(pid):
    start = None
    for i, l in enumerate(t):
        if ('data-ps-placement="%s"' % pid) in l and l.lstrip().startswith("<div"):
            start = i
            break
    if start is None:
        die("placement block not found: " + pid)
    depth = 0
    for j in range(start, len(t)):
        depth += len(re.findall(r"<div\b", t[j])) - len(re.findall(r"</div>", t[j]))
        if depth == 0:
            return "\n".join(t[start:j + 1])
    die("unbalanced block: " + pid)


airalo = block("airalo-japan").replace("airalo-japan", "airalo-tokyo-station")
_a = "Install it before you fly, switch it on when you land. No airport SIM queue."
if _a not in airalo:
    die("airalo tagline not found")
airalo = airalo.replace(_a, "Install it on your phone and switch it on when you need it. No counter, no queue.")
# ---------------------------------------------------------------- body content
def esc(s):
    return html.escape(s, quote=False)


FAQ = [
    ("Which exit should I use at Tokyo Station: Marunouchi or Yaesu?",
     "Tokyo Station has two main sides. The Marunouchi side is the west side, with the red-brick station building, and the Yaesu side is the east side. "
     "For bullet train tickets bought on Smart EX, Tokyo Station City recommends the Yaesu side and describes the Marunouchi side as about a 10-minute walk away. "
     "The route to the Narita Express platform starts at the Marunouchi Central Gate, and the JR East Travel Service Center is on the Marunouchi side. The airport limousine buses leave from the Yaesu North Exit."),
    ("Which platforms are the Shinkansen at Tokyo Station?",
     "Tokyo Station City lists platforms 14 to 19 for the Tokaido and Sanyo Shinkansen (to Nagoya, Kyoto, Shin-Osaka, Hiroshima and Hakata) and platforms 20 to 23 for the Tohoku, Joetsu and Hokuriku Shinkansen (to Sendai, Nagano, Echigo-Yuzawa and Kanazawa). "
     "On the 1st floor, head toward the central information counter along the central passage, look for the blue ticket gates, and check the platform on the electronic board inside the gate."),
    ("Where is the Narita Express platform?",
     "Tokyo Station City says the Narita Express leaves from underground platforms 3 and 4. From the Marunouchi Central Gate, go down to B1, then to B4, then to the B5 platform level. "
     "JR East's timetables also show some trains using tracks 1 and 2, so check the departure board. Several platforms in the station share the numbers 1 to 4, so look for the line name as well as the number. "
     "The Narita Express is all reserved seating, and JR East's timetables give roughly an hour from Narita Airport."),
    ("Can I use the JR Tokyo Wide Pass on the Tokaido Shinkansen?",
     "No. JR East says the JR TOKYO Wide Pass cannot be used on the Tokaido Shinkansen, because that line is run by a different company, JR Central. "
     "JR East's reservation service also cannot book the Tokaido and Sanyo Shinkansen, so use JR Central's Smart EX or a ticket office."),
    ("How big a suitcase can I take on the Shinkansen?",
     "On the Tokaido and Sanyo Shinkansen, JR Central says a bag with three sides adding up to more than 160 cm, up to 250 cm, needs a seat with an oversized baggage area, reserved in advance. "
     "Bags of 160 cm or less go on the overhead racks, at your feet, or in the deck storage area with no extra booking. JR East says its Tohoku, Joetsu and Hokuriku lines have no designated seats for oversized luggage."),
    ("Where can I leave my luggage at Tokyo Station?",
     "JR East's Travel Service Center offers temporary luggage storage, and items are kept for the day only. There are also coin lockers around the station, and Tokyo Station City links to a locker search and reservation tool. "
     "JNTO warns that lockers in very busy places fill up quickly. A Welcome Suica card can pay for a locker and unlock it. We did not find official locker prices, so we give none."),
    ("Where is the JR East Travel Service Center?",
     "JR East says that after you pass through the Marunouchi North Exit ticket gate on the 1st floor, the center is on your left. "
     "It exchanges rail passes, sells passes and tickets, exchanges currency, stores luggage for the day, and has a prayer room open 10:00 to 17:00. There is also a counter inside JAPAN RAIL CAFE TOKYO on the Yaesu side, outside the Yaesu Central Exit. "
     "JR East and JNTO print different opening hours, so check JR East's page before you go."),
    ("Where can I buy a Welcome Suica?",
     "JR East sells the Welcome Suica at its Travel Service Centers, including the one at Tokyo Station, at JAPAN RAIL CAFE, and from machines at Narita and Haneda airports. "
     "It lasts 28 days, needs no deposit and, in principle, only one is sold to each person. It works on trains, buses and in many shops across Japan. "
     "JNTO also lists the TOURIST PASMO as a deposit-free card for visitors."),
    ("How do I get from Tokyo Station to Tokyo Disney Resort?",
     "Take the JR Keiyo Line (or the Musashino Line) to Maihama Station. Tokyo Disney Resort says it takes about 15 minutes, and Tokyo Disneyland is a short walk from the station. "
     "For Tokyo DisneySea, change at Resort Gateway Station to the Disney Resort Line monorail. The Keiyo platforms are a separate part of Tokyo Station, so follow the signs and give yourself extra time. We did not find an official walking time."),
    ("How do I get from Tokyo Station to Haneda Airport?",
     "Tokyo Monorail says its Haneda Express takes 13 minutes from Hamamatsucho to Haneda Airport Terminal 3, and Hamamatsucho is on the JR Yamanote Line. "
     "The Airport Limousine Bus also runs from the Yaesu North Exit (Tekko Building) to Haneda, according to the bus company. Our Haneda guide has the full list of options."),
    ("Where can I eat in the station?",
     "First Avenue Tokyo Station, on the Yaesu side underground, has Tokyo Ramen Street (10:30 to 23:00, last orders 22:30) and Tokyo Character Street (10:00 to 20:30), according to the First Avenue site. "
     "Inside the ticket gates, GRANSTA Tokyo has shops such as Ekibenya Matsuri for boxed meals (5:30 to 22:00). Hours differ by shop, so check before you go."),
    ("Is there a hotel inside Tokyo Station?",
     "Yes. The Tokyo Station Hotel is inside the red-brick Marunouchi building, with its main entrance on the ground floor, reached directly from the JR Marunouchi South Gate, according to the hotel's access map."),
    ("How do I get to the Marunouchi Line and other Metro lines?",
     "The Tokyo Metro Marunouchi Line has its own Tokyo Station, number M17. JNTO adds that long underground passages link Tokyo Station with Otemachi Station, where the Tozai, Chiyoda, Hanzomon and Toei Mita lines stop, though it is a bit of a walk."),
]
def faq_html():
    out = ['<h2 id="faq">Frequently Asked Questions</h2>']
    for q, a in FAQ:
        out.append("<h3>%s</h3>\n<p>%s</p>" % (esc(q), esc(a)))
    return "\n".join(out)


ld_faq = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ
    ],
}
ld_article = {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": H1,
    "description": DESC,
    "image": SITE + "/og-default.png",
    "datePublished": TODAY,
    "dateModified": TODAY,
    "author": {"@type": "Organization", "name": "PackSmart"},
    "publisher": {"@type": "Organization", "name": "PackSmart",
                  "logo": {"@type": "ImageObject", "url": SITE + "/logo.png"}},
    "mainEntityOfPage": URL,
    "about": {"@type": "TrainStation", "name": "Tokyo Station"},
}
ld_crumbs = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE},
        {"@type": "ListItem", "position": 2, "name": "Travel Essentials", "item": SITE + "/travel-essentials"},
        {"@type": "ListItem", "position": 3, "name": "Tokyo Station Guide", "item": URL},
    ],
}


def ld(obj):
    return '<script type="application/ld+json">\n%s\n</script>' % json.dumps(obj, ensure_ascii=False)


TOC = [
    ("one-page", "Tokyo Station on one page"),
    ("which-side", "Which side: Marunouchi or Yaesu?"),
    ("shinkansen", "Bullet trains at Tokyo Station"),
    ("narita", "Narita Express and the airports"),
    ("rail", "Local trains, Metro and Disney"),
    ("connected", "Getting online: eSIM and Wi-Fi"),
    ("cards", "Paying for trains: IC cards"),
    ("luggage", "Lockers and luggage"),
    ("food", "Eating in the station"),
    ("finder", "Find it fast: lockers, information, tickets"),
    ("facilities", "Facilities in the station"),
    ("help", "Help for older travellers and anyone who needs assistance"),
    ("leaving", "Leaving Tokyo by train or bus"),
    ("faq", "FAQ"),
    ("about-this-guide", "About this guide and change log"),
]
# ---- v71: "What do you need first?" tiles + a quick-jump bar that appears once you scroll
TOC_SHORT = {
    "one-page": "On one page", "which-side": "Which side", "shinkansen": "Bullet trains", "narita": "Narita Express", "rail": "Local trains",
    "connected": "Get online", "cards": "IC cards", "luggage": "Luggage", "food": "Eating", "finder": "Find it fast",
    "facilities": "Facilities", "help": "Help", "leaving": "Leaving", "faq": "FAQ", "about-this-guide": "About",
}
TOC_TILES = [
    ("which-side", "&#129517;", "Which side?", "Marunouchi or Yaesu"),
    ("shinkansen", "&#128645;", "Bullet trains", "Platforms 14 to 23"),
    ("narita", "&#9992;&#65039;", "Narita Express", "Underground platforms"),
    ("rail", "&#128646;", "Local trains", "Yamanote, Metro, Disney"),
    ("luggage", "&#129523;", "Luggage and lockers", "Hands-free"),
    ("finder", "&#128269;", "Find it fast", "Lockers, info, tickets"),
    ("help", "&#129309;", "Help and assistance", "For older travellers"),
]
TOC_CSS = """<style>
html{scroll-behavior:smooth}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
""" + ",".join("#%s" % i for i, _ in TOC) + """{scroll-margin-top:var(--psn-off,150px)}
.psn-now{background:#E7FAF5;border:1px solid #cdeee5;border-left:4px solid #00C9A7;border-radius:14px;padding:20px;margin:24px 0}
.psn-now h3{margin:0 0 4px;font-size:1.2rem;color:#0f0f23}
.psn-now p.psn-sub{margin:0 0 14px;font-size:.95rem;color:#555}
.psn-tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(138px,1fr));gap:10px}
.psn-tile{display:flex;flex-direction:column;gap:2px;background:#fff;border:1.5px solid #cdeee5;border-radius:12px;padding:14px 14px 12px;text-decoration:none!important;color:#0f0f23!important;transition:border-color .15s,box-shadow .15s}
.psn-tile:hover,.psn-tile:focus-visible{border-color:#00C9A7;box-shadow:0 2px 10px rgba(0,201,167,.25)}
.psn-tile .em{font-size:1.6rem;line-height:1.1;margin-bottom:4px}
.psn-tile b{font-size:1.02rem}
.psn-tile small{color:#666;font-size:.82rem}
.psn-now details{margin-top:12px}
.psn-now summary{cursor:pointer;font-weight:700;color:#0a8f78;font-size:.95rem;padding:6px 0}
.psn-now ol{columns:2;column-gap:24px;margin:8px 0 0;padding-left:1.3rem;font-size:.92rem}
.psn-now li{margin:0 0 6px;break-inside:avoid}
.psn-now li a{color:#0f0f23}
#psnBar{position:fixed;left:0;right:0;top:var(--psn-top,64px);z-index:40;background:rgba(255,255,255,.97);-webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px);border-bottom:1px solid #e9f3f0;padding:10px 0;transform:translateY(-130%);visibility:hidden;transition:transform .25s ease-out,visibility .25s}
#psnBar.on{transform:none;visibility:visible}
#psnBar .in{max-width:800px;margin:0 auto;padding:0 20px;display:flex;gap:8px;align-items:center}
#psnBar .rail{flex:1;min-width:0;display:flex;gap:8px;overflow-x:auto;scrollbar-width:none;-webkit-overflow-scrolling:touch;align-items:center}
#psnBar .rail::-webkit-scrollbar{display:none}
#psnBar .chip{flex:none;text-decoration:none;font-weight:700;font-size:.92rem;color:#0f0f23;background:#fff;border:1.5px solid #cdeee5;border-radius:999px;padding:8px 14px;white-space:nowrap;transition:background .15s,border-color .15s}
#psnBar .chip:hover{border-color:#00C9A7}
#psnBar .chip.cur{background:#00C9A7;border-color:#00C9A7}
#psnBar .up{flex:none;width:38px;height:38px;border-radius:50%;border:1.5px solid #00C9A7;background:#fff;color:#0a8f78;font-size:1.1rem;font-weight:800;display:flex;align-items:center;justify-content:center;cursor:pointer;padding:0;font-family:inherit}
@media (max-width:600px){.psn-now ol{columns:1}.psn-tiles .psn-tile:last-child:nth-child(odd){grid-column:1/-1}}
@media print{#psnBar{display:none!important}}
</style>"""
toc_html = (
    TOC_CSS
    + '\n<div class="psn-now" id="contents"><h3>What do you need first?</h3><p class="psn-sub">Tap a card to jump straight there.</p>'
    + '<div class="psn-tiles">'
    + "".join('<a class="psn-tile" href="#%s" data-psn="tile-%s"><span class="em">%s</span><b>%s</b><small>%s</small></a>' % (i, i, e, esc(b), esc(sm)) for i, e, b, sm in TOC_TILES)
    + '</div>\n<details><summary>See all %d sections</summary><ol>' % len(TOC)
    + "".join('<li><a href="#%s" data-psn="list-%s">%s</a></li>' % (i, i, esc(n)) for i, n in TOC)
    + '</ol></details></div>\n'
    + '<div id="psnBar" role="navigation" aria-label="Jump to a section"><div class="in">'
    + '<button type="button" class="up" aria-label="Back to the top of the page" data-psn="up">&uarr;</button><div class="rail">'
    + "".join('<a class="chip" href="#%s" data-id="%s" data-psn="chip-%s">%s</a>' % (i, i, i, esc(TOC_SHORT[i])) for i, _ in TOC)
    + '</div></div></div>\n'
    + """<script>
(function(){
  var bar=document.getElementById('psnBar'); if(!bar) return;
  var rail=bar.querySelector('.rail'), chips=[].slice.call(rail.querySelectorAll('.chip')), nav=document.getElementById('nav');
  var ids=chips.map(function(c){return c.getAttribute('data-id')}), cur=null, tick=false;
  function ev(a){ try{ if(window.gtag) gtag('event','toc_nav',{event_category:'engagement',action:a,page_path:location.pathname}); }catch(e){} }
  function setTop(){ var h=nav?Math.round(nav.getBoundingClientRect().bottom):64; if(h<0||h>140) h=64; document.documentElement.style.setProperty('--psn-top',h+'px'); document.documentElement.style.setProperty('--psn-off',(h+84)+'px'); }
  function current(){ var y=window.pageYOffset+260, c=null; ids.forEach(function(id){ var e=document.getElementById(id); if(e&&e.getBoundingClientRect().top+window.pageYOffset<=y) c=id; }); return c; }
  function paint(){
    tick=false;
    var box=document.getElementById('contents'), on=box?box.getBoundingClientRect().bottom<(parseInt(getComputedStyle(document.documentElement).getPropertyValue('--psn-top'),10)||64):window.pageYOffset>520;
    bar.classList.toggle('on',on);
    var c=on?current():null;
    if(c===cur) return; cur=c;
    chips.forEach(function(a){
      var is=a.getAttribute('data-id')===c; a.classList.toggle('cur',is);
      if(is){ a.setAttribute('aria-current','true'); var t=a.offsetLeft-rail.offsetLeft-rail.clientWidth/2+a.offsetWidth/2; if(Math.abs(rail.scrollLeft-t)>8) rail.scrollTo({left:t}); } else a.removeAttribute('aria-current');
    });
  }
  function req(){ if(!tick){ tick=true; requestAnimationFrame(paint); } }
  window.addEventListener('scroll',req,{passive:true}); window.addEventListener('resize',function(){ setTop(); req(); });
  setTop(); paint();
  bar.querySelector('.up').addEventListener('click',function(){ try{ window.scrollTo({top:0,behavior:'smooth'}); }catch(e){ window.scrollTo(0,0); } });
  document.addEventListener('click',function(e){ var a=e.target.closest&&e.target.closest('[data-psn]'); if(a) ev(a.getAttribute('data-psn')); });
})();
</script>"""
)

PRINT_CSS = """<style>
.ps-card{background:#fff;border:2px solid #00C9A7;border-radius:14px;padding:22px 24px;margin:24px 0;}
.ps-card h2{margin-top:0!important;}
.ps-card ul{margin:0 0 14px 1.2rem;padding:0;}
.ps-card li{font-size:1.08rem;line-height:1.55;margin:0 0 9px;}
.ps-print-btn{font:inherit;font-size:1rem;font-weight:700;color:#fff;background:#00C9A7;border:0;border-radius:10px;padding:12px 20px;cursor:pointer;}
.ps-print-btn:hover,.ps-print-btn:focus-visible{background:#00b396;}
.ps-note{font-size:0.82rem;color:#777;line-height:1.5;margin:6px 0 18px;}
.ps-scroll{overflow-x:auto;-webkit-overflow-scrolling:touch;margin:0 0 20px;}
.ps-scroll table{min-width:560px;}
@media(max-width:600px){
  .ps-scroll{overflow:visible;}
  .ps-scroll table{min-width:0;display:block;border:0;box-shadow:none;}
  .ps-scroll thead{display:none;}
  .ps-scroll tbody{display:block;}
  .ps-scroll tr{display:block;border:1px solid #E9ECEF;border-radius:10px;margin:0 0 12px;padding:6px 0;background:#fff;}
  .ps-scroll td{display:block;border:0!important;padding:5px 14px!important;font-size:1rem;}
  .ps-scroll td:first-child{font-size:1.08rem;padding-top:8px!important;}
  .ps-scroll td[data-label]:not(:first-child)::before{content:attr(data-label);display:block;font-size:0.72rem;font-weight:700;color:#00967d;text-transform:uppercase;letter-spacing:0.03em;}
}

.ps-fig{margin:22px 0;text-align:center;}
.ps-fig svg{width:100%;max-width:480px;height:auto;display:block;margin:0 auto;}
.ps-fig figcaption{font-size:0.85rem;color:#777;margin-top:6px;}
.ps-btn2{font:inherit;font-size:1rem;font-weight:700;color:#0f0f23;background:#fff;border:2px solid #00C9A7;border-radius:10px;padding:12px 18px;cursor:pointer;margin:6px 6px 0 0;}
.ps-btn2:hover,.ps-btn2:focus-visible{background:#00C9A7;color:#fff;}
.ps-finder{background:#fff;border:2px solid #00C9A7;border-radius:14px;padding:22px 24px;margin:24px 0;}
.ps-finder h2{margin-top:0!important;}
.ps-step-h{font-weight:700;font-size:1.1rem;margin:14px 0 6px;}
.ps-chips{display:flex;flex-wrap:wrap;gap:10px;}
.ps-chip{font:inherit;font-size:1.05rem;font-weight:600;min-height:48px;padding:10px 16px;border-radius:12px;border:2px solid #E9ECEF;background:#fff;color:#0f0f23;cursor:pointer;}
.ps-chip:hover{border-color:#00C9A7;}
.ps-chip[aria-pressed="true"]{background:#00C9A7;border-color:#00C9A7;color:#fff;}
.ps-result{margin-top:18px;padding:16px 18px;border-radius:12px;background:#F1FBF9;border-left:5px solid #00C9A7;font-size:1.2rem;line-height:1.5;}
.ps-result small{display:block;font-size:0.88rem;color:#666;margin-top:8px;line-height:1.45;}
.ps-about{background:#f8f9fa;border-radius:12px;padding:16px 20px;margin:28px 0;font-size:0.95rem;line-height:1.6;}
.ps-about h2{margin:0 0 6px!important;font-size:1.15rem!important;}
.ps-about ul{margin:6px 0 0 1.2rem;padding:0;}
@media(max-width:600px){.ps-finder{padding:16px;}.ps-chip{flex:1 1 100%;text-align:left;}}
@media(max-width:820px){.ps-qr.ps-qr-screen{display:none}}
.ps-qr{display:flex;align-items:center;gap:14px;margin:4px 0 16px;padding:12px 14px;border:1px solid #E9ECEF;border-radius:12px;background:#fff;}
.ps-qr svg{width:116px;height:116px;flex:none;}
.ps-qr p{margin:0;font-size:0.95rem;line-height:1.45;color:#333;}
.ps-qr .u{display:block;font-weight:700;font-size:1rem;color:#0f0f23;margin-top:4px;word-break:break-all;}
.ps-qr.ps-qr-print{display:none;}
@media print{
  body *:not(.ps-card):not(.ps-card *):not(:has(.ps-card)){display:none!important}
  body *{visibility:hidden!important}
  .ps-card,.ps-card *{visibility:visible!important}
  .ps-qr.ps-qr-print{display:flex!important}
  .ps-qr.ps-qr-screen{display:none!important}
  .ps-card{position:absolute;left:0;top:0;width:100%;border:0;box-shadow:none}
  .ps-print-btn{display:none!important}
}
</style>"""

def _dg_pill(y, text, fill, stroke, color, weight="600"):
    return ('<rect x="48" y="%d" width="392" height="34" rx="17" fill="%s" stroke="%s" stroke-width="1.5"/>' % (y, fill, stroke)
            + '<text x="244" y="%d" font-size="17" font-weight="%s" text-anchor="middle" fill="%s">%s</text>' % (y + 23, weight, color, text))


_DG_SVG = (
    '<svg id="tokDiagram" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 624" role="img" aria-labelledby="tokT tokD" font-family="Arial, Helvetica, sans-serif">'
    '<title id="tokT">Tokyo Station at a glance</title>'
    '<desc id="tokD">Tokyo Station has two sides. The Marunouchi side, to the west, has the red-brick station building, the Narita Express route, the JR East Travel Service Center and the Tokyo Station Hotel. '
    'The Yaesu side, to the east, has the main bullet train approach, First Avenue shops and ramen, and the airport and highway buses. '
    'They are linked by the central passage on the first floor.</desc>'
    '<rect width="480" height="624" fill="#fff"/>'
    '<text x="240" y="38" font-size="26" font-weight="700" text-anchor="middle" fill="#0f0f23">Tokyo Station at a glance</text>'
    '<text x="240" y="64" font-size="17" text-anchor="middle" fill="#555">Marunouchi for the red-brick side, Yaesu for bullet trains</text>'
    '<rect x="24" y="88" width="432" height="212" rx="18" fill="#FBEFEA" stroke="#B5482B" stroke-width="2"/>'
    '<text x="48" y="128" font-size="28" font-weight="700" fill="#0f0f23">Marunouchi side (west)</text>'
    '<text x="48" y="152" font-size="18" fill="#0f0f23">Red-brick station building</text>'
    + _dg_pill(164, "Narita Express route, hotel, gallery", "#fff", "#B5482B", "#7a2e17", "700")
    + _dg_pill(204, "JR East Travel Service Center", "#fff", "#B5482B", "#7a2e17")
    + _dg_pill(244, "Marunouchi Central Gate (1F)", "#fff", "#B5482B", "#7a2e17")
    + '<line x1="240" y1="304" x2="240" y2="376" stroke="#2563EB" stroke-width="4" stroke-dasharray="8 6" stroke-linecap="round"/>'
    '<text x="254" y="334" font-size="15" font-weight="700" fill="#2563EB">Central passage, 1F</text>'
    '<text x="254" y="358" font-size="15" fill="#2563EB">links the two sides</text>'
    '<rect x="24" y="380" width="432" height="212" rx="18" fill="#EEF0FB" stroke="#34346e" stroke-width="2"/>'
    '<text x="48" y="420" font-size="28" font-weight="700" fill="#0f0f23">Yaesu side (east)</text>'
    '<text x="48" y="444" font-size="18" fill="#0f0f23">Bullet trains, shops and buses</text>'
    + _dg_pill(456, "Shinkansen, platforms 14 to 23", "#fff", "#34346e", "#1a1a3e", "700")
    + _dg_pill(496, "Airport and highway buses", "#fff", "#34346e", "#1a1a3e")
    + _dg_pill(536, "First Avenue, Ramen Street", "#fff", "#34346e", "#1a1a3e")
    + '<text x="240" y="614" font-size="14" text-anchor="middle" fill="#777">Simplified, not to scale. packsmartapp.com</text></svg>'
)

DIAGRAM = '<figure class="ps-fig" id="at-a-glance">\n' + _DG_SVG + """
<button type="button" class="ps-btn2" id="tokDl">Download the diagram (PNG)</button>
</figure>
<script>
(function(){
  var b=document.getElementById('tokDl'); if(!b) return;
  b.addEventListener('click',function(){
    try{
      var svg=document.getElementById('tokDiagram');
      var xml=new XMLSerializer().serializeToString(svg);
      var img=new Image();
      img.onload=function(){
        var c=document.createElement('canvas'); c.width=960; c.height=1248;
        var x=c.getContext('2d'); x.fillStyle='#fff'; x.fillRect(0,0,c.width,c.height); x.drawImage(img,0,0,c.width,c.height);
        c.toBlob(function(bl){
          var a=document.createElement('a'); a.href=URL.createObjectURL(bl); a.download='tokyo-station-at-a-glance.png';
          document.body.appendChild(a); a.click(); document.body.removeChild(a);
        },'image/png');
      };
      img.src='data:image/svg+xml;charset=utf-8,'+encodeURIComponent(xml);
    }catch(e){ window.print(); }
  });
})();
</script>"""
_NONE = "We did not find this on the official station pages. Please ask station staff."
FINDER_DATA = {
    "terms": [["T1", "Marunouchi"], ["T2", "Yaesu"]],
    "items": [
        ["toilet", "Toilets", {
            "T1": "We did not find an official list of toilet locations for the Marunouchi side. Follow the toilet signs, or ask at the JR East Information Center (1F Marunouchi Central Exit, 10 am to 6 pm).",
            "T2": "We did not find an official list of toilet locations for the Yaesu side. Follow the toilet signs, or ask station staff."}],
        ["lockers", "Luggage lockers and storage", {
            "T1": "The JR East Travel Service Center keeps luggage for the day only (it is on your left after the Marunouchi North ticket gate, 1F). Coin lockers are around the station: Tokyo Station City links to a locker search tool. Lockers in big stations fill up fast (JNTO). We did not find official locker prices.",
            "T2": "Coin lockers are around the station, including the Yaesu side: Tokyo Station City links to a locker search tool. Lockers in big stations fill up fast (JNTO). A Welcome Suica card can pay for a locker and unlock it (JR East). We did not find official locker prices."}],
        ["info", "Tourist information", {
            "T1": "The JR East Travel Service Center is on your left after the Marunouchi North ticket gate (1F). JR East Information Centers (10 am to 6 pm) are at the 1F Central Passage, the 1F Marunouchi Central Exit and the B1 Marunouchi Underground Central Exit, inside the gates. JR East and JNTO print different hours for the Travel Service Center, so check JR East's page.",
            "T2": "JAPAN RAIL CAFE TOKYO is on the 1st floor of the GRAN TOKYO North Tower, outside the Yaesu Central Exit (8 am to 9 pm daily, Tokyo Station City), and JR East has a counter there. The main Travel Service Center is on the Marunouchi side, reached by the central passage on 1F."}],
        ["tickets", "Tickets and passes", {
            "T1": "The JR East Travel Service Center exchanges and sells rail passes and tickets. It also sells the Welcome Suica. For the Tokaido Shinkansen, Tokyo Station City suggests the Yaesu side, which it says is about a 10-minute walk from the Marunouchi side.",
            "T2": "Tokyo Station City tells Smart EX users to use the Yaesu side for the bullet trains. JR East's reservation service cannot book the Tokaido and Sanyo Shinkansen. The JR TOKYO Wide Pass is not valid on the Tokaido Shinkansen."}],
        ["help", "Wheelchair, lifts and help", {
            "T1": "Ask station staff, or go to a JR East Information Center. We did not find an official list of lift locations in the pages we read. In an emergency, call 119.",
            "T2": "Ask station staff. We did not find an official list of lift locations in the pages we read. In an emergency, call 119."}],
        ["baby", "Nursing room", {
            "T1": _NONE,
            "T2": _NONE}],
        ["wifi", "Wi-Fi and SIM", {
            "T1": "JR East lists free Wi-Fi at the Travel Service Center. We did not find an official list of SIM or Wi-Fi rental counters in the station. An eSIM installed on your phone needs no counter.",
            "T2": "We did not find an official list of SIM or Wi-Fi rental counters in the station. An eSIM installed on your phone needs no counter."}],
        ["food", "Food and drink", {
            "T1": "Inside the gates, GRANSTA Tokyo has Ekibenya Matsuri for boxed meals (5:30 am to 10 pm) and Honnoriya for rice balls (6 am to 10 pm). Tokyo Station Cafe North Dome and T's TanTan (vegan ramen, 10 am to 10 pm) are outside the gates. Hours differ by shop.",
            "T2": "First Avenue Tokyo Station, underground on the Yaesu side: Tokyo Ramen Street (10:30 am to 11 pm, last order 10:30 pm), Okashi Land (9 am to 9 pm) and Tokyo Character Street (10 am to 8:30 pm). Some ramen shops open earlier. Check each shop."}],
        ["unwell", "Feeling unwell", {
            "T1": "Tell station staff, or go to a JR East Information Center. In an emergency, call 119.",
            "T2": "Tell station staff. In an emergency, call 119."}],
    ],
}
_ORDER = ["toilet", "lockers", "info", "tickets", "help", "baby", "wifi", "food", "unwell"]
assert sorted(_ORDER) == sorted(i[0] for i in FINDER_DATA["items"])
FINDER_DATA["items"].sort(key=lambda i: _ORDER.index(i[0]))
FINDER = """<section class="ps-finder" id="finder">
<h2>Find it fast</h2>
<p>Choose your side of the station, then what you need. Large buttons, no typing.</p>
<p class="ps-step-h">1. Which side are you on?</p>
<div class="ps-chips" id="fdTerm"></div>
<p class="ps-step-h">2. What do you need?</p>
<div class="ps-chips" id="fdWhat"></div>
<div class="ps-result" id="fdResult" aria-live="polite">Choose a side and what you need, and the answer shows here.</div>
<noscript><p>This tool needs JavaScript. The full table is just below.</p></noscript>
</section>
<script>
(function(){
  var D=__FINDER_JSON__;
  var term=null, what=null;
  var tEl=document.getElementById('fdTerm'), wEl=document.getElementById('fdWhat'), rEl=document.getElementById('fdResult');
  if(!tEl||!wEl||!rEl) return;
  function mk(label,id,group){
    var b=document.createElement('button'); b.type='button'; b.className='ps-chip'; b.textContent=label; b.setAttribute('aria-pressed','false'); b.setAttribute('data-id',id);
    b.addEventListener('click',function(){
      if(group==='t'){term=id;} else {what=id;}
      [].forEach.call((group==='t'?tEl:wEl).children,function(c){c.setAttribute('aria-pressed',c.getAttribute('data-id')===id?'true':'false');});
      show();
    });
    return b;
  }
  D.terms.forEach(function(t){tEl.appendChild(mk(t[1],t[0],'t'));});
  D.items.forEach(function(i){wEl.appendChild(mk(i[1],i[0],'w'));});
  function show(){
    if(!term||!what){ rEl.textContent=!term?'Now choose your side.':'Now choose what you need.'; return; }
    var tn=D.terms.filter(function(t){return t[0]===term;})[0][1];
    var it=D.items.filter(function(i){return i[0]===what;})[0];
    var txt=it[2][term];
    rEl.innerHTML='';
    var s=document.createElement('strong'); s.textContent=it[1]+' at '+tn; rEl.appendChild(s);
    rEl.appendChild(document.createElement('br'));
    rEl.appendChild(document.createTextNode(txt?txt:'We did not find this on the official station pages. Please ask station staff.'));
    var sm=document.createElement('small'); sm.textContent='From Tokyo Station City, JR East, First Avenue and JNTO pages, checked 19 November 2026. Floors and hours can change. If you cannot find it, ask station staff or a JR East Information Center.'; rEl.appendChild(sm);
  }
})();
</script>"""
FINDER = FINDER.replace("__FINDER_JSON__", json.dumps(FINDER_DATA, ensure_ascii=False))

CHOOSER = """<h3>Which side is yours?</h3>
<div class="ps-scroll">
<table class="checklist-table">
<thead><tr><th>You are going to</th><th>Easiest side</th><th>Why</th></tr></thead>
<tbody>
<tr><td><strong>Shinkansen (bullet train)</strong></td><td>Yaesu side (east)</td><td>Tokyo Station City recommends the Yaesu side for Smart EX bullet train tickets, and says the Marunouchi side is about a 10-minute walk away. The Tokaido and Sanyo Shinkansen use platforms 14 to 19, and the Tohoku, Joetsu and Hokuriku lines use 20 to 23.</td></tr>
<tr><td><strong>Narita Express (N&rsquo;EX)</strong></td><td>Marunouchi side (west)</td><td>Tokyo Station City starts the route at the Marunouchi Central Gate: down to B1, then B4, then B5, to underground platforms 3 and 4.</td></tr>
<tr><td><strong>Airport Limousine Bus to Haneda or Narita</strong></td><td>Yaesu side (east)</td><td>The bus company lists the stop at the Yaesu North Exit (Tekko Building).</td></tr>
<tr><td><strong>Highway buses</strong></td><td>Yaesu side (east)</td><td>JNTO lists the JR Highway Bus Terminal at the Yaesu South Exit, and the Tekko Building terminal about 2 minutes from the Yaesu North Exit.</td></tr>
<tr><td><strong>JR East Travel Service Center</strong></td><td>Marunouchi side (west)</td><td>JR East says it is on your left after the Marunouchi North ticket gate on the 1st floor.</td></tr>
<tr><td><strong>Ramen Street and Character Street</strong></td><td>Yaesu side (east)</td><td>They are in First Avenue Tokyo Station, underground, connected to the Yaesu Underground Central gate.</td></tr>
<tr><td><strong>Red-brick building, Tokyo Station Hotel and Tokyo Station Gallery</strong></td><td>Marunouchi side (west)</td><td>The hotel entrance is on the ground floor, direct from the Marunouchi South Gate. The gallery is in front of the Marunouchi North Gate.</td></tr>
<tr><td><strong>Yamanote Line, Keiyo Line (for Disney), Metro Marunouchi Line</strong></td><td>Follow the line name on the signs</td><td>Several platforms share the numbers 1 to 4, so look for the line name as well as the number. The Marunouchi Line has its own station, M17.</td></tr>
<tr><td><strong>Not sure</strong></td><td>Check your ticket or booking</td><td>Bullet trains and airport buses are on the Yaesu side. The Narita Express route, the Travel Service Center and the red-brick building are on the Marunouchi side.</td></tr>
</tbody>
</table>
</div>
"""


LUGGAGE = """<h2 id="luggage">Lockers and luggage</h2>
<p>Tokyo Station City describes the station as 28 platforms and about 182,000 square metres, so it is worth sorting out your bags before you start walking. You have three choices: a coin locker, the storage counter, or sending the bag to your hotel.</p>
<ul>
<li><strong>Coin lockers.</strong> Tokyo Station City links to a locker search and reservation tool on its website. JNTO warns that lockers at very busy stations fill up quickly. A Welcome Suica card can pay for a locker and unlock it, according to JR East. We did not find an official list of sizes and fees, so we give none.</li>
<li><strong>JR East Travel Service Center.</strong> JR East says it keeps luggage for the day only. It is on your left after the Marunouchi North ticket gate on the 1st floor. Opening hours differ between JR East and JNTO, so check JR East's page before you go.</li>
<li><strong>Sending a bag to your hotel.</strong> JNTO's hands-free travel page, an older page, names a delivery counter at the Marunouchi North Exit. We did not confirm that it is current, or its cut-off time, so check JR East's page for the delivery counter.</li>
<li><strong>Keep with you:</strong> medicines, valuables, chargers and a change of clothes.</li>
<li><strong>Have these ready:</strong> your hotel name, address and phone number, written down.</li>
</ul>
<h3>Big suitcases on the Shinkansen</h3>
<div class="ps-scroll">
<table class="checklist-table">
<thead><tr><th>Line</th><th>Bag size</th><th>What the operator says</th></tr></thead>
<tbody>
<tr><td><strong>Tokaido and Sanyo (JR Central)</strong></td><td>160 cm or less (sum of three sides)</td><td>Overhead racks, at your feet, or the deck storage area. No extra booking.</td></tr>
<tr><td><strong>Tokaido and Sanyo (JR Central)</strong></td><td>Over 160 cm, up to 250 cm</td><td>You need a seat with an oversized baggage area, reserved in advance.</td></tr>
<tr><td><strong>Tohoku, Joetsu and Hokuriku (JR East)</strong></td><td>Any</td><td>JR East says there are no designated seats for oversized luggage on these lines.</td></tr>
</tbody>
</table>
</div>
<p class="ps-note">Sources: <a href="https://www.tokyostationcity.com/en/" target="_blank" rel="noopener noreferrer">Tokyo Station City</a>, <a href="https://www.jreast.co.jp/en/" target="_blank" rel="noopener noreferrer">JR East</a>, <a href="https://global.jr-central.co.jp/en/" target="_blank" rel="noopener noreferrer">JR Central</a> and <a href="https://www.japan.travel/en/" target="_blank" rel="noopener noreferrer">JNTO</a>. Checked 19 November 2026. Hours and counters change, so confirm at the counter.</p>"""

HELP = """<h2 id="help">Help for older travellers and anyone who needs assistance</h2>
<p>You do not have to cope alone. Asking early is easier than struggling.</p>
<ul>
<li><strong>Information centres.</strong> JR East Information Centers (10 am to 6 pm) are at the 1st-floor central passage, the 1st-floor Marunouchi Central Exit and the B1 Marunouchi Underground Central Exit, inside the ticket gates. The JR East Travel Service Center is on your left after the Marunouchi North ticket gate.</li>
<li><strong>Station staff.</strong> Tell staff at a ticket gate or ticket office if you need help or are not sure which way to go.</li>
<li><strong>Allow extra time.</strong> The station is very large, and the Marunouchi and Yaesu sides are about a 10-minute walk apart, according to Tokyo Station City. We did not find official walking times between gates and platforms, so add a buffer, especially with luggage.</li>
<li><strong>Lifts and toilets.</strong> We did not find an official list of lift and toilet locations in the pages we read. Follow the signs, or ask staff.</li>
<li><strong>Send your suitcase ahead.</strong> See the luggage section above.</li>
<li><strong>Visitor hotline.</strong> The Japan Visitor Hotline, 050-3816-2787, is open 24 hours and helps in English, Chinese and Korean. In an emergency, call 119.</li>
</ul>
<p class="ps-note">Sources: <a href="https://www.tokyostationcity.com/en/" target="_blank" rel="noopener noreferrer">Tokyo Station City</a>, <a href="https://www.jreast.co.jp/en/" target="_blank" rel="noopener noreferrer">JR East</a> and <a href="https://www.japan.travel/en/" target="_blank" rel="noopener noreferrer">JNTO</a>, checked 19 November 2026.</p>"""

ABOUT = """<div class="ps-about" id="about-this-guide">
<h2>About this guide</h2>
<p>Written by PackSmart. Station details were checked against Tokyo Station City, JR East and JR Central pages, First Avenue Tokyo Station, Tokyo Disney Resort, Tokyo Monorail, the Tokyo Station Hotel and the Japan National Tourism Organization (JNTO) on 19 November 2026. We give fares only where we read them on an official page, so most fares are left out and point to the operator's own fare tool. Where official pages disagree, for example on the opening hours of the JR East Travel Service Center, we say so instead of picking one. Spotted something out of date? <a href="/contact">Tell us</a> and we will fix it.</p>
<ul>
<li><strong>19 Nov 2026:</strong> first version, with the which-side chooser, the diagram, Shinkansen and Narita Express platforms, local trains, Metro and Disney, IC cards, lockers and luggage, food, the find-it tool and help.</li>
</ul>
</div>"""
def _card(title, text, slug, tag):
    return ('        <div class="related-card">\n            <div class="related-card-body">\n                <h4>%s</h4>\n                <p>%s</p>\n'
            '                <a href="https://www.packsmartapp.com%s">Read More <span class="related-arrow">&rarr;</span></a>\n                <div class="related-tag">%s</div>\n            </div>\n        </div>\n') % (title, text, slug, tag)

RELATED = ('<div class="related-posts">\n    <h3>Related Guides</h3>\n    <div class="related-grid">\n'
    + _card("Japan Travel and Packing Guide 2026", "What to pack, rail passes, etiquette and a budget breakdown for Tokyo, Kyoto and Osaka.", "/blog/japan-travel-packing-guide", "Destination Guide")
    + _card("Narita Airport Guide 2026", "Landing at Narita? Terminals, arrival steps, SIM and the trains and buses into Tokyo.", "/blog/narita-airport-guide", "Airport Guide")
    + _card("Haneda Airport Guide 2026", "Terminals, arrival steps and the quickest ways into central Tokyo.", "/blog/haneda-airport-guide", "Airport Guide")
    + '    </div>\n</div>')
# hero image (optional): save the photo as public/images/tokyo-station-hero.jpg (any of jpg/jpeg/png/webp), then run this script
def prepare_hero():
    imgdir = os.path.join(ROOT, "public", "images")
    src = None
    for ext in ("jpg", "jpeg", "png", "webp"):
        cand = os.path.join(imgdir, "tokyo-station-hero." + ext)
        if os.path.isfile(cand):
            src = cand
            break
    if not src:
        return None, None
    dst = os.path.join(imgdir, "tokyo-station-hero-1600.jpg")
    note = None
    if (not os.path.isfile(dst)) or os.path.getmtime(dst) < os.path.getmtime(src):
        import subprocess, shutil
        try:
            subprocess.run(["sips", "-Z", "1600", "-s", "format", "jpeg", "-s", "formatOptions", "72", src, "--out", dst],
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            note = "tokyo-station-hero-1600.jpg (optimised from your photo)"
        except Exception:
            if src.lower().endswith(".jpg"):
                return "/images/" + os.path.basename(src), "using the original photo (could not optimise it here)"
            return None, None
    return "/images/tokyo-station-hero-1600.jpg", note

HERO_URL, HERO_NOTE = prepare_hero()

CARD = """<div class="ps-card" id="one-page">
<h2>Tokyo Station on one page</h2>
<ul>
<li><strong>Two sides:</strong> the Marunouchi side (west) has the red-brick building, the Narita Express route and the JR East Travel Service Center. The Yaesu side (east) is the one Tokyo Station City recommends for bullet trains, and has the airport buses and First Avenue.</li>
<li><strong>Between the sides:</strong> the central passage on the 1st floor. Allow about 10 minutes (Tokyo Station City).</li>
<li><strong>Shinkansen platforms:</strong> 14 to 19 for the Tokaido and Sanyo lines (Nagoya, Kyoto, Osaka, Hiroshima), 20 to 23 for the Tohoku, Joetsu and Hokuriku lines. Check the board inside the blue ticket gates.</li>
<li><strong>Narita Express:</strong> from the Marunouchi Central Gate, down to B1, B4, then B5. Usually platform 3 or 4. All seats reserved, about an hour to Narita. Check the board.</li>
<li><strong>Local trains:</strong> several lines share platform numbers 1 to 4. Look for the line name as well as the number.</li>
<li><strong>Metro:</strong> the Marunouchi Line has its own station, M17.</li>
<li><strong>Luggage:</strong> coin lockers around the station, and day storage at the JR East Travel Service Center (left after the Marunouchi North ticket gate).</li>
<li><strong>Need help?</strong> Ask station staff or a JR East Information Center. In an emergency, call 119.</li>
</ul>
<div class="ps-qr ps-qr-screen">__QR_SCREEN__<p><strong>Want it on your phone?</strong> Point your phone camera at this code. It opens the free Tokyo Station Pocket Guide, which works without internet once opened.<span class="u">packsmartapp.com/tokyo-pocket</span></p></div>
<div class="ps-qr ps-qr-print">__QR_PRINT__<p><strong>Free Tokyo Station Pocket Guide.</strong> Point your phone camera at this code. Open it once with signal and it works without internet.<span class="u">packsmartapp.com/tokyo-pocket</span></p></div>
<button type="button" class="ps-print-btn" onclick="window.print()">Print this card</button>
</div>"""
# QR codes are made once for each guide address (?src=qr on screen, ?src=card on paper), with segno. For another guide ask Claude to make the two codes.
QR_SCREEN = '<svg shape-rendering="crispEdges" viewBox="0 0 41 41" class="segno"><title>QR code: open the Tokyo Station Pocket Guide</title><path fill="#fff" d="M0 0h41v41h-41z"/><path class="qrline" stroke="#000" d="M4 4.5h7m1 0h3m2 0h1m1 0h2m1 0h1m4 0h1m2 0h7m-33 1h1m5 0h1m2 0h3m1 0h2m1 0h1m1 0h4m2 0h1m1 0h1m5 0h1m-33 1h1m1 0h3m1 0h1m5 0h1m1 0h1m2 0h2m1 0h2m1 0h1m2 0h1m1 0h3m1 0h1m-33 1h1m1 0h3m1 0h1m1 0h1m3 0h1m3 0h2m4 0h2m2 0h1m1 0h3m1 0h1m-33 1h1m1 0h3m1 0h1m1 0h1m4 0h1m2 0h1m2 0h1m2 0h2m2 0h1m1 0h3m1 0h1m-33 1h1m5 0h1m1 0h3m2 0h1m1 0h1m2 0h1m1 0h1m3 0h1m1 0h1m5 0h1m-33 1h7m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h7m-25 1h1m2 0h1m5 0h5m-22 1h1m3 0h1m1 0h5m1 0h1m2 0h1m1 0h1m3 0h2m2 0h5m2 0h1m-31 1h2m5 0h2m1 0h1m1 0h2m1 0h1m3 0h1m1 0h1m1 0h1m3 0h3m-32 1h1m2 0h1m1 0h2m3 0h1m2 0h3m2 0h1m2 0h1m1 0h1m2 0h1m2 0h1m1 0h1m-30 1h1m1 0h1m2 0h2m4 0h1m1 0h1m3 0h1m1 0h1m2 0h3m4 0h1m-31 1h2m1 0h1m1 0h4m3 0h1m1 0h2m2 0h1m1 0h3m2 0h1m1 0h2m1 0h1m-30 1h1m1 0h2m3 0h1m1 0h4m3 0h3m1 0h2m1 0h1m1 0h1m1 0h1m-28 1h5m2 0h7m1 0h1m2 0h1m1 0h5m3 0h2m-32 1h2m1 0h3m2 0h2m2 0h2m1 0h3m3 0h1m3 0h5m-30 1h1m2 0h1m1 0h2m1 0h1m2 0h1m2 0h1m2 0h1m1 0h1m1 0h2m1 0h1m1 0h1m1 0h1m2 0h1m-32 1h3m1 0h2m1 0h1m1 0h1m1 0h1m2 0h3m6 0h2m4 0h2m-30 1h2m3 0h1m2 0h4m1 0h2m1 0h1m2 0h6m1 0h1m1 0h1m1 0h1m-32 1h3m1 0h2m4 0h2m1 0h2m2 0h2m2 0h1m2 0h2m1 0h1m3 0h2m-33 1h3m1 0h3m1 0h3m1 0h2m1 0h1m2 0h5m3 0h1m1 0h2m1 0h1m-32 1h2m1 0h1m1 0h1m4 0h1m1 0h2m2 0h1m2 0h1m1 0h3m3 0h1m1 0h1m1 0h1m-30 1h3m1 0h4m2 0h1m1 0h1m1 0h2m1 0h1m2 0h4m5 0h1m-29 1h1m1 0h1m2 0h2m7 0h1m1 0h3m2 0h3m-27 1h8m4 0h4m1 0h2m1 0h10m1 0h2m-25 1h1m2 0h2m1 0h5m3 0h3m3 0h1m1 0h2m-32 1h7m1 0h4m1 0h1m1 0h1m2 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h2m1 0h1m-32 1h1m5 0h1m3 0h1m1 0h2m2 0h1m3 0h3m1 0h1m3 0h1m2 0h2m-33 1h1m1 0h3m1 0h1m1 0h2m6 0h1m3 0h1m3 0h6m-30 1h1m1 0h3m1 0h1m2 0h4m1 0h1m2 0h4m2 0h1m2 0h3m1 0h1m-31 1h1m1 0h3m1 0h1m2 0h1m1 0h2m1 0h2m2 0h1m3 0h1m2 0h5m-30 1h1m5 0h1m4 0h1m2 0h4m3 0h1m2 0h2m-26 1h7m1 0h2m2 0h1m1 0h1m2 0h1m1 0h4m1 0h3m5 0h1"/></svg>'
QR_PRINT = '<svg shape-rendering="crispEdges" viewBox="0 0 41 41" class="segno"><title>QR code: open the Tokyo Station Pocket Guide</title><path fill="#fff" d="M0 0h41v41h-41z"/><path class="qrline" stroke="#000" d="M4 4.5h7m1 0h1m1 0h4m1 0h2m1 0h1m4 0h1m2 0h7m-33 1h1m5 0h1m4 0h1m1 0h2m1 0h1m1 0h4m2 0h1m1 0h1m5 0h1m-33 1h1m1 0h3m1 0h1m2 0h1m2 0h1m1 0h1m2 0h2m1 0h2m1 0h1m2 0h1m1 0h3m1 0h1m-33 1h1m1 0h3m1 0h1m1 0h1m1 0h1m5 0h2m4 0h2m2 0h1m1 0h3m1 0h1m-33 1h1m1 0h3m1 0h1m1 0h3m2 0h1m2 0h1m2 0h1m2 0h2m2 0h1m1 0h3m1 0h1m-33 1h1m5 0h1m1 0h2m3 0h1m1 0h1m2 0h1m1 0h1m3 0h1m1 0h1m5 0h1m-33 1h7m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h7m-25 1h1m1 0h1m6 0h5m-22 1h1m3 0h1m1 0h7m2 0h1m1 0h1m3 0h2m2 0h5m2 0h1m-31 1h1m2 0h1m1 0h3m4 0h2m1 0h1m3 0h1m1 0h1m1 0h1m3 0h3m-31 1h1m3 0h2m2 0h1m2 0h4m2 0h1m2 0h1m1 0h1m2 0h1m2 0h1m1 0h1m-32 1h1m1 0h1m1 0h2m2 0h1m4 0h1m1 0h1m3 0h1m1 0h1m2 0h3m4 0h1m-31 1h1m1 0h1m2 0h1m1 0h2m1 0h1m1 0h1m1 0h2m2 0h5m2 0h1m1 0h2m1 0h1m-29 1h2m2 0h1m3 0h2m1 0h1m3 0h3m2 0h1m1 0h1m1 0h1m1 0h1m-30 1h4m2 0h1m1 0h3m2 0h1m1 0h1m1 0h1m4 0h5m3 0h2m-29 1h3m1 0h2m1 0h8m3 0h1m3 0h5m-30 1h2m2 0h5m4 0h1m3 0h1m1 0h1m1 0h2m1 0h1m1 0h1m1 0h1m2 0h1m-31 1h1m1 0h1m3 0h2m1 0h3m2 0h2m6 0h2m4 0h2m-30 1h2m1 0h3m1 0h1m1 0h2m3 0h1m1 0h1m2 0h1m1 0h4m1 0h1m1 0h1m1 0h1m-29 1h2m2 0h2m3 0h3m2 0h2m2 0h1m2 0h2m1 0h1m3 0h2m-33 1h2m2 0h4m1 0h1m5 0h1m2 0h5m3 0h1m1 0h2m1 0h1m-32 1h6m3 0h1m2 0h3m1 0h1m2 0h3m1 0h1m3 0h1m1 0h1m1 0h1m-28 1h1m1 0h4m4 0h1m1 0h2m4 0h4m5 0h1m-30 1h4m1 0h3m1 0h1m2 0h1m2 0h1m2 0h2m2 0h3m5 0h1m-33 1h3m2 0h7m2 0h2m1 0h13m1 0h2m-25 1h2m4 0h5m3 0h3m3 0h1m1 0h2m-32 1h7m1 0h1m2 0h1m1 0h3m2 0h1m1 0h3m1 0h1m1 0h1m1 0h2m1 0h1m-32 1h1m5 0h1m3 0h3m3 0h1m3 0h2m2 0h1m3 0h1m2 0h2m-33 1h1m1 0h3m1 0h1m1 0h1m1 0h1m1 0h1m3 0h1m3 0h3m1 0h6m-30 1h1m1 0h3m1 0h1m3 0h2m1 0h1m3 0h2m3 0h2m2 0h3m1 0h1m-31 1h1m1 0h3m1 0h1m3 0h1m1 0h4m2 0h1m3 0h1m2 0h5m-30 1h1m5 0h1m2 0h1m1 0h2m2 0h3m1 0h1m1 0h1m2 0h2m-26 1h7m1 0h1m1 0h1m3 0h1m2 0h1m1 0h4m1 0h3m5 0h1"/></svg>'
CARD = CARD.replace("__QR_SCREEN__", QR_SCREEN).replace("__QR_PRINT__", QR_PRINT)

WHICH = """<h2 id="which-side">Which side: Marunouchi or Yaesu?</h2>
<p>Tokyo Station is one huge building with two main sides, joined by a central passage on the 1st floor. The <strong>Marunouchi side</strong> is to the west, and it is the one with the red-brick station building. The <strong>Yaesu side</strong> is to the east. Tokyo Station City tells people using Smart EX bullet train tickets to use the Yaesu side, and says the Marunouchi side is about a 10-minute walk from it.</p>
<p>Both sides have a North, a Central and a South gate, so a name like &ldquo;North Exit&rdquo; means two different places. Say which side as well, and follow the signs for the place you want.</p>
""" + CHOOSER + """
<p class="ps-note">Sources: <a href="https://www.tokyostationcity.com/en/" target="_blank" rel="noopener noreferrer">Tokyo Station City</a>, <a href="https://www.jreast.co.jp/en/" target="_blank" rel="noopener noreferrer">JR East</a>, <a href="https://www.japan.travel/en/" target="_blank" rel="noopener noreferrer">JNTO</a>, <a href="https://www.tokyoeki-1bangai.co.jp/en/" target="_blank" rel="noopener noreferrer">First Avenue Tokyo Station</a> and <a href="https://www.tokyostationhotel.jp/en/" target="_blank" rel="noopener noreferrer">Tokyo Station Hotel</a>. Checked 19 November 2026. Station layouts change, so follow the signs.</p>"""

CONNECTED = """<h2 id="connected">Getting online: eSIM and Wi-Fi</h2>
<p>You will want a connection for maps, messages and your hotel. Here are the usual choices.</p>
<div class="ps-scroll">
<table class="checklist-table">
<thead><tr><th>Option</th><th>How it works</th><th>Good to know</th></tr></thead>
<tbody>
<tr><td><strong>eSIM</strong></td><td>Install it on your phone. It works as soon as you switch it on.</td><td>Needs an eSIM-ready, unlocked phone. No counter or queue.</td></tr>
<tr><td><strong>Free station Wi-Fi</strong></td><td>JR East lists free Wi-Fi at the Travel Service Center.</td><td>We did not find an official list of other free Wi-Fi spots in the station. Fine for a quick message, not for a day of maps.</td></tr>
<tr><td><strong>SIM or Wi-Fi rental</strong></td><td>Counters and vending machines.</td><td>We did not find an official list of rental counters at Tokyo Station, so we do not name one. The airports have them.</td></tr>
</tbody>
</table>
</div>
<p>If you are flying in, see our <a href="/blog/narita-airport-guide">Narita Airport guide</a> and <a href="/blog/haneda-airport-guide">Haneda Airport guide</a> for SIM counters and vending machines.</p>
<p class="ps-note">Sources: <a href="https://www.jreast.co.jp/en/" target="_blank" rel="noopener noreferrer">JR East</a>. Checked 19 November 2026.</p>"""
JB_LINK = "https://www.japan-bullettrain.com/?via=packsmart"
JB_SHIN = '<svg style="display:block;width:100%;height:auto;" aria-hidden="true" focusable="false" viewBox="0 0 320 170" xmlns="http://www.w3.org/2000/svg"><rect width="320" height="170" fill="#E8F1FE"/><circle cx="64" cy="40" r="20" fill="#FFE3CC"/><path d="M120 120 L188 44 L204 60 L214 52 L282 120Z" fill="#b9cdf0"/><path d="M174 62 L188 44 L204 60 L196 64 L188 58 L181 66Z" fill="#fff"/><path d="M0 124 L60 96 L110 120 L150 104 L200 124Z" fill="#d3e0f7"/><g fill="#f7b9cf"><circle cx="262" cy="104" r="14"/><circle cx="276" cy="112" r="12"/><circle cx="250" cy="114" r="11"/></g><rect x="260" y="112" width="4" height="22" fill="#8b5a3c"/><rect y="132" width="320" height="38" fill="#d3e0f7"/><rect y="146" width="320" height="4" fill="#9db8e6"/><g><path d="M14 138 L14 110 C14 104 20 100 28 100 L214 100 C250 100 286 118 306 138 Z" fill="#fff" stroke="#0f0f23" stroke-width="2.5"/><path d="M14 124 L300 124 L304 130 L14 130Z" fill="#2563EB"/><g fill="#7fb4f5" stroke="#0f0f23" stroke-width="1.5"><rect x="34" y="106" width="20" height="11" rx="2"/><rect x="62" y="106" width="20" height="11" rx="2"/><rect x="90" y="106" width="20" height="11" rx="2"/><rect x="118" y="106" width="20" height="11" rx="2"/><rect x="146" y="106" width="20" height="11" rx="2"/><rect x="174" y="106" width="20" height="11" rx="2"/></g><path d="M214 101 C238 102 262 112 282 124 L214 124Z" fill="#0f0f23" opacity=".9"/><g fill="#0f0f23"><circle cx="60" cy="140" r="5"/><circle cx="104" cy="140" r="5"/><circle cx="200" cy="140" r="5"/><circle cx="244" cy="140" r="5"/></g></g><g stroke="#2563EB" stroke-width="3" stroke-linecap="round"><path d="M4 108h22"/><path d="M0 118h16"/><path d="M6 128h12"/></g></svg>'
JB_TRAIN = '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M5 16V8a5 5 0 0 1 5-5h4a5 5 0 0 1 5 5v8a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2z"/><path d="M5 11h14M9 15h.01M15 15h.01M8 18l-2 3M16 18l2 3"/></svg>'


def jb_node(text):
    return '<div class="jb-rn"><span class="jb-dot"></span><strong style="color:#0f0f23;font-size:1rem;">%s</strong></div>' % text


def jb_leg(text, icon="", blue=False):
    return '<div class="jb-lg%s"><span class="jb-ln"></span><span class="jb-lt">%s%s</span></div>' % (" jb-blue" if blue else "", icon, text)


JB_SHINKANSEN = (
    '<div data-ps-placement="jw-shinkansen-tokyo" style="max-width:800px;margin:20px auto;padding:20px;background:#f0faf7;border:1px solid #cdeee5;border-left:4px solid #00C9A7;border-radius:12px;">'
    '<style>.ps-jb-ghost{transition:background .15s,box-shadow .15s}.ps-jb-btn:hover .ps-jb-ghost,.ps-jb-btn:focus-visible .ps-jb-ghost{background:#E7FAF5!important;box-shadow:0 2px 10px rgba(0,201,167,.25)}'
    '.jb-grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:22px;align-items:center;margin:0 0 16px}'
    '.jb-row{display:flex;gap:22px;align-items:center}.jb-row .jb-tx{flex:1 1 0;min-width:0}.jb-row{align-items:flex-start}.jb-row .jb-bt{flex:0 0 280px}'
    '@media(max-width:640px){.jb-grid{grid-template-columns:1fr;gap:14px}.jb-row{flex-direction:column;align-items:stretch;gap:12px}.jb-row .jb-bt{flex:none}}'
    '.jb-rn{display:flex;gap:10px;align-items:center;padding:2px 0}'
    '.jb-dot{width:14px;height:14px;border-radius:50%;background:#00C9A7;border:3px solid #fff;box-shadow:0 0 0 2px #00C9A7;flex:none;margin:0 2px}'
    '.jb-lg{display:flex;gap:14px;align-items:stretch;padding:3px 0 3px 8px}'
    '.jb-ln{width:4px;height:30px;border-radius:2px;flex:none;background:repeating-linear-gradient(180deg,#00C9A7 0 8px,transparent 8px 13px)}'
    '.jb-blue .jb-ln{background:repeating-linear-gradient(180deg,#2563EB 0 8px,transparent 8px 13px)}'
    '.jb-lt{display:flex;align-items:center;gap:6px;align-self:center;font-size:.85rem;font-weight:700;color:#0a8f78;line-height:1.25}'
    '.jb-blue .jb-lt{color:#2563EB}</style>'
    '<strong style="display:block;font-size:1.1rem;color:#0f0f23;margin:0 0 12px;">Going on by bullet train?</strong>'
    '<div class="jb-grid">'
    '<a href="' + JB_LINK + '" target="_blank" rel="nofollow noopener sponsored" tabindex="-1" aria-hidden="true" style="display:block;border-radius:12px;overflow:hidden;">' + JB_SHIN + '</a>'
    '<div>'
    + jb_node("Tokyo Station") + jb_leg("Shinkansen (bullet train)", JB_TRAIN, True) + jb_node("Kyoto") + jb_node("Osaka") +
    '</div></div>'
    '<div class="jb-row"><div class="jb-tx">'
    '<p style="margin:0 0 8px;font-size:0.95rem;line-height:1.5;color:#333;">Shinkansen from Tokyo Station run west to Nagoya, Kyoto and Shin-Osaka. If you want your tickets sorted before you travel, you can book them online. The company says its tickets cover the JR East, JR West, JR Central and JR Kyushu Shinkansen lines and are collected with a QR code.</p>'
    '</div><div class="jb-bt">'
    '<a class="ps-jb-btn" href="' + JB_LINK + '" target="_blank" rel="nofollow noopener sponsored" style="display:block;box-sizing:border-box;text-decoration:none;"><span class="ps-jb-ghost" style="display:block;border:1.5px solid #00C9A7;background:#fff;color:#0a8f78;text-align:center;font-weight:700;font-size:1rem;border-radius:12px;padding:11px 14px;min-height:46px;line-height:1.25;">Book Shinkansen tickets &rarr;</span><span style="display:block;text-align:center;font-size:0.76rem;color:#777;margin-top:6px;">Japan Bullet Train &middot; partner link</span></a>'
    '<p style="margin:10px 0 0;font-size:0.85rem;line-height:1.5;color:#555;">You can also buy at a station on the day, so check the price and the change and cancellation rules before you pay.</p>'
    '</div></div></div>'
)



# ---- Klook placements on the Tokyo Station page: links to be generated in Travelpayouts by Ari (aff_pid=711400, one Sub ID per placement).
# While a link is "" the matching partner line is not rendered at all.
KLK = {
    "klook-tokyo-station-shinkansen": "",
    "klook-tokyo-station-nex": "",
    "klook-tokyo-station-suica": "",
    "klook-tokyo-station-disney": "",
    "klook-tokyo-station-limousine": "",
    "klook-tokyo-station-luggage": "",
}


def klp(key, text):
    link = KLK.get(key, "")
    if not link:
        return ""
    return ('<p data-ps-placement="%s">%s, a partner link. Check the listing for the current price and terms: '
            '<a href="%s" target="_blank" rel="nofollow noopener sponsored">see the listing</a>.</p>' % (key, text, link))
KL_BUS = '<svg aria-hidden="true" focusable="false" style="display:block;width:100%;height:auto;" viewBox="0 0 320 150" xmlns="http://www.w3.org/2000/svg"><rect width="320" height="150" fill="#FFF1E2"/><g fill="#fbd9b6"><rect x="14" y="40" width="40" height="74"/><rect x="60" y="62" width="28" height="52"/><rect x="236" y="34" width="44" height="80"/><rect x="284" y="64" width="26" height="50"/></g><g fill="#fff3e6"><rect x="22" y="50" width="8" height="8"/><rect x="38" y="50" width="8" height="8"/><rect x="22" y="66" width="8" height="8"/><rect x="38" y="66" width="8" height="8"/><rect x="246" y="46" width="8" height="8"/><rect x="262" y="46" width="8" height="8"/><rect x="246" y="62" width="8" height="8"/><rect x="262" y="62" width="8" height="8"/></g><rect y="116" width="320" height="34" fill="#efd3b3"/><rect y="132" width="320" height="3" fill="#fff" opacity=".6"/><g><rect x="52" y="64" width="216" height="56" rx="10" fill="#fff" stroke="#0f0f23" stroke-width="2.5"/><rect x="52" y="104" width="216" height="8" fill="#F97316"/><g fill="#9ad8e8" stroke="#0f0f23" stroke-width="1.5"><rect x="64" y="72" width="26" height="22" rx="3"/><rect x="96" y="72" width="26" height="22" rx="3"/><rect x="128" y="72" width="26" height="22" rx="3"/><rect x="160" y="72" width="26" height="22" rx="3"/><rect x="192" y="72" width="26" height="22" rx="3"/><rect x="228" y="72" width="30" height="30" rx="3"/></g><circle cx="94" cy="122" r="11" fill="#0f0f23"/><circle cx="94" cy="122" r="4" fill="#bbb"/><circle cx="226" cy="122" r="11" fill="#0f0f23"/><circle cx="226" cy="122" r="4" fill="#bbb"/></g></svg>'
KL_CAR = '<svg aria-hidden="true" focusable="false" style="display:block;width:100%;height:auto;" viewBox="0 0 320 150" xmlns="http://www.w3.org/2000/svg"><rect width="320" height="150" fill="#E7FAF5"/><g fill="#cdeee5"><rect x="18" y="52" width="30" height="62"/><rect x="54" y="68" width="24" height="46"/><rect x="240" y="44" width="34" height="70"/><rect x="280" y="66" width="28" height="48"/></g><rect y="116" width="320" height="34" fill="#d6f1ea"/><rect y="132" width="320" height="3" fill="#fff" opacity=".7"/><g><path d="M56 112 L56 98 C56 92 60 88 66 86 L108 70 C116 66 124 64 134 64 L190 64 C200 64 208 68 216 74 L246 88 C256 90 262 96 262 104 L262 112 Z" fill="#fff" stroke="#0f0f23" stroke-width="2.5" stroke-linejoin="round"/><path d="M116 72 L134 68 L160 68 L160 88 L104 88 Z" fill="#9ad8e8" stroke="#0f0f23" stroke-width="1.5" stroke-linejoin="round"/><path d="M168 68 L190 68 C196 68 202 71 208 76 L220 88 L168 88 Z" fill="#9ad8e8" stroke="#0f0f23" stroke-width="1.5" stroke-linejoin="round"/><rect x="56" y="100" width="206" height="6" fill="#00C9A7"/><circle cx="96" cy="114" r="12" fill="#0f0f23"/><circle cx="96" cy="114" r="4.5" fill="#bbb"/><circle cx="224" cy="114" r="12" fill="#0f0f23"/><circle cx="224" cy="114" r="4.5" fill="#bbb"/></g></svg>'
KL_LBL = "display:block;font-weight:700;color:#0a8f78;font-size:0.76rem;letter-spacing:.03em;text-transform:uppercase;"
KL_VAL = "display:block;font-size:0.92rem;line-height:1.35;color:#0f0f23;"
KL_BAGS_LINK = ""
KL_TRAIN = ""
KL_ROWS = []
def kl_row(label, text):
    return '<div style="margin:0 0 7px;"><span style="%s">%s</span><span style="%s">%s</span></div>' % (KL_LBL, label, KL_VAL, text)
def kl_tile(r):
    pid, name, to, mins, price, note, link, btn, svg = r
    return (
        '<a class="ps-kl-tile" data-ps-placement="klook-tokyo-station-transport-%s" href="%s" target="_blank" rel="nofollow noopener sponsored" style="display:flex;flex-direction:column;background:#fff;border:1.5px solid #cdeee5;border-radius:12px;padding:12px 12px 14px;text-decoration:none;color:#0f0f23;">' % (pid, link)
        + '<span style="display:block;margin:0 0 10px;border-radius:12px;overflow:hidden;">%s</span>' % svg
        + '<strong style="display:block;font-size:1.1rem;color:#0f0f23;margin:0 0 8px;">%s</strong>' % name
        + kl_row("Goes to", to) + kl_row("About how long", mins) + kl_row("About how much", price)
        + '<p style="margin:0 0 12px;font-size:0.88rem;color:#555;line-height:1.4;">%s</p><span style="flex:1;min-height:4px;display:block;"></span>' % note
        + '<span class="ps-kl-ghost" style="display:block;box-sizing:border-box;border:1.5px solid #00C9A7;color:#0a8f78;text-align:center;font-weight:700;font-size:0.98rem;border-radius:12px;padding:10px 12px;min-height:46px;line-height:1.25;display:flex;align-items:center;justify-content:center;">%s&nbsp;&rarr;</span><span style="display:block;text-align:center;font-size:0.76rem;color:#777;margin-top:6px;">Klook &middot; partner link</span></a>' % btn.replace(" ", "&nbsp;", btn.count(" ") - 1)
    )


KLOOK_TRANSPORT = ""
SHINKANSEN = """<h2 id="shinkansen">Bullet trains at Tokyo Station</h2>
<p>Tokyo Station City lists two groups of Shinkansen platforms. Your ticket and the departure boards show your platform, and platforms can change, so check before you walk up.</p>
<div class="ps-scroll">
<table class="checklist-table">
<thead><tr><th>Platforms</th><th>Lines</th><th>Run by</th><th>Goes toward</th></tr></thead>
<tbody>
<tr><td><strong>14 to 19</strong></td><td>Tokaido and Sanyo Shinkansen</td><td>JR Central</td><td>Nagoya, Kyoto, Shin-Osaka, Hiroshima, Hakata</td></tr>
<tr><td><strong>20 to 23</strong></td><td>Tohoku, Joetsu and Hokuriku Shinkansen</td><td>JR East</td><td>Sendai, Nagano, Echigo-Yuzawa, Kanazawa</td></tr>
</tbody>
</table>
</div>
<ul>
<li><strong>Finding the platform.</strong> Tokyo Station City's route: on the 1st floor, head toward the central information counter along the central passage, look for the blue ticket gates, then check the platform on the electronic board inside the gate. Wait at your car number.</li>
<li><strong>Which side.</strong> Tokyo Station City recommends the Yaesu side for Smart EX tickets and says the Marunouchi side is about a 10-minute walk away.</li>
<li><strong>Booking.</strong> JR East's reservation service cannot book the Tokaido and Sanyo Shinkansen, so use JR Central's Smart EX or a ticket office for Kyoto and Osaka. JR East says the JR TOKYO Wide Pass is not valid on the Tokaido Shinkansen.</li>
<li><strong>Reserved or not.</strong> Non-reserved tickets are valid on the day of purchase, but JR East says trains such as the Hayabusa and Hayate are all reserved. Check your train.</li>
<li><strong>Big suitcases.</strong> Over 160 cm (sum of three sides) up to 250 cm needs a seat with an oversized baggage area on the Tokaido and Sanyo lines. See the luggage section for the full table.</li>
<li><strong>Tokyo to Kyoto.</strong> About 130 minutes on the fastest trains (JR Central).</li>
</ul>
""" + JB_SHINKANSEN + klp("klook-tokyo-station-shinkansen", "Tokyo to Kyoto and Osaka bullet train tickets") + """
<p class="ps-note">Sources: <a href="https://www.tokyostationcity.com/en/" target="_blank" rel="noopener noreferrer">Tokyo Station City</a>, <a href="https://www.jreast.co.jp/en/" target="_blank" rel="noopener noreferrer">JR East</a> and <a href="https://global.jr-central.co.jp/en/" target="_blank" rel="noopener noreferrer">JR Central</a>. Checked 19 November 2026.</p>"""

NARITA = """<h2 id="narita">Narita Express and the airports</h2>
<p>The Narita Express (N&rsquo;EX) uses underground platforms. Tokyo Station City gives this route: from the Marunouchi Central Gate, go down to B1, then to B4, then to B5, and the N&rsquo;EX leaves from platforms 3 and 4.</p>
<ul>
<li><strong>Check the board.</strong> JR East's timetables also show some N&rsquo;EX trains on tracks 1 and 2, so treat 3 or 4 as the usual platforms and confirm on the departure board.</li>
<li><strong>Board the right train.</strong> Tokyo Station City says the Narita-bound platform also serves a regular rapid train, so make sure you board the N&rsquo;EX.</li>
<li><strong>Reserved seats.</strong> All N&rsquo;EX seats are reserved. JR East's timetables give roughly an hour between Narita Airport and Tokyo Station.</li>
<li><strong>Airport Limousine Bus.</strong> The bus company lists a stop at the Yaesu North Exit (Tekko Building) for both Haneda and Narita. We did not find a fare we could confirm, so we give none.</li>
<li><strong>Haneda by train.</strong> Take the JR Yamanote Line to Hamamatsucho, then the Tokyo Monorail. Tokyo Monorail says the express takes 13 minutes from Hamamatsucho to Terminal 3.</li>
</ul>
""" + klp("klook-tokyo-station-nex", "Narita Express tickets") + klp("klook-tokyo-station-limousine", "Airport Limousine Bus tickets") + """
<p>More detail: our <a href="/blog/narita-airport-guide">Narita Airport guide</a> and <a href="/blog/haneda-airport-guide">Haneda Airport guide</a>.</p>
<p class="ps-note">Sources: <a href="https://www.tokyostationcity.com/en/" target="_blank" rel="noopener noreferrer">Tokyo Station City</a>, <a href="https://www.jreast.co.jp/en/" target="_blank" rel="noopener noreferrer">JR East timetables</a>, <a href="https://www.tokyo-monorail.co.jp/english/" target="_blank" rel="noopener noreferrer">Tokyo Monorail</a> and the airport limousine bus operator's pages. Checked 19 November 2026. Times change, so check the operator.</p>"""

RAIL = """<h2 id="rail">Local trains, Metro and Disney</h2>
<p>JNTO and JR East list these lines at Tokyo Station: the Yamanote Line, the Chuo Rapid Line, the Keihin-Tohoku Line, the Sobu Rapid Line, the Yokosuka Line, the Keiyo and Musashino Lines and the Narita Express. Tokyo Station City says platforms 1 to 4 are shared by several of them, so check the line name as well as the number.</p>
<ul>
<li><strong>Yamanote Line.</strong> The loop line. It links Tokyo Station with Hamamatsucho, where you change for the monorail to Haneda.</li>
<li><strong>Tokyo Metro.</strong> The Marunouchi Line has its own station, M17. JNTO says long underground passages link Tokyo Station with Otemachi Station, where the Tozai, Chiyoda, Hanzomon and Toei Mita lines stop. It is a bit of a walk.</li>
<li><strong>Tokyo Disney Resort.</strong> Take the Keiyo or Musashino Line to Maihama Station, about 15 minutes according to Tokyo Disney Resort. Tokyo Disneyland is a short walk from the station. For Tokyo DisneySea, change at Resort Gateway Station to the Disney Resort Line. We did not find an official walking time from the Keiyo platform, so allow extra time.</li>
<li><strong>Mount Fuji and Kawaguchiko.</strong> JNTO's tourist information schedules list buses from Tokyo Station. We did not confirm times or fares.</li>
</ul>
""" + klp("klook-tokyo-station-disney", "Tokyo Disney Resort tickets") + """
<p class="ps-note">Sources: <a href="https://www.tokyostationcity.com/en/" target="_blank" rel="noopener noreferrer">Tokyo Station City</a>, <a href="https://www.japan.travel/en/" target="_blank" rel="noopener noreferrer">JNTO</a>, <a href="https://www.tokyo-disneyresort.jp/en/" target="_blank" rel="noopener noreferrer">Tokyo Disney Resort</a> and <a href="https://www.jreast.co.jp/en/" target="_blank" rel="noopener noreferrer">JR East</a>. Checked 19 November 2026. Times change, so check the operator.</p>"""

CARDS = """<h2 id="cards">Paying for trains: IC cards</h2>
<p>An IC card lets you tap in and out of most trains and buses in Japan without buying a ticket each time.</p>
<ul>
<li><strong>Welcome Suica.</strong> JR East says it lasts 28 days and needs no deposit. In principle one card is sold to each person. You load 1,000 to 10,000 yen when you buy it, and can top up with cash to 20,000 yen. JR East says it works on trains, buses and in shops across Japan, but not in stores in the PiTaPa area.</li>
<li><strong>Where to buy.</strong> The JR East Travel Service Center at Tokyo Station sells it (left after the Marunouchi North ticket gate). It is also sold at JAPAN RAIL CAFE TOKYO on the Yaesu side, and by machines at Narita and Haneda airports.</li>
<li><strong>Lockers.</strong> JR East says a Welcome Suica card can pay for a coin locker and unlock it.</li>
<li><strong>Tourist PASMO.</strong> JNTO also lists the TOURIST PASMO as a deposit-free card for visitors.</li>
<li><strong>Phone version.</strong> JR East also has Welcome Suica Mobile. Check JR East's page for which phones it supports.</li>
</ul>
""" + klp("klook-tokyo-station-suica", "Tokyo IC card listing") + """
<p class="ps-note">Sources: <a href="https://www.jreast.co.jp/en/" target="_blank" rel="noopener noreferrer">JR East</a> and <a href="https://www.japan.travel/en/" target="_blank" rel="noopener noreferrer">JNTO</a>. Checked 19 November 2026. Rules and prices change, so check before you buy.</p>"""

FOOD = """<h2 id="food">Eating in the station</h2>
<p>Hours are as printed by each operator and can change. Check before you plan a meal around them.</p>
<div class="ps-scroll">
<table class="checklist-table">
<thead><tr><th>Where</th><th>What</th><th>Hours</th></tr></thead>
<tbody>
<tr><td><strong>First Avenue Tokyo Station (Yaesu side, underground)</strong></td><td>Tokyo Ramen Street</td><td>10:30 am to 11 pm, last order 10:30 pm (a few shops open earlier)</td></tr>
<tr><td><strong>First Avenue Tokyo Station</strong></td><td>Tokyo Character Street</td><td>10 am to 8:30 pm</td></tr>
<tr><td><strong>First Avenue Tokyo Station</strong></td><td>Okashi Land (sweets)</td><td>9 am to 9 pm</td></tr>
<tr><td><strong>GRANSTA Tokyo (inside the gates)</strong></td><td>Ekibenya Matsuri, boxed meals</td><td>5:30 am to 10 pm</td></tr>
<tr><td><strong>GRANSTA Tokyo (inside the gates)</strong></td><td>Honnoriya, rice balls</td><td>6 am to 10 pm</td></tr>
<tr><td><strong>Outside the gates</strong></td><td>T's TanTan, vegan ramen</td><td>10 am to 10 pm</td></tr>
</tbody>
</table>
</div>
<p>You can reach Character Street by the stairs down at the Yaesu North Exit (JNTO). The Tokyo Station Hotel and Tokyo Station Gallery are on the Marunouchi side, if you want a quieter break: the gallery is open 10 am to 6 pm, until 8 pm on Fridays, and is generally closed on Mondays.</p>
<p class="ps-note">Sources: <a href="https://www.tokyoeki-1bangai.co.jp/en/" target="_blank" rel="noopener noreferrer">First Avenue Tokyo Station</a>, <a href="https://www.tokyostationcity.com/en/" target="_blank" rel="noopener noreferrer">Tokyo Station City</a> and <a href="https://www.japan.travel/en/" target="_blank" rel="noopener noreferrer">JNTO</a>. Checked 19 November 2026.</p>"""
POCKET_BAR = """<style>
#psPocketBar{display:none}
@media (max-width:820px){
#psPocketBar{position:fixed;left:0;right:0;bottom:0;z-index:90;display:flex;align-items:center;gap:10px;padding:10px 12px calc(10px + env(safe-area-inset-bottom));background:#1a1a3e;color:#fff;box-shadow:0 -6px 20px rgba(15,15,35,.25);transform:translateY(110%);transition:transform .25s ease-out;visibility:hidden}
#psPocketBar.on{transform:none;visibility:visible}
#psPocketBar .t{flex:1;min-width:0;line-height:1.25;font-size:15px}
#psPocketBar .t b{display:block;font-size:16px}
#psPocketBar .t span{color:#C9D1F0;font-size:13px}
#psPocketBar a.go{flex:none;background:#00C9A7;color:#0f0f23;font-weight:800;font-size:16px;text-decoration:none;border-radius:12px;padding:12px 16px;min-height:44px;display:flex;align-items:center}
#psPocketBar button.x{flex:none;background:none;border:0;color:#fff;font-size:26px;line-height:1;width:44px;height:44px;cursor:pointer;opacity:.8}
html.ps-pb body{padding-bottom:84px}
}
@media (prefers-reduced-motion:reduce){#psPocketBar{transition:none}}
@media print{#psPocketBar{display:none!important}}
</style>
<div id="psPocketBar" role="region" aria-label="Tokyo Station Pocket Guide">
<div class="t"><b>Get the Tokyo Station Pocket Guide</b><span>Free. Works offline at the station.</span></div>
<a class="go" href="/tokyo-pocket?src=bar">Get it</a>
<button type="button" class="x" aria-label="Hide this message">&times;</button>
</div>
<script>
(function(){
  var bar=document.getElementById('psPocketBar'); if(!bar) return;
  var KEY='psPocketBar', DAYS=30, shown=false;
  function ls(k,v){ try{ if(v===undefined) return localStorage.getItem(k); localStorage.setItem(k,v); }catch(e){} return null; }
  function ev(a){ try{ if(window.gtag) gtag('event','pocket_prompt',{event_category:'engagement',action:a,page_path:location.pathname}); }catch(e){} }
  var mq=window.matchMedia&&window.matchMedia('(max-width: 820px)');
  if(!mq||!mq.matches) return;
  if(window.navigator.standalone) return;
  var last=parseInt(ls(KEY)||'0',10); if(last&&Date.now()-last<DAYS*864e5) return;
  var hold=document.getElementById('save-offline'), inView=false;
  function paint(){
    var want=(window.pageYOffset||document.documentElement.scrollTop)>500&&!inView;
    if(want&&!shown){ shown=true; ev('view'); }
    bar.classList.toggle('on',want);
    document.documentElement.classList.toggle('ps-pb',want);
  }
  if(hold&&'IntersectionObserver' in window){ new IntersectionObserver(function(en){ inView=en[0].isIntersecting; paint(); }).observe(hold); }
  window.addEventListener('scroll',paint,{passive:true}); paint();
  bar.querySelector('.go').addEventListener('click',function(){ ev('open'); ls(KEY,String(Date.now())); });
  bar.querySelector('.x').addEventListener('click',function(){ ev('dismiss'); ls(KEY,String(Date.now())); bar.classList.remove('on'); document.documentElement.classList.remove('ps-pb'); window.removeEventListener('scroll',paint); });
})();
</script>"""

SAVE_BOX = """<div class="ps-about" id="save-offline">
<h3 style="margin:0 0 6px;">Save the finder on your phone (works without internet)</h3>
<p>Open the Tokyo Station Pocket Guide once while you have signal, then add it to your home screen. At the station it opens like an app, even with no connection.</p>
<p><a class="ps-btn2" href="/tokyo-pocket?src=box" onclick="try{window.gtag&&gtag('event','pocket_prompt',{event_category:'engagement',action:'open_box',page_path:location.pathname});}catch(e){}" style="display:inline-block;text-decoration:none;">Open the Pocket Guide</a></p>
<ul>
<li><strong>iPhone:</strong> open it in Safari, tap the Share button, then "Add to Home Screen".</li>
<li><strong>Android:</strong> open it in Chrome, tap the menu (three dots), then "Add to Home screen" or "Install app".</li>
</ul>
</div>"""

FACILITIES = """<h2 id="facilities">Facilities in the station</h2>
<p>This table follows Tokyo Station City, JR East and the other pages listed in each section, checked on 19 November 2026. A dash means the pages we read do not list one. Hours are as printed on those pages and can change.</p>
<div class="ps-scroll">
<table class="checklist-table">
<thead><tr><th>Facility</th><th>What we found</th></tr></thead>
<tbody>
<tr><td><strong>Travel Service Center (JR East)</strong></td><td>Marunouchi side, on your left after the Marunouchi North ticket gate, 1F. Exchanges and sells passes and tickets, exchanges currency, keeps luggage for the day, has a prayer room (10 am to 5 pm) and free Wi-Fi. JR East and JNTO print different opening hours, so check JR East's page</td></tr>
<tr><td><strong>Information centres</strong></td><td>JR East Information Centers, 10 am to 6 pm, at the 1F central passage, the 1F Marunouchi Central Exit and the B1 Marunouchi Underground Central Exit (inside the gates). JAPAN RAIL CAFE TOKYO, Yaesu side, GRAN TOKYO North Tower 1F, 8 am to 9 pm</td></tr>
<tr><td><strong>Coin lockers</strong></td><td>Around the station. Tokyo Station City links to a locker search tool. No official fee list found</td></tr>
<tr><td><strong>Luggage storage</strong></td><td>JR East Travel Service Center, for the day only</td></tr>
<tr><td><strong>Toilets, lifts, nursing rooms</strong></td><td>-</td></tr>
<tr><td><strong>Tickets and rail passes</strong></td><td>Travel Service Center for passes and tickets. JR East says the Welcome Suica is sold there and at JAPAN RAIL CAFE</td></tr>
<tr><td><strong>Buses</strong></td><td>JR Highway Bus Terminal at the Yaesu South Exit. Tekko Building bus terminal, about 2 minutes from the Yaesu North Exit. Airport Limousine Bus from the Yaesu North Exit (Tekko Building)</td></tr>
<tr><td><strong>Shops and food</strong></td><td>First Avenue Tokyo Station (Yaesu side, underground) and GRANSTA Tokyo (inside the gates). See the food section</td></tr>
<tr><td><strong>Hotel</strong></td><td>Tokyo Station Hotel, in the red-brick building. Entrance on the ground floor, direct from the Marunouchi South Gate</td></tr>
<tr><td><strong>Gallery and gardens</strong></td><td>Tokyo Station Gallery, in front of the Marunouchi North Gate (10 am to 6 pm, Fridays to 8 pm, generally closed Mondays). The Imperial Palace East Gardens are a quick walk from the Marunouchi Central Exit, open from 9 am, with closing times that change by season, and are generally closed on Mondays and Fridays</td></tr>
</tbody>
</table>
</div>
<h3>If you need help</h3>
<p>If you are tired, unsure or carrying a lot, go straight to an information centre or a staff member instead of searching on your own.</p>
<p class="ps-note">Sources: <a href="https://www.tokyostationcity.com/en/" target="_blank" rel="noopener noreferrer">Tokyo Station City</a>, <a href="https://www.jreast.co.jp/en/" target="_blank" rel="noopener noreferrer">JR East</a>, <a href="https://www.japan.travel/en/" target="_blank" rel="noopener noreferrer">JNTO</a>, <a href="https://www.tokyostationhotel.jp/en/" target="_blank" rel="noopener noreferrer">Tokyo Station Hotel</a> and <a href="https://www.tokyoeki-1bangai.co.jp/en/" target="_blank" rel="noopener noreferrer">First Avenue Tokyo Station</a>. Checked 19 November 2026. Opening hours can change.</p>"""

LEAVING = """<h2 id="leaving">Leaving Tokyo by train or bus</h2>
<ul>
<li><strong>Know your side.</strong> Bullet trains, the airport limousine buses and highway buses are on the Yaesu side. The Narita Express route starts on the Marunouchi side.</li>
<li><strong>To Narita Airport.</strong> The Narita Express takes about an hour (JR East's timetables), and all seats are reserved. The Airport Limousine Bus leaves from the Yaesu North Exit (Tekko Building). See our <a href="/blog/narita-airport-guide">Narita Airport guide</a>.</li>
<li><strong>To Haneda Airport.</strong> The Yamanote Line to Hamamatsucho, then the Tokyo Monorail, which takes 13 minutes on the express to Terminal 3 (Tokyo Monorail). Or the Airport Limousine Bus from the Yaesu North Exit. See our <a href="/blog/haneda-airport-guide">Haneda Airport guide</a>.</li>
<li><strong>To Kyoto and Osaka.</strong> Tokaido Shinkansen from platforms 14 to 19. About 130 minutes to Kyoto on the fastest trains (JR Central). See our <a href="/blog/kyoto-station-guide">Kyoto Station guide</a> and <a href="/blog/osaka-station-guide">Osaka station guide</a>.</li>
<li><strong>To Tokyo Disney Resort.</strong> Keiyo or Musashino Line to Maihama, about 15 minutes (Tokyo Disney Resort).</li>
<li><strong>Allow time for the station itself.</strong> Tokyo Station is huge, and the two sides are about a 10-minute walk apart. We did not find official walking times between gates and platforms, so add a buffer, especially with luggage.</li>
<li><strong>Last trains.</strong> We did not confirm last-train times, so check the timetable for your route before a late evening journey.</li>
<li><strong>Taking a Shinkansen?</strong> Check your platform on the departure board, and your train name against your pass.</li>
</ul>"""
AFFILIATE_P = ('<p style="font-size:0.82rem;color:#999;margin-bottom:0.5rem;padding-bottom:0.8rem;border-bottom:1px solid #eee;">'
               'This article contains affiliate links. If you make a purchase through these links, we may earn a small commission at no extra cost to you. '
               '<a href="/affiliate-disclosure" style="color:#00C9A7;">Learn more</a>.</p>')
# take the exact affiliate disclosure paragraph from the template if present
for l in t:
    if l.startswith('<p style="font-size:0.82rem;color:#999;margin-bottom:0.5rem') and "affiliate links" in l:
        AFFILIATE_P = l
        break

# share row, adapted from the template
sr_start = next(i for i, l in enumerate(t) if 'class="share-row"' in l)
sr_end = next(i for i in range(sr_start, len(t)) if t[i].strip() == "</div>")
share = "\n".join(t[sr_start:sr_end + 1])
enc_title = quote(H1, safe="")
old_title_enc = quote("Japan Travel & Packing Guide 2026: Tokyo, Kyoto, Osaka & Beyond", safe="")
# template uses a lighter encoding in places; normalise with regexes on the text= / description= params
share = share.replace("japan-travel-packing-guide", SLUG)
share = re.sub(r"text=[^&\"']*?(?=(%20https|&url|\"))", "text=" + enc_title, share)
share = re.sub(r"media=[^&\"']*", "media=" + quote(SITE + "/og-default.png", safe=""), share)
share = re.sub(r"description=[^\"']*", "description=" + enc_title, share)

BODY = "\n\n".join([
    '<p style="font-size:0.85rem;color:#666;margin:0 0 0.6rem;">Published November 19, 2026 · Last updated November 2026 · Facts checked 19 Nov 2026</p>',
    AFFILIATE_P,
    share,
    PRINT_CSS,
    '<p>Tokyo Station is one very large building with two main sides, and it is easy to come out of the wrong one. The bullet trains, the Narita Express, the Yamanote Line, the Metro and the airport buses all use different parts of it. '
    'This guide is written in plain English so that a first-time visitor, a family or an older traveller can follow it step by step. '
    'You can print the one-page card below and carry it with you.</p>',
    toc_html,
    CARD,
    WHICH,
    DIAGRAM,
    SHINKANSEN,
    NARITA,
    RAIL,
    CONNECTED,
    airalo,
    CARDS,
    LUGGAGE,
    klp("klook-tokyo-station-luggage", "Luggage storage listing"),
    FOOD,
    FINDER,
    SAVE_BOX,
    FACILITIES,
    HELP,
    LEAVING,
    '<div class="tip-box">\n    <strong>Planning more of Japan?</strong> Our <a href="/blog/japan-travel-packing-guide">Japan travel and packing guide</a> covers what to pack, rail passes, etiquette and a budget breakdown, and the <a href="/blog/japan-7-day-itinerary-budget">7-day Japan itinerary</a> shows how a first week can look. Flying in? See our <a href="/blog/narita-airport-guide">Narita Airport guide</a> or <a href="/blog/haneda-airport-guide">Haneda Airport guide</a>.\n</div>',
    "<!-- FIRST-HAND NOTES: add notes and photos from a Tokyo Station visit here -->",
    faq_html(),
    ABOUT,
    RELATED,
    POCKET_BAR,
])
# hero button (v50): a quiet way into the Pocket Guide from the top of the article
HERO_CTA = ('        <div style="margin:48px 0 0;text-align:center;">'
            '<a href="/tokyo-pocket?src=hero" onclick="try{window.gtag&&gtag(\'event\',\'pocket_prompt\',{event_category:\'engagement\',action:\'open_hero\',page_path:location.pathname});}catch(e){}" '
            'style="display:inline-flex;align-items:center;gap:12px;background:#00C9A7;color:#0f0f23;text-align:left;padding:12px 14px 12px 20px;width:340px;max-width:100%;box-sizing:border-box;border-radius:12px;text-decoration:none;min-height:44px;box-shadow:0 6px 18px rgba(0,0,0,.28);line-height:1.2;">'
            '<span style="flex:1;min-width:0;text-align:left;">'
            '<span style="display:block;font-weight:700;font-size:0.8rem;opacity:0.8;">Save to your phone</span>'
            '<span style="display:block;font-weight:800;font-size:1.05rem;margin-top:2px;">Tokyo Station Pocket Guide</span>'
            '<span style="display:block;font-weight:600;font-size:0.8rem;margin-top:2px;opacity:0.8;">Works offline</span></span>'
            '<span aria-hidden="true" style="flex:none;width:40px;height:40px;border-radius:50%;background:#F97316;display:flex;align-items:center;justify-content:center;box-shadow:0 2px 6px rgba(0,0,0,.18);">'
            '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><rect x="6.5" y="2.5" width="11" height="19" rx="2.6"/><path d="M12 8.5v6M9 11.5h6"/></svg></span>'
            '</a></div>')

head = "\n".join([
    "<!DOCTYPE html>",
    '<html lang="en">',
    "<head>",
    '    <meta charset="UTF-8">',
    '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
    '<meta name="robots" content="max-image-preview:large">',
    "    <title>%s</title>" % esc(TITLE),
    '    <meta name="description" content="%s">' % html.escape(DESC),
    '    <meta name="keywords" content="%s">' % html.escape(KEYWORDS),
    '    <link rel="canonical" href="%s">' % URL,
    '    <meta property="og:title" content="%s">' % html.escape(TITLE),
    '    <meta property="og:description" content="%s">' % html.escape(DESC),
    '    <meta property="og:url" content="%s">' % URL,
    '    <meta property="og:type" content="article">',
    '    <meta property="og:site_name" content="PackSmart">',
    ('    <meta property="og:image" content="%s%s">' % (SITE, HERO_URL)) if HERO_URL else ('    <meta property="og:image" content="%s/og-default.png">' % SITE),
    '    <meta name="twitter:card" content="summary_large_image">',
    '    <meta name="twitter:title" content="%s">' % html.escape(TITLE),
    '    <meta name="twitter:description" content="%s">' % html.escape(DESC),
    ('    <meta name="twitter:image" content="%s%s">' % (SITE, HERO_URL)) if HERO_URL else ('    <meta name="twitter:image" content="%s/og-default.png">' % SITE),
    '    <meta property="article:author" content="PackSmart">',
    '    <meta property="article:section" content="Travel">',
    line(25), line(26), line(28),
    "\n".join(t[28:35]),
    ld(ld_article),
    ld(ld_crumbs),
    ld(ld_faq),
    "\n".join(t[84:454]),
    line(462),
    "</head>",
    "<body>",
    "\n".join(t[NAV0:NAV1 + 1]),
    "",
    ('    <div class="hero-blog" style="position:relative; background: linear-gradient(rgba(15,15,35,0.62), rgba(26,26,62,0.72)), url(\'%s\'); background-size: cover; background-position: center 40%%;">' % HERO_URL) if HERO_URL else '    <div class="hero-blog" style="position:relative; background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 100%);">',
    "        <h1>%s</h1>" % esc(H1),
    '        <div class="meta">Station Guide • Japan · Published 19 Nov 2026 · 8 min read</div>',
    HERO_CTA,
    ('        <div style="position:absolute;left:12px;right:12px;bottom:8px;font-size:0.7rem;opacity:0.7;text-align:center;">Photo: PAKUTASO. Illustrative image of the Tokyo Station Marunouchi building at night.</div>' if HERO_URL else ''),
    "</div>",
    "",
    '    <div class="content">',
    "",
])
tail = "\n".join(["    </div>", ""] + t[FOOT:])

page = head + "\n" + BODY + "\n\n" + tail


def add_labels(m):
    tbl = m.group(0)
    heads = [re.sub(r"<[^>]+>", "", h).strip() for h in re.findall(r"<th>(.*?)</th>", tbl, re.S)]
    def row(r):
        i = [0]
        def cell(c):
            lab = heads[i[0]] if i[0] < len(heads) else ""
            i[0] += 1
            return '<td data-label="%s">' % html.escape(lab, quote=True)
        return re.sub(r"<td>", cell, r.group(0))
    return re.sub(r"<tr>(?:(?!</tr>).)*</tr>", row, tbl, flags=re.S)


page = re.sub(r'<div class="ps-scroll">.*?</div>', add_labels, page, flags=re.S)
if "India" in re.sub(r"<script[^>]*>.*?</script>", "", page, flags=re.S) and False:
    pass
# neutral rule check (visible text and JSON-LD)
bad = re.findall(r"\b(India|Indian|INR|Rs\.?|rupee|lakh|Aadhaar|UPI|VFS|BLS)\b|₹", page)
if bad:
    die("neutral-rule violation in generated page: %r" % sorted(set(map(str, bad))))
if "data-ps-placement=\"pickups-japan\"" in page or "airalo-japan" in page:
    die("placement id rename failed")

# GA4 click names for the Sakura and Japan Bullet Train partner links (idempotent)
for _dom, _nm in (("p.sakuramobile.jp", "Sakura_Mobile"), ("japan-bullettrain.com", "Japan_Bullet_Train"), ("klook.tpo.lu", "Klook")):
    if "'%s'" % _dom not in page:
        page = page.replace("'klook.tpx.li': 'Klook',", "'%s': '%s',\n        'klook.tpx.li': 'Klook'," % (_dom, _nm), 1)
    if "'%s'" % _dom not in page:
        die("could not add %s to the affiliate click map" % _dom)

changed = []
if HERO_NOTE:
    changed.append(HERO_NOTE)
old = open(OUT, encoding="utf-8").read() if os.path.isfile(OUT) else None
if old != page:
    open(OUT, "w", encoding="utf-8").write(page)
    changed.append("tokyo-station-guide.html (%s bytes)" % len(page.encode("utf-8")))


# ---- Tokyo Station Pocket Guide: standalone page + service worker + manifest (works offline once visited)
POCKET_PATH = "/tokyo-pocket"
# ---- Pocket Guide analytics (v47): anonymous taps only, no accounts, honours Do Not Track / GPC
GUIDE_ID = "tokyo"
AIRPORT_CODE = "TOKYO-STN"
GA_ID = "G-0C4Z7VVGPE"
AUTO_INSTALL_SHEET = True   # False = never auto-open the install sheet on first visit (the quiet strip stays)
SPONSOR = None              # one labelled slot under the Find tab. Example:
# SPONSOR = {"id": "acme", "brand": "Acme Hotels", "line": "Rooms near Terminal 2", "cta": "See offer", "url": "https://example.com/narita"}
if os.environ.get("PG_SPONSOR_DEMO"):
    SPONSOR = {"id": "demo", "brand": "Demo Brand", "line": "A short line about the offer", "cta": "Learn more", "url": "https://example.com/offer"}
if SPONSOR:
    if not SPONSOR["url"].startswith("https://"):
        die("sponsor url must be https")
    SPONSOR = dict(SPONSOR, url=SPONSOR["url"] + ("&" if "?" in SPONSOR["url"] else "?") + "utm_source=packsmartapp&utm_medium=pocket_guide&utm_campaign=%s_find" % GUIDE_ID)

PG_BOOT = r"""(function(){
  var ID='__GA__', G='__GUIDE__', AP='__AP__', W=window;
  var dbg=/[?&]pgdebug\b/.test(location.search||'');
  function ls(k,v){ try{ if(v===undefined) return localStorage.getItem(k); localStorage.setItem(k,v); }catch(e){} return null; }
  var dnt=(navigator.doNotTrack==='1'||W.doNotTrack==='1'||navigator.globalPrivacyControl===true);
  W.pgDnt=dnt;
  function off(){ return dnt||ls('pgOff')==='1'; }
  var MODE=(navigator.standalone||(W.matchMedia&&W.matchMedia('(display-mode: standalone)').matches))?'app':'web';
  W.dataLayer=W.dataLayer||[]; function gt(){ W.dataLayer.push(arguments); }
  var loaded=false;
  function loadGA(){
    if(loaded||off()||!navigator.onLine) return; loaded=true;
    var cfg={transport_type:'beacon',allow_google_signals:false,allow_ad_personalization_signals:false,page_title:'Pocket Guide: '+G};
    if(dbg) cfg.debug_mode=true;
    gt('js',new Date()); gt('config',ID,cfg);
    var s=document.createElement('script'); s.async=true; s.src='https://www.googletagmanager.com/gtag/js?id='+ID; document.head.appendChild(s);
  }
  function qread(){ try{ return JSON.parse(ls('pgQ')||'[]'); }catch(e){ return []; } }
  function flush(){
    if(off()||!navigator.onLine) return; var a=qread(); if(!a.length) return; ls('pgQ','[]'); loadGA();
    var now=Date.now(); a.forEach(function(x){ if(!x||now-x.t>7*864e5) return; var p=x.p||{}; p.queued=1; p.age_min=Math.round((now-x.t)/6e4); gt('event',x.n,p); });
  }
  W.pgTrack=function(n,p){
    if(off()) return;
    p=p||{}; p.guide=G; p.airport=AP; p.mode=MODE;
    for(var k in p){ if(typeof p[k]==='string') p[k]=p[k].replace(/\s+/g,' ').trim().slice(0,100); }
    if(dbg||W.__pgTest){ (W.__pgLog=W.__pgLog||[]).push({n:n,p:p,online:navigator.onLine}); if(dbg&&W.console) console.log('[pg]',n,p); }
    if(!navigator.onLine){ var a=qread(); a.push({n:n,p:p,t:Date.now()}); ls('pgQ',JSON.stringify(a.slice(-60))); return; }
    loadGA(); flush(); gt('event',n,p);
  };
  W.addEventListener('online',flush);
  var errs=0; W.addEventListener('error',function(e){ if(errs++<3) W.pgTrack('pg_error',{msg:String(e&&e.message||'error')}); });
})();"""
PG_BOOT = PG_BOOT.replace("__GA__", GA_ID).replace("__GUIDE__", GUIDE_ID).replace("__AP__", AIRPORT_CODE)

PG_HOOKS = r"""/* analytics: taps only (see PG_BOOT). One delegated listener, so tiles need no code of their own. */
  var AUTO_INSTALL_SHEET=__AUTO__;
  var instVia='help';
  function tabNow(){ var p=document.querySelector('.panel:not([hidden])'); return p?p.id.replace('p-',''):''; }
  function whereNow(){ return ((!sheet.hidden&&shT.textContent)||tabNow()).replace(/^[^A-Za-z0-9]+/,''); }
  function bare(h){ return String(h||'').replace(/^www\./,''); }
  function linkEv(a){
    var h=a.getAttribute('href')||''; if(!h||h.charAt(0)==='#'||a.hasAttribute('data-sp')) return;
    if(/^tel:/i.test(h)){ var d=h.replace(/^tel:/i,'').replace(/[^0-9+]/g,''); var nm={'119':'fire_ambulance','110':'police','+815038162787':'help_line'}; pgTrack('pg_call',{dest:nm[d]||d,where:whereNow()}); return; }
    if(/^mailto:/i.test(h)) return;
    if(/(^|\s)sponsored(\s|$)/.test(a.getAttribute('rel')||'')){ pgTrack('pg_partner',{partner:a.textContent,host:a.hostname,where:whereNow()}); return; }
    if(a.hostname&&bare(a.hostname)!==bare(location.hostname)&&a.hostname!=='packsmartapp.com'){ pgTrack('pg_outbound',{host:a.hostname,where:whereNow()}); return; }
    pgTrack('pg_internal',{path:a.pathname,where:whereNow()});
  }
  document.addEventListener('click',function(e){
    var el=e.target&&e.target.closest?e.target.closest('a,button'):null; if(!el) return;
    if(el.tagName==='A'){ linkEv(el); return; }
    var id=el.id||'', tab=tabNow(), tx;
    if(el.getAttribute('role')==='tab'&&el.getAttribute('data-tab')){ pgTrack('pg_tab',{tab:el.getAttribute('data-tab')}); return; }
    if(el.classList.contains('tile')){
      if(el.classList.contains('more')){ pgTrack('pg_slide',{tab:tab,to:el.classList.contains('pgnext')?'more':'back'}); return; }
      tx=el.querySelector('.tx'); var lab=el.getAttribute('data-id')||(tx?tx.textContent:'');
      if(el.closest('#askTiles')) pgTrack('pg_phrase',{cat:askCat,item:lab});
      else pgTrack('pg_tile',{tab:tab,item:lab,terminal:term});
      return;
    }
    if(el.hasAttribute('data-t')&&el.closest('.seg')){ pgTrack('pg_terminal',{terminal:el.getAttribute('data-t'),from:tab}); return; }
    if(el.hasAttribute('data-c')&&el.closest('#askCats')){ pgTrack('pg_phrase_cat',{cat:el.getAttribute('data-c')}); return; }
    if(el.hasAttribute('data-d')){ pgTrack('pg_dep_view',{view:el.getAttribute('data-d')}); return; }
    if(el.classList.contains('stp')){ tx=el.querySelector('b'); pgTrack('pg_step',{tab:tab,step:tx?tx.textContent:'',done:el.getAttribute('aria-pressed')==='true'?1:0}); return; }
    if(id==='playJp'){ var en=shB.querySelector('.en2'); pgTrack('pg_play',{item:en?en.textContent:''}); return; }
    if(id==='shareBtn'){ pgTrack('pg_share',{}); return; }
    if(id==='instGo'){ pgTrack('pg_install_tap',{}); return; }
    if(id==='instLater'){ pgTrack('pg_install_later',{}); return; }
    if(id==='instDone'){ pgTrack('pg_install_claimed',{}); return; }
  });
  (function(){
    var n=parseInt(flag('pgVisits')||'0',10)+1; flag('pgVisits',String(n));
    var sp=new URLSearchParams(location.search), src=(sp.get('src')||'').replace(/[^a-z0-9_-]/gi,'').slice(0,20);
    if(src&&!flag('pgSrc')) flag('pgSrc',src);
    var ref=''; try{ if(document.referrer){ var rh=bare(new URL(document.referrer).hostname); ref=(rh===bare(location.hostname)||rh==='packsmartapp.com')?'packsmartapp.com':rh; } }catch(e){}
    pgTrack('pg_open',{os:isIOS?'ios':isAnd?'android':'desktop',src:src,src_first:flag('pgSrc')||'',ref:ref,visit:Math.min(n,20),online:navigator.onLine?1:0,lang:(navigator.language||'').slice(0,5).toLowerCase()});
    if(standalone&&!flag('pgApp')){ flag('pgApp','1'); pgTrack('pg_first_app_open',{os:isIOS?'ios':isAnd?'android':'desktop'}); }
  })();
  /* transparency line + off switch */
  (function(){
    var po=$('pgOpt'); if(!po) return;
    function paintOpt(){ if(window.pgDnt){ po.textContent='Counting is off (your browser asks sites not to track).'; po.removeAttribute('href'); } else { po.textContent=flag('pgOff')==='1'?'Turn counting back on':'Turn off counting'; } }
    po.addEventListener('click',function(e){ e.preventDefault(); if(window.pgDnt) return; if(flag('pgOff')==='1'){ flag('pgOff','0'); } else { flag('pgOff','1'); flag('pgQ','[]'); } paintOpt(); });
    paintOpt();
  })();
  /* the one sponsor slot (off unless SPONSOR is set in the generator) */
  (function(){
    var SP=__SPONSOR__, box=$('sponsor'); if(!SP||!box||!/^https:\/\//.test(SP.url)) return;
    var a=document.createElement('a'); a.href=SP.url; a.target='_blank'; a.rel='sponsored nofollow noopener'; a.className='spon-a'; a.setAttribute('data-sp','1');
    var l=document.createElement('span'); l.className='spon-l'; l.textContent='Sponsor';
    var b=document.createElement('b'); b.textContent=SP.brand;
    var s=document.createElement('span'); s.className='spon-t'; s.textContent=SP.line;
    var c=document.createElement('span'); c.className='spon-c'; c.textContent=SP.cta||'Learn more';
    a.appendChild(l); a.appendChild(b); a.appendChild(s); a.appendChild(c); box.appendChild(a);
    function vis(){ box.hidden=!navigator.onLine; } vis(); window.addEventListener('online',vis); window.addEventListener('offline',vis);
    a.addEventListener('click',function(){ pgTrack('pg_sponsor_click',{brand:SP.id,slot:'find_bottom'}); });
    if('IntersectionObserver' in window){ var seen=false; new IntersectionObserver(function(en){ if(en[0].isIntersecting&&!seen&&!box.hidden){ seen=true; pgTrack('pg_sponsor_view',{brand:SP.id,slot:'find_bottom'}); } },{threshold:0.5}).observe(box); }
  })();
  """
PG_HOOKS = PG_HOOKS.replace("__AUTO__", "true" if AUTO_INSTALL_SHEET else "false").replace("__SPONSOR__", json.dumps(SPONSOR).replace("</", "<\\/") if SPONSOR else "null")

POCKET_SVG = re.search(r'<svg id="tokDiagram".*?</svg>', DIAGRAM, re.S).group(0).replace('id="tokDiagram"', 'id="pkDiagram"').replace('id="tokT"', 'id="pkT"').replace('id="tokD"', 'id="pkD"').replace('aria-labelledby="tokT tokD"', 'aria-labelledby="pkT pkD"')
POCKET_CSS = """
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html{-webkit-text-size-adjust:100%;height:100%}
body{margin:0;height:100%;height:100dvh;display:flex;flex-direction:column;overflow:hidden;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;font-size:18px;line-height:1.5;color:#0f0f23;background:#EEF3F4;--tabh:calc(64px + env(safe-area-inset-bottom))}
.top{flex:none;background:linear-gradient(135deg,#1a1a3e 0%,#0f0f23 55%,#0b5d57 140%);color:#fff;padding:calc(10px + env(safe-area-inset-top)) 16px 12px;display:flex;justify-content:space-between;align-items:center;gap:10px;border-bottom:3px solid #00C9A7}
.top strong{display:block;font-size:1.15rem;line-height:1.2}
.top .by{display:block;font-size:0.78rem;color:#B9C3E6;margin-top:2px}
.status{flex:none;font-size:0.8rem;font-weight:700;border-radius:20px;padding:5px 11px;background:rgba(255,255,255,.16);color:#fff;white-space:nowrap}
.status.saved{background:#00C9A7;color:#0f0f23}
.status.off{background:#FFB84D;color:#3a2400}
.panels{flex:1;min-height:0;overflow-y:auto;-webkit-overflow-scrolling:touch;padding-bottom:12px}
.panel{max-width:560px;margin:0 auto;padding:12px 14px 4px}
.panel[hidden]{display:none}
.seg-h{font-weight:700;font-size:0.95rem;color:#333;margin:2px 2px 8px}
.seg{display:grid;grid-template-columns:repeat(2,1fr) .8fr;gap:8px}
.seg button{font:inherit;min-height:54px;border:2px solid #D5DCE0;background:#fff;color:#0f0f23;border-radius:14px;cursor:pointer;padding:4px 2px;line-height:1.1;display:flex;flex-direction:column;align-items:center;justify-content:center}
.seg button small{font-size:0.7rem;font-weight:600;color:#666}
.seg button b{font-size:1.05rem}
.seg button.txt{font-weight:700;font-size:0.95rem}
.seg button[aria-pressed="true"]{background:#1a1a3e;border-color:#1a1a3e;color:#fff;box-shadow:0 3px 0 #00C9A7}
.seg button[aria-pressed="true"] small{color:#B9C3E6}
.tiles{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:6px}
.tile{font:inherit;display:flex;align-items:center;gap:10px;min-height:64px;padding:8px 10px;border-radius:16px;border:2px solid #E1E8EB;background:#fff;color:#0f0f23;cursor:pointer;text-align:left;box-shadow:0 2px 0 rgba(15,15,35,.06)}
.tile:active{transform:translateY(1px)}
.tile .ic{flex:none;width:42px;height:42px;border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:1.65rem;background:#D9F7EF}
.tile.c1 .ic{background:#FDE4E9}
.tile.c2 .ic{background:#E6E6F5}
.tile .tx{font-weight:700;font-size:1rem;line-height:1.2}
.hint{margin:8px 2px 0;font-size:0.82rem;color:#555;text-align:center}
#sponsor{margin:12px 0 0}
#sponsor[hidden]{display:none}
.spon-a{display:block;text-decoration:none;color:inherit;border:1px solid #e3e3ea;border-radius:12px;padding:10px 12px;background:#fff}
.spon-l{display:block;font-size:0.68rem;letter-spacing:0.06em;text-transform:uppercase;color:#666;margin-bottom:2px}
.spon-a b{display:block;font-size:0.95rem;color:#1a1a3e}
.spon-t{display:block;font-size:0.85rem;color:#444;margin-top:2px}
.spon-c{display:inline-block;margin-top:6px;font-size:0.85rem;font-weight:600;color:#1a1a3e;text-decoration:underline}
.card{background:#fff;border-radius:16px;padding:14px 16px;margin:0 0 10px;border:2px solid #E1E8EB}
.card h2{margin:0 0 6px;font-size:1.1rem}
.card p{margin:0 0 6px}
.small{font-size:0.82rem;color:#555}
.tmap{display:flex;flex-direction:column}
.seg2{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:0 0 10px}
.seg2 button{font:inherit;font-weight:800;font-size:0.95rem;min-height:46px;border:2px solid #D5DCE0;background:#fff;color:#0f0f23;border-radius:14px;cursor:pointer}
.seg2 button[aria-pressed="true"]{background:#1a1a3e;border-color:#1a1a3e;color:#fff;box-shadow:0 3px 0 #00C9A7}
.sheet a{color:#00776a;font-weight:700}
.tcard{position:relative;display:flex;gap:14px;align-items:center;border-radius:20px;padding:14px 14px;border:2px solid #CDEFE8;background:linear-gradient(135deg,#E6FAF5,#fff 70%);box-shadow:0 3px 0 rgba(15,15,35,.06)}
.tcard h3{margin:0 0 4px;font-size:1.25rem;line-height:1.1}
.tcard.here{border-color:#00A98C;box-shadow:0 0 0 3px rgba(0,201,167,.35)}
.tcard .heretag{display:inline-block;background:#00A98C;color:#fff;font-weight:800;font-size:.78rem;border-radius:20px;padding:2px 10px;margin:0 0 4px}
.tcard .route{font-weight:700;color:#2a2f45;margin-top:6px}
.tlink[hidden]{display:none}
.tcard p{margin:2px 0;font-size:0.95rem;line-height:1.3}
.tcard .tb{min-width:0}
.badge{flex:none;width:54px;height:54px;border-radius:16px;display:flex;align-items:center;justify-content:center;font-size:1.9rem;font-weight:800;color:#fff;background:linear-gradient(135deg,#00C9A7,#0b8f7c);box-shadow:0 3px 0 rgba(0,0,0,.12)}
.t2{border-color:#D3D3EE;background:linear-gradient(135deg,#ECECF9,#fff 70%)}
.t2 .badge{background:linear-gradient(135deg,#34346e,#1a1a3e)}
.t3{border-color:#F6CBD3;background:linear-gradient(135deg,#FDECEF,#fff 70%)}
.t3 .badge{background:linear-gradient(135deg,#E94560,#c92f4a)}
.wing{display:inline-block;font-size:0.72rem;font-weight:800;letter-spacing:.02em;text-transform:uppercase;background:#1a1a3e;color:#fff;border-radius:6px;padding:1px 6px;margin-right:4px;vertical-align:1px}
.stn{display:inline-block;margin-top:6px!important;font-weight:700;color:#0b6b59;background:#fff;border:1.5px solid #BFEADF;border-radius:10px;padding:3px 9px}
.t2 .stn{color:#1a1a3e;border-color:#D3D3EE}
.stn.warn{color:#a3243b;border-color:#F6CBD3}
.tlink{display:flex;gap:10px;align-items:center;margin:0 0 0 27px;padding:6px 0 6px 20px;border-left:3px dashed #B9C3D0;font-size:0.9rem;font-weight:600;color:#2a2f45;line-height:1.25}
.tlink span:first-child{font-size:1.3rem}
.steps{list-style:none;margin:0;padding:0}
.steps li{margin:0 0 7px}
.stp{font:inherit;width:100%;display:flex;gap:12px;align-items:flex-start;text-align:left;background:#fff;border:2px solid #E1E8EB;border-radius:14px;padding:8px 12px;line-height:1.28;color:#0f0f23;cursor:pointer;box-shadow:0 2px 0 rgba(15,15,35,.05)}
.stp .n{flex:none;width:34px;height:34px;border-radius:50%;background:linear-gradient(135deg,#00C9A7,#0b8f7c);color:#fff;font-weight:800;display:flex;align-items:center;justify-content:center;margin-top:1px}
.stp b{display:block;font-size:1.02rem}
.stp .tx{font-size:0.9rem;color:#333}
.stp[aria-pressed="true"]{background:#F1FBF9;border-color:#00C9A7}
.stp[aria-pressed="true"] .n{background:#0b6b59}
.stp[aria-pressed="true"] b::after{content:" · Done";font-size:0.8rem;font-weight:700;color:#0b6b59}
.reset[hidden]{display:none}
.reset{font:inherit;font-size:0.85rem;font-weight:700;color:#0b6b59;background:none;border:0;text-decoration:underline;cursor:pointer;padding:8px 4px;margin:0 0 0 2px}
.lead2{margin:0 2px 8px;font-size:0.9rem;color:#555}
.sheet .jp{font-size:2.1rem;font-weight:800;line-height:1.35;text-align:center;margin:10px 0 6px;color:#0f0f23}
.sheet .rom{font-size:1.15rem;text-align:center;color:#444;margin:0 0 8px}
.sheet .en2{font-size:1.15rem;text-align:center;font-weight:700;margin:0 0 8px;color:#00776a}
.heroline{display:flex;gap:12px;align-items:center;background:linear-gradient(135deg,#1a1a3e,#0f0f23);color:#fff;border-radius:14px;padding:8px 14px;margin:0 0 8px}
.heroline .big2{flex:none;font-size:1.7rem;font-weight:800;line-height:1;color:#00C9A7}
.heroline span{font-size:0.9rem;line-height:1.25}
.sec-h{font-weight:800;font-size:0.95rem;margin:10px 2px 4px;color:#1a1a3e}
#p-help .tiles{grid-template-columns:repeat(2,minmax(0,1fr))}
#p-help .sec-h{margin-top:16px}
.cats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:6px;margin:10px 0 12px}
.cats button{font:inherit;font-weight:700;font-size:.78rem;line-height:1.1;min-height:58px;padding:6px 2px;border-radius:14px;border:2px solid #DCE3E8;background:#F4F7F8;color:#2a2f45;cursor:pointer;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px;overflow-wrap:break-word;min-width:0}
.cats button .ci{font-size:1.25rem;line-height:1}
.cats button[aria-pressed=true]{background:#1a1a3e;border-color:#1a1a3e;color:#fff}
#p-help .tile{padding:8px;gap:8px}
#p-help .tile .ic{width:38px;height:38px;font-size:1.45rem}
#p-help .tile .tx{font-size:.95rem;min-width:0;overflow-wrap:break-word}
.sheet ul.pl{margin:6px 0 6px 1.1rem;padding:0;font-size:1.05rem}
.sheet ul.pl li{margin:0 0 6px}
.sheet p.n2{margin:6px 0;font-size:1.05rem}
.sheet .sm{font-size:0.85rem;color:#555;margin:6px 0 0}
.tiles .tile:last-child:nth-child(odd){grid-column:1/-1}
.pager{overflow:hidden;margin-top:6px}
.track{display:flex;align-items:flex-start;transition:transform .28s ease}
.tiles.pane{flex:0 0 100%;min-width:0;margin-top:0;visibility:visible}
.tiles.pane.off{visibility:hidden}
.hpane{flex:0 0 100%;min-width:0}
.hpane.off{visibility:hidden;height:0;overflow:hidden}
#p-help .tiles.hnav{grid-template-columns:minmax(0,1fr);margin:2px 0 12px}
@media (max-width:380px){#p-help .tile{padding:7px 6px;gap:6px}#p-help .tile .ic{width:32px;height:32px;font-size:1.25rem}#p-help .tile .tx{font-size:.86rem}}
@media (max-width:340px){#p-help .tile{padding:6px 5px;gap:5px}#p-help .tile .ic{width:26px;height:26px;font-size:1.05rem}#p-help .tile .tx{font-size:.78rem}}
.card.slim{padding:10px 12px}
.quiet{margin-top:18px}
.quiet .card.slim{background:#E8EEF1;border-color:#E8EEF1;padding:8px 12px;margin-bottom:6px}
.quiet .card.slim h2{font-size:.92rem}
.quiet .card.slim p{font-size:.85rem;color:#3d4659}
.quiet .card.slim button.big{padding:7px 12px;font-size:.88rem;border-color:#9DB4BC;background:#fff}
.quiet>.small{margin-top:10px}
.card.slim .row{display:flex;gap:10px;align-items:center}
.card.slim .row>div:first-child{flex:1;min-width:0}
.card.slim h2{font-size:1rem;margin:0 0 2px}
.card.slim p{margin:0;font-size:.9rem}
.card.slim p.small{font-size:.8rem;margin-top:2px}
.card.slim button.big{flex:none;padding:10px 14px;font-size:.95rem}
#p-help .tile.more{padding:4px 12px;gap:8px;min-height:46px;background:#EAF8F4;border:2px solid #BCE8DD;color:#0b6f60}
#p-help .tile.more .ic{width:30px;height:30px;font-size:1.15rem}
#p-help .tile.more .tx{font-size:1rem}
.tiles.pane .tile:last-child:nth-child(odd):not(.more){grid-column:auto}
.tiles .tile.more{grid-column:1/-1;min-height:50px;padding:5px 12px;gap:8px;background:#fff;border:3px solid #00C9A7;box-shadow:none;color:#0b6f60}
.tiles .tile.more .ic{width:36px;height:36px;border-radius:50%;background:#00C9A7;color:#fff;font-weight:900;font-size:1.35rem;line-height:1;justify-content:center}
.tiles .tile.more .tx{font-weight:800;line-height:1.15}
.tiles .tile.more small{display:block;font-weight:700;font-size:.8em;color:#4a5568;margin-top:1px}
.tiles .tile.pgnext{flex-direction:row-reverse;justify-content:space-between}
.tiles.pane .tile:not(.more){flex-direction:row;justify-content:flex-start;text-align:left;min-height:76px;gap:8px;padding:8px 10px}
.tiles.pane .tile:not(.more) .ic{width:42px;height:auto;flex:none;background:transparent;font-size:2.15rem;line-height:1.1}
.tiles.pane .tile:not(.more) .tx{flex:1;min-width:0;text-align:left;line-height:1.15}
.tiles.pane .tile:not(.more).c0{background:linear-gradient(180deg,#F3FDFA,#CFF4EB);border:2px solid #8EE3D2;box-shadow:0 4px 0 #00A98C}
.tiles.pane .tile:not(.more).c1{background:linear-gradient(180deg,#FFF5F7,#FFD9E0);border:2px solid #FFA3B3;box-shadow:0 4px 0 #C93550}
.tiles.pane .tile:not(.more).c2{background:linear-gradient(180deg,#F6F6FF,#DADAF8);border:2px solid #AFAFEE;box-shadow:0 4px 0 #5959BE}
@media (prefers-reduced-motion:reduce){.track{transition:none}}
a{color:#00776a}
a.num{display:flex;align-items:center;gap:12px;text-decoration:none;color:#fff;border-radius:16px;padding:12px 14px;margin:8px 0 0;min-height:60px}
a.num .ni{font-size:1.9rem;line-height:1;flex:none}
a.num .nt{display:flex;flex-direction:column;min-width:0;line-height:1.2}
a.num .nt b{font-size:1rem;font-weight:800}
a.num .nt span{font-size:1.25rem;font-weight:800;overflow-wrap:anywhere}
a.num .nt small{font-size:.85rem;font-weight:600;opacity:.92;margin-top:2px}
a.num.air{background:linear-gradient(135deg,#1a1a3e,#2c2c63);box-shadow:0 3px 0 #0b0b22}
a.num.em{background:linear-gradient(135deg,#E94560,#c92f4a);box-shadow:0 3px 0 #9d2238;margin:0}
a.num.hot{background:linear-gradient(135deg,#00B398,#00897a);box-shadow:0 3px 0 #006b5e}
.numgrid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;margin-top:8px}
.numgrid a.num{padding:10px 10px;gap:8px;min-height:56px}
.numgrid a.num .ni{font-size:1.6rem}
.numgrid a.num .nt b{font-size:.9rem}
details.card summary{font-weight:700;font-size:1.05rem;cursor:pointer;min-height:36px;display:flex;align-items:center}
details.card[open] summary{margin-bottom:6px}
button.big{font:inherit;font-weight:700;font-size:1.05rem;background:#fff;border:2px solid #00C9A7;border-radius:12px;padding:12px 18px;cursor:pointer}
.tabs{flex:none;display:grid;grid-template-columns:repeat(5,1fr);background:#fff;border-top:1px solid #D5DCE0;padding-bottom:env(safe-area-inset-bottom);box-shadow:0 -4px 14px rgba(15,15,35,.08);position:relative;z-index:6}
.tabs button{font:inherit;height:64px;border:0;background:none;color:#5a6070;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;font-size:0.74rem;font-weight:700;cursor:pointer;position:relative}
.tabs button span{font-size:1.5rem;line-height:1}
.tabs button[aria-selected="true"]{color:#0b6b59}
.tabs button[aria-selected="true"]::before{content:"";position:absolute;top:0;left:22%;right:22%;height:4px;border-radius:0 0 4px 4px;background:#00C9A7}
.inst-strip{flex:none;display:flex;align-items:center;gap:10px;width:100%;border:0;border-bottom:2px solid #00C9A7;background:#D9F7EF;color:#0f3a33;font:inherit;font-size:0.95rem;line-height:1.25;padding:8px 14px;text-align:left;cursor:pointer;min-height:48px}
.inst-strip[hidden]{display:none}
.inst-strip .ico{font-size:1.4rem;flex:none}
.inst-strip .go{margin-left:auto;flex:none;font-weight:800;background:#1a1a3e;color:#fff;border-radius:20px;padding:6px 14px;font-size:0.9rem}
.istep{list-style:none;margin:12px 0;padding:0}
.istep li{display:flex;gap:12px;align-items:center;margin:0 0 12px;font-size:1.1rem;line-height:1.3}
.istep .n{flex:none;width:34px;height:34px;border-radius:50%;background:#1a1a3e;color:#fff;font-weight:800;display:flex;align-items:center;justify-content:center}
.istep svg{flex:none;width:32px;height:32px;color:#0b6b59;background:#F1FBF9;border-radius:8px;padding:3px}
.tipbox{background:#FFF4D6;border-radius:12px;padding:10px 12px;font-size:0.95rem;margin:8px 0;line-height:1.35}
.sheet .lede{margin:2px 0 4px;color:#333;font-size:1rem}
.sheet .row2{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.sheet .close.ghost{background:#fff;color:#1a1a3e;border:2px solid #1a1a3e}
.scrim{position:fixed;inset:0;background:rgba(15,15,35,.45);z-index:7}
.scrim[hidden],.sheet[hidden]{display:none}
.sheet{position:fixed;left:0;right:0;bottom:var(--tabh);z-index:8;background:#fff;border-radius:22px 22px 0 0;box-shadow:0 -10px 30px rgba(15,15,35,.25);padding:16px 18px 16px;max-height:calc(100dvh - var(--tabh) - 70px);overflow-y:auto;max-width:560px;margin:0 auto;animation:up .18s ease-out}
@keyframes up{from{transform:translateY(24px);opacity:.4}to{transform:none;opacity:1}}
.sheet h2{margin:0 0 4px;font-size:1.3rem;display:flex;align-items:center;gap:10px}
.sheet .ans{font-size:1.35rem;line-height:1.4;margin:8px 0;padding:12px 14px;border-radius:12px;background:#F1FBF9;border-left:6px solid #00C9A7}
.sheet .ans em{display:block;font-style:normal;font-weight:800;font-size:0.85rem;color:#0b6b59;margin-bottom:2px}
.sheet .ans.mini{font-size:1.05rem;margin:6px 0}
.sheet .close{font:inherit;font-weight:800;width:100%;min-height:54px;margin-top:8px;border:0;border-radius:14px;background:#1a1a3e;color:#fff;font-size:1.1rem;cursor:pointer}
@media (prefers-reduced-motion:reduce){.sheet{animation:none}.tile:active{transform:none}}
@media (max-height:640px){.tile{min-height:62px}.tabs button{height:58px}body{--tabh:calc(58px + env(safe-area-inset-bottom))}}
"""
POCKET_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Tokyo Station Pocket Guide | PackSmart</title>
<meta name="description" content="A simple Tokyo Station helper that works offline: Marunouchi and Yaesu sides, Shinkansen and Narita Express platforms, lockers, information and more. By PackSmart.">
<meta name="robots" content="noindex,follow">
<link rel="canonical" href="__GUIDE_URL__">
<meta name="theme-color" content="#1a1a3e">
<link rel="manifest" href="/tokyo-pocket.webmanifest">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" href="/images/tokyo-apple-touch-180.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Tokyo">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<script>__PG_BOOT__</script>
<style>__CSS__</style>
</head>
<body>
<header class="top">
<div><strong>Tokyo Station Pocket Guide</strong><span class="by">by PackSmart &middot; 19 Nov 2026</span></div>
<div class="status" id="status" role="status">Checking...</div>
</header>
<button type="button" class="inst-strip" id="instStrip" hidden><span class="ico" aria-hidden="true">&#128242;</span><span><b>Add this to your home screen</b><br>so it works with no internet</span><span class="go">How</span></button>
<div class="panels" id="panels">
<section class="panel" id="p-find" role="tabpanel" aria-labelledby="t-find">
<p class="seg-h">Which side are you on?</p>
<div class="seg" id="seg"></div>
<p class="seg-h" style="margin-top:14px">What do you need? <span class="small">Tap one.</span></p>
<div class="pager" id="pager"><div class="track" id="track"><div class="tiles pane" id="tiles"></div><div class="tiles pane off" id="tiles2" aria-hidden="true"></div></div></div>
<p class="hint">Floors can change. Ask station staff.</p>
<div id="sponsor" hidden></div>
<noscript><p class="card">This guide needs JavaScript. Please turn it on, or ask at any information counter.</p></noscript>
</section>
<section class="panel" id="p-map" role="tabpanel" aria-labelledby="t-map" hidden>
<p class="seg-h" style="margin-top:2px">Which side are you on?</p>
<div class="seg" id="mseg"></div>
<p class="lead2" id="mLead" style="margin-top:10px">Bullet train passengers: the Yaesu side is recommended.</p>
<div class="tmap" id="tmap">
<div class="tcard t1" data-t="T1"><div class="badge">&#127963;&#65039;</div><div class="tb"><h3>Marunouchi side</h3><p>West: the red-brick building, the Narita Express route, the Travel Service Center, the hotel</p><p class="stn"><span aria-hidden="true">&#128645;</span> Narita Express: Central Gate, down to B5</p></div></div>
<div class="tlink"><span aria-hidden="true">&#128694;</span><span>Walk through the station<br>by the central passage, 1st floor</span></div>
<div class="tcard t2" data-t="T2"><div class="badge">&#128645;</div><div class="tb"><h3>Yaesu side</h3><p>East: bullet trains, First Avenue and Ramen Street, airport and highway buses</p><p class="stn"><span aria-hidden="true">&#128652;</span> Airport buses: Yaesu North Exit</p></div></div>
</div>
<p class="small" style="text-align:center;margin-top:10px">Simplified, not to scale. Station layouts change, so follow the signs.</p>
</section>
<section class="panel" id="p-arrive" role="tabpanel" aria-labelledby="t-arrive" hidden>
<p class="lead2">Arrived by Shinkansen? Tap a step to tick it off.</p>
<ol class="steps" id="arrSteps"></ol>
<button type="button" class="reset" id="arrReset" hidden>Clear ticks</button>
<p class="sec-h">Then, once you are out</p>
<div class="tiles" id="arrTiles"></div>
</section>
<section class="panel" id="p-depart" role="tabpanel" aria-labelledby="t-depart" hidden>
<div class="seg2" id="depSeg" role="group" aria-label="Departure sections"><button type="button" data-d="before" aria-pressed="true">Before you go</button><button type="button" data-d="air" aria-pressed="false">At the station</button></div>
<div id="depBefore">
<div class="tiles" id="depTiles"></div>
<p class="hint">Tap one for the details. Prices and times are approximate.</p>
</div>
<div id="depAir" hidden>
<div class="heroline"><span class="big2">14-23</span><span><b>Shinkansen platforms at Tokyo.</b><br>Your ticket and the boards show yours. Platforms can change.</span></div>
<ol class="steps" id="depSteps"></ol>
<button type="button" class="reset" id="depReset" hidden>Clear ticks</button>
</div>
</section>
<section class="panel" id="p-help" role="tabpanel" aria-labelledby="t-help" hidden>
<div class="pager" id="hpager"><div class="track" id="htrack">
<div class="hpane" id="hp1">
<div class="card" id="sayCard"><h2>Say it in Japanese</h2><p class="small">Tap one, then show your phone. Or tap Play.</p><div class="cats" id="askCats" role="group" aria-label="Phrase groups"></div><div class="tiles" id="askTiles"></div></div>
<div class="tiles hnav" id="hnav1"></div>
</div>
<div class="hpane off" id="hp2" aria-hidden="true">
<div class="card" id="numCard"><h2>Useful phone numbers</h2><p class="small">Tap a number to call. Your phone company may charge for calls abroad.</p>
<p class="sec-h">Emergency (free, 24 hours)</p>
<div class="numgrid"><a class="num em" href="tel:119"><span class="ni" aria-hidden="true">&#128657;</span><span class="nt"><b>Ambulance or fire</b><span>119</span></span></a><a class="num em" href="tel:110"><span class="ni" aria-hidden="true">&#128659;</span><span class="nt"><b>Police</b><span>110</span></span></a></div>
<p class="sec-h">At the station</p>
<p class="small" style="margin-top:0">JR East Information Centers, 10 am to 6 pm, on the 1st floor. Staff will help, so just ask.</p>
<p class="sec-h">Help or travel questions</p>
<a class="num hot" href="tel:+815038162787"><span class="ni" aria-hidden="true">&#128222;</span><span class="nt"><b>Japan Visitor Hotline</b><span>050-3816-2787</span><small>24 hours. English, Chinese, Korean</small></span></a>
</div>
<div class="tiles hnav" id="hnav2"></div>
</div>
</div></div>
<div class="quiet"><div class="card slim" id="shareCard" hidden><div class="row"><div><h2>Helping someone travel?</h2><p>Send them this guide for offline use.</p></div><button type="button" class="big" id="shareBtn">Send it</button></div></div>
<div class="card slim install" id="install"><div class="row"><div><h2>Keep this on your phone</h2><p>Add it to your home screen. Works offline.</p><p class="small" id="instDesk">Open this page on your phone, then add it to your home screen.</p></div><div id="instHow" hidden><button type="button" class="big" id="instBtn">Show me</button></div></div></div>
<p class="small">Facility details come from Tokyo Station City, JR East, First Avenue and JNTO pages, checked 19 November 2026. Floors, opening hours and counters can change. If you cannot find something, ask station staff or a JR East Information Center. Found something out of date? <a href="/contact">Tell us</a> (needs internet). We count anonymous taps to improve this guide: no name, no account. <a href="/privacy-policy">Privacy</a> &middot; <a href="#" id="pgOpt">Turn off counting</a>. The full guide, with platforms, trains and luggage, is at <a href="__GUIDE_URL__">packsmartapp.com</a> (needs internet).</p></div>
</section>
</div>
<nav class="tabs" role="tablist" aria-label="Sections">
<button type="button" role="tab" id="t-find" data-tab="find" aria-selected="true"><span aria-hidden="true">&#128269;</span>Find</button>
<button type="button" role="tab" id="t-map" data-tab="map" aria-selected="false"><span aria-hidden="true">&#128506;&#65039;</span>Sides</button>
<button type="button" role="tab" id="t-arrive" data-tab="arrive" aria-selected="false"><span aria-hidden="true">&#128649;</span>Arrival</button>
<button type="button" role="tab" id="t-depart" data-tab="depart" aria-selected="false"><span aria-hidden="true">&#128646;</span>Leaving</button>
<button type="button" role="tab" id="t-help" data-tab="help" aria-selected="false"><span aria-hidden="true">&#128587;</span>Help</button>
</nav>
<div class="scrim" id="scrim" hidden></div>
<div class="sheet" id="inst" role="dialog" aria-modal="true" aria-labelledby="instT" hidden>
<h2 id="instT"><span aria-hidden="true">&#128242;</span>Add to your home screen</h2>
<div id="instBody"></div>
</div>
<div class="sheet" id="sheet" role="dialog" aria-modal="true" aria-labelledby="shTitle" hidden>
<h2 id="shTitle"></h2>
<div id="shBody" aria-live="polite"></div>
<button type="button" class="close" id="shClose">Close</button>
</div>
<script>
(function(){
  var D=__FINDER_JSON__;
  var ICON={prayer:'\\uD83D\\uDE4F',baby:'\\uD83C\\uDF7C',quiet:'\\uD83E\\uDD2B',info:'\\u2139\\uFE0F',help:'\\u267F',lockers:'\\uD83E\\uDDF3',wifi:'\\uD83D\\uDCF6',shower:'\\uD83D\\uDEBF',internet:'\\uD83D\\uDCBB',play:'\\uD83E\\uDDF8',smoking:'\\uD83D\\uDEAC',toilet:'\\uD83D\\uDEBB',food:'\\uD83C\\uDF5C',money:'\\uD83D\\uDCB4',unwell:'\\uD83C\\uDFE5',pharmacy:'\\uD83D\\uDC8A',trains:'\\uD83D\\uDE86',tickets:'\\uD83C\\uDFAB',phone:'\\uD83D\\uDCF6',charge:'\\uD83D\\uDD0B',more:'\\u2795'};
  var SHORT={prayer:'Prayer room',baby:'Nursing room',quiet:'Quiet space',info:'Information counter',help:'Wheelchair and help',lockers:'Luggage',wifi:'Wi-Fi rental',shower:'Showers',internet:'Free internet',play:'Kids play area',smoking:'Smoking room',toilet:'Toilets',food:'Food and drink',money:'Money and ATMs',unwell:'Feeling unwell',pharmacy:'Pharmacy',trains:'Trains and buses',tickets:'Tickets and passes',phone:'Phone and Wi-Fi',charge:'Phone charging',more:'More places'};
  var term='ALL', lastTile=null;
  try{ var s=localStorage.getItem('tokTerm'); if(s&&/^(ALL|T1|T2)$/.test(s)) term=s; }catch(e){}
  function $(id){return document.getElementById(id);}
  /* side selector */
  var seg=$('seg');
  function segBtn(id,html,cls){
    var b=document.createElement('button'); b.type='button'; b.setAttribute('data-t',id); if(cls) b.className=cls;
    b.innerHTML=html; b.addEventListener('click',function(){ term=id; try{localStorage.setItem('tokTerm',id);}catch(e){} paintSeg(); renderDep(); }); return b;
  }
  D.terms.forEach(function(t){ seg.appendChild(segBtn(t[0],'<small>'+(t[0]==='T1'?'West':'East')+'</small><b>'+t[1]+'</b>')); });
  seg.appendChild(segBtn('ALL','Not sure','txt'));
  var mseg=$('mseg');
  D.terms.forEach(function(t){ mseg.appendChild(segBtn(t[0],'<small>'+(t[0]==='T1'?'West':'East')+'</small><b>'+t[1]+'</b>')); });
  mseg.appendChild(segBtn('ALL','Not sure','txt'));
  function paintSeg(){ [seg,mseg].forEach(function(g){ [].forEach.call(g.children,function(b){ b.setAttribute('aria-pressed',b.getAttribute('data-t')===term?'true':'false'); }); }); paintMap(); }
  /* Sides tab: personal view for the side the person chose */
  function paintMap(){
    var S={T1:8,T2:9,T3:0};
    var R={T1:{T2:'Walk through the station by the central passage on the 1st floor'},T2:{T1:'Walk through the station by the central passage on the 1st floor'}};
    var personal=(term==='T1'||term==='T2');
    $('mLead').textContent=personal?('You are on the '+(term==='T1'?'Marunouchi':'Yaesu')+' side. Here is how to reach the other side.'):'Bullet train passengers: the Yaesu side is recommended.';
    [].forEach.call(document.querySelectorAll('#tmap .tlink'),function(e){ e.hidden=personal; });
    [].forEach.call(document.querySelectorAll('#tmap .tcard'),function(c){
      var id=c.getAttribute('data-t'), tb=c.querySelector('.tb');
      [].forEach.call(c.querySelectorAll('.heretag,.route'),function(e){ e.parentNode.removeChild(e); });
      c.classList.toggle('here',personal&&id===term);
      if(!personal) return;
      if(id===term){ var g=document.createElement('p'); g.className='heretag'; g.textContent='You are here'; tb.insertBefore(g,tb.firstChild); }
      else { var r=document.createElement('p'); r.className='route'; r.textContent='\\uD83D\\uDEB6 From here: '+R[term][id]; tb.appendChild(r); }
    });
  }
  paintSeg();
  /* need tiles */
  var tiles=$('tiles'), tiles2=$('tiles2'), track=$('track'), pager=$('pager'), page=0, offTimer=null;
  var MAIN=8;
  function pill(cls,iconTxt,label,sub,fn){
    var b=document.createElement('button'); b.type='button'; b.className='tile more'+(cls?' '+cls:'');
    var ic=document.createElement('span'); ic.className='ic'; ic.setAttribute('aria-hidden','true'); ic.textContent=iconTxt;
    var tx=document.createElement('span'); tx.className='tx'; tx.appendChild(document.createTextNode(label));
    var sm=document.createElement('small'); sm.textContent=sub; tx.appendChild(sm);
    b.appendChild(ic); b.appendChild(tx); b.addEventListener('click',fn); return b;
  }
  function slideTo(p){
    page=p; if(offTimer){ clearTimeout(offTimer); offTimer=null; }
    var on=p?tiles2:tiles, off=p?tiles:tiles2;
    on.classList.remove('off'); on.removeAttribute('aria-hidden'); on.inert=false;
    off.setAttribute('aria-hidden','true'); off.inert=true;
    track.style.transform='translateX('+(p?'-100%':'0')+')';
    offTimer=setTimeout(function(){ off.classList.add('off'); offTimer=null; },320);
  }
  tiles2.inert=true;
  var PH_TXT=' Phone charging: ask station staff where to find power outlets.';
  var phoneIt=['phone','Phone and Wi-Fi',{}];
  D.terms.forEach(function(t){ phoneIt[2][t[0]]=item('wifi')[2][t[0]]; });
  var trainsIt=['trains','Subway and buses',{}];
  var LIST=[];
  ['toilet','lockers','info','tickets','trains','help','baby','phone','food','unwell'].forEach(function(id){
    LIST.push(id==='trains'?trainsIt:id==='phone'?phoneIt:item(id));
  });
  LIST.forEach(function(it,n){
    var b=document.createElement('button'); b.type='button'; b.className='tile c'+(n%3); b.setAttribute('data-id',it[0]);
    var ic=document.createElement('span'); ic.className='ic'; ic.setAttribute('aria-hidden','true'); ic.textContent=ICON[it[0]]||'\\u2022';
    var tx=document.createElement('span'); tx.className='tx'; tx.textContent=SHORT[it[0]]||it[1];
    b.appendChild(ic); b.appendChild(tx);
    b.addEventListener('click',function(){ if(it[0]==='trains'){ openInfo(ICON.trains,it[1],trainHTML(),b); } else { openSheet(it,b); } });
    (n<MAIN?tiles:tiles2).appendChild(b);
    if(n===MAIN-1){ tiles.appendChild(pill('pgnext','\\u2192','More','Food and drink, feeling unwell',function(){ slideTo(1); })); }
  });
  tiles2.appendChild(pill('pgback','\\u2190','Back','Main places',function(){ slideTo(0); }));
  /* swipe between the two screens */
  (function(){
    var sx=0, sy=0, on=false;
    pager.addEventListener('touchstart',function(e){ if(e.touches.length!==1){on=false;return;} on=true; sx=e.touches[0].clientX; sy=e.touches[0].clientY; },{passive:true});
    pager.addEventListener('touchend',function(e){
      if(!on) return; on=false; var t=e.changedTouches[0], dx=t.clientX-sx, dy=t.clientY-sy;
      if(Math.abs(dx)>60 && Math.abs(dx)>1.6*Math.abs(dy)){ if(dx<0 && page===0) slideTo(1); else if(dx>0 && page===1) slideTo(0); }
    },{passive:true});
  })();
  /* answer sheet */
  var sheet=$('sheet'), scrim=$('scrim'), shT=$('shTitle'), shB=$('shBody');
  var NONE='We did not find this on the official station pages. Please ask station staff.';
  function ans(label,txt,mini){
    var d=document.createElement('div'); d.className='ans'+(mini?' mini':'');
    if(label){ var e=document.createElement('em'); e.textContent=label; d.appendChild(e); }
    d.appendChild(document.createTextNode(txt||NONE)); return d;
  }
  function openSheet(it,btn){
    lastTile=btn; shT.textContent=''; shB.textContent='';
    var ic=document.createElement('span'); ic.setAttribute('aria-hidden','true'); ic.textContent=ICON[it[0]]||''; shT.appendChild(ic);
    shT.appendChild(document.createTextNode(it[1]));
    if(term==='ALL'&&D.terms.every(function(t){return it[2][t[0]]===it[2][D.terms[0][0]];})){ shB.appendChild(ans('Both sides',it[2][D.terms[0][0]],false)); }
    else if(term==='ALL'){ D.terms.forEach(function(t){ shB.appendChild(ans(t[1],it[2][t[0]],true)); }); }
    else { var tn=D.terms.filter(function(t){return t[0]===term;})[0][1]; shB.appendChild(ans(tn,it[2][term],false)); }
    hideAll(); sheet.hidden=false; scrim.hidden=false; sheet.scrollTop=0; $('shClose').focus();
  }
  var inst=$('inst');
  function hideAll(){ sheet.hidden=true; inst.hidden=true; scrim.hidden=true; }
  function closeSheet(){ hideAll(); if(lastTile) lastTile.focus(); }
  $('shClose').addEventListener('click',closeSheet); scrim.addEventListener('click',closeSheet);
  document.addEventListener('keydown',function(e){ if(e.key==='Escape'&&(!sheet.hidden||!inst.hidden)) closeSheet(); });
  /* answer sheet for info tiles (static text only) */
  function openInfo(icon,title,html,btn){
    lastTile=btn||null; shT.textContent='';
    var ic=document.createElement('span'); ic.setAttribute('aria-hidden','true'); ic.textContent=icon; shT.appendChild(ic);
    shT.appendChild(document.createTextNode(title)); shB.innerHTML=html;
    hideAll(); sheet.hidden=false; scrim.hidden=false; sheet.scrollTop=0; $('shClose').focus();
  }
  function item(id){ return D.items.filter(function(i){return i[0]===id;})[0]; }
  var KLP=__KLP_JSON__;
  function klp(k,t){ return KLP[k]?'<p class="sm">'+t+' (partner link): <a href="'+KLP[k]+'" target="_blank" rel="sponsored nofollow noopener">Check the listing</a></p>':''; }
  function trainHTML(){
    var h='<p class="n2">Tokyo Station has many lines. Several share the platform numbers 1 to 4, so look for the line name as well as the number.</p>';
    h+='<ul class="pl"><li><b>Yamanote Line:</b> the loop line. It links Tokyo Station with Hamamatsucho, where you change for the monorail to Haneda.</li>'
      +'<li><b>Other JR lines:</b> Chuo Rapid, Keihin-Tohoku, Sobu Rapid, Yokosuka, Keiyo and Musashino (JNTO, JR East).</li>'
      +'<li><b>Tokyo Metro Marunouchi Line:</b> its own station, M17.</li>'
      +'<li><b>Otemachi:</b> long underground passages link Tokyo Station with Otemachi, where the Tozai, Chiyoda, Hanzomon and Toei Mita lines stop. It is a bit of a walk.</li>'
      +'<li><b>Buses:</b> JR Highway Bus Terminal at the Yaesu South Exit, and the Tekko Building terminal about 2 minutes from the Yaesu North Exit.</li></ul>';
    h+='<div class="tipbox">We did not find official fares or walking times for these routes. Check the operator.</div>';
    h+='<p class="sm">Source: JR East, JNTO and Tokyo Station City, checked 19 November 2026. Routes change. Check the operator.</p>';
    return h;
  }
  function sidesHTML(){
    return '<p class="n2">Tokyo Station has two main sides, joined by a central passage on the 1st floor. Both have North, Central and South gates, so say which side too.</p>'
      +'<ul class="pl"><li><b>Marunouchi side (west):</b> the red-brick building. The Narita Express route starts at the Marunouchi Central Gate. The JR East Travel Service Center is on your left after the Marunouchi North ticket gate. The Tokyo Station Hotel and Tokyo Station Gallery are here.</li>'
      +'<li><b>Yaesu side (east):</b> Tokyo Station City recommends it for Smart EX bullet train tickets. The airport limousine buses leave from the Yaesu North Exit. First Avenue, with Ramen Street, is underground.</li>'
      +'<li><b>Between the sides:</b> walk by the central passage on the 1st floor. Tokyo Station City says the Marunouchi side is about a 10-minute walk from the Yaesu side.</li></ul>';
  }
  function cardHTML(){
    return '<ul class="pl"><li><b>Welcome Suica:</b> lasts 28 days, no deposit. In principle one card per person. Load 1,000 to 10,000 yen when you buy it (JR East).</li>'
      +'<li>It works on trains, buses and in shops across Japan, but not in stores in the PiTaPa area.</li>'
      +'<li>Sold at the JR East Travel Service Center (left after the Marunouchi North ticket gate), at JAPAN RAIL CAFE TOKYO on the Yaesu side, and by machines at Narita and Haneda airports.</li>'
      +'<li>It can pay for a coin locker and unlock it.</li>'
      +'<li>JNTO also lists the TOURIST PASMO as a deposit-free card for visitors.</li>'
      +'<li>The JR TOKYO Wide Pass is not valid on the Tokaido Shinkansen.</li></ul>'
      +klp('klook-tokyo-station-suica','Tokyo IC card listing')
      +'<p class="sm">Source: JR East and JNTO, checked 19 November 2026. Rules and prices change. Check before you buy.</p>';
  }
  function bagsHTML(){
    return '<ul class="pl"><li><b>Coin lockers:</b> around the station. Tokyo Station City links to a locker search tool. Big-station lockers fill up fast (JNTO).</li>'
      +'<li><b>JR East Travel Service Center:</b> keeps luggage for the day only. On your left after the Marunouchi North ticket gate, 1F. Check JR East for hours.</li>'
      +'<li><b>Sending a bag to your hotel:</b> check JR East&rsquo;s page for the delivery counter.</li>'
      +'<li><b>Big bags on the Shinkansen:</b> on the Tokaido and Sanyo lines, over 160 cm (sum of three sides) up to 250 cm needs a seat with an oversized baggage area, reserved in advance. 160 cm or less goes on the racks or the deck. JR East&rsquo;s lines have no designated seats for oversized luggage.</li>'
      +'<li>Write down your hotel name, address and phone number. Keep medicines, valuables and chargers with you.</li></ul>'
      +klp('klook-tokyo-station-luggage','Luggage storage listing')
      +'<p class="sm">We did not find official locker prices, so we give none. Hours change.</p>';
  }
  function simHTML(){
    return '<ul class="pl"><li><b>eSIM:</b> install it on your phone and switch it on when you need it. No counter, no queue.</li>'
      +'<li><b>Free Wi-Fi:</b> JR East lists free Wi-Fi at the Travel Service Center.</li>'
      +'<li>We did not find an official list of SIM or Wi-Fi rental counters at Tokyo Station.</li></ul>';
  }
  function onwardHTML(){
    return '<ul class="pl"><li><b>Kyoto and Osaka:</b> Tokaido Shinkansen, platforms 14 to 19. About 130 min to Kyoto on the fastest trains (JR Central).</li>'
      +'<li><b>Tokyo Disney Resort:</b> Keiyo or Musashino Line to Maihama, about 15 min (Tokyo Disney Resort). Disneyland is a short walk. For DisneySea, change at Resort Gateway to the Disney Resort Line. We did not find a walking time from the Keiyo platform.</li>'
      +'<li><b>Narita Airport:</b> Narita Express, about an hour, all seats reserved.</li>'
      +'<li><b>Haneda Airport:</b> Yamanote Line to Hamamatsucho, then the Tokyo Monorail, 13 min on the express to Terminal 3.</li>'
      +'<li><b>Mount Fuji and Kawaguchiko:</b> buses from Tokyo Station are listed by JNTO. Times and fares not confirmed.</li></ul>'
      +klp('klook-tokyo-station-disney','Tokyo Disney Resort tickets')
      +'<p class="sm">Times are approximate and change. Check the operator.</p>'
      +'<p class="sm"><a href="/blog/narita-airport-guide">Our Narita Airport guide</a> and <a href="/blog/haneda-airport-guide">Haneda Airport guide</a> (need internet)</p>';
  }
  var NEXT=[['🚆','Trains and Metro',trainHTML],['🧭','Marunouchi or Yaesu?',sidesHTML],['🎫','Passes and paying',cardHTML],['🧳','Luggage',bagsHTML],['📱','Phone data',simHTML],['🗺️','Onward trips',onwardHTML]];
  var at=$('arrTiles');
  NEXT.forEach(function(n,k){
    var b=document.createElement('button'); b.type='button'; b.className='tile c'+(k%3);
    var ic=document.createElement('span'); ic.className='ic'; ic.setAttribute('aria-hidden','true'); ic.textContent=n[0];
    var tx=document.createElement('span'); tx.className='tx'; tx.textContent=n[1]; b.appendChild(ic); b.appendChild(tx);
    b.addEventListener('click',function(){ openInfo(n[0],n[1],n[2](),b); }); at.appendChild(b);
  });
  /* tick-off steps for arrival and departure */
  var doneA=[], doneD=[];
  function renderSteps(ol,list,done){
    ol.innerHTML='';
    list.forEach(function(st,i){
      var li=document.createElement('li'), b=document.createElement('button'); b.type='button'; b.className='stp'; b.setAttribute('aria-pressed',done[i]?'true':'false');
      var n=document.createElement('span'); n.className='n'; n.textContent=done[i]?'✓':String(i+1);
      var tx=document.createElement('span'); tx.className='tx'; var bb=document.createElement('b'); bb.textContent=st[0]; tx.appendChild(bb);
      tx.appendChild(document.createTextNode(typeof st[1]==='function'?st[1]():st[1]));
      b.appendChild(n); b.appendChild(tx);
      b.addEventListener('click',function(){ done[i]=!done[i]; b.setAttribute('aria-pressed',done[i]?'true':'false'); n.textContent=done[i]?'✓':String(i+1); syncReset(); });
      li.appendChild(b); ol.appendChild(li);
    });
  }
  function syncReset(){ $('arrReset').hidden=!doneA.some(Boolean); $('depReset').hidden=!doneD.some(Boolean); }
  var ARR=[['Find your side','Bullet trains: platforms 14 to 23, and the Yaesu side is recommended for Smart EX. The Narita Express route starts on the Marunouchi side.'],
    ['Ticket gate','Put your ticket through the gate. For the Shinkansen, look for the blue ticket gates on the 1st floor.'],
    ['Check the board','Check your platform on the board inside the gate. Several lines share platform numbers 1 to 4, so read the line name too.'],
    ['Need help or storage','JR East Travel Service Center: left after the Marunouchi North ticket gate, 1F. It keeps bags for the day only.']];
  var DEP=[['Know your platform','Tokaido and Sanyo Shinkansen: platforms 14 to 19. Tohoku, Joetsu and Hokuriku: 20 to 23. Narita Express: usually 3 or 4, underground.'],
    ['Pick your side','Yaesu side for bullet trains and airport buses. Marunouchi Central Gate for the Narita Express (down to B1, B4, then B5).'],
    ['Bags','Coin lockers are around the station. The Travel Service Center keeps bags for the day only.'],
    ['Allow walking time','The two sides are about a 10-minute walk apart (Tokyo Station City). Add a buffer with luggage.'],
    ['Go to your platform','Check the display for your train, and your ticket for your car and seat. Wait at your car number.']];
  function renderDep(){ renderSteps($('depSteps'),DEP,doneD); }
  renderSteps($('arrSteps'),ARR,doneA); renderDep();
  $('arrReset').addEventListener('click',function(){ doneA.length=0; renderSteps($('arrSteps'),ARR,doneA); syncReset(); });
  $('depReset').addEventListener('click',function(){ doneD.length=0; renderDep(); syncReset(); });
  /* departure: before you go */
  var GUIDE='__GUIDE_URL__';
  function more(a){ return '<p class="sm"><a href="'+GUIDE+a+'">More in the full guide</a> (needs internet)</p>'; }
  function shinHTML(){
    return '<p class="n2">Bullet trains leave Tokyo Station from <b>platforms 14 to 23</b>.</p>'
      +'<ul class="pl"><li><b>14 to 19:</b> Tokaido and Sanyo Shinkansen (JR Central), toward Nagoya, Kyoto, Shin-Osaka, Hiroshima and Hakata.</li>'
      +'<li><b>20 to 23:</b> Tohoku, Joetsu and Hokuriku Shinkansen (JR East), toward Sendai, Nagano, Echigo-Yuzawa and Kanazawa.</li>'
      +'<li>On the 1st floor, head toward the central information counter along the central passage, look for the blue ticket gates, and check the platform on the board inside the gate.</li>'
      +'<li>Tokyo Station City recommends the Yaesu side for Smart EX tickets.</li>'
      +'<li>Tokyo to Kyoto is about 130 min on the fastest trains.</li></ul>'
      +klp('klook-tokyo-station-shinkansen','Tokyo to Kyoto and Osaka bullet train tickets')
      +'<p class="sm">Source: Tokyo Station City and JR Central, checked 19 November 2026.</p>'
      +'<p class="sm"><a href="'+GUIDE+'#shinkansen">More in the full guide</a> (needs internet)</p>';
  }
  function passHTML(){
    return '<ul class="pl"><li><b>Tickets and passes:</b> the JR East Travel Service Center exchanges and sells passes and tickets.</li>'
      +'<li><b>Booking the Tokaido Shinkansen:</b> JR East&rsquo;s reservation service cannot book the Tokaido and Sanyo lines. Use JR Central&rsquo;s Smart EX or a ticket office.</li>'
      +'<li><b>JR TOKYO Wide Pass:</b> not valid on the Tokaido Shinkansen.</li>'
      +'<li><b>Reserved seats:</b> non-reserved tickets are valid on the day of purchase, but trains such as the Hayabusa and Hayate are all reserved (JR East).</li></ul>'
      +'<p class="sm">Hours and prices change. Confirm with JR East or JR Central.</p>';
  }
  function airportHTML(){
    return '<ul class="pl"><li><b>Narita Express:</b> from the Marunouchi Central Gate, down to B1, then B4, then B5. Usually platform 3 or 4. All seats reserved. About an hour to Narita.</li>'
      +'<li>The Narita-bound platform also serves a regular rapid train. Board the N&rsquo;EX.</li>'
      +'<li>JR East&rsquo;s timetables also show some N&rsquo;EX trains on tracks 1 and 2. Check the board.</li>'
      +'<li><b>Haneda:</b> Yamanote Line to Hamamatsucho, then the Tokyo Monorail, 13 min on the express to Terminal 3.</li>'
      +'<li><b>Airport Limousine Bus:</b> from the Yaesu North Exit (Tekko Building), to Haneda and Narita.</li></ul>'
      +klp('klook-tokyo-station-nex','Narita Express tickets')
      +klp('klook-tokyo-station-limousine','Airport Limousine Bus tickets')
      +'<div class="tipbox">We did not confirm last-train or first-train times. Check the timetable the day before a very early or late flight.</div>'
      +'<p class="sm">Times are approximate and change. Check the operator.</p>'
      +'<p class="sm"><a href="/blog/narita-airport-guide">Our Narita Airport guide</a> and <a href="/blog/haneda-airport-guide">Haneda Airport guide</a> (need internet)</p>';
  }
  function allowHTML(){
    return '<p class="n2">Tokyo Station is huge. Add a buffer for walking, gates and luggage.</p>'
      +'<ul class="pl"><li>The Marunouchi and Yaesu sides are about a 10-minute walk apart (Tokyo Station City).</li>'
      +'<li>The Narita Express platforms are underground: B1, then B4, then B5.</li>'
      +'<li>Several lines share platform numbers 1 to 4. Read the line name.</li>'
      +'<li>We did not find official walking times between gates and platforms, so we give none.</li>'
      +'<li>Last trains: we did not confirm times. Check the timetable before a late journey.</li></ul>'
      +'<p class="sm">Times are approximate and change. Check the operator.</p>';
  }
  var BEFORE=[['🚅','Catching a Shinkansen',shinHTML],['🎫','Tickets and passes',passHTML],['✈️','To the airports',airportHTML],['⏱️','Allow time',allowHTML]];
  var dtl=$('depTiles');
  BEFORE.forEach(function(n,k){
    var b=document.createElement('button'); b.type='button'; b.className='tile c'+(k%3);
    var ic=document.createElement('span'); ic.className='ic'; ic.setAttribute('aria-hidden','true'); ic.textContent=n[0];
    var tx=document.createElement('span'); tx.className='tx'; tx.textContent=n[1]; b.appendChild(ic); b.appendChild(tx);
    b.addEventListener('click',function(){ openInfo(n[0],n[1],n[2](),b); }); dtl.appendChild(b);
  });
  var dseg=$('depSeg');
  function paintDep(w){
    [].forEach.call(dseg.children,function(b){ b.setAttribute('aria-pressed',b.getAttribute('data-d')===w?'true':'false'); });
    $('depBefore').hidden=(w!=='before'); $('depAir').hidden=(w!=='air'); $('panels').scrollTop=0;
  }
  [].forEach.call(dseg.children,function(b){ b.addEventListener('click',function(){ var w=b.getAttribute('data-d'); try{localStorage.setItem('tokDepSeg',w);}catch(e){} paintDep(w); }); });
  var dsv='before'; try{ var q=localStorage.getItem('tokDepSeg'); if(q==='air'||q==='before') dsv=q; }catch(e){}
  paintDep(dsv);
  /* tabs */
  var tabs=[].slice.call(document.querySelectorAll('.tabs button'));
  function go(name,focus){
    hideAll();
    tabs.forEach(function(b){ var on=b.getAttribute('data-tab')===name; b.setAttribute('aria-selected',on?'true':'false'); b.tabIndex=on?0:-1; $('p-'+(b.getAttribute('data-tab')==='arrive'?'arrive':b.getAttribute('data-tab'))).hidden=!on; });
    $('panels').scrollTop=0;
    try{ history.replaceState(null,'','#'+name); }catch(e){}
    if(focus){ var cur=tabs.filter(function(b){return b.getAttribute('data-tab')===name;})[0]; if(cur) cur.focus(); }
  }
  tabs.forEach(function(b,i){
    b.addEventListener('click',function(){ go(b.getAttribute('data-tab')); });
    b.addEventListener('keydown',function(e){ var d=e.key==='ArrowRight'?1:e.key==='ArrowLeft'?-1:0; if(d){ e.preventDefault(); go(tabs[(i+d+tabs.length)%tabs.length].getAttribute('data-tab'),true); } });
  });
  var h=(location.hash||'').replace('#',''); go(/^(find|map|arrive|depart|help)$/.test(h)?h:'find');
  /* offline status and install */
  var st=$('status'), saved=false;
  function paint(){
    if(!navigator.onLine){ st.className='status off'; st.textContent=saved?'Offline: saved copy':'Offline'; }
    else if(saved){ st.className='status saved'; st.textContent='Saved for offline use'; }
    else { st.className='status'; st.textContent='Online'; }
  }
  window.addEventListener('online',paint); window.addEventListener('offline',paint); paint();
  if('serviceWorker' in navigator){
    navigator.serviceWorker.register('/tokyo-sw.js',{scope:'/tokyo-pocket',updateViaCache:'none'})
      .then(function(){ return navigator.serviceWorker.ready; })
      .then(function(){ return caches.has('tokyo-pocket-v1'); })
      .then(function(ok){ saved=!!ok; if(!saved){ setTimeout(function(){ caches.has('tokyo-pocket-v1').then(function(k){ saved=!!k; paint(); }); },2500);} paint(); })
      .catch(function(){ paint(); });
  }
  /* install help: shown first, in the person's own phone type */
  var ua=navigator.userAgent||'';
  var isIOS=/iPad|iPhone|iPod/.test(ua)||(navigator.platform==='MacIntel'&&navigator.maxTouchPoints>1);
  var isAnd=/Android/.test(ua);
  var mobile=isIOS||isAnd;
  var standalone=!!(window.navigator.standalone||(window.matchMedia&&window.matchMedia('(display-mode: standalone)').matches));
  function flag(k,v){ try{ if(v===undefined) return localStorage.getItem(k); localStorage.setItem(k,v); }catch(e){} return null; }
  var strip=$('instStrip'), dp=null;
  function needed(){ return mobile&&!standalone&&flag('tokInstalled')!=='1'; }
  function refresh(){
    var n=needed(); strip.hidden=!n;
    $('instHow').hidden=!n; $('instDesk').hidden=mobile;
    if(standalone||flag('tokInstalled')==='1'){ $('install').hidden=true; }
  }
  var SHARE='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3v12"/><path d="M8 7l4-4 4 4"/><path d="M6 11H5a1 1 0 0 0-1 1v8a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-8a1 1 0 0 0-1-1h-1"/></svg>';
  var PLUS='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><rect x="4" y="4" width="16" height="16" rx="3"/><path d="M12 8v8M8 12h8"/></svg>';
  var DOTS='<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><circle cx="12" cy="5" r="2"/><circle cx="12" cy="12" r="2"/><circle cx="12" cy="19" r="2"/></svg>';
  var DOWN='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 4v11"/><path d="M7 11l5 5 5-5"/><path d="M5 20h14"/></svg>';
  function steps(list){ return '<ol class="istep">'+list.map(function(x,i){ return '<li><span class="n">'+(i+1)+'</span>'+x[0]+'<span>'+x[1]+'</span></li>'; }).join('')+'</ol>'; }
  function openInst(){
    pgTrack('pg_install_view',{via:instVia}); instVia='help';
    var h='<p class="lede">Do this once, now, while you have signal. Then it opens like an app, even with no internet.</p>';
    if(isIOS){
      h+=steps([[SHARE,'Tap the <b>Share</b> button (a square with an arrow) in Safari'],[PLUS,'Scroll down and tap <b>Add to Home Screen</b>'],['','Tap <b>Add</b>']]);
      h+='<div class="tipbox">Cannot see Share? Tap the <b>&middot;&middot;&middot;</b> button first. Not in Safari (for example Chrome, Instagram or Facebook)? Open this page in <b>Safari</b> first.</div>';
    } else if(dp){
      h+='<button type="button" class="close" id="instGo">Install now</button>';
      h+='<div class="tipbox">Or tap the menu <b>&#8942;</b> in Chrome, then <b>Install app</b> or <b>Add to Home screen</b>.</div>';
    } else {
      h+=steps([[DOTS,'Tap the menu <b>&#8942;</b> (three dots) in Chrome'],[DOWN,'Tap <b>Install app</b> or <b>Add to Home screen</b>'],['','Tap <b>Install</b> or <b>Add</b>']]);
      h+='<div class="tipbox">Do not see it? Open this page in Chrome and try again.</div>';
    }
    h+='<div class="row2"><button type="button" class="close ghost" id="instLater">Later</button><button type="button" class="close" id="instDone">I added it</button></div>';
    $('instBody').innerHTML=h;
    lastTile=document.activeElement&&document.activeElement.focus?document.activeElement:null;
    hideAll(); inst.hidden=false; scrim.hidden=false; inst.scrollTop=0;
    var go=$('instGo'); if(go){ go.addEventListener('click',function(){ if(!dp) return; dp.prompt(); try{ dp.userChoice.then(function(r){ if(r&&r.outcome) pgTrack('pg_install_prompt',{outcome:r.outcome}); if(r&&r.outcome==='accepted') markInstalled(); }); }catch(e){} dp=null; closeSheet(); }); }
    $('instLater').addEventListener('click',closeSheet);
    $('instDone').addEventListener('click',function(){ markInstalled(); closeSheet(); });
    (go||$('instDone')).focus();
  }
  function markInstalled(){ flag('tokInstalled','1'); refresh(); }
  strip.addEventListener('click',function(){ instVia='strip'; openInst(); });
  $('instBtn').addEventListener('click',function(){ instVia='help'; openInst(); });
  /* show this to staff */
  var ASK=[
    ['basics','👋','Hello','こんにちは。','Konnichiwa.','Hello.'],
    ['basics','🙏','Thank you','ありがとうございます。','Arigatou gozaimasu.','Thank you very much.'],
    ['basics','🙇','Excuse me','すみません。','Sumimasen.','Excuse me. Or: I am sorry.'],
    ['basics','👌','No thanks','大丈夫です。','Daijoubu desu.','I am fine, no thank you.'],
    ['basics','❓','I do not understand','分かりません。','Wakarimasen.','I do not understand.'],
    ['basics','🐢','Slowly, please','ゆっくりお願いします。','Yukkuri onegai shimasu.','Please speak slowly.'],
    ['basics','🔁','Once more','もう一度お願いします。','Mou ichido onegai shimasu.','One more time, please.'],
    ['basics','⏳','One moment','ちょっと待ってください。','Chotto matte kudasai.','Please wait a moment.'],
    ['basics','✍️','Write it down','書いてください。','Kaite kudasai.','Please write it down.'],
    ['basics','🗣️','English?','英語を話せる人はいますか？','Eigo o hanaseru hito wa imasu ka?','Is there someone who speaks English?'],
    ['where','🚻','Toilet','トイレはどこですか？','Toire wa doko desu ka?','Where is the toilet?'],
    ['where','🚪','Exit','出口はどこですか？','Deguchi wa doko desu ka?','Where is the exit?'],
    ['where','➡️','Entrance','入口はどこですか？','Iriguchi wa doko desu ka?','Where is the entrance?'],
    ['where','🛗','Lift','エレベーターはどこですか？','Erebeetaa wa doko desu ka?','Where is the lift?'],
    ['where','☕','Coffee','コーヒーはどこですか？','Koohii wa doko desu ka?','Where is the coffee?'],
    ['where','💧','Water','お水はどこですか？','Omizu wa doko desu ka?','Where is the water?'],
    ['where','🏪','Konbini','コンビニはどこですか？','Konbini wa doko desu ka?','Where is a convenience store?'],
    ['where','🍜','Food','食事ができる所はどこですか？','Shokuji ga dekiru tokoro wa doko desu ka?','Where can I eat?'],
    ['where','🏧','ATM','ATMはどこですか？','Eetiiemu wa doko desu ka?','Where is an ATM?'],
    ['where','🔐','Coin locker','コインロッカーはどこですか？','Koin rokkaa wa doko desu ka?','Where are the coin lockers?'],
    ['where','ℹ️','Information','案内所はどこですか？','Annaijo wa doko desu ka?','Where is the information counter?'],
    ['where','💊','Pharmacy','薬局はどこですか？','Yakkyoku wa doko desu ka?','Where is a pharmacy?'],
    ['shop','💴','How much?','いくらですか？','Ikura desu ka?','How much is it?'],
    ['shop','👉','This one','これをください。','Kore o kudasai.','This one, please.'],
    ['shop','💳','Card OK?','カードは使えますか？','Kaado wa tsukaemasu ka?','Can I pay by card?'],
    ['shop','♨️','Heat it up','温めてください。','Atatamete kudasai.','Please heat it up.'],
    ['shop','🛍️','A bag, please','袋をください。','Fukuro o kudasai.','A bag, please.'],
    ['shop','🙅','No bag','袋はいりません。','Fukuro wa irimasen.','I do not need a bag.'],
    ['shop','🧾','Receipt','レシートをください。','Reshiito o kudasai.','A receipt, please.'],
    ['shop','🏷️','Tax-free?','免税で買えますか？','Menzei de kaemasu ka?','Can I buy this tax-free?'],
    ['shop','👗','Fitting room','試着室はどこですか？','Shichakushitsu wa doko desu ka?','Where is the fitting room?'],
    ['shop','📏','Bigger size?','もっと大きいサイズはありますか？','Motto ookii saizu wa arimasu ka?','Do you have a bigger size?'],
    ['eat','👥','Two people','二人です。','Futari desu.','Two people.'],
    ['eat','👤','One person','一人です。','Hitori desu.','One person.'],
    ['eat','📖','Menu, please','メニューをください。','Menyuu o kudasai.','The menu, please.'],
    ['eat','🔤','English menu?','英語のメニューはありますか？','Eigo no menyuu wa arimasu ka?','Do you have an English menu?'],
    ['eat','🥤','Water, please','お水をください。','Omizu o kudasai.','Water, please.'],
    ['eat','🍴','A fork','フォークをください。','Fooku o kudasai.','A fork, please.'],
    ['eat','🧾','The bill','お会計をお願いします。','Okaikei o onegai shimasu.','The bill, please.'],
    ['eat','😋','Delicious','おいしいです。','Oishii desu.','It is delicious.'],
    ['eat','🌶️','Not spicy?','辛くないものはありますか？','Karakunai mono wa arimasu ka?','Do you have something not spicy?'],
    ['eat','🥗','No meat or fish','肉と魚は食べません。','Niku to sakana wa tabemasen.','I do not eat meat or fish.'],
    ['eat','⚠️','Food allergy','食物アレルギーがあります。','Shokumotsu arerugii ga arimasu.','I have a food allergy. Write or point to what you cannot eat.'],
    ['sights','🎟️','Ticket counter','チケット売り場はどこですか？','Chiketto uriba wa doko desu ka?','Where is the ticket counter?'],
    ['sights','⏱️','Wait time','待ち時間はどのくらいですか？','Machijikan wa dono kurai desu ka?','How long is the wait?'],
    ['sights','🚶','End of the line','列の最後尾はどこですか？','Retsu no saikoubi wa doko desu ka?','Where is the end of the line?'],
    ['sights','📸','Photo, please','写真を撮っていただけますか？','Shashin o totte itadakemasu ka?','Could you take a photo of us?'],
    ['sights','🕒','Open until?','何時まで開いていますか？','Nanji made aite imasu ka?','Until what time is it open?'],
    ['sights','🪑','Place to rest','休める所はどこですか？','Yasumeru tokoro wa doko desu ka?','Where can I rest?'],
    ['sights','🗺️','Map, please','地図をください。','Chizu o kudasai.','A map, please.'],
    ['sights','👶','Stroller','ベビーカーを借りられますか？','Bebiikaa o kariraremasu ka?','Can I rent a stroller?'],
    ['sights','♿','Wheelchair rental','車いすを借りられますか？','Kuruma-isu o kariraremasu ka?','Can I rent a wheelchair?'],
    ['sights','📦','Lost and found','落とし物の窓口はどこですか？','Otoshimono no madoguchi wa doko desu ka?','Where is the lost and found?'],
    ['go','🗺️','Show on map','この場所へはどう行けばいいですか？','Kono basho e wa dou ikeba ii desu ka?','How do I get to this place? Show it on your phone.'],
    ['go','🥾','Is it far?','遠いですか？','Tooi desu ka?','Is it far?'],
    ['go','🚉','Nearest station','一番近い駅はどこですか？','Ichiban chikai eki wa doko desu ka?','Where is the nearest station?'],
    ['go','🔢','Which platform?','何番ホームですか？','Nanban hoomu desu ka?','Which platform is it?'],
    ['go','🎫','Buy a ticket','切符はどこで買えますか？','Kippu wa doko de kaemasu ka?','Where can I buy a ticket?'],
    ['go','🌙','Last train','終電は何時ですか？','Shuuden wa nanji desu ka?','What time is the last train?'],
    ['go','🏙️','Shinjuku?','これは新宿に行きますか？','Kore wa Shinjuku ni ikimasu ka?','Does this go to Shinjuku?'],
    ['go','🛍️','Shibuya?','これは渋谷に行きますか？','Kore wa Shibuya ni ikimasu ka?','Does this go to Shibuya?'],
    ['go','✈️','Haneda Airport?','これは羽田空港に行きますか？','Kore wa Haneda-kuukou ni ikimasu ka?','Does this go to Haneda Airport?'],
    ['go','🛫','Narita Airport?','これは成田空港に行きますか？','Kore wa Narita-kuukou ni ikimasu ka?','Does this go to Narita Airport?'],
    ['go','🎢','Maihama Station?','これは舞浜駅に行きますか？','Kore wa Maihama-eki ni ikimasu ka?','Does this go to Maihama Station (Tokyo Disney Resort)?'],
    ['go','📞','Call a taxi','タクシーを呼んでください。','Takushii o yonde kudasai.','Please call a taxi.'],
    ['go','📍','Take me here','この住所までお願いします。','Kono juusho made onegai shimasu.','Please take me to this address. Show the address on your phone.'],
    ['go','🛑','Stop here','ここで止めてください。','Koko de tomete kudasai.','Please stop here.'],
    ['air','🎫','Ticket gate','改札はどこですか？','Kaisatsu wa doko desu ka?','Where is the ticket gate?'],
    ['air','🚅','Shinkansen platform','新幹線のホームはどこですか？','Shinkansen no hoomu wa doko desu ka?','Where is the Shinkansen platform?'],
    ['air','🧳','Coin lockers','コインロッカーはどこですか？','Koin rokkaa wa doko desu ka?','Where are the coin lockers?'],
    ['air','🚪','Exit','出口はどこですか？','Deguchi wa doko desu ka?','Where is the exit?'],
    ['air','ℹ️','Information desk','案内所はどこですか？','Annaijo wa doko desu ka?','Where is the information desk?'],
    ['air','📩','Collect my ticket','予約した切符を受け取りたいです。','Yoyaku shita kippu o uketoritai desu.','I want to collect my reserved ticket.'],
    ['air','🚕','Taxi stand','タクシー乗り場はどこですか？','Takushii noriba wa doko desu ka?','Where is the taxi stand?'],
    ['air','⏰','Missed my train','電車に乗り遅れました。','Densha ni noriokuremashita.','I missed my train.'],
    ['help','🆘','Help me','すみません、助けてください。','Sumimasen, tasukete kudasai.','Excuse me, please help me.'],
    ['help','🤒','I feel sick','具合が悪いです。助けてください。','Guai ga warui desu. Tasukete kudasai.','I feel sick. Please help me.'],
    ['help','🚑','Ambulance','救急車を呼んでください。','Kyuukyuusha o yonde kudasai.','Please call an ambulance.'],
    ['help','🚓','Police','警察を呼んでください。','Keisatsu o yonde kudasai.','Please call the police.'],
    ['help','🏥','Hospital','病院はどこですか？','Byouin wa doko desu ka?','Where is a hospital?'],
    ['help','💊','Need medicine','薬が欲しいです。','Kusuri ga hoshii desu.','I need medicine.'],
    ['help','♿','Wheelchair','車いすをお願いします。','Kuruma-isu o onegai shimasu.','A wheelchair, please.'],
    ['help','🛂','Lost passport','パスポートをなくしました。','Pasupooto o nakushimashita.','I lost my passport.'],
    ['help','👛','Lost wallet','財布をなくしました。','Saifu o nakushimashita.','I lost my wallet.'],
    ['help','📱','Lost phone','スマホをなくしました。','Sumaho o nakushimashita.','I lost my phone.'],
    ['help','🧳','Lost bag','かばんをなくしました。','Kaban o nakushimashita.','I lost my bag.'],
    ['help','🧒','Lost child','子どもがいなくなりました。助けてください。','Kodomo ga inaku narimashita. Tasukete kudasai.','My child is missing. Please help me.']];
  var ASKC=[['basics','Basics','👋'],['where','Where is&hellip;?','📍'],['shop','Shopping','🛍️'],['eat','Eating out','🍜'],['sights','Sights','🎡'],['go','Getting around','🚆'],['air','Station','🚉'],['help','Help','🆘']];
  var askCat='basics'; try{ var sc=localStorage.getItem('tokAskCat'); if(sc&&ASKC.some(function(c){return c[0]===sc;})) askCat=sc; }catch(e){}
  var askT=$('askTiles'), askC=$('askCats');
  function jaVoices(){ try{ return window.speechSynthesis.getVoices().filter(function(v){return /^ja/i.test(v.lang);}); }catch(e){ return []; } }
  function canSpeak(){ try{ if(!('speechSynthesis' in window)||typeof SpeechSynthesisUtterance==='undefined') return false; var all=window.speechSynthesis.getVoices(); return !all.length||jaVoices().length>0; }catch(e){ return false; } }
  function speakJp(txt){ try{ var ss=window.speechSynthesis; ss.cancel(); var u=new SpeechSynthesisUtterance(txt); u.lang='ja-JP'; u.rate=0.85; var vs=jaVoices(); if(vs.length) u.voice=vs[0]; ss.speak(u); }catch(e){} }
  try{ window.speechSynthesis.getVoices(); window.speechSynthesis.addEventListener('voiceschanged',function(){}); }catch(e){}
  function paintAsk(){
    [].forEach.call(askC.children,function(b){ b.setAttribute('aria-pressed',b.getAttribute('data-c')===askCat?'true':'false'); });
    askT.textContent=''; var n=0;
    ASK.filter(function(a){return a[0]===askCat;}).forEach(function(a){
      var b=document.createElement('button'); b.type='button'; b.className='tile c'+(n++%3);
      var ic=document.createElement('span'); ic.className='ic'; ic.setAttribute('aria-hidden','true'); ic.textContent=a[1];
      var tx=document.createElement('span'); tx.className='tx'; tx.textContent=a[2];
      b.appendChild(ic); b.appendChild(tx);
      b.addEventListener('click',function(){
        var h='<p class="jp"></p><p class="rom"></p><p class="en2"></p>'+(canSpeak()?'<p><button type="button" class="big" id="playJp" style="width:100%;font-size:1.15rem">&#128266; Play</button></p>':'');
        openInfo(a[1],'Show this, or play it',h,b);
        var q=shB.querySelectorAll('p'); q[0].textContent=a[3]; q[1].textContent=a[4]; q[2].textContent=a[5];
        var pb=$('playJp'); if(pb) pb.addEventListener('click',function(){ speakJp(a[3]); });
      });
      askT.appendChild(b);
    });
  }
  ASKC.forEach(function(c){
    var b=document.createElement('button'); b.type='button'; b.setAttribute('data-c',c[0]); var ci=document.createElement('span'); ci.className='ci'; ci.setAttribute('aria-hidden','true'); ci.textContent=c[2]; var cl=document.createElement('span'); cl.innerHTML=c[1]; b.appendChild(ci); b.appendChild(cl);
    b.addEventListener('click',function(){ askCat=c[0]; try{localStorage.setItem('tokAskCat',c[0]);}catch(e){} paintAsk(); });
    askC.appendChild(b);
  });
  paintAsk();
  /* Help: two screens (phrases, then phone numbers) */
  (function(){
    var hp1=$('hp1'), hp2=$('hp2'), htrack=$('htrack'), hpager=$('hpager'), hpage=0, hTimer=null;
    function hslide(p){
      hpage=p; if(hTimer){ clearTimeout(hTimer); hTimer=null; }
      var pn=document.querySelector('.panels'); if(pn) pn.scrollTop=0;
      var on=p?hp2:hp1, off=p?hp1:hp2;
      on.classList.remove('off'); on.removeAttribute('aria-hidden'); on.inert=false;
      off.setAttribute('aria-hidden','true'); off.inert=true;
      htrack.style.transform='translateX('+(p?'-100%':'0')+')';
      hTimer=setTimeout(function(){ off.classList.add('off'); hTimer=null; },320);
    }
    hp2.inert=true;
    $('hnav1').appendChild(pill('pgnext','\\u2192','Phone numbers','Emergency, station, help line',function(){ hslide(1); }));
    $('hnav2').appendChild(pill('pgback','\\u2190','Back','Say it in Japanese',function(){ hslide(0); }));
    var sx=0, sy=0, on=false;
    hpager.addEventListener('touchstart',function(e){ if(e.touches.length!==1){on=false;return;} on=true; sx=e.touches[0].clientX; sy=e.touches[0].clientY; },{passive:true});
    hpager.addEventListener('touchend',function(e){
      if(!on) return; on=false; var t=e.changedTouches[0], dx=t.clientX-sx, dy=t.clientY-sy;
      if(Math.abs(dx)>60 && Math.abs(dx)>1.6*Math.abs(dy)){ if(dx<0 && hpage===0) hslide(1); else if(dx>0 && hpage===1) hslide(0); }
    },{passive:true});
  })();
  /* send this guide */
  if(navigator.share){
    $('shareCard').hidden=false;
    $('shareBtn').addEventListener('click',function(){ try{ navigator.share({title:'Tokyo Station Pocket Guide',url:location.origin+location.pathname+'?src=share'}); }catch(e){} });
  }
  window.addEventListener('beforeinstallprompt',function(e){ e.preventDefault(); dp=e; });
  window.addEventListener('appinstalled',function(){ pgTrack('pg_installed',{via:'browser'}); markInstalled(); if(!inst.hidden) closeSheet(); });
  /*__PG_HOOKS__*/
  refresh();
  if(needed()&&!flag('tokIntro')&&AUTO_INSTALL_SHEET){ flag('tokIntro','1'); setTimeout(function(){ if(sheet.hidden&&inst.hidden){ instVia='auto'; openInst(); } },700); }
})();
</script>
</body>
</html>
"""
POCKET_HTML = (POCKET_HTML.replace("__CSS__", POCKET_CSS).replace("__FINDER_JSON__", json.dumps(FINDER_DATA, ensure_ascii=False)).replace("__KLP_JSON__", json.dumps({k: v for k, v in KLK.items() if v}))
               .replace("__PG_BOOT__", PG_BOOT).replace("/*__PG_HOOKS__*/", PG_HOOKS).replace("__SVG__", POCKET_SVG).replace("__GUIDE_URL__", URL))
if re.search(r"\b(India|Indian|INR|Rs\.?|rupee|lakh|Aadhaar|UPI|VFS|BLS)\b|₹", re.sub(r"<script[^>]*>.*?</script>", "", POCKET_HTML, flags=re.S)):
    die("neutral-rule violation in the pocket guide")

POCKET_SW = """/* Tokyo Station Pocket Guide service worker. Bump V when the page changes shape. */
var V='tokyo-pocket-v1';
var PAGE='/tokyo-pocket';
var SHELL=[PAGE,'/tokyo-pocket.webmanifest','/favicon-32.png','/images/tokyo-icon-192.png','/images/tokyo-icon-512.png','/images/tokyo-icon-maskable-512.png'];
self.addEventListener('install',function(e){
  e.waitUntil(caches.open(V).then(function(c){return c.addAll(SHELL);}).then(function(){return self.skipWaiting();}));
});
self.addEventListener('activate',function(e){
  e.waitUntil(caches.keys().then(function(ks){
    return Promise.all(ks.filter(function(k){return k.indexOf('tokyo-pocket-')===0&&k!==V;}).map(function(k){return caches.delete(k);}));
  }).then(function(){return self.clients.claim();}));
});
function pageFirst(req){
  return new Promise(function(resolve){
    var done=false;
    function fromCache(){ return caches.match(PAGE).then(function(m){ if(m&&!done){done=true;resolve(m);} return m; }); }
    var t=setTimeout(fromCache,3000);
    fetch(req).then(function(res){
      clearTimeout(t);
      var cp=(res&&res.ok)?res.clone():null;
      if(!done){done=true;resolve(res);}
      if(cp){ caches.open(V).then(function(c){c.put(PAGE,cp);}); }
    }).catch(function(){
      clearTimeout(t);
      fromCache().then(function(m){ if(!m&&!done){done=true;resolve(Response.error());} });
    });
  });
}
self.addEventListener('fetch',function(e){
  var r=e.request;
  if(r.method!=='GET') return;
  var u=new URL(r.url);
  if(u.origin!==location.origin) return;
  if(r.mode==='navigate'){
    if(u.pathname!==PAGE) return;
    e.respondWith(pageFirst(r));
    return;
  }
  e.respondWith(caches.match(r).then(function(m){return m||fetch(r);}));
});
"""
POCKET_MANIFEST = json.dumps({
    "name": "Tokyo Station Pocket Guide",
    "short_name": "Tokyo",
    "description": "A simple Tokyo Station helper that works offline.",
    "start_url": POCKET_PATH,
    "scope": POCKET_PATH,
    "display": "standalone",
    "background_color": "#2e7d5b",
    "theme_color": "#1a1a3e",
    "lang": "en",
    "icons": [
        {"src": "/images/tokyo-icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
        {"src": "/images/tokyo-icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
        {"src": "/images/tokyo-icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ],
}, indent=2) + "\n"
PUB = os.path.join(ROOT, "public")
for _ic in ("tokyo-icon-192.png", "tokyo-icon-512.png", "tokyo-icon-maskable-512.png", "tokyo-apple-touch-180.png"):
    if not os.path.isfile(os.path.join(PUB, "images", _ic)):
        die("pocket guide icon missing: public/images/" + _ic + " (the service worker would fail to install without it)")
for _name, _content in (("tokyo-pocket.html", POCKET_HTML), ("tokyo-sw.js", POCKET_SW), ("tokyo-pocket.webmanifest", POCKET_MANIFEST)):
    _p = os.path.join(PUB, _name)
    _old = open(_p, encoding="utf-8").read() if os.path.isfile(_p) else None
    if _old != _content:
        open(_p, "w", encoding="utf-8").write(_content)
        changed.append("%s (%s bytes)" % (_name, len(_content.encode("utf-8"))))

# ---- link from the Japan guide (after the Kyoto city sentence)
MARK = "tokyo-station-guide link"
jp = open(TEMPLATE, encoding="utf-8").read()
if MARK not in jp:
    anchor = re.search(r'(<!-- kyoto-' + r'travel-guide link -->\s*<p>.*?</p>)', jp, re.S)
    if not anchor:
        die("anchor for the Japan guide link (Kyoto city sentence) not found: run the Kyoto city generator (w41) first")
    add = ('\n\n<!-- %s -->\n<p>Changing trains in Tokyo? Our <a href="/blog/%s">Tokyo Station guide</a> explains the Marunouchi and Yaesu sides, the Shinkansen and Narita Express platforms, '
           'local trains and the Metro, luggage lockers, and tourist information.</p>') % (MARK, SLUG)
    jp = jp.replace(anchor.group(1), anchor.group(1) + add, 1)
    open(TEMPLATE, "w", encoding="utf-8").write(jp)
    changed.append("japan-travel-packing-guide.html (link added)")

# ---- sitemap
sm = open(SITEMAP, encoding="utf-8").read()
orig = sm
if ("/blog/%s</loc>" % SLUG) not in sm:
    entry = ("  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.8</priority>\n  </url>\n") % (URL, TODAY)
    if "</urlset>" not in sm:
        die("sitemap has no </urlset>")
    sm = sm.replace("</urlset>", entry + "</urlset>", 1)
rx = re.compile(r"(<loc>%s/blog/japan-travel-packing-guide</loc>\s*<lastmod>)[^<]*(</lastmod>)" % re.escape(SITE))
if not rx.search(sm):
    die("sitemap entry for the Japan guide not found")
sm = rx.sub(r"\g<1>%s\g<2>" % TODAY, sm, count=1)
if sm != orig:
    open(SITEMAP, "w", encoding="utf-8").write(sm)
    changed.append("sitemap.xml")

print("changed:" if changed else "nothing to do (already applied)")
for c in changed:
    print("  - " + c)

