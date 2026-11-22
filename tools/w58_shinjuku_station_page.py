#!/usr/bin/env python3
"""
w58: new page /blog/shinjuku-station-guide + offline /shinjuku-pocket (neutral, plain-English station guide for Shinjuku Station).
Built from the Tokyo Station generator (w42), with the Pillow hero fallback from w36.

Run from the repo root (after w42):  python3 tools/w58_shinjuku_station_page.py
Then, as for the other guides: w44-w49 (pocket chain, cross-links, hub, trip picker), w55, w56, and w59 for the hub card.

Facts: ONLY from docs/research/shinjuku-sources.md (official pages, checked 22 November 2026). Anything not in that file
is written as "We did not find this on the official station pages. Please ask station staff." (_NONE). No new partner blocks:
only the Airalo eSIM block copied from the Japan guide (placement id renamed to *-shinjuku-station). KLK stays empty.

What it does (idempotent):
  1. Builds public/blog/shinjuku-station-guide.html from the site template taken from
     public/blog/japan-travel-packing-guide.html (head, CSS, nav, footer, tracking scripts)
     plus new body content and the Airalo eSIM block.
  2. Builds public/shinjuku-pocket.html (offline pocket guide), shinjuku-sw.js and shinjuku-pocket.webmanifest
     (cache shinjuku-pocket-v1; later scripts bump it; storage prefix "sjk", as w44 expects).
  3. Makes public/images/shinjuku-station-hero-1600.jpg from shinjuku-station-hero.jpg (sips on a Mac, Pillow elsewhere).
  4. Adds one sentence linking to the new page in the Japan guide (marker: shinjuku-station-guide link),
     right after the Tokyo Station guide sentence that w42 adds.
  5. Adds the page to public/sitemap.xml and bumps the Japan guide's lastmod.
It does NOT touch public/blog.html (the Travel Essentials hub card comes from w59).
Aborts without writing anything if an expected anchor is missing.
"""
import os, re, sys, json, html
from urllib.parse import quote

ROOT = os.getcwd()
BLOG = os.path.join(ROOT, "public", "blog")
SITEMAP = os.path.join(ROOT, "public", "sitemap.xml")
TEMPLATE = os.path.join(BLOG, "japan-travel-packing-guide.html")
OUT = os.path.join(BLOG, "shinjuku-station-guide.html")
SITE = "https://www.packsmartapp.com"
SLUG = "shinjuku-station-guide"
URL = "%s/blog/%s" % (SITE, SLUG)
TODAY = "2026-11-22"

TITLE = "Shinjuku Station Guide 2026: West vs East Exits, Platforms & Luggage | PackSmart"
H1 = "Shinjuku Station Guide 2026: West vs East Exits, Platforms and Luggage"
DESC = ("Plain-English Shinjuku Station guide: West or East exit, platforms 1 to 16, the last Narita Express, "
        "airport buses from Busta, ATMs and luggage.")
KEYWORDS = ("Shinjuku Station guide, Shinjuku Station west exit, Shinjuku Station east exit, Shinjuku Station platforms, "
            "last Narita Express Shinjuku, Busta Shinjuku, Shinjuku Station coin lockers, Shinjuku Station ATM, Shinjuku New South Gate, Odakyu Romancecar Shinjuku")

# ---- official sources (docs/research/shinjuku-sources.md), checked 22 November 2026
CHECKED = "Checked 22 November 2026."
SRC = {
    "jrmap": ("https://www.jreast.co.jp/en/e/stations/e866.html", "JR East station map"),
    "jrtsc": ("https://www.jreast.co.jp/en/multi/customer_support/service_center_shinjuku.html", "JR EAST Travel Service Center"),
    "nex": ("https://timetables.jreast.co.jp/en/2612/timetable/tt0866/0866120.html", "JR East Narita Express timetable (weekdays)"),
    "nex2": ("https://timetables.jreast.co.jp/en/2612/timetable/tt0866/0866121.html", "Saturdays and holidays"),
    "busta": ("https://shinjuku-busterminal.co.jp/en/service/", "Busta Shinjuku services"),
    "bustaacc": ("https://shinjuku-busterminal.co.jp/en/access/", "Busta Shinjuku access"),
    "tic": ("https://www.gotokyo.org/en/plan/tourist-info-center/index.html", "GO TOKYO Tourist Information Center"),
    "pdf": ("https://www.gotokyo.org/book/wp-content/uploads/2025/10/2510_sinjukueki_EN_low.pdf", "GO TOKYO Around Shinjuku Station map (PDF)"),
    "limo": ("https://www.limousinebus.co.jp/en/", "Airport Limousine Bus"),
    "limon": ("https://www.limousinebus.co.jp/en/timetable/detail/Narita-Shinjuku/?dir=2", "Narita timetable"),
    "limoh": ("https://www.limousinebus.co.jp/en/timetable/detail/Haneda-Shinjuku/?dir=2", "Haneda timetable"),
    "odakyu": ("https://odakyu-global.com/services/odakyu-sightseeing-service-center-west/", "Odakyu Sightseeing Service Center"),
    "romance": ("https://odakyu-global.com/passes/romancecar/", "Odakyu Romancecar"),
    "keio": ("https://www.keio.co.jp/english/", "Keio"),
    "metro": ("https://www.tokyometro.jp/lang_en/station/shinjuku/index.html", "Tokyo Metro Shinjuku Station"),
}


def a_src(k, label=None):
    u, n = SRC[k]
    return '<a href="%s" target="_blank" rel="noopener noreferrer">%s</a>' % (u, label or n)


def sources(keys, extra=""):
    parts = [a_src(k) for k in keys]
    s = parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " and " + parts[-1]
    return '<p class="ps-note">Sources: %s. %s%s</p>' % (s, CHECKED, (" " + extra) if extra else "")


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


airalo = block("airalo-japan").replace("airalo-japan", "airalo-shinjuku-station")
_a = "Install it before you fly, switch it on when you land. No airport SIM queue."
if _a not in airalo:
    die("airalo tagline not found")
airalo = airalo.replace(_a, "Install it on your phone and switch it on when you need it. No counter, no queue.")
# ---------------------------------------------------------------- body content
def esc(s):
    return html.escape(s, quote=False)


FAQ = [
    ("What time is the last Narita Express from Shinjuku?",
     "JR East's timetable (edition 2612) shows the last Narita Express from Shinjuku at 19:39, on weekdays and on Saturdays and holidays. The first is at 5:55. "
     "The trains run to Narita Airport Terminal 1, via Terminal 2·3, and JR East's station map shows them on platforms 5 and 6. "
     "One sample train leaves Shinjuku at 10:08 and reaches Terminal 1 at 11:27, about 80 minutes. Timetables change, so check JR East before you travel."),
    ("What if I miss the last Narita Express?",
     "The Airport Limousine Bus leaves from the Shinjuku Expressway Bus Terminal (Busta Shinjuku), 4th floor, to Narita and Haneda. "
     "We did not verify the last buses, so check the bus company's live timetable before you rely on one."),
    ("Which exit do I use for Busta Shinjuku and the airport buses?",
     "Use the JR New South Gate on the 2nd floor. Busta Shinjuku says the New South Gate is open from 5:45 to 24:00 and that outside those hours you should use the South Gate. "
     "Buses leave from the 4th floor and arrive on the 3rd floor."),
    ("Should I use the West exit or the East exit?",
     "The West side is for the Odakyū and Keiō lines, the Toei Shinjuku and Ōedo lines, the West exit bus stop and the Tokyo Metropolitan Government Building, about 10 minutes on foot from the west exit (GO TOKYO). "
     "The East side is for Kabukichō and Seibu-Shinjuku: the Godzilla head on the Shinjuku Toho Building is about 5 minutes from the east exit. "
     "Busta Shinjuku and the JR EAST Travel Service Center are by the New South Gate on the 2nd floor. The B1 Free Passage links the East and West sides outside the ticket gates."),
    ("Which platform is the Yamanote Line at Shinjuku?",
     "JR East's station map shows platform 14 for Harajuku, Shibuya and Shinagawa, and platform 15 for Ikebukuro, Tabata and Ueno."),
    ("Where can I leave my luggage at Shinjuku Station?",
     "Busta Shinjuku has coin lockers on the 4th floor, for up to 72 hours. You need the QR code on the receipt to open them. "
     "The Tokyo Tourist Information Center on Busta's 3rd floor (6:30 to 21:00) offers temporary safekeeping and parcel delivery. "
     "The Odakyū Sightseeing Service Center keeps bags from 8:00 to 16:00, with pick-up until 19:00. JR East's map shows coin lockers in the station too, but we did not find their prices."),
    ("Where is the JR EAST Travel Service Center at Shinjuku?",
     "JR East says it is on the right after you exit the New South Ticket Gate, on the 2nd floor. It is open 8:00 to 19:00 all year, sells JR East passes and tickets, hands out tickets booked on JR-EAST Train Reservation, exchanges currency (Travelex) and has free Wi-Fi. It does not list luggage storage."),
    ("Where is there an ATM at Shinjuku Station?",
     "Busta Shinjuku has a Seven Bank ATM in its waiting room, open 3:30 to 25:00 (1 am). Seven Bank says its ATMs take cards issued outside Japan. "
     "Tokyo Metro's station map also marks ATMs on B1F and B2F. To change money, the JR EAST Travel Service Center has Travelex (8:00 to 19:00) and the Odakyū Sightseeing Service Center exchanges currency from 8:00 to 16:00."),
    ("How do I get to Hakone from Shinjuku?",
     "Odakyū's Romancecar limited express runs direct from Shinjuku to Hakone-Yumoto in about 80 minutes. All seats are reserved, and you need a limited express ticket plus a regular fare ticket. "
     "The Odakyū Sightseeing Service Center (B1, West Underground Exit, 8:00 to 16:00) sells Romancecar tickets and the Hakone Freepass."),
    ("Is there English help at Shinjuku Station?",
     "JR East lists English information at the 2F South Gate (10:00 to 18:00 inside the gates, 10:00 to 17:00 outside) and inside the B1 West Gate (10:00 to 17:00). "
     "Busta Shinjuku's information counter is open 7:00 to 23:00 and says it supports English and Japanese at all hours."),
    ("Why are some Marunouchi Line exits closed?",
     "Tokyo Metro's station map (as of November 2025) marks many Shinjuku exits as closed during construction, for example A11, A13, A14, B9 and B13. Follow the signs, and ask station staff if a route is closed."),
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
    "about": {"@type": "TrainStation", "name": "Shinjuku Station"},
}
ld_crumbs = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE},
        {"@type": "ListItem", "position": 2, "name": "Travel Essentials", "item": SITE + "/travel-essentials"},
        {"@type": "ListItem", "position": 3, "name": "Shinjuku Station Guide", "item": URL},
    ],
}


def ld(obj):
    return '<script type="application/ld+json">\n%s\n</script>' % json.dumps(obj, ensure_ascii=False)


TOC = [
    ("one-page", "Shinjuku Station on one page"),
    ("which-side", "Which side: West, or East and South?"),
    ("exits", "Which exit for where?"),
    ("platforms", "JR platforms 1 to 16"),
    ("narita", "Narita Express and airport buses"),
    ("lines", "Odakyū, Keiō, Seibu, Metro and Toei"),
    ("money", "Money and ATMs"),
    ("connected", "Getting online: eSIM and Wi-Fi"),
    ("luggage", "Lockers and luggage"),
    ("finder", "Find it fast: ATMs, lockers, information"),
    ("facilities", "Facilities in the station"),
    ("help", "Help for older travellers and anyone who needs assistance"),
    ("daytrips", "Day trips from Shinjuku"),
    ("leaving", "Leaving Shinjuku: a checklist"),
    ("faq", "FAQ"),
    ("about-this-guide", "About this guide and change log"),
]
# ---- "What do you need first?" tiles + a quick-jump bar that appears once you scroll (as w42)
TOC_SHORT = {
    "one-page": "On one page", "which-side": "Which side", "exits": "Which exit", "platforms": "Platforms", "narita": "Airport",
    "lines": "Other lines", "money": "Money", "connected": "Get online", "luggage": "Luggage", "finder": "Find it fast",
    "facilities": "Facilities", "help": "Help", "daytrips": "Day trips", "leaving": "Leaving", "faq": "FAQ", "about-this-guide": "About",
}
TOC_TILES = [
    ("narita", "&#9992;&#65039;", "Last Narita Express", "19:39 from Shinjuku"),
    ("exits", "&#128682;", "Which exit?", "Busta, Godzilla, Govt. Building"),
    ("which-side", "&#129517;", "West or East?", "Two sides, one passage"),
    ("platforms", "&#128646;", "Platforms", "JR lines 1 to 16"),
    ("money", "&#128180;", "Money and ATMs", "Yen, cards, exchange"),
    ("luggage", "&#129523;", "Luggage and lockers", "Busta 4F, info centers"),
    ("help", "&#129309;", "Help and assistance", "English help desks"),
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
    '<svg id="shjDiagram" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 624" role="img" aria-labelledby="shjT shjD" font-family="Arial, Helvetica, sans-serif">'
    '<title id="shjT">Shinjuku Station at a glance</title>'
    '<desc id="shjD">Shinjuku Station has two sides. The West side has the West Gate and the Central West Gate on B1, the Odakyu, Keio and Toei lines, the West exit bus stop and the Tokyo Metropolitan Government Building. '
    'The East and South side has the East Gate, Kabukicho and Seibu-Shinjuku, and on the 2nd floor the South and New South gates, Busta Shinjuku for airport buses, and the JR EAST Travel Service Center. '
    'The B1 Free Passage links East and West outside the ticket gates.</desc>'
    '<rect width="480" height="624" fill="#fff"/>'
    '<text x="240" y="38" font-size="26" font-weight="700" text-anchor="middle" fill="#0f0f23">Shinjuku Station at a glance</text>'
    '<text x="240" y="64" font-size="17" text-anchor="middle" fill="#555">West for Odakyu and Keio, South for Busta</text>'
    '<rect x="24" y="88" width="432" height="212" rx="18" fill="#F3EFFB" stroke="#6b4fb3" stroke-width="2"/>'
    '<text x="48" y="128" font-size="28" font-weight="700" fill="#0f0f23">West side</text>'
    '<text x="48" y="152" font-size="18" fill="#0f0f23">West Gate, Central West Gate (B1)</text>'
    + _dg_pill(164, "Odakyu, Keio, Toei Shinjuku and Oedo", "#fff", "#6b4fb3", "#4a3385", "700")
    + _dg_pill(204, "West exit bus stop", "#fff", "#6b4fb3", "#4a3385")
    + _dg_pill(244, "Metropolitan Govt. Building, 10 min", "#fff", "#6b4fb3", "#4a3385")
    + '<line x1="240" y1="304" x2="240" y2="376" stroke="#2563EB" stroke-width="4" stroke-dasharray="8 6" stroke-linecap="round"/>'
    '<text x="254" y="334" font-size="15" font-weight="700" fill="#2563EB">B1 Free Passage</text>'
    '<text x="254" y="358" font-size="15" fill="#2563EB">outside the ticket gates</text>'
    '<rect x="24" y="380" width="432" height="212" rx="18" fill="#EEF0FB" stroke="#34346e" stroke-width="2"/>'
    '<text x="48" y="420" font-size="28" font-weight="700" fill="#0f0f23">East and South side</text>'
    '<text x="48" y="444" font-size="18" fill="#0f0f23">East Gate (B1), South gates (2F)</text>'
    + _dg_pill(456, "Busta: airport buses, 4F", "#fff", "#34346e", "#1a1a3e", "700")
    + _dg_pill(496, "New South Gate, Travel Service Center", "#fff", "#34346e", "#1a1a3e")
    + _dg_pill(536, "Kabukicho, Seibu-Shinjuku", "#fff", "#34346e", "#1a1a3e")
    + '<text x="240" y="614" font-size="14" text-anchor="middle" fill="#777">Simplified, not to scale. packsmartapp.com</text></svg>'
)

