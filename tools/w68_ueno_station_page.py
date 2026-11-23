#!/usr/bin/env python3
"""
w68: new page /blog/ueno-station-guide + offline /ueno-pocket (neutral, plain-English station guide for Ueno Station).
Modelled on the Shinjuku Station generator (w58): same template, partner-block helpers, Sources list and Pocket Guide shell.

Run from the repo root (after w58):  python3 tools/w68_ueno_station_page.py
Then, as for the other guides: w53 (airport transfer and car blocks), w44-w49 (pocket chain, cross-links, hub,
trip picker), w55, w56, w59 (Travel Essentials card), w64 and w65.

Facts: ONLY from docs/research/ueno-sources.md (JR East station map from the owner's screenshots, Tokyo Metro, Keisei,
Ueno Park official pages; checked 23 November 2026). Anything not in that file is left out, or written as
"We did not find this on the official station pages. Please ask station staff." (_NONE). Tokyo Metro exit numbers are
not known, so people are routed by the JR gates and exits.

Partner blocks (no new programmes, no Klook): the eSIM tiles copied from the Japan guide (placement id renamed to
airalo-ueno-station), the bullet-train booking box (jw-shinkansen-ueno, Ueno has Shinkansen tracks 19 to 22),
a tours-and-tickets box with a search for Ueno (gyg-ueno-station, cmp ps-ueno-station-gyg) and the Tokyo luggage
storage callout (bags-ueno-station, the same tracked link as the Japan guide). KLK stays empty.

What it does (idempotent):
  1. Builds public/blog/ueno-station-guide.html from the site template taken from
     public/blog/japan-travel-packing-guide.html (head, CSS, nav, footer, tracking scripts) plus new body content.
  2. Builds public/ueno-pocket.html (offline Pocket Guide), ueno-sw.js and ueno-pocket.webmanifest
     (cache ueno-pocket-v1; later scripts bump it; storage prefix "uen", as w44 expects).
  3. Makes public/images/ueno-station-hero-1600.jpg from ueno-station-hero.jpg and ueno-park-sakura-1200.jpg from
     ueno-park-sakura.jpg (sips on a Mac, Pillow elsewhere; an existing copy is kept).
  4. Adds one sentence linking to the new page in the Japan guide (marker: ueno-station-guide link),
     right after the Shinjuku Station guide sentence that w58 adds.
  5. Adds the page to public/sitemap.xml and moves the Japan guide's lastmod forward (never back).
It does NOT touch public/travel-essentials.html (the hub card comes from w59).
Aborts without writing anything if an expected anchor is missing.
"""
import os, re, sys, json, html
from urllib.parse import quote

ROOT = os.getcwd()
BLOG = os.path.join(ROOT, "public", "blog")
SITEMAP = os.path.join(ROOT, "public", "sitemap.xml")
TEMPLATE = os.path.join(BLOG, "japan-travel-packing-guide.html")
OUT = os.path.join(BLOG, "ueno-station-guide.html")
SITE = "https://www.packsmartapp.com"
SLUG = "ueno-station-guide"
URL = "%s/blog/%s" % (SITE, SLUG)
TODAY = "2026-11-23"
READ_MIN = 10   # as the other station guides: a reference page people scan, not read end to end (w59 card uses the same)

TITLE = "Ueno Station Guide 2026: Exits, Skyliner to Narita, Ueno Park & Cherry Blossoms | PackSmart Blog"
H1 = "Ueno Station Guide 2026: Exits, Skyliner to Narita, Ueno Park and Cherry Blossoms"
DESC = ("Plain-English Ueno Station guide: which gate for Ueno Park, JR platforms by floor, the Skyliner to Narita "
        "(not JR's Narita Line), Metro, lockers and cherry blossoms.")
KEYWORDS = ("Ueno Station guide, Ueno Station exits, Ueno Station Park exit, Ueno Station platforms, Skyliner Ueno to Narita, "
            "Keisei Ueno, Ueno Park cherry blossoms, Ueno Station coin lockers, Ueno Station Shinkansen, Ueno Station lost and found")

# ---- official sources (docs/research/ueno-sources.md), checked 23 November 2026
CHECKED = "Checked 23 November 2026."
SRC = {
    "jrmap": ("https://www.jreast.co.jp/en/e/stations/e204.html", "JR East Ueno Station map"),
    "metro": ("https://www.tokyometro.jp/lang_en/station/ueno/index.html", "Tokyo Metro Ueno Station"),
    "sky": ("https://www.keisei.co.jp/keisei/tetudou/skyliner/us/index.php", "Keisei Skyliner"),
    "skyueno": ("https://www.keisei.co.jp/keisei/tetudou/skyliner/us/directions/ueno.php", "Keisei: Skyliner to Ueno"),
    "nippori": ("https://www.keisei.co.jp/keisei/tetudou/skyliner/us/traffic/nippori_transfer.php", "Keisei: transferring at Nippori"),
    "kstation": ("https://www.keisei.co.jp/keisei/tetudou/skyliner/us/traffic/station.php", "Keisei station maps"),
    "parkacc": ("https://www.kensetsu.metro.tokyo.lg.jp/jimusho/toubuk/ueno/access", "Ueno Park access (Tokyo Metropolitan Government)"),
    "parkabout": ("https://www.kensetsu.metro.tokyo.lg.jp/jimusho/toubuk/ueno/kouenannai", "About Ueno Park (Tokyo Metropolitan Government)"),
    "parkhi": ("https://www.kensetsu.metro.tokyo.lg.jp/jimusho/toubuk/ueno/midokoro", "Ueno Park highlights (Tokyo Metropolitan Government)"),
    "parkrules": ("https://www.kensetsu.metro.tokyo.lg.jp/jimusho/toubuk/ueno/rules", "Ueno Park rules (Tokyo Metropolitan Government)"),
    "tpa": ("https://www.tokyo-park.or.jp/park/ueno/index.html", "Tokyo Metropolitan Park Association: Ueno Park"),
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


airalo = block("airalo-japan").replace("airalo-japan", "airalo-ueno-station")
_a = "Install it before you fly, switch it on when you land. No airport SIM queue."
if _a not in airalo:
    die("airalo tagline not found")
airalo = airalo.replace(_a, "Install it on your phone and switch it on when you need it. No counter, no queue.")
# no partner names in our own words (D47): neutral labels on the eSIM tiles
for _o, _n in ((", opens Airalo", ", opens our eSIM partner"),
               ("Airalo asks you to verify your ID before you buy.", "The provider asks you to verify your ID before you buy.")):
    if _o not in airalo and _n not in airalo:   # the Japan guide may already carry the neutral wording (w65)
        die("eSIM block text not found: " + _o)
    airalo = airalo.replace(_o, _n)
# ---------------------------------------------------------------- body content
def esc(s):
    return html.escape(s, quote=False)


FAQ = [
    ("How do I get from Ueno to Narita Airport?",
     "Take the Keisei Skyliner from Keisei Ueno station, which is Keisei's own station, separate from JR Ueno. "
     "Keisei gives 41 minutes from Narita Airport Terminal 2·3 to Keisei Ueno on the Skyliner. "
     "We did not find the first and last Skyliner times on the pages we read, so check Keisei's timetable before you travel."),
    ("Does JR's Narita Line from Ueno go to Narita Airport?",
     "Do not rely on it for the airport. JR East's station map lists the Narita Line on tracks 10 to 12 \"for Matsudo, Toride, Mito & Narita\": "
     "that Narita is the city, not the airport. For Narita Airport, use the Keisei Skyliner from Keisei Ueno."),
    ("Is Keisei Ueno the same station as JR Ueno?",
     "No. Keisei Ueno is Keisei's own station. We did not find an official walking route between JR Ueno and Keisei Ueno, "
     "so follow the signs or ask station staff. Tokyo Metro lists Keisei as a transfer at Ueno, and the Ueno Park office says Keisei Ueno is 1 minute's walk from the park."),
    ("Can I change from the Skyliner to the JR lines at Nippori instead?",
     "Keisei says that with the \"Skyliner & Tokyo Subway Ticket\" or the \"Greater Tokyo Pass\" you cannot transfer at Nippori, so use Ueno. "
     "Changing to JR at Nippori also needs a JR ticket."),
    ("Which exit do I use for Ueno Park?",
     "Use the Park Gate or the Panda Bridge Exit, both on the 3rd floor. JR East's map marks the end of Panda Bridge \"for Ueno Park\". "
     "The park office gives a 2-minute walk from JR Ueno."),
    ("When are the cherry blossoms in Ueno Park?",
     "The park office says Ueno Park has about 1,200 cherry trees and that the blossoms last about two months, from the early-flowering kanzakura to the Somei-yoshino. "
     "The dates change every year, so check the official cherry blossom forecasts nearer the time. The park is open from 5:00 to 23:00, with no entry outside those hours."),
    ("Which platform is the Yamanote Line at Ueno?",
     "JR East's station map shows track 2 for Tabata, Ikebukuro and Shinjuku, and track 3 for Akihabara, Tokyo, Hamamatsucho and Shinagawa. Both are on the 2nd floor."),
    ("Where are the Shinkansen platforms at Ueno?",
     "Underground, on tracks 19 to 22 (floors B4 to B1). Tracks 19 and 20 are for the Tohoku, Yamagata, Akita, Hokkaido, Joetsu and Hokuriku Shinkansen, "
     "and tracks 21 and 22 for Tokyo. JR East's map shows a Transfer to Shinkansen gate inside the station on 1F, and lifts G and H to the Shinkansen platforms."),
    ("Where can I leave my luggage at Ueno Station?",
     "JR East's station map shows coin lockers on 1F (near the Main Exit and taxi side, and inside the gates by the Shinkansen transfer), "
     "on 2F (along the concourse to the Iriya Exit) and on 3F (by the Panda Bridge Exit and near the Iriya Gate). We did not find their sizes or prices."),
    ("Where is the lost and found at Ueno Station?",
     "JR East's map puts Lost & Found on 2F, near the stairs to the Panda Bridge Exit. For something lost on the Tokyo Metro, "
     "Tokyo Metro says: on the same day, ask the station office where you lost it; from the next day, contact the Lost and Found at Iidabashi Station or the Tokyo Metro Customer Relations Center."),
    ("Which Tokyo Metro lines stop at Ueno, and which exit should I use?",
     "The Ginza Line (G16) and the Hibiya Line (H18). We did not find Tokyo Metro's exit list, so this guide routes you by the JR gates: "
     "for Ueno Park, the Park Gate or Panda Bridge on 3F. The park office gives a 4-minute walk to the park from the Metro station."),
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
    "about": {"@type": "TrainStation", "name": "Ueno Station"},
}
ld_crumbs = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE},
        {"@type": "ListItem", "position": 2, "name": "Travel Essentials", "item": SITE + "/travel-essentials"},
        {"@type": "ListItem", "position": 3, "name": "Ueno Station Guide", "item": URL},
    ],
}


def ld(obj):
    return '<script type="application/ld+json">\n%s\n</script>' % json.dumps(obj, ensure_ascii=False)


