#!/usr/bin/env python3
"""
w31: new page /blog/haneda-airport-guide + offline /haneda-pocket (neutral, plain-English airport guide, pilot page #2).
Built from the Narita generator (w25) pattern.

Run from the repo root:  python3 tools/w31_haneda_airport_page.py

What it does (idempotent):
  1. Builds public/blog/haneda-airport-guide.html from the site template taken from
     public/blog/japan-travel-packing-guide.html (head, CSS, nav, footer, tracking scripts)
     plus new body content, the Airalo eSIM block and the Welcome Pickups block
     (copied from the Japan guide, placement ids renamed to *-haneda).
  2. Builds public/haneda-pocket.html (offline pocket guide), haneda-sw.js and haneda-pocket.webmanifest.
  3. Adds one sentence linking to the new page in the Japan guide (marker: haneda-airport-guide link).
  4. Adds the page to public/sitemap.xml and bumps the Japan guide's lastmod.
It does NOT touch public/blog.html (no photo for the index card yet).
Aborts without writing anything if an expected anchor is missing.
"""
import os, re, sys, json, html
from urllib.parse import quote

ROOT = os.getcwd()
BLOG = os.path.join(ROOT, "public", "blog")
SITEMAP = os.path.join(ROOT, "public", "sitemap.xml")
TEMPLATE = os.path.join(BLOG, "japan-travel-packing-guide.html")
OUT = os.path.join(BLOG, "haneda-airport-guide.html")
SITE = "https://www.packsmartapp.com"
SLUG = "haneda-airport-guide"
URL = "%s/blog/%s" % (SITE, SLUG)
TODAY = "2026-11-18"

TITLE = "Haneda Airport Guide 2026: Terminals, Arrival, SIM & Transport | PackSmart"
H1 = "Haneda Airport Guide 2026: Terminals, Arrival Steps, SIM and Getting to Tokyo"
DESC = ("Plain-English Haneda Airport (HND) guide: which terminal, steps after landing, SIM and eSIM, "
        "trains, monorail and buses to Tokyo, plus prayer rooms, nursing rooms and help for older travellers.")
KEYWORDS = ("Haneda airport guide, Haneda airport terminals, Haneda airport arrival, Haneda to Tokyo, "
            "Haneda airport SIM card, Haneda airport eSIM, Haneda airport prayer room, Haneda airport facilities")


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


pickups = block("pickups-japan").replace("pickups-japan", "pickups-haneda")
airalo = block("airalo-japan").replace("airalo-japan", "airalo-haneda")

# DiscoverCars block for Haneda (adapted from the Japan guide block; Haneda is the default pick-up place there, no India framing)
cars = block("discovercars-japan-guide").replace("discovercars-japan-guide", "discovercars-haneda")
cars = cars.replace('<div data-ps-placement="discovercars-haneda"', '<div id="rent-a-car" data-ps-placement="discovercars-haneda"', 1)
_h = "Rent a Car in Japan: Go Where Trains and Buses Don't"
if _h not in cars:
    die("cars heading not found")
cars = cars.replace(_h, "Rent a Car at Haneda: Go Where Trains and Buses Don't")
_l = "Japan drives on the left, as in the UK, Australia and India."
if _l not in cars:
    die("cars left-hand line not found")
cars = cars.replace(_l, "Japan drives on the left.")
_on = 'class="ps-dc-chip on" data-country="japan" data-city="tokyo" data-place="hnd" aria-pressed="true"'
if _on not in cars:
    die("cars: Haneda chip is not the default any more")
if cars.count("&city=tokyo&place=hnd&locale=en") < 1:
    die("cars initial widget place not found")
if "India" in cars:
    die("India framing left in the Haneda car block")

# Haneda-specific fare line for the transfer block
old_fare = re.search(r'(<p data-ps-anchor="pickups"[^>]*>)Typical fares, airport to city centre:[^<]*(</p>)', pickups)
if not old_fare:
    die("pickups fare line not found")
pickups = pickups.replace(
    old_fare.group(0),
    old_fare.group(1)
    + "Typical fares, airport to city centre: Tokyo Haneda about €45 · Narita about €139. Per car, not per person."
    + old_fare.group(2),
)
_PK_H = "Your Driver at Haneda: Comfort After a Long Flight, to Your Hotel"
_k = pickups.find("</style>")
if _k < 0:
    die("pickups style close not found")
_k += len("</style>")
pickups = pickups[:_k] + '\n    <h3 style="margin:0 0 16px 0;color:#0f0f23;font-size:1.3rem;line-height:1.3;">' + _PK_H + '</h3>' + pickups[_k:]

airalo = airalo.replace("Install it before you fly, switch it on when you land. No airport SIM queue.",
                        "Install it before you fly, switch it on when you land at Haneda. No counter queue.")

# ---------------------------------------------------------------- body content
def esc(s):
    return html.escape(s, quote=False)


FAQ = [
    ("Is Haneda Airport in Tokyo?",
     "Yes. Haneda is in Ota Ward, in the south of Tokyo, much closer to the centre than Narita. Haneda's own website gives about 15 minutes by train to Shinagawa, "
     "20 to Hamamatsucho, 30 to Yokohama and 40 to Asakusa."),
    ("Which terminal will my flight use?",
     "Most international flights use Terminal 3. Terminal 2 also has an international area that some airlines use. Terminals 1 and 2 are mainly for domestic flights "
     "(Terminal 1 mainly Japan Airlines, Terminal 2 mainly ANA). Check your ticket or airline app, because airlines can change terminals."),
    ("How do I get between the terminals?",
     "A free shuttle bus links all three. Boarding is on the 1st floor: Terminal 3 stop 0, Terminal 1 stop 8, Terminal 2 stop 9. Haneda says buses run every 4 minutes "
     "from 5 am to 8 pm and every 8 minutes until midnight. The underground walkway between Terminals 1 and 2 was out of service for construction when we checked."),
    ("Is there free Wi-Fi at Haneda?",
     "Yes. Look for the network named HANEDA-FREE-WIFI. It works for quick messages, but it is not meant for a full day of maps and apps."),
    ("Do I need Visit Japan Web?",
     "It is not required, because you can still use paper forms. But registering on the free Visit Japan Web site before you fly lets you show QR codes "
     "for immigration and customs, which can speed up your arrival."),
    ("How do I get from Haneda to central Tokyo?",
     "By Keikyu Line train (to Shinagawa, Yokohama and Asakusa), by Tokyo Monorail (to Hamamatsucho, then JR), by Airport Limousine bus, by taxi, "
     "or by a pre-booked private transfer. Fares and times change, so check the operator before you go."),
    ("Is there a prayer room at Haneda Airport?",
     "Yes, in Terminals 2 and 3. Haneda's service page lists two rooms on the 3rd floor of Terminal 3 (before security), and in Terminal 2's international area "
     "two on the 3rd floor (before security) and two on the 2nd floor (after security). There is none in Terminal 1. Opening hours are not listed, so ask at an information counter."),
    ("Where can I find a nursing room or a quiet space?",
     "Nursing rooms are marked on the floor maps of every terminal. Haneda also has small \"Calm down, cool down\" spaces for people who find crowds or noise very hard. "
     "Ask at an information counter for the nearest one."),
    ("What if I land late at night?",
     "Trains run from about 5 am until around midnight, so a very late arrival may miss the last one. Late-night buses and taxis run after that, "
     "and there are hotels inside the terminals. Check the last train for your route before you book."),
    ("Can I connect to a domestic flight at Haneda?",
     "Yes. Terminal 3 has a transfer area on the 2nd floor for passengers changing between international and domestic flights. Rules for bags and customs depend on "
     "your airline and tickets, so ask your airline before you fly."),
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
    "about": {"@type": "Airport", "name": "Tokyo International Airport (Haneda)", "iataCode": "HND", "url": "https://tokyo-haneda.com/en/"},
}
ld_crumbs = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE},
        {"@type": "ListItem", "position": 2, "name": "Travel Essentials", "item": SITE + "/travel-essentials"},
        {"@type": "ListItem", "position": 3, "name": "Haneda Airport Guide", "item": URL},
    ],
}


def ld(obj):
    return '<script type="application/ld+json">\n%s\n</script>' % json.dumps(obj, ensure_ascii=False)