DIAGRAM = '<figure class="ps-fig" id="at-a-glance">\n' + _DG_SVG + """
<button type="button" class="ps-btn2" id="shjDl">Download the diagram (PNG)</button>
</figure>
<script>
(function(){
  var b=document.getElementById('shjDl'); if(!b) return;
  b.addEventListener('click',function(){
    try{
      var svg=document.getElementById('shjDiagram');
      var xml=new XMLSerializer().serializeToString(svg);
      var img=new Image();
      img.onload=function(){
        var c=document.createElement('canvas'); c.width=960; c.height=1248;
        var x=c.getContext('2d'); x.fillStyle='#fff'; x.fillRect(0,0,c.width,c.height); x.drawImage(img,0,0,c.width,c.height);
        c.toBlob(function(bl){
          var a=document.createElement('a'); a.href=URL.createObjectURL(bl); a.download='shinjuku-station-at-a-glance.png';
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
    "terms": [["T1", "West"], ["T2", "East and South"]],
    "items": [
        ["money", "Money and ATMs", {
            "T1": "In the Metro Marunouchi Line station, Tokyo Metro's map marks ATMs on B1F and B2F. The Odakyū Sightseeing Service Center (Odakyū Line B1, West Underground Exit) exchanges currency from 8:00 to 16:00.",
            "T2": "Seven Bank ATM in the Busta Shinjuku waiting room, 3:30 to 25:00 (1 am). Seven Bank says its ATMs take cards issued outside Japan. Travelex currency exchange at the JR EAST Travel Service Center, right after the New South Gate (2F), 8:00 to 19:00. Tokyo Metro's map also marks ATMs on B1F and B2F of the Marunouchi Line station."}],
        ["toilet", "Toilets", {
            "T1": "JR East's station map shows restrooms, but we did not find a list in words. In the Metro Marunouchi Line station, Tokyo Metro's map shows toilets and an accessible toilet near exit A8. Follow the signs, or ask station staff.",
            "T2": "Busta Shinjuku has multipurpose, wheelchair-accessible toilets with ostomate facilities. JR East's station map shows other restrooms. Follow the signs, or ask station staff."}],
        ["lockers", "Luggage lockers and storage", {
            "T1": "The Odakyū Sightseeing Service Center (B1, West Underground Exit) keeps bags from 8:00 to 16:00, with pick-up until 19:00. JR East's map shows coin lockers in the station, but we did not find their prices.",
            "T2": "Busta Shinjuku 4F coin lockers, up to 72 hours, from 30 minutes before the first bus to the last bus. Keep the receipt: its QR code opens the locker. The Tokyo Tourist Information Center (Busta 3F, 6:30 to 21:00) offers temporary safekeeping and parcel delivery."}],
        ["info", "Tourist information", {
            "T1": "English information inside the B1 West Gate, 10:00 to 17:00 (JR East). The Odakyū Sightseeing Service Center (B1, West Underground Exit, 8:00 to 16:00) has Hakone information.",
            "T2": "JR EAST Travel Service Center, right after the New South Gate (2F), 8:00 to 19:00. English information at the 2F South Gate: 10:00 to 18:00 inside the gates, 10:00 to 17:00 outside. Tokyo Tourist Information Center, Busta 3F, 6:30 to 21:00. Busta information counter, 7:00 to 23:00."}],
        ["tickets", "Tickets and passes", {
            "T1": "The JR ticket office (Midori-no-madoguchi) is beside the B1 Free Passage near the West Gate (JR East map). The Odakyū Sightseeing Service Center sells Romancecar tickets and the Hakone Freepass, 8:00 to 16:00.",
            "T2": "The JR EAST Travel Service Center (New South Gate, 2F, 8:00 to 19:00) sells East Japan passes and tickets and hands out tickets booked on JR-EAST Train Reservation. Airport Limousine tickets at Busta: staffed office 4:20 to 22:50, machines 3:40 to 22:50."}],
        ["help", "Wheelchair, lifts and help", {
            "T1": "JR East's map shows lifts (lettered A to O) to the platforms. At the West exit bus stop there is a lift to the ground and a lift to the Marunouchi Line (B2). Ask station staff for the best route. In an emergency, call 119.",
            "T2": "JR East's map shows a lift to the Kōshū-kaidō overpass (ground floor) near the Miraina Tower Gate, and lifts (lettered A to O) to the platforms. Busta has wheelchair-accessible toilets. Ask station staff. In an emergency, call 119."}],
        ["baby", "Nursing room", {
            "T1": "In the Metro Marunouchi Line station, Tokyo Metro's map shows a baby room near exit A8. JR East's map shows a nursery symbol, but we did not find its location in words. Ask station staff.",
            "T2": "Busta Shinjuku has a nursing room with hot water and a baby-changing stand. Tokyo Metro's map shows a baby room near Marunouchi Line exit A8."}],
        ["wifi", "Wi-Fi and SIM", {
            "T1": "The Odakyū Sightseeing Service Center sells SIM cards and eSIMs (8:00 to 16:00). An eSIM installed on your phone needs no counter.",
            "T2": "Free Wi-Fi: JR-EAST Free Wi-Fi at the Travel Service Center, and \"Shinjuku-Bus-Terminal_Free_Wi-Fi\" at Busta. Busta also has coin-operated phone chargers beside the ticket machines. An eSIM installed on your phone needs no counter."}],
        ["food", "Food and drink", {
            "T1": "We did not find an official list of places to eat on the West side. Please ask station staff.",
            "T2": "Busta Shinjuku has a convenience store, 3:30 to 25:00 (1 am). For anything else, please ask station staff."}],
        ["unwell", "Feeling unwell", {
            "T1": "Tell station staff. In an emergency, call 119.",
            "T2": "Tell station staff, or the Busta information counter (7:00 to 23:00). In an emergency, call 119."}],
    ],
}
_ORDER = ["money", "toilet", "lockers", "info", "tickets", "help", "baby", "wifi", "food", "unwell"]
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
  D.terms.forEach(function(t){tEl.appendChild(mk(t[1]+' side',t[0],'t'));});
  D.items.forEach(function(i){wEl.appendChild(mk(i[1],i[0],'w'));});
  function show(){
    if(!term||!what){ rEl.textContent=!term?'Now choose your side.':'Now choose what you need.'; return; }
    var tn=D.terms.filter(function(t){return t[0]===term;})[0][1];
    var it=D.items.filter(function(i){return i[0]===what;})[0];
    var txt=it[2][term];
    rEl.innerHTML='';
    var s=document.createElement('strong'); s.textContent=it[1]+': '+tn+' side'; rEl.appendChild(s);
    rEl.appendChild(document.createElement('br'));
    rEl.appendChild(document.createTextNode(txt?txt:'We did not find this on the official station pages. Please ask station staff.'));
    var sm=document.createElement('small'); sm.textContent='From JR East, Tokyo Metro, Busta Shinjuku, GO TOKYO and Odakyū pages, checked 22 November 2026. Floors and hours can change. If you cannot find it, ask station staff.'; rEl.appendChild(sm);
  }
})();
</script>"""
FINDER = FINDER.replace("__FINDER_JSON__", json.dumps(FINDER_DATA, ensure_ascii=False))

CHOOSER = """<h3>Which side is yours?</h3>
<div class="ps-scroll">
<table class="checklist-table">
<thead><tr><th>You are going to</th><th>Easiest side</th><th>Why</th></tr></thead>
<tbody>
<tr><td><strong>Narita Express (N&rsquo;EX)</strong></td><td>Inside the JR ticket gates</td><td>JR East's station map shows the Narita Express on platforms 5 and 6. Follow the signs for platforms 5 and 6.</td></tr>
<tr><td><strong>Airport buses, Busta Shinjuku</strong></td><td>South: New South Gate (2F)</td><td>Busta says the New South Gate is open 5:45 to 24:00. Outside those hours, use the South Gate. Buses leave from Busta's 4th floor.</td></tr>
<tr><td><strong>JR EAST Travel Service Center</strong></td><td>South: New South Gate (2F)</td><td>JR East says it is on the right after you exit the New South Ticket Gate.</td></tr>
<tr><td><strong>Odakyū Line, Romancecar to Hakone</strong></td><td>West side</td><td>JR East's map shows the route to the Odakyū Line on B1. The Odakyū Sightseeing Service Center is at the Odakyū B1 West Underground Exit. The 2F South Gate is also marked for the Odakyū Line.</td></tr>
<tr><td><strong>Keiō Line</strong></td><td>West side</td><td>The Central West Gate (B1), also called the Keiō exit, is open from 6:00 to the last train.</td></tr>
<tr><td><strong>Toei Shinjuku and Ōedo lines</strong></td><td>West side</td><td>JR East's map shows the B1 route via the Central West Gate area.</td></tr>
<tr><td><strong>Tokyo Metropolitan Government Building</strong></td><td>West side</td><td>About 10 minutes on foot from the west exit (GO TOKYO). The observation decks on the 45th floor are free.</td></tr>
<tr><td><strong>Kabukichō, Godzilla head, Seibu-Shinjuku</strong></td><td>East side</td><td>JR East's map shows Kabukichō via the East side. The Godzilla head is about 5 minutes from the east exit (GO TOKYO).</td></tr>
<tr><td><strong>Marunouchi Line (Metro)</strong></td><td>East side, or the West exit lift</td><td>JR East's map shows the Marunouchi Line via the East side, and a lift to the Marunouchi Line (B2) at the West exit bus stop. Many Metro exits are closed during construction.</td></tr>
<tr><td><strong>Not sure</strong></td><td>Check your ticket or booking</td><td>Ask at the JR EAST Travel Service Center (New South Gate) or an English information desk (2F South Gate, B1 West Gate).</td></tr>
</tbody>
</table>
</div>
"""


LUGGAGE = """<h2 id="luggage">Lockers and luggage</h2>
<p>Sort your bags out before you start walking. You have three choices: a coin locker, a storage counter, or sending the bag on.</p>
<ul>
<li><strong>Busta Shinjuku coin lockers (4th floor).</strong> Up to 72 hours. Small lockers cost &yen;100 per 60 minutes (then &yen;500 per 6 hours), medium &yen;100 per 40 minutes (then &yen;600 per 6 hours) and large &yen;100 per 30 minutes (then &yen;900 per 6 hours). They can be used from 30 minutes before the first bus until the last bus. Keep the receipt: you need its QR code to open the locker.</li>
<li><strong>Tokyo Tourist Information Center, Busta 3rd floor.</strong> 6:30 to 21:00, seven days a week. GO TOKYO says it offers delivery of parcels and temporary safekeeping of personal belongings (only at Busta Shinjuku).</li>
<li><strong>Odakyū Sightseeing Service Center (West side).</strong> Baggage storage from 8:00 to 16:00, with pick-up until 19:00. It is at the Odakyū Line B1, West Underground Exit.</li>
<li><strong>JR coin lockers.</strong> JR East's station map shows several coin lockers inside the station. We did not find their sizes or prices, so we give none.</li>
<li><strong>JR EAST Travel Service Center.</strong> Its page does not list luggage storage or delivery.</li>
<li><strong>Keep with you:</strong> medicines, valuables, chargers and a change of clothes.</li>
<li><strong>Have these ready:</strong> your hotel name, address and phone number, written down.</li>
</ul>
""" + sources(["busta", "tic", "odakyu", "jrmap", "jrtsc"], "Prices and hours change, so check at the counter.")

HELP = """<h2 id="help">Help for older travellers and anyone who needs assistance</h2>
<p>You do not have to cope alone. Asking early is easier than struggling.</p>
<ul>
<li><strong>English information (JR East).</strong> 2F South Gate: 10:00 to 18:00 inside the ticket gates, 10:00 to 17:00 outside. B1 West Gate, inside the gates: 10:00 to 17:00.</li>
<li><strong>JR EAST Travel Service Center.</strong> On the right after the New South Ticket Gate (2F), 8:00 to 19:00, open all year. Tourist information for the East Japan and Hokuriku areas, and maps of the Shinjuku area.</li>
<li><strong>Busta Shinjuku information counter.</strong> 7:00 to 23:00. Busta says it supports English and Japanese at all hours.</li>
<li><strong>Station staff.</strong> Tell staff at a ticket gate or ticket office if you need help or are not sure which way to go.</li>
<li><strong>Lifts.</strong> JR East's map shows lifts lettered A to O to the platforms, a lift to the ground and to the Marunouchi Line (B2) at the West exit bus stop, and a lift to the Kōshū-kaidō overpass near the Miraina Tower Gate. Busta has wheelchair-accessible toilets.</li>
<li><strong>Allow extra time.</strong> We did not find official walking times between gates and platforms, so add a buffer, especially with luggage.</li>
<li><strong>Visitor hotline.</strong> The Japan Visitor Hotline, 050-3816-2787, is open 24 hours and helps in English, Chinese and Korean. In an emergency, call 119.</li>
</ul>
""" + sources(["jrmap", "jrtsc", "busta"])