TOC = [
    ("one-page", "Ueno Station on one page"),
    ("narita", "To Narita Airport: the Skyliner, not JR's Narita Line"),
    ("exits", "Which gate or exit for where?"),
    ("platforms", "JR platforms by floor"),
    ("metro", "Tokyo Metro: Ginza and Hibiya lines"),
    ("park", "Ueno Park and the cherry blossoms"),
    ("connected", "Getting online: eSIM"),
    ("luggage", "Lockers and luggage"),
    ("finder", "Find it fast: lockers, tickets, lifts"),
    ("facilities", "Facilities in the station"),
    ("help", "Help for older travellers and anyone who needs assistance"),
    ("leaving", "Leaving Ueno: a checklist"),
    ("faq", "FAQ"),
    ("about-this-guide", "About this guide and change log"),
]
# ---- "What do you need first?" tiles + a quick-jump bar that appears once you scroll (as w42)
TOC_SHORT = {
    "one-page": "On one page", "narita": "Narita", "exits": "Which exit", "platforms": "Platforms", "metro": "Metro",
    "park": "Ueno Park", "connected": "Get online", "luggage": "Luggage", "finder": "Find it fast",
    "facilities": "Facilities", "help": "Help", "leaving": "Leaving", "faq": "FAQ", "about-this-guide": "About",
}
TOC_TILES = [
    ("narita", "&#9992;&#65039;", "To Narita Airport", "Skyliner, not JR"),
    ("exits", "&#128682;", "Which exit?", "Park Gate, Panda Bridge"),
    ("park", "&#127800;", "Ueno Park", "Cherry blossoms, 5:00 to 23:00"),
    ("platforms", "&#128646;", "Platforms", "JR tracks 1 to 22 by floor"),
    ("metro", "&#128647;", "Tokyo Metro", "Ginza G16, Hibiya H18"),
    ("luggage", "&#129523;", "Lockers", "On 1F, 2F and 3F"),
    ("help", "&#129309;", "Help and lifts", "Lifts A to I, lost and found"),
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
.ps-sources{font-size:0.9rem;line-height:1.6;}
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


DG_H = 636
_DG_SVG = (
    '<svg id="uenDiagram" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 %d" role="img" aria-labelledby="uenT uenD" font-family="Arial, Helvetica, sans-serif">' % DG_H
    + '<title id="uenT">Ueno Station by floor</title>'
    '<desc id="uenD">JR Ueno Station by floor. 3F: the Park Gate, Panda Bridge Exit and Iriya Gate, the way to Ueno Park, and ecute Ueno shops inside the gates. '
    '2F: JR tracks 1 to 12, including the Yamanote Line on tracks 2 and 3, and Lost and Found near the Panda Bridge stairs. '
    '1F: the Central Gate, Main Exit and taxi stop, the Asakusa, Yamashita and Iriya exits, and JR tracks 13 to 17. M2: the Shinobazu Gate. '
    'B1 to B4: Shinkansen tracks 19 to 22. The Keisei Skyliner to Narita Airport leaves from Keisei Ueno, a separate station.</desc>'
    '<rect width="480" height="%d" fill="#fff"/>' % DG_H
    + '<text x="240" y="38" font-size="26" font-weight="700" text-anchor="middle" fill="#0f0f23">Ueno Station by floor</text>'
    '<text x="240" y="64" font-size="17" text-anchor="middle" fill="#555">Ueno Park from 3F. Skyliner from Keisei Ueno</text>'
    '<rect x="24" y="84" width="432" height="150" rx="18" fill="#FBEFF4" stroke="#b8306a" stroke-width="2"/>'
    '<text x="48" y="120" font-size="28" font-weight="700" fill="#0f0f23">3F</text>'
    '<text x="96" y="120" font-size="17" fill="#0f0f23">Park Gate, Panda Bridge, Iriya Gate</text>'
    + _dg_pill(136, "Ueno Park: Park Gate or Panda Bridge", "#fff", "#b8306a", "#8a1f4e", "700")
    + _dg_pill(180, "ecute Ueno shops, inside the gates", "#fff", "#b8306a", "#8a1f4e")
    + '<rect x="24" y="244" width="432" height="110" rx="18" fill="#EEF0FB" stroke="#34346e" stroke-width="2"/>'
    '<text x="48" y="280" font-size="28" font-weight="700" fill="#0f0f23">2F</text>'
    '<text x="96" y="280" font-size="17" fill="#0f0f23">JR tracks 1 to 12, Yamanote 2 and 3</text>'
    + _dg_pill(300, "Lost &amp; Found, by the Panda Bridge stairs", "#fff", "#34346e", "#1a1a3e")
    + '<rect x="24" y="364" width="432" height="150" rx="18" fill="#EEF0FB" stroke="#34346e" stroke-width="2"/>'
    '<text x="48" y="400" font-size="28" font-weight="700" fill="#0f0f23">1F</text>'
    '<text x="96" y="400" font-size="17" fill="#0f0f23">JR tracks 13 to 17. M2: Shinobazu Gate</text>'
    + _dg_pill(416, "Central Gate, Main Exit, taxi stop", "#fff", "#34346e", "#1a1a3e", "700")
    + _dg_pill(460, "Asakusa, Yamashita and Iriya exits", "#fff", "#34346e", "#1a1a3e")
    + '<rect x="24" y="524" width="432" height="76" rx="18" fill="#E8F1FE" stroke="#2563EB" stroke-width="2"/>'
    '<text x="48" y="560" font-size="28" font-weight="700" fill="#0f0f23">B1&#8211;B4</text>'
    '<text x="48" y="586" font-size="17" fill="#0f0f23">Shinkansen tracks 19 to 22</text>'
    '<text x="240" y="626" font-size="14" text-anchor="middle" fill="#777">Simplified, not to scale. packsmartapp.com</text></svg>'
)

DIAGRAM = '<figure class="ps-fig" id="at-a-glance">\n' + _DG_SVG + """
<button type="button" class="ps-btn2" id="uenDl">Download the diagram (PNG)</button>
</figure>
<script>
(function(){
  var b=document.getElementById('uenDl'); if(!b) return;
  b.addEventListener('click',function(){
    try{
      var svg=document.getElementById('uenDiagram');
      var xml=new XMLSerializer().serializeToString(svg);
      var img=new Image();
      img.onload=function(){
        var c=document.createElement('canvas'); c.width=960; c.height=""" + str(2 * DG_H) + """;
        var x=c.getContext('2d'); x.fillStyle='#fff'; x.fillRect(0,0,c.width,c.height); x.drawImage(img,0,0,c.width,c.height);
        c.toBlob(function(bl){
          var a=document.createElement('a'); a.href=URL.createObjectURL(bl); a.download='ueno-station-at-a-glance.png';
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
    "terms": [["T1", "Park level (3F)"], ["T2", "Ground level (1F)"]],
    "items": [
        ["lockers", "Luggage lockers", {
            "T1": "JR East's map shows coin lockers on 3F by the Panda Bridge Exit and near the Iriya Gate, and on 2F along the concourse to the Iriya Exit. We did not find their sizes or prices.",
            "T2": "JR East's map shows coin lockers on 1F near the Main Exit (taxi side), and inside the gates by the Transfer to Shinkansen gate. We did not find their sizes or prices."}],
        ["info", "Information", {
            "T1": "The Question & Answer counter is on 1F, beside the Central Gate (JR East map). On 3F, ask station staff.",
            "T2": "Question & Answer counter beside the Central Gate (1F). The JR EAST Travel Service Center is by the Central Gate ticket hall (1F)."}],
        ["tickets", "Tickets and passes", {
            "T1": "JR East's map shows ticket machines and a fare adjustment machine beside the Park Gate (3F). The ticket office and the passport-reader machines are on 1F, by the Central Gate.",
            "T2": "Ticket Office and JR EAST Travel Service Center by the Central Gate ticket hall (1F). The Passport Reader & Reserved Seat Ticket Vending Machine is by the Central Gate tickets."}],
        ["help", "Lifts and help", {
            "T1": "JR East's map shows lifts A to F from 3F to platforms 1 to 12. Ask station staff for the step-free route. In an emergency, call 119.",
            "T2": "Lifts G and H go to the Shinkansen platforms, and lift I to the 2F concourse outside the gates (JR East map). Ask station staff. In an emergency, call 119."}],
        ["lost", "Lost and found", {
            "T1": "JR Lost & Found is on 2F, near the stairs to the Panda Bridge Exit (JR East map). Lost it on the Tokyo Metro? Same day: ask the Metro station office. From the next day: Tokyo Metro's Lost and Found at Iidabashi Station or its Customer Relations Center.",
            "T2": "JR Lost & Found is on 2F, near the stairs to the Panda Bridge Exit (JR East map). Lost it on the Tokyo Metro? Same day: ask the Metro station office. From the next day: Tokyo Metro's Lost and Found at Iidabashi Station or its Customer Relations Center."}],
        ["money", "Money and ATMs", {
            "T1": "We did not find ATMs on the official station pages we read. Please ask station staff.",
            "T2": "We did not find ATMs on the official station pages we read. Please ask station staff."}],
        ["toilet", "Toilets", {
            "T1": "We did not find toilet locations in words on the official pages. Follow the signs, or ask station staff.",
            "T2": "We did not find toilet locations in words on the official pages. Follow the signs, or ask station staff."}],
        ["food", "Shops and food", {
            "T1": "ecute Ueno, shops inside the ticket gates on 3F (JR East map).",
            "T2": "atre Ueno, outside the ticket gates on 1F and 2F, and NewDays kiosks (JR East map)."}],
        ["unwell", "Feeling unwell", {
            "T1": "Tell station staff. In an emergency, call 119.",
            "T2": "Tell station staff, or go to the Question & Answer counter beside the Central Gate (1F). In an emergency, call 119."}],
    ],
}
_ORDER = ["lockers", "info", "tickets", "help", "lost", "money", "toilet", "food", "unwell"]
assert sorted(_ORDER) == sorted(i[0] for i in FINDER_DATA["items"])
FINDER_DATA["items"].sort(key=lambda i: _ORDER.index(i[0]))
FINDER = """<section class="ps-finder" id="finder">
<h2>Find it fast</h2>
<p>Choose your level of the station, then what you need. Large buttons, no typing.</p>
<p class="ps-step-h">1. Which level are you on?</p>
<div class="ps-chips" id="fdTerm"></div>
<p class="ps-step-h">2. What do you need?</p>
<div class="ps-chips" id="fdWhat"></div>
<div class="ps-result" id="fdResult" aria-live="polite">Choose a level and what you need, and the answer shows here.</div>
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
    if(!term||!what){ rEl.textContent=!term?'Now choose your level.':'Now choose what you need.'; return; }
    var tn=D.terms.filter(function(t){return t[0]===term;})[0][1];
    var it=D.items.filter(function(i){return i[0]===what;})[0];
    var txt=it[2][term];
    rEl.innerHTML='';
    var s=document.createElement('strong'); s.textContent=it[1]+': '+tn; rEl.appendChild(s);
    rEl.appendChild(document.createElement('br'));
    rEl.appendChild(document.createTextNode(txt?txt:'We did not find this on the official station pages. Please ask station staff.'));
    var sm=document.createElement('small'); sm.textContent='From JR East\\'s Ueno Station map and Tokyo Metro, checked 23 November 2026. Floors and counters can change. If you cannot find it, ask station staff.'; rEl.appendChild(sm);
  }
})();
</script>"""
FINDER = FINDER.replace("__FINDER_JSON__", json.dumps(FINDER_DATA, ensure_ascii=False))

# luggage storage callout: the same tracked link as the Japan guide's "bags-japan-tokyo" callout (no partner name, D47)
BAGS_LINK = "https://radicalstorage.tpx.li/d0Eds67a"
BAGS = ('<p data-ps-placement="bags-ueno-station" style="background:#f0faf7;border-left:3px solid #00C9A7;padding:12px 16px;border-radius:0 8px 8px 0;font-size:0.92rem;margin:20px 0;">'
        '&#129523; No locker free, or a bag too big for one? <a href="' + BAGS_LINK + '" target="_blank" rel="nofollow noopener sponsored" '
        'style="color:#00C9A7;text-decoration:underline;">Store your bags in Tokyo</a> (partner link) and explore hands-free.</p>')

LUGGAGE = """<h2 id="luggage">Lockers and luggage</h2>
<p>Sort your bags out before you head into the park or the museums. JR East's station map shows coin lockers on three floors.</p>
<ul>
<li><strong>1F.</strong> Near the Main Exit, on the taxi side, and inside the ticket gates by the Transfer to Shinkansen gate.</li>
<li><strong>2F.</strong> Along the concourse to the Iriya Exit.</li>
<li><strong>3F.</strong> By the Panda Bridge Exit and near the Iriya Gate, on the park side.</li>
<li><strong>Sizes and prices.</strong> We did not find them on the official pages, so we give none.</li>
<li><strong>Keep with you:</strong> medicines, valuables, chargers and your passport.</li>
<li><strong>Have these ready:</strong> your hotel name, address and phone number, written down.</li>
</ul>
""" + sources(["jrmap"], "Station layouts change, so follow the signs.") + "\n" + BAGS

HELP = """<h2 id="help">Help for older travellers and anyone who needs assistance</h2>
<p>You do not have to cope alone. Asking early is easier than struggling.</p>
<ul>
<li><strong>Question &amp; Answer counter.</strong> JR East's map puts it on 1F, beside the Central Gate.</li>
<li><strong>JR EAST Travel Service Center and ticket office.</strong> On 1F, by the Central Gate ticket hall.</li>
<li><strong>Lifts.</strong> JR East's map letters them A to I: A to F go from 3F to platforms 1 to 12, G and H to the Shinkansen platforms, and I to the 2F concourse outside the ticket gates.</li>
<li><strong>Station staff.</strong> Tell staff at a ticket gate if you need help or are not sure which way to go.</li>
<li><strong>Tokyo Metro.</strong> The Metro station office number is 03-3832-6629 (Tokyo Metro).</li>
<li><strong>Allow extra time.</strong> We did not find official walking times between gates and platforms, so add a buffer, especially with luggage.</li>
<li><strong>Visitor hotline.</strong> The Japan Visitor Hotline, 050-3816-2787, is open 24 hours and helps in English, Chinese and Korean. In an emergency, call 119.</li>
</ul>
""" + sources(["jrmap", "metro"])

ABOUT = """<div class="ps-about" id="about-this-guide">
<h2>About this guide</h2>
<p>Written by PackSmart. Station details were checked on 23 November 2026 against JR East's Ueno Station map, Tokyo Metro's Ueno Station page, Keisei's Skyliner pages and the Ueno Park pages of the Tokyo Metropolitan Government. Where an official page did not tell us something, for example Tokyo Metro exit numbers, locker prices or the first and last Skyliner, we say so instead of guessing. Spotted something out of date? <a href="/contact">Tell us</a> and we will fix it.</p>
<ul>
<li><strong>23 Nov 2026:</strong> first version, with the one-page card, the Skyliner and the Narita Line warning, which gate or exit for where, the floor diagram, JR platforms by floor, Tokyo Metro, Ueno Park and the cherry blossoms, lockers, the find-it tool, help and a leaving checklist.</li>
</ul>
</div>"""
def _card(title, text, slug, tag):
    return ('        <div class="related-card">\n            <div class="related-card-body">\n                <h4>%s</h4>\n                <p>%s</p>\n'
            '                <a href="https://www.packsmartapp.com%s">Read More <span class="related-arrow">&rarr;</span></a>\n                <div class="related-tag">%s</div>\n            </div>\n        </div>\n') % (title, text, slug, tag)

RELATED = ('<div class="related-posts">\n    <h3>Related Guides</h3>\n    <div class="related-grid">\n'
    + _card("Narita Airport Guide 2026", "Flying out of Narita? Terminals, departure steps, SIM and the trains and buses from Tokyo.", "/blog/narita-airport-guide", "Airport Guide")
    + _card("Tokyo Station Guide 2026", "Which side to use, bullet train platforms, the Narita Express and luggage.", "/blog/tokyo-station-guide", "Station Guide")
    + _card("Shinjuku Station Guide 2026", "West or East side, which exit for where, platforms, airport buses and luggage.", "/blog/shinjuku-station-guide", "Station Guide")
    + '    </div>\n</div>')
# photos: public/images/ueno-station-hero.jpg and ueno-park-sakura.jpg (PAKUTASO, checked by eye, see
# docs/research/ueno-sources.md); optimised copies made here (as w58: sips on a Mac, Pillow elsewhere, an existing copy is kept)
def prepare_img(base, dst_name, max_px, write=False):
    """write=False only works out the URL (nothing is written before every anchor check has passed)."""
    imgdir = os.path.join(ROOT, "public", "images")
    src = None
    for ext in ("jpg", "jpeg", "png", "webp"):
        cand = os.path.join(imgdir, base + "." + ext)
        if os.path.isfile(cand):
            src = cand
            break
    if not src:
        return None, None
    dst = os.path.join(imgdir, dst_name)
    note = None
    if (not os.path.isfile(dst)) or os.path.getmtime(dst) < os.path.getmtime(src):
        if not write:
            try:
                import PIL  # noqa: F401  (Pillow can make the copy later)
            except Exception:
                import shutil
                if not shutil.which("sips") and not os.path.isfile(dst):
                    return ("/images/" + os.path.basename(src) if src.lower().endswith(".jpg") else None), None
            return "/images/" + dst_name, None
        import subprocess
        try:
            subprocess.run(["sips", "-Z", str(max_px), "-s", "format", "jpeg", "-s", "formatOptions", "72", src, "--out", dst],
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            note = dst_name + " (optimised from your photo)"
        except Exception:
            # no sips (Linux): resize with Pillow, else keep an existing optimised copy
            try:
                from PIL import Image
                _im = Image.open(src).convert("RGB")
                _im.thumbnail((max_px, max_px))
                if os.path.isfile(dst) and os.path.getmtime(dst) >= os.path.getmtime(src) - 1:
                    pass
                else:
                    _im.save(dst, "JPEG", quality=72, optimize=True, progressive=True)
                    note = dst_name + " (optimised from your photo)"
            except Exception:
                if not os.path.isfile(dst):
                    if src.lower().endswith(".jpg"):
                        return "/images/" + os.path.basename(src), "using the original photo (could not optimise it here)"
                    return None, None
    return "/images/" + dst_name, note


IMAGES = {"hero": ("ueno-station-hero", "ueno-station-hero-1600.jpg", 1600),
          "sakura": ("ueno-park-sakura", "ueno-park-sakura-1200.jpg", 1200)}
HERO_URL, HERO_NOTE = prepare_img(*IMAGES["hero"])
SAKURA_URL, _ = prepare_img(*IMAGES["sakura"])
if not SAKURA_URL:
    die("cherry blossom photo not found: public/images/ueno-park-sakura.jpg")


CARD = """<div class="ps-card" id="one-page">
<h2>Ueno Station on one page</h2>
<ul>
<li><strong>To Narita Airport:</strong> the Keisei Skyliner from <strong>Keisei Ueno</strong>, a separate station. Keisei gives 41 minutes from Narita Airport Terminal 2&middot;3 to Keisei Ueno.</li>
<li><strong>Not JR's Narita Line:</strong> tracks 10 to 12 are &ldquo;for Matsudo, Toride, Mito &amp; Narita&rdquo;. That is Narita city, not the airport.</li>
<li><strong>Ueno Park:</strong> the Park Gate or the Panda Bridge Exit, both on 3F. About a 2-minute walk (park office). Open 5:00 to 23:00.</li>
<li><strong>Main side:</strong> Central Gate and Main Exit on 1F, with the taxi stop, the ticket office and the JR EAST Travel Service Center.</li>
<li><strong>JR platforms:</strong> tracks 1 to 12 on 2F (Yamanote Line 2 and 3), 13 to 17 on 1F, Shinkansen 19 to 22 underground.</li>
<li><strong>Tokyo Metro:</strong> Ginza Line G16 and Hibiya Line H18. Follow the &ldquo;for Tokyo Metro&rdquo; signs near the Central Gate.</li>
<li><strong>Lockers:</strong> on 1F, 2F and 3F (JR East map). Lost &amp; Found: 2F, by the Panda Bridge Exit stairs.</li>
<li><strong>Need help?</strong> Question &amp; Answer counter beside the Central Gate (1F). In an emergency, call 119.</li>
</ul>
<div class="ps-qr ps-qr-screen">__QR_SCREEN__<p><strong>Want it on your phone?</strong> Point your phone camera at this code. It opens the free Ueno Station Pocket Guide, which works without internet once opened.<span class="u">packsmartapp.com/ueno-pocket</span></p></div>
<div class="ps-qr ps-qr-print">__QR_PRINT__<p><strong>Free Ueno Station Pocket Guide.</strong> Point your phone camera at this code. Open it once with signal and it works without internet.<span class="u">packsmartapp.com/ueno-pocket</span></p></div>
<button type="button" class="ps-print-btn" onclick="window.print()">Print this card</button>
</div>"""
# QR codes are made once for each guide address (?src=qr on screen, ?src=card on paper), with segno (error="m"), as in w42.
QR_SCREEN = '<svg shape-rendering="crispEdges" viewBox="0 0 41 41" class="segno"><title>QR code: open the Ueno Station Pocket Guide</title><path fill="#fff" d="M0 0h41v41h-41z"/><path class="qrline" stroke="#000" d="M4 4.5h7m2 0h3m6 0h1m3 0h1m3 0h7m-33 1h1m5 0h1m1 0h1m2 0h1m1 0h2m1 0h2m4 0h1m1 0h1m1 0h1m5 0h1m-33 1h1m1 0h3m1 0h1m1 0h2m1 0h1m1 0h1m2 0h3m1 0h3m1 0h1m1 0h1m1 0h3m1 0h1m-33 1h1m1 0h3m1 0h1m1 0h4m3 0h1m5 0h1m4 0h1m1 0h3m1 0h1m-33 1h1m1 0h3m1 0h1m2 0h1m1 0h1m3 0h1m2 0h1m2 0h4m1 0h1m1 0h3m1 0h1m-33 1h1m5 0h1m2 0h1m4 0h1m1 0h1m1 0h1m1 0h1m5 0h1m5 0h1m-33 1h7m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h7m-25 1h4m2 0h1m7 0h3m-25 1h1m5 0h1m1 0h2m2 0h4m1 0h1m2 0h1m1 0h1m2 0h2m2 0h3m-32 1h1m3 0h2m1 0h3m1 0h1m2 0h3m2 0h1m2 0h2m4 0h3m-27 1h3m2 0h1m1 0h1m3 0h2m1 0h1m2 0h1m2 0h2m2 0h1m1 0h1m-28 1h1m3 0h3m1 0h1m2 0h1m1 0h1m2 0h1m2 0h2m1 0h1m1 0h6m-33 1h1m2 0h1m2 0h1m3 0h2m1 0h2m1 0h5m3 0h1m1 0h2m-24 1h2m3 0h1m1 0h4m1 0h1m3 0h1m1 0h2m1 0h3m1 0h1m1 0h2m-30 1h1m1 0h5m3 0h1m4 0h2m4 0h3m1 0h4m-31 1h1m3 0h1m3 0h2m1 0h1m1 0h2m2 0h2m3 0h3m3 0h2m1 0h1m-32 1h2m2 0h2m4 0h1m1 0h1m3 0h1m1 0h2m1 0h1m1 0h2m1 0h3m2 0h1m-32 1h1m1 0h2m3 0h1m2 0h1m2 0h4m1 0h2m2 0h4m2 0h2m1 0h1m-32 1h2m3 0h2m1 0h2m1 0h1m2 0h1m3 0h1m2 0h2m2 0h2m1 0h2m1 0h1m-33 1h1m1 0h4m1 0h1m1 0h2m1 0h1m1 0h5m4 0h1m4 0h3m1 0h1m-33 1h2m1 0h1m2 0h1m2 0h6m1 0h1m3 0h2m5 0h3m1 0h2m-33 1h1m1 0h2m1 0h1m4 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h4m1 0h1m1 0h2m1 0h1m-31 1h1m3 0h6m3 0h4m1 0h1m1 0h1m4 0h1m2 0h1m1 0h2m-32 1h1m1 0h2m3 0h2m1 0h2m2 0h1m3 0h1m3 0h5m2 0h4m-33 1h2m2 0h3m2 0h3m2 0h3m1 0h3m2 0h7m-22 1h3m1 0h1m1 0h3m1 0h3m1 0h3m3 0h1m1 0h1m1 0h1m-33 1h7m4 0h1m2 0h3m1 0h1m1 0h2m1 0h2m1 0h1m1 0h1m1 0h2m-32 1h1m5 0h1m2 0h1m1 0h1m1 0h4m5 0h3m3 0h5m-33 1h1m1 0h3m1 0h1m2 0h2m1 0h4m2 0h2m1 0h1m2 0h6m1 0h1m-32 1h1m1 0h3m1 0h1m2 0h1m1 0h2m3 0h2m2 0h1m2 0h1m1 0h1m1 0h3m2 0h1m-33 1h1m1 0h3m1 0h1m2 0h2m2 0h2m1 0h1m3 0h1m1 0h1m1 0h1m2 0h2m2 0h2m-33 1h1m5 0h1m2 0h1m3 0h1m1 0h2m1 0h3m1 0h2m1 0h6m-31 1h7m1 0h1m3 0h2m3 0h1m1 0h1m2 0h6m3 0h1"/></svg>'
QR_PRINT = '<svg shape-rendering="crispEdges" viewBox="0 0 41 41" class="segno"><title>QR code: open the Ueno Station Pocket Guide</title><path fill="#fff" d="M0 0h41v41h-41z"/><path class="qrline" stroke="#000" d="M4 4.5h7m3 0h1m1 0h1m5 0h1m3 0h1m3 0h7m-33 1h1m5 0h1m1 0h2m3 0h2m1 0h2m4 0h1m1 0h1m1 0h1m5 0h1m-33 1h1m1 0h3m1 0h1m1 0h2m2 0h2m2 0h3m1 0h3m1 0h1m1 0h1m1 0h3m1 0h1m-33 1h1m1 0h3m1 0h1m1 0h1m1 0h1m1 0h1m2 0h1m5 0h1m4 0h1m1 0h3m1 0h1m-33 1h1m1 0h3m1 0h1m2 0h3m3 0h1m2 0h1m2 0h1m1 0h2m1 0h1m1 0h3m1 0h1m-33 1h1m5 0h1m2 0h3m2 0h1m1 0h1m1 0h1m1 0h1m5 0h1m5 0h1m-33 1h7m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h7m-25 1h2m1 0h1m2 0h1m7 0h3m-25 1h1m5 0h1m1 0h2m1 0h5m1 0h1m2 0h1m1 0h1m2 0h2m2 0h3m-29 1h3m2 0h3m1 0h1m1 0h3m2 0h1m2 0h2m4 0h3m-31 1h1m1 0h1m1 0h5m3 0h1m2 0h2m1 0h1m5 0h2m2 0h1m1 0h1m-31 1h1m1 0h1m2 0h1m1 0h1m1 0h2m3 0h1m1 0h1m2 0h1m2 0h2m1 0h1m1 0h6m-31 1h3m1 0h1m2 0h6m1 0h5m3 0h1m1 0h2m-28 1h1m3 0h2m2 0h2m1 0h1m1 0h2m1 0h1m3 0h1m2 0h1m1 0h3m1 0h1m1 0h2m-32 1h1m1 0h4m3 0h2m2 0h1m3 0h2m4 0h3m1 0h4m-32 1h3m2 0h1m2 0h6m1 0h1m2 0h2m3 0h3m3 0h2m1 0h1m-32 1h1m1 0h7m2 0h1m4 0h1m1 0h2m1 0h1m1 0h2m1 0h3m2 0h1m-33 1h2m5 0h2m1 0h1m1 0h1m1 0h4m1 0h2m2 0h4m2 0h2m1 0h1m-31 1h2m1 0h3m2 0h1m1 0h2m1 0h1m3 0h1m1 0h3m2 0h2m1 0h2m1 0h1m-32 1h1m1 0h2m2 0h1m4 0h1m1 0h5m3 0h2m4 0h3m1 0h1m-33 1h3m3 0h2m1 0h1m1 0h4m1 0h1m5 0h1m4 0h3m1 0h2m-33 1h1m4 0h1m1 0h2m2 0h2m1 0h1m1 0h1m1 0h1m1 0h2m1 0h1m1 0h1m1 0h2m1 0h1m-31 1h1m1 0h1m1 0h1m1 0h1m2 0h4m1 0h3m1 0h1m6 0h1m2 0h1m1 0h2m-32 1h1m1 0h4m1 0h1m2 0h1m7 0h1m3 0h5m2 0h3m-32 1h4m2 0h3m1 0h3m1 0h3m1 0h3m2 0h7m1 0h2m-25 1h2m5 0h2m1 0h3m1 0h3m3 0h1m1 0h1m1 0h1m-33 1h7m3 0h2m1 0h1m1 0h2m1 0h1m1 0h1m2 0h2m1 0h1m1 0h1m1 0h2m-32 1h1m5 0h1m2 0h1m1 0h3m1 0h2m5 0h3m3 0h5m-33 1h1m1 0h3m1 0h1m2 0h3m1 0h3m2 0h2m2 0h1m1 0h6m1 0h1m-32 1h1m1 0h3m1 0h1m2 0h2m1 0h3m1 0h2m5 0h1m1 0h1m1 0h3m1 0h2m-33 1h1m1 0h3m1 0h1m2 0h1m2 0h1m1 0h1m1 0h1m2 0h2m1 0h1m1 0h1m2 0h2m2 0h2m-33 1h1m5 0h1m4 0h1m1 0h4m1 0h1m1 0h1m1 0h2m1 0h6m-31 1h7m1 0h1m1 0h2m1 0h1m3 0h1m4 0h6m3 0h1"/></svg>'
CARD = CARD.replace("__QR_SCREEN__", QR_SCREEN).replace("__QR_PRINT__", QR_PRINT)

WARN_CSS = """<style>
.ps-warn{background:#FDECEF;border:2px solid #E94560;border-radius:14px;padding:16px 18px;margin:20px 0;line-height:1.55}
.ps-warn strong.h{display:block;font-size:1.12rem;color:#a3243b;margin:0 0 6px}
.ps-warn p{margin:0 0 8px}
.ps-warn p:last-child{margin:0}
</style>"""

NARITA = """<h2 id="narita">To Narita Airport: the Skyliner, not JR's Narita Line</h2>
<div class="ps-warn" role="note"><strong class="h">&#9888;&#65039; JR's &ldquo;Narita Line&rdquo; does not mean Narita Airport</strong>
<p>JR East's station map lists the Narita Line on tracks 10 to 12 (2F) &ldquo;for Matsudo, Toride, Mito &amp; Narita&rdquo;, and also on tracks 6 and 9. That Narita is the city. Do not board it for your flight.</p>
<p><strong>For Narita Airport, take the Keisei Skyliner from Keisei Ueno</strong>, Keisei's own station, separate from JR Ueno.</p></div>
<ul>
<li><strong>How long.</strong> Keisei gives 41 minutes on the Skyliner from Narita Airport Terminal 2&middot;3 to Keisei Ueno. Its Skyliner page also says &ldquo;in as little as 41 minutes&rdquo; from Narita Airport to Keisei Ueno; the &ldquo;as little as 36 minutes&rdquo; figure on the same page is to Nippori.</li>
<li><strong>Where to board.</strong> At Keisei Ueno, not in the JR station. We did not find an official walking route between JR Ueno and Keisei Ueno, so follow the signs or ask station staff. Keisei links its station maps for Keisei Ueno and Nippori from its station page.</li>
<li><strong>Tickets.</strong> Keisei sells a Skyliner discount ticket between Narita Airport Station and Ueno Station, and a Skyliner and Tokyo Subway Ticket set. Fares are on Keisei's own pages, and they change.</li>
<li><strong>Holding the &ldquo;Skyliner &amp; Tokyo Subway Ticket&rdquo; or the &ldquo;Greater Tokyo Pass&rdquo;?</strong> Keisei says you cannot transfer at Nippori with these, so use Ueno.</li>
<li><strong>Changing to JR at Nippori?</strong> Keisei says the JR transfer at Nippori needs a JR ticket.</li>
<li><strong>First and last Skyliner.</strong> We did not find them on the pages we read. Check Keisei's timetable before a very early or late trip.</li>
</ul>
<p>More detail: our <a href="/blog/narita-airport-guide">Narita Airport guide</a>.</p>
""" + sources(["jrmap", "skyueno", "sky", "nippori", "kstation"], "Times and fares change, so check Keisei.")

EXITS = """<h2 id="exits">Which gate or exit for where?</h2>
<p>JR Ueno has gates and exits on several floors. These are the ones named on JR East's station map (as of November 2026). Tokyo Metro has its own exits, but we did not find Tokyo Metro's exit list, so this guide routes you by the JR gates.</p>
<div class="ps-scroll">
<table class="checklist-table">
<thead><tr><th>Going to</th><th>Use</th><th>Good to know</th></tr></thead>
<tbody>
<tr><td><strong>Ueno Park</strong></td><td>Park Gate or Panda Bridge Exit, 3F</td><td>JR East's map marks the end of Panda Bridge &ldquo;for Ueno Park&rdquo;. The park office gives a 2-minute walk from JR Ueno.</td></tr>
<tr><td><strong>Ticket office, Travel Service Center, taxi</strong></td><td>Central Gate and Main Exit, 1F</td><td>The ticket hall is by the Central Gate. The map marks the taxi stop by the Main Exit.</td></tr>
<tr><td><strong>Tokyo Metro (Ginza and Hibiya lines)</strong></td><td>&ldquo;for Tokyo Metro&rdquo; signs, 1F</td><td>Two signs near the Central Gate area. On 2F the map also points to the Ginza and Hibiya lines.</td></tr>
<tr><td><strong>Shinkansen</strong></td><td>Transfer to Shinkansen gate, 1F</td><td>Inside the station. The Shinkansen platforms (tracks 19 to 22) are underground. Lifts G and H go down to them.</td></tr>
<tr><td><strong>Iriya side</strong></td><td>Iriya Gate (3F) or Iriya Exit (1F)</td><td>On 2F, the map points along the concourse &ldquo;for Iriya Exit&rdquo;.</td></tr>
<tr><td><strong>Asakusa Exit, Yamashita Exit</strong></td><td>1F</td><td>Named on JR East's map. We did not find official directions from each exit, so check a map before you walk.</td></tr>
<tr><td><strong>Shinobazu Gate</strong></td><td>M2 (a mezzanine floor)</td><td>Named on JR East's map. We did not find where it leads in words, so ask station staff.</td></tr>
<tr><td><strong>Keisei Ueno (Skyliner)</strong></td><td>A separate station</td><td>We did not find an official walking route from JR Ueno. Follow the signs, or ask station staff.</td></tr>
</tbody>
</table>
</div>
""" + sources(["jrmap", "parkacc"], "Station layouts change, so follow the signs.")

PLATFORMS = """<h2 id="platforms">JR platforms by floor</h2>
<p>JR East's station map (as of November 2026) lists these tracks. Your ticket and the departure boards show your platform, and platforms can change, so check before you walk down.</p>
<h3>2F: tracks 1 to 12</h3>
<div class="ps-scroll">
<table class="checklist-table">
<thead><tr><th>Track</th><th>Line</th><th>Toward</th></tr></thead>
<tbody>
<tr><td><strong>1</strong></td><td>Keihin-Tohoku Line</td><td>Akabane, Urawa and Omiya</td></tr>
<tr><td><strong>2</strong></td><td>Yamanote Line</td><td>Tabata, Ikebukuro and Shinjuku</td></tr>
<tr><td><strong>3</strong></td><td>Yamanote Line</td><td>Akihabara, Tokyo, Hamamatsucho and Shinagawa</td></tr>
<tr><td><strong>4</strong></td><td>Keihin-Tohoku Line</td><td>Kamata, Kawasaki, Yokohama and Kannai</td></tr>
<tr><td><strong>5</strong></td><td>Utsunomiya Line, Takasaki Line</td><td>Akabane, Omiya, Utsunomiya and Takasaki</td></tr>
<tr><td><strong>6</strong></td><td>Joban Line, Joban Line (Rapid), Narita Line, Utsunomiya Line, Takasaki Line</td><td>Check the board</td></tr>
<tr><td><strong>7</strong></td><td>Ueno-Tokyo Line</td><td>Tokyo, Shinagawa, Yokohama, Odawara and Atami</td></tr>
<tr><td><strong>8</strong></td><td>Joban Line; Ueno-Tokyo Line</td><td>Joban Line: Kashiwa, Tsuchiura, Mito and Iwaki. Ueno-Tokyo Line: Tokyo and Shinagawa</td></tr>
<tr><td><strong>9</strong></td><td>Joban Line, Joban Line (Rapid), Narita Line, Ueno-Tokyo Line</td><td>Check the board</td></tr>
<tr><td><strong>10 to 12</strong></td><td>Joban Line, Joban Line (Rapid), Narita Line</td><td>Matsudo, Toride, Mito and Narita (the city, <strong>not the airport</strong>)</td></tr>
</tbody>
</table>
</div>
<h3>1F: tracks 13 to 17</h3>
<div class="ps-scroll">
<table class="checklist-table">
<thead><tr><th>Track</th><th>Line</th><th>Toward</th></tr></thead>
<tbody>
<tr><td><strong>13 to 15</strong></td><td>Utsunomiya Line, Takasaki Line</td><td>Akabane, Omiya, Utsunomiya and Takasaki</td></tr>
<tr><td><strong>16</strong></td><td>Joban Line; Utsunomiya Line, Takasaki Line</td><td>Joban Line: Kashiwa, Toride, Tsuchiura and Mito</td></tr>
<tr><td><strong>17</strong></td><td>Joban Line</td><td>Kashiwa, Toride, Tsuchiura and Mito</td></tr>
</tbody>
</table>
</div>
<h3>Underground (B4 to B1): Shinkansen tracks 19 to 22</h3>
<div class="ps-scroll">
<table class="checklist-table">
<thead><tr><th>Track</th><th>Line</th><th>Toward</th></tr></thead>
<tbody>
<tr><td><strong>19 and 20</strong></td><td>Tohoku, Yamagata, Akita, Hokkaido, Joetsu and Hokuriku Shinkansen</td><td>Check your ticket and the board</td></tr>
<tr><td><strong>21 and 22</strong></td><td>Shinkansen</td><td>Tokyo</td></tr>
</tbody>
</table>
</div>
<ul>
<li><strong>Getting down to the Shinkansen.</strong> Through the Transfer to Shinkansen gate inside the station on 1F. Lifts G and H go to the Shinkansen platforms. The Shinkansen concourse has a waiting room.</li>
<li><strong>Lifts to tracks 1 to 12.</strong> Lifts A to F go from 3F to these platforms.</li>
<li><strong>Reserved seats.</strong> The map shows a Passport Reader &amp; Reserved Seat Ticket Vending Machine by the Central Gate tickets (1F).</li>
</ul>
""" + sources(["jrmap"])

METRO = """<h2 id="metro">Tokyo Metro: Ginza and Hibiya lines</h2>
<ul>
<li><strong>Lines.</strong> Ginza Line (G16) and Hibiya Line (H18). Tokyo Metro lists transfers to JR East and to Keisei.</li>
<li><strong>From the JR station.</strong> JR East's map shows &ldquo;for Tokyo Metro&rdquo; signs near the Central Gate (1F), and on 2F a route to the Ginza and Hibiya lines.</li>
<li><strong>Exits.</strong> We did not find Tokyo Metro's exit list for Ueno. For Ueno Park, the park office gives a 4-minute walk from the Ginza and Hibiya line station. If you are unsure, go up into the JR station and use the Park Gate or Panda Bridge on 3F.</li>
<li><strong>Tickets.</strong> Tokyo Metro says its multi-functional ticket machines are at all ticket offices, from the first train to the last. Ueno also has a Tokyo Metro Pass Office (for commuter passes; the map we saw does not say whether it sells visitor tickets).</li>
<li><strong>Lost something on the Metro?</strong> On the same day, ask the station office where you lost it. From the next day, contact the Lost and Found at Iidabashi Station (Namboku Line) or the Tokyo Metro Customer Relations Center.</li>
<li><strong>Station office.</strong> 03-3832-6629. Address: 3-19-6 Higashiueno, Taito-ku, Tokyo.</li>
<li><strong>Busy.</strong> Tokyo Metro counts 191,804 passengers a day on average in 2025 at Ueno (10th of its 130 stations), not counting passengers on directly connected lines.</li>
</ul>
""" + sources(["metro", "jrmap", "parkacc"], "Routes change, so follow the signs.")

PARK = """<h2 id="park">Ueno Park and the cherry blossoms</h2>
<p>Ueno Park (Ueno Onshi Park) is a short walk from the station. The Tokyo Metropolitan Government calls it one of Japan's best-known cherry blossom spots, and the park association describes it as known for cherry blossoms and Shinobazu Pond. It opened in 1873 and was one of Japan's first designated parks.</p>
<figure style="margin:28px 0;text-align:center;">
<img src="__SAKURA_IMG__" alt="An avenue of cherry trees in full bloom in Ueno Park, with paper lanterns along the path" width="1200" height="762" style="width:100%;height:auto;border-radius:12px;object-fit:cover;" loading="lazy">
<figcaption style="font-size:0.82rem;color:#999;margin-top:8px;font-style:italic;">Cherry trees in full bloom in Ueno Park. Photo: PAKUTASO.</figcaption>
</figure>
<ul>
<li><strong>Walking times (park office).</strong> JR Ueno (Yamanote, Keihin-Tohoku, Takasaki and Utsunomiya lines): 2 minutes. Tokyo Metro Ginza and Hibiya lines, Ueno: 4 minutes. Toei Oedo Line, Ueno-okachimachi: 5 minutes. Keisei Main Line, Keisei Ueno: 1 minute.</li>
<li><strong>From JR Ueno.</strong> Use the Park Gate or the Panda Bridge Exit on 3F.</li>
<li><strong>Opening hours.</strong> 5:00 to 23:00. There is no entry outside these hours.</li>
<li><strong>Cherry trees.</strong> About 1,200, among the park's main plants.</li>
<li><strong>When.</strong> The park office says the blossoms last for about two months, from the early-flowering kanzakura to the Somei-yoshino. Dates change every year, so check the official cherry blossom forecasts nearer the time before you plan a day around them.</li>
<li><strong>Summer.</strong> The lotus on Shinobazu Pond is at its best in late July.</li>
<li><strong>Park rules.</strong> The park's rules page lists no fireworks and no catch-ball, among others.</li>
<li><strong>Nearby.</strong> Keisei lists Ueno Park, Ueno Zoo, the Tokyo National Museum, Kaneiji Temple, the National Science Museum, Shinobazu Pond and Ameyoko near Keisei Ueno. Check each one's own opening hours.</li>
</ul>
""" + sources(["parkacc", "parkabout", "parkhi", "parkrules", "tpa", "skyueno"], "Hours and rules can change, so check the park's pages.")

PARK = PARK.replace("__SAKURA_IMG__", SAKURA_URL)

CONNECTED = """<h2 id="connected">Getting online: eSIM</h2>
<p>You will want a connection for maps, messages and the blossom forecast. We did not find official free Wi-Fi or SIM counters on the Ueno station pages we read, so an eSIM installed before you arrive is the simplest choice.</p>
<ul>
<li><strong>eSIM:</strong> install it on your phone and switch it on when you need it. It needs an eSIM-ready, unlocked phone.</li>
</ul>
"""
# ---- Klook placements: none on this page (D46: no new Klook links). KLK stays empty, so klp() renders nothing.
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
<div id="psPocketBar" role="region" aria-label="Ueno Station Pocket Guide">
<div class="t"><b>Get the Ueno Station Pocket Guide</b><span>Free. Works offline at the station.</span></div>
<a class="go" href="/ueno-pocket?src=bar">Get it</a>
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
<p>Open the Ueno Station Pocket Guide once while you have signal, then add it to your home screen. At the station it opens like an app, even with no connection.</p>
<p><a class="ps-btn2" href="/ueno-pocket?src=box" onclick="try{window.gtag&&gtag('event','pocket_prompt',{event_category:'engagement',action:'open_box',page_path:location.pathname});}catch(e){}" style="display:inline-block;text-decoration:none;">Open the Pocket Guide</a></p>
<ul>
<li><strong>iPhone:</strong> open it in Safari, tap the Share button, then "Add to Home Screen".</li>
<li><strong>Android:</strong> open it in Chrome, tap the menu (three dots), then "Add to Home screen" or "Install app".</li>
</ul>
</div>"""

FACILITIES = """<h2 id="facilities">Facilities in the station</h2>
<p>This table follows JR East's Ueno Station map and Tokyo Metro's Ueno Station page, checked on 23 November 2026. A dash means the pages we read do not list one.</p>
<div class="ps-scroll">
<table class="checklist-table">
<thead><tr><th>Facility</th><th>What we found</th></tr></thead>
<tbody>
<tr><td><strong>Ticket Office and JR EAST Travel Service Center</strong></td><td>1F, by the Central Gate ticket hall</td></tr>
<tr><td><strong>Passport Reader &amp; Reserved Seat Ticket Vending Machine</strong></td><td>1F, by the Central Gate tickets</td></tr>
<tr><td><strong>Question &amp; Answer</strong></td><td>1F, beside the Central Gate</td></tr>
<tr><td><strong>Coin lockers</strong></td><td>1F (near the Main Exit and taxi side; inside the gates by the Shinkansen transfer), 2F (along the concourse to the Iriya Exit), 3F (by the Panda Bridge Exit and near the Iriya Gate). No official prices found</td></tr>
<tr><td><strong>Lost &amp; Found (JR)</strong></td><td>2F, near the Panda Bridge Exit stairs</td></tr>
<tr><td><strong>Lifts</strong></td><td>A to I: A to F from 3F to platforms 1 to 12, G and H to the Shinkansen platforms, I to the 2F concourse outside the gates</td></tr>
<tr><td><strong>Shinkansen concourse</strong></td><td>A waiting room and &ldquo;Tokimeki Square&rdquo;</td></tr>
<tr><td><strong>Shops</strong></td><td>atre Ueno (outside the gates, 1F and 2F), ecute Ueno (inside the gates, 3F), NewDays kiosks</td></tr>
<tr><td><strong>Statue of Panda</strong></td><td>3F, marked on JR East's map</td></tr>
<tr><td><strong>Tokyo Metro ticket machines</strong></td><td>Multi-functional machines at all ticket offices, first train to last (Tokyo Metro)</td></tr>
<tr><td><strong>ATMs, currency exchange, toilets</strong></td><td>-</td></tr>
</tbody>
</table>
</div>
<h3>If you need help</h3>
<p>If you are tired, unsure or carrying a lot, go straight to the Question &amp; Answer counter or a staff member instead of searching on your own.</p>
""" + sources(["jrmap", "metro"], "Shops and counters can change.")

JB_LINK = "https://www.japan-bullettrain.com/?via=packsmart"
JB_SHIN = '<svg style="display:block;width:100%;height:auto;" aria-hidden="true" focusable="false" viewBox="0 0 320 170" xmlns="http://www.w3.org/2000/svg"><rect width="320" height="170" fill="#E8F1FE"/><circle cx="64" cy="40" r="20" fill="#FFE3CC"/><path d="M120 120 L188 44 L204 60 L214 52 L282 120Z" fill="#b9cdf0"/><path d="M174 62 L188 44 L204 60 L196 64 L188 58 L181 66Z" fill="#fff"/><path d="M0 124 L60 96 L110 120 L150 104 L200 124Z" fill="#d3e0f7"/><g fill="#f7b9cf"><circle cx="262" cy="104" r="14"/><circle cx="276" cy="112" r="12"/><circle cx="250" cy="114" r="11"/></g><rect x="260" y="112" width="4" height="22" fill="#8b5a3c"/><rect y="132" width="320" height="38" fill="#d3e0f7"/><rect y="146" width="320" height="4" fill="#9db8e6"/><g><path d="M14 138 L14 110 C14 104 20 100 28 100 L214 100 C250 100 286 118 306 138 Z" fill="#fff" stroke="#0f0f23" stroke-width="2.5"/><path d="M14 124 L300 124 L304 130 L14 130Z" fill="#2563EB"/><g fill="#7fb4f5" stroke="#0f0f23" stroke-width="1.5"><rect x="34" y="106" width="20" height="11" rx="2"/><rect x="62" y="106" width="20" height="11" rx="2"/><rect x="90" y="106" width="20" height="11" rx="2"/><rect x="118" y="106" width="20" height="11" rx="2"/><rect x="146" y="106" width="20" height="11" rx="2"/><rect x="174" y="106" width="20" height="11" rx="2"/></g><path d="M214 101 C238 102 262 112 282 124 L214 124Z" fill="#0f0f23" opacity=".9"/><g fill="#0f0f23"><circle cx="60" cy="140" r="5"/><circle cx="104" cy="140" r="5"/><circle cx="200" cy="140" r="5"/><circle cx="244" cy="140" r="5"/></g></g><g stroke="#2563EB" stroke-width="3" stroke-linecap="round"><path d="M4 108h22"/><path d="M0 118h16"/><path d="M6 128h12"/></g></svg>'
JB_TRAIN = '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M5 16V8a5 5 0 0 1 5-5h4a5 5 0 0 1 5 5v8a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2z"/><path d="M5 11h14M9 15h.01M15 15h.01M8 18l-2 3M16 18l2 3"/></svg>'


def jb_node(text):
    return '<div class="jb-rn"><span class="jb-dot"></span><strong style="color:#0f0f23;font-size:1rem;">%s</strong></div>' % text


def jb_leg(text, icon="", blue=False):
    return '<div class="jb-lg%s"><span class="jb-ln"></span><span class="jb-lt">%s%s</span></div>' % (" jb-blue" if blue else "", icon, text)


JB_SHINKANSEN = (
    '<div data-ps-placement="jw-shinkansen-ueno" style="max-width:800px;margin:20px auto;padding:20px;background:#f0faf7;border:1px solid #cdeee5;border-left:4px solid #00C9A7;border-radius:12px;">'
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
    + jb_node("Ueno, tracks 19 and 20 (underground)") + jb_leg("Shinkansen (bullet train)", JB_TRAIN, True) + jb_node("Tohoku, Yamagata, Akita, Hokkaido, Joetsu and Hokuriku lines")
    + jb_node("Ueno, tracks 21 and 22") + jb_leg("Shinkansen (bullet train)", JB_TRAIN, True) + jb_node("Tokyo Station") +
    '</div></div>'
    '<div class="jb-row"><div class="jb-tx">'
    '<p style="margin:0 0 8px;font-size:0.95rem;line-height:1.5;color:#333;">Ueno has its own Shinkansen platforms, tracks 19 to 22, underground (JR East&rsquo;s station map). Tracks 19 and 20 are for the Tohoku, Yamagata, Akita, Hokkaido, Joetsu and Hokuriku Shinkansen, and tracks 21 and 22 for Tokyo. Use the Transfer to Shinkansen gate on 1F, or lifts G and H. If you want your tickets sorted before you travel, you can book them online. The company says its tickets cover the JR East, JR West, JR Central and JR Kyushu Shinkansen lines and are collected with a QR code.</p>'
    '</div><div class="jb-bt">'
    '<a class="ps-jb-btn" href="' + JB_LINK + '" target="_blank" rel="nofollow noopener sponsored" style="display:block;box-sizing:border-box;text-decoration:none;"><span class="ps-jb-ghost" style="display:block;border:1.5px solid #00C9A7;background:#fff;color:#0a8f78;text-align:center;font-weight:700;font-size:1rem;border-radius:12px;padding:11px 14px;min-height:46px;line-height:1.25;">Book Shinkansen tickets &rarr;</span><span style="display:block;text-align:center;font-size:0.76rem;color:#777;margin-top:6px;">Partner link</span></a>'
    '<p style="margin:10px 0 0;font-size:0.85rem;line-height:1.5;color:#555;">You can also buy at a station on the day, so check the price and the change and cancellation rules before you pay.</p>'
    '</div></div></div>'
)


# ---- GetYourGuide box: tours and tickets for a search on Ueno (partner D7IXONS, its own cmp so clicks can be told apart).
#      Hides itself if the widget does not load.
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

# Ueno: the widget shows the partner's own top results for a search (data-gyg-q, as w61), not hand-picked tour IDs,
# plus a plain search link (CLAUDE.md: a search for what the link names, never the bare homepage).
GYG_Q = "Ueno Tokyo"
GYG_CMP = "ps-ueno-station-gyg"
GYG_SEARCH = "https://www.getyourguide.com/s/?q=%s&partner_id=%s&cmp=ps-ueno-station" % (quote(GYG_Q), GYG_PARTNER)
GYGQ_TPL = """<div class="ps-gyg" data-ps-placement="__PID__">
<strong class="ps-gyg-h">__HEAD__</strong>
<p class="ps-gyg-s">__BLURB__</p>
<div class="ps-gyg-w"><div class="ps-gyg-slot" data-gyg-href="https://widget.getyourguide.com/default/activities.frame" data-gyg-locale-code="en-US" data-gyg-number-of-items="3" data-gyg-partner-id="__PARTNER__"></div></div>
<p class="ps-gyg-s" style="margin:8px 0 0;"><a href="__SEARCH__" target="_blank" rel="nofollow noopener sponsored" style="color:#0a8f78;font-weight:700;">See more tours and tickets around Ueno</a> (partner link)</p>
<script>
(function(){
var root=document.currentScript.parentNode;
var q='__Q__',cmp='__CMP__';
var slot=root.querySelector('.ps-gyg-slot'),phone=window.matchMedia('(max-width:600px)'),started=false;
function render(){
slot.setAttribute('data-gyg-widget','activities');
slot.setAttribute('data-gyg-number-of-items',phone.matches?'2':'3');
slot.setAttribute('data-gyg-q',q);
slot.setAttribute('data-gyg-cmp',cmp);
var t=0;(function go(){if(window.GYG&&window.GYG.refresh){window.GYG.refresh()}else if(t++<50){setTimeout(go,200)}})();}
function start(){if(started)return;started=true;render();var n=0;(function watch(){if(slot.querySelector('iframe'))return;if(++n>15){root.style.display='none';return}setTimeout(watch,1000)})()}
if('IntersectionObserver' in window){var io=new IntersectionObserver(function(e){if(e[0].isIntersecting){io.disconnect();start()}},{rootMargin:'400px 0px'});io.observe(root)}else{start()}
if(phone.addEventListener){phone.addEventListener('change',function(){if(started)render()})}
})();
</script>
</div>"""
GYG_UENO = (GYGQ_TPL.replace("__PID__", "gyg-ueno-station").replace("__HEAD__", "Tours and tickets around Ueno")
            .replace("__BLURB__", "Popular tours and tickets for Ueno and Tokyo, as listed by our partner. Check what is included before you book.")
            .replace("__PARTNER__", GYG_PARTNER).replace("__SEARCH__", html.escape(GYG_SEARCH))
            .replace("__Q__", GYG_Q).replace("__CMP__", GYG_CMP))

LEAVING = """<h2 id="leaving">Leaving Ueno: a checklist</h2>
<ul>
<li><strong>Flying from Narita?</strong> Take the Keisei Skyliner from Keisei Ueno, not JR's Narita Line (tracks 10 to 12 go to Narita city). See our <a href="/blog/narita-airport-guide">Narita Airport guide</a>.</li>
<li><strong>Holding the &ldquo;Skyliner &amp; Tokyo Subway Ticket&rdquo; or the &ldquo;Greater Tokyo Pass&rdquo;?</strong> Board at Ueno: Keisei says you cannot transfer at Nippori with these.</li>
<li><strong>Early or late flight?</strong> We did not find the first and last Skyliner on the pages we read. Check Keisei's timetable the day before.</li>
<li><strong>Going by bullet train?</strong> Shinkansen tracks 19 to 22 are underground. Use the Transfer to Shinkansen gate (1F), or lifts G and H.</li>
<li><strong>Collect your bags.</strong> Lockers are on 1F, 2F and 3F, so remember which floor you used.</li>
<li><strong>Allow time for the station itself.</strong> We did not find official walking times between gates and platforms, so add a buffer, especially with luggage.</li>
<li><strong>Heading south to Kyoto or Osaka?</strong> Tracks 21 and 22 are for Tokyo. See our <a href="/blog/tokyo-station-guide">Tokyo Station guide</a>.</li>
</ul>
""" + sources(["skyueno", "nippori", "jrmap"], "Times change, so check the operator.")
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
    '<p style="font-size:0.85rem;color:#666;margin:0 0 0.6rem;">Published November 23, 2026 · Last updated November 2026 · Facts checked 23 Nov 2026</p>',
    AFFILIATE_P,
    share,
    PRINT_CSS,
    WARN_CSS,
    '<p>Ueno Station is where many visitors first meet Tokyo: the Keisei Skyliner from Narita Airport arrives at Keisei Ueno, Keisei&rsquo;s own station, and Ueno Park, with its museums and cherry trees, is a short walk from the JR gates. '
    'It also has a JR line called the &ldquo;Narita Line&rdquo; that does not go to the airport. '
    'This guide is written in plain English so that a first-time visitor, a family or an older traveller can follow it step by step. '
    'You can print the one-page card below and carry it with you.</p>',
    toc_html,
    CARD,
    NARITA,
    EXITS,
    DIAGRAM,
    PLATFORMS,
    JB_SHINKANSEN,
    METRO,
    PARK,
    GYG_UENO,
    CONNECTED,
    airalo,
    LUGGAGE,
    FINDER,
    SAVE_BOX,
    FACILITIES,
    HELP,
    LEAVING,
    '<div class="tip-box">\n    <strong>Planning more of Japan?</strong> Our <a href="/blog/japan-travel-packing-guide">Japan travel and packing guide</a> covers what to pack, rail passes, etiquette and a budget breakdown, and the <a href="/blog/japan-7-day-itinerary-budget">7-day Japan itinerary</a> shows how a first week can look. Flying out? See our <a href="/blog/narita-airport-guide">Narita Airport guide</a> or <a href="/blog/haneda-airport-guide">Haneda Airport guide</a>.\n</div>',
    "<!-- FIRST-HAND NOTES: add notes and photos from an Ueno Station visit here -->",
    faq_html(),
    ABOUT,
    RELATED,
    POCKET_BAR,
])
# one Sources list before the FAQ instead of a note under each section (Ari, 23 Nov 2026).
# A section keeps only its caution ("Times change, so check the operator.") as a short note.
_src_links = []
def _gather(m):
    body = m.group(1)
    for a in re.findall(r'<a [^>]*>.*?</a>', body):
        if a not in _src_links:
            _src_links.append(a)
    for plain in re.findall(r'(?:^|, |and )([A-Z][^,<]*\([a-z0-9.-]+\.[a-z]{2,}\))', body):
        if plain not in _src_links:
            _src_links.append(plain)
    rest = body.split(CHECKED, 1)[1].strip() if CHECKED in body else ""
    return '<p class="ps-note">%s</p>' % rest if rest else ""