TOC = [
    ("one-page", "Haneda on one page"),
    ("terminals", "Which terminal?"),
    ("arrival", "Your first hour after landing"),
    ("connected", "Getting online: SIM, eSIM and Wi-Fi"),
    ("ic-card", "A train card (Suica or PASMO)"),
    ("to-tokyo", "Getting to Tokyo"),
    ("rent-a-car", "Rent a car at Haneda"),
    ("luggage", "Sending your suitcase to your hotel"),
    ("finder", "Find it fast: prayer room, nursing room and more"),
    ("facilities", "Facilities by terminal"),
    ("help", "Help for older travellers and anyone who needs assistance"),
    ("leaving", "Leaving Haneda"),
    ("layover", "A short stop or a long layover"),
    ("haneda-or-narita", "Haneda or Narita?"),
    ("faq", "FAQ"),
    ("about-this-guide", "About this guide and change log"),
]
# ---- v71: "What do you need first?" tiles + a quick-jump bar that appears once you scroll
TOC_SHORT = {
    "one-page": "On one page", "terminals": "Terminals", "arrival": "First hour", "connected": "Get online",
    "ic-card": "Train card", "to-tokyo": "To Tokyo", "rent-a-car": "Rent a car", "luggage": "Suitcase", "finder": "Find it fast",
    "facilities": "Facilities", "help": "Help", "leaving": "Leaving", "layover": "Layover",
    "haneda-or-narita": "Haneda or Narita", "faq": "FAQ", "about-this-guide": "About",
}
TOC_TILES = [
    ("connected", "&#128246;", "Get online", "SIM, eSIM, Wi-Fi"),
    ("ic-card", "&#128646;", "Train card", "Suica or PASMO"),
    ("to-tokyo", "&#128652;", "Get to Tokyo", "Train, bus, taxi"),
    ("luggage", "&#129523;", "Send your suitcase", "To your hotel"),
    ("finder", "&#128332;", "Prayer and nursing rooms", "Find it fast"),
    ("help", "&#129309;", "Help and assistance", "For older travellers"),
    ("rent-a-car", "&#128663;", "Rent a car", "Beyond the city"),
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

_TRAIN_ICON = '<g transform="translate(102,{y})" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="1" width="16" height="18" rx="4"/><path d="M1 11h16"/><circle cx="5.5" cy="15" r="0.6" fill="{c}"/><circle cx="12.5" cy="15" r="0.6" fill="{c}"/><path d="M4 23l2-4M14 23l-2-4"/></g>'


def _dg_node(n, y):
    return ('<circle cx="44" cy="%d" r="22" fill="#00C9A7"/><text x="44" y="%d" font-size="25" font-weight="700" text-anchor="middle" fill="#0f0f23">%s</text>' % (y, y + 9, n)
            + '<text x="90" y="%d" font-size="26" font-weight="700" fill="#0f0f23">Terminal %s</text>' % (y + 8, n))


def _dg_line(y, text):
    return '<text x="90" y="%d" font-size="20" fill="#0f0f23">%s</text>' % (y, text)


def _dg_stn(y, text):
    return ('<rect x="90" y="%d" width="370" height="34" rx="17" fill="#E7FAF5"/>' % y
            + _TRAIN_ICON.format(y=y + 5, c="#0b6b59")
            + '<text x="130" y="%d" font-size="18" font-weight="700" fill="#0b6b59">%s</text>' % (y + 23, text))


def _dg_bus(y, text):
    return ('<rect x="90" y="%d" width="370" height="34" rx="17" fill="#FFF3E0" stroke="#F2C27B" stroke-width="1.5"/>' % y
            + '<text x="275" y="%d" font-size="18" font-weight="600" text-anchor="middle" fill="#6b4a12">%s</text>' % (y + 23, text))


_DG_SVG = (
    '<svg id="hndDiagram" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 690" role="img" aria-labelledby="hndT hndD" font-family="Arial, Helvetica, sans-serif">'
    '<title id="hndT">Haneda Airport at a glance</title>'
    '<desc id="hndD">Three terminals in a row, linked by a free shuttle bus. Terminal 3 is for most international flights and has its own Keikyu and Tokyo Monorail stations. '
    'Terminal 1, mainly Japan Airlines domestic flights, and Terminal 2, mainly ANA domestic flights with some international flights, share one Keikyu station and have separate Monorail stations. '
    'The free shuttle bus stops are on the first floor: Terminal 3 stop 0, Terminal 1 stop 8, Terminal 2 stop 9.</desc>'
    '<rect width="480" height="690" fill="#fff"/>'
    '<text x="240" y="38" font-size="26" font-weight="700" text-anchor="middle" fill="#0f0f23">Haneda Airport at a glance</text>'
    '<text x="240" y="64" font-size="17" text-anchor="middle" fill="#555">3 terminals, one free shuttle bus</text>'
    '<line x1="44" y1="124" x2="44" y2="524" stroke="#00C9A7" stroke-width="6" stroke-linecap="round"/>'
    + _dg_node(3, 124) + _dg_line(162, "Most international flights") + _dg_stn(180, "Own Keikyu and Monorail stations") + _dg_bus(232, "Free shuttle bus · stop 0")
    + _dg_node(1, 324) + _dg_line(362, "Domestic flights, mainly JAL") + _dg_stn(380, "Keikyu 1·2 and Monorail stations") + _dg_bus(432, "Free shuttle bus · stop 8")
    + _dg_node(2, 524) + _dg_line(562, "Domestic flights, mainly ANA") + _dg_line(588, "Some international flights too") + _dg_stn(606, "Keikyu 1·2 and Monorail stations")
    + '<text x="240" y="672" font-size="14" text-anchor="middle" fill="#777">Simplified, not to scale. packsmartapp.com</text></svg>'
)

DIAGRAM = '<figure class="ps-fig" id="at-a-glance">\n' + _DG_SVG + """
<button type="button" class="ps-btn2" id="hndDl">Download the diagram (PNG)</button>
</figure>
<script>
(function(){
  var b=document.getElementById('hndDl'); if(!b) return;
  b.addEventListener('click',function(){
    try{
      var svg=document.getElementById('hndDiagram');
      var xml=new XMLSerializer().serializeToString(svg);
      var img=new Image();
      img.onload=function(){
        var c=document.createElement('canvas'); c.width=960; c.height=1380;
        var x=c.getContext('2d'); x.fillStyle='#fff'; x.fillRect(0,0,c.width,c.height); x.drawImage(img,0,0,c.width,c.height);
        c.toBlob(function(bl){
          var a=document.createElement('a'); a.href=URL.createObjectURL(bl); a.download='haneda-airport-at-a-glance.png';
          document.body.appendChild(a); a.click(); document.body.removeChild(a);
        },'image/png');
      };
      img.src='data:image/svg+xml;charset=utf-8,'+encodeURIComponent(xml);
    }catch(e){ window.print(); }
  });
})();
</script>"""

_T_ALL = lambda s: {"T1": s, "T2": s, "T3": s}
FINDER_DATA = {
    "terms": [["T1", "Terminal 1"], ["T2", "Terminal 2"], ["T3", "Terminal 3"]],
    "items": [
        ["toilet", "Toilets", _T_ALL("Toilets, including accessible toilets, are marked on every terminal's floor map. Look for the toilet signs, or ask at an information counter.")],
        ["food", "Food, drink and water", {
            "T1": "Restaurants and shops: 3F and 4F. Convenience stores: Air LAWSON on B1F (5:30 am to 11 pm), Seven-Eleven on 3F (7 am to 9 pm) and in the 2F gate area (6 am to 8 pm). None is open all night. Haneda's website has a restaurant search.",
            "T2": "Restaurants and shops: 4F and above. Convenience stores: FamilyMart on B1F (5:30 am to 11 pm) and on 3F in the international area (from 5 am until the last domestic arrival), and Seven-Eleven in the 2F domestic gate area (7 am to 8 pm). None is open all night. Haneda's website has a restaurant search.",
            "T3": "Restaurants: about 20 on 4F, and food courts in the departure area on 3F, after security. Convenience stores: Air LAWSON on 1F and Seven-Eleven on 3F are both open 24 hours. Haneda's website has a restaurant search."}],
        ["prayer", "Prayer room", {
            "T1": "Terminal 1 has no prayer room. The nearest are in Terminal 2 and Terminal 3, a short ride on the free shuttle bus.",
            "T2": "Four rooms in the international area: two on 3F before security, and two on 2F after security. They have washing facilities. Opening hours are not listed, so ask at an information counter.",
            "T3": "Two rooms on 3F, before security (departure lobby). They have washing facilities. Opening hours are not listed, so ask at an information counter."}],
        ["baby", "Nursing room", {
            "T1": "Marked on the floor map on B1F, 1F and in the 2F gate area. Ask at an information counter for the exact spot.",
            "T2": "Marked on the floor map on 1F, 3F and 4F. Ask at an information counter for the exact spot.",
            "T3": "Marked on the floor map on 1F, 2F, 3F and 4F. Ask at an information counter for the exact spot."}],
        ["quiet", "Quiet space (Calm down, cool down)", {
            "T1": "In the 2F domestic gate area, after domestic security. These small spaces are mainly for people who find crowds or noise very hard, such as some people with developmental or intellectual disabilities.",
            "T2": "In the 2F domestic gate area, after domestic security. These small spaces are mainly for people who find crowds or noise very hard, such as some people with developmental or intellectual disabilities.",
            "T3": "Marked on the 3F floor map, in the departure area. These small spaces are mainly for people who find crowds or noise very hard. Ask at an information counter for the exact spot."}],
        ["info", "Information counter", {
            "T1": "Airport Service Center on 1F (6 am to 8 pm). More information counters are marked on the 2F floor map.",
            "T2": "Information counters are marked on B1F, 1F and 2F. A Tourist Information Center is on 2F, south terminal lobby (5:45 am to 11 pm).",
            "T3": "Tourist Information Center on 2F, arrival lobby: open 24 hours. It handles JR tickets, sightseeing tickets and hotel bookings. More information counters are marked on the other floors."}],
        ["help", "Wheelchair and help", _T_ALL("Go to an information counter. Wheelchair and stroller rental and special assistance are listed in Haneda's service guide, and your airline can arrange help for you if you ask when you book. Haneda general information: +81 3-5757-8111 (5 am to midnight). In an emergency, call 119.")],
        ["lockers", "Luggage lockers and storage", {
            "T1": "Coin lockers are marked on B1F, 1F and 2F. Baggage storage and cleaning: B1F (8 am to 7:30 pm). Delivery counters (Yamato, JAL and Sagawa): 1F.",
            "T2": "Coin lockers are marked on 1F, 2F and 3F. Baggage storage and cleaning: B1F. Bonded baggage storage, international side: 2F, open 24 hours. Delivery: Yamato on 1F, 2F (5:45 am to 11 pm) and 3F (6 am to 11 pm), Sagawa on 1F (7 am to 8 pm).",
            "T3": "Coin lockers are marked on 2F and 3F. Baggage storage and bonded baggage storage: 2F. Short-term baggage storage and bag wrapping: 3F. Delivery counters (Yamato and JAL): 2F and 3F."}],
        ["wifi", "Wi-Fi rental counter", {
            "T1": "None listed in Terminal 1. Use Terminal 2 or Terminal 3.",
            "T2": "2F, international arrival lobby: J WiFi & Mobile and Global WiFi (5:45 am to 11 pm). 3F: MOBILE CENTER (7 am to 10 pm).",
            "T3": "2F, arrival lobby: MOBILE CENTER, AnyFone and Global WiFi. 3F, departure lobby: XCOM Global, MOBILE CENTER and Global WiFi."}],
        ["shower", "Showers", {
            "T1": "None listed in Terminal 1.",
            "T2": "Shower rooms on 1F, domestic arrival lobby (5 am to 10 pm).",
            "T3": "Shower room on 2F, open 24 hours."}],
        ["smoking", "Smoking area", _T_ALL("Smoking rooms are marked on the floor maps of every terminal. Look for the signs, or ask at an information counter. Please smoke only in a marked smoking room.")],
        ["play", "Children's play area", {
            "T1": "Kid's Space: 2F departure lobby (before security) and two in the 2F gate area.",
            "T2": "Kid's Space: 2F domestic departure lobby, the 2F domestic gate area, and the 2F international departure area.",
            "T3": "Kids Space: two on 3F, after departure procedures."}],
        ["pharmacy", "Pharmacy and medicine", {
            "T1": "A pharmacy on 1F (9 am to 5:30 pm). Opening hours can change, so check the shop.",
            "T2": "Airport Drug on B1F (7:30 am to 8 pm). BOOKS & DRUGS on 2F in the international departure area (6:30 am to 12:15 am).",
            "T3": "A drugstore on 2F (Air Bic Camera) and several on 3F (Airport Drug, Books & Drugs, Matsumoto Kiyoshi). Hours are not shown on the map, so check the shop."}],
        ["charge", "Phone charging", _T_ALL("Power outlets and charging corners are marked on the terminal floor maps. Ask at an information counter for the nearest.")],
        ["money", "Money and ATMs", {
            "T1": "Currency exchange: Travelex on 1F (9 am to 7 pm). ATMs: B1F, 1F, 2F and 3F (Seven Bank, Japan Post Bank, Mizuho, MUFG and others). Exchange rates differ from shop to shop, so check the rate before you exchange.",
            "T2": "Currency exchange: SBJ Bank on 1F (9 am to 6 pm); in the international area, 3F (Japan Airport Terminal exchange, 6:30 am to 9:30 pm, and Travelex) and 2F (SBJ Bank, 7 am to 1:30 pm). ATMs: B1F, 1F and 2F. Exchange rates differ from shop to shop, so check the rate before you exchange.",
            "T3": "Currency exchange: 2F (Japan Airport Terminal exchange and Travelex) and 3F (Japan Airport Terminal exchange, Travelex and SBJ Bank). ATMs: 1F, 2F (Japan Post Bank, Seven Bank) and 3F. Exchange rates differ from shop to shop, so check the rate before you exchange."}],
        ["unwell", "Feeling unwell", {
            "T1": "Tokyo International Medical Office on 1F (9 am to noon, and 1 pm to 5 pm; reception closes 11:50 am and 4:50 pm). Outside those hours, ask at an information counter. In an emergency, call 119.",
            "T2": "Toho University Haneda Airport Clinic on 1F (9 am to 1 pm, and 2 pm to 10 pm; reception closes 12:30 pm and 9:30 pm). Outside those hours, ask at an information counter. In an emergency, call 119.",
            "T3": "Toho University Haneda Airport Terminal 3 Clinic on 1F (9 am to 11 pm, closed noon to 1 pm; reception closes 10:30 pm). Outside those hours, ask at an information counter. In an emergency, call 119."}],
    ],
}
_ORDER = ["money", "food", "toilet", "help", "lockers", "baby", "play", "wifi", "info", "unwell", "pharmacy", "charge", "prayer", "quiet", "shower", "smoking"]
assert sorted(_ORDER) == sorted(i[0] for i in FINDER_DATA["items"])
FINDER_DATA["items"].sort(key=lambda i: _ORDER.index(i[0]))

FINDER = """<section class="ps-finder" id="finder">
<h2>Find it fast</h2>
<p>Choose your terminal, then what you need. Large buttons, no typing.</p>
<p class="ps-step-h">1. Which terminal are you in?</p>
<div class="ps-chips" id="fdTerm"></div>
<p class="ps-step-h">2. What do you need?</p>
<div class="ps-chips" id="fdWhat"></div>
<div class="ps-result" id="fdResult" aria-live="polite">Choose a terminal and what you need, and the answer shows here.</div>
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
    if(!term||!what){ rEl.textContent=!term?'Now choose your terminal.':'Now choose what you need.'; return; }
    var tn=D.terms.filter(function(t){return t[0]===term;})[0][1];
    var it=D.items.filter(function(i){return i[0]===what;})[0];
    var txt=it[2][term];
    rEl.innerHTML='';
    var s=document.createElement('strong'); s.textContent=it[1]+' at '+tn; rEl.appendChild(s);
    rEl.appendChild(document.createElement('br'));
    rEl.appendChild(document.createTextNode(txt?txt:'The airport list does not show one here. Please ask at an information counter.'));
    var sm=document.createElement('small'); sm.textContent='From Haneda Airport floor maps and pages, checked 18 November 2026. Floors and hours can change. If you cannot find it, ask at an information counter.'; rEl.appendChild(sm);
  }
})();
</script>"""
FINDER = FINDER.replace("__FINDER_JSON__", json.dumps(FINDER_DATA, ensure_ascii=False))

CHOOSER = """<h3>Where are you staying?</h3>
<div class="ps-scroll">
<table class="checklist-table">
<thead><tr><th>You are going to</th><th>Easiest choice</th><th>Why</th></tr></thead>
<tbody>
<tr><td><strong>Shinagawa, Yokohama or Asakusa</strong></td><td>Keikyu Line</td><td>Direct trains from the Terminal 3 station.</td></tr>
<tr><td><strong>Tokyo Station, Ueno, Akihabara or other Yamanote Line stops</strong></td><td>Tokyo Monorail to Hamamatsucho, or Keikyu to Shinagawa, then JR</td><td>Both reach the Yamanote Line in 15 to 20 minutes.</td></tr>
<tr><td><strong>Shinjuku, Ikebukuro, a large hotel or Tokyo Disney Resort</strong></td><td>Airport Limousine Bus</td><td>No changing trains, and fewer station stairs with a suitcase.</td></tr>
<tr><td><strong>Tired, lots of luggage, or not sure</strong></td><td>Limousine bus, a taxi or a pre-booked private transfer</td><td>Least walking and the fewest decisions.</td></tr>
</tbody>
</table>
</div>
"""


IC_CARD = """<h2 id="ic-card">A train card (Suica or PASMO)</h2>
<p>A tap-on travel card saves you buying a ticket for every train, subway or bus ride, and it also pays in many shops and vending machines. Visitors usually buy a tourist version, called Welcome Suica. It has no deposit, it is valid for 28 days, and any money left on it cannot be refunded.</p>
<ul>
<li><strong>Where at Haneda:</strong> the JR East Travel Service Center and the dedicated Welcome Suica ticket machines at Haneda Airport Terminal 3 (Tokyo Monorail) Station. In principle only one card is sold per person. Sales points change, so check <a href="https://www.jreast.co.jp/en/multi/welcomesuica/purchase.html" target="_blank" rel="noopener noreferrer">JR East's Welcome Suica page</a> before you fly. The Tourist Information Center in the Terminal 3 arrival lobby (open 24 hours) handles JR tickets and can point you the right way.</li>
<li><strong>Which trains:</strong> IC cards such as Suica and PASMO are used on many Tokyo trains, subways and buses. Look for the card symbol on the ticket gate.</li>
<li><strong>iPhone users:</strong> an app version, Welcome Suica Mobile, lets you set up before you land (iPhone only, as of April 2026).</li>
<li><strong>Staying longer than 28 days?</strong> A regular Suica or PASMO may suit you better. Ask at a ticket counter.</li>
</ul>
<div class="warning-box">
    <strong>This changes often.</strong> Sales points and card types have changed several times in recent years. Check <a href="https://www.jreast.co.jp/multi/en/welcomeSUICA/welcomeSUICA.html" target="_blank" rel="noopener noreferrer">JR East's Welcome Suica page</a> before you travel.
</div>"""

LUGGAGE = """<h2 id="luggage">Sending your suitcase to your hotel</h2>
<p>If you do not want to carry heavy bags on a crowded train, you can post them ahead. Haneda's floor maps list delivery counters run by Yamato, JAL and Sagawa. Ask which counter is in your terminal.</p>
<ul>
<li><strong>Terminal 3.</strong> Delivery counters (Yamato and JAL) are on the 2nd floor, in the arrival area, and on the 3rd floor, in the departure area.</li>
<li><strong>Usually next day.</strong> JAL ABC says the earliest delivery from the airport is the next day. Some same-day services exist for limited areas, with cut-off times, so do not plan around same-day.</li>
<li><strong>Prices vary by size and company.</strong> JAL ABC lists ¥1,950 for a bag up to 120 cm (length, width and height added together) sent to Tokyo, Kanagawa, Chiba or Saitama. Ask for the price at the counter before you hand your bag over.</li>
<li><strong>Have these ready:</strong> your hotel name, address and phone number, written down.</li>
<li><strong>Keep with you:</strong> medicines, valuables, chargers and a change of clothes.</li>
</ul>
<p data-ps-placement="klook-haneda-luggage">Prefer to book it online? Klook lists a <a href="https://klook.tpo.lu/jmWXAbkc" target="_blank" rel="nofollow noopener sponsored">luggage delivery service between Tokyo hotels and the airport</a> (Haneda or Narita), a partner link. Check the listing for sizes, prices and cut-off times.</p>
<p class="ps-note">Sources: <a href="https://tokyo-haneda.com/site_resource/floor/pdf/floor__pdf_floor_map_t3_en.pdf" target="_blank" rel="noopener noreferrer">Haneda Terminal 3 floor map</a> (PDF) and <a href="https://www.jalabc.com/en/hands-freetravel/airport-baggage-delivery/from-the-airport.html" target="_blank" rel="noopener noreferrer">JAL ABC airport luggage delivery</a>, checked 18 November 2026. Cut-off times change, so confirm at the counter.</p>"""

HELP = """<h2 id="help">Help for older travellers and anyone who needs assistance</h2>
<p>You do not have to cope alone. Haneda is set up to help, and asking early is easier than struggling.</p>
<ul>
<li><strong>Information counters.</strong> Every terminal has them, and Haneda's floor maps show where. Staff can answer questions and solve problems.</li>
<li><strong>Phone help.</strong> Haneda's general information line is +81 3-5757-8111, open every day from 5 am to midnight.</li>
<li><strong>Special assistance.</strong> Haneda's service guide lists wheelchair and stroller rental and special-assistance services. To arrange help from the aircraft door to baggage claim or the station, contact your airline.</li>
<li><strong>Trains and buses.</strong> Tell station or bus staff if you need help. Haneda's website also lists accessibility information for trains and buses.</li>
<li><strong>Before you fly.</strong> Ask your airline to arrange assistance at the airport when you book.</li>
</ul>
<p class="ps-note">Sources: Haneda Airport's floor maps for <a href="https://tokyo-haneda.com/site_resource/floor/pdf/floor__pdf_floor_map_t1_en.pdf" target="_blank" rel="noopener noreferrer">Terminal 1</a>, <a href="https://tokyo-haneda.com/site_resource/floor/pdf/floor__pdf_floor_map_t2_en.pdf" target="_blank" rel="noopener noreferrer">Terminal 2</a> and <a href="https://tokyo-haneda.com/site_resource/floor/pdf/floor__pdf_floor_map_t3_en.pdf" target="_blank" rel="noopener noreferrer">Terminal 3</a> (PDF), and its <a href="https://tokyo-haneda.com/en/service/facilities/travel_center.html" target="_blank" rel="noopener noreferrer">Tourist Information Center page</a>. Checked 18 November 2026.</p>"""

LATE = """<h3>Landing late or leaving very early?</h3>
<p>Haneda has a hotel in each terminal, according to the airport's own service page: First Cabin Haneda Terminal 1 (a capsule hotel on the 1st-floor arrival lobby), Haneda Excel Hotel Tokyu in Terminal 2 (2nd-floor terminal lobby, north), and The Royal Park Hotel Tokyo Haneda in Terminal 3, with its entrance in the 3rd-floor departure lobby and short-stay transit rooms on the airside. Check each hotel's own page for check-in times and whether it has space.</p>"""

HND_NRT = """<h2 id="haneda-or-narita">Haneda or Narita?</h2>
<p>Many travellers cannot choose, because the airline decides. If you can choose, here is the short version.</p>
<div class="ps-scroll">
<table class="checklist-table">
<thead><tr><th></th><th>Haneda (HND)</th><th>Narita (NRT)</th></tr></thead>
<tbody>
<tr><td><strong>Where</strong></td><td>In Ota Ward, in the south of Tokyo</td><td>About 60 km east of Tokyo, in Chiba</td></tr>
<tr><td><strong>Getting into the city</strong></td><td>About 15 to 30 minutes by train to Shinagawa, Hamamatsucho or Tokyo Station</td><td>About an hour or more</td></tr>
<tr><td><strong>Flights</strong></td><td>Many international routes, plus Japan's main domestic network</td><td>Many international routes and low-cost airlines</td></tr>
<tr><td><strong>Good to know</strong></td><td>International flights mostly use Terminal 3. Trains stop around midnight, but late buses and taxis run</td><td>Three terminals; plan for the transfer. See our <a href="/blog/narita-airport-guide">Narita guide</a></td></tr>
</tbody>
</table>
</div>
<p><strong>Going between the two?</strong> Haneda's train page lists about 1 hour 45 minutes by train to Narita Airport Station. Keikyu and Keisei trains connect the airports, and a limousine bus takes roughly 85 minutes. Allow extra time for the transfer. Klook also sells a direct <a href="https://klook.tpo.lu/isKZCpio" target="_blank" rel="nofollow noopener sponsored">bus ticket between Haneda and Narita</a> (partner link).</p>"""

ABOUT = """<div class="ps-about" id="about-this-guide">
<h2>About this guide</h2>
<p>Written by PackSmart. Facility details were checked against Haneda Airport's own floor maps (2025 editions) and service pages on 18 November 2026. Transport times come from Haneda's website and the Tokyo tourism board, and fares are rounded from airline and operator pages. Spotted something out of date? <a href="/contact">Tell us</a> and we will fix it.</p>
<ul>
<li><strong>18 Nov 2026:</strong> first version, with the find-it tool, the diagram, the train card, luggage, assistance, late arrival and Haneda-or-Narita sections.</li>
</ul>
</div>"""

def _card(title, text, slug, tag):
    return ('        <div class="related-card">\n            <div class="related-card-body">\n                <h4>%s</h4>\n                <p>%s</p>\n'
            '                <a href="https://www.packsmartapp.com%s">Read More <span class="related-arrow">&rarr;</span></a>\n                <div class="related-tag">%s</div>\n            </div>\n        </div>\n') % (title, text, slug, tag)

RELATED = ('<div class="related-posts">\n    <h3>Related Guides</h3>\n    <div class="related-grid">\n'
    + _card("Narita Airport Guide 2026", "Terminals, arrival steps, SIM and getting to Tokyo from Narita.", "/blog/narita-airport-guide", "Airport Guide")
    + _card("Japan Travel and Packing Guide 2026", "What to pack, rail passes, etiquette and a budget breakdown for Tokyo, Kyoto and Osaka.", "/blog/japan-travel-packing-guide", "Destination Guide")
    + _card("Japan 7-Day Itinerary on a Budget", "A first week in Tokyo, Kyoto and Osaka, with costs.", "/blog/japan-7-day-itinerary-budget", "Itinerary")
    + '    </div>\n</div>')

# hero image (optional): save the photo as public/images/haneda-airport-hero.jpg (any of jpg/jpeg/png/webp), then run this script
def prepare_hero():
    imgdir = os.path.join(ROOT, "public", "images")
    src = None
    for ext in ("jpg", "jpeg", "png", "webp"):
        cand = os.path.join(imgdir, "haneda-airport-hero." + ext)
        if os.path.isfile(cand):
            src = cand
            break
    if not src:
        return None, None
    dst = os.path.join(imgdir, "haneda-airport-hero-1600.jpg")
    note = None
    if (not os.path.isfile(dst)) or os.path.getmtime(dst) < os.path.getmtime(src):
        import subprocess, shutil
        try:
            subprocess.run(["sips", "-Z", "1600", "-s", "format", "jpeg", "-s", "formatOptions", "72", src, "--out", dst],
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            note = "haneda-airport-hero-1600.jpg (optimised from your photo)"
        except Exception:
            if src.lower().endswith(".jpg"):
                return "/images/" + os.path.basename(src), "using the original photo (could not optimise it here)"
            return None, None
    return "/images/haneda-airport-hero-1600.jpg", note

HERO_URL, HERO_NOTE = prepare_hero()

CARD = """<div class="ps-card" id="one-page">
<h2>Haneda on one page</h2>
<ul>
<li><strong>Where:</strong> Haneda is in southern Tokyo, about 15 to 20 minutes by train from Shinagawa or Hamamatsucho.</li>
<li><strong>Terminals:</strong> there are 3. Most international flights use Terminal 3. A free shuttle bus links all three terminals.</li>
<li><strong>Before you fly:</strong> register on Visit Japan Web (free) and keep the QR codes on your phone.</li>
<li><strong>After landing:</strong> immigration, then baggage, then customs, then the arrival lobby on the 2nd floor.</li>
<li><strong>In the arrival lobby:</strong> the Tourist Information Center (open 24 hours), SIM and Wi-Fi counters, cash machines, and the gates for the Keikyu Line and Tokyo Monorail.</li>
<li><strong>Free Wi-Fi:</strong> connect to HANEDA-FREE-WIFI for quick messages.</li>
<li><strong>Need help?</strong> Every terminal has information counters, or call +81 3-5757-8111 (5 am to midnight).</li>
</ul>
<div class="ps-qr ps-qr-screen">__QR_SCREEN__<p><strong>Want it on your phone?</strong> Point your phone camera at this code. It opens the free Haneda Pocket Guide, which works without internet once opened.<span class="u">packsmartapp.com/haneda-pocket</span></p></div>
<div class="ps-qr ps-qr-print">__QR_PRINT__<p><strong>Free Haneda Pocket Guide.</strong> Point your phone camera at this code. Open it once with signal and it works without internet.<span class="u">packsmartapp.com/haneda-pocket</span></p></div>
<button type="button" class="ps-print-btn" onclick="window.print()">Print this card</button>
</div>"""
# QR codes are made once for each guide address (the Narita one has ?src=qr on screen, ?src=card on paper). For another airport ask Claude to make the two codes.
QR_SCREEN = '<svg shape-rendering="crispEdges" viewBox="0 0 41 41" class="segno"><title>QR code: open the Haneda Pocket Guide</title><path fill="#fff" d="M0 0h41v41h-41z"/><path class="qrline" stroke="#000" d="M4 4.5h7m3 0h1m2 0h1m2 0h6m1 0h1m2 0h7m-33 1h1m5 0h1m3 0h1m2 0h5m6 0h1m1 0h1m5 0h1m-33 1h1m1 0h3m1 0h1m1 0h4m1 0h1m2 0h3m1 0h2m2 0h1m1 0h1m1 0h3m1 0h1m-33 1h1m1 0h3m1 0h1m1 0h1m1 0h3m1 0h1m1 0h1m3 0h1m1 0h1m3 0h1m1 0h3m1 0h1m-33 1h1m1 0h3m1 0h1m1 0h2m1 0h3m1 0h1m2 0h1m2 0h1m1 0h1m2 0h1m1 0h3m1 0h1m-33 1h1m5 0h1m1 0h1m1 0h3m2 0h2m1 0h1m1 0h2m4 0h1m5 0h1m-33 1h7m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h7m-25 1h1m1 0h1m1 0h1m2 0h1m5 0h4m-25 1h1m1 0h5m3 0h1m1 0h4m1 0h1m2 0h1m1 0h1m3 0h5m-27 1h2m4 0h3m6 0h3m1 0h1m2 0h2m1 0h2m1 0h1m-31 1h2m1 0h2m1 0h4m3 0h2m1 0h1m5 0h1m3 0h1m1 0h2m-31 1h4m7 0h1m1 0h3m2 0h1m1 0h3m1 0h2m1 0h4m-32 1h2m2 0h1m1 0h4m1 0h1m6 0h1m4 0h1m1 0h1m1 0h3m1 0h1m-32 1h1m2 0h1m1 0h1m1 0h1m2 0h1m1 0h1m1 0h3m3 0h4m2 0h1m2 0h4m-30 1h1m2 0h6m2 0h1m3 0h2m5 0h2m1 0h1m1 0h2m-24 1h1m1 0h1m1 0h1m3 0h1m1 0h6m1 0h2m1 0h3m-31 1h1m5 0h1m2 0h2m3 0h1m2 0h1m1 0h2m1 0h4m1 0h2m3 0h1m-33 1h1m1 0h4m3 0h1m3 0h1m2 0h2m1 0h2m2 0h5m1 0h2m1 0h1m-33 1h1m2 0h5m1 0h1m2 0h2m1 0h3m2 0h3m3 0h3m1 0h2m-32 1h1m1 0h2m1 0h1m2 0h1m5 0h1m1 0h3m2 0h3m1 0h6m1 0h1m-32 1h1m1 0h2m1 0h4m1 0h2m3 0h1m5 0h1m2 0h1m1 0h3m1 0h2m-33 1h3m2 0h1m3 0h3m1 0h1m1 0h1m2 0h1m3 0h3m1 0h1m3 0h1m1 0h1m-33 1h1m4 0h2m1 0h6m1 0h2m1 0h1m5 0h2m1 0h1m1 0h3m-32 1h1m2 0h2m2 0h1m2 0h6m2 0h1m2 0h2m2 0h3m2 0h2m-32 1h1m2 0h4m1 0h2m1 0h1m3 0h1m1 0h2m3 0h1m1 0h5m-21 1h1m3 0h1m3 0h1m1 0h7m3 0h1m1 0h1m1 0h1m-33 1h7m2 0h4m2 0h2m1 0h1m1 0h2m1 0h2m1 0h1m1 0h1m1 0h2m-32 1h1m5 0h1m1 0h1m1 0h1m1 0h1m1 0h1m5 0h5m3 0h4m-32 1h1m1 0h3m1 0h1m1 0h1m3 0h1m1 0h2m2 0h2m2 0h1m1 0h6m-30 1h1m1 0h3m1 0h1m1 0h4m1 0h1m1 0h3m3 0h3m1 0h1m2 0h2m1 0h2m-33 1h1m1 0h3m1 0h1m1 0h1m2 0h1m1 0h2m2 0h1m5 0h5m1 0h2m-31 1h1m5 0h1m2 0h4m3 0h1m1 0h2m1 0h3m1 0h1m2 0h3m-31 1h7m1 0h3m3 0h1m2 0h1m4 0h4m1 0h1m1 0h1m1 0h1"/></svg>'
QR_PRINT = '<svg shape-rendering="crispEdges" viewBox="0 0 41 41" class="segno"><title>QR code: open the Haneda Pocket Guide</title><path fill="#fff" d="M0 0h41v41h-41z"/><path class="qrline" stroke="#000" d="M4 4.5h7m3 0h4m2 0h6m1 0h1m2 0h7m-33 1h1m5 0h1m2 0h1m3 0h5m6 0h1m1 0h1m5 0h1m-33 1h1m1 0h3m1 0h1m1 0h4m1 0h1m2 0h3m1 0h2m2 0h1m1 0h1m1 0h3m1 0h1m-33 1h1m1 0h3m1 0h1m1 0h5m1 0h1m1 0h1m5 0h1m3 0h1m1 0h3m1 0h1m-33 1h1m1 0h3m1 0h1m1 0h1m4 0h1m1 0h1m2 0h1m2 0h1m1 0h1m2 0h1m1 0h3m1 0h1m-33 1h1m5 0h1m1 0h1m6 0h2m1 0h1m2 0h1m4 0h1m5 0h1m-33 1h7m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h7m-25 1h1m2 0h1m3 0h1m5 0h4m-25 1h1m1 0h5m3 0h6m1 0h1m2 0h1m1 0h1m3 0h5m-31 1h1m2 0h2m2 0h2m2 0h1m7 0h3m1 0h1m2 0h2m1 0h2m1 0h1m-31 1h1m1 0h1m1 0h1m1 0h1m2 0h2m2 0h2m1 0h1m5 0h1m3 0h1m1 0h2m-32 1h1m1 0h2m1 0h1m1 0h1m4 0h1m1 0h3m2 0h1m1 0h3m1 0h2m1 0h4m-32 1h1m1 0h2m1 0h2m3 0h1m1 0h1m5 0h1m4 0h1m1 0h1m1 0h3m1 0h1m-32 1h1m6 0h10m4 0h3m2 0h1m2 0h4m-33 1h7m1 0h4m6 0h1m6 0h2m1 0h1m1 0h2m-32 1h3m4 0h1m1 0h1m4 0h1m1 0h1m1 0h1m1 0h4m1 0h2m1 0h3m-31 1h5m1 0h1m2 0h2m2 0h1m3 0h1m2 0h1m1 0h4m1 0h2m3 0h1m-25 1h3m1 0h1m1 0h1m1 0h2m1 0h2m2 0h5m1 0h2m1 0h1m-33 1h1m2 0h1m2 0h3m4 0h1m1 0h3m2 0h3m3 0h3m1 0h2m-32 1h1m3 0h2m1 0h1m1 0h1m1 0h2m3 0h3m2 0h3m1 0h6m1 0h1m-33 1h1m1 0h1m3 0h1m1 0h1m1 0h2m1 0h1m2 0h1m5 0h1m2 0h1m1 0h3m1 0h2m-33 1h1m2 0h2m3 0h1m1 0h1m1 0h4m2 0h3m2 0h2m1 0h1m3 0h1m1 0h1m-33 1h1m4 0h9m1 0h2m1 0h1m5 0h2m1 0h1m1 0h3m-32 1h1m2 0h1m4 0h1m1 0h1m1 0h2m1 0h1m2 0h2m1 0h2m2 0h3m2 0h3m-33 1h1m1 0h1m2 0h3m2 0h1m1 0h2m1 0h1m1 0h2m3 0h1m1 0h5m-21 1h2m1 0h1m1 0h1m2 0h1m1 0h7m3 0h1m1 0h1m1 0h1m-33 1h7m3 0h4m1 0h2m1 0h1m1 0h1m2 0h2m1 0h1m1 0h1m1 0h2m-32 1h1m5 0h1m1 0h1m2 0h2m7 0h5m3 0h4m-32 1h1m1 0h3m1 0h1m1 0h2m2 0h4m2 0h3m1 0h1m1 0h6m-30 1h1m1 0h3m1 0h1m1 0h1m1 0h1m3 0h4m1 0h3m1 0h1m1 0h1m2 0h2m1 0h2m-33 1h1m1 0h3m1 0h1m1 0h3m3 0h1m2 0h1m2 0h1m2 0h5m1 0h2m-31 1h1m5 0h1m3 0h3m1 0h1m1 0h1m1 0h1m2 0h3m1 0h1m2 0h3m-31 1h7m1 0h1m3 0h1m1 0h1m2 0h1m4 0h4m1 0h1m1 0h1m1 0h1"/></svg>'
CARD = CARD.replace("__QR_SCREEN__", QR_SCREEN).replace("__QR_PRINT__", QR_PRINT)

TERMINALS = """<h2 id="terminals">Which terminal?</h2>
<p>Haneda has three terminals. Check your ticket or airline app, because airlines can change terminals.</p>
<div class="ps-scroll">
<table class="checklist-table">
<thead><tr><th>Terminal</th><th>Who uses it</th><th>Train station</th></tr></thead>
<tbody>
<tr><td><strong>Terminal 3</strong></td><td>Most international flights.</td><td>Its own stations: Keikyu "Haneda Airport Terminal 3" and Tokyo Monorail "Terminal 3". The ticket gates are on the 2nd-floor arrival lobby.</td></tr>
<tr><td><strong>Terminal 1</strong></td><td>Domestic flights, mainly Japan Airlines (JAL).</td><td>Keikyu "Terminal 1·2" and Tokyo Monorail "Terminal 1", on the basement floor.</td></tr>
<tr><td><strong>Terminal 2</strong></td><td>Domestic flights, mainly ANA. It also has an international area used by some airlines.</td><td>Keikyu "Terminal 1·2" and Tokyo Monorail "Terminal 2", on the basement floor.</td></tr>
</tbody>
</table>
</div>
<div class="tip-box">
    <strong>Moving between terminals:</strong> a free shuttle bus links all three. Boarding is on the 1st floor: Terminal 3 stop 0, Terminal 1 stop 8, Terminal 2 stop 9. Haneda says buses run every 4 minutes from 5 am to 8 pm and every 8 minutes until midnight (first and last buses differ a little by route). The underground walkway between Terminals 1 and 2 was out of service for construction when we checked on 18 November 2026. See <a href="https://tokyo-haneda.com/en/access/travel_between_terminals" target="_blank" rel="noopener noreferrer">Haneda's page on travelling between terminals</a>.
</div>"""

ARRIVAL = """<h2 id="arrival">Your first hour after landing</h2>
<p>Most people follow the same steps. Signs are in Japanese and English, and staff are nearby if you are unsure. These are the steps Haneda lists for international arrivals (the same at Terminals 2 and 3).</p>
<ol>
<li><strong>Before you fly (optional but helpful).</strong> Register on the free <a href="https://www.vjw.digital.go.jp/" target="_blank" rel="noopener noreferrer">Visit Japan Web</a> site. You enter your immigration and customs details once and get QR codes. Take a screenshot of them in case your signal is weak.</li>
<li><strong>Quarantine.</strong> Haneda lists this as the first step. If your flight handed out a health form, fill it in. If you became unwell on the way, tell an officer.</li>
<li><strong>Immigration.</strong> Have your passport ready, and your arrival card if you filled one in. The automatic gates do not stamp your passport: ask the staff after the gate if you would like a stamp.</li>
<li><strong>Baggage claim.</strong> Find your flight on the screens and collect your bags. If a bag is missing or damaged, go to your airline staff with your baggage tag.</li>
<li><strong>Customs.</strong> Show your Visit Japan Web QR code, or a paper declaration form (many flights hand these out). If you carry meat, fruit, plants or animals, Haneda lists an animal and plant quarantine step before customs.</li>
</ol>
<p>Then you arrive in the <strong>arrival lobby on the 2nd floor</strong>. Here you find the Tourist Information Center (open 24 hours), SIM and pocket Wi-Fi counters, currency exchange, cash machines, and the gates for the Keikyu Line and Tokyo Monorail. Bus tickets are sold from ticket machines and a bus counter, and taxis leave from the 1st floor (stop 21).</p>
<div class="warning-box">
    <strong>Rules change.</strong> Immigration and customs procedures are updated often. If anything here differs from what the signs or officers tell you, follow the signs and officers.
</div>
<p class="ps-note">Sources: <a href="https://tokyo-haneda.com/en/flight/int/arr_step.html?tab=terminal3" target="_blank" rel="noopener noreferrer">Haneda Airport: international arrival procedures</a>, <a href="https://tokyo-haneda.com/en/service/facilities/travel_center.html" target="_blank" rel="noopener noreferrer">Tourist Information Center</a> and <a href="https://www.tokyo-haneda.com/en/access/taxi/index.html?tab=terminal3" target="_blank" rel="noopener noreferrer">taxi stands</a>. Checked 18 November 2026.</p>"""

CONNECTED = """<h2 id="connected">Getting online: SIM, eSIM and Wi-Fi</h2>
<p>You will want a connection soon after landing, for maps, messages and your hotel. Here are the usual choices.</p>
<div class="ps-scroll">
<table class="checklist-table">
<thead><tr><th>Option</th><th>How it works</th><th>Good to know</th></tr></thead>
<tbody>
<tr><td><strong>eSIM</strong></td><td>Install it on your phone before you fly. It works as soon as you land.</td><td>Needs an eSIM-ready, unlocked phone. No counter or queue.</td></tr>
<tr><td><strong>Tourist SIM card</strong></td><td>Buy a SIM from a vending machine or counter in the arrival area and swap it into your phone.</td><td>Keep your home SIM safe while you swap.</td></tr>
<tr><td><strong>Pocket Wi-Fi</strong></td><td>Pick up a small device that shares one connection with several phones.</td><td>You must return it. Many companies let you post it back in a prepaid envelope.</td></tr>
<tr><td><strong>Airport free Wi-Fi</strong></td><td>Connect to HANEDA-FREE-WIFI.</td><td>Fine for a quick "I have landed" message, not for a full day of maps and apps.</td></tr>
</tbody>
</table>
</div>
<p>Haneda's floor maps show Wi-Fi rental counters on the 2nd floor (arrival lobby) and 3rd floor (departure lobby) of Terminal 3, and on the 2nd and 3rd floors of Terminal 2. None is listed in Terminal 1. Counter hours and stock vary by company, so ordering ahead is safer.</p>"""


SAKURA_LINK = "https://p.sakuramobile.jp/idevaffiliate.php?id=728"
SAKURA_SIM_LINK = SAKURA_LINK  # TODO: swap for a link to Sakura's travel SIM page if the programme gives one (this one opens Sakura's home page)
SAKURA = """<div style="max-width:800px;margin:24px auto;padding:22px 24px;background:#f0faf7;border:1px solid #cdeee5;border-left:4px solid #00C9A7;border-radius:12px;">
  <style>.ps-sk-tile{transition:border-color .15s,box-shadow .15s}.ps-sk-tile:hover,.ps-sk-tile:focus-visible{border-color:#00C9A7!important;box-shadow:0 2px 10px rgba(0,201,167,.25)}.ps-sk-ghost{transition:background .15s}.ps-sk-tile:hover .ps-sk-ghost,.ps-sk-tile:focus-visible .ps-sk-ghost{background:#E7FAF5}</style>
  <strong style="display:block;font-size:1.1rem;color:#0f0f23;margin:0 0 6px 0;">No eSIM? Two other ways to get online</strong>
  <p style="margin:0 0 18px 0;font-size:0.9rem;color:#555;line-height:1.5;">An eSIM needs a compatible phone. If yours is not, or you would rather hold something real, choose a travel SIM card or a pocket Wi-Fi. Both are from Sakura Mobile.</p>
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:18px 12px;margin:14px 0 16px 0;">
  <a class="ps-sk-tile" data-ps-placement="sakura-haneda-sim" href="__SAKURA_SIM_LINK__" target="_blank" rel="sponsored nofollow noopener" style="position:relative;display:flex;flex-direction:column;background:#fff;border:1.5px solid #cdeee5;border-radius:12px;padding:22px 16px 16px;text-decoration:none;text-align:center;color:#0f0f23;"><span style="position:absolute;top:-10px;left:50%;transform:translateX(-50%);background:#00C9A7;color:#fff;font-size:0.68rem;font-weight:700;letter-spacing:.03em;padding:2px 10px;border-radius:999px;white-space:nowrap;">FOR ONE TRAVELLER</span><span style="display:block;max-width:340px;width:100%;margin:0 auto 12px;"><picture><source type="image/webp" srcset="/images/sakura-sim-banner.webp"><img src="/images/sakura-sim-banner.png" width="380" height="364" loading="lazy" alt="Sakura Mobile Japan travel SIM card" style="display:block;width:100%;height:auto;border-radius:12px;"></picture></span><span style="display:block;font-size:1.5rem;font-weight:700;line-height:1.15;">Travel SIM card</span><span style="display:block;font-size:0.85rem;color:#666;line-height:1.35;margin:4px 0 10px;">Data only, no phone number</span><span style="display:block;font-size:1.05rem;font-weight:700;color:#0a8f78;">From &yen;3,500 before tax</span><span style="display:block;font-size:0.78rem;color:#777;line-height:1.3;margin:6px 0 10px;">3 GB a day on docomo, or unlimited on au</span><span style="flex:1;min-height:2px;display:block;"></span><span class="ps-sk-ghost" style="display:block;box-sizing:border-box;border:1.5px solid #00C9A7;color:#0a8f78;font-weight:700;font-size:1rem;border-radius:12px;padding:10px 14px;margin-top:6px;">Get a travel SIM &rarr;</span><span style="display:block;font-size:0.76rem;color:#777;margin-top:6px;">Sakura Mobile &middot; partner link</span></a>
  <a class="ps-sk-tile" data-ps-placement="sakura-haneda-wifi" href="__SAKURA_LINK__" target="_blank" rel="sponsored nofollow noopener" style="position:relative;display:flex;flex-direction:column;background:#fff;border:1.5px solid #cdeee5;border-radius:12px;padding:22px 16px 16px;text-decoration:none;text-align:center;color:#0f0f23;"><span style="position:absolute;top:-10px;left:50%;transform:translateX(-50%);background:#00C9A7;color:#fff;font-size:0.68rem;font-weight:700;letter-spacing:.03em;padding:2px 10px;border-radius:999px;white-space:nowrap;">FOR FAMILIES AND GROUPS</span><span style="display:block;max-width:340px;width:100%;margin:0 auto 12px;"><picture><source type="image/webp" srcset="/images/sakura-wifi-banner.webp"><img src="/images/sakura-wifi-banner.png" width="570" height="546" loading="lazy" alt="Sakura Mobile pocket Wi-Fi device" style="display:block;width:100%;height:auto;border-radius:12px;"></picture></span><span style="display:block;font-size:1.5rem;font-weight:700;line-height:1.15;">Pocket Wi-Fi</span><span style="display:block;font-size:0.85rem;color:#666;line-height:1.35;margin:4px 0 10px;">One device for every phone</span><span style="display:block;font-size:1.05rem;font-weight:700;color:#0a8f78;">The price depends on your dates</span><span style="display:block;font-size:0.78rem;color:#777;line-height:1.3;margin:6px 0 10px;">Docomo network, data described as unlimited</span><span style="flex:1;min-height:2px;display:block;"></span><span class="ps-sk-ghost" style="display:block;box-sizing:border-box;border:1.5px solid #00C9A7;color:#0a8f78;font-weight:700;font-size:1rem;border-radius:12px;padding:10px 14px;margin-top:6px;">Rent a pocket Wi-Fi &rarr;</span><span style="display:block;font-size:0.76rem;color:#777;margin-top:6px;">Sakura Mobile &middot; partner link</span></a>
  </div>
  <p style="margin:0 0 8px;font-size:0.82rem;color:#666;line-height:1.5;"><strong style="color:#0a8f78;">Pocket Wi-Fi pick-up:</strong> at the JAL ABC counter in Terminal 3, on the 2nd floor of the arrival lobby (Sakura lists it as closed from 1 am to 4 am), or ask for free delivery to your hotel. Return it in the prepaid envelope that comes with it: post it in any Japanese postbox before you leave, or hand it in at the same counter. A fair use policy may apply to unlimited data.</p>
  <p style="margin:0;font-size:0.82rem;color:#666;line-height:1.5;"><strong style="color:#0a8f78;">Travel SIM card pick-up:</strong> Sakura Mobile lists pick-up at Haneda in the Terminal 3 arrival lobby, the same JAL ABC counter. Show your booking on your phone. Order ahead: same-day orders are possible, but stock is limited.</p>
</div>""".replace("__SAKURA_SIM_LINK__", SAKURA_SIM_LINK).replace("__SAKURA_LINK__", SAKURA_LINK)

JB_LINK = "https://www.japan-bullettrain.com/?via=packsmart"
JB_SHIN = '<svg style="display:block;width:100%;height:auto;" aria-hidden="true" focusable="false" viewBox="0 0 320 170" xmlns="http://www.w3.org/2000/svg"><rect width="320" height="170" fill="#E8F1FE"/><circle cx="64" cy="40" r="20" fill="#FFE3CC"/><path d="M120 120 L188 44 L204 60 L214 52 L282 120Z" fill="#b9cdf0"/><path d="M174 62 L188 44 L204 60 L196 64 L188 58 L181 66Z" fill="#fff"/><path d="M0 124 L60 96 L110 120 L150 104 L200 124Z" fill="#d3e0f7"/><g fill="#f7b9cf"><circle cx="262" cy="104" r="14"/><circle cx="276" cy="112" r="12"/><circle cx="250" cy="114" r="11"/></g><rect x="260" y="112" width="4" height="22" fill="#8b5a3c"/><rect y="132" width="320" height="38" fill="#d3e0f7"/><rect y="146" width="320" height="4" fill="#9db8e6"/><g><path d="M14 138 L14 110 C14 104 20 100 28 100 L214 100 C250 100 286 118 306 138 Z" fill="#fff" stroke="#0f0f23" stroke-width="2.5"/><path d="M14 124 L300 124 L304 130 L14 130Z" fill="#2563EB"/><g fill="#7fb4f5" stroke="#0f0f23" stroke-width="1.5"><rect x="34" y="106" width="20" height="11" rx="2"/><rect x="62" y="106" width="20" height="11" rx="2"/><rect x="90" y="106" width="20" height="11" rx="2"/><rect x="118" y="106" width="20" height="11" rx="2"/><rect x="146" y="106" width="20" height="11" rx="2"/><rect x="174" y="106" width="20" height="11" rx="2"/></g><path d="M214 101 C238 102 262 112 282 124 L214 124Z" fill="#0f0f23" opacity=".9"/><g fill="#0f0f23"><circle cx="60" cy="140" r="5"/><circle cx="104" cy="140" r="5"/><circle cx="200" cy="140" r="5"/><circle cx="244" cy="140" r="5"/></g></g><g stroke="#2563EB" stroke-width="3" stroke-linecap="round"><path d="M4 108h22"/><path d="M0 118h16"/><path d="M6 128h12"/></g></svg>'
JB_TRAIN = '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M5 16V8a5 5 0 0 1 5-5h4a5 5 0 0 1 5 5v8a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2z"/><path d="M5 11h14M9 15h.01M15 15h.01M8 18l-2 3M16 18l2 3"/></svg>'


def jb_node(text):
    return '<div class="jb-rn"><span class="jb-dot"></span><strong style="color:#0f0f23;font-size:1rem;">%s</strong></div>' % text


def jb_leg(text, icon="", blue=False):
    return '<div class="jb-lg%s"><span class="jb-ln"></span><span class="jb-lt">%s%s</span></div>' % (" jb-blue" if blue else "", icon, text)


JB_SHINKANSEN = (
    '<div data-ps-placement="jw-shinkansen-haneda" style="max-width:800px;margin:20px auto;padding:20px;background:#f0faf7;border:1px solid #cdeee5;border-left:4px solid #00C9A7;border-radius:12px;">'
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
    '<strong style="display:block;font-size:1.1rem;color:#0f0f23;margin:0 0 12px;">Going on to Kyoto or Osaka?</strong>'
    '<div class="jb-grid">'
    '<a href="' + JB_LINK + '" target="_blank" rel="nofollow noopener sponsored" tabindex="-1" aria-hidden="true" style="display:block;border-radius:12px;overflow:hidden;">' + JB_SHIN + '</a>'
    '<div>'
    + jb_node("Haneda Airport") + jb_leg("Keikyu Line, about 15 minutes") + jb_node("Shinagawa Station")
    + jb_leg("Shinkansen (bullet train)", JB_TRAIN, True) + jb_node("Kyoto") + jb_node("Osaka") +
    '</div></div>'
    '<div class="jb-row"><div class="jb-tx">'
    '<p style="margin:0 0 8px;font-size:0.95rem;line-height:1.5;color:#333;">Many Shinkansen to Kyoto and Osaka stop at Shinagawa Station, a short train ride from Haneda, so check the timetable and you may not need to go into Tokyo Station. If you want your tickets sorted before you fly, you can book them online. The company says its tickets cover the JR East, JR West, JR Central and JR Kyushu Shinkansen lines and are collected with a QR code.</p>'
    '</div><div class="jb-bt">'
    '<a class="ps-jb-btn" href="' + JB_LINK + '" target="_blank" rel="nofollow noopener sponsored" style="display:block;box-sizing:border-box;text-decoration:none;"><span class="ps-jb-ghost" style="display:block;border:1.5px solid #00C9A7;background:#fff;color:#0a8f78;text-align:center;font-weight:700;font-size:1rem;border-radius:12px;padding:11px 14px;min-height:46px;line-height:1.25;">Book Shinkansen tickets &rarr;</span><span style="display:block;text-align:center;font-size:0.76rem;color:#777;margin-top:6px;">Japan Bullet Train &middot; partner link</span></a>'
    '<p style="margin:10px 0 0;font-size:0.85rem;line-height:1.5;color:#555;">You can also buy at a station on the day, so check the price and the change and cancellation rules before you pay.</p>'
    '</div></div></div>'
)



# ---- Klook placements (links verified in Chrome 18 Nov 2026; aff_pid=711400) ----
KL_LIMO_LINK = "https://klook.tpo.lu/PwSUuJEu"
KL_CAR_LINK = "https://klook.tpo.lu/5y9oQYD7"
KL_BAGS_LINK = "https://klook.tpo.lu/jmWXAbkc"
KL_HNDNRT_LINK = "https://klook.tpo.lu/isKZCpio"
KL_BUS = '<svg aria-hidden="true" focusable="false" style="display:block;width:100%;height:auto;" viewBox="0 0 320 150" xmlns="http://www.w3.org/2000/svg"><rect width="320" height="150" fill="#FFF1E2"/><g fill="#fbd9b6"><rect x="14" y="40" width="40" height="74"/><rect x="60" y="62" width="28" height="52"/><rect x="236" y="34" width="44" height="80"/><rect x="284" y="64" width="26" height="50"/></g><g fill="#fff3e6"><rect x="22" y="50" width="8" height="8"/><rect x="38" y="50" width="8" height="8"/><rect x="22" y="66" width="8" height="8"/><rect x="38" y="66" width="8" height="8"/><rect x="246" y="46" width="8" height="8"/><rect x="262" y="46" width="8" height="8"/><rect x="246" y="62" width="8" height="8"/><rect x="262" y="62" width="8" height="8"/></g><rect y="116" width="320" height="34" fill="#efd3b3"/><rect y="132" width="320" height="3" fill="#fff" opacity=".6"/><g><rect x="52" y="64" width="216" height="56" rx="10" fill="#fff" stroke="#0f0f23" stroke-width="2.5"/><rect x="52" y="104" width="216" height="8" fill="#F97316"/><g fill="#9ad8e8" stroke="#0f0f23" stroke-width="1.5"><rect x="64" y="72" width="26" height="22" rx="3"/><rect x="96" y="72" width="26" height="22" rx="3"/><rect x="128" y="72" width="26" height="22" rx="3"/><rect x="160" y="72" width="26" height="22" rx="3"/><rect x="192" y="72" width="26" height="22" rx="3"/><rect x="228" y="72" width="30" height="30" rx="3"/></g><circle cx="94" cy="122" r="11" fill="#0f0f23"/><circle cx="94" cy="122" r="4" fill="#bbb"/><circle cx="226" cy="122" r="11" fill="#0f0f23"/><circle cx="226" cy="122" r="4" fill="#bbb"/></g></svg>'
KL_CAR = '<svg aria-hidden="true" focusable="false" style="display:block;width:100%;height:auto;" viewBox="0 0 320 150" xmlns="http://www.w3.org/2000/svg"><rect width="320" height="150" fill="#E7FAF5"/><g fill="#cdeee5"><rect x="18" y="52" width="30" height="62"/><rect x="54" y="68" width="24" height="46"/><rect x="240" y="44" width="34" height="70"/><rect x="280" y="66" width="28" height="48"/></g><rect y="116" width="320" height="34" fill="#d6f1ea"/><rect y="132" width="320" height="3" fill="#fff" opacity=".7"/><g><path d="M56 112 L56 98 C56 92 60 88 66 86 L108 70 C116 66 124 64 134 64 L190 64 C200 64 208 68 216 74 L246 88 C256 90 262 96 262 104 L262 112 Z" fill="#fff" stroke="#0f0f23" stroke-width="2.5" stroke-linejoin="round"/><path d="M116 72 L134 68 L160 68 L160 88 L104 88 Z" fill="#9ad8e8" stroke="#0f0f23" stroke-width="1.5" stroke-linejoin="round"/><path d="M168 68 L190 68 C196 68 202 71 208 76 L220 88 L168 88 Z" fill="#9ad8e8" stroke="#0f0f23" stroke-width="1.5" stroke-linejoin="round"/><rect x="56" y="100" width="206" height="6" fill="#00C9A7"/><circle cx="96" cy="114" r="12" fill="#0f0f23"/><circle cx="96" cy="114" r="4.5" fill="#bbb"/><circle cx="224" cy="114" r="12" fill="#0f0f23"/><circle cx="224" cy="114" r="4.5" fill="#bbb"/></g></svg>'
KL_LBL = "display:block;font-weight:700;color:#0a8f78;font-size:0.76rem;letter-spacing:.03em;text-transform:uppercase;"
KL_VAL = "display:block;font-size:0.92rem;line-height:1.35;color:#0f0f23;"
KL_ROWS = [
    ("limousine", "Airport Limousine Bus", "Shinjuku, Ikebukuro, Tokyo Disney Resort and other stops", "About 45 to 80 min", "About &yen;1,000 to &yen;1,300", "Board by scanning a QR code. Easy with heavy luggage.", KL_LIMO_LINK, "See Limousine Bus tickets", KL_BUS),
    ("car", "Private car transfer", "Your hotel in Tokyo, door to door", "Depends on the traffic", "From about US$54 per car", "A driver meets you at arrivals and helps with bags.", KL_CAR_LINK, "See private transfers", KL_CAR),
]


def kl_row(label, text):
    return '<div style="margin:0 0 7px;"><span style="%s">%s</span><span style="%s">%s</span></div>' % (KL_LBL, label, KL_VAL, text)


def kl_tile(r):
    pid, name, to, mins, price, note, link, btn, svg = r
    return (
        '<a class="ps-kl-tile" data-ps-placement="klook-haneda-transport-%s" href="%s" target="_blank" rel="nofollow noopener sponsored" style="display:flex;flex-direction:column;background:#fff;border:1.5px solid #cdeee5;border-radius:12px;padding:12px 12px 14px;text-decoration:none;color:#0f0f23;">' % (pid, link)
        + '<span style="display:block;margin:0 0 10px;border-radius:12px;overflow:hidden;">%s</span>' % svg
        + '<strong style="display:block;font-size:1.1rem;color:#0f0f23;margin:0 0 8px;">%s</strong>' % name
        + kl_row("Goes to", to) + kl_row("About how long", mins) + kl_row("About how much", price)
        + '<p style="margin:0 0 12px;font-size:0.88rem;color:#555;line-height:1.4;">%s</p><span style="flex:1;min-height:4px;display:block;"></span>' % note
        + '<span class="ps-kl-ghost" style="display:block;box-sizing:border-box;border:1.5px solid #00C9A7;color:#0a8f78;text-align:center;font-weight:700;font-size:0.98rem;border-radius:12px;padding:10px 12px;min-height:46px;line-height:1.25;display:flex;align-items:center;justify-content:center;">%s&nbsp;&rarr;</span><span style="display:block;text-align:center;font-size:0.76rem;color:#777;margin-top:6px;">Klook &middot; partner link</span></a>' % btn.replace(" ", "&nbsp;", btn.count(" ") - 1)
    )


KLOOK_TRANSPORT = (
    '<div data-ps-placement="klook-haneda-transport" style="max-width:800px;margin:20px auto;padding:20px;background:#f0faf7;border:1px solid #cdeee5;border-left:4px solid #00C9A7;border-radius:12px;">'
    '<style>.ps-kl-tile{transition:border-color .15s,box-shadow .15s}.ps-kl-tile:hover,.ps-kl-tile:focus-visible{border-color:#00C9A7!important;box-shadow:0 2px 10px rgba(0,201,167,.25)}.ps-kl-ghost{transition:background .15s}.ps-kl-tile:hover .ps-kl-ghost,.ps-kl-tile:focus-visible .ps-kl-ghost{background:#E7FAF5}</style>'
    '<strong style="display:block;font-size:1.1rem;color:#0f0f23;margin:0 0 6px;">Want your bus or car sorted before you fly?</strong>'
    '<p style="margin:0 0 14px;font-size:0.95rem;color:#333;line-height:1.5;">You can book both on Klook. You can also buy a bus ticket at the airport or take a train, so booking ahead is a convenience, not a must.</p>'
    '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin:0 0 12px;">'
    + "".join(kl_tile(r) for r in KL_ROWS) +
    '</div>'
    '<p style="margin:0;font-size:0.85rem;color:#555;line-height:1.5;">Before you pay, read each listing\'s change and cancellation rules. Limousine Bus bookings cannot be amended: you cancel and rebook. Buses can run late in traffic, so leave a buffer. Klook prices checked 18 Nov 2026 and they change by date and route. We earn a small commission if you book through these links, at no extra cost to you.</p>'
    '</div>'
)


TO_TOKYO = """<h2 id="to-tokyo">Getting to Tokyo</h2>
<p>Haneda is close to the city, so most people take a train. Times and prices below are approximate: they differ a little between sources and change over time, so check the operator before you go.</p>
""" + CHOOSER + """
<h3>All the options</h3>
<div class="ps-scroll">
<table class="checklist-table">
<thead><tr><th>Option</th><th>Goes to</th><th>About how long</th><th>About how much</th><th>Good to know</th></tr></thead>
<tbody>
<tr><td><strong>Keikyu Line</strong></td><td>Shinagawa, Yokohama, Asakusa</td><td>Shinagawa about 15 min; Yokohama about 30; Asakusa about 40</td><td>About ¥510 to Tokyo Station, changing at Shinagawa</td><td>Gates for Tokyo and Yokohama are on the 2nd-floor arrival lobby. Check the train type on the display.</td></tr>
<tr><td><strong>Tokyo Monorail</strong></td><td>Hamamatsucho, then JR trains</td><td>Hamamatsucho about 20 min; Tokyo Station about 30 min with the change</td><td>About ¥690 to Tokyo Station</td><td>Good for Tokyo Station and the Yamanote Line. Gates are on the 2nd and 3rd floors of Terminal 3.</td></tr>
<tr><td><strong>Airport Limousine Bus</strong></td><td>Shinjuku, Shibuya, Tokyo Station, large hotels, Tokyo Disney Resort</td><td>About 45 to 80 min, depending on where you go and the traffic</td><td>About ¥1,000 to ¥1,300 to the main stops</td><td>Buy a ticket from a machine or the bus counter in the 2nd-floor arrival lobby. No changing trains.</td></tr>
<tr><td><strong>Taxi</strong></td><td>Door to door</td><td>Depends on the area and the traffic</td><td>Haneda lists fixed fares on most routes to Tokyo and Kanagawa; tolls are added. Ask the company for the fare</td><td>Taxis leave from stop 21 on the 1st floor. A late-night surcharge may apply. Check the fare before you set off.</td></tr>
</tbody>
</table>
</div>
<div class="warning-box">
    <strong>Check the train name.</strong> Keikyu runs fast and slow trains on the same line, and the time to Shinagawa depends on which you board. Look at the train type and destination on the display before you get on.
</div>
""" + KLOOK_TRANSPORT + """
<p><strong>Late arrival?</strong> Trains run from about 5 am until around midnight (ANA's airport guide lists the last Keikyu train around 23:48 and the last Monorail around 00:02). After that, late-night buses and taxis run, and there are hotels inside the terminals. Check the last train for your route before you book.</p>
<p><strong>Going on to Narita?</strong> See the Haneda-or-Narita section below.</p>
""" + JB_SHINKANSEN + """
<p>If you would rather have a driver waiting for you after a long flight, you can book a fixed-price private transfer in advance:</p>
""" + pickups + """
<p>If you are leaving Tokyo by road, you can also collect a rental car at Haneda:</p>
""" + cars + """
<p class="ps-note">Sources: <a href="https://tokyo-haneda.com/en/access/train" target="_blank" rel="noopener noreferrer">Haneda Airport: trains and monorail</a>, <a href="https://ana.co.jp/en/gb/international/departure/airport/map/hnd.html" target="_blank" rel="noopener noreferrer">ANA's Haneda guide</a>, <a href="https://www.tokyo-haneda.com/en/access/taxi" target="_blank" rel="noopener noreferrer">Haneda taxis</a>. Checked 18 November 2026.</p>"""


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
<div id="psPocketBar" role="region" aria-label="Haneda Pocket Guide">
<div class="t"><b>Get the Haneda Pocket Guide</b><span>Free. Works offline at the airport.</span></div>
<a class="go" href="/haneda-pocket?src=bar">Get it</a>
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
<p>Open the Haneda Pocket Guide once while you have signal, then add it to your home screen. At the airport it opens like an app, even with no connection.</p>
<p><a class="ps-btn2" href="/haneda-pocket?src=box" onclick="try{window.gtag&&gtag('event','pocket_prompt',{event_category:'engagement',action:'open_box',page_path:location.pathname});}catch(e){}" style="display:inline-block;text-decoration:none;">Open the Pocket Guide</a></p>
<ul>
<li><strong>iPhone:</strong> open it in Safari, tap the Share button, then "Add to Home Screen".</li>
<li><strong>Android:</strong> open it in Chrome, tap the menu (three dots), then "Add to Home screen" or "Install app".</li>
</ul>
</div>"""

FACILITIES = """<h2 id="facilities">Facilities by terminal</h2>
<p>This table follows Haneda Airport's own floor maps (2025 editions) and service pages, checked on 18 November 2026. Floor labels use the airport's wording. A dash means the airport's list does not show one. Hours are as printed on the maps and can change.</p>
<div class="ps-scroll">
<table class="checklist-table">
<thead><tr><th>Facility</th><th>Terminal 1</th><th>Terminal 2</th><th>Terminal 3</th></tr></thead>
<tbody>
<tr><td><strong>Prayer room</strong></td><td>None</td><td>International area: 3F, before security (2 rooms); 2F, after security (2 rooms)</td><td>3F, before security (2 rooms)</td></tr>
<tr><td><strong>Nursing room</strong></td><td>Marked on B1F, 1F and the 2F gate area</td><td>Marked on 1F, 3F and 4F</td><td>Marked on 1F to 4F</td></tr>
<tr><td><strong>Quiet space</strong> ("Calm down, cool down")</td><td>2F domestic gate area</td><td>2F domestic gate area</td><td>Marked on 3F</td></tr>
<tr><td><strong>Information counter</strong></td><td>1F Airport Service Center (6 am to 8 pm); others on 2F</td><td>B1F, 1F, 2F; Tourist Information Center on 2F (5:45 am to 11 pm)</td><td>Tourist Information Center on 2F (24 hours); others on every floor</td></tr>
<tr><td><strong>Coin lockers</strong></td><td>B1F, 1F, 2F</td><td>1F, 2F, 3F</td><td>2F, 3F</td></tr>
<tr><td><strong>Showers</strong></td><td>-</td><td>1F (5 am to 10 pm)</td><td>2F (24 hours)</td></tr>
<tr><td><strong>Wi-Fi rental counter</strong></td><td>-</td><td>2F, 3F</td><td>2F, 3F</td></tr>
<tr><td><strong>Children's play area</strong></td><td>2F (3 spaces)</td><td>2F (3 spaces)</td><td>3F (2 spaces)</td></tr>
<tr><td><strong>Clinic</strong></td><td>1F</td><td>1F</td><td>1F</td></tr>
<tr><td><strong>Airport hotel</strong></td><td>First Cabin (1F arrival lobby)</td><td>Haneda Excel Hotel Tokyu (2F terminal lobby, north)</td><td>The Royal Park Hotel Tokyo Haneda (3F departure lobby, plus airside transit rooms)</td></tr>
</tbody>
</table>
</div>
<h3>Nursing rooms</h3>
<p>Nursing rooms are marked on the floor maps of every terminal. The maps show the symbol on several floors but do not name each room, so ask at an information counter for the nearest one.</p>
<h3>If you need help</h3>
<p>Every terminal has information counters. If you are tired, unsure or carrying a lot, go straight to a counter instead of searching on your own.</p>
<p class="ps-note">Sources: Haneda Airport's floor maps for <a href="https://tokyo-haneda.com/site_resource/floor/pdf/floor__pdf_floor_map_t1_en.pdf" target="_blank" rel="noopener noreferrer">Terminal 1</a>, <a href="https://tokyo-haneda.com/site_resource/floor/pdf/floor__pdf_floor_map_t2_en.pdf" target="_blank" rel="noopener noreferrer">Terminal 2</a> and <a href="https://tokyo-haneda.com/site_resource/floor/pdf/floor__pdf_floor_map_t3_en.pdf" target="_blank" rel="noopener noreferrer">Terminal 3</a> (PDF), and its pages on <a href="https://tokyo-haneda.com/en/service/facilities/prayer_room.html" target="_blank" rel="noopener noreferrer">prayer rooms</a> and <a href="https://tokyo-haneda.com/en/service/facilities/hotel.html" target="_blank" rel="noopener noreferrer">airport hotels</a>. Floors and opening hours can change, so confirm on the day. Found something out of date? <a href="/contact">Tell us</a>.</p>"""

LEAVING = """<h2 id="leaving">Leaving Haneda</h2>
<ul>
<li><strong>Know your terminal.</strong> Most international flights leave from Terminal 3, which has its own Keikyu and Monorail stations. Some airlines use Terminal 2's international area. Check your ticket before you set off.</li>
<li><strong>Return rented gear first.</strong> If you rented a pocket Wi-Fi, check how to return it. Some companies take it back at the airport counter, others at a postbox.</li>
<li><strong>Allow time.</strong> Check-in, security and passport control all take time, so arrive early. Your airline sets its own advice for international flights, so check your ticket.</li>
<li><strong>Shopped tax-free?</strong> From 1 November 2026 you pay the tax at the shop and claim it back at the airport. Within 90 days of buying, scan your passport at a tax-free procedure terminal <em>before</em> you board, with your receipts and the items with you, because they may be inspected and cannot be checked in first. Haneda lists the terminals on its <a href="https://tokyo-haneda.com/en/service/facilities/tax_refund.html" target="_blank" rel="noopener noreferrer">tax refund page</a>: Terminal 1 has no tax refund service, so use Terminal 2 or 3, where the procedure terminals are before the 3rd-floor security check. Terminal 3's are open 24 hours. Allow extra time, as queues are likely while the system is new (checked 18 November 2026).</li>
</ul>
<p data-ps-placement="bags-haneda-tokyo" style="background:#f0faf7;border-left:3px solid #00C9A7;padding:12px 16px;border-radius:0 8px 8px 0;font-size:0.92rem;margin:20px 0;">&#129523; Checked out of your Tokyo hotel with hours to spare before a Haneda flight? <a href="https://radicalstorage.tpx.li/d0Eds67a" target="_blank" rel="nofollow noopener sponsored" style="color:#00C9A7;text-decoration:underline;">Store your bags in Tokyo with Radical Storage</a> and travel light until it is time to go.</p>"""

LAYOVER = """<h2 id="layover">A short stop or a long layover</h2>
<p>If you have less than about 4 hours between flights, stay in the airport. Immigration, the train ride and the trip back eat up the time. Haneda is close to central Tokyo, so with a longer wait a short trip is realistic: leaving the airport means passing immigration, so check whether you need a visa, and leave plenty of time to get back. You can also rest inside the airport: The Royal Park Hotel Tokyo Haneda has transit rooms on the airside of Terminal 3, and the HANEDA AIRPORT GARDEN complex next to Terminal 3 has a tourist-information centre with luggage storage and currency exchange.</p>"""




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
    '<p style="font-size:0.85rem;color:#666;margin:0 0 0.6rem;">Published November 18, 2026 · Last updated November 2026 · Facts checked 18 Nov 2026</p>',
    AFFILIATE_P,
    share,
    PRINT_CSS,
    '<p>Haneda is the airport closest to central Tokyo, but it has three terminals, and most international flights use Terminal 3. '
    'This guide is written in plain English so that a first-time visitor, a family or an older traveller can follow it step by step. '
    'You can print the one-page card below and carry it with you.</p>',
    toc_html,
    CARD,
    TERMINALS,
    DIAGRAM,
    ARRIVAL,
    CONNECTED,
    airalo,
    SAKURA,
    IC_CARD,
    TO_TOKYO,
    LUGGAGE,
    FINDER,
    SAVE_BOX,
    FACILITIES,
    HELP,
    LEAVING,
    LAYOVER,
    LATE,
    HND_NRT,
    '<div class="tip-box">\n    <strong>Planning more of Japan?</strong> Our <a href="/blog/japan-travel-packing-guide">Japan travel and packing guide</a> covers what to pack, rail passes, etiquette and a budget breakdown, and the <a href="/blog/japan-7-day-itinerary-budget">7-day Japan itinerary</a> shows how a first week can look.\n</div>',
    "<!-- FIRST-HAND NOTES: add notes and photos from a Haneda visit here -->",
    faq_html(),
    ABOUT,
    RELATED,
    POCKET_BAR,
])