ABOUT = """<div class="ps-about" id="about-this-guide">
<h2>About this guide</h2>
<p>Written by PackSmart. Station details were checked on 22 November 2026 against JR East (station map, Travel Service Center and timetables), Tokyo Metro, Busta Shinjuku, GO TOKYO, the Airport Limousine Bus, Odakyū and Keiō pages. Where an official page did not tell us something, for example JR coin-locker prices or the last airport buses, we say so instead of guessing. Spotted something out of date? <a href="/contact">Tell us</a> and we will fix it.</p>
<ul>
<li><strong>22 Nov 2026:</strong> first version, with the West and East chooser, which exit for where, the diagram, JR platforms, the last Narita Express, airport buses, other lines, money, lockers and luggage, the find-it tool, help and day trips.</li>
</ul>
</div>"""
def _card(title, text, slug, tag):
    return ('        <div class="related-card">\n            <div class="related-card-body">\n                <h4>%s</h4>\n                <p>%s</p>\n'
            '                <a href="https://www.packsmartapp.com%s">Read More <span class="related-arrow">&rarr;</span></a>\n                <div class="related-tag">%s</div>\n            </div>\n        </div>\n') % (title, text, slug, tag)

RELATED = ('<div class="related-posts">\n    <h3>Related Guides</h3>\n    <div class="related-grid">\n'
    + _card("Narita Airport Guide 2026", "Flying out of Narita? Terminals, departure steps, SIM and the trains and buses from Tokyo.", "/blog/narita-airport-guide", "Airport Guide")
    + _card("Haneda Airport Guide 2026", "Terminals, departure steps and the quickest ways from central Tokyo.", "/blog/haneda-airport-guide", "Airport Guide")
    + _card("Tokyo Station Guide 2026", "Which side to use, bullet train platforms, the Narita Express and luggage.", "/blog/tokyo-station-guide", "Station Guide")
    + '    </div>\n</div>')