BODY = re.sub(r'<p class="ps-note">Sources: (.*?)</p>\n?', _gather, BODY, flags=re.S)
if "Sources: " in BODY or len(_src_links) < 10:
    die("source notes not gathered (%d links)" % len(_src_links))
SOURCES = ('<h2 id="sources">Sources</h2>\n<p>Every station fact on this page comes from the official sites below, '
           'checked on 23 November 2026. Stations change, so follow the signs on the day.</p>\n<ul class="ps-sources">\n'
           + "".join("<li>%s</li>\n" % a for a in _src_links) + "</ul>")
_faq = BODY.index('<h2 id="faq">')
BODY = BODY[:_faq] + SOURCES + "\n\n" + BODY[_faq:]
# hero button: a quiet way into the Pocket Guide from the top of the article (as w42)
HERO_CTA = ('        <div style="margin:48px 0 0;text-align:center;">'
            '<a href="/ueno-pocket?src=hero" onclick="try{window.gtag&&gtag(\'event\',\'pocket_prompt\',{event_category:\'engagement\',action:\'open_hero\',page_path:location.pathname});}catch(e){}" '
            'style="display:inline-flex;align-items:center;gap:12px;background:#00C9A7;color:#0f0f23;text-align:left;padding:12px 14px 12px 20px;width:340px;max-width:100%;box-sizing:border-box;border-radius:12px;text-decoration:none;min-height:44px;box-shadow:0 6px 18px rgba(0,0,0,.28);line-height:1.2;">'
            '<span style="flex:1;min-width:0;text-align:left;">'
            '<span style="display:block;font-weight:700;font-size:0.8rem;opacity:0.8;">Save to your phone</span>'
            '<span style="display:block;font-weight:800;font-size:1.05rem;margin-top:2px;">Ueno Station Pocket Guide</span>'
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
    '        <div class="meta">Station Guide • Japan · Published 23 Nov 2026 · __READ__ min read</div>',
    HERO_CTA,
    ('        <div style="position:absolute;left:12px;right:12px;bottom:8px;font-size:0.7rem;opacity:0.7;text-align:center;">Photo: PAKUTASO. Illustrative image of JR Ueno Station&rsquo;s main building.</div>' if HERO_URL else ''),
    "</div>",
    "",
    '    <div class="content">',
    "",
])
tail = "\n".join(["    </div>", ""] + t[FOOT:])