# hero button (v50): a quiet way into the Pocket Guide from the top of the article
HERO_CTA = ('        <div style="margin:48px 0 0;text-align:center;">'
            '<a href="/haneda-pocket?src=hero" onclick="try{window.gtag&&gtag(\'event\',\'pocket_prompt\',{event_category:\'engagement\',action:\'open_hero\',page_path:location.pathname});}catch(e){}" '
            'style="display:inline-flex;align-items:center;gap:12px;background:#00C9A7;color:#0f0f23;text-align:left;padding:12px 14px 12px 20px;width:340px;max-width:100%;box-sizing:border-box;border-radius:12px;text-decoration:none;min-height:44px;box-shadow:0 6px 18px rgba(0,0,0,.28);line-height:1.2;">'
            '<span style="flex:1;min-width:0;text-align:left;">'
            '<span style="display:block;font-weight:700;font-size:0.8rem;opacity:0.8;">Save to your phone</span>'
            '<span style="display:block;font-weight:800;font-size:1.05rem;margin-top:2px;">Haneda Pocket Guide</span>'
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
    '        <div class="meta">Airport Guide • Japan · 8 min read</div>',
    HERO_CTA,
    ('        <div style="position:absolute;left:12px;right:12px;bottom:8px;font-size:0.7rem;opacity:0.7;text-align:center;">Photo: PAKUTASO. Illustrative image of the Haneda Airport Terminal 3 departure hall.</div>' if HERO_URL else ''),
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
    changed.append("haneda-airport-guide.html (%s bytes)" % len(page.encode("utf-8")))


# ---- Haneda Pocket Guide: standalone page + service worker + manifest (works offline once visited)
POCKET_PATH = "/haneda-pocket"
# ---- Pocket Guide analytics (v47): anonymous taps only, no accounts, honours Do Not Track / GPC
GUIDE_ID = "haneda"
AIRPORT_CODE = "HND"
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
    if(/^tel:/i.test(h)){ var d=h.replace(/^tel:/i,'').replace(/[^0-9+]/g,''); var nm={'119':'fire_ambulance','110':'police','+81357578111':'airport','+815038162787':'help_line'}; pgTrack('pg_call',{dest:nm[d]||d,where:whereNow()}); return; }
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

POCKET_SVG = re.search(r'<svg id="hndDiagram".*?</svg>', DIAGRAM, re.S).group(0).replace('id="hndDiagram"', 'id="pkDiagram"').replace('id="hndT"', 'id="pkT"').replace('id="hndD"', 'id="pkD"').replace('aria-labelledby="hndT hndD"', 'aria-labelledby="pkT pkD"')
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
.seg{display:grid;grid-template-columns:repeat(3,1fr) 1.15fr;gap:8px}
.seg button{font:inherit;min-height:54px;border:2px solid #D5DCE0;background:#fff;color:#0f0f23;border-radius:14px;cursor:pointer;padding:4px 2px;line-height:1.1;display:flex;flex-direction:column;align-items:center;justify-content:center}
.seg button small{font-size:0.7rem;font-weight:600;color:#666}
.seg button b{font-size:1.5rem}
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
<title>Haneda Pocket Guide | PackSmart</title>
<meta name="description" content="A simple Haneda Airport helper that works offline: terminals, prayer rooms, nursing rooms, lockers and more. By PackSmart.">
<meta name="robots" content="noindex,follow">
<link rel="canonical" href="__GUIDE_URL__">
<meta name="theme-color" content="#1a1a3e">
<link rel="manifest" href="/haneda-pocket.webmanifest">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" href="/images/haneda-apple-touch-v2-180.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Haneda">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<script>__PG_BOOT__</script>
<style>__CSS__</style>
</head>
<body>
<header class="top">
<div><strong>Haneda Pocket Guide</strong><span class="by">by PackSmart &middot; 18 Nov 2026</span></div>
<div class="status" id="status" role="status">Checking...</div>
</header>
<button type="button" class="inst-strip" id="instStrip" hidden><span class="ico" aria-hidden="true">&#128242;</span><span><b>Add this to your home screen</b><br>so it works with no internet</span><span class="go">How</span></button>
<div class="panels" id="panels">
<section class="panel" id="p-find" role="tabpanel" aria-labelledby="t-find">
<p class="seg-h">Which terminal are you in?</p>
<div class="seg" id="seg"></div>
<p class="seg-h" style="margin-top:14px">What do you need? <span class="small">Tap one.</span></p>
<div class="pager" id="pager"><div class="track" id="track"><div class="tiles pane" id="tiles"></div><div class="tiles pane off" id="tiles2" aria-hidden="true"></div></div></div>
<p class="hint">Floors can change. Ask at an information counter.</p>
<div id="sponsor" hidden></div>
<noscript><p class="card">This guide needs JavaScript. Please turn it on, or ask at any information counter.</p></noscript>
</section>
<section class="panel" id="p-map" role="tabpanel" aria-labelledby="t-map" hidden>
<p class="seg-h" style="margin-top:2px">Which terminal are you in?</p>
<div class="seg" id="mseg"></div>
<p class="lead2" id="mLead" style="margin-top:10px">Your ticket or airline app shows which one is yours.</p>
<div class="tmap" id="tmap">
<div class="tcard t3" data-t="T3"><div class="badge">3</div><div class="tb"><h3>Terminal 3</h3><p>Most international flights</p><p class="stn"><span aria-hidden="true">&#128646;</span> Own Keikyu and Monorail stations</p></div></div>
<div class="tlink"><span aria-hidden="true">&#128652;</span><span>Free shuttle bus<br>(1st floor)</span></div>
<div class="tcard t1" data-t="T1"><div class="badge">1</div><div class="tb"><h3>Terminal 1</h3><p>Domestic flights, mainly JAL</p><p class="stn"><span aria-hidden="true">&#128646;</span> Keikyu 1&middot;2 and Monorail 1 stations</p></div></div>
<div class="tlink"><span aria-hidden="true">&#128652;</span><span>Free shuttle bus<br>(1st floor)</span></div>
<div class="tcard t2" data-t="T2"><div class="badge">2</div><div class="tb"><h3>Terminal 2</h3><p>Domestic flights, mainly ANA</p><p>Also an international area</p><p class="stn"><span aria-hidden="true">&#128646;</span> Keikyu 1&middot;2 and Monorail 2 stations</p></div></div>
</div>
<p class="small" style="text-align:center;margin-top:10px">Simplified, not to scale. Airlines can change terminals, so check before you go. Shuttle buses can run late in traffic. The walkway between Terminals 1 and 2 was out of service when we checked. <a href="https://tokyo-haneda.com/en/access/travel_between_terminals" target="_blank" rel="noopener noreferrer">Official page on travelling between terminals</a> (needs internet).</p>
</section>
<section class="panel" id="p-arrive" role="tabpanel" aria-labelledby="t-arrive" hidden>
<p class="lead2">Landed? Tap a step to tick it off.</p>
<ol class="steps" id="arrSteps"></ol>
<button type="button" class="reset" id="arrReset" hidden>Clear ticks</button>
<p class="sec-h">Then, once you are out</p>
<div class="tiles" id="arrTiles"></div>
</section>
<section class="panel" id="p-depart" role="tabpanel" aria-labelledby="t-depart" hidden>
<div class="seg2" id="depSeg" role="group" aria-label="Departure sections"><button type="button" data-d="before" aria-pressed="true">Before you go</button><button type="button" data-d="air" aria-pressed="false">At the airport</button></div>
<div id="depBefore">
<div class="tiles" id="depTiles"></div>
<p class="hint">Tap one for the details. Prices and times are approximate.</p>
</div>
<div id="depAir" hidden>
<div class="heroline"><span class="big2">2 h</span><span><b>Aim to arrive about 2 hours early.</b><br>Your airline sets when check-in opens, so check your ticket.</span></div>
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
<p class="sec-h">At Haneda Airport only</p>
<a class="num air" href="tel:+81357578111"><span class="ni" aria-hidden="true">&#8505;&#65039;</span><span class="nt"><b>Haneda Airport Information</b><span>+81 3-5757-8111</span><small>5 am to midnight</small></span></a>
<p class="small" style="margin-top:8px">Every terminal has information counters. Staff will help, so just ask.</p>
<p class="sec-h">Help or travel questions</p>
<a class="num hot" href="tel:+815038162787"><span class="ni" aria-hidden="true">&#128222;</span><span class="nt"><b>Japan Visitor Hotline</b><span>050-3816-2787</span><small>24 hours. English, Chinese, Korean</small></span></a>
</div>
<div class="tiles hnav" id="hnav2"></div>
</div>
</div></div>
<div class="quiet"><div class="card slim" id="shareCard" hidden><div class="row"><div><h2>Helping someone travel?</h2><p>Send them this guide for offline use.</p></div><button type="button" class="big" id="shareBtn">Send it</button></div></div>
<div class="card slim install" id="install"><div class="row"><div><h2>Keep this on your phone</h2><p>Add it to your home screen. Works offline.</p><p class="small" id="instDesk">Open this page on your phone, then add it to your home screen.</p></div><div id="instHow" hidden><button type="button" class="big" id="instBtn">Show me</button></div></div></div>
<p class="small">Facility details come from Haneda Airport's own floor maps and pages, checked 18 November 2026. Floors, opening hours and counters can change. If you cannot find something, ask at an information counter. Found something out of date? <a href="/contact">Tell us</a> (needs internet). We count anonymous taps to improve this guide: no name, no account. <a href="/privacy-policy">Privacy</a> &middot; <a href="#" id="pgOpt">Turn off counting</a>. The full guide, with trains, SIM and luggage, is at <a href="__GUIDE_URL__">packsmartapp.com</a> (needs internet).</p></div>
</section>
</div>
<nav class="tabs" role="tablist" aria-label="Sections">
<button type="button" role="tab" id="t-find" data-tab="find" aria-selected="true"><span aria-hidden="true">&#128269;</span>Find</button>
<button type="button" role="tab" id="t-map" data-tab="map" aria-selected="false"><span aria-hidden="true">&#128506;&#65039;</span>Terminals</button>
<button type="button" role="tab" id="t-arrive" data-tab="arrive" aria-selected="false"><span aria-hidden="true">&#128748;</span>Arrival</button>
<button type="button" role="tab" id="t-depart" data-tab="depart" aria-selected="false"><span aria-hidden="true">&#128747;</span>Departure</button>
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
  var ICON={prayer:'\\uD83D\\uDE4F',baby:'\\uD83C\\uDF7C',quiet:'\\uD83E\\uDD2B',info:'\\u2139\\uFE0F',help:'\\u267F',lockers:'\\uD83E\\uDDF3',wifi:'\\uD83D\\uDCF6',shower:'\\uD83D\\uDEBF',internet:'\\uD83D\\uDCBB',play:'\\uD83E\\uDDF8',smoking:'\\uD83D\\uDEAC',toilet:'\\uD83D\\uDEBB',food:'\\uD83C\\uDF5C',money:'\\uD83D\\uDCB4',unwell:'\\uD83C\\uDFE5',pharmacy:'\\uD83D\\uDC8A',trains:'\\uD83D\\uDE86',phone:'\\uD83D\\uDCF6',charge:'\\uD83D\\uDD0B',more:'\\u2795'};
  var SHORT={prayer:'Prayer room',baby:'Nursing room',quiet:'Quiet space',info:'Information counter',help:'Wheelchair and help',lockers:'Luggage',wifi:'Wi-Fi rental',shower:'Showers',internet:'Free internet',play:'Kids play area',smoking:'Smoking room',toilet:'Toilets',food:'Food and drink',money:'Money and ATMs',unwell:'Feeling unwell',pharmacy:'Pharmacy',trains:'Train, bus, taxi',phone:'Phone and Wi-Fi',charge:'Phone charging',more:'More places'};
  var term='ALL', lastTile=null;
  try{ var s=localStorage.getItem('hndTerm'); if(s&&/^(ALL|T1|T2|T3)$/.test(s)) term=s; }catch(e){}
  function $(id){return document.getElementById(id);}
  /* terminal selector */
  var seg=$('seg');
  function segBtn(id,html,cls){
    var b=document.createElement('button'); b.type='button'; b.setAttribute('data-t',id); if(cls) b.className=cls;
    b.innerHTML=html; b.addEventListener('click',function(){ term=id; try{localStorage.setItem('hndTerm',id);}catch(e){} paintSeg(); renderDep(); }); return b;
  }
  D.terms.forEach(function(t){ seg.appendChild(segBtn(t[0],'<small>Terminal</small><b>'+t[0].charAt(1)+'</b>')); });
  seg.appendChild(segBtn('ALL','Not sure','txt'));
  var mseg=$('mseg');
  D.terms.forEach(function(t){ mseg.appendChild(segBtn(t[0],'<small>Terminal</small><b>'+t[0].charAt(1)+'</b>')); });
  mseg.appendChild(segBtn('ALL','Not sure','txt'));
  function paintSeg(){ [seg,mseg].forEach(function(g){ [].forEach.call(g.children,function(b){ b.setAttribute('aria-pressed',b.getAttribute('data-t')===term?'true':'false'); }); }); paintMap(); }
  /* Terminals tab: personal view for the terminal the person chose */
  function paintMap(){
    var S={T1:8,T2:9,T3:0};
    var R={}; ['T1','T2','T3'].forEach(function(a){ R[a]={}; ['T1','T2','T3'].forEach(function(b){ if(a!==b) R[a][b]='Free shuttle bus from stop '+S[a]+' on the 1st floor'; }); });
    var personal=(term==='T1'||term==='T2'||term==='T3');
    $('mLead').textContent=personal?('You are in Terminal '+term.charAt(1)+'. Here is how to reach the others.'):'Your ticket or airline app shows which one is yours.';
    [].forEach.call(document.querySelectorAll('#tmap .tlink'),function(e){ e.hidden=personal; });
    [].forEach.call(document.querySelectorAll('#tmap .tcard'),function(c){
      var id=c.getAttribute('data-t'), tb=c.querySelector('.tb');
      [].forEach.call(c.querySelectorAll('.heretag,.route'),function(e){ e.parentNode.removeChild(e); });
      c.classList.toggle('here',personal&&id===term);
      if(!personal) return;
      if(id===term){ var g=document.createElement('p'); g.className='heretag'; g.textContent='You are here'; tb.insertBefore(g,tb.firstChild); }
      else { var r=document.createElement('p'); r.className='route'; r.textContent='\\uD83D\\uDE8C From here: '+R[term][id]; tb.appendChild(r); }
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
  var PH_TXT=' Phone charging: power outlets and charging corners are marked on the terminal floor maps. Ask at an information counter for the nearest.';
  var phoneIt=['phone','Phone and Wi-Fi',{}];
  D.terms.forEach(function(t){ phoneIt[2][t[0]]='Pocket Wi-Fi and SIM rental counters: '+item('wifi')[2][t[0]]+'.'+PH_TXT; });
  var trainsIt=['trains','Train, bus or taxi',{}];
  var LIST=[];
  ['money','food','toilet','help','lockers','baby','play','trains','info','unwell','pharmacy','phone','prayer','quiet','shower','smoking'].forEach(function(id){
    LIST.push(id==='trains'?trainsIt:id==='phone'?phoneIt:item(id));
  });
  LIST.forEach(function(it,n){
    var b=document.createElement('button'); b.type='button'; b.className='tile c'+(n%3); b.setAttribute('data-id',it[0]);
    var ic=document.createElement('span'); ic.className='ic'; ic.setAttribute('aria-hidden','true'); ic.textContent=ICON[it[0]]||'\\u2022';
    var tx=document.createElement('span'); tx.className='tx'; tx.textContent=SHORT[it[0]]||it[1];
    b.appendChild(ic); b.appendChild(tx);
    b.addEventListener('click',function(){ if(it[0]==='trains'){ openInfo(ICON.trains,it[1],trainHTML(),b); } else { openSheet(it,b); } });
    (n<MAIN?tiles:tiles2).appendChild(b);
    if(n===MAIN-1){ tiles.appendChild(pill('pgnext','\\u2192','More','Information counter, prayer room and others',function(){ slideTo(1); })); }
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
  var NONE='The airport list does not show one here. Please ask at an information counter.';
  function ans(label,txt,mini){
    var d=document.createElement('div'); d.className='ans'+(mini?' mini':'');
    if(label){ var e=document.createElement('em'); e.textContent=label; d.appendChild(e); }
    d.appendChild(document.createTextNode(txt||NONE)); return d;
  }
  function openSheet(it,btn){
    lastTile=btn; shT.textContent=''; shB.textContent='';
    var ic=document.createElement('span'); ic.setAttribute('aria-hidden','true'); ic.textContent=ICON[it[0]]||''; shT.appendChild(ic);
    shT.appendChild(document.createTextNode(it[1]));
    if(term==='ALL'&&D.terms.every(function(t){return it[2][t[0]]===it[2][D.terms[0][0]];})){ shB.appendChild(ans('All terminals',it[2][D.terms[0][0]],false)); }
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
  function trainHTML(){
    var st={T1:'Terminal 1: <b>Keikyu Terminal 1&middot;2</b> or <b>Monorail Terminal 1</b> station (basement floor).',T2:'Terminal 2: <b>Keikyu Terminal 1&middot;2</b> or <b>Monorail Terminal 2</b> station (basement floor).',T3:'Terminal 3: its own <b>Keikyu</b> and <b>Monorail</b> stations. Ticket gates are on 2F, the arrival lobby.'};
    var h='<p class="n2">'+(term==='ALL'?[st.T3,st.T1,st.T2].join('<br>'):st[term])+'</p>';
    h+='<ul class="pl"><li><b>Keikyu Line:</b> about 15 min to Shinagawa, 30 to Yokohama, 40 to Asakusa. About &yen;510 to Tokyo Station with a change at Shinagawa.</li>'
      +'<li><b>Tokyo Monorail:</b> about 20 min to Hamamatsucho, about 30 min to Tokyo Station with a change. About &yen;690.</li>'
      +'<li><b>Limousine bus:</b> about 45 to 80 min to Shinjuku, Tokyo Station and large hotels. About &yen;1,000 to &yen;1,300 to the main stops. Tickets from machines in the 2F arrival lobby.</li>'
      +'<li><b>Taxi:</b> from stop 21 on 1F. Haneda lists fixed fares on most routes to Tokyo and Kanagawa; tolls are added. Check the fare first.</li>'
      +'<li><b>Private car:</b> a fixed-price transfer is about &euro;45 per car (figure from the company, Nov 2026).</li></ul>';
    h+='<div class="tipbox">Trains run from about 5 am until around midnight. After that, late-night buses and taxis run. Check the last train for your route.</div>';
    h+='<p class="sm">Times and prices are approximate and change. Check the operator.</p>';
    h+='<p class="sm">You can book here (partner links): <a href="https://klook.tpo.lu/PwSUuJEu" target="_blank" rel="sponsored nofollow noopener">Limousine bus</a> &middot; <a href="https://klook.tpo.lu/5y9oQYD7" target="_blank" rel="sponsored nofollow noopener">Private car</a></p>';
    return h;
  }
  function simHTML(){
    var w=item('wifi')[2], f=term==='ALL'?D.terms.map(function(t){return t[1]+': '+w[t[0]];}).join('<br>'):w[term];
    return '<ul class="pl"><li><b>eSIM:</b> install it before you fly. It works as soon as you land.</li>'
      +'<li><b>Pocket Wi-Fi rental counters</b> are in the terminals. Floors:<br>'+f+'</li>'
      +'<li><b>Free airport Wi-Fi:</b> HANEDA-FREE-WIFI. Fine for a quick message, not for a day of maps.</li></ul>'
      +'<p class="sm">Counter hours and stock vary. Ordering ahead is safer.</p>'
      +'<p class="sm">You can book pocket Wi-Fi here (partner link): <a href="https://p.sakuramobile.jp/idevaffiliate.php?id=728" target="_blank" rel="sponsored nofollow noopener">Sakura Mobile</a></p>';
  }
  function cashHTML(){
    return '<ul class="pl"><li><b>Currency exchange</b> offices and <b>cash machines</b> are in the terminals. Tap Find, then Money and ATMs.</li>'
      +'<li><b>Welcome Suica</b> is a tourist train card. No deposit, valid 28 days, and money left on it cannot be refunded.</li>'
      +'<li>Where to buy it: the JR East Travel Service Center or the Welcome Suica machines at Haneda Airport Terminal 3 (Tokyo Monorail) Station. Not sure? Ask at the Tourist Information Center (Terminal 3, 2F arrival lobby, open 24 hours).</li>'
      +'<li>iPhone users can set up Welcome Suica Mobile before landing.</li></ul>'
      +'<p class="sm">Card types and sales points change often. Check JR East before you travel.</p>';
  }
  function carHTML(){
    return '<p class="n2">Most visitors skip a car in Tokyo, because trains are quicker.</p>'
      +'<ul class="pl"><li>A car helps for trips out of the city, such as Mt Fuji or the countryside. Haneda is an easy place to pick one up.</li>'
      +'<li>Bring your <b>passport</b>, your <b>home driving licence</b> and an <b>International Driving Permit</b> (1949 Geneva Convention type). Get it before you leave home. It cannot be issued in Japan.</li>'
      +'<li>Some countries, such as Germany and France, use an official Japanese translation of the licence instead. Check before you travel.</li>'
      +'<li>Japan drives on the left.</li>'
      +'<li>Book ahead in busy seasons.</li></ul>'
      +'<p class="sm"><a href="'+GUIDE+'#rent-a-car">Compare car prices in the full guide</a> (needs internet)</p>';
  }
  function bagsHTML(){
    return '<ul class="pl"><li>Haneda lists luggage delivery counters (<b>Yamato</b>, <b>JAL</b> and <b>Sagawa</b>) in all three terminals. Ask which counter is in your terminal.</li>'
      +'<li>Usually arrives <b>the next day</b>.</li>'
      +'<li>Write down your hotel name, address and phone number.</li>'
      +'<li>Keep medicines, valuables and chargers with you.</li></ul>'
      +'<p class="sm">Prices and cut-off times change. Confirm at the counter.</p>'
      +'<p class="sm">You can also book online (partner link): <a href="https://klook.tpo.lu/jmWXAbkc" target="_blank" rel="sponsored nofollow noopener">Luggage delivery between Tokyo hotels and the airport</a> (Haneda or Narita).</p>';
  }
  var NEXT=[['🚆','Train, bus or taxi',trainHTML],['📱','Phone data',simHTML],['💴','Cash and train card',cashHTML],['📦','Send your suitcase',bagsHTML],['🚗','Rent a car',carHTML]];
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
  var ARR=[['Quarantine',"Hand in the health form if your flight gave you one. Feeling unwell? Tell an officer."],
    ['Immigration','Show your passport. Automatic gates give no stamp: ask staff if you want one.'],
    ['Baggage claim','Find your flight on the screen and go to its carousel. Carts are nearby.'],
    ['Customs','Show your Visit Japan Web QR code or paper form. Food or plants? Declare them first.'],
    ['Arrival lobby','You are on 2F. Follow the signs to trains, monorail, buses and taxis.']];
  function ckText(){
    if(term==='ALL') return 'Most international flights: Terminal 3, 3F departure lobby. Some airlines use the Terminal 2 international area, 3F. Check your ticket.';
    if(term==='T1') return 'Terminal 1 is mainly for domestic flights. For an international flight, check your ticket: most leave from Terminal 3, 3F.';
    if(term==='T2') return 'Terminal 2: the international departure lobby is on 3F. Domestic flights use the other counters. Check your ticket.';
    return 'Terminal 3: international check-in is in the 3F departure lobby. Or use a kiosk or self bag drop.';
  }
  var DEP=[['Tax-free procedure, if you shopped','Scan your passport at a tax-free procedure terminal before security, and keep the items with you. Terminal 1 has none: use Terminal 2 or 3.'],
    ['Check in',ckText],
    ['Before security','Change money, sort roaming or insurance, hand back or post rented Wi-Fi. Spend any Welcome Suica balance: no refunds.'],
    ['Security',"Have your passport, boarding pass and carry-on ready. Check your airline's rules on liquids."],
    ['Customs, only if needed','Declare over ¥1 million cash, foreign-made goods like a watch, or duty-free items. Checked-bag items: before check-in.'],
    ['Passport control','Show your passport and boarding pass. Automatic gates give no stamp.'],
    ['Boarding gate','Be at your gate well before boarding. Wait for staff instructions.']];
  function renderDep(){ renderSteps($('depSteps'),DEP,doneD); }
  renderSteps($('arrSteps'),ARR,doneA); renderDep();
  $('arrReset').addEventListener('click',function(){ doneA.length=0; renderSteps($('arrSteps'),ARR,doneA); syncReset(); });
  $('depReset').addEventListener('click',function(){ doneD.length=0; renderDep(); syncReset(); });
  /* departure: before you go */
  var GUIDE='__GUIDE_URL__';
  function more(a){ return '<p class="sm"><a href="'+GUIDE+a+'">More in the full guide</a> (needs internet)</p>'; }
  function gettingHTML(){
    var st={T1:'Terminal 1: <b>Keikyu Terminal 1&middot;2</b> or <b>Monorail Terminal 1</b> station.',T2:'Terminal 2: <b>Keikyu Terminal 1&middot;2</b> or <b>Monorail Terminal 2</b> station.',T3:'Terminal 3: its own <b>Keikyu</b> and <b>Monorail</b> stations.'};
    var h='<p class="n2">'+(term==='ALL'?[st.T3,st.T1,st.T2].join('<br>'):st[term])+'</p>';
    h+='<ul class="pl"><li><b>Keikyu Line:</b> about 15 min from Shinagawa, 30 from Yokohama, 40 from Asakusa.</li>'
      +'<li><b>Tokyo Monorail:</b> about 20 min from Hamamatsucho, about 30 min from Tokyo Station with a change.</li>'
      +'<li><b>Limousine bus from hotels:</b> about 45 to 80 min, about &yen;1,000 to &yen;1,300 from the main stops.</li>'
      +'<li><b>Taxi or private car:</b> door to door. Haneda lists fixed taxi fares on most routes to Tokyo and Kanagawa; tolls are added. A fixed-price private car is about &euro;45 per car (figure from the company, Nov 2026).</li></ul>';
    h+='<div class="tipbox"><b>Early flight?</b> Trains start around 5 am. Check first-train times for your route the day before. For a very early flight you may need a taxi, a late-night bus, or a hotel near the airport the night before.</div>';
    h+='<p class="sm">Times and prices are approximate and change. Check the operator.</p>';
    return h;
  }
  function sendOutHTML(){
    return '<ul class="pl"><li>Services such as <b>Yamato</b> and <b>JAL ABC</b> can collect your suitcase from your hotel and send it to Haneda. Ask your hotel front desk what is on offer.</li>'
      +'<li>Book ahead: bags usually need to reach the airport the day before, so ask when to hand yours over.</li>'
      +'<li>On departure day, show your receipt and ID at the counter, collect the bag, then go to check-in.</li>'
      +'<li>Haneda lists delivery counters in every terminal. Ask which one and its opening hours, especially for an early or late flight.</li>'
      +'<li>Keep your passport, medicines and valuables with you.</li></ul>'
      +'<p class="sm">Rules, prices and cut-off times change: confirm with the company.</p>';
  }
  function taxHTML(){
    return '<p class="n2">From <b>1 November 2026</b> you pay the full price, tax included, at the shop. You claim the tax back at the airport.</p>'
      +'<ul class="pl"><li>Applies when you spend <b>&yen;5,000 or more</b> (before tax) at one shop in one day.</li>'
      +'<li>Within <b>90 days</b> of buying, scan your passport at a <b>tax-free procedure terminal</b> before security, with your receipts and the items with you. Do not check the items in first.</li>'
      +'<li><b>Terminal 1</b> has no tax refund service. In Terminals 2 and 3 the procedure terminals are before the 3F security check, and Terminal 3&rsquo;s are open 24 hours.</li>'
      +'<li><b>Green</b> result: you are done. <b>Red</b> result: take the items to the customs inspection area.</li></ul>'
      +'<div class="tipbox">Finish this before you board. If you miss your flight, neither customs nor the airline pays you back. Queues are likely while the system is new, so allow extra time.</div>'
      +'<p class="sm">How the refund is paid is not covered in the official summary: ask at the kiosk or check your shop receipt. Sources: Haneda Airport and the Japan National Tourism Organization, checked 18 November 2026.</p>';
  }
  function earlyHTML(){
    return '<p class="n2">For an international flight, about <b>2 hours</b> before departure is a common guide. Your airline sets its own advice, so check your ticket.</p>'
      +'<ul class="pl"><li>Add the journey from central Tokyo: Haneda lists about <b>30 to 50 minutes</b> by train from stations such as Tokyo Station or Shinjuku.</li>'
      +'<li>Add time to reach the station, and a little extra.</li>'
      +'<li>Most international flights leave from Terminal 3, which has its own stations. For Terminal 1 or 2, add time to find your station and gates.</li>'
      +'<li>Shopped tax-free? Add time for the tax-free procedure terminal.</li></ul>'
      +'<div class="tipbox"><b>Example:</b> flight at 12:00. Be at the airport by 10:00. Leave central Tokyo by about 9:00.</div>'
      +'<p class="sm">Your airline decides when check-in opens and closes. Check your ticket.</p>';
  }
  var BEFORE=[['🚆','Getting to Haneda',gettingHTML],['📦','Luggage to the airport',sendOutHTML],['🧾','Tax refund',taxHTML],['⏰','How early to leave',earlyHTML]];
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
  [].forEach.call(dseg.children,function(b){ b.addEventListener('click',function(){ var w=b.getAttribute('data-d'); try{localStorage.setItem('hndDepSeg',w);}catch(e){} paintDep(w); }); });
  var dsv='before'; try{ var q=localStorage.getItem('hndDepSeg'); if(q==='air'||q==='before') dsv=q; }catch(e){}
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
    navigator.serviceWorker.register('/haneda-sw.js',{scope:'/haneda-pocket',updateViaCache:'none'})
      .then(function(){ return navigator.serviceWorker.ready; })
      .then(function(){ return caches.has('haneda-pocket-v4'); })
      .then(function(ok){ saved=!!ok; if(!saved){ setTimeout(function(){ caches.has('haneda-pocket-v4').then(function(k){ saved=!!k; paint(); }); },2500);} paint(); })
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
  function needed(){ return mobile&&!standalone&&flag('hndInstalled')!=='1'; }
  function refresh(){
    var n=needed(); strip.hidden=!n;
    $('instHow').hidden=!n; $('instDesk').hidden=mobile;
    if(standalone||flag('hndInstalled')==='1'){ $('install').hidden=true; }
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
  function markInstalled(){ flag('hndInstalled','1'); refresh(); }
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
    ['go','🚆','Tokyo Station?','これは東京駅に行きますか？','Kore wa Toukyou-eki ni ikimasu ka?','Does this go to Tokyo Station?'],
    ['go','📞','Call a taxi','タクシーを呼んでください。','Takushii o yonde kudasai.','Please call a taxi.'],
    ['go','📍','Take me here','この住所までお願いします。','Kono juusho made onegai shimasu.','Please take me to this address. Show the address on your phone.'],
    ['go','🛑','Stop here','ここで止めてください。','Koko de tomete kudasai.','Please stop here.'],
    ['air','🧳','Baggage claim','手荷物受取所はどこですか？','Tenimotsu uketorijo wa doko desu ka?','Where is baggage claim?'],
    ['air','🎫','Check-in','チェックインカウンターはどこですか？','Chekkuin kauntaa wa doko desu ka?','Where is the check-in counter?'],
    ['air','🛫','My gate','搭乗口はどこですか？','Toujouguchi wa doko desu ka?','Where is my boarding gate?'],
    ['air','💴','Money exchange','両替所はどこですか？','Ryougaejo wa doko desu ka?','Where can I exchange money?'],
    ['air','🚆','Train station','電車の駅はどこですか？','Densha no eki wa doko desu ka?','Where is the train station?'],
    ['air','🚌','Bus stop','バス乗り場はどこですか？','Basu noriba wa doko desu ka?','Where is the bus stop?'],
    ['air','🚕','Taxi stand','タクシー乗り場はどこですか？','Takushii noriba wa doko desu ka?','Where is the taxi stand?'],
    ['air','⏰','Missed my flight','飛行機に乗り遅れました。','Hikouki ni noriokuremashita.','I missed my flight.'],
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
  var ASKC=[['basics','Basics','👋'],['where','Where is&hellip;?','📍'],['shop','Shopping','🛍️'],['eat','Eating out','🍜'],['sights','Sights','🎡'],['go','Getting around','🚆'],['air','Airport','✈️'],['help','Help','🆘']];
  var askCat='basics'; try{ var sc=localStorage.getItem('hndAskCat'); if(sc&&ASKC.some(function(c){return c[0]===sc;})) askCat=sc; }catch(e){}
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
    b.addEventListener('click',function(){ askCat=c[0]; try{localStorage.setItem('hndAskCat',c[0]);}catch(e){} paintAsk(); });
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
    $('hnav1').appendChild(pill('pgnext','\\u2192','Phone numbers','Emergency, airport, help line',function(){ hslide(1); }));
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
    $('shareBtn').addEventListener('click',function(){ try{ navigator.share({title:'Haneda Pocket Guide',url:location.origin+location.pathname+'?src=share'}); }catch(e){} });
  }
  window.addEventListener('beforeinstallprompt',function(e){ e.preventDefault(); dp=e; });
  window.addEventListener('appinstalled',function(){ pgTrack('pg_installed',{via:'browser'}); markInstalled(); if(!inst.hidden) closeSheet(); });
  /*__PG_HOOKS__*/
  refresh();
  if(needed()&&!flag('hndIntro')&&AUTO_INSTALL_SHEET){ flag('hndIntro','1'); setTimeout(function(){ if(sheet.hidden&&inst.hidden){ instVia='auto'; openInst(); } },700); }
})();
</script>
</body>
</html>
"""
POCKET_HTML = (POCKET_HTML.replace("__CSS__", POCKET_CSS).replace("__FINDER_JSON__", json.dumps(FINDER_DATA, ensure_ascii=False))
               .replace("__PG_BOOT__", PG_BOOT).replace("/*__PG_HOOKS__*/", PG_HOOKS).replace("__SVG__", POCKET_SVG).replace("__GUIDE_URL__", URL))
if re.search(r"\b(India|Indian|INR|Rs\.?|rupee|lakh|Aadhaar|UPI|VFS|BLS)\b|₹", re.sub(r"<script[^>]*>.*?</script>", "", POCKET_HTML, flags=re.S)):
    die("neutral-rule violation in the pocket guide")

POCKET_SW = """/* Haneda Pocket Guide service worker. Bump V when the page changes shape. */
var V='haneda-pocket-v4';
var PAGE='/haneda-pocket';
var SHELL=[PAGE,'/haneda-pocket.webmanifest','/favicon-32.png','/images/haneda-icon-v2-192.png','/images/haneda-icon-v2-512.png','/images/haneda-icon-v2-maskable-512.png'];
self.addEventListener('install',function(e){
  e.waitUntil(caches.open(V).then(function(c){return c.addAll(SHELL);}).then(function(){return self.skipWaiting();}));
});
self.addEventListener('activate',function(e){
  e.waitUntil(caches.keys().then(function(ks){
    return Promise.all(ks.filter(function(k){return k.indexOf('haneda-pocket-')===0&&k!==V;}).map(function(k){return caches.delete(k);}));
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
    "name": "Haneda Pocket Guide",
    "short_name": "Haneda",
    "description": "A simple Haneda Airport helper that works offline.",
    "start_url": POCKET_PATH,
    "scope": POCKET_PATH,
    "display": "standalone",
    "background_color": "#1a1a3e",
    "theme_color": "#1a1a3e",
    "lang": "en",
    "icons": [
        {"src": "/images/haneda-icon-v2-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
        {"src": "/images/haneda-icon-v2-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
        {"src": "/images/haneda-icon-v2-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ],
}, indent=2) + "\n"
PUB = os.path.join(ROOT, "public")
for _ic in ("haneda-icon-v2-192.png", "haneda-icon-v2-512.png", "haneda-icon-v2-maskable-512.png", "haneda-apple-touch-v2-180.png"):
    if not os.path.isfile(os.path.join(PUB, "images", _ic)):
        die("pocket guide icon missing: public/images/" + _ic + " (the service worker would fail to install without it)")
for _name, _content in (("haneda-pocket.html", POCKET_HTML), ("haneda-sw.js", POCKET_SW), ("haneda-pocket.webmanifest", POCKET_MANIFEST)):
    _p = os.path.join(PUB, _name)
    _old = open(_p, encoding="utf-8").read() if os.path.isfile(_p) else None
    if _old != _content:
        open(_p, "w", encoding="utf-8").write(_content)
        changed.append("%s (%s bytes)" % (_name, len(_content.encode("utf-8"))))

# ---- link from the Japan guide (after the Narita sentence)
MARK = "haneda-airport-guide link"
jp = open(TEMPLATE, encoding="utf-8").read()
if MARK not in jp:
    anchor = re.search(r'(<!-- narita-' + r'airport-guide link -->\s*<p>.*?</p>)', jp, re.S)
    if not anchor:
        die("anchor for the Japan guide link (Narita sentence) not found: run the Narita generator first")
    add = ('\n\n<!-- %s -->\n<p>Landing at Haneda? Our <a href="/blog/%s">Haneda Airport guide</a> explains the terminals, the arrival steps, SIM and eSIM options, '
           'trains, monorail and buses to Tokyo, and airport facilities such as prayer rooms and nursing rooms.</p>') % (MARK, SLUG)
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