# hero image: public/images/shinjuku-station-hero.jpg (PAKUTASO, see docs/research/shinjuku-sources.md); optimised copy made here
def prepare_hero(write=False):
    """write=False only works out the URL (nothing is written before every anchor check has passed)."""
    imgdir = os.path.join(ROOT, "public", "images")
    src = None
    for ext in ("jpg", "jpeg", "png", "webp"):
        cand = os.path.join(imgdir, "shinjuku-station-hero." + ext)
        if os.path.isfile(cand):
            src = cand
            break
    if not src:
        return None, None
    dst = os.path.join(imgdir, "shinjuku-station-hero-1600.jpg")
    note = None
    if (not os.path.isfile(dst)) or os.path.getmtime(dst) < os.path.getmtime(src):
        if not write:
            try:
                import PIL  # noqa: F401  (Pillow can make the copy later)
            except Exception:
                import shutil
                if not shutil.which("sips") and not os.path.isfile(dst):
                    return ("/images/" + os.path.basename(src) if src.lower().endswith(".jpg") else None), None
            return "/images/shinjuku-station-hero-1600.jpg", None
        import subprocess, shutil
        try:
            subprocess.run(["sips", "-Z", "1600", "-s", "format", "jpeg", "-s", "formatOptions", "72", src, "--out", dst],
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            note = "shinjuku-station-hero-1600.jpg (optimised from your photo)"
        except Exception:
            # no sips (Linux): resize with Pillow, else keep an existing optimised copy (as w36)
            try:
                from PIL import Image
                _im = Image.open(src).convert("RGB")
                _im.thumbnail((1600, 1600))
                if os.path.isfile(dst) and os.path.getmtime(dst) >= os.path.getmtime(src) - 1:
                    pass
                else:
                    _im.save(dst, "JPEG", quality=72, optimize=True, progressive=True)
                    note = os.path.basename(dst) + " (optimised from your photo)"
            except Exception:
                if not os.path.isfile(dst):
                    if src.lower().endswith(".jpg"):
                        return "/images/" + os.path.basename(src), "using the original photo (could not optimise it here)"
                    return None, None
    return "/images/shinjuku-station-hero-1600.jpg", note

HERO_URL, HERO_NOTE = prepare_hero()

CARD = """<div class="ps-card" id="one-page">
<h2>Shinjuku Station on one page</h2>
<ul>
<li><strong>Last Narita Express:</strong> 19:39 from Shinjuku, every day (first 5:55), platforms 5 and 6. About 80 minutes to Narita Terminal 1 on a sample train (JR East). Timetables change, so check.</li>
<li><strong>Airport buses:</strong> Busta Shinjuku, 4th floor. Use the JR New South Gate (2F, open 5:45 to 24:00), or the South Gate outside those hours. Narita: adult &yen;3,600. Check the live timetable for the last bus.</li>
<li><strong>Two sides:</strong> the West side has the Odakyū, Keiō and Toei lines and the West exit buses. The East side has Kabukichō and Seibu-Shinjuku. The South gates on 2F lead to Busta and the JR EAST Travel Service Center.</li>
<li><strong>Between East and West:</strong> the B1 Free Passage, outside the ticket gates.</li>
<li><strong>JR platforms:</strong> Yamanote Line 14 and 15, Chūō Line (Rapid) 7&ndash;8 and 11&ndash;12, Chūō limited express 9&ndash;10, Saikyō and Shōnan-Shinjuku lines 1&ndash;4.</li>
<li><strong>Metro Marunouchi Line:</strong> many exits are closed during construction. Follow the signs.</li>
<li><strong>Money:</strong> Seven Bank ATM in the Busta waiting room, 3:30 to 25:00 (1 am). Seven Bank takes cards issued outside Japan.</li>
<li><strong>Luggage:</strong> Busta 4F coin lockers (up to 72 hours), or the Tokyo Tourist Information Center on Busta 3F (6:30 to 21:00).</li>
<li><strong>Need help?</strong> JR EAST Travel Service Center, right after the New South Gate, 8:00 to 19:00. In an emergency, call 119.</li>
</ul>
<div class="ps-qr ps-qr-screen">__QR_SCREEN__<p><strong>Want it on your phone?</strong> Point your phone camera at this code. It opens the free Shinjuku Station Pocket Guide, which works without internet once opened.<span class="u">packsmartapp.com/shinjuku-pocket</span></p></div>
<div class="ps-qr ps-qr-print">__QR_PRINT__<p><strong>Free Shinjuku Station Pocket Guide.</strong> Point your phone camera at this code. Open it once with signal and it works without internet.<span class="u">packsmartapp.com/shinjuku-pocket</span></p></div>
<button type="button" class="ps-print-btn" onclick="window.print()">Print this card</button>
</div>"""
# QR codes are made once for each guide address (?src=qr on screen, ?src=card on paper), with segno (error="m"), as in w42.
QR_SCREEN = '<svg shape-rendering="crispEdges" viewBox="0 0 41 41" class="segno"><title>QR code: open the Shinjuku Station Pocket Guide</title><path fill="#fff" d="M0 0h41v41h-41z"/><path class="qrline" stroke="#000" d="M4 4.5h7m3 0h1m7 0h1m3 0h1m3 0h7m-33 1h1m5 0h1m1 0h2m2 0h3m1 0h2m3 0h2m1 0h1m1 0h1m5 0h1m-33 1h1m1 0h3m1 0h1m1 0h2m3 0h1m2 0h3m1 0h3m1 0h1m1 0h1m1 0h3m1 0h1m-33 1h1m1 0h3m1 0h1m1 0h3m1 0h1m2 0h1m4 0h2m4 0h1m1 0h3m1 0h1m-33 1h1m1 0h3m1 0h1m4 0h1m3 0h1m2 0h1m2 0h4m1 0h1m1 0h3m1 0h1m-33 1h1m5 0h1m2 0h1m1 0h3m2 0h1m1 0h1m5 0h1m1 0h1m5 0h1m-33 1h7m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h7m-25 1h1m2 0h1m2 0h1m7 0h1m-23 1h1m5 0h1m1 0h3m1 0h4m1 0h1m2 0h1m1 0h1m2 0h2m2 0h3m-32 1h1m1 0h3m2 0h3m2 0h1m1 0h3m2 0h1m2 0h2m4 0h3m-31 1h4m1 0h2m1 0h1m2 0h1m3 0h2m1 0h1m5 0h1m3 0h1m1 0h2m-32 1h1m2 0h1m1 0h1m3 0h1m2 0h1m1 0h1m1 0h1m2 0h1m2 0h2m3 0h4m1 0h1m-33 1h2m2 0h5m2 0h4m1 0h5m5 0h1m-26 1h1m3 0h1m1 0h1m1 0h1m1 0h4m1 0h1m5 0h2m2 0h2m3 0h2m-33 1h2m1 0h2m1 0h1m2 0h6m3 0h1m6 0h2m4 0h1m-30 1h2m1 0h1m1 0h4m1 0h1m1 0h2m2 0h3m4 0h1m1 0h1m1 0h2m1 0h1m-32 1h7m1 0h2m2 0h2m2 0h1m2 0h1m1 0h1m1 0h2m1 0h3m2 0h1m-33 1h3m2 0h1m3 0h2m2 0h5m1 0h2m2 0h4m2 0h2m1 0h1m-31 1h3m1 0h1m1 0h1m2 0h3m1 0h1m3 0h1m2 0h2m3 0h1m1 0h2m1 0h1m-33 1h3m1 0h1m2 0h2m3 0h7m4 0h1m1 0h2m1 0h4m-32 1h1m1 0h1m1 0h6m2 0h2m2 0h1m3 0h1m1 0h1m1 0h2m1 0h3m2 0h1m-33 1h2m1 0h1m4 0h1m2 0h1m4 0h1m1 0h2m1 0h3m4 0h3m-31 1h1m3 0h1m1 0h2m1 0h8m1 0h1m1 0h1m4 0h1m3 0h3m-32 1h1m1 0h1m1 0h1m4 0h1m1 0h1m1 0h1m4 0h1m3 0h6m1 0h4m-33 1h3m1 0h3m5 0h1m1 0h3m1 0h3m3 0h6m1 0h2m-25 1h3m4 0h2m1 0h3m1 0h3m3 0h1m1 0h1m1 0h1m-33 1h7m2 0h8m1 0h1m1 0h1m2 0h2m1 0h1m1 0h1m1 0h2m-32 1h1m5 0h1m5 0h1m2 0h2m6 0h2m3 0h3m1 0h1m-33 1h1m1 0h3m1 0h1m2 0h2m1 0h1m2 0h1m2 0h3m3 0h6m2 0h1m-33 1h1m1 0h3m1 0h1m4 0h4m1 0h2m1 0h2m1 0h2m1 0h1m1 0h2m2 0h2m-33 1h1m1 0h3m1 0h1m2 0h1m1 0h1m2 0h1m1 0h1m2 0h1m2 0h1m1 0h1m2 0h2m2 0h2m-33 1h1m5 0h1m2 0h1m1 0h1m1 0h1m1 0h2m1 0h1m1 0h1m1 0h1m4 0h4m-31 1h7m1 0h1m4 0h2m2 0h1m1 0h1m2 0h6m1 0h1m1 0h1"/></svg>'
QR_PRINT = '<svg shape-rendering="crispEdges" viewBox="0 0 41 41" class="segno"><title>QR code: open the Shinjuku Station Pocket Guide</title><path fill="#fff" d="M0 0h41v41h-41z"/><path class="qrline" stroke="#000" d="M4 4.5h7m6 0h2m1 0h1m1 0h3m2 0h1m2 0h7m-33 1h1m5 0h1m2 0h1m1 0h6m5 0h1m1 0h1m1 0h1m5 0h1m-33 1h1m1 0h3m1 0h1m1 0h2m3 0h1m2 0h1m1 0h1m1 0h3m1 0h1m1 0h1m1 0h3m1 0h1m-33 1h1m1 0h3m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m3 0h1m3 0h1m1 0h3m1 0h1m-33 1h1m1 0h3m1 0h1m1 0h1m2 0h2m2 0h1m2 0h7m1 0h1m1 0h3m1 0h1m-33 1h1m5 0h1m1 0h4m1 0h1m1 0h2m1 0h1m2 0h1m2 0h1m1 0h1m5 0h1m-33 1h7m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h7m-25 1h1m2 0h2m1 0h2m3 0h1m1 0h2m-23 1h1m1 0h5m4 0h1m1 0h3m1 0h1m2 0h1m1 0h1m3 0h5m-30 1h1m5 0h2m1 0h1m1 0h1m6 0h3m1 0h1m2 0h2m1 0h2m1 0h1m-32 1h3m1 0h2m2 0h3m3 0h2m1 0h1m5 0h1m3 0h1m1 0h2m-32 1h3m4 0h2m2 0h2m1 0h3m1 0h2m1 0h3m4 0h3m1 0h1m-30 1h2m1 0h2m3 0h1m6 0h1m1 0h1m1 0h2m1 0h1m2 0h2m1 0h2m-33 1h1m3 0h2m2 0h3m1 0h5m1 0h6m2 0h1m4 0h2m-33 1h2m4 0h1m3 0h1m7 0h1m1 0h1m4 0h2m4 0h1m-29 1h3m1 0h1m2 0h1m1 0h1m3 0h1m1 0h1m2 0h2m2 0h2m1 0h3m-29 1h3m1 0h1m1 0h1m2 0h1m1 0h1m3 0h1m2 0h1m1 0h1m1 0h2m1 0h3m2 0h1m-32 1h2m6 0h2m1 0h1m1 0h1m1 0h2m1 0h3m1 0h5m1 0h2m1 0h1m-32 1h1m3 0h3m1 0h3m1 0h1m1 0h3m2 0h1m4 0h4m1 0h2m-32 1h1m2 0h1m3 0h2m1 0h1m1 0h2m2 0h3m2 0h1m1 0h1m1 0h7m-32 1h3m2 0h5m1 0h1m2 0h1m1 0h1m5 0h1m1 0h2m1 0h3m2 0h1m-33 1h1m6 0h1m2 0h1m4 0h1m2 0h3m2 0h1m2 0h2m1 0h2m1 0h1m-33 1h1m1 0h3m1 0h1m1 0h3m1 0h1m1 0h3m1 0h1m1 0h1m4 0h1m3 0h3m-32 1h1m1 0h3m3 0h1m1 0h1m1 0h4m2 0h2m1 0h6m2 0h3m-32 1h1m5 0h1m1 0h2m1 0h1m2 0h2m1 0h2m3 0h7m2 0h1m-24 1h1m4 0h1m2 0h1m1 0h7m3 0h1m1 0h1m1 0h1m-33 1h7m2 0h1m2 0h1m2 0h2m1 0h1m1 0h1m2 0h2m1 0h1m1 0h1m1 0h2m-32 1h1m5 0h1m1 0h1m2 0h1m1 0h1m6 0h5m3 0h3m-31 1h1m1 0h3m1 0h1m1 0h1m1 0h1m1 0h4m2 0h2m4 0h6m2 0h1m-33 1h1m1 0h3m1 0h1m1 0h3m3 0h4m1 0h5m1 0h1m2 0h1m2 0h2m-33 1h1m1 0h3m1 0h1m1 0h1m1 0h2m1 0h2m2 0h1m2 0h1m2 0h5m1 0h1m-30 1h1m5 0h1m2 0h1m6 0h1m1 0h1m1 0h3m5 0h3m-31 1h7m1 0h1m1 0h1m6 0h1m1 0h1m2 0h6m1 0h1m1 0h1"/></svg>'
CARD = CARD.replace("__QR_SCREEN__", QR_SCREEN).replace("__QR_PRINT__", QR_PRINT)

WHICH = """<h2 id="which-side">Which side: West, or East and South?</h2>
<p>Shinjuku Station has gates on two levels. On B1 are the <strong>East Gate</strong>, the <strong>West Gate</strong>, the <strong>Central East Gate</strong> and the <strong>Central West Gate</strong> (6:00 to the last train, also called the Keiō exit). On the 2nd floor are the <strong>South Gate</strong>, the <strong>Southeast Gate</strong> (7:00 to 24:00), the <strong>Kōshū-kaidō Gate</strong>, the <strong>New South Gate</strong> and the <strong>Miraina Tower Gate</strong>, according to JR East's station map.</p>
<p>In this guide we use two sides. The <strong>West side</strong> is for the Odakyū, Keiō and Toei lines and the West exit bus stop. The <strong>East and South side</strong> covers the East Gate (Kabukichō, Seibu-Shinjuku) and the 2nd-floor south gates, which lead to Busta Shinjuku and the JR EAST Travel Service Center. Outside the ticket gates, the B1 <strong>Free Passage</strong> links the East and West sides.</p>
""" + CHOOSER + sources(["jrmap", "jrtsc", "bustaacc", "pdf"], "Station layouts change, so follow the signs.")

EXITS = """<h2 id="exits">Which exit for where?</h2>
<p>Walking times are the ones printed on GO TOKYO's &ldquo;Around Shinjuku Station&rdquo; map. Gate hours are from JR East and Busta Shinjuku.</p>
<div class="ps-scroll">
<table class="checklist-table">
<thead><tr><th>Going to</th><th>Use</th><th>Good to know</th></tr></thead>
<tbody>
<tr><td><strong>Busta Shinjuku (airport and highway buses)</strong></td><td>JR New South Gate, 2F</td><td>Open 5:45 to 24:00. Outside those hours, use the South Gate. Buses leave from the 4th floor and arrive on the 3rd.</td></tr>
<tr><td><strong>Tokyo Metropolitan Government Building</strong></td><td>West exit</td><td>About 10 minutes on foot. Free observation decks on the 45th floor.</td></tr>
<tr><td><strong>Godzilla head (Shinjuku Toho Building, Kabukichō)</strong></td><td>East exit</td><td>About 5 minutes on foot.</td></tr>
<tr><td><strong>Kabukichō Tower</strong></td><td>East side</td><td>About 7 minutes from Shinjuku Station, 1 minute from Seibu-Shinjuku Station.</td></tr>
<tr><td><strong>Odakyū Line and the Odakyū Sightseeing Service Center</strong></td><td>West side, B1</td><td>The center is at the Odakyū B1 West Underground Exit. Odakyū says stairs and escalators have moved because of construction.</td></tr>
<tr><td><strong>Keiō Line</strong></td><td>Central West Gate (Keiō exit), B1</td><td>Open from 6:00 to the last train.</td></tr>
<tr><td><strong>Toei Shinjuku and Ōedo lines</strong></td><td>Central West Gate area, B1</td><td>Tokyo Metro's map also shows a route to the Ōedo Line at Shinjuku-nishiguchi (E01).</td></tr>
<tr><td><strong>Metro Marunouchi Line (M08)</strong></td><td>East side</td><td>Platforms on B2F. Many Metro exits are marked closed during construction, so follow the signs.</td></tr>
<tr><td><strong>Taxi</strong></td><td>New South Gate side</td><td>JR East's map shows the taxi stop on 3F, reached from the 2F New South Gate side.</td></tr>
</tbody>
</table>
</div>
""" + sources(["pdf", "jrmap", "bustaacc", "odakyu", "metro"], "Exits close and move during construction, so follow the signs.")

PLATFORMS = """<h2 id="platforms">JR platforms 1 to 16</h2>
<p>JR East's station map (as of August 2026) lists these JR platforms on 1F. Your ticket and the departure boards show your platform, and platforms can change, so check before you walk up.</p>
<div class="ps-scroll">
<table class="checklist-table">
<thead><tr><th>Platforms</th><th>Line</th><th>Toward</th></tr></thead>
<tbody>
<tr><td><strong>1 to 4</strong></td><td>Saikyō Line, Shōnan-Shinjuku Line</td><td>-</td></tr>
<tr><td><strong>5 and 6</strong></td><td>Narita Express (also the Tōbu Line direct limited express)</td><td>Narita Airport</td></tr>
<tr><td><strong>7 and 8</strong></td><td>Chūō Line (Rapid)</td><td>Ochanomizu and Tokyo</td></tr>
<tr><td><strong>9 and 10</strong></td><td>Chūō Line limited express</td><td>Kōfu and Matsumoto</td></tr>
<tr><td><strong>11 and 12</strong></td><td>Chūō Line (Rapid)</td><td>Nakano, Tachikawa and Takao</td></tr>
<tr><td><strong>13</strong></td><td>Chūō-Sōbu Line (Local)</td><td>Suidōbashi, Akihabara and Chiba</td></tr>
<tr><td><strong>14</strong></td><td>Yamanote Line</td><td>Harajuku, Shibuya and Shinagawa</td></tr>
<tr><td><strong>15</strong></td><td>Yamanote Line</td><td>Ikebukuro, Tabata and Ueno</td></tr>
<tr><td><strong>16</strong></td><td>Chūō-Sōbu Line (Local)</td><td>Higashi-Nakano, Nakano and Mitaka</td></tr>
</tbody>
</table>
</div>
<ul>
<li><strong>Lifts.</strong> JR East's map shows lifts, lettered A to O, to the platforms.</li>
<li><strong>Reserved-seat machines.</strong> The map also shows a passport reader and reserved-seat ticket machine, and ticket offices.</li>
</ul>
""" + sources(["jrmap"])

NARITA = """<h2 id="narita">Narita Express and airport buses</h2>
<div class="tip-box"><strong>The last Narita Express from Shinjuku leaves at 19:39</strong>, on weekdays and on Saturdays and holidays (JR East timetable, edition 2612). The first leaves at 5:55. After 19:39, plan another way to the airport.</div>
<ul>
<li><strong>Narita Express (N&rsquo;EX).</strong> Platforms 5 and 6 (JR East's map). Trains run to Narita Airport Terminal 1, via Terminal 2&middot;3. On weekdays they leave at 5:55, 6:34, 7:07, 7:27, 8:05, 9:05 and 9:40, then at about :08 and :38 past each hour until 16:38, then 17:09, 17:39, 18:09, 18:39 and 19:39. One sample train leaves at 10:08 and reaches Terminal 1 at 11:27, about 80 minutes.</li>
<li><strong>Airport Limousine Bus to Narita.</strong> From the Shinjuku Expressway Bus Terminal (Busta Shinjuku), 4th floor. Adult &yen;3,600, child &yen;1,800. The first sample bus leaves Busta at 5:40 and reaches Terminal 1 at 7:10, about 90 minutes.</li>
<li><strong>Airport Limousine Bus to Haneda.</strong> Also from Busta. The bus company lists an early-morning bus at 3:50. Late-night and early-morning fares are higher: the route page lists adult &yen;1,400 by day and &yen;2,800 late at night.</li>
<li><strong>Last buses.</strong> We did not verify the last buses to Narita or Haneda. Check the <a href="https://www.limousinebus.co.jp/en/" target="_blank" rel="noopener noreferrer">Airport Limousine Bus timetable</a> on the day.</li>
<li><strong>Bus tickets at Busta.</strong> The staffed Airport Limousine ticket office is open 4:20 to 22:50, and the ticket machines 3:40 to 22:50.</li>
<li><strong>Getting to Busta.</strong> Through the JR New South Gate (2F), open 5:45 to 24:00. Busta says it is about 2 minutes from there. Outside those hours, use the South Gate (about 4 minutes).</li>
</ul>
<p>More detail: our <a href="/blog/narita-airport-guide">Narita Airport guide</a> and <a href="/blog/haneda-airport-guide">Haneda Airport guide</a>.</p>
""" + sources(["nex", "nex2", "jrmap", "limon", "limoh", "busta", "bustaacc"], "Times change, so check the operator.")

LINES = """<h2 id="lines">Odakyū, Keiō, Seibu, Metro and Toei</h2>
<p>Several railway companies meet at Shinjuku. JR East's station map shows how to reach them from the JR gates.</p>
<ul>
<li><strong>Odakyū Line (West side).</strong> Reached on B1 from the West side. The 2F South Gate is also marked for the Odakyū Line. The Odakyū Sightseeing Service Center is at the B1 West Underground Exit.</li>
<li><strong>Keiō Line (West side).</strong> Through the Central West Gate, also called the Keiō exit, open from 6:00 to the last train.</li>
<li><strong>Toei Shinjuku and Ōedo lines (West side).</strong> On B1 via the Central West Gate area. Tokyo Metro's map also shows a route to the Ōedo Line at Shinjuku-nishiguchi (E01, B4F).</li>
<li><strong>Tokyo Metro Marunouchi Line (M08).</strong> Platforms on B2F, reached via the East side, or by the lift at the West exit bus stop. Tokyo Metro's map (as of November 2025) marks many exits as closed during construction, for example A11, A13, A14, A15, A18, B9, B13, B14 and B15. Follow the signs.</li>
<li><strong>Seibu-Shinjuku Station.</strong> GO TOKYO's map puts Kabukichō Tower 1 minute from Seibu-Shinjuku Station, and Tokyo Metro's map shows a route to the Seibu Shinjuku Line near exit B10.</li>
<li><strong>Buses.</strong> Expressway and airport buses leave from Busta Shinjuku (4F). There is also a West exit bus stop.</li>
</ul>
""" + sources(["jrmap", "metro", "odakyu", "pdf"], "Routes change during construction, so follow the signs.")

MONEY = """<h2 id="money">Money and ATMs</h2>
<ul>
<li><strong>Seven Bank ATM, Busta Shinjuku.</strong> In the waiting room, 3:30 to 25:00 (1 am). Seven Bank says its ATMs accept cards issued outside Japan (Visa, Mastercard, UnionPay, American Express, JCB, Discover and Diners).</li>
<li><strong>ATMs in the Metro station.</strong> Tokyo Metro's station map marks ATMs on B1F and B2F.</li>
<li><strong>Currency exchange, JR EAST Travel Service Center.</strong> Travelex, foreign currency to yen and back, 8:00 to 19:00. The center is on the right after the New South Ticket Gate (2F).</li>
<li><strong>Currency exchange, Odakyū Sightseeing Service Center.</strong> 8:00 to 16:00, at the Odakyū B1 West Underground Exit.</li>
<li><strong>Paying by card.</strong> The JR EAST Travel Service Center accepts JCB, Visa, Mastercard, American Express, Diners Club and Discover.</li>
</ul>
<p class="ps-note">Sources: """ + a_src("busta") + ", Seven Bank (sevenbank.co.jp), " + a_src("metro") + ", " + a_src("jrtsc") + " and " + a_src("odakyu") + ". " + CHECKED + """ Hours change, so check before you go.</p>"""

CONNECTED = """<h2 id="connected">Getting online: eSIM and Wi-Fi</h2>
<p>You will want a connection for maps, messages and your hotel. Here are the usual choices.</p>
<div class="ps-scroll">
<table class="checklist-table">
<thead><tr><th>Option</th><th>How it works</th><th>Good to know</th></tr></thead>
<tbody>
<tr><td><strong>eSIM</strong></td><td>Install it on your phone. It works as soon as you switch it on.</td><td>Needs an eSIM-ready, unlocked phone. No counter or queue.</td></tr>
<tr><td><strong>Free Wi-Fi</strong></td><td>JR-EAST Free Wi-Fi at the JR EAST Travel Service Center, and &ldquo;Shinjuku-Bus-Terminal_Free_Wi-Fi&rdquo; at Busta Shinjuku.</td><td>Busta's Wi-Fi asks you to register an email address. Fine for a quick message, not for a day of maps.</td></tr>
<tr><td><strong>SIM card or eSIM at a counter</strong></td><td>The Odakyū Sightseeing Service Center (West side, 8:00 to 16:00) sells SIM cards and eSIMs.</td><td>We did not find other official SIM or Wi-Fi rental counters in the station.</td></tr>
<tr><td><strong>Phone charging</strong></td><td>Busta Shinjuku has coin-operated phone chargers beside the ticket machines on the north side.</td><td>&yen;100 per 20 minutes, according to Busta.</td></tr>
</tbody>
</table>
</div>
""" + sources(["jrtsc", "busta", "odakyu"])

# ---- partner placements: none on this page (no Klook, no Japan Bullet Train). KLK stays empty, so klp() renders nothing.
KLK = {}


def klp(key, text):
    link = KLK.get(key, "")
    if not link:
        return ""
    return ('<p data-ps-placement="%s">%s, a partner link. Check the listing for the current price and terms: '
            '<a href="%s" target="_blank" rel="nofollow noopener sponsored">see the listing</a>.</p>' % (key, text, link))
KL_ROWS = []
KLOOK_TRANSPORT = ""

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
<div id="psPocketBar" role="region" aria-label="Shinjuku Station Pocket Guide">
<div class="t"><b>Get the Shinjuku Station Pocket Guide</b><span>Free. Works offline at the station.</span></div>
<a class="go" href="/shinjuku-pocket?src=bar">Get it</a>
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
<p>Open the Shinjuku Station Pocket Guide once while you have signal, then add it to your home screen. At the station it opens like an app, even with no connection.</p>
<p><a class="ps-btn2" href="/shinjuku-pocket?src=box" onclick="try{window.gtag&&gtag('event','pocket_prompt',{event_category:'engagement',action:'open_box',page_path:location.pathname});}catch(e){}" style="display:inline-block;text-decoration:none;">Open the Pocket Guide</a></p>
<ul>
<li><strong>iPhone:</strong> open it in Safari, tap the Share button, then "Add to Home Screen".</li>
<li><strong>Android:</strong> open it in Chrome, tap the menu (three dots), then "Add to Home screen" or "Install app".</li>
</ul>
</div>"""

FACILITIES = """<h2 id="facilities">Facilities in the station</h2>
<p>This table follows JR East, Tokyo Metro, Busta Shinjuku, GO TOKYO and Odakyū pages, checked on 22 November 2026. A dash means the pages we read do not list one. Hours are as printed on those pages and can change.</p>
<div class="ps-scroll">
<table class="checklist-table">
<thead><tr><th>Facility</th><th>What we found</th></tr></thead>
<tbody>
<tr><td><strong>JR EAST Travel Service Center</strong></td><td>On the right after the New South Ticket Gate (2F). 8:00 to 19:00, open all year. Passes and tickets, tickets booked on JR-EAST Train Reservation, tourist information, Shinjuku maps, Travelex currency exchange, JR-EAST Free Wi-Fi. Cards: JCB, Visa, Mastercard, American Express, Diners Club, Discover</td></tr>
<tr><td><strong>English information (JR East)</strong></td><td>2F South Gate: 10:00 to 18:00 inside the gates, 10:00 to 17:00 outside. B1 West Gate, inside: 10:00 to 17:00</td></tr>
<tr><td><strong>JR ticket office</strong></td><td>Midori-no-madoguchi, beside the B1 Free Passage near the West Gate</td></tr>
<tr><td><strong>Busta Shinjuku</strong></td><td>Departures 4F, arrivals 3F, station level 2F. Waiting room 3:30 to 25:00. Information counter 7:00 to 23:00. Coin lockers (4F), Seven Bank ATM, convenience store (3:30 to 25:00), wheelchair-accessible toilets with ostomate facilities, nursing room, free Wi-Fi</td></tr>
<tr><td><strong>Tokyo Tourist Information Center</strong></td><td>Busta 3F, 6:30 to 21:00, seven days a week. Parcel delivery, temporary safekeeping and ticket sales</td></tr>
<tr><td><strong>Odakyū Sightseeing Service Center, Shinjuku West</strong></td><td>Odakyū B1, West Underground Exit. 8:00 to 16:00, 365 days a year. Hakone information, Romancecar tickets and passes, baggage storage (pick-up until 19:00), currency exchange, SIM cards and eSIMs</td></tr>
<tr><td><strong>JR coin lockers</strong></td><td>Several on JR East's map. No official prices found</td></tr>
<tr><td><strong>Toilets, lifts, nursery</strong></td><td>Restrooms, accessible facilities, a nursery symbol and lifts A to O are on JR East's map. In the Metro station, toilets, an accessible toilet and a baby room near exit A8 (Tokyo Metro)</td></tr>
<tr><td><strong>Food</strong></td><td>-</td></tr>
</tbody>
</table>
</div>
<h3>If you need help</h3>
<p>If you are tired, unsure or carrying a lot, go straight to an information desk or a staff member instead of searching on your own.</p>
""" + sources(["jrmap", "jrtsc", "metro", "busta", "tic", "odakyu"], "Opening hours can change.")

JB_LINK = "https://www.japan-bullettrain.com/?via=packsmart"
JB_SHIN = '<svg style="display:block;width:100%;height:auto;" aria-hidden="true" focusable="false" viewBox="0 0 320 170" xmlns="http://www.w3.org/2000/svg"><rect width="320" height="170" fill="#E8F1FE"/><circle cx="64" cy="40" r="20" fill="#FFE3CC"/><path d="M120 120 L188 44 L204 60 L214 52 L282 120Z" fill="#b9cdf0"/><path d="M174 62 L188 44 L204 60 L196 64 L188 58 L181 66Z" fill="#fff"/><path d="M0 124 L60 96 L110 120 L150 104 L200 124Z" fill="#d3e0f7"/><g fill="#f7b9cf"><circle cx="262" cy="104" r="14"/><circle cx="276" cy="112" r="12"/><circle cx="250" cy="114" r="11"/></g><rect x="260" y="112" width="4" height="22" fill="#8b5a3c"/><rect y="132" width="320" height="38" fill="#d3e0f7"/><rect y="146" width="320" height="4" fill="#9db8e6"/><g><path d="M14 138 L14 110 C14 104 20 100 28 100 L214 100 C250 100 286 118 306 138 Z" fill="#fff" stroke="#0f0f23" stroke-width="2.5"/><path d="M14 124 L300 124 L304 130 L14 130Z" fill="#2563EB"/><g fill="#7fb4f5" stroke="#0f0f23" stroke-width="1.5"><rect x="34" y="106" width="20" height="11" rx="2"/><rect x="62" y="106" width="20" height="11" rx="2"/><rect x="90" y="106" width="20" height="11" rx="2"/><rect x="118" y="106" width="20" height="11" rx="2"/><rect x="146" y="106" width="20" height="11" rx="2"/><rect x="174" y="106" width="20" height="11" rx="2"/></g><path d="M214 101 C238 102 262 112 282 124 L214 124Z" fill="#0f0f23" opacity=".9"/><g fill="#0f0f23"><circle cx="60" cy="140" r="5"/><circle cx="104" cy="140" r="5"/><circle cx="200" cy="140" r="5"/><circle cx="244" cy="140" r="5"/></g></g><g stroke="#2563EB" stroke-width="3" stroke-linecap="round"><path d="M4 108h22"/><path d="M0 118h16"/><path d="M6 128h12"/></g></svg>'
JB_TRAIN = '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M5 16V8a5 5 0 0 1 5-5h4a5 5 0 0 1 5 5v8a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2z"/><path d="M5 11h14M9 15h.01M15 15h.01M8 18l-2 3M16 18l2 3"/></svg>'


def jb_node(text):
    return '<div class="jb-rn"><span class="jb-dot"></span><strong style="color:#0f0f23;font-size:1rem;">%s</strong></div>' % text


def jb_leg(text, icon="", blue=False):
    return '<div class="jb-lg%s"><span class="jb-ln"></span><span class="jb-lt">%s%s</span></div>' % (" jb-blue" if blue else "", icon, text)


JB_SHINKANSEN = (
    '<div data-ps-placement="jw-shinkansen-shinjuku" style="max-width:800px;margin:20px auto;padding:20px;background:#f0faf7;border:1px solid #cdeee5;border-left:4px solid #00C9A7;border-radius:12px;">'
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
    '<strong style="display:block;font-size:1.1rem;color:#0f0f23;margin:0 0 12px;">Going on to Kyoto or Osaka by bullet train?</strong>'
    '<div class="jb-grid">'
    '<a href="' + JB_LINK + '" target="_blank" rel="nofollow noopener sponsored" tabindex="-1" aria-hidden="true" style="display:block;border-radius:12px;overflow:hidden;">' + JB_SHIN + '</a>'
    '<div>'
    + jb_node("Shinjuku") + jb_leg("JR Chūō Line (Rapid), platforms 7 and 8") + jb_node("Tokyo Station") + jb_leg("Shinkansen (bullet train)", JB_TRAIN, True) + jb_node("Kyoto") + jb_node("Osaka") +
    '</div></div>'
    '<div class="jb-row"><div class="jb-tx">'
    '<p style="margin:0 0 8px;font-size:0.95rem;line-height:1.5;color:#333;">There is no Shinkansen at Shinjuku: JR East&rsquo;s platform list for the station has none. For Kyoto and Osaka, take the JR Chūō Line (Rapid) from platform 7 or 8 to Tokyo Station (about 14 minutes, according to GO TOKYO), where Shinkansen run west to Nagoya, Kyoto and Shin-Osaka. If you want your tickets sorted before you travel, you can book them online. The company says its tickets cover the JR East, JR West, JR Central and JR Kyushu Shinkansen lines and are collected with a QR code.</p>'
    '</div><div class="jb-bt">'
    '<a class="ps-jb-btn" href="' + JB_LINK + '" target="_blank" rel="nofollow noopener sponsored" style="display:block;box-sizing:border-box;text-decoration:none;"><span class="ps-jb-ghost" style="display:block;border:1.5px solid #00C9A7;background:#fff;color:#0a8f78;text-align:center;font-weight:700;font-size:1rem;border-radius:12px;padding:11px 14px;min-height:46px;line-height:1.25;">Book Shinkansen tickets &rarr;</span><span style="display:block;text-align:center;font-size:0.76rem;color:#777;margin-top:6px;">Japan Bullet Train &middot; partner link</span></a>'
    '<p style="margin:10px 0 0;font-size:0.85rem;line-height:1.5;color:#555;">You can also buy at a station on the day, so check the price and the change and cancellation rules before you pay.</p>'
    '</div></div></div>'
)


# ---- GetYourGuide day-trip widget (same widget and tour IDs as the "Mt Fuji" tab of the Japan 7-day itinerary,
#      partner D7IXONS, its own cmp so clicks can be told apart). Hides itself if the widget does not load.
GYG_PARTNER = "D7IXONS"
GYG_CSS = """<style>
.ps-gyg{margin:24px 0;font-family:"DM Sans",sans-serif}
.ps-gyg-h{display:block;text-align:center;font-size:1.05rem;font-weight:700;color:#0f0f23;margin:0 0 4px}
.ps-gyg-s{text-align:center;font-size:.85rem;color:#3f7f70;margin:0 0 14px}
.ps-gyg-w{min-height:495px;margin-bottom:-30px}
@media(max-width:600px){.ps-gyg-w{min-height:772px;margin-bottom:0}}
</style>"""
GYG_HEAD = ('<script async defer src="https://widget.getyourguide.com/dist/pa.umd.production.min.js" data-gyg-partner-id="%s"></script>\n'
            '<style>[data-gyg-widget]{overflow:hidden!important} [data-gyg-widget]>span{display:none!important} '
            '[data-gyg-widget] iframe{clip-path:inset(0 0 35px 0)!important;margin-bottom:-35px!important}</style>' % GYG_PARTNER)

GYG_TPL = """<div class="ps-gyg" data-ps-placement="__PID__">
<strong class="ps-gyg-h">__HEAD__</strong>
<p class="ps-gyg-s">__BLURB__</p>
<div class="ps-gyg-w"><div class="ps-gyg-slot" data-gyg-href="https://widget.getyourguide.com/default/activities.frame" data-gyg-locale-code="en-US" data-gyg-number-of-items="__N__" data-gyg-partner-id="__PARTNER__"></div></div>
<script>
(function(){
var root=document.currentScript.parentNode;
var ids='__IDS__',cmp='__CMP__';
var slot=root.querySelector('.ps-gyg-slot'),phone=window.matchMedia('(max-width:600px)'),started=false;
function render(){
var a=ids.split(',');
slot.setAttribute('data-gyg-widget','activities');
slot.setAttribute('data-gyg-number-of-items',String(phone.matches?Math.min(2,a.length):a.length));
slot.setAttribute('data-gyg-tour-ids',(phone.matches?a.slice(0,2):a).join(','));
slot.setAttribute('data-gyg-cmp',cmp);
var t=0;(function go(){if(window.GYG&&window.GYG.refresh){window.GYG.refresh()}else if(t++<50){setTimeout(go,200)}})();}
function start(){if(started)return;started=true;render();var n=0;(function watch(){if(slot.querySelector('iframe'))return;if(++n>15){root.style.display='none';return}setTimeout(watch,1000)})()}
if('IntersectionObserver' in window){var io=new IntersectionObserver(function(e){if(e[0].isIntersecting){io.disconnect();start()}},{rootMargin:'400px 0px'});io.observe(root)}else{start()}
if(phone.addEventListener){phone.addEventListener('change',function(){if(started)render()})}
})();
</script>
</div>"""


def gyg(pid, head, blurb, ids, cmp):
    return (GYG_TPL.replace("__PID__", pid).replace("__HEAD__", esc(head)).replace("__BLURB__", esc(blurb))
            .replace("__N__", str(len(ids))).replace("__PARTNER__", GYG_PARTNER)
            .replace("__IDS__", ",".join(ids)).replace("__CMP__", cmp))


GYG_DAYTRIPS = gyg("gyg-shinjuku-daytrips", "Mt Fuji and Hakone day tours from Tokyo",
                   "Guided day trips you can book ahead, as listed by GetYourGuide.",
                   ["792363", "668266", "1226194"], "packsmart-shinjuku-daytrips")


DAYTRIPS = """<h2 id="daytrips">Day trips from Shinjuku</h2>
<ul>
<li><strong>Hakone by Romancecar (Odakyū).</strong> Odakyū says the Romancecar limited express runs direct from Shinjuku to Hakone-Yumoto in about 80 minutes. All seats are reserved, and you need a limited express ticket as well as a regular fare ticket. The Odakyū Sightseeing Service Center (B1, West Underground Exit, 8:00 to 16:00) sells Romancecar tickets and the Hakone Freepass, Hakone-Kamakura Pass and Fuji Hakone Pass.</li>
<li><strong>Kōfu and Matsumoto (JR).</strong> The Chūō Line limited express uses platforms 9 and 10 (JR East's map).</li>
<li><strong>Takao (JR or Keiō).</strong> The JR Chūō Line (Rapid) for Nakano, Tachikawa and Takao uses platforms 11 and 12. Keiō says its line runs from Shinjuku to Takaosanguchi, for Mount Takao; use the Central West Gate (Keiō exit).</li>
</ul>
<p>We did not check times or fares for these trips beyond what is written here. Check the operator before you go.</p>
""" + sources(["romance", "odakyu", "jrmap", "keio"], "Times change, so check the operator.")

LEAVING = """<h2 id="leaving">Leaving Shinjuku: a checklist</h2>
<ul>
<li><strong>Flying from Narita?</strong> The last Narita Express from Shinjuku is at 19:39 (first 5:55), platforms 5 and 6. Airport Limousine Buses leave from Busta Shinjuku, 4F. See our <a href="/blog/narita-airport-guide">Narita Airport guide</a>.</li>
<li><strong>Flying from Haneda?</strong> Airport Limousine Buses leave from Busta Shinjuku, 4F, with an early-morning bus at 3:50. Check the last bus on the live timetable. See our <a href="/blog/haneda-airport-guide">Haneda Airport guide</a>.</li>
<li><strong>Early start for the bus?</strong> The New South Gate opens at 5:45 (Busta). Before then, use the South Gate.</li>
<li><strong>Collect your bags.</strong> Busta's coin lockers need the QR code on your receipt. The Odakyū center's bag pick-up ends at 19:00.</li>
<li><strong>Cash for the trip.</strong> The Seven Bank ATM in the Busta waiting room is open 3:30 to 25:00 (1 am).</li>
<li><strong>Allow time for the station itself.</strong> We did not find official walking times between gates and platforms, so add a buffer, especially with luggage.</li>
<li><strong>Going on by bullet train?</strong> JR East's list of Shinjuku platforms (1 to 16) has no Shinkansen. See our <a href="/blog/tokyo-station-guide">Tokyo Station guide</a>.</li>
</ul>
""" + sources(["nex", "jrmap", "busta", "bustaacc", "limo", "odakyu"], "Times change, so check the operator.")
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
    '<p style="font-size:0.85rem;color:#666;margin:0 0 0.6rem;">Published November 22, 2026 · Last updated November 2026 · Facts checked 22 Nov 2026</p>',
    AFFILIATE_P,
    share,
    PRINT_CSS,
    '<p>Shinjuku Station has gates on two levels and several railway companies, and it is easy to come out on the wrong side. The Narita Express, the airport buses, the Odakyū and Keiō lines and the Metro all use different parts of it. '
    'This guide is written in plain English so that a first-time visitor, a family or an older traveller can follow it step by step. '
    'You can print the one-page card below and carry it with you.</p>',
    toc_html,
    CARD,
    WHICH,
    DIAGRAM,
    EXITS,
    PLATFORMS,
    NARITA,
    LINES,
    MONEY,
    CONNECTED,
    airalo,
    LUGGAGE,
    FINDER,
    SAVE_BOX,
    FACILITIES,
    HELP,
    DAYTRIPS,
    GYG_DAYTRIPS,
    JB_SHINKANSEN,
    LEAVING,
    '<div class="tip-box">\n    <strong>Planning more of Japan?</strong> Our <a href="/blog/japan-travel-packing-guide">Japan travel and packing guide</a> covers what to pack, rail passes, etiquette and a budget breakdown, and the <a href="/blog/japan-7-day-itinerary-budget">7-day Japan itinerary</a> shows how a first week can look. Flying out? See our <a href="/blog/narita-airport-guide">Narita Airport guide</a> or <a href="/blog/haneda-airport-guide">Haneda Airport guide</a>.\n</div>',
    "<!-- FIRST-HAND NOTES: add notes and photos from a Shinjuku Station visit here -->",
    faq_html(),
    ABOUT,
    RELATED,
    POCKET_BAR,
])
# hero button: a quiet way into the Pocket Guide from the top of the article (as w42)
HERO_CTA = ('        <div style="margin:48px 0 0;text-align:center;">'
            '<a href="/shinjuku-pocket?src=hero" onclick="try{window.gtag&&gtag(\'event\',\'pocket_prompt\',{event_category:\'engagement\',action:\'open_hero\',page_path:location.pathname});}catch(e){}" '
            'style="display:inline-flex;align-items:center;gap:12px;background:#00C9A7;color:#0f0f23;text-align:left;padding:12px 14px 12px 20px;width:340px;max-width:100%;box-sizing:border-box;border-radius:12px;text-decoration:none;min-height:44px;box-shadow:0 6px 18px rgba(0,0,0,.28);line-height:1.2;">'
            '<span style="flex:1;min-width:0;text-align:left;">'
            '<span style="display:block;font-weight:700;font-size:0.8rem;opacity:0.8;">Save to your phone</span>'
            '<span style="display:block;font-weight:800;font-size:1.05rem;margin-top:2px;">Shinjuku Station Pocket Guide</span>'
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
    GYG_HEAD,
    GYG_CSS,
    "</head>",
    "<body>",
    "\n".join(t[NAV0:NAV1 + 1]),
    "",
    ('    <div class="hero-blog" style="position:relative; background: linear-gradient(rgba(15,15,35,0.62), rgba(26,26,62,0.72)), url(\'%s\'); background-size: cover; background-position: center 40%%;">' % HERO_URL) if HERO_URL else '    <div class="hero-blog" style="position:relative; background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 100%);">',
    "        <h1>%s</h1>" % esc(H1),
    '        <div class="meta">Station Guide • Japan · Published 22 Nov 2026 · 9 min read</div>',
    HERO_CTA,
    ('        <div style="position:absolute;left:12px;right:12px;bottom:8px;font-size:0.7rem;opacity:0.7;text-align:center;">Photo: PAKUTASO. Illustrative image of the JR Shinjuku Station South exit.</div>' if HERO_URL else ''),
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



# ---- Shinjuku Station Pocket Guide: standalone page + service worker + manifest (works offline once visited)
POCKET_PATH = "/shinjuku-pocket"
THEME = "#6b4fb3"   # violet, one colour per guide
# ---- Pocket Guide analytics (v47): anonymous taps only, no accounts, honours Do Not Track / GPC
GUIDE_ID = "shinjuku"
AIRPORT_CODE = "SHINJUKU-STN"
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
    if(/^tel:/i.test(h)){ var d=h.replace(/^tel:/i,'').replace(/[^0-9+]/g,''); var nm={'119':'fire_ambulance','110':'police','+815038162787':'help_line','+81359090211':'odakyu_center'}; pgTrack('pg_call',{dest:nm[d]||d,where:whereNow()}); return; }
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

POCKET_SVG = re.search(r'<svg id="shjDiagram".*?</svg>', DIAGRAM, re.S).group(0).replace('id="shjDiagram"', 'id="pkDiagram"').replace('id="shjT"', 'id="pkT"').replace('id="shjD"', 'id="pkD"').replace('aria-labelledby="shjT shjD"', 'aria-labelledby="pkT pkD"')
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
<title>Shinjuku Station Pocket Guide | PackSmart</title>
<meta name="description" content="A simple Shinjuku Station helper that works offline: West and East sides, which exit, the last Narita Express, airport buses, ATMs, lockers and more. By PackSmart.">
<meta name="robots" content="noindex,follow">
<link rel="canonical" href="__GUIDE_URL__">
<meta name="theme-color" content="#1a1a3e">
<link rel="manifest" href="/shinjuku-pocket.webmanifest">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" href="/images/shinjuku-apple-touch-180.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Shinjuku">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<script>__PG_BOOT__</script>
<style>__CSS__</style>
</head>
<body>
<header class="top">
<div><strong>Shinjuku Station Pocket Guide</strong><span class="by">by PackSmart &middot; 22 Nov 2026</span></div>
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
<p class="lead2" id="mLead" style="margin-top:10px">Airport buses: the South side (New South Gate, 2F). Odakyū and Keiō: the West side.</p>
<div class="tmap" id="tmap">
<div class="tcard t1" data-t="T1"><div class="badge">&#127963;&#65039;</div><div class="tb"><h3>West side</h3><p>West Gate and Central West Gate (B1). Odakyū, Keiō and Toei lines, West exit bus stop, Metropolitan Government Building</p><p class="stn"><span aria-hidden="true">&#128649;</span> Keiō: Central West Gate, 6:00 to last train</p></div></div>
<div class="tlink"><span aria-hidden="true">&#128694;</span><span>Walk between East and West<br>by the B1 Free Passage, outside the gates</span></div>
<div class="tcard t2" data-t="T2"><div class="badge">&#128652;</div><div class="tb"><h3>East and South side</h3><p>East: East Gate, Central East Gate (B1), Kabukichō, Seibu-Shinjuku. South (2F): South, Southeast, Kōshū-kaidō, New South and Miraina Tower gates, Busta Shinjuku, Travel Service Center</p><p class="stn"><span aria-hidden="true">&#128652;</span> Airport buses: Busta 4F, via the New South Gate</p></div></div>
</div>
<p class="small" style="text-align:center;margin-top:10px">Simplified, not to scale. Station layouts change, so follow the signs.</p>
</section>
<section class="panel" id="p-arrive" role="tabpanel" aria-labelledby="t-arrive" hidden>
<p class="lead2">Just arrived at Shinjuku? Tap a step to tick it off.</p>
<ol class="steps" id="arrSteps"></ol>
<button type="button" class="reset" id="arrReset" hidden>Clear ticks</button>
<p class="sec-h">Then, once you are out</p>
<div class="tiles" id="arrTiles"></div>
</section>
<section class="panel" id="p-depart" role="tabpanel" aria-labelledby="t-depart" hidden>
<div class="heroline"><span class="big2">19:39</span><span><b>Last Narita Express from Shinjuku.</b><br>Every day. First 5:55. Platforms 5 and 6. Times change, so check.</span></div>
<div class="seg2" id="depSeg" role="group" aria-label="Departure sections"><button type="button" data-d="before" aria-pressed="true">Before you go</button><button type="button" data-d="air" aria-pressed="false">At the station</button></div>
<div id="depBefore">
<div class="tiles" id="depTiles"></div>
<p class="hint">Tap one for the details. Prices and times are approximate.</p>
</div>
<div id="depAir" hidden>
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
<p class="small" style="margin-top:0">English information (JR East): 2F South Gate, 10:00 to 18:00 inside the gates, 10:00 to 17:00 outside; B1 West Gate, inside, 10:00 to 17:00. Busta information counter: 7:00 to 23:00. Staff will help, so just ask.</p>
<a class="num air" href="tel:+81359090211"><span class="ni" aria-hidden="true">&#128649;</span><span class="nt"><b>Odakyū Sightseeing Service Center</b><span>+81-3-5909-0211</span><small>8:00 to 16:00. Hakone, Romancecar, bags</small></span></a>
<p class="sec-h">Help or travel questions</p>
<a class="num hot" href="tel:+815038162787"><span class="ni" aria-hidden="true">&#128222;</span><span class="nt"><b>Japan Visitor Hotline</b><span>050-3816-2787</span><small>24 hours. English, Chinese, Korean</small></span></a>
</div>
<div class="tiles hnav" id="hnav2"></div>
</div>
</div></div>
<div class="quiet"><div class="card slim" id="shareCard" hidden><div class="row"><div><h2>Helping someone travel?</h2><p>Send them this guide for offline use.</p></div><button type="button" class="big" id="shareBtn">Send it</button></div></div>
<div class="card slim install" id="install"><div class="row"><div><h2>Keep this on your phone</h2><p>Add it to your home screen. Works offline.</p><p class="small" id="instDesk">Open this page on your phone, then add it to your home screen.</p></div><div id="instHow" hidden><button type="button" class="big" id="instBtn">Show me</button></div></div></div>
<p class="small">Facility details come from JR East, Tokyo Metro, Busta Shinjuku, GO TOKYO, the Airport Limousine Bus and Odakyū pages, checked 22 November 2026. Floors, opening hours and counters can change. If you cannot find something, ask station staff. Found something out of date? <a href="/contact">Tell us</a> (needs internet). We count anonymous taps to improve this guide: no name, no account. <a href="/privacy-policy">Privacy</a> &middot; <a href="#" id="pgOpt">Turn off counting</a>. The full guide, with platforms, exits and luggage, is at <a href="__GUIDE_URL__">packsmartapp.com</a> (needs internet).</p></div>
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
  var ICON={prayer:'\\uD83D\\uDE4F',baby:'\\uD83C\\uDF7C',quiet:'\\uD83E\\uDD2B',info:'\\u2139\\uFE0F',help:'\\u267F',lockers:'\\uD83E\\uDDF3',wifi:'\\uD83D\\uDCF6',shower:'\\uD83D\\uDEBF',internet:'\\uD83D\\uDCBB',play:'\\uD83E\\uDDF8',smoking:'\\uD83D\\uDEAC',toilet:'\\uD83D\\uDEBB',food:'\\uD83C\\uDF5C',money:'\\uD83D\\uDCB4',unwell:'\\uD83C\\uDFE5',pharmacy:'\\uD83D\\uDC8A',trains:'\\uD83D\\uDE86',tickets:'\\uD83C\\uDFAB',phone:'\\uD83D\\uDCF6',charge:'\\uD83D\\uDD0B',exits:'\\uD83D\\uDEAA',more:'\\u2795'};
  var SHORT={prayer:'Prayer room',baby:'Nursing room',quiet:'Quiet space',info:'Information counter',help:'Wheelchair and help',lockers:'Luggage',wifi:'Wi-Fi rental',shower:'Showers',internet:'Free internet',play:'Kids play area',smoking:'Smoking room',toilet:'Toilets',food:'Food and drink',money:'Money and ATMs',unwell:'Feeling unwell',pharmacy:'Pharmacy',trains:'Trains and buses',tickets:'Tickets and passes',phone:'Phone and Wi-Fi',charge:'Phone charging',exits:'Which exit?',more:'More places'};
  var term='ALL', lastTile=null;
  try{ var s=localStorage.getItem('sjkTerm'); if(s&&/^(ALL|T1|T2)$/.test(s)) term=s; }catch(e){}
  function $(id){return document.getElementById(id);}
  /* side selector */
  var seg=$('seg');
  function segBtn(id,html,cls){
    var b=document.createElement('button'); b.type='button'; b.setAttribute('data-t',id); if(cls) b.className=cls;
    b.innerHTML=html; b.addEventListener('click',function(){ term=id; try{localStorage.setItem('sjkTerm',id);}catch(e){} paintSeg(); renderDep(); }); return b;
  }
  var CAP={T1:'Odaky\\u016B, Kei\\u014D',T2:'Busta, Kabukich\\u014D'};
  D.terms.forEach(function(t){ seg.appendChild(segBtn(t[0],'<small>'+CAP[t[0]]+'</small><b>'+t[1]+'</b>')); });
  seg.appendChild(segBtn('ALL','Not sure','txt'));
  var mseg=$('mseg');
  D.terms.forEach(function(t){ mseg.appendChild(segBtn(t[0],'<small>'+CAP[t[0]]+'</small><b>'+t[1]+'</b>')); });
  mseg.appendChild(segBtn('ALL','Not sure','txt'));
  function paintSeg(){ [seg,mseg].forEach(function(g){ [].forEach.call(g.children,function(b){ b.setAttribute('aria-pressed',b.getAttribute('data-t')===term?'true':'false'); }); }); paintMap(); }
  /* Sides tab: personal view for the side the person chose */
  function paintMap(){
    var S={T1:8,T2:9,T3:0};
    var R={T1:{T2:'East: the B1 Free Passage, outside the ticket gates. The south gates and Busta are on 2F'},T2:{T1:'West: the B1 Free Passage, outside the ticket gates'}};
    var personal=(term==='T1'||term==='T2');
    $('mLead').textContent=personal?('You are on the '+(term==='T1'?'West':'East and South')+' side. Here is how to reach the other side.'):'Airport buses: the South side (New South Gate, 2F). Odakyū and Keiō: the West side.';
    [].forEach.call(document.querySelectorAll('#tmap .tlink'),function(e){ e.hidden=personal; });
    [].forEach.call(document.querySelectorAll('#tmap .tcard'),function(c){
      var id=c.getAttribute('data-t'), tb=c.querySelector('.tb');
      [].forEach.call(c.querySelectorAll('.heretag,.route'),function(e){ e.parentNode.removeChild(e); });
      c.classList.toggle('here',personal&&id===term);
      if(!personal) return;
      if(id===term){ var g=document.createElement('p'); g.className='heretag'; g.textContent='You are here'; tb.insertBefore(g,tb.firstChild); }
      else { var r=document.createElement('p'); r.className='route'; r.textContent='\\uD83D\\uDEB6 To the '+R[term][id]; tb.appendChild(r); }
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
  var phoneIt=['phone','Phone and Wi-Fi',{}];
  D.terms.forEach(function(t){ phoneIt[2][t[0]]=item('wifi')[2][t[0]]; });
  var trainsIt=['trains','Trains, Metro and buses',{}];
  var exitsIt=['exits','Which exit?',{}];
  var LIST=[];
  ['exits','money','toilet','lockers','info','tickets','trains','help','baby','phone','food','unwell'].forEach(function(id){
    LIST.push(id==='trains'?trainsIt:id==='exits'?exitsIt:id==='phone'?phoneIt:item(id));
  });
  LIST.forEach(function(it,n){
    var b=document.createElement('button'); b.type='button'; b.className='tile c'+(n%3); b.setAttribute('data-id',it[0]);
    var ic=document.createElement('span'); ic.className='ic'; ic.setAttribute('aria-hidden','true'); ic.textContent=ICON[it[0]]||'\\u2022';
    var tx=document.createElement('span'); tx.className='tx'; tx.textContent=SHORT[it[0]]||it[1];
    b.appendChild(ic); b.appendChild(tx);
    b.addEventListener('click',function(){ if(it[0]==='trains'){ openInfo(ICON.trains,it[1],trainHTML(),b); } else if(it[0]==='exits'){ openInfo(ICON.exits,it[1],exitHTML(),b); } else { openSheet(it,b); } });
    (n<MAIN?tiles:tiles2).appendChild(b);
    if(n===MAIN-1){ tiles.appendChild(pill('pgnext','\\u2192','More','Nursing room, Wi-Fi, food, feeling unwell',function(){ slideTo(1); })); }
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
    else if(term==='ALL'){ D.terms.forEach(function(t){ shB.appendChild(ans(t[1]+' side',it[2][t[0]],true)); }); }
    else { var tn=D.terms.filter(function(t){return t[0]===term;})[0][1]; shB.appendChild(ans(tn+' side',it[2][term],false)); }
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
    var h='<p class="n2">JR platforms (JR East station map). Check the board: platforms can change.</p>';
    h+='<ul class="pl"><li><b>1 to 4:</b> Saikyō and Shōnan-Shinjuku lines.</li>'
      +'<li><b>5 and 6:</b> Narita Express (also the Tōbu Line direct limited express).</li>'
      +'<li><b>7 and 8:</b> Chūō Line (Rapid) for Ochanomizu and Tokyo.</li>'
      +'<li><b>9 and 10:</b> Chūō Line limited express for Kōfu and Matsumoto.</li>'
      +'<li><b>11 and 12:</b> Chūō Line (Rapid) for Nakano, Tachikawa and Takao.</li>'
      +'<li><b>13:</b> Chūō-Sōbu Line (Local) for Suidōbashi, Akihabara and Chiba.</li>'
      +'<li><b>14:</b> Yamanote Line for Harajuku, Shibuya and Shinagawa.</li>'
      +'<li><b>15:</b> Yamanote Line for Ikebukuro, Tabata and Ueno.</li>'
      +'<li><b>16:</b> Chūō-Sōbu Line (Local) for Higashi-Nakano, Nakano and Mitaka.</li></ul>';
    h+='<ul class="pl"><li><b>Odakyū and Keiō:</b> West side, B1. Keiō by the Central West Gate (6:00 to the last train).</li>'
      +'<li><b>Toei Shinjuku and Ōedo lines:</b> B1, via the Central West Gate area.</li>'
      +'<li><b>Metro Marunouchi Line (M08):</b> B2F, via the East side. Many Metro exits are closed during construction. Follow the signs.</li>'
      +'<li><b>Buses:</b> airport and expressway buses from Busta Shinjuku, 4F (New South Gate, 2F). Also a West exit bus stop.</li></ul>';
    h+='<p class="sm">Source: JR East station map and Tokyo Metro, checked 22 November 2026. Routes change. Check the operator.</p>';
    return h;
  }
  function exitHTML(){
    return '<ul class="pl"><li><b>Busta Shinjuku (airport buses):</b> JR New South Gate, 2F, open 5:45 to 24:00. Otherwise the South Gate.</li>'
      +'<li><b>Tokyo Metropolitan Government Building:</b> West exit, about 10 min on foot. Free observation decks, 45th floor.</li>'
      +'<li><b>Godzilla head (Shinjuku Toho Building, Kabukichō):</b> East exit, about 5 min.</li>'
      +'<li><b>Kabukichō Tower:</b> about 7 min from the station, 1 min from Seibu-Shinjuku Station.</li>'
      +'<li><b>Odakyū Line and Odakyū Sightseeing Service Center:</b> West side, B1 West Underground Exit.</li>'
      +'<li><b>Keiō Line:</b> Central West Gate (Keiō exit), B1, 6:00 to the last train.</li>'
      +'<li><b>Toei Shinjuku and Ōedo lines:</b> Central West Gate area, B1.</li>'
      +'<li><b>Metro Marunouchi Line:</b> many exits are closed during construction. Follow the signs.</li>'
      +'<li><b>Taxi:</b> the taxi stop is on 3F, from the 2F New South Gate side.</li></ul>'
      +'<p class="sm">Source: GO TOKYO map (walking times), JR East, Busta Shinjuku, Odakyū and Tokyo Metro, checked 22 November 2026. Exits change during construction.</p>';
  }
  function sidesHTML(){
    return '<p class="n2">Shinjuku has gates on two levels: B1 (East, West, Central East, Central West) and 2F (South, Southeast, Kōshū-kaidō, New South, Miraina Tower).</p>'
      +'<ul class="pl"><li><b>West side:</b> Odakyū, Keiō and Toei lines, the West exit bus stop, the Metropolitan Government Building. English help inside the B1 West Gate.</li>'
      +'<li><b>East side:</b> Kabukichō and Seibu-Shinjuku. The Godzilla head is about 5 min from the east exit.</li>'
      +'<li><b>South (2F):</b> the New South Gate for Busta Shinjuku and the JR EAST Travel Service Center. The Southeast Gate is open 7:00 to 24:00.</li>'
      +'<li><b>Between East and West:</b> the B1 Free Passage, outside the ticket gates.</li></ul>';
  }
  function cardHTML(){
    return '<ul class="pl"><li><b>JR EAST Travel Service Center:</b> right after the New South Gate (2F), 8:00 to 19:00. East Japan passes and tickets, and tickets booked on JR-EAST Train Reservation. Cards: JCB, Visa, Mastercard, American Express, Diners Club, Discover.</li>'
      +'<li><b>JR ticket office:</b> beside the B1 Free Passage, near the West Gate.</li>'
      +'<li><b>Odakyū Sightseeing Service Center:</b> Romancecar tickets, Hakone Freepass, Hakone-Kamakura Pass, Fuji Hakone Pass. 8:00 to 16:00.</li>'
      +'<li><b>Airport Limousine tickets at Busta:</b> staffed office 4:20 to 22:50, machines 3:40 to 22:50.</li></ul>'
      +'<p class="sm">Source: JR East, Odakyū and Busta Shinjuku, checked 22 November 2026. Rules and prices change. Check before you buy.</p>';
  }
  function bagsHTML(){
    return '<ul class="pl"><li><b>Busta Shinjuku 4F coin lockers:</b> up to 72 hours. Small &yen;100 per 60 min, medium &yen;100 per 40 min, large &yen;100 per 30 min, then a 6-hour rate. Keep the receipt: its QR code opens the locker.</li>'
      +'<li><b>Tokyo Tourist Information Center, Busta 3F:</b> 6:30 to 21:00. Temporary safekeeping and parcel delivery.</li>'
      +'<li><b>Odakyū Sightseeing Service Center (West side):</b> bags 8:00 to 16:00, pick-up until 19:00.</li>'
      +'<li><b>JR coin lockers:</b> on JR East&rsquo;s map, but we did not find their prices.</li>'
      +'<li>Write down your hotel name, address and phone number. Keep medicines, valuables and chargers with you.</li></ul>'
      +'<p class="sm">Source: Busta Shinjuku, GO TOKYO, Odakyū and JR East, checked 22 November 2026. Hours change.</p>';
  }
  function simHTML(){
    return '<ul class="pl"><li><b>eSIM:</b> install it on your phone and switch it on when you need it. No counter, no queue.</li>'
      +'<li><b>Free Wi-Fi:</b> JR-EAST Free Wi-Fi at the Travel Service Center, and Shinjuku-Bus-Terminal_Free_Wi-Fi at Busta.</li>'
      +'<li><b>SIM cards and eSIMs:</b> sold at the Odakyū Sightseeing Service Center, 8:00 to 16:00.</li>'
      +'<li><b>Phone charging:</b> coin-operated chargers at Busta, beside the ticket machines.</li></ul>';
  }
  function onwardHTML(){
    return '<ul class="pl"><li><b>Hakone:</b> Odakyū Romancecar, direct to Hakone-Yumoto in about 80 min. All seats reserved: you need a limited express ticket and a regular fare ticket.</li>'
      +'<li><b>Kōfu and Matsumoto:</b> Chūō Line limited express, platforms 9 and 10.</li>'
      +'<li><b>Takao:</b> JR Chūō Line (Rapid), platforms 11 and 12, or the Keiō Line to Takaosanguchi (Central West Gate).</li>'
      +'<li><b>Narita Airport:</b> Narita Express, platforms 5 and 6, last at 19:39.</li>'
      +'<li><b>Bullet trains:</b> none from Shinjuku&rsquo;s JR platforms 1 to 16.</li></ul>'
      +'<p class="sm">Times are approximate and change. Check the operator.</p>'
      +'<p class="sm"><a href="/blog/tokyo-station-guide">Our Tokyo Station guide</a> (needs internet)</p>';
  }
  var NEXT=[['🚆','Trains and Metro',trainHTML],['🚪','Which exit?',exitHTML],['🧭','West or East?',sidesHTML],['🎫','Tickets and passes',cardHTML],['🧳','Luggage',bagsHTML],['📱','Phone data',simHTML],['🗺️','Day trips',onwardHTML]];
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
  var ARR=[['Find your side','West: Odakyū, Keiō, Toei lines, West exit buses. East: Kabukichō, Seibu-Shinjuku. South (2F): Busta Shinjuku and the Travel Service Center.'],
    ['Pick your gate','B1: East, West, Central East and Central West (Keiō exit). 2F: South, Southeast, Kōshū-kaidō, New South and Miraina Tower.'],
    ['Cross between sides','The B1 Free Passage links East and West, outside the ticket gates.'],
    ['Need help or storage','JR EAST Travel Service Center: right after the New South Gate, 2F, 8:00 to 19:00. Bags: Busta 4F coin lockers, or the Tourist Information Center on Busta 3F.']];
  var DEP=[['Know your platform','Narita Express: platforms 5 and 6 (last 19:39). Chūō limited express: 9 and 10. Yamanote: 14 and 15. Check the board.'],
    ['Pick your gate','Airport buses: Busta 4F, through the New South Gate (5:45 to 24:00, otherwise the South Gate). Keiō: Central West Gate. Odakyū: West side.'],
    ['Bags','Busta 4F coin lockers need the QR code on your receipt. The Odakyū center bag pick-up ends at 19:00.'],
    ['Allow walking time','We did not find official walking times between gates and platforms. Add a buffer with luggage.'],
    ['Go to your platform','Check the display for your train, and your ticket for your car and seat.']];
  function renderDep(){ renderSteps($('depSteps'),DEP,doneD); }
  renderSteps($('arrSteps'),ARR,doneA); renderDep();
  $('arrReset').addEventListener('click',function(){ doneA.length=0; renderSteps($('arrSteps'),ARR,doneA); syncReset(); });
  $('depReset').addEventListener('click',function(){ doneD.length=0; renderDep(); syncReset(); });
  /* departure: before you go */
  var GUIDE='__GUIDE_URL__';
  function more(a){ return '<p class="sm"><a href="'+GUIDE+a+'">More in the full guide</a> (needs internet)</p>'; }
  function nexHTML(){
    return '<p class="n2">The <b>last Narita Express</b> from Shinjuku leaves at <b>19:39</b>, every day. The first is at 5:55.</p>'
      +'<ul class="pl"><li><b>Platforms 5 and 6</b> (JR East&rsquo;s map).</li>'
      +'<li>Trains run to Narita Airport Terminal 1, via Terminal 2&middot;3.</li>'
      +'<li>Weekdays: 5:55, 6:34, 7:07, 7:27, 8:05, 9:05, 9:40, then about :08 and :38 each hour to 16:38, then 17:09, 17:39, 18:09, 18:39, 19:39.</li>'
      +'<li>Sample: 10:08 from Shinjuku, 11:27 at Terminal 1, about 80 min.</li></ul>'
      +'<p class="sm">Source: JR East timetable (edition 2612), checked 22 November 2026. Timetables change. Check JR East.</p>'
      +more('#narita');
  }
  function busHTML(){
    return '<ul class="pl"><li><b>Airport Limousine Bus:</b> from Busta Shinjuku, 4F. Go through the JR New South Gate (2F, 5:45 to 24:00), or the South Gate outside those hours.</li>'
      +'<li><b>Narita:</b> adult &yen;3,600, child &yen;1,800. Sample first bus 5:40, Terminal 1 at 7:10 (about 90 min).</li>'
      +'<li><b>Haneda:</b> an early-morning bus at 3:50. Late-night and early-morning fares are higher.</li>'
      +'<li><b>Tickets:</b> staffed office 4:20 to 22:50, machines 3:40 to 22:50.</li></ul>'
      +'<div class="tipbox">We did not verify the last buses. Check the live timetable before a late trip: <a href="https://www.limousinebus.co.jp/en/" target="_blank" rel="noopener">limousinebus.co.jp</a> (needs internet).</div>'
      +'<p class="sm">Source: Airport Limousine Bus and Busta Shinjuku, checked 22 November 2026. Times and fares change.</p>';
  }
  function passHTML(){
    return '<ul class="pl"><li><b>JR EAST Travel Service Center:</b> right after the New South Gate (2F), 8:00 to 19:00. East Japan passes and tickets.</li>'
      +'<li><b>JR ticket office:</b> beside the B1 Free Passage, near the West Gate.</li>'
      +'<li><b>Romancecar and Hakone passes:</b> Odakyū Sightseeing Service Center, 8:00 to 16:00.</li></ul>'
      +'<p class="sm">Hours and prices change. Confirm at the counter.</p>';
  }
  function allowHTML(){
    return '<p class="n2">Shinjuku has gates on two levels and several railway companies. Add a buffer for walking, gates and luggage.</p>'
      +'<ul class="pl"><li>The south gates and Busta are on 2F. The East and West gates are on B1.</li>'
      +'<li>The New South Gate opens at 5:45. Before then, use the South Gate for Busta.</li>'
      +'<li>Many Metro Marunouchi Line exits are closed during construction.</li>'
      +'<li>We did not find official walking times between gates and platforms, so we give none.</li></ul>'
      +'<p class="sm">Times are approximate and change. Check the operator.</p>';
  }
  var BEFORE=[['🚆','Last Narita Express',nexHTML],['🚌','Airport buses',busHTML],['🎫','Tickets and passes',passHTML],['⏱️','Allow time',allowHTML]];
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
  [].forEach.call(dseg.children,function(b){ b.addEventListener('click',function(){ var w=b.getAttribute('data-d'); try{localStorage.setItem('sjkDepSeg',w);}catch(e){} paintDep(w); }); });
  var dsv='before'; try{ var q=localStorage.getItem('sjkDepSeg'); if(q==='air'||q==='before') dsv=q; }catch(e){}
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
    navigator.serviceWorker.register('/shinjuku-sw.js',{scope:'/shinjuku-pocket',updateViaCache:'none'})
      .then(function(){ return navigator.serviceWorker.ready; })
      .then(function(){ return caches.has('shinjuku-pocket-v1'); })
      .then(function(ok){ saved=!!ok; if(!saved){ setTimeout(function(){ caches.has('shinjuku-pocket-v1').then(function(k){ saved=!!k; paint(); }); },2500);} paint(); })
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
  function needed(){ return mobile&&!standalone&&flag('sjkInstalled')!=='1'; }
  function refresh(){
    var n=needed(); strip.hidden=!n;
    $('instHow').hidden=!n; $('instDesk').hidden=mobile;
    if(standalone||flag('sjkInstalled')==='1'){ $('install').hidden=true; }
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
  function markInstalled(){ flag('sjkInstalled','1'); refresh(); }
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
    ['go','🏙️','Shinjuku Station?','これは新宿駅に行きますか？','Kore wa Shinjuku-eki ni ikimasu ka?','Does this go to Shinjuku Station?'],
    ['go','🛍️','Shibuya?','これは渋谷に行きますか？','Kore wa Shibuya ni ikimasu ka?','Does this go to Shibuya?'],
    ['go','✈️','Haneda Airport?','これは羽田空港に行きますか？','Kore wa Haneda-kuukou ni ikimasu ka?','Does this go to Haneda Airport?'],
    ['go','🛫','Narita Airport?','これは成田空港に行きますか？','Kore wa Narita-kuukou ni ikimasu ka?','Does this go to Narita Airport?'],
    ['go','🚉','Tokyo Station?','これは東京駅に行きますか？','Kore wa Toukyou-eki ni ikimasu ka?','Does this go to Tokyo Station?'],
    ['go','📞','Call a taxi','タクシーを呼んでください。','Takushii o yonde kudasai.','Please call a taxi.'],
    ['go','📍','Take me here','この住所までお願いします。','Kono juusho made onegai shimasu.','Please take me to this address. Show the address on your phone.'],
    ['go','🛑','Stop here','ここで止めてください。','Koko de tomete kudasai.','Please stop here.'],
    ['air','🎫','Ticket gate','改札はどこですか？','Kaisatsu wa doko desu ka?','Where is the ticket gate?'],
    ['air','🚆','Narita Express platform','成田エクスプレスのホームはどこですか？','Narita Ekusupuresu no hoomu wa doko desu ka?','Where is the Narita Express platform?'],
    ['air','🚌','Busta Shinjuku','バスタ新宿はどこですか？','Basuta Shinjuku wa doko desu ka?','Where is Busta Shinjuku (the bus terminal)?'],
    ['air','⬅️','West exit','西口はどこですか？','Nishiguchi wa doko desu ka?','Where is the West exit?'],
    ['air','➡️','East exit','東口はどこですか？','Higashiguchi wa doko desu ka?','Where is the East exit?'],
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
  var askCat='basics'; try{ var sc=localStorage.getItem('sjkAskCat'); if(sc&&ASKC.some(function(c){return c[0]===sc;})) askCat=sc; }catch(e){}
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
    b.addEventListener('click',function(){ askCat=c[0]; try{localStorage.setItem('sjkAskCat',c[0]);}catch(e){} paintAsk(); });
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
    $('shareBtn').addEventListener('click',function(){ try{ navigator.share({title:'Shinjuku Station Pocket Guide',url:location.origin+location.pathname+'?src=share'}); }catch(e){} });
  }
  window.addEventListener('beforeinstallprompt',function(e){ e.preventDefault(); dp=e; });
  window.addEventListener('appinstalled',function(){ pgTrack('pg_installed',{via:'browser'}); markInstalled(); if(!inst.hidden) closeSheet(); });
  /*__PG_HOOKS__*/
  refresh();
  if(needed()&&!flag('sjkIntro')&&AUTO_INSTALL_SHEET){ flag('sjkIntro','1'); setTimeout(function(){ if(sheet.hidden&&inst.hidden){ instVia='auto'; openInst(); } },700); }
})();
</script>
</body>
</html>
"""
POCKET_HTML = (POCKET_HTML.replace("__CSS__", POCKET_CSS).replace("__FINDER_JSON__", json.dumps(FINDER_DATA, ensure_ascii=False)).replace("__KLP_JSON__", json.dumps({k: v for k, v in KLK.items() if v}))
               .replace("__PG_BOOT__", PG_BOOT).replace("/*__PG_HOOKS__*/", PG_HOOKS).replace("__SVG__", POCKET_SVG).replace("__GUIDE_URL__", URL))
if re.search(r"\b(India|Indian|INR|Rs\.?|rupee|lakh|Aadhaar|UPI|VFS|BLS)\b|₹", re.sub(r"<script[^>]*>.*?</script>", "", POCKET_HTML, flags=re.S)):
    die("neutral-rule violation in the pocket guide")
for _bad in ("tokyo-pocket", "tokTerm", "tokInstalled", "Yaesu", "Marunouchi side", "Tokyo Station Pocket"):
    if _bad in POCKET_HTML or _bad in page:
        die("leftover Tokyo text in the Shinjuku pages: %r" % _bad)

POCKET_SW = """/* Shinjuku Station Pocket Guide service worker. Bump V when the page changes shape. */
var V='shinjuku-pocket-v1';
var PAGE='/shinjuku-pocket';
var SHELL=[PAGE,'/shinjuku-pocket.webmanifest','/favicon-32.png','/images/shinjuku-icon-192.png','/images/shinjuku-icon-512.png','/images/shinjuku-icon-maskable-512.png'];
self.addEventListener('install',function(e){
  e.waitUntil(caches.open(V).then(function(c){return c.addAll(SHELL);}).then(function(){return self.skipWaiting();}));
});
self.addEventListener('activate',function(e){
  e.waitUntil(caches.keys().then(function(ks){
    return Promise.all(ks.filter(function(k){return k.indexOf('shinjuku-pocket-')===0&&k!==V;}).map(function(k){return caches.delete(k);}));
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
    "name": "Shinjuku Station Pocket Guide",
    "short_name": "Shinjuku",
    "description": "A simple Shinjuku Station helper that works offline.",
    "start_url": POCKET_PATH,
    "scope": POCKET_PATH,
    "display": "standalone",
    "background_color": THEME,
    "theme_color": "#1a1a3e",
    "lang": "en",
    "icons": [
        {"src": "/images/shinjuku-icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
        {"src": "/images/shinjuku-icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
        {"src": "/images/shinjuku-icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ],
}, indent=2) + "\n"
PUB = os.path.join(ROOT, "public")
for _ic in ("shinjuku-icon-192.png", "shinjuku-icon-512.png", "shinjuku-icon-maskable-512.png", "shinjuku-apple-touch-180.png"):
    if not os.path.isfile(os.path.join(PUB, "images", _ic)):
        die("pocket guide icon missing: public/images/" + _ic + " (the service worker would fail to install without it)")

# ---- anchors for the Japan guide link and the sitemap: check everything before writing anything
MARK = "shinjuku-station-guide link"
jp = open(TEMPLATE, encoding="utf-8").read()
jp_new = jp
if MARK not in jp:
    anchor = re.search(r'(<!-- tokyo-' + r'station-guide link -->\s*<p>.*?</p>)', jp, re.S)
    if not anchor:
        die("anchor for the Japan guide link (Tokyo Station sentence) not found: run the Tokyo Station generator (w42) first")
    add = ('\n\n<!-- %s -->\n<p>Staying in Shinjuku? Our <a href="/blog/%s">Shinjuku Station guide</a> explains the West and East sides, which exit to use, '
           'the last Narita Express, airport buses from Busta Shinjuku, ATMs and luggage.</p>') % (MARK, SLUG)
    jp_new = jp.replace(anchor.group(1), anchor.group(1) + add, 1)

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
sm = rx.sub(lambda _m: _m.group(0) if re.search(r"<lastmod>([^<]*)", _m.group(0)).group(1) >= TODAY else _m.group(1) + TODAY + _m.group(2), sm, count=1)  # only move the date forward   # as w42: the Japan guide links to the new page

# ---- write (all checks passed)
changed = []
if HERO_URL:
    _hu, HERO_NOTE = prepare_hero(write=True)
    if _hu != HERO_URL:
        die("hero image could not be prepared as planned (%r)" % _hu)
if HERO_NOTE:
    changed.append(HERO_NOTE)
old = open(OUT, encoding="utf-8").read() if os.path.isfile(OUT) else None
if old != page:
    open(OUT, "w", encoding="utf-8").write(page)
    changed.append("shinjuku-station-guide.html (%s bytes)" % len(page.encode("utf-8")))
for _name, _content in (("shinjuku-pocket.html", POCKET_HTML), ("shinjuku-sw.js", POCKET_SW), ("shinjuku-pocket.webmanifest", POCKET_MANIFEST)):
    _p = os.path.join(PUB, _name)
    _old = open(_p, encoding="utf-8").read() if os.path.isfile(_p) else None
    if _old != _content:
        open(_p, "w", encoding="utf-8").write(_content)
        changed.append("%s (%s bytes)" % (_name, len(_content.encode("utf-8"))))
if jp_new != jp:
    open(TEMPLATE, "w", encoding="utf-8").write(jp_new)
    changed.append("japan-travel-packing-guide.html (link added)")
if sm != orig:
    open(SITEMAP, "w", encoding="utf-8").write(sm)
    changed.append("sitemap.xml")

print("changed:" if changed else "nothing to do (already applied)")
for c in changed:
    print("  - " + c)