page = head + "\n" + BODY + "\n\n" + tail
page = page.replace("__READ__", str(READ_MIN))


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



# ---- Ueno Station Pocket Guide: standalone page + service worker + manifest (works offline once visited)
POCKET_PATH = "/ueno-pocket"
THEME = "#b8306a"   # sakura pink, one colour per guide
# ---- Pocket Guide analytics (v47): anonymous taps only, no accounts, honours Do Not Track / GPC
GUIDE_ID = "ueno"
AIRPORT_CODE = "UENO-STN"
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
    if(/^tel:/i.test(h)){ var d=h.replace(/^tel:/i,'').replace(/[^0-9+]/g,''); var nm={'119':'fire_ambulance','110':'police','+815038162787':'help_line','+81338326629':'metro_office'}; pgTrack('pg_call',{dest:nm[d]||d,where:whereNow()}); return; }
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

POCKET_SVG = re.search(r'<svg id="uenDiagram".*?</svg>', DIAGRAM, re.S).group(0).replace('id="uenDiagram"', 'id="pkDiagram"').replace('id="uenT"', 'id="pkT"').replace('id="uenD"', 'id="pkD"').replace('aria-labelledby="uenT uenD"', 'aria-labelledby="pkT pkD"')
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
<title>Ueno Station Pocket Guide | PackSmart</title>
<meta name="description" content="A simple Ueno Station helper that works offline: which gate for Ueno Park, the Skyliner to Narita (not JR's Narita Line), platforms by floor, Metro, lockers and more. By PackSmart.">
<meta name="robots" content="noindex,follow">
<link rel="canonical" href="__GUIDE_URL__">
<meta name="theme-color" content="#1a1a3e">
<link rel="manifest" href="/ueno-pocket.webmanifest">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" href="/images/ueno-apple-touch-180.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Ueno">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<script>__PG_BOOT__</script>
<style>__CSS__</style>
</head>
<body>
<header class="top">
<div><strong>Ueno Station Pocket Guide</strong><span class="by">by PackSmart &middot; 23 Nov 2026</span></div>
<div class="status" id="status" role="status">Checking...</div>
</header>
<button type="button" class="inst-strip" id="instStrip" hidden><span class="ico" aria-hidden="true">&#128242;</span><span><b>Add this to your home screen</b><br>so it works with no internet</span><span class="go">How</span></button>
<div class="panels" id="panels">
<section class="panel" id="p-find" role="tabpanel" aria-labelledby="t-find">
<p class="seg-h">Which level are you on?</p>
<div class="seg" id="seg"></div>
<p class="seg-h" style="margin-top:14px">What do you need? <span class="small">Tap one.</span></p>
<div class="pager" id="pager"><div class="track" id="track"><div class="tiles pane" id="tiles"></div><div class="tiles pane off" id="tiles2" aria-hidden="true"></div></div></div>
<p class="hint">Floors can change. Ask station staff.</p>
<div id="sponsor" hidden></div>
<noscript><p class="card">This guide needs JavaScript. Please turn it on, or ask at any information counter.</p></noscript>
</section>
<section class="panel" id="p-map" role="tabpanel" aria-labelledby="t-map" hidden>
<p class="seg-h" style="margin-top:2px">Which level are you on?</p>
<div class="seg" id="mseg"></div>
<p class="lead2" id="mLead" style="margin-top:10px">Ueno Park: 3F (Park Gate, Panda Bridge). Taxi and ticket office: 1F (Central Gate).</p>
<div class="tmap" id="tmap">
<div class="tcard t3" data-t="T1"><div class="badge">3F</div><div class="tb"><h3>Park level</h3><p>Park Gate, Panda Bridge Exit, Iriya Gate. ecute Ueno shops inside the gates. Statue of Panda</p><p class="stn"><span aria-hidden="true">&#127800;</span> Ueno Park: Park Gate or Panda Bridge</p></div></div>
<div class="tlink"><span aria-hidden="true">&#128727;</span><span>Lifts A to F: 3F to platforms 1 to 12</span></div>
<div class="tcard t2" data-t="F2"><div class="badge">2F</div><div class="tb"><h3>JR tracks 1 to 12</h3><p>Yamanote Line 2 and 3, Keihin-Tohoku 1 and 4, Ueno-Tokyo Line 7 and 8. Lost &amp; Found by the Panda Bridge Exit stairs</p><p class="stn warn"><span aria-hidden="true">&#9888;&#65039;</span> Narita Line 10 to 12: Narita city, not the airport</p></div></div>
<div class="tcard t1" data-t="T2"><div class="badge">1F</div><div class="tb"><h3>Ground level</h3><p>Central Gate, Main Exit, taxi stop, ticket office, Travel Service Center. Asakusa, Yamashita and Iriya exits. JR tracks 13 to 17. M2 floor: Shinobazu Gate</p><p class="stn"><span aria-hidden="true">&#128647;</span> Tokyo Metro: &ldquo;for Tokyo Metro&rdquo; signs by the Central Gate</p></div></div>
<div class="tlink"><span aria-hidden="true">&#128645;</span><span>Transfer to Shinkansen gate (1F), lifts G and H</span></div>
<div class="tcard t2" data-t="UG"><div class="badge">B</div><div class="tb"><h3>Underground, B1 to B4</h3><p>Shinkansen tracks 19 to 22. 19 and 20: Tohoku, Yamagata, Akita, Hokkaido, Joetsu, Hokuriku. 21 and 22: for Tokyo. Waiting room</p></div></div>
</div>
<p class="small" style="text-align:center;margin-top:10px">Simplified, not to scale. Keisei Ueno (Skyliner) is a separate station. Follow the signs.</p>
</section>
<section class="panel" id="p-arrive" role="tabpanel" aria-labelledby="t-arrive" hidden>
<p class="lead2">Just arrived at Ueno? Tap a step to tick it off.</p>
<ol class="steps" id="arrSteps"></ol>
<button type="button" class="reset" id="arrReset" hidden>Clear ticks</button>
<p class="sec-h">Then, once you are out</p>
<div class="tiles" id="arrTiles"></div>
</section>
<section class="panel" id="p-depart" role="tabpanel" aria-labelledby="t-depart" hidden>
<div class="heroline"><span class="big2">41&nbsp;min</span><span><b>Skyliner, Keisei Ueno and Narita Airport.</b><br>Keisei&rsquo;s time from Terminal 2&middot;3 to Keisei Ueno. Not JR&rsquo;s Narita Line.</span></div>
<div class="seg2" id="depSeg" role="group" aria-label="Departure sections"><button type="button" data-d="before" aria-pressed="true">Before you go</button><button type="button" data-d="air" aria-pressed="false">At the station</button></div>
<div id="depBefore">
<div class="tiles" id="depTiles"></div>
<p class="hint">Tap one for the details. Times change, so check the operator.</p>
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
<p class="small" style="margin-top:0">JR: the Question &amp; Answer counter is beside the Central Gate (1F). Lost &amp; Found is on 2F, by the Panda Bridge Exit stairs. Staff will help, so just ask.</p>
<a class="num air" href="tel:+81338326629"><span class="ni" aria-hidden="true">&#128647;</span><span class="nt"><b>Tokyo Metro Ueno station office</b><span>03-3832-6629</span><small>Ginza and Hibiya lines</small></span></a>
<p class="sec-h">Help or travel questions</p>
<a class="num hot" href="tel:+815038162787"><span class="ni" aria-hidden="true">&#128222;</span><span class="nt"><b>Japan Visitor Hotline</b><span>050-3816-2787</span><small>24 hours. English, Chinese, Korean</small></span></a>
</div>
<div class="tiles hnav" id="hnav2"></div>
</div>
</div></div>
<div class="quiet"><div class="card slim" id="shareCard" hidden><div class="row"><div><h2>Helping someone travel?</h2><p>Send them this guide for offline use.</p></div><button type="button" class="big" id="shareBtn">Send it</button></div></div>
<div class="card slim install" id="install"><div class="row"><div><h2>Keep this on your phone</h2><p>Add it to your home screen. Works offline.</p><p class="small" id="instDesk">Open this page on your phone, then add it to your home screen.</p></div><div id="instHow" hidden><button type="button" class="big" id="instBtn">Show me</button></div></div></div>
<p class="small">Station details come from JR East&rsquo;s Ueno Station map, Tokyo Metro, Keisei and the Ueno Park pages of the Tokyo Metropolitan Government, checked 23 November 2026. Floors, opening hours and counters can change. If you cannot find something, ask station staff. Found something out of date? <a href="/contact">Tell us</a> (needs internet). We count anonymous taps to improve this guide: no name, no account. <a href="/privacy-policy">Privacy</a> &middot; <a href="#" id="pgOpt">Turn off counting</a>. The full guide, with platforms, exits and Ueno Park, is at <a href="__GUIDE_URL__">packsmartapp.com</a> (needs internet).</p></div>
</section>
</div>
<nav class="tabs" role="tablist" aria-label="Sections">
<button type="button" role="tab" id="t-find" data-tab="find" aria-selected="true"><span aria-hidden="true">&#128269;</span>Find</button>
<button type="button" role="tab" id="t-map" data-tab="map" aria-selected="false"><span aria-hidden="true">&#128506;&#65039;</span>Floors</button>
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
  var ICON={prayer:'\\uD83D\\uDE4F',baby:'\\uD83C\\uDF7C',quiet:'\\uD83E\\uDD2B',info:'\\u2139\\uFE0F',help:'\\u267F',lockers:'\\uD83E\\uDDF3',wifi:'\\uD83D\\uDCF6',shower:'\\uD83D\\uDEBF',internet:'\\uD83D\\uDCBB',play:'\\uD83E\\uDDF8',smoking:'\\uD83D\\uDEAC',toilet:'\\uD83D\\uDEBB',food:'\\uD83C\\uDF5C',money:'\\uD83D\\uDCB4',unwell:'\\uD83C\\uDFE5',pharmacy:'\\uD83D\\uDC8A',trains:'\\uD83D\\uDE86',tickets:'\\uD83C\\uDFAB',phone:'\\uD83D\\uDCF6',charge:'\\uD83D\\uDD0B',exits:'\\uD83D\\uDEAA',park:'\\uD83C\\uDF38',lost:'\\uD83D\\uDCE6',more:'\\u2795'};
  var SHORT={prayer:'Prayer room',baby:'Nursing room',quiet:'Quiet space',info:'Information counter',help:'Wheelchair and help',lockers:'Lockers',wifi:'Wi-Fi rental',shower:'Showers',internet:'Free internet',play:'Kids play area',smoking:'Smoking room',toilet:'Toilets',food:'Shops and food',money:'Money and ATMs',unwell:'Feeling unwell',pharmacy:'Pharmacy',trains:'Trains and platforms',tickets:'Tickets and passes',phone:'Phone and Wi-Fi',charge:'Phone charging',exits:'Which exit?',park:'Ueno Park',lost:'Lost and found',more:'More places'};
  var term='ALL', lastTile=null;
  try{ var s=localStorage.getItem('uenTerm'); if(s&&/^(ALL|T1|T2)$/.test(s)) term=s; }catch(e){}
  function $(id){return document.getElementById(id);}
  /* side selector */
  var seg=$('seg');
  function segBtn(id,html,cls){
    var b=document.createElement('button'); b.type='button'; b.setAttribute('data-t',id); if(cls) b.className=cls;
    b.innerHTML=html; b.addEventListener('click',function(){ term=id; try{localStorage.setItem('uenTerm',id);}catch(e){} paintSeg(); renderDep(); }); return b;
  }
  var CAP={T1:['Park Gate','3F'],T2:['Central Gate','1F']};
  D.terms.forEach(function(t){ seg.appendChild(segBtn(t[0],'<small>'+CAP[t[0]][0]+'</small><b>'+CAP[t[0]][1]+'</b>')); });
  seg.appendChild(segBtn('ALL','Not sure','txt'));
  var mseg=$('mseg');
  D.terms.forEach(function(t){ mseg.appendChild(segBtn(t[0],'<small>'+CAP[t[0]][0]+'</small><b>'+CAP[t[0]][1]+'</b>')); });
  mseg.appendChild(segBtn('ALL','Not sure','txt'));
  function paintSeg(){ [seg,mseg].forEach(function(g){ [].forEach.call(g.children,function(b){ b.setAttribute('aria-pressed',b.getAttribute('data-t')===term?'true':'false'); }); }); paintMap(); }
  /* Floors tab: marks the level the person chose */
  function paintMap(){
    var personal=(term==='T1'||term==='T2');
    $('mLead').textContent=personal?(term==='T1'?'You are on 3F, the park level. Tracks 1 to 12 are on 2F, the Central Gate on 1F.':'You are on 1F, the ground level. For Ueno Park, go up to 3F (Park Gate, Panda Bridge).'):'Ueno Park: 3F (Park Gate, Panda Bridge). Taxi and ticket office: 1F (Central Gate).';
    [].forEach.call(document.querySelectorAll('#tmap .tcard'),function(c){
      var id=c.getAttribute('data-t'), tb=c.querySelector('.tb');
      [].forEach.call(c.querySelectorAll('.heretag'),function(e){ e.parentNode.removeChild(e); });
      c.classList.toggle('here',personal&&id===term);
      if(personal&&id===term){ var g=document.createElement('p'); g.className='heretag'; g.textContent='You are here'; tb.insertBefore(g,tb.firstChild); }
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
  var trainsIt=['trains','Trains and platforms',{}];
  var exitsIt=['exits','Which exit?',{}];
  var parkIt=['park','Ueno Park',{}];
  var LIST=[];
  ['exits','park','lockers','info','tickets','trains','help','lost','money','toilet','food','unwell'].forEach(function(id){
    LIST.push(id==='trains'?trainsIt:id==='exits'?exitsIt:id==='park'?parkIt:item(id));
  });
  LIST.forEach(function(it,n){
    var b=document.createElement('button'); b.type='button'; b.className='tile c'+(n%3); b.setAttribute('data-id',it[0]);
    var ic=document.createElement('span'); ic.className='ic'; ic.setAttribute('aria-hidden','true'); ic.textContent=ICON[it[0]]||'\\u2022';
    var tx=document.createElement('span'); tx.className='tx'; tx.textContent=SHORT[it[0]]||it[1];
    b.appendChild(ic); b.appendChild(tx);
    b.addEventListener('click',function(){ if(it[0]==='trains'){ openInfo(ICON.trains,it[1],trainHTML(),b); } else if(it[0]==='exits'){ openInfo(ICON.exits,it[1],exitHTML(),b); } else if(it[0]==='park'){ openInfo(ICON.park,it[1],parkHTML(),b); } else { openSheet(it,b); } });
    (n<MAIN?tiles:tiles2).appendChild(b);
    if(n===MAIN-1){ tiles.appendChild(pill('pgnext','\\u2192','More','Money, toilets, shops, feeling unwell',function(){ slideTo(1); })); }
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
    if(term==='ALL'&&D.terms.every(function(t){return it[2][t[0]]===it[2][D.terms[0][0]];})){ shB.appendChild(ans('Both levels',it[2][D.terms[0][0]],false)); }
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
  var SRCL='<p class="sm">Source: JR East Ueno Station map, checked 23 November 2026. Floors can change. Follow the signs.</p>';
  function trainHTML(){
    var h='<p class="n2">JR platforms (JR East station map). Check the board: platforms can change.</p>';
    h+='<p class="sm"><b>2F</b></p><ul class="pl"><li><b>1:</b> Keihin-Tohoku Line for Akabane, Urawa and Omiya.</li>'
      +'<li><b>2:</b> Yamanote Line for Tabata, Ikebukuro and Shinjuku.</li>'
      +'<li><b>3:</b> Yamanote Line for Akihabara, Tokyo, Hamamatsucho and Shinagawa.</li>'
      +'<li><b>4:</b> Keihin-Tohoku Line for Kamata, Kawasaki, Yokohama and Kannai.</li>'
      +'<li><b>5:</b> Utsunomiya and Takasaki lines for Akabane, Omiya, Utsunomiya and Takasaki.</li>'
      +'<li><b>6:</b> Joban Line, Joban Line (Rapid), Narita Line, Utsunomiya and Takasaki lines.</li>'
      +'<li><b>7:</b> Ueno-Tokyo Line for Tokyo, Shinagawa, Yokohama, Odawara and Atami.</li>'
      +'<li><b>8:</b> Joban Line for Kashiwa, Tsuchiura, Mito and Iwaki; Ueno-Tokyo Line for Tokyo and Shinagawa.</li>'
      +'<li><b>9:</b> Joban Line, Joban Line (Rapid), Narita Line, Ueno-Tokyo Line.</li>'
      +'<li><b>10 to 12:</b> Joban Line, Joban Line (Rapid), Narita Line for Matsudo, Toride, Mito and Narita (the city, <b>not the airport</b>).</li></ul>';
    h+='<p class="sm"><b>1F</b></p><ul class="pl"><li><b>13 to 15:</b> Utsunomiya and Takasaki lines for Akabane, Omiya, Utsunomiya and Takasaki.</li>'
      +'<li><b>16:</b> Joban Line for Kashiwa, Toride, Tsuchiura and Mito; Utsunomiya and Takasaki lines.</li>'
      +'<li><b>17:</b> Joban Line for Kashiwa, Toride, Tsuchiura and Mito.</li></ul>';
    h+='<p class="sm"><b>Underground (B4 to B1)</b></p><ul class="pl"><li><b>19 and 20:</b> Tohoku, Yamagata, Akita, Hokkaido, Joetsu and Hokuriku Shinkansen.</li>'
      +'<li><b>21 and 22:</b> Shinkansen for Tokyo.</li></ul>';
    h+='<ul class="pl"><li><b>Tokyo Metro:</b> Ginza Line G16, Hibiya Line H18. Follow the &ldquo;for Tokyo Metro&rdquo; signs by the Central Gate (1F).</li>'
      +'<li><b>Narita Airport:</b> the Keisei Skyliner from Keisei Ueno, a separate station.</li></ul>';
    return h+SRCL;
  }
  function exitHTML(){
    return '<ul class="pl"><li><b>Ueno Park:</b> Park Gate or Panda Bridge Exit, 3F. About 2 min on foot (park office).</li>'
      +'<li><b>Ticket office, Travel Service Center, taxi:</b> Central Gate and Main Exit, 1F.</li>'
      +'<li><b>Tokyo Metro:</b> the &ldquo;for Tokyo Metro&rdquo; signs by the Central Gate (1F).</li>'
      +'<li><b>Shinkansen:</b> the Transfer to Shinkansen gate inside the station (1F), or lifts G and H.</li>'
      +'<li><b>Iriya side:</b> Iriya Gate (3F) or Iriya Exit (1F).</li>'
      +'<li><b>Asakusa Exit, Yamashita Exit:</b> 1F. We did not find official directions from them. Check a map.</li>'
      +'<li><b>Shinobazu Gate:</b> the M2 floor. Ask staff where it comes out.</li>'
      +'<li><b>Keisei Ueno (Skyliner):</b> a separate station. Follow the signs, or ask staff.</li></ul>'
      +'<p class="sm">We did not find Tokyo Metro&rsquo;s exit numbers, so this guide uses the JR gates.</p>'+SRCL;
  }
  function parkHTML(){
    return '<p class="n2">Ueno Park is open <b>5:00 to 23:00</b>. No entry outside these hours.</p>'
      +'<ul class="pl"><li><b>From JR:</b> Park Gate or Panda Bridge Exit, 3F. About 2 min on foot.</li>'
      +'<li><b>From the Metro (Ginza, Hibiya):</b> about 4 min. From Keisei Ueno: about 1 min. From Ueno-okachimachi (Toei Oedo Line): about 5 min.</li>'
      +'<li><b>Cherry trees:</b> about 1,200. Blossoms for about two months, from the early kanzakura to the Somei-yoshino. Dates change every year: check the official forecasts nearer the time.</li>'
      +'<li><b>Shinobazu Pond:</b> the lotus is at its best in late July.</li>'
      +'<li><b>Rules:</b> no fireworks, no catch-ball, among others.</li></ul>'
      +'<p class="sm">Source: Ueno Park pages of the Tokyo Metropolitan Government, checked 23 November 2026.</p>';
  }
  function metroHTML(){
    return '<ul class="pl"><li><b>Lines:</b> Ginza Line G16, Hibiya Line H18. Transfers to JR East and Keisei.</li>'
      +'<li><b>From JR:</b> the &ldquo;for Tokyo Metro&rdquo; signs by the Central Gate (1F).</li>'
      +'<li><b>Exits:</b> we did not find Tokyo Metro&rsquo;s exit list. For Ueno Park, use the JR Park Gate or Panda Bridge (3F).</li>'
      +'<li><b>Tickets:</b> multi-functional ticket machines at all ticket offices, first train to last.</li>'
      +'<li><b>Lost something on the Metro?</b> Same day: ask the station office. From the next day: the Lost and Found at Iidabashi Station or the Tokyo Metro Customer Relations Center.</li>'
      +'<li><b>Station office:</b> 03-3832-6629.</li></ul>'
      +'<p class="sm">Source: Tokyo Metro Ueno Station page, checked 23 November 2026.</p>';
  }
  function ticketsHTML(){
    return '<ul class="pl"><li><b>Ticket Office and JR EAST Travel Service Center:</b> 1F, by the Central Gate ticket hall.</li>'
      +'<li><b>Passport Reader &amp; Reserved Seat Ticket Vending Machine:</b> 1F, by the Central Gate tickets.</li>'
      +'<li><b>Ticket and fare adjustment machines:</b> beside the Park Gate, 3F.</li>'
      +'<li><b>Skyliner tickets:</b> Keisei sells a Skyliner discount ticket between Narita Airport and Ueno, and a Skyliner and Tokyo Subway Ticket set.</li></ul>'
      +'<p class="sm">Source: JR East station map and Keisei, checked 23 November 2026. Rules and prices change. Check before you buy.</p>';
  }
  function bagsHTML(){
    return '<ul class="pl"><li><b>1F:</b> near the Main Exit (taxi side), and inside the gates by the Transfer to Shinkansen gate.</li>'
      +'<li><b>2F:</b> along the concourse to the Iriya Exit.</li>'
      +'<li><b>3F:</b> by the Panda Bridge Exit and near the Iriya Gate.</li>'
      +'<li>We did not find locker sizes or prices.</li>'
      +'<li>Write down your hotel name, address and phone number. Keep medicines, valuables and chargers with you.</li></ul>'+SRCL;
  }
  function simHTML(){
    return '<ul class="pl"><li><b>eSIM:</b> install it on your phone and switch it on when you need it. No counter, no queue.</li>'
      +'<li>We did not find official free Wi-Fi or SIM counters on the Ueno station pages we read.</li></ul>';
  }
  var NEXT=[['🚆','Trains and platforms',trainHTML],['🚪','Which exit?',exitHTML],['🌸','Ueno Park',parkHTML],['🚇','Tokyo Metro',metroHTML],['🎫','Tickets',ticketsHTML],['🧳','Lockers',bagsHTML],['📱','Phone data',simHTML]];
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
  var ARR=[['Find your level','3F: Park Gate and Panda Bridge, for Ueno Park. 1F: Central Gate, Main Exit and the taxi stop. M2: Shinobazu Gate.'],
    ['Came on the Skyliner?','You arrive at Keisei Ueno, a separate station from JR Ueno. Follow the signs, or ask staff.'],
    ['Changing to the Metro','Ginza Line G16, Hibiya Line H18. Follow the “for Tokyo Metro” signs by the Central Gate (1F).'],
    ['Need help or a locker','Question & Answer counter beside the Central Gate (1F). Coin lockers on 1F, 2F and 3F.']];
  var DEP=[['Flying from Narita?','Go to Keisei Ueno for the Skyliner. Not JR’s Narita Line (tracks 10 to 12): it goes to Narita city.'],
    ['Skyliner & Tokyo Subway Ticket or Greater Tokyo Pass?','Board at Ueno. Keisei says you cannot transfer at Nippori with these.'],
    ['Bullet train?','Shinkansen tracks 19 to 22, underground. Transfer to Shinkansen gate (1F), or lifts G and H.'],
    ['Bags','Lockers are on 1F, 2F and 3F. Remember which floor you used.'],
    ['Go to your platform','Check the display for your train, and your ticket for your car and seat.']];
  function renderDep(){ renderSteps($('depSteps'),DEP,doneD); }
  renderSteps($('arrSteps'),ARR,doneA); renderDep();
  $('arrReset').addEventListener('click',function(){ doneA.length=0; renderSteps($('arrSteps'),ARR,doneA); syncReset(); });
  $('depReset').addEventListener('click',function(){ doneD.length=0; renderDep(); syncReset(); });
  /* departure: before you go */
  var GUIDE='__GUIDE_URL__';
  function more(a){ return '<p class="sm"><a href="'+GUIDE+a+'">More in the full guide</a> (needs internet)</p>'; }
  function skyHTML(){
    return '<p class="n2">For <b>Narita Airport</b>, take the <b>Keisei Skyliner</b> from <b>Keisei Ueno</b>, Keisei&rsquo;s own station, separate from JR Ueno.</p>'
      +'<ul class="pl"><li>Keisei gives <b>41 min</b> from Narita Airport Terminal 2&middot;3 to Keisei Ueno.</li>'
      +'<li>With the Skyliner &amp; Tokyo Subway Ticket or the Greater Tokyo Pass you cannot transfer at Nippori, so use Ueno (Keisei).</li>'
      +'<li>Changing to JR at Nippori needs a JR ticket (Keisei).</li>'
      +'<li>We did not find the first and last Skyliner. Check Keisei&rsquo;s timetable.</li></ul>'
      +'<p class="sm">Source: Keisei Skyliner pages, checked 23 November 2026. Times and fares change.</p>'
      +more('#narita');
  }
  function nlineHTML(){
    return '<div class="tipbox"><b>JR&rsquo;s &ldquo;Narita Line&rdquo; is not the airport train.</b> JR East lists it on tracks 10 to 12 for Matsudo, Toride, Mito and Narita: that is Narita city.</div>'
      +'<p class="n2">For Narita Airport, use the Keisei Skyliner from Keisei Ueno.</p>'
      +'<p class="sm">Source: JR East Ueno Station map, checked 23 November 2026.</p>';
  }
  function shinHTML(){
    return '<ul class="pl"><li><b>Tracks 19 and 20:</b> Tohoku, Yamagata, Akita, Hokkaido, Joetsu and Hokuriku Shinkansen.</li>'
      +'<li><b>Tracks 21 and 22:</b> Shinkansen for Tokyo.</li>'
      +'<li>Underground (B4 to B1). Go through the Transfer to Shinkansen gate (1F), or take lifts G and H.</li>'
      +'<li>The Shinkansen concourse has a waiting room.</li></ul>'+SRCL;
  }
  function allowHTML(){
    return '<p class="n2">Ueno has gates and platforms on several floors, and Keisei Ueno is a separate station. Add a buffer for walking, gates and luggage.</p>'
      +'<ul class="pl"><li>Ueno Park side: 3F. Central Gate and taxi: 1F. Tracks 1 to 12: 2F. Tracks 13 to 17: 1F. Shinkansen: underground.</li>'
      +'<li>Lifts A to I. Ask station staff for the step-free route.</li>'
      +'<li>We did not find official walking times between gates and platforms, so we give none.</li></ul>'
      +'<p class="sm">Times are approximate and change. Check the operator.</p>';
  }
  var BEFORE=[['✈️','Skyliner to Narita',skyHTML],['⚠️','Not JR\u2019s Narita Line',nlineHTML],['🚄','Shinkansen',shinHTML],['⏱️','Allow time',allowHTML]];
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
  [].forEach.call(dseg.children,function(b){ b.addEventListener('click',function(){ var w=b.getAttribute('data-d'); try{localStorage.setItem('uenDepSeg',w);}catch(e){} paintDep(w); }); });
  var dsv='before'; try{ var q=localStorage.getItem('uenDepSeg'); if(q==='air'||q==='before') dsv=q; }catch(e){}
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
    navigator.serviceWorker.register('/ueno-sw.js',{scope:'/ueno-pocket',updateViaCache:'none'})
      .then(function(){ return navigator.serviceWorker.ready; })
      .then(function(){ return caches.has('ueno-pocket-v1'); })
      .then(function(ok){ saved=!!ok; if(!saved){ setTimeout(function(){ caches.has('ueno-pocket-v1').then(function(k){ saved=!!k; paint(); }); },2500);} paint(); })
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
  function needed(){ return mobile&&!standalone&&flag('uenInstalled')!=='1'; }
  function refresh(){
    var n=needed(); strip.hidden=!n;
    $('instHow').hidden=!n; $('instDesk').hidden=mobile;
    if(standalone||flag('uenInstalled')==='1'){ $('install').hidden=true; }
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
  function markInstalled(){ flag('uenInstalled','1'); refresh(); }
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
    ['go','🏙️','Ueno Station?','これは上野駅に行きますか？','Kore wa Ueno-eki ni ikimasu ka?','Does this go to Ueno Station?'],
    ['go','🛍️','Shibuya?','これは渋谷に行きますか？','Kore wa Shibuya ni ikimasu ka?','Does this go to Shibuya?'],
    ['go','✈️','Haneda Airport?','これは羽田空港に行きますか？','Kore wa Haneda-kuukou ni ikimasu ka?','Does this go to Haneda Airport?'],
    ['go','🛫','Narita Airport?','これは成田空港に行きますか？','Kore wa Narita-kuukou ni ikimasu ka?','Does this go to Narita Airport?'],
    ['go','🚉','Tokyo Station?','これは東京駅に行きますか？','Kore wa Toukyou-eki ni ikimasu ka?','Does this go to Tokyo Station?'],
    ['go','📞','Call a taxi','タクシーを呼んでください。','Takushii o yonde kudasai.','Please call a taxi.'],
    ['go','📍','Take me here','この住所までお願いします。','Kono juusho made onegai shimasu.','Please take me to this address. Show the address on your phone.'],
    ['go','🛑','Stop here','ここで止めてください。','Koko de tomete kudasai.','Please stop here.'],
    ['air','🎫','Ticket gate','改札はどこですか？','Kaisatsu wa doko desu ka?','Where is the ticket gate?'],
    ['air','🚆','Skyliner','スカイライナーの乗り場はどこですか？','Sukairainaa no noriba wa doko desu ka?','Where do I board the Skyliner?'],
    ['air','🚉','Keisei Ueno','京成上野駅はどこですか？','Keisei Ueno-eki wa doko desu ka?','Where is Keisei Ueno Station?'],
    ['air','🌸','Ueno Park','上野公園はどこですか？','Ueno-kouen wa doko desu ka?','Where is Ueno Park?'],
    ['air','🚄','Shinkansen','新幹線の乗り場はどこですか？','Shinkansen no noriba wa doko desu ka?','Where do I board the Shinkansen?'],
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
  var askCat='basics'; try{ var sc=localStorage.getItem('uenAskCat'); if(sc&&ASKC.some(function(c){return c[0]===sc;})) askCat=sc; }catch(e){}
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
    b.addEventListener('click',function(){ askCat=c[0]; try{localStorage.setItem('uenAskCat',c[0]);}catch(e){} paintAsk(); });
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
    $('shareBtn').addEventListener('click',function(){ try{ navigator.share({title:'Ueno Station Pocket Guide',url:location.origin+location.pathname+'?src=share'}); }catch(e){} });
  }
  window.addEventListener('beforeinstallprompt',function(e){ e.preventDefault(); dp=e; });
  window.addEventListener('appinstalled',function(){ pgTrack('pg_installed',{via:'browser'}); markInstalled(); if(!inst.hidden) closeSheet(); });
  /*__PG_HOOKS__*/
  refresh();
  if(needed()&&!flag('uenIntro')&&AUTO_INSTALL_SHEET){ flag('uenIntro','1'); setTimeout(function(){ if(sheet.hidden&&inst.hidden){ instVia='auto'; openInst(); } },700); }
})();
</script>
</body>
</html>
"""
POCKET_HTML = (POCKET_HTML.replace("__CSS__", POCKET_CSS).replace("__FINDER_JSON__", json.dumps(FINDER_DATA, ensure_ascii=False)).replace("__KLP_JSON__", json.dumps({k: v for k, v in KLK.items() if v}))
               .replace("__PG_BOOT__", PG_BOOT).replace("/*__PG_HOOKS__*/", PG_HOOKS).replace("__SVG__", POCKET_SVG).replace("__GUIDE_URL__", URL))
if re.search(r"\b(India|Indian|INR|Rs\.?|rupee|lakh|Aadhaar|UPI|VFS|BLS)\b|₹", re.sub(r"<script[^>]*>.*?</script>", "", POCKET_HTML, flags=re.S)):
    die("neutral-rule violation in the pocket guide")
for _bad in ("shinjuku-pocket", "sjkTerm", "sjkInstalled", "Busta", "Odaky", "Kabukich", "19:39",
             "New South", "Free Passage", "Romancecar", "Shinjuku Station Pocket", "West side", "Chūō"):
    if _bad in POCKET_HTML or _bad in page:
        die("leftover Shinjuku text in the Ueno pages: %r" % _bad)

POCKET_SW = """/* Ueno Station Pocket Guide service worker. Bump V when the page changes shape. */
var V='ueno-pocket-v1';
var PAGE='/ueno-pocket';
var SHELL=[PAGE,'/ueno-pocket.webmanifest','/favicon-32.png','/images/ueno-icon-192.png','/images/ueno-icon-512.png','/images/ueno-icon-maskable-512.png'];
self.addEventListener('install',function(e){
  e.waitUntil(caches.open(V).then(function(c){return c.addAll(SHELL);}).then(function(){return self.skipWaiting();}));
});
self.addEventListener('activate',function(e){
  e.waitUntil(caches.keys().then(function(ks){
    return Promise.all(ks.filter(function(k){return k.indexOf('ueno-pocket-')===0&&k!==V;}).map(function(k){return caches.delete(k);}));
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
    "name": "Ueno Station Pocket Guide",
    "short_name": "Ueno",
    "description": "A simple Ueno Station helper that works offline.",
    "start_url": POCKET_PATH,
    "scope": POCKET_PATH,
    "display": "standalone",
    "background_color": THEME,
    "theme_color": "#1a1a3e",
    "lang": "en",
    "icons": [
        {"src": "/images/ueno-icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
        {"src": "/images/ueno-icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
        {"src": "/images/ueno-icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ],
}, indent=2) + "\n"
PUB = os.path.join(ROOT, "public")
for _ic in ("ueno-icon-192.png", "ueno-icon-512.png", "ueno-icon-maskable-512.png", "ueno-apple-touch-180.png"):
    if not os.path.isfile(os.path.join(PUB, "images", _ic)):
        die("pocket guide icon missing: public/images/" + _ic + " (the service worker would fail to install without it)")

# ---- anchors for the Japan guide link and the sitemap: check everything before writing anything
MARK = "ueno-station-guide link"
jp = open(TEMPLATE, encoding="utf-8").read()
jp_new = jp
if MARK not in jp:
    anchor = re.search(r'(<!-- shinjuku-' + r'station-guide link -->\s*<p>.*?</p>)', jp, re.S)
    if not anchor:
        die("anchor for the Japan guide link (Shinjuku Station sentence) not found: run the Shinjuku Station generator (w58) first")
    add = ('\n\n<!-- %s -->\n<p>Arriving on the Skyliner, or here for the cherry blossoms? Our <a href="/blog/%s">Ueno Station guide</a> explains which gate to use for Ueno Park, '
           'the JR platforms by floor, why JR&rsquo;s Narita Line is not the airport train, the Tokyo Metro and the lockers.</p>') % (MARK, SLUG)
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
for _k, _want in (("hero", HERO_URL), ("sakura", SAKURA_URL)):
    if not _want:
        continue
    _u, _note = prepare_img(*IMAGES[_k], write=True)
    if _u != _want:
        die("%s image could not be prepared as planned (%r)" % (_k, _u))
    if _note:
        changed.append(_note)
old = open(OUT, encoding="utf-8").read() if os.path.isfile(OUT) else None
if old != page:
    open(OUT, "w", encoding="utf-8").write(page)
    changed.append("ueno-station-guide.html (%s bytes)" % len(page.encode("utf-8")))
for _name, _content in (("ueno-pocket.html", POCKET_HTML), ("ueno-sw.js", POCKET_SW), ("ueno-pocket.webmanifest", POCKET_MANIFEST)):
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
