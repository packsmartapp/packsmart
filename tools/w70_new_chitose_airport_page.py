#!/usr/bin/env python3
"""
w70: new page /blog/new-chitose-airport-guide + offline /new-chitose-pocket (neutral, plain-English airport guide for
New Chitose Airport, CTS, the airport for Sapporo). Built from the Ueno Station generator (w68): same template,
partner-block helpers, Sources list and Pocket Guide shell, with the airport's two terminals in place of station levels.

Run from the repo root (after w68):  python3 tools/w70_new_chitose_airport_page.py
Then, as for the other guides: w71 (Sapporo Station), the rest of the page generators, w44-w49 (pocket chain,
cross-links, hub, trip picker), w55, w56, w59 (Travel Essentials card), w64, w65, w66, w67 and w69 (read times).

Facts: ONLY from docs/research/sapporo-sources.md (the airport's own site www.hokkaido-airports.com, JR Hokkaido,
Hokkaido Chuo Bus and the Sapporo Tourist Association; checked 24 November 2026). Anything not in that file is left
out, or written as "We did not find this on the airport's pages. Please ask at an information center." (_NONE).
Where sources disagree the operator wins: JR's 33 / 37 / 43 minutes for the Airport Train, and about 70 minutes for
the bus (the bus timetables), not the airport's "about 1 hour 50 minutes". (first and last Airport Trains added 24 Nov 2026 from JR's station timetables),
ski-bus times, the walking time between terminals and toilet locations are not stated.

Partner blocks (no new programmes, no Klook, no hotel links): the eSIM tiles copied from the Japan guide (placement
id airalo-new-chitose) and a tours-and-tickets box with a search for Niseko skiing (gyg-new-chitose,
cmp ps-new-chitose-gyg). No luggage-storage callout (the existing tracked link is for Tokyo), no airport-transfer
or car-rental block (no checked pick-up location for New Chitose in those widgets yet). KLK stays empty.

What it does (idempotent):
  1. Builds public/blog/new-chitose-airport-guide.html from the site template taken from
     public/blog/japan-travel-packing-guide.html (head, CSS, nav, footer, tracking scripts) plus new body content.
     Hero: a plain dark colour, no photo (no suitable photo exists; see the research notes).
  2. Builds public/new-chitose-pocket.html (offline Pocket Guide), new-chitose-sw.js and
     new-chitose-pocket.webmanifest (cache new-chitose-pocket-v1; later scripts bump it; storage prefix "cts", as w44 expects).
  3. Adds one sentence linking to the new page in the Japan guide (marker: new-chitose-airport-guide link),
     right after the Ueno Station guide sentence that w68 adds.
  4. Adds the page to public/sitemap.xml and moves the Japan guide's lastmod forward (never back).
It does NOT touch public/travel-essentials.html (the hub card comes from w59).
Aborts without writing anything if an expected anchor is missing.
"""
import os, re, sys, json, html
from urllib.parse import quote

ROOT = os.getcwd()
BLOG = os.path.join(ROOT, "public", "blog")
SITEMAP = os.path.join(ROOT, "public", "sitemap.xml")
TEMPLATE = os.path.join(BLOG, "japan-travel-packing-guide.html")
OUT = os.path.join(BLOG, "new-chitose-airport-guide.html")
SITE = "https://www.packsmartapp.com"
SLUG = "new-chitose-airport-guide"
URL = "%s/blog/%s" % (SITE, SLUG)
TODAY = "2026-11-24"
READ_MIN = 10   # placeholder only: w69 sets the real read time from the words on the page

TITLE = "New Chitose Airport (CTS) Guide 2026: Terminals, Trains & Buses to Sapporo | PackSmart Blog"
H1 = "New Chitose Airport (CTS) Guide 2026: Terminals, Trains and Buses to Sapporo, and Winter Tips"
DESC = ("Plain-English New Chitose Airport guide: which terminal, the 2F walkway, "
        "the train and buses to Sapporo, ski buses, money, lockers and winter tips.")
KEYWORDS = ("New Chitose Airport guide, New Chitose Airport to Sapporo, CTS airport, Rapid Airport train, New Chitose airport bus, "
            "New Chitose international terminal, New Chitose domestic terminal, New Chitose Airport lockers, Niseko ski bus, Sapporo airport")

# ---- official sources (docs/research/sapporo-sources.md), checked 24 November 2026
CHECKED = "Checked 24 November 2026."
_A = "https://www.hokkaido-airports.com/en/new-chitose/"
SRC = {
    "fm": (_A + "floormap/", "New Chitose Airport: floor maps"),
    "fmdom": ("https://www.hokkaido-airports.com/ja/new-chitose/assets/pages/floormap/pdf/en_dom.pdf", "New Chitose Airport: Domestic Terminal floor guide (PDF, information as of 17 September 2026)"),
    "fmint": ("https://www.hokkaido-airports.com/ja/new-chitose/assets/pages/floormap/pdf/en_int.pdf", "New Chitose Airport: International Terminal floor guide (PDF, information as of 17 September 2026)"),
    "renov": (_A + "info/20261109-7624.html", "New Chitose Airport: notice on facility renovations (posted 9 November 2026)"),
    "hours": (_A + "service/", "New Chitose Airport: services and building opening hours"),
    "ajr": (_A + "access/jr/", "New Chitose Airport: access by JR"),
    "abus": (_A + "access/bus/", "New Chitose Airport: access by bus"),
    "infoc": (_A + "service/information/info-center/", "New Chitose Airport: information centers"),
    "tic": (_A + "service/information/tourist-info/", "New Chitose Airport: Hokkaido Foreign Tourist Information Center"),
    "fx": (_A + "service/money/currency-exchange/", "New Chitose Airport: currency exchange"),
    "atm": (_A + "service/money/bank/", "New Chitose Airport: ATMs and bank"),
    "sim": (_A + "service/internet-fax-copy/sim-card/", "New Chitose Airport: SIM cards"),
    "wifi": (_A + "service/internet-fax-copy/wifi/", "New Chitose Airport: Wi-Fi and phone rental"),
    "lan": (_A + "service/internet-fax-copy/lan/", "New Chitose Airport: free Wi-Fi"),
    "locker": (_A + "service/baggage/locker/", "New Chitose Airport: coin lockers and Baggage Port"),
    "bagroom": (_A + "service/baggage/baggage-checkroom/", "New Chitose Airport: baggage storage and delivery"),
    "deck": (_A + "service/other/deck/", "New Chitose Airport: observation deck"),
    "qa": (_A + "contact/qa/", "New Chitose Airport: FAQ"),
    "jrhome": ("https://www.jrhokkaido.co.jp/global/index.html", "JR Hokkaido: English home page (notices)"),
    "jrops": ("https://www3.jrhokkaido.co.jp/webunkou/index_en.html", "JR Hokkaido: Train Operation Information (English)"),
    "jrttcts": ("https://www3.jrhokkaido.co.jp/webunkou/timetable_en.html?id=246", "JR Hokkaido: New Chitose Airport departures, 24 Nov 2026"),
    "jrttspk": ("https://www3.jrhokkaido.co.jp/webunkou/timetable_en.html?id=091", "JR Hokkaido: Sapporo departures, Chitose Line, 24 Nov 2026"),
    "jrwifi": ("https://www.jrhokkaido.co.jp/global/english/travel/wifi.html", "JR Hokkaido: Wi-Fi guide"),
    "jrair": ("https://www.jrhokkaido.co.jp/global/english/travel/airport.html", "JR Hokkaido: Airport Train (New Chitose Airport, Sapporo, Otaru)"),
    "jrdis": ("https://www.jrhokkaido.co.jp/global/english/travel/airport_disruption.html", "JR Hokkaido: when train services are disrupted"),
    "jrfaq": ("https://www.jrhokkaido.co.jp/global/english/faq/faq10.html", "JR Hokkaido: FAQ on delays"),
    "jrinfo": ("https://www.jrhokkaido.co.jp/global/english/travel/info.html", "JR Hokkaido: JR Information Desk"),
    "jrpdf": ("https://www.jrhokkaido.co.jp/global/pdf/e-chitose.pdf", "JR Hokkaido: route from the International Terminal to the JR station (PDF, February 2024)"),
    "jrlock": ("https://www.jrhokkaido.co.jp/network/locker/locker.pdf", "JR Hokkaido: coin locker list (PDF, July 2026)"),
    "jrstn": ("https://www.jrhokkaido.co.jp/network/station/station.html", "JR Hokkaido: station search (New Chitose Airport station, map as of September 2026)"),
    "chuo": ("https://www.chuo-bus.co.jp/airport/timetable/?ope=det&n=34&o=2&t=14", "Hokkaido Chuo Bus: airport bus timetable, Chitose to Sapporo (summer timetable, updated 1 April 2026)"),
    "chuofeat": ("https://www.chuo-bus.co.jp/feature/airport/", "Hokkaido Chuo Bus: the airport bus (payment and frequency)"),
    "chuobeg": ("https://www.chuo-bus.co.jp/airport/beginner", "Hokkaido Chuo Bus: how to use the airport bus"),
    "chuobag": ("https://www.chuo-bus.co.jp/airport/baggage", "Hokkaido Chuo Bus: baggage on the airport bus"),
    "stv": ("https://www.sapporo.travel/en/info/about/transportation/", "Sapporo Tourist Association: transportation"),
    "stvnews": ("https://www.sapporo.travel/en/news/important-information-for-travelers-to-sapporo/", "Sapporo Tourist Association: important information for travelers (17 December 2025)"),
    "safe": ("https://hokkaido-safe-travel.mlit.go.jp/", "Hokkaido travel safety information (Hokkaido District Transport Bureau)"),
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


airalo = block("airalo-japan").replace("airalo-japan", "airalo-new-chitose")
_a = "Install it before you fly, switch it on when you land. No airport SIM queue."
if _a not in airalo:
    die("airalo tagline not found")
# the Japan guide's tagline ("before you fly ... when you land") fits an airport, so it stays as it is
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
    ("How do I get from New Chitose Airport to Sapporo?",
     "By JR train or by bus. JR Hokkaido's Airport Train leaves from JR New Chitose Airport Station, on B1F under the Domestic Terminal. "
     "JR gives six trains an hour between 9:00 and 16:00, and 33 minutes for the fastest (the Special Rapid). "
     "The airport buses to Sapporo city centre take about 70 minutes to Sapporo Station on the bus company's timetable."),
    ("How long is the train from New Chitose Airport to Sapporo?",
     "JR Hokkaido gives the fastest times as 33 minutes on the Special Rapid, 37 minutes on the Rapid and 43 minutes on the Semi-Rapid."),
    ("Which terminal am I in at New Chitose Airport?",
     "International flights use the International Terminal Building, on the west side. Domestic flights use the Domestic Terminal Building, on the east side. "
     "A connecting corridor joins them. The JR station is under the Domestic Terminal, on B1F."),
    ("How do I walk between the international and domestic terminals?",
     "Use the 2F Connecting Corridor, which has moving walkways. Part of the 3F passage in the connecting facility is closed for construction "
     "from 2 September 2026 until about the end of June 2027, and during that time you cannot go between the terminals on 3F. "
     "The airport does not state a walking time, so allow extra time with luggage."),
    ("Where do the buses to Sapporo leave from?",
     "The airport lists the Sapporo city centre buses at stops 14 and 22 outside the Domestic Terminal (1F), and stop 84 at the International Terminal. "
     "The bus company says the buses leave on time even if flights are delayed."),
    ("Can I use Suica or another IC card at New Chitose Airport?",
     "On the JR Airport Train to Sapporo, yes: JR Hokkaido lists Suica, PASMO, Kitaca and other IC cards. Not beyond Otaru, for Yoichi, Kutchan or Niseko. "
     "On the airport buses, Hokkaido Chuo Bus says transport IC cards work on its own buses only, not on Hokuto Kotsu buses."),
    ("Is there a bus from New Chitose Airport to Niseko or Furano?",
     "The airport's bus page lists a ski bus to Niseko and Rusutsu from domestic stop 12, in winter only, and a bus to Furano from domestic stop 23. "
     "We could not read the timetables, so check the bus company's own page before you travel."),
    ("Can I stay overnight at New Chitose Airport?",
     "The airport says you may not stay in the terminal after it closes, except in the accommodation facilities. "
     "The Domestic Terminal is open 5:00 to 23:30 and the International Terminal 5:00 to 21:00. "
     "The New Chitose Airport Onsen on Domestic 4F is open 23 hours, from 10:00 to 9:00 the next morning."),
    ("What happens at New Chitose Airport when it snows?",
     "For your flight, the airport says to contact your airline. For delays and transport disruption, it points to the airlines, "
     "the transport operators and the Hokkaido District Transport Bureau's Hokkaido travel safety information. "
     "If trains stop, JR Hokkaido lists the airport bus and taxis as alternatives, but says they can get extremely crowded."),
    ("Where can I change money or use an ATM at New Chitose Airport?",
     "International 2F has a currency exchange counter (8:30 to 19:00) and a Seven Bank ATM (6:00 to 21:00) that takes overseas cards. "
     "The Domestic Terminal has exchange counters on 1F and ATMs on its north and south sides, including Seven Bank and Japan Post Bank, which take overseas cards."),
    ("Can I send my luggage to my hotel in Sapporo?",
     "Yes, to designated hotels in Sapporo's Chuo Ward. The airport lists same-day delivery from Domestic 1F (near Arrival Gate 4, accepted 8:00 to 14:30, "
     "and near Arrival Gate 2, 8:00 to 14:30). The International 2F baggage counter (9:00 to 18:00) also lists same-day delivery."),
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
    "about": {"@type": "Airport", "name": "New Chitose Airport", "iataCode": "CTS"},
}
ld_crumbs = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE},
        {"@type": "ListItem", "position": 2, "name": "Travel Essentials", "item": SITE + "/travel-essentials"},
        {"@type": "ListItem", "position": 3, "name": "New Chitose Airport Guide", "item": URL},
    ],
}


def ld(obj):
    return '<script type="application/ld+json">\n%s\n</script>' % json.dumps(obj, ensure_ascii=False)


TOC = [
    ("one-page", "New Chitose Airport on one page"),
    ("terminals", "Which terminal? Domestic and International, floor by floor"),
    ("between", "Between the terminals: the 2F corridor (3F closed)"),
    ("train", "To Sapporo by train: the Airport Train"),
    ("bus", "To Sapporo by bus"),
    ("ski", "Ski buses: Niseko, Rusutsu and Furano"),
    ("money", "Money: currency exchange and ATMs"),
    ("connected", "Getting online: SIM machines, Wi-Fi and eSIM"),
    ("luggage", "Lockers, big bags and hotel delivery"),
    ("finder", "Find it fast: by terminal"),
    ("hours", "Opening hours, hotels, onsen and the observation deck"),
    ("winter", "Snow, delays and cancelled flights"),
    ("help", "Information and help"),
    ("leaving", "Leaving from New Chitose: a checklist"),
    ("faq", "FAQ"),
    ("about-this-guide", "About this guide and change log"),
]
# ---- "What do you need first?" tiles + a quick-jump bar that appears once you scroll (as w42)
TOC_SHORT = {
    "one-page": "On one page", "terminals": "Terminals", "between": "Between terminals", "train": "Train", "bus": "Bus",
    "ski": "Ski buses", "money": "Money", "connected": "Get online", "luggage": "Luggage", "finder": "Find it fast",
    "hours": "Hours", "winter": "Snow", "help": "Help", "leaving": "Leaving", "faq": "FAQ", "about-this-guide": "About",
}
TOC_TILES = [
    ("train", "&#128646;", "Train to Sapporo", "33 min fastest, B1F"),
    ("bus", "&#128652;", "Bus to Sapporo", "About 70 min"),
    ("between", "&#128694;", "Between terminals", "2F corridor, 3F closed"),
    ("terminals", "&#9992;&#65039;", "Which terminal?", "Domestic or International"),
    ("money", "&#128180;", "Money", "Exchange and ATMs"),
    ("connected", "&#128246;", "Get online", "SIM, Wi-Fi, eSIM"),
    ("luggage", "&#129523;", "Luggage", "Lockers, hotel delivery"),
    ("winter", "&#10052;&#65039;", "Snow and delays", "What to do"),
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


DG_H = 756
_DG_SVG = (
    '<svg id="ctsDiagram" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 %d" role="img" aria-labelledby="ctsT ctsD" font-family="Arial, Helvetica, sans-serif">' % DG_H
    + '<title id="ctsT">New Chitose Airport at a glance</title>'
    '<desc id="ctsD">New Chitose Airport has two terminal buildings joined by a connecting corridor. International Terminal (west side): '
    '4F hotel entrance, 3F departures, 2F arrivals with currency exchange, ATMs and SIM machines, 1F buses (stop 84) and taxis. '
    'Connecting corridor: 2F open, with moving walkways; part of the 3F passage is closed until about the end of June 2027. '
    'Domestic Terminal (east side): 4F onsen and observation deck, 3F food, 2F departures and shops, 1F arrivals and buses (stops 14 and 22). '
    'B1F: JR New Chitose Airport Station, Airport Train to Sapporo, 33 minutes at the fastest.</desc>'
    '<rect width="480" height="%d" fill="#fff"/>' % DG_H
    + '<text x="240" y="38" font-size="26" font-weight="700" text-anchor="middle" fill="#0f0f23">New Chitose Airport</text>'
    '<text x="240" y="64" font-size="17" text-anchor="middle" fill="#555">Two terminals, one corridor, JR under Domestic</text>'
    '<rect x="24" y="84" width="432" height="192" rx="18" fill="#EEF0FB" stroke="#34346e" stroke-width="2"/>'
    '<text x="48" y="120" font-size="23" font-weight="700" fill="#0f0f23">International Terminal</text>'
    '<text x="432" y="120" font-size="15" text-anchor="end" fill="#555">west</text>'
    + _dg_pill(136, "3F Departures &#183; 4F hotel", "#fff", "#34346e", "#1a1a3e", "700")
    + _dg_pill(180, "2F Arrivals: exchange, ATM, SIM", "#fff", "#34346e", "#1a1a3e")
    + _dg_pill(224, "1F Buses (stop 84) and taxis", "#fff", "#34346e", "#1a1a3e")
    + '<rect x="24" y="286" width="432" height="144" rx="18" fill="#FFF6E5" stroke="#b45309" stroke-width="2"/>'
    '<text x="48" y="322" font-size="23" font-weight="700" fill="#0f0f23">Connecting corridor</text>'
    + _dg_pill(338, "2F: open, moving walkways", "#fff", "#0a8f78", "#0a6b5a", "700")
    + _dg_pill(382, "3F: closed to about end June 2027", "#FDECEF", "#E94560", "#a3243b", "700")
    + '<rect x="24" y="440" width="432" height="188" rx="18" fill="#E6FAF5" stroke="#0a8f78" stroke-width="2"/>'
    '<text x="48" y="476" font-size="23" font-weight="700" fill="#0f0f23">Domestic Terminal</text>'
    '<text x="432" y="476" font-size="15" text-anchor="end" fill="#555">east</text>'
    + _dg_pill(492, "4F onsen &#183; 3F food &#183; 2F Departures", "#fff", "#0a8f78", "#0a6b5a")
    + _dg_pill(536, "1F Arrivals, buses (stops 14, 22)", "#fff", "#0a8f78", "#0a6b5a", "700")
    + _dg_pill(580, "Go down to B1F for JR trains", "#fff", "#0a8f78", "#0a6b5a")
    + '<rect x="24" y="638" width="432" height="80" rx="18" fill="#E8F1FE" stroke="#2563EB" stroke-width="2"/>'
    '<text x="48" y="672" font-size="23" font-weight="700" fill="#0f0f23">B1F: JR station</text>'
    '<text x="48" y="700" font-size="17" fill="#0f0f23">Airport Train to Sapporo, 33 min fastest</text>'
    '<text x="240" y="744" font-size="14" text-anchor="middle" fill="#777">Simplified, not to scale. packsmartapp.com</text></svg>'
)

DIAGRAM = '<figure class="ps-fig" id="at-a-glance">\n' + _DG_SVG + """
<button type="button" class="ps-btn2" id="ctsDl">Download the diagram (PNG)</button>
</figure>
<script>
(function(){
  var b=document.getElementById('ctsDl'); if(!b) return;
  b.addEventListener('click',function(){
    try{
      var svg=document.getElementById('ctsDiagram');
      var xml=new XMLSerializer().serializeToString(svg);
      var img=new Image();
      img.onload=function(){
        var c=document.createElement('canvas'); c.width=960; c.height=""" + str(2 * DG_H) + """;
        var x=c.getContext('2d'); x.fillStyle='#fff'; x.fillRect(0,0,c.width,c.height); x.drawImage(img,0,0,c.width,c.height);
        c.toBlob(function(bl){
          var a=document.createElement('a'); a.href=URL.createObjectURL(bl); a.download='new-chitose-airport-at-a-glance.png';
          document.body.appendChild(a); a.click(); document.body.removeChild(a);
        },'image/png');
      };
      img.src='data:image/svg+xml;charset=utf-8,'+encodeURIComponent(xml);
    }catch(e){ window.print(); }
  });
})();
</script>"""
_NONE = "We did not find this on the airport's pages. Please ask at an information center."
_BOTH = lambda s: {"T1": s, "T2": s}
FINDER_DATA = {
    "terms": [["T1", "International Terminal"], ["T2", "Domestic Terminal"]],
    "items": [
        ["money", "Money: exchange and ATMs", {
            "T1": "2F (arrivals): a currency exchange counter, 8:30 to 19:00, an automatic exchange machine, and ATMs: Seven Bank (6:00 to 21:00, takes overseas cards) and AEON Bank. 3F (departures): an exchange counter on the north side, 9:30 to 16:00, and ATMs. Hours can change with flight times.",
            "T2": "1F (arrivals): currency exchange counters in the arrival lobby, ANA side 7:15 to 20:00 and JAL side 9:00 to 17:00, and automatic exchange machines on the north and south sides. ATMs on the north and south sides: Seven Bank (6:20 to 23:00) and Japan Post Bank take overseas cards, as do AEON Bank and Lawson Bank."}],
        ["phone", "SIM and Wi-Fi", {
            "T1": "Prepaid SIM vending machines on 2F and 3F. Mobile Wi-Fi and phone rental counters on 2F (for example 9:00 to 19:00, or 9:00 to 17:00), and one on 3F. Free Wi-Fi in the terminal, but not in the connecting corridor.",
            "T2": "Prepaid SIM vending machines on 1F. Mobile Wi-Fi and phone rental counters on 1F (one is open 9:00 to 18:00, closed 13:00 to 14:00). Free Wi-Fi in the terminal, but not in the connecting corridor."}],
        ["lockers", "Lockers", {
            "T1": "The airport lists coin lockers on International 1F to 4F and in the connecting corridor (1F to 3F). Up to 3 days. The exact spots are on the airport's online map, so follow the signs.",
            "T2": "The airport lists coin lockers on Domestic B1F to 4F, and JR has coin lockers in the JR station (B1F). Up to 3 days. Too big for a locker? The Baggage Port takes large cases and strollers (cashless: IC card or QR code payment)."}],
        ["bags", "Bag storage and hotel delivery", {
            "T1": "2F baggage counter, 9:00 to 18:00: storage and same-day delivery. 3F: baggage wrapping, 11:00 to 14:00.",
            "T2": "1F baggage counter, 7:00 to 20:00: storage, home delivery and porters (skis, snowboards and golf bags count as large). 2F counter, 7:30 to 20:00. Same-day delivery to designated hotels in Sapporo's Chuo Ward from 1F: near Arrival Gate 4 (accepted 8:00 to 14:30) and near Arrival Gate 2 (8:00 to 14:30)."}],
        ["info", "Information", {
            "T1": "Information centers on 1F (curbside lobby), 2F (arrival lobby) and 3F (departure lobby, north and south, and inside the boarding area). The Hokkaido Foreign Tourist Information Center is on 2F, 8:00 to 20:00, in English, Chinese and Korean. Hotel bookings in Hokkaido: 2F arrival lobby.",
            "T2": "Information centers on 1F in front of Arrival Gates 2, 4 and 5, on 2F in the departure lobby (north and south) and in Center Plaza. They open with the flights. Hotel bookings in Hokkaido: 1F, at Arrival Gates 2 and 5."}],
        ["help", "Wheelchair and help", _BOTH("The information centers lend wheelchairs free of charge. Ask at any information center, or call the airport on 0123-23-0111 (7:00 to 23:00, Japanese and English). In an emergency, call 119.")],
        ["prayer", "Prayer room", {
            "T1": "A prayer room on 2F, the arrivals floor (airport floor guide). There is also a dressing room on 2F.",
            "T2": "We did not find a prayer room in the Domestic Terminal on the airport's floor guide. Please ask at an information center."}],
        ["rest", "Hotels and onsen", {
            "T1": "Portom International Hokkaido, a hotel on 4F. Enter by the escalator on the 3F departure lobby side, or by the hotel lift from 1F to 3F.",
            "T2": "Air Terminal Hotel, by Arrival Gate 5 (its own lift, 1F to 5F). New Chitose Airport Onsen on 4F: open 23 hours, 10:00 to 9:00 the next morning, last entry 7:30. A late-night surcharge applies after 1:00. Between 23:00 and 5:00, use the 24-hour lift (1F to 4F)."}],
        ["food", "Shops and food", {
            "T1": "Hokkaido Food Hall on 3F (departures).",
            "T2": "Gourmet World and the food court on 3F. Shopping World on 2F."}],
        ["toilet", "Toilets", _BOTH("We did not find toilet locations in words on the airport's pages. Follow the signs, or ask at an information center.")],
        ["unwell", "Feeling unwell", _BOTH("Tell airport staff, or go to an information center. In an emergency, call 119.")],
    ],
}
_ORDER = ["money", "phone", "lockers", "bags", "info", "help", "prayer", "rest", "food", "toilet", "unwell"]
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
<noscript><p>This tool needs JavaScript. The sections above have the same facts.</p></noscript>
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
    var s=document.createElement('strong'); s.textContent=it[1]+': '+tn; rEl.appendChild(s);
    rEl.appendChild(document.createElement('br'));
    rEl.appendChild(document.createTextNode(txt?txt:'We did not find this on the airport\\'s pages. Please ask at an information center.'));
    var sm=document.createElement('small'); sm.textContent='From the New Chitose Airport website and its floor guides (information as of 17 September 2026), checked 24 November 2026. Counters and hours can change. If you cannot find it, ask at an information center.'; rEl.appendChild(sm);
  }
})();
</script>"""
FINDER = FINDER.replace("__FINDER_JSON__", json.dumps(FINDER_DATA, ensure_ascii=False))

LUGGAGE = """<h2 id="luggage">Lockers, big bags and hotel delivery</h2>
<p>Skiing, or carrying winter gear? The airport has lockers on almost every floor, a place for bags too big for a locker, and counters that send bags on to Sapporo.</p>
<ul>
<li><strong>Coin lockers.</strong> Large, medium and small, on Domestic B1F to 4F, International 1F to 4F and in the connecting corridor (1F to 3F). Up to 3 days; for longer, use the baggage storage counters. The airport says lockers are charged by the 12 hours. The exact spots are on the airport's online map, so follow the signs.</li>
<li><strong>Too big for a locker?</strong> The Baggage Port takes large carry-on cases and strollers, unlocked with your IC card, for up to 3 days. It is cashless: transport IC cards and QR code payments.</li>
<li><strong>JR lockers.</strong> JR also has coin lockers in the JR station on B1F (JR's locker list, July 2026).</li>
<li><strong>Baggage counters, Domestic Terminal.</strong> 1F, 7:00 to 20:00: storage, home delivery and porters. Golf bags, skis and snowboards count as large. 2F, 7:30 to 20:00.</li>
<li><strong>Baggage counters, International Terminal.</strong> 2F, 9:00 to 18:00: storage and same-day delivery. Baggage wrapping on 3F, 11:00 to 14:00.</li>
<li><strong>Same-day delivery to your Sapporo hotel.</strong> To designated hotels in Sapporo's Chuo Ward, from Domestic 1F: near Arrival Gate 4 (open 8:00 to 20:00; same-day hotel delivery accepted 8:00 to 14:30) and near Arrival Gate 2 (8:00 to 14:30). Ask whether your hotel is on the list.</li>
<li><strong>On the bus.</strong> Big bags go in the trunk. Hokkaido Chuo Bus takes bags under 30 kg, under 0.25 m&sup3; and under 2 m long.</li>
<li><strong>On the train.</strong> JR's limit on the Airport Train: within 250 cm in total (2 m at most in length), up to 2 items, each up to 30 kg. Some items may not be allowed.</li>
</ul>
""" + sources(["locker", "bagroom", "jrlock", "chuobag", "jrair"], "Hours can change with flight times.")

HELP = """<h2 id="help">Information and help</h2>
<p>You do not have to cope alone. Asking early is easier than struggling, especially in snow.</p>
<ul>
<li><strong>Information centers.</strong> Domestic Terminal: 1F in front of Arrival Gates 2, 4 and 5; 2F departure lobby (north and south) and Center Plaza. International Terminal: 1F curbside lobby, 2F arrival lobby, 3F departure lobby (north and south) and inside the 3F boarding area. The airport says they open in line with the flights. They give flight, transport and Hokkaido tourist information and lend wheelchairs free of charge.</li>
<li><strong>Hokkaido Foreign Tourist Information Center.</strong> International Terminal 2F, 8:00 to 20:00, all year. Help in English, Chinese and Korean (Thai, Vietnamese, Portuguese and Spanish through a three-way interpreter service): travel advice, sightseeing and transport, and pointers to places to stay, duty-free shops, car rental and Wi-Fi.</li>
<li><strong>Hotel bookings in Hokkaido.</strong> At the information centers at Domestic 1F, Arrival Gates 2 and 5, and International 2F, arrival lobby.</li>
<li><strong>JR Information Desk.</strong> On B1F by the JR ticket gates. JR lists help in English, Chinese and Korean, rail passes and tickets, 8:30 to 19:00 (hours from a February 2024 JR leaflet, so check).</li>
<li><strong>Airport phone line.</strong> 0123-23-0111, 7:00 to 23:00, all year, in Japanese and English (it starts with an automated voice menu).</li>
<li><strong>Prayer room.</strong> International Terminal 2F, on the airport's floor guide. We did not find one in the Domestic Terminal.</li>
<li><strong>Moving walkways.</strong> The airport says the connecting corridor has moving walkways for people who find walking difficult.</li>
<li><strong>Emergency.</strong> Call 119 for an ambulance or fire, 110 for the police.</li>
</ul>
""" + sources(["infoc", "tic", "qa", "jrinfo", "jrpdf", "fmint", "ajr"], "Counters and hours can change.")

ABOUT = """<div class="ps-about" id="about-this-guide">
<h2>About this guide</h2>
<p>Written by PackSmart. Airport details were checked on 24 November 2026 against the New Chitose Airport website and its floor guides, JR Hokkaido, Hokkaido Chuo Bus and the Sapporo Tourist Association. Where an official page did not tell us something, for example the first and last Airport Train, the ski-bus times, the walking time between the terminals or where the toilets are, we say so instead of guessing. The bus times come from the summer 2026 timetable, which was still the current one on 24 November 2026. Spotted something out of date? <a href="/contact">Tell us</a> and we will fix it.</p>
<ul>
<li><strong>24 Nov 2026:</strong> first version, with the one-page card, the terminals floor by floor, the 3F corridor closure, the Airport Train and the buses to Sapporo, ski buses, money, getting online, lockers and hotel delivery, the find-it tool, opening hours, winter and delays, help and a leaving checklist.</li>
</ul>
</div>"""


def _card(title, text, slug, tag):
    return ('        <div class="related-card">\n            <div class="related-card-body">\n                <h4>%s</h4>\n                <p>%s</p>\n'
            '                <a href="https://www.packsmartapp.com%s">Read More <span class="related-arrow">&rarr;</span></a>\n                <div class="related-tag">%s</div>\n            </div>\n        </div>\n') % (title, text, slug, tag)


RELATED = ('<div class="related-posts">\n    <h3>Related Guides</h3>\n    <div class="related-grid">\n'
    + _card("Sapporo Station Guide 2026", "West and East gates during the Shinkansen works, the subway to Odori and Susukino, lockers and the Snow Festival.", "/blog/sapporo-station-guide", "Station Guide")
    + _card("Japan Travel and Packing Guide 2026", "What to pack, rail passes, etiquette and a budget breakdown for a first trip to Japan.", "/blog/japan-travel-packing-guide", "Destination Guide")
    + _card("Haneda Airport Guide 2026", "Flying on from Tokyo? Terminals, arrival steps, SIM and the trains, monorail and buses.", "/blog/haneda-airport-guide", "Airport Guide")
    + '    </div>\n</div>')

# no photo: a plain dark colour hero (no suitable photo exists; docs/research/sapporo-sources.md)
HERO_URL = None

WARN_CSS = """<style>
.ps-warn{background:#FDECEF;border:2px solid #E94560;border-radius:14px;padding:16px 18px;margin:20px 0;line-height:1.55}
.ps-warn strong.h{display:block;font-size:1.12rem;color:#a3243b;margin:0 0 6px}
.ps-warn p{margin:0 0 8px}
.ps-warn p:last-child{margin:0}
</style>"""

CARD = """<div class="ps-card" id="one-page">
<h2>New Chitose Airport on one page</h2>
<ul>
<li><strong>Two terminals:</strong> International flights use the International Terminal (west), domestic flights the Domestic Terminal (east).</li>
<li><strong>Between them:</strong> the <strong>2F</strong> Connecting Corridor. Part of the 3F passage is closed until about the end of June 2027.</li>
<li><strong>Train to Sapporo:</strong> JR New Chitose Airport Station, B1F under the Domestic Terminal. Fastest 33 minutes (JR). Car 4 is the reserved &ldquo;U seat&rdquo; car.</li>
<li><strong>Bus to Sapporo:</strong> Domestic 1F stops 14 and 22, International stop 84. About 70 minutes to Sapporo Station. Buses leave on time even if your flight is late.</li>
<li><strong>Money:</strong> International 2F exchange counter (8:30 to 19:00) and a Seven Bank ATM that takes overseas cards (6:00 to 21:00).</li>
<li><strong>Buildings open:</strong> Domestic 5:00 to 23:30, International 5:00 to 21:00. No staying overnight except in the airport hotels.</li>
<li><strong>Snow or a cancelled flight?</strong> Contact your airline, and check Hokkaido travel safety information.</li>
<li><strong>Help:</strong> information centers in both terminals. Airport line 0123-23-0111 (7:00 to 23:00). Emergency: 119.</li>
</ul>
<div class="ps-qr ps-qr-screen">__QR_SCREEN__<p><strong>Want it on your phone?</strong> Point your phone camera at this code. It opens the free New Chitose Airport Pocket Guide, which works without internet once opened.<span class="u">packsmartapp.com/new-chitose-pocket</span></p></div>
<div class="ps-qr ps-qr-print">__QR_PRINT__<p><strong>Free New Chitose Airport Pocket Guide.</strong> Point your phone camera at this code. Open it once with signal and it works without internet.<span class="u">packsmartapp.com/new-chitose-pocket</span></p></div>
<button type="button" class="ps-print-btn" onclick="window.print()">Print this card</button>
</div>"""

TERMINALS = """<h2 id="terminals">Which terminal? Domestic and International, floor by floor</h2>
<p>New Chitose has two terminal buildings joined by a connecting facility: the Domestic Terminal on the east side and the International Terminal on the west side. Your ticket and the departure boards tell you which one you need. This is how the airport's floor guide (information as of 17 September 2026) lays them out.</p>
<div class="ps-scroll">
<table class="checklist-table">
<thead><tr><th>Floor</th><th>International Terminal</th><th>Domestic Terminal</th></tr></thead>
<tbody>
<tr><td><strong>4F</strong></td><td>Gate lounge; hotel entrance</td><td>Oasis Park; New Chitose Airport Onsen; observation deck (closed December to March)</td></tr>
<tr><td><strong>3F</strong></td><td><strong>Departures</strong>: airline counters A to D, passport control, Hokkaido Food Hall</td><td>Gourmet World and the food court</td></tr>
<tr><td><strong>2F</strong></td><td><strong>Arrivals</strong>: immigration, customs, baggage claim, tourist information, ATMs, prayer room</td><td><strong>Departures</strong> and gate lounge; Shopping World; Center Plaza</td></tr>
<tr><td><strong>1F</strong></td><td>Bus and taxi area, bus counter, car rental, hotel entrance</td><td><strong>Arrivals</strong> and baggage claim; bus counters and bus stops; car rental</td></tr>
<tr><td><strong>B1F</strong></td><td>-</td><td>JR New Chitose Airport Station (platforms on B2F)</td></tr>
</tbody>
</table>
</div>
<ul>
<li><strong>Domestic arrivals by airline.</strong> The floor guide shows Arrival Gates 1 to 3 for ANA, AIR DO, IBEX and Peach, Gate 4 for JAL, and Gate 5 for JAL, SKYMARK, FDA, Jetstar and Spring Japan.</li>
<li><strong>Domestic 1F notices.</strong> The airport says part of the Arrivals Lobby cannot be reached, so use the outside walkway, or go up to 2F by escalator or lift. There is no way between the Main and Center buildings on 1F, because that area is a road for vehicles; go via the 2F Departure Lobby.</li>
<li><strong>Taxis.</strong> The Sapporo Tourist Association lists two taxi stands outside the Domestic Terminal exits and one outside the International Terminal exit.</li>
</ul>
""" + sources(["fm", "fmdom", "fmint", "stv"], "Floors and counters can change, so follow the signs.")

BETWEEN = """<h2 id="between">Between the terminals: the 2F corridor (3F closed)</h2>
<div class="ps-warn" role="note"><strong class="h">&#9888;&#65039; The 3F passage between the terminals is closed until about the end of June 2027</strong>
<p>The airport's notice (posted 9 November 2026): because of construction, part of the 3rd-floor passage in the connecting facility is closed, and you cannot go between the Domestic and International Terminals on 3F. The closure runs from 2 September 2026 to the end of June 2027 (the airport says this end date is tentative).</p>
<p><strong>Use the 2F Connecting Corridor.</strong> It has moving walkways, signed &ldquo;To Domestic Terminal Building&rdquo; and &ldquo;To International Terminal Building&rdquo;.</p></div>
<ul>
<li><strong>Landed on an international flight and taking the train?</strong> Arrivals are on International 2F. Walk the 2F corridor to the Domestic Terminal, carry on past the souvenir shops to the lift, and go down to B1F for JR. That is JR's own route (its February 2024 leaflet).</li>
<li><strong>Flying out internationally from the JR station?</strong> Go up to the Domestic Terminal 2F, walk the corridor to the International Terminal, then up to 3F for departures.</li>
<li><strong>How far?</strong> The airport does not state a walking time. JR's leaflet gives the walkway as 240 metres in its text and 300 metres on its map, so think of it as a few hundred metres and allow extra time with luggage or children.</li>
<li><strong>Corridor hours.</strong> 5:00 to 23:30.</li>
<li><strong>No free Wi-Fi in the corridor.</strong> The airport's free Wi-Fi covers both terminals, but not the connecting facilities.</li>
</ul>
""" + sources(["renov", "fmint", "jrpdf", "ajr", "hours", "qa"], "Construction dates can change, so follow the signs.")

TRAIN = """<h2 id="train">To Sapporo by train: the Airport Train</h2>
<p>JR Hokkaido runs the &ldquo;Airport Train&rdquo; (the Rapid Airport) straight from the airport to Sapporo, and some trains go on to Otaru. JR New Chitose Airport Station (AP15) is on B1F of the Domestic Terminal; the ticket gates and the JR Information Desk are on B1F, and the platforms on B2F.</p>
<ul>
<li><strong>How often and how fast.</strong> JR: &ldquo;six Airport Trains per hour between 9:00 and 16:00 from New Chitose Airport to Sapporo&rdquo;: one Special Rapid (fastest 33 minutes), three Rapid trains (fastest 37 minutes) and two Semi-Rapid trains (fastest 43 minutes). Fastest to Otaru: 73 minutes.</li>
<li><strong>Stops.</strong> Minami-Chitose (H14) and Shin-Sapporo (H05) for every type; Chitose (H13) for the Rapid and Semi-Rapid; then Sapporo (01). Teine, Minami-Otaru and Otaru for the trains that go on.</li>
<li><strong>Seats.</strong> Cars 1 to 3 and 5 to 6 are non-reserved: no booking needed, and you can board any Airport Train that day. Car 4 is the reserved &ldquo;U seat&rdquo; car (43 seats): you need a reserved-seat ticket as well as the fare, and you cannot enter car 4 without one.</li>
<li><strong>IC cards work.</strong> JR lists Suica, PASMO, TOICA, manaca, ICOCA, PiTaPa, SUGOCA, nimoca, Hayakaken and Kitaca. Not for Yoichi, Kutchan or Niseko: buy a ticket at the station first.</li>
<li><strong>Paper tickets.</strong> The ticket machines take cash only; the reserved-seat machine and the ticket counter take cash and credit cards. No QR code payments. A ticket is for one ride: leave the gates on the way and you need a new one.</li>
<li><strong>Passport-reader ticket machines.</strong> JR Hokkaido has posted a notice (8 October 2026) with important notes on its ticket machines with passport readers at Sapporo and New Chitose Airport stations. We did not read it, so check it on JR&rsquo;s English home page before you rely on those machines.</li>
<li><strong>IC cards elsewhere.</strong> JR&rsquo;s English home page also notes that IC cards can be used only at some stations, so check before travelling beyond the Airport Train route.</li>
<li><strong>Wi-Fi on board.</strong> JR Hokkaido says it provides Wi-Fi on the Airport Train cars and at stations.</li>
<li><strong>Booked a reserved seat online?</strong> JR says reserved-seat e-tickets do not open the gates: go through with an IC card or a paper fare ticket.</li>
<li><strong>Luggage.</strong> Within 250 cm in total (2 m at most in length), up to 2 items, each up to 30 kg.</li>
<li><strong>Ticket office.</strong> 6:30 to 22:00. Reserved-seat machines from 6:30 until the last train. Tour counter 9:00 to 17:30.</li>
<li><strong>First and last trains.</strong> JR Hokkaido&rsquo;s timetable for 24 November 2026 (a weekday): from New Chitose Airport, the first train to Sapporo is the Rapid Airport at 6:38 (Sapporo 7:18), and the last is the Special Rapid Airport at 23:21 (Sapporo 23:59). From Sapporo to the airport, the first is the Rapid Airport at 5:50 (airport 6:28), and the last is a local train at 22:25, which stops everywhere and reaches the airport at 23:12. Timetables change, so check JR&rsquo;s departures the day before.</li>
<li><strong>Going on to Hakodate, Noboribetsu, Tomamu or Kushiro?</strong> Change at Minami-Chitose, where the limited express trains leave from the same platform. JR says all seats on those limited expresses are reserved.</li>
<li><strong>Going on to Otaru from Sapporo?</strong> JR says trains for &ldquo;Teine&rdquo; or &ldquo;Hoshimi&rdquo; do not continue to Otaru.</li>
</ul>
<div class="tip-box"><strong>If the trains stop.</strong> JR asks you to check the boards and announcements (some are only in Japanese, so use a translation app) and to consider other transport: the airport bus (about 70 to 90 minutes) or a taxi (about 60 minutes). It warns that buses can get extremely crowded when trains are cancelled, and that times grow or services stop in bad weather. With a paper ticket, a cancelled trip is refunded in full, and the station can give you a delay certificate. JR says it does not pay for meals, other transport or hotels when trains are late or stopped.</div>
<p>Arriving in Sapporo? Our <a href="/blog/sapporo-station-guide">Sapporo Station guide</a> covers the gates during the Shinkansen works, the subway to Odori and Susukino, and the lockers.</p>
""" + sources(["jrair", "jrttcts", "jrttspk", "jrops", "jrpdf", "jrstn", "jrdis", "jrfaq", "ajr", "jrhome", "jrwifi"], "Times change, so check JR Hokkaido.")

BUS = """<h2 id="bus">To Sapporo by bus</h2>
<p>Two companies, Hokkaido Chuo Bus and Hokuto Kotsu, run the airport buses to Sapporo city centre on one shared timetable, taking turns. Hokkaido Chuo Bus says no booking is needed and gives about every 10 minutes.</p>
<div class="ps-scroll">
<table class="checklist-table">
<thead><tr><th>Bus</th><th>Domestic stop (1F)</th><th>International stop</th></tr></thead>
<tbody>
<tr><td><strong>Sapporo city centre</strong> (and the direct bus, last stop Nakajima Park)</td><td>14, 22</td><td>84</td></tr>
<tr><td><strong>Makomanai, Maruyama Bus Terminal, Soen</strong></td><td>12, 21</td><td>84</td></tr>
<tr><td><strong>Jozankei Onsen</strong></td><td>21</td><td>85</td></tr>
<tr><td><strong>Otaru, Sapporo Beer Garden, Miyanosawa, Kita 24-jo</strong></td><td>13, 20</td><td>84</td></tr>
<tr><td><strong>Asahikawa, Obihiro, Tokachigawa Onsen</strong></td><td>21</td><td>85</td></tr>
<tr><td><strong>Hakodate</strong></td><td>13</td><td>84</td></tr>
</tbody>
</table>
</div>
<ul>
<li><strong>How long.</strong> On the bus company's summer 2026 timetable, about 70 minutes from the International Terminal to Sapporo Station (68 to 70 minutes) and 74 minutes from the ANA stop, and 62 to 64 minutes from the International Terminal to Odori Park. The Sapporo stops include Susukino, Odori Park and Sapporo Station.</li>
<li><strong>First and last bus.</strong> On that timetable, from the ANA stop 8:40 to 22:55, and from the International Terminal 8:46 to 22:59, with 76 departures a day. A winter timetable may replace it from December, so check before you travel.</li>
<li><strong>Tickets and payment.</strong> Cash, contactless credit cards, return and coupon tickets work on both companies' buses. Transport IC cards (SAPICA, Kitaca, Suica and others) work only on Hokkaido Chuo Bus buses; PayPay only on Hokuto Kotsu buses. Tickets from the bus counters or ticket machines are good on buses of both companies (Sapporo Tourist Association).</li>
<li><strong>Where to buy.</strong> Domestic 1F: the Hokkaido Chuo Bus counter near Arrival Gate 4, and the Hokuto Kotsu and Donan Bus counter near Arrival Gate 2. International: ticket machines in the 1F Main Entrance Lobby (not for every route).</li>
<li><strong>The bus leaves on time.</strong> Hokkaido Chuo Bus says its buses leave on schedule even if flights are delayed, and that weather and traffic can make them late, so allow time before a flight.</li>
<li><strong>Big bags</strong> go in the trunk: tell the staff your stop. If the bus is full, you may be offered a fold-down seat or the next bus.</li>
</ul>
""" + sources(["abus", "chuo", "chuofeat", "chuobeg", "chuobag", "stv", "fmdom"], "Timetables change with the season, so check the bus company.")

SKI = """<h2 id="ski">Ski buses: Niseko, Rusutsu and Furano</h2>
<p>The airport's bus page lists these, from the Domestic Terminal:</p>
<ul>
<li><strong>Ski Bus to Niseko and Rusutsu</strong> (Niseko Bus): domestic stop 12. No international stop is listed. The airport says the ski bus runs in winter only.</li>
<li><strong>Furano</strong> (HOKKAIDO BUS): domestic stop 23. No international stop is listed.</li>
<li><strong>Times, fares and booking.</strong> We could not read the bus companies' timetable pages, so we give none. Check Niseko Bus and HOKKAIDO BUS before you travel, and plan a back-up in case snow delays your flight.</li>
<li><strong>Landed at the International Terminal?</strong> Walk the 2F corridor to the Domestic Terminal; the domestic bus stops are on 1F.</li>
<li><strong>Skis and snowboards</strong> count as large items at the baggage counters (Domestic 1F, 7:00 to 20:00).</li>
</ul>
""" + sources(["abus", "bagroom"], "Ski-bus dates and times change every season.")

MONEY = """<h2 id="money">Money: currency exchange and ATMs</h2>
<p>The airport says its currency exchange opens in line with the flights. These are the counters, machines and ATMs it lists.</p>
<ul>
<li><strong>International 2F (arrivals).</strong> Currency exchange counter in the arrival lobby, 8:30 to 19:00 (may change with flight times), and an automatic exchange machine. ATMs: Seven Bank, 6:00 to 21:00, all year, takes overseas cards; AEON Bank. A bank counter (North Pacific Bank), weekdays only.</li>
<li><strong>International 3F (departures).</strong> Exchange counter in the north departure lobby, 9:30 to 16:00 (the south one is suspended). ATMs (North Pacific Bank, AEON Bank) on the floor guide.</li>
<li><strong>Domestic 1F.</strong> Exchange counters in the arrival lobby: ANA side 7:15 to 20:00, JAL side 9:00 to 17:00. Automatic exchange machines on the north and south sides, open with the building.</li>
<li><strong>Domestic ATMs</strong>, north and south sides. Seven Bank, 6:20 to 23:00, and Japan Post Bank (hours vary by side and day) both take overseas cards. AEON Bank and Lawson Bank also take overseas cards and follow the building hours.</li>
</ul>
""" + sources(["fx", "atm", "fmint"], "Hours can change with flight times.")

CONNECTED = """<h2 id="connected">Getting online: SIM machines, Wi-Fi and eSIM</h2>
<ul>
<li><strong>Free Wi-Fi.</strong> In both terminal buildings, but not in the connecting corridor. JR Hokkaido also provides Wi-Fi at its stations and on the Airport Train cars.</li>
<li><strong>Prepaid SIM vending machines.</strong> Domestic 1F, and International 2F and 3F. The airport lists data-only SIMs for Japan and an eSIM option, and says to check the price at the machine.</li>
<li><strong>Mobile Wi-Fi and phone rental counters.</strong> Domestic 1F and International 2F, and one on International 3F. Hours differ by counter: for example 9:00 to 19:00 and 9:00 to 17:00 at International 2F, and 9:00 to 18:00 at Domestic 1F (closed 13:00 to 14:00). Pick-up and return machines follow the building hours.</li>
<li><strong>eSIM:</strong> install it on your phone before you fly and switch it on when you land. It needs an eSIM-ready, unlocked phone.</li>
</ul>
""" + sources(["sim", "wifi", "lan", "qa", "jrwifi"])

HOURS = """<h2 id="hours">Opening hours, hotels, onsen and the observation deck</h2>
<ul>
<li><strong>Building hours.</strong> Domestic Terminal 5:00 to 23:30. International Terminal 5:00 to 21:00. Connecting corridor 5:00 to 23:30. The airport says hours can change with flight delays, and on days with late-night domestic flights only some areas stay open later.</li>
<li><strong>No staying overnight.</strong> After closing you may not rest in the airport, except in the accommodation facilities.</li>
<li><strong>Airport hotels.</strong> Air Terminal Hotel, in the Domestic Terminal by Arrival Gate 5 (its own lift, 1F to 5F). Portom International Hokkaido, on International 4F: enter by the escalator on the 3F departure lobby side, or by the hotel lift from 1F to 3F.</li>
<li><strong>New Chitose Airport Onsen.</strong> Domestic 4F. The airport describes it as a relaxation facility using natural hot spring water, where you can stay a long time. Open 23 hours, 10:00 to 9:00 the next morning (last entry 7:30). A late-night surcharge applies after 1:00. Between 23:00 and 5:00, when the terminal is closed, use the 24-hour lift from 1F to 4F.</li>
<li><strong>Observation deck.</strong> Domestic 4F, entered from the 3F food area, beside the Airport History Museum. Open 1 April to 30 November, 8:00 to 20:00; <strong>closed December to March</strong>. It may also close in strong wind or heavy snow.</li>
</ul>
""" + sources(["hours", "fmdom", "fmint", "deck"], "Hours can change, so check the airport's pages.")

WINTER = """<h2 id="winter">Snow, delays and cancelled flights</h2>
<p>Hokkaido winters are cold and snowy. The Sapporo Tourist Association recommends warm clothing and shoes with good grip on snowy roads. This is what the official pages say to do when the weather gets in the way.</p>
<ul>
<li><strong>Your flight.</strong> The airport's FAQ: for seat availability, bookings, cancellations and missed flights, contact the airline you are flying with.</li>
<li><strong>Delays and transport.</strong> The airport points you to the airlines' and transport companies' own websites, and to the Hokkaido District Transport Bureau's <a href="https://hokkaido-safe-travel.mlit.go.jp/" target="_blank" rel="noopener noreferrer">Hokkaido travel safety information</a>.</li>
<li><strong>Live train information.</strong> Check JR Hokkaido&rsquo;s <a href="https://www3.jrhokkaido.co.jp/webunkou/index_en.html" target="_blank" rel="noopener noreferrer">Train Operation Information (English)</a>, or its <a href="https://www3.jrhokkaido.co.jp/webunkou/stationlist_en.html" target="_blank" rel="noopener noreferrer">information for each station</a>, which also shows that day&rsquo;s departures. JR&rsquo;s guide to it describes delays of 5 minutes or more by station (5:00 to 25:00), a map of cancellations and delays of 30 minutes or more by line, including the Chitose Line (Sapporo, New Chitose Airport, Tomakomai), 5:00 to 24:00, and train locations with delays of 1 minute or more (5:00 to 25:00).</li>
<li><strong>Trains stopped?</strong> JR Hokkaido lists the airport bus (about 70 to 90 minutes) and taxis (about 60 minutes) as alternatives, and warns they can get extremely crowded.</li>
<li><strong>Buses in snow.</strong> Hokkaido Chuo Bus says weather and traffic can delay the bus, and that it leaves on time even when flights are late.</li>
<li><strong>Stuck late at night?</strong> The terminals close (Domestic 23:30, International 21:00) and you may not stay inside after closing, except in the accommodation facilities. There is a hotel in each terminal, and the New Chitose Airport Onsen (Domestic 4F) is open 23 hours, 10:00 to 9:00 the next morning.</li>
<li><strong>Observation deck</strong> is closed December to March.</li>
</ul>
<p>We did not find airport pages about snow clearing or what the airport provides on a snowbound night, so we give no advice on that. Ask your airline and the information centers.</p>
""" + sources(["qa", "safe", "jrdis", "jrhome", "chuobeg", "hours", "deck", "stvnews"], "Rules can change, so check your airline.")

LEAVING = """<h2 id="leaving">Leaving from New Chitose: a checklist</h2>
<ul>
<li><strong>Which terminal?</strong> International departures are on International 3F; domestic departures on Domestic 2F.</li>
<li><strong>Coming by train?</strong> You arrive at B1F under the Domestic Terminal. For an international flight, go up to 2F and walk the 2F corridor (the 3F passage is closed until about the end of June 2027), then up to 3F.</li>
<li><strong>Early flight?</strong> The first Airport Train from Sapporo leaves at 5:50 and reaches the airport at 6:28 (JR&rsquo;s timetable for 24 November 2026). The first bus from Sapporo was not on the timetable we read. Check JR and the bus companies the day before. The terminals open at 5:00.</li>
<li><strong>Snow forecast?</strong> Contact your airline, check Hokkaido travel safety information, and leave earlier: trains and buses can be delayed and crowded.</li>
<li><strong>Collect your bags.</strong> Lockers hold bags for up to 3 days; check the counter hours if you left bags at a baggage counter.</li>
<li><strong>Leftover yen?</strong> The International 3F exchange counter (north) is open 9:30 to 16:00.</li>
<li><strong>Flying on from Tokyo?</strong> See our <a href="/blog/haneda-airport-guide">Haneda Airport guide</a> or <a href="/blog/narita-airport-guide">Narita Airport guide</a>.</li>
</ul>
""" + sources(["fmint", "fmdom", "renov", "hours", "qa", "fx", "locker"], "Times change, so check the operator.")

QR_SCREEN = '<svg shape-rendering="crispEdges" viewBox="0 0 41 41" class="segno"><title>QR code: open the New Chitose Airport Pocket Guide</title><path fill="#fff" d="M0 0h41v41h-41z"/><path class="qrline" stroke="#000" d="M4 4.5h7m1 0h2m1 0h1m4 0h1m1 0h3m2 0h1m2 0h7m-33 1h1m5 0h1m1 0h2m4 0h1m1 0h2m2 0h2m1 0h1m2 0h1m5 0h1m-33 1h1m1 0h3m1 0h1m2 0h1m1 0h1m1 0h3m2 0h3m5 0h1m1 0h3m1 0h1m-33 1h1m1 0h3m1 0h1m1 0h1m1 0h3m4 0h1m2 0h1m1 0h1m1 0h1m1 0h1m1 0h3m1 0h1m-33 1h1m1 0h3m1 0h1m2 0h2m2 0h1m2 0h4m4 0h1m1 0h1m1 0h3m1 0h1m-33 1h1m5 0h1m2 0h1m1 0h2m1 0h3m2 0h2m1 0h1m1 0h1m1 0h1m5 0h1m-33 1h7m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h7m-25 1h2m4 0h5m3 0h1m-23 1h1m1 0h2m1 0h3m1 0h2m1 0h1m1 0h5m1 0h2m2 0h1m1 0h1m2 0h1m1 0h2m-33 1h2m1 0h2m3 0h1m1 0h1m2 0h1m5 0h3m1 0h1m2 0h2m1 0h2m1 0h1m-32 1h2m2 0h2m3 0h1m1 0h2m2 0h1m3 0h1m1 0h2m2 0h4m1 0h2m-33 1h1m1 0h1m1 0h2m3 0h3m11 0h2m1 0h2m1 0h1m-30 1h1m1 0h1m3 0h3m2 0h1m2 0h1m1 0h1m1 0h1m1 0h1m1 0h4m2 0h2m1 0h2m-30 1h2m2 0h1m2 0h1m1 0h1m1 0h1m2 0h1m1 0h2m1 0h1m1 0h1m2 0h1m1 0h1m1 0h1m-26 1h1m1 0h1m1 0h1m1 0h1m6 0h4m1 0h1m1 0h2m1 0h2m-31 1h6m1 0h7m1 0h1m2 0h2m1 0h3m1 0h2m1 0h3m-31 1h2m1 0h1m1 0h4m1 0h1m7 0h1m2 0h2m2 0h2m1 0h3m-30 1h3m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m2 0h1m1 0h1m1 0h2m2 0h1m1 0h2m1 0h2m-33 1h5m1 0h3m1 0h2m1 0h1m1 0h2m1 0h1m1 0h3m2 0h1m1 0h2m1 0h1m-31 1h2m1 0h1m4 0h1m1 0h2m1 0h5m2 0h1m3 0h3m1 0h1m2 0h1m-32 1h2m4 0h3m2 0h2m2 0h2m2 0h1m1 0h2m2 0h1m3 0h2m-31 1h5m3 0h4m1 0h4m1 0h3m1 0h2m2 0h1m5 0h1m-31 1h2m1 0h4m2 0h1m1 0h3m1 0h1m2 0h2m1 0h1m1 0h2m2 0h1m1 0h2m-32 1h3m1 0h1m5 0h2m1 0h2m10 0h4m1 0h2m-33 1h1m1 0h1m3 0h1m3 0h1m1 0h1m1 0h1m2 0h2m3 0h1m1 0h5m2 0h1m-24 1h3m4 0h2m2 0h1m1 0h2m1 0h1m3 0h2m1 0h1m-32 1h7m1 0h1m1 0h2m2 0h1m2 0h5m1 0h2m1 0h1m1 0h1m-29 1h1m5 0h1m1 0h1m1 0h2m1 0h2m2 0h2m1 0h5m3 0h4m-32 1h1m1 0h3m1 0h1m2 0h4m3 0h4m1 0h8m1 0h3m-33 1h1m1 0h3m1 0h1m1 0h4m1 0h1m2 0h2m2 0h1m2 0h2m2 0h1m2 0h1m1 0h1m-33 1h1m1 0h3m1 0h1m1 0h2m4 0h4m2 0h1m2 0h5m1 0h2m-31 1h1m5 0h1m4 0h1m1 0h1m3 0h1m1 0h2m1 0h1m1 0h2m1 0h2m3 0h1m-33 1h7m1 0h3m2 0h1m2 0h4m1 0h1m1 0h1m4 0h3"/></svg>'
QR_PRINT = '<svg shape-rendering="crispEdges" viewBox="0 0 41 41" class="segno"><title>QR code: open the New Chitose Airport Pocket Guide</title><path fill="#fff" d="M0 0h41v41h-41z"/><path class="qrline" stroke="#000" d="M4 4.5h7m1 0h2m6 0h1m1 0h3m2 0h1m2 0h7m-33 1h1m5 0h1m1 0h3m1 0h1m1 0h1m1 0h1m3 0h2m1 0h1m2 0h1m5 0h1m-33 1h1m1 0h3m1 0h1m3 0h2m1 0h3m2 0h3m5 0h1m1 0h3m1 0h1m-33 1h1m1 0h3m1 0h1m1 0h2m1 0h1m5 0h1m4 0h1m1 0h1m1 0h1m1 0h3m1 0h1m-33 1h1m1 0h3m1 0h1m2 0h2m2 0h1m2 0h2m1 0h1m4 0h1m1 0h1m1 0h3m1 0h1m-33 1h1m5 0h1m2 0h1m4 0h3m2 0h2m1 0h1m1 0h1m1 0h1m5 0h1m-33 1h7m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h7m-25 1h1m3 0h1m1 0h5m3 0h1m-23 1h1m1 0h2m1 0h3m1 0h1m1 0h1m2 0h5m1 0h2m2 0h1m1 0h1m2 0h1m1 0h2m-31 1h3m2 0h3m1 0h1m1 0h1m5 0h3m1 0h1m2 0h2m1 0h2m1 0h1m-33 1h1m4 0h2m1 0h1m2 0h3m2 0h2m2 0h1m1 0h2m2 0h4m1 0h2m-32 1h3m4 0h2m1 0h2m5 0h1m4 0h2m1 0h2m1 0h1m-29 1h1m4 0h3m1 0h1m3 0h1m1 0h2m2 0h1m1 0h4m2 0h2m1 0h2m-29 1h1m2 0h1m1 0h1m4 0h1m2 0h4m1 0h1m1 0h1m2 0h1m1 0h1m1 0h1m-32 1h2m2 0h1m1 0h2m1 0h1m2 0h1m6 0h4m1 0h1m1 0h2m1 0h2m-30 1h2m1 0h1m3 0h1m1 0h1m3 0h2m2 0h2m1 0h3m1 0h2m1 0h3m-31 1h2m4 0h1m1 0h1m1 0h1m1 0h3m3 0h1m2 0h2m2 0h2m1 0h3m-27 1h2m2 0h1m2 0h1m2 0h2m2 0h1m1 0h1m1 0h2m2 0h1m1 0h2m1 0h2m-33 1h1m2 0h5m2 0h3m1 0h5m1 0h3m2 0h1m1 0h2m1 0h1m-30 1h1m1 0h1m1 0h1m1 0h1m2 0h8m2 0h1m3 0h3m1 0h1m2 0h1m-32 1h1m1 0h2m2 0h1m2 0h1m1 0h2m2 0h5m1 0h2m2 0h1m3 0h2m-31 1h2m3 0h1m1 0h2m1 0h2m1 0h4m1 0h3m1 0h2m2 0h1m5 0h1m-30 1h1m1 0h3m1 0h1m1 0h2m2 0h1m1 0h1m2 0h2m1 0h1m1 0h2m2 0h1m1 0h2m-32 1h1m5 0h2m1 0h1m2 0h1m1 0h1m10 0h4m1 0h1m-32 1h1m1 0h1m1 0h3m1 0h1m2 0h1m1 0h1m3 0h2m3 0h1m1 0h5m3 0h1m-25 1h1m3 0h1m2 0h3m1 0h1m1 0h2m1 0h1m3 0h2m1 0h1m-32 1h7m1 0h1m1 0h5m3 0h4m1 0h2m1 0h1m1 0h1m-29 1h1m5 0h1m1 0h1m1 0h1m1 0h2m4 0h1m1 0h5m3 0h4m-32 1h1m1 0h3m1 0h1m2 0h2m1 0h1m1 0h1m2 0h1m1 0h1m1 0h8m1 0h3m-33 1h1m1 0h3m1 0h1m1 0h1m3 0h2m2 0h2m2 0h1m2 0h2m2 0h1m2 0h1m1 0h1m-33 1h1m1 0h3m1 0h1m1 0h1m4 0h3m1 0h1m2 0h1m2 0h5m1 0h2m-31 1h1m5 0h1m3 0h2m1 0h2m2 0h1m1 0h2m1 0h1m1 0h2m1 0h2m3 0h1m-33 1h7m1 0h1m4 0h1m2 0h4m1 0h1m1 0h1m4 0h3"/></svg>'
CARD = CARD.replace("__QR_SCREEN__", QR_SCREEN).replace("__QR_PRINT__", QR_PRINT)

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
<div id="psPocketBar" role="region" aria-label="New Chitose Airport Pocket Guide">
<div class="t"><b>Get the New Chitose Airport Pocket Guide</b><span>Free. Works offline at the airport.</span></div>
<a class="go" href="/new-chitose-pocket?src=bar">Get it</a>
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
<p>Open the New Chitose Airport Pocket Guide once while you have signal, then add it to your home screen. At the airport it opens like an app, even with no connection.</p>
<p><a class="ps-btn2" href="/new-chitose-pocket?src=box" onclick="try{window.gtag&&gtag('event','pocket_prompt',{event_category:'engagement',action:'open_box',page_path:location.pathname});}catch(e){}" style="display:inline-block;text-decoration:none;">Open the Pocket Guide</a></p>
<ul>
<li><strong>iPhone:</strong> open it in Safari, tap the Share button, then "Add to Home Screen".</li>
<li><strong>Android:</strong> open it in Chrome, tap the menu (three dots), then "Add to Home screen" or "Install app".</li>
</ul>
</div>"""

# ---- GetYourGuide box: tours and tickets for a search on Niseko skiing (partner D7IXONS, its own cmp so clicks can be told apart).
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

GYGQ_TPL = """<div class="ps-gyg" data-ps-placement="__PID__">
<strong class="ps-gyg-h">__HEAD__</strong>
<p class="ps-gyg-s">__BLURB__</p>
<div class="ps-gyg-w"><div class="ps-gyg-slot" data-gyg-href="https://widget.getyourguide.com/default/activities.frame" data-gyg-locale-code="en-US" data-gyg-number-of-items="3" data-gyg-partner-id="__PARTNER__"></div></div>
<p class="ps-gyg-s" style="margin:8px 0 0;"><a href="__SEARCH__" target="_blank" rel="nofollow noopener sponsored" style="color:#0a8f78;font-weight:700;">__MORE__</a> (partner link)</p>
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

GYG_Q = "Niseko ski"
GYG_CMP = "ps-new-chitose-gyg"
GYG_SEARCH = "https://www.getyourguide.com/s/?q=%s&partner_id=%s&cmp=ps-new-chitose" % (quote(GYG_Q), GYG_PARTNER)
GYG_BOX = (GYGQ_TPL.replace("__PID__", "gyg-new-chitose").replace("__HEAD__", "Ski and snow tours in Hokkaido")
           .replace("__BLURB__", "Popular ski and snow tours, as listed by our partner. Check what is included, and the pick-up point, before you book.")
           .replace("__MORE__", "See more ski tours and tickets")
           .replace("__PARTNER__", GYG_PARTNER).replace("__SEARCH__", html.escape(GYG_SEARCH))
           .replace("__Q__", GYG_Q).replace("__CMP__", GYG_CMP))

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
share = share.replace("japan-travel-packing-guide", SLUG)
share = re.sub(r"text=[^&\"']*?(?=(%20https|&url|\"))", "text=" + enc_title, share)
share = re.sub(r"media=[^&\"']*", "media=" + quote(SITE + "/og-default.png", safe=""), share)
share = re.sub(r"description=[^\"']*", "description=" + enc_title, share)

BODY = "\n\n".join([
    '<p style="font-size:0.85rem;color:#666;margin:0 0 0.6rem;">Published November 24, 2026 · Last updated November 2026 · Facts checked 24 Nov 2026</p>',
    AFFILIATE_P,
    share,
    PRINT_CSS,
    WARN_CSS,
    '<p>New Chitose Airport (CTS) is the airport for Sapporo and the start of most ski trips and Snow Festival visits in Hokkaido. '
    'It has two terminal buildings, a JR station underneath and buses at the door, and in winter the weather can change your plans. '
    'Until about the end of June 2027 the 3F passage between the terminals is closed, so the way across is the 2F corridor. '
    'This guide is written in plain English so that a first-time visitor, a family or an older traveller can follow it step by step. '
    'You can print the one-page card below and carry it with you.</p>',
    toc_html,
    CARD,
    TERMINALS,
    DIAGRAM,
    BETWEEN,
    TRAIN,
    BUS,
    SKI,
    GYG_BOX,
    MONEY,
    CONNECTED,
    airalo,
    LUGGAGE,
    FINDER,
    SAVE_BOX,
    HOURS,
    WINTER,
    HELP,
    LEAVING,
    '<div class="tip-box">\n    <strong>Planning more of Japan?</strong> Our <a href="/blog/japan-travel-packing-guide">Japan travel and packing guide</a> covers what to pack, rail passes, etiquette and a budget breakdown. '
    'Heading into the city? See our <a href="/blog/sapporo-station-guide">Sapporo Station guide</a>.\n</div>',
    "<!-- FIRST-HAND NOTES: add notes and photos from a New Chitose Airport visit here -->",
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
SOURCES = ('<h2 id="sources">Sources</h2>\n<p>Every airport fact on this page comes from the official sites below, '
           'checked on 24 November 2026. Airports change, so follow the signs on the day.</p>\n<ul class="ps-sources">\n'
           + "".join("<li>%s</li>\n" % a for a in _src_links) + "</ul>")
_faq = BODY.index('<h2 id="faq">')
BODY = BODY[:_faq] + SOURCES + "\n\n" + BODY[_faq:]
# hero button: a quiet way into the Pocket Guide from the top of the article (as w42)
HERO_CTA = ('        <div style="margin:48px 0 0;text-align:center;">'
            '<a href="/new-chitose-pocket?src=hero" onclick="try{window.gtag&&gtag(\'event\',\'pocket_prompt\',{event_category:\'engagement\',action:\'open_hero\',page_path:location.pathname});}catch(e){}" '
            'style="display:inline-flex;align-items:center;gap:12px;background:#00C9A7;color:#0f0f23;text-align:left;padding:12px 14px 12px 20px;width:340px;max-width:100%;box-sizing:border-box;border-radius:12px;text-decoration:none;min-height:44px;box-shadow:0 6px 18px rgba(0,0,0,.28);line-height:1.2;">'
            '<span style="flex:1;min-width:0;text-align:left;">'
            '<span style="display:block;font-weight:700;font-size:0.8rem;opacity:0.8;">Save to your phone</span>'
            '<span style="display:block;font-weight:800;font-size:1.05rem;margin-top:2px;">New Chitose Airport Pocket Guide</span>'
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
    '        <div class="meta">Airport Guide • Japan · Published 24 Nov 2026 · __READ__ min read</div>',
    HERO_CTA,
    ('        <div style="position:absolute;left:12px;right:12px;bottom:8px;font-size:0.7rem;opacity:0.7;text-align:center;">Photo: PAKUTASO. (no photo on this page)</div>' if HERO_URL else ''),
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



# ---- New Chitose Airport Pocket Guide: standalone page + service worker + manifest (works offline once visited)
POCKET_PATH = "/new-chitose-pocket"
THEME = "#2563EB"   # winter blue, one colour per guide
# ---- Pocket Guide analytics (v47): anonymous taps only, no accounts, honours Do Not Track / GPC
GUIDE_ID = "new-chitose"
AIRPORT_CODE = "CTS"
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

POCKET_SVG = re.search(r'<svg id="ctsDiagram".*?</svg>', DIAGRAM, re.S).group(0).replace('id="ctsDiagram"', 'id="pkDiagram"').replace('id="ctsT"', 'id="pkT"').replace('id="ctsD"', 'id="pkD"').replace('aria-labelledby="ctsT ctsD"', 'aria-labelledby="pkT pkD"')
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
.tlink.warn{color:#a3243b;border-left-color:#E94560}
.badge.sm{font-size:1.15rem;letter-spacing:.02em}
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
<title>New Chitose Airport Pocket Guide | PackSmart</title>
<meta name="description" content="A simple New Chitose Airport helper that works offline: which terminal, the 2F corridor (3F closed), the train and buses to Sapporo, money, SIM, lockers and winter tips. By PackSmart.">
<meta name="robots" content="noindex,follow">
<link rel="canonical" href="__GUIDE_URL__">
<meta name="theme-color" content="#1a1a3e">
<link rel="manifest" href="/new-chitose-pocket.webmanifest">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" href="/images/new-chitose-apple-touch-180.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="New Chitose">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<script>__PG_BOOT__</script>
<style>__CSS__</style>
</head>
<body>
<header class="top">
<div><strong>New Chitose Airport Pocket Guide</strong><span class="by">by PackSmart &middot; 24 Nov 2026</span></div>
<div class="status" id="status" role="status">Checking...</div>
</header>
<button type="button" class="inst-strip" id="instStrip" hidden><span class="ico" aria-hidden="true">&#128242;</span><span><b>Add this to your home screen</b><br>so it works with no internet</span><span class="go">How</span></button>
<div class="panels" id="panels">
<section class="panel" id="p-find" role="tabpanel" aria-labelledby="t-find">
<p class="seg-h">Which terminal are you in?</p>
<div class="seg" id="seg"></div>
<p class="seg-h" style="margin-top:14px">What do you need? <span class="small">Tap one.</span></p>
<div class="pager" id="pager"><div class="track" id="track"><div class="tiles pane" id="tiles"></div><div class="tiles pane off" id="tiles2" aria-hidden="true"></div></div></div>
<p class="hint">Counters and hours can change. Ask at an information center.</p>
<div id="sponsor" hidden></div>
<noscript><p class="card">This guide needs JavaScript. Please turn it on, or ask at any information counter.</p></noscript>
</section>
<section class="panel" id="p-map" role="tabpanel" aria-labelledby="t-map" hidden>
<p class="seg-h" style="margin-top:2px">Which terminal are you in?</p>
<div class="seg" id="mseg"></div>
<p class="lead2" id="mLead" style="margin-top:10px">International flights: International Terminal. Domestic flights and JR trains: Domestic Terminal.</p>
<div class="tmap" id="tmap">
<div class="tcard t2" data-t="T1"><div class="badge sm">INTL</div><div class="tb"><h3>International Terminal</h3><p>West side. 3F Departures. 2F Arrivals: exchange, Seven Bank ATM, SIM machines, tourist information, prayer room. 1F buses (stop 84) and taxis. 4F hotel</p></div></div>
<div class="tlink warn"><span aria-hidden="true">&#128694;</span><span>2F Connecting Corridor (moving walkways). 3F passage closed to about end June 2027</span></div>
<div class="tcard t1" data-t="T2"><div class="badge sm">DOM</div><div class="tb"><h3>Domestic Terminal</h3><p>East side. 2F Departures and shops. 1F Arrivals, bus stops 14 and 22 (Sapporo), bus counters. 3F food. 4F onsen and observation deck (closed Dec to Mar)</p><p class="stn"><span aria-hidden="true">&#128646;</span> JR: go down to B1F</p></div></div>
<div class="tlink"><span aria-hidden="true">&#11015;&#65039;</span><span>Lifts and escalators down to B1F</span></div>
<div class="tcard t3" data-t="JR"><div class="badge sm">B1F</div><div class="tb"><h3>JR New Chitose Airport Station</h3><p>Ticket gates, JR Information Desk (8:30 to 19:00), ticket office, JR lockers. Platforms on B2F. Airport Train to Sapporo: fastest 33 min</p></div></div>
</div>
<p class="small" style="text-align:center;margin-top:10px">Simplified, not to scale. From the airport's floor guide (17 September 2026). Follow the signs.</p>
</section>
<section class="panel" id="p-arrive" role="tabpanel" aria-labelledby="t-arrive" hidden>
<p class="lead2">Landed? Tap a step to tick it off.</p>
<ol class="steps" id="arrSteps"></ol>
<button type="button" class="reset" id="arrReset" hidden>Clear ticks</button>
<p class="sec-h">Then, once you are out</p>
<div class="tiles" id="arrTiles"></div>
</section>
<section class="panel" id="p-depart" role="tabpanel" aria-labelledby="t-depart" hidden>
<div class="heroline"><span class="big2">33&nbsp;min</span><span><b>Fastest Airport Train, airport to Sapporo.</b><br>JR&rsquo;s Special Rapid. Bus: about 70 min.</span></div>
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
<p class="sec-h">At New Chitose Airport only</p>
<p class="small" style="margin-top:0">Information centers in both terminals lend wheelchairs and help with transport. Hokkaido Foreign Tourist Information Center: International 2F, 8:00 to 20:00, English, Chinese and Korean.</p>
<a class="num air" href="tel:+81123230111"><span class="ni" aria-hidden="true">&#9992;&#65039;</span><span class="nt"><b>New Chitose Airport information</b><span>0123-23-0111</span><small>7:00 to 23:00. Japanese and English</small></span></a>
</div>
<div class="tiles hnav" id="hnav2"></div>
</div>
</div></div>
<div class="quiet"><div class="card slim" id="shareCard" hidden><div class="row"><div><h2>Helping someone travel?</h2><p>Send them this guide for offline use.</p></div><button type="button" class="big" id="shareBtn">Send it</button></div></div>
<div class="card slim install" id="install"><div class="row"><div><h2>Keep this on your phone</h2><p>Add it to your home screen. Works offline.</p><p class="small" id="instDesk">Open this page on your phone, then add it to your home screen.</p></div><div id="instHow" hidden><button type="button" class="big" id="instBtn">Show me</button></div></div></div>
<p class="small">Airport details come from the New Chitose Airport website and floor guides, JR Hokkaido and Hokkaido Chuo Bus, checked 24 November 2026. Counters, hours and timetables can change. If you cannot find something, ask at an information center. Found something out of date? <a href="/contact">Tell us</a> (needs internet). We count anonymous taps to improve this guide: no name, no account. <a href="/privacy-policy">Privacy</a> &middot; <a href="#" id="pgOpt">Turn off counting</a>. The full guide, with the terminals, trains, buses and winter tips, is at <a href="__GUIDE_URL__">packsmartapp.com</a> (needs internet).</p></div>
</section>
</div>
<nav class="tabs" role="tablist" aria-label="Sections">
<button type="button" role="tab" id="t-find" data-tab="find" aria-selected="true"><span aria-hidden="true">&#128269;</span>Find</button>
<button type="button" role="tab" id="t-map" data-tab="map" aria-selected="false"><span aria-hidden="true">&#128506;&#65039;</span>Terminals</button>
<button type="button" role="tab" id="t-arrive" data-tab="arrive" aria-selected="false"><span aria-hidden="true">&#128748;</span>Arrival</button>
<button type="button" role="tab" id="t-depart" data-tab="depart" aria-selected="false"><span aria-hidden="true">&#128747;</span>Leaving</button>
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
  var ICON={prayer:'\\uD83D\\uDE4F',baby:'\\uD83C\\uDF7C',quiet:'\\uD83E\\uDD2B',info:'\\u2139\\uFE0F',help:'\\u267F',lockers:'\\uD83E\\uDDF3',wifi:'\\uD83D\\uDCF6',shower:'\\uD83D\\uDEBF',internet:'\\uD83D\\uDCBB',play:'\\uD83E\\uDDF8',smoking:'\\uD83D\\uDEAC',toilet:'\\uD83D\\uDEBB',food:'\\uD83C\\uDF5C',money:'\\uD83D\\uDCB4',unwell:'\\uD83C\\uDFE5',pharmacy:'\\uD83D\\uDC8A',trains:'\\uD83D\\uDE86',tickets:'\\uD83C\\uDFAB',phone:'\\uD83D\\uDCF6',charge:'\\uD83D\\uDD0B',exits:'\\uD83D\\uDEAA',park:'\\uD83C\\uDF38',lost:'\\uD83D\\uDCE6',bus:'\\uD83D\\uDE8C',bags:'\\uD83D\\uDEC4',rest:'\\u2668\\uFE0F',walk:'\\uD83D\\uDEB6',more:'\\u2795'};
  var SHORT={prayer:'Prayer room',baby:'Nursing room',quiet:'Quiet space',info:'Information counter',help:'Wheelchair and help',lockers:'Lockers',wifi:'Wi-Fi rental',shower:'Showers',internet:'Free internet',play:'Kids play area',smoking:'Smoking room',toilet:'Toilets',food:'Shops and food',money:'Money and ATMs',unwell:'Feeling unwell',pharmacy:'Pharmacy',trains:'Train to Sapporo',tickets:'Tickets and passes',phone:'Phone and Wi-Fi',charge:'Phone charging',exits:'Which exit?',park:'Park',lost:'Lost and found',bus:'Bus to Sapporo',bags:'Bag storage',rest:'Hotels and onsen',walk:'Between terminals',more:'More places'};
  var term='ALL', lastTile=null;
  try{ var s=localStorage.getItem('ctsTerm'); if(s&&/^(ALL|T1|T2)$/.test(s)) term=s; }catch(e){}
  function $(id){return document.getElementById(id);}
  /* side selector */
  var seg=$('seg');
  function segBtn(id,html,cls){
    var b=document.createElement('button'); b.type='button'; b.setAttribute('data-t',id); if(cls) b.className=cls;
    b.innerHTML=html; b.addEventListener('click',function(){ term=id; try{localStorage.setItem('ctsTerm',id);}catch(e){} paintSeg(); renderDep(); }); return b;
  }
  var CAP={T1:['Terminal','International'],T2:['Terminal','Domestic']};
  D.terms.forEach(function(t){ seg.appendChild(segBtn(t[0],'<small>'+CAP[t[0]][0]+'</small><b>'+CAP[t[0]][1]+'</b>')); });
  seg.appendChild(segBtn('ALL','Not sure','txt'));
  var mseg=$('mseg');
  D.terms.forEach(function(t){ mseg.appendChild(segBtn(t[0],'<small>'+CAP[t[0]][0]+'</small><b>'+CAP[t[0]][1]+'</b>')); });
  mseg.appendChild(segBtn('ALL','Not sure','txt'));
  function paintSeg(){ [seg,mseg].forEach(function(g){ [].forEach.call(g.children,function(b){ b.setAttribute('aria-pressed',b.getAttribute('data-t')===term?'true':'false'); }); }); paintMap(); }
  /* Floors tab: marks the level the person chose */
  function paintMap(){
    var personal=(term==='T1'||term==='T2');
    $('mLead').textContent=personal?(term==='T1'?'You are in the International Terminal. For JR trains, walk the 2F corridor to the Domestic Terminal, then go down to B1F.':'You are in the Domestic Terminal. JR trains: B1F. Sapporo buses: 1F stops 14 and 22.'):'International flights: International Terminal. Domestic flights and JR trains: Domestic Terminal.';
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
  var trainsIt=['trains','Train to Sapporo',{}];
  var busIt=['bus','Bus to Sapporo',{}];
  var walkIt=['walk','Between terminals',{}];
  var LIST=[];
  ['trains','bus','walk','money','phone','lockers','bags','info','help','prayer','rest','food','toilet','unwell'].forEach(function(id){
    LIST.push(id==='trains'?trainsIt:id==='bus'?busIt:id==='walk'?walkIt:item(id));
  });
  LIST.forEach(function(it,n){
    var b=document.createElement('button'); b.type='button'; b.className='tile c'+(n%3); b.setAttribute('data-id',it[0]);
    var ic=document.createElement('span'); ic.className='ic'; ic.setAttribute('aria-hidden','true'); ic.textContent=ICON[it[0]]||'\\u2022';
    var tx=document.createElement('span'); tx.className='tx'; tx.textContent=SHORT[it[0]]||it[1];
    b.appendChild(ic); b.appendChild(tx);
    b.addEventListener('click',function(){ if(it[0]==='trains'){ openInfo(ICON.trains,it[1],trainHTML(),b); } else if(it[0]==='bus'){ openInfo(ICON.bus,it[1],busHTML(),b); } else if(it[0]==='walk'){ openInfo(ICON.walk,it[1],betweenHTML(),b); } else { openSheet(it,b); } });
    (n<MAIN?tiles:tiles2).appendChild(b);
    if(n===MAIN-1){ tiles.appendChild(pill('pgnext','\\u2192','More','Help, prayer room, hotels, food, toilets',function(){ slideTo(1); })); }
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
  var NONE='We did not find this on the airport\\'s pages. Please ask at an information center.';
  function ans(label,txt,mini){
    var d=document.createElement('div'); d.className='ans'+(mini?' mini':'');
    if(label){ var e=document.createElement('em'); e.textContent=label; d.appendChild(e); }
    d.appendChild(document.createTextNode(txt||NONE)); return d;
  }
  function openSheet(it,btn){
    lastTile=btn; shT.textContent=''; shB.textContent='';
    var ic=document.createElement('span'); ic.setAttribute('aria-hidden','true'); ic.textContent=ICON[it[0]]||''; shT.appendChild(ic);
    shT.appendChild(document.createTextNode(it[1]));
    if(term==='ALL'&&D.terms.every(function(t){return it[2][t[0]]===it[2][D.terms[0][0]];})){ shB.appendChild(ans('Both terminals',it[2][D.terms[0][0]],false)); }
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
  var SRCL='<p class="sm">Source: New Chitose Airport website and floor guides, checked 24 November 2026. Counters and hours can change. Follow the signs.</p>';
  function trainHTML(){
    return '<p class="n2">JR New Chitose Airport Station is on <b>B1F</b>, under the Domestic Terminal. Platforms on B2F.</p>'
      +'<ul class="pl"><li><b>Fastest to Sapporo (JR):</b> Special Rapid 33 min, Rapid 37 min, Semi-Rapid 43 min. Six trains an hour from 9:00 to 16:00.</li>'
      +'<li><b>Seats:</b> cars 1 to 3 and 5 to 6 non-reserved. Car 4 is the reserved &ldquo;U seat&rdquo; car: reserved-seat ticket needed.</li>'
      +'<li><b>IC cards</b> (Suica, Kitaca and others) work. Not for Yoichi, Kutchan or Niseko: buy a ticket first.</li>'
      +'<li><b>Ticket machines:</b> cash only. Ticket counter and reserved-seat machine: cash or credit card. No QR payments.</li>'
      +'<li><b>Luggage:</b> within 250 cm in total, up to 2 items, each up to 30 kg.</li>'
      +'<li><b>From the International Terminal:</b> walk the 2F corridor to the Domestic Terminal, then go down to B1F.</li>'
      +'<li>First to Sapporo 6:38, last 23:21 (JR timetable, 24 Nov 2026). Timetables change.</li></ul>'
      +'<p class="sm">Source: JR Hokkaido, checked 24 November 2026. Times change.</p>'+more('#train');
  }
  function busHTML(){
    return '<p class="n2">Sapporo city centre buses: <b>Domestic 1F stops 14 and 22</b>, <b>International stop 84</b>. About <b>70 min</b> to Sapporo Station.</p>'
      +'<ul class="pl"><li>Two companies, one timetable: Hokkaido Chuo Bus and Hokuto Kotsu. No booking needed.</li>'
      +'<li><b>Pay:</b> cash or contactless credit card on both. IC cards (SAPICA, Kitaca, Suica) on Hokkaido Chuo Bus only.</li>'
      +'<li><b>Tickets:</b> bus counters on Domestic 1F (near Arrival Gates 2 and 4), ticket machines in the International 1F Main Entrance Lobby.</li>'
      +'<li>The bus <b>leaves on time even if your flight is late</b>. Snow and traffic can slow it.</li>'
      +'<li>Summer 2026 timetable: first 8:40, last 22:55 from the ANA stop. A winter timetable may replace it.</li>'
      +'<li><b>Ski bus</b> to Niseko and Rusutsu: domestic stop 12, winter only. <b>Furano:</b> domestic stop 23. We did not find their times.</li></ul>'
      +'<p class="sm">Source: New Chitose Airport bus page and Hokkaido Chuo Bus, checked 24 November 2026.</p>'+more('#bus');
  }
  function betweenHTML(){
    return '<div class="tipbox"><b>The 3F passage between the terminals is closed</b> from 2 September 2026 to about the end of June 2027 (construction).</div>'
      +'<ul class="pl"><li>Use the <b>2F Connecting Corridor</b>, with moving walkways. Open 5:00 to 23:30.</li>'
      +'<li>International arrivals are on 2F: walk the corridor, pass the souvenir shops, take the lift down to B1F for JR.</li>'
      +'<li>The airport gives no walking time. Allow extra time with luggage.</li>'
      +'<li>No free Wi-Fi in the corridor.</li></ul>'
      +'<p class="sm">Source: New Chitose Airport notice (9 November 2026) and floor guide, and JR Hokkaido, checked 24 November 2026.</p>';
  }
  function moneyHTML(){
    return '<ul class="pl"><li><b>International 2F:</b> exchange counter 8:30 to 19:00. Seven Bank ATM 6:00 to 21:00, takes overseas cards.</li>'
      +'<li><b>International 3F:</b> exchange counter (north) 9:30 to 16:00.</li>'
      +'<li><b>Domestic 1F:</b> exchange counters, ANA side 7:15 to 20:00, JAL side 9:00 to 17:00. Exchange machines north and south.</li>'
      +'<li><b>Domestic ATMs</b> (north and south): Seven Bank 6:20 to 23:00 and Japan Post Bank take overseas cards.</li></ul>'+SRCL;
  }
  function simHTML(){
    return '<ul class="pl"><li><b>Free Wi-Fi</b> in both terminals, not in the connecting corridor. JR Wi-Fi at the station and on the Airport Train.</li>'
      +'<li><b>SIM vending machines:</b> Domestic 1F, International 2F and 3F.</li>'
      +'<li><b>Wi-Fi rental counters:</b> Domestic 1F, International 2F (and one on 3F). Hours differ by counter.</li>'
      +'<li><b>eSIM:</b> install it on your phone and switch it on when you need it. No counter, no queue.</li></ul>'+SRCL;
  }
  function bagsHTML(){
    return '<ul class="pl"><li><b>Coin lockers</b> on almost every floor of both terminals and the corridor. Up to 3 days.</li>'
      +'<li><b>Too big?</b> The Baggage Port takes large cases and strollers. Cashless: IC card or QR code.</li>'
      +'<li><b>Counters:</b> Domestic 1F 7:00 to 20:00 (skis count as large), Domestic 2F 7:30 to 20:00, International 2F 9:00 to 18:00.</li>'
      +'<li><b>Same-day delivery</b> to designated hotels in Sapporo&rsquo;s Chuo Ward from Domestic 1F, near Arrival Gate 4 or 2: accepted 8:00 to 14:30.</li></ul>'+SRCL;
  }
  function hoursHTML(){
    return '<ul class="pl"><li><b>Domestic Terminal:</b> 5:00 to 23:30. <b>International Terminal:</b> 5:00 to 21:00. Corridor: 5:00 to 23:30.</li>'
      +'<li>No staying overnight after closing, except in the accommodation facilities.</li>'
      +'<li><b>Hotels:</b> Air Terminal Hotel (Domestic, by Arrival Gate 5). Portom International Hokkaido (International 4F).</li>'
      +'<li><b>Onsen:</b> Domestic 4F, 10:00 to 9:00 next morning, last entry 7:30. Late-night surcharge after 1:00. After 23:00 use the 24-hour lift (1F to 4F).</li>'
      +'<li><b>Observation deck:</b> Domestic 4F, 8:00 to 20:00, April to November only. Closed December to March.</li></ul>'+SRCL;
  }
  var NEXT=[['🚆','Train to Sapporo',trainHTML],['🚌','Bus to Sapporo',busHTML],['🚶','Between terminals',betweenHTML],['💴','Money',moneyHTML],['📶','SIM and Wi-Fi',simHTML],['🧳','Luggage',bagsHTML],['🕒','Hours and hotels',hoursHTML]];
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
  var ARR=[['Which terminal?','International flights: arrivals on International 2F. Domestic flights: arrivals on Domestic 1F.'],
    ['Money and SIM','International 2F: exchange counter and a Seven Bank ATM (overseas cards). SIM machines on International 2F and 3F, and Domestic 1F.'],
    ['Crossing to Domestic','From International 2F, walk the 2F Connecting Corridor. The 3F passage is closed until about the end of June 2027.'],
    ['Train to Sapporo','Go down to B1F under the Domestic Terminal: JR New Chitose Airport Station. Fastest 33 min (JR).'],
    ['Or the bus','Sapporo city centre: Domestic 1F stops 14 and 22, International stop 84. About 70 min to Sapporo Station.']];
  var DEP=[['Check your terminal','International departures: International 3F. Domestic departures: Domestic 2F.'],
    ['Came by train?','JR arrives at B1F under the Domestic Terminal. International flight: go up to 2F and walk the 2F corridor, then up to 3F.'],
    ['Snow or a delay?','Ask your airline about your flight. Check Hokkaido travel safety information and JR Hokkaido Train Operation Information. Leave earlier: trains and buses can be slow and crowded.'],
    ['Bags','Collect bags from lockers or the baggage counter before it closes.'],
    ['Building hours','Domestic 5:00 to 23:30, International 5:00 to 21:00. No staying overnight except in the hotels.']];
  function renderDep(){ renderSteps($('depSteps'),DEP,doneD); }
  renderSteps($('arrSteps'),ARR,doneA); renderDep();
  $('arrReset').addEventListener('click',function(){ doneA.length=0; renderSteps($('arrSteps'),ARR,doneA); syncReset(); });
  $('depReset').addEventListener('click',function(){ doneD.length=0; renderDep(); syncReset(); });
  /* departure: before you go */
  var GUIDE='__GUIDE_URL__';
  function more(a){ return '<p class="sm"><a href="'+GUIDE+a+'">More in the full guide</a> (needs internet)</p>'; }
  function winterHTML(){
    return '<div class="tipbox"><b>Snow, a delay or a cancelled flight?</b> The airport says: contact the airline you are flying with.</div>'
      +'<ul class="pl"><li>For delays and transport, it points to the airlines, the transport companies and <a href="https://hokkaido-safe-travel.mlit.go.jp/" target="_blank" rel="noopener">Hokkaido travel safety information</a> (needs internet).</li>'
      +'<li>Live trains: JR Hokkaido&rsquo;s Train Operation Information (English). It maps cancellations and delays of 30 min or more on the Chitose Line.</li>'
      +'<li>Trains stopped? JR lists the airport bus (about 70 to 90 min) and taxis (about 60 min), and warns they can get extremely crowded.</li>'
      +'<li>The terminals close at night (Domestic 23:30, International 21:00). No staying overnight, except in the accommodation facilities.</li>'
      +'<li>With a paper JR ticket, a cancelled trip is refunded in full. The station can give you a delay certificate.</li></ul>'
      +'<p class="sm">Source: New Chitose Airport FAQ and JR Hokkaido, checked 24 November 2026.</p>'+more('#winter');
  }
  function leaveHTML(){
    return '<ul class="pl"><li><b>Airport Train</b> between Sapporo and the airport: fastest 33 min (Special Rapid, JR). You arrive at B1F under the Domestic Terminal.</li>'
      +'<li><b>International flight?</b> From B1F go up to Domestic 2F, walk the 2F corridor, then up to International 3F. The 3F passage is closed.</li>'
      +'<li>First Airport Train from Sapporo: 5:50, at the airport 6:28 (JR timetable, 24 Nov 2026). Check JR the day before.</li>'
      +'<li>The terminals open at 5:00.</li></ul>'
      +'<p class="sm">Source: JR Hokkaido and New Chitose Airport, checked 24 November 2026.</p>';
  }
  function allowHTML(){
    return '<p class="n2">Two terminals and a long corridor. Add a buffer for walking, check-in and snow.</p>'
      +'<ul class="pl"><li>The airport gives no walking time between the terminals; JR&rsquo;s leaflet puts the walkway at a few hundred metres.</li>'
      +'<li>Moving walkways in the 2F corridor.</li>'
      +'<li>Bus companies say snow and traffic can delay the bus.</li></ul>'
      +'<p class="sm">Times are approximate and change. Check the operator.</p>';
  }
  var BEFORE=[['🚆','Train to the airport',leaveHTML],['❄️','Snow and delays',winterHTML],['🚶','Between terminals',betweenHTML],['⏱️','Allow time',allowHTML]];
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
  [].forEach.call(dseg.children,function(b){ b.addEventListener('click',function(){ var w=b.getAttribute('data-d'); try{localStorage.setItem('ctsDepSeg',w);}catch(e){} paintDep(w); }); });
  var dsv='before'; try{ var q=localStorage.getItem('ctsDepSeg'); if(q==='air'||q==='before') dsv=q; }catch(e){}
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
    navigator.serviceWorker.register('/new-chitose-sw.js',{scope:'/new-chitose-pocket',updateViaCache:'none'})
      .then(function(){ return navigator.serviceWorker.ready; })
      .then(function(){ return caches.has('new-chitose-pocket-v1'); })
      .then(function(ok){ saved=!!ok; if(!saved){ setTimeout(function(){ caches.has('new-chitose-pocket-v1').then(function(k){ saved=!!k; paint(); }); },2500);} paint(); })
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
  function needed(){ return mobile&&!standalone&&flag('ctsInstalled')!=='1'; }
  function refresh(){
    var n=needed(); strip.hidden=!n;
    $('instHow').hidden=!n; $('instDesk').hidden=mobile;
    if(standalone||flag('ctsInstalled')==='1'){ $('install').hidden=true; }
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
  function markInstalled(){ flag('ctsInstalled','1'); refresh(); }
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
    ['go','🏙️','Sapporo Station?','これは札幌駅に行きますか？','Kore wa Sapporo-eki ni ikimasu ka?','Does this go to Sapporo Station?'],
    ['go','🌳','Odori?','これは大通に行きますか？','Kore wa Oodoori ni ikimasu ka?','Does this go to Odori?'],
    ['go','🌃','Susukino?','これはすすきのに行きますか？','Kore wa Susukino ni ikimasu ka?','Does this go to Susukino?'],
    ['go','✈️','New Chitose Airport?','これは新千歳空港に行きますか？','Kore wa Shin-Chitose-kuukou ni ikimasu ka?','Does this go to New Chitose Airport?'],
    ['go','⚓','Otaru?','これは小樽に行きますか？','Kore wa Otaru ni ikimasu ka?','Does this go to Otaru?'],
    ['go','📞','Call a taxi','タクシーを呼んでください。','Takushii o yonde kudasai.','Please call a taxi.'],
    ['go','📍','Take me here','この住所までお願いします。','Kono juusho made onegai shimasu.','Please take me to this address. Show the address on your phone.'],
    ['go','🛑','Stop here','ここで止めてください。','Koko de tomete kudasai.','Please stop here.'],
    ['air','🎫','Ticket gate','改札はどこですか？','Kaisatsu wa doko desu ka?','Where is the ticket gate?'],
    ['air','🚆','JR station','JRの駅はどこですか？','Jeiaaru no eki wa doko desu ka?','Where is the JR station?'],
    ['air','🚌','Bus to Sapporo','札幌行きのバス乗り場はどこですか？','Sapporo-iki no basu noriba wa doko desu ka?','Where is the bus stop for Sapporo?'],
    ['air','🌏','International Terminal','国際線ターミナルはどこですか？','Kokusaisen taaminaru wa doko desu ka?','Where is the International Terminal?'],
    ['air','🗾','Domestic Terminal','国内線ターミナルはどこですか？','Kokunaisen taaminaru wa doko desu ka?','Where is the Domestic Terminal?'],
    ['air','✈️','Check-in counter','チェックインカウンターはどこですか？','Chekku-in kauntaa wa doko desu ka?','Where is the check-in counter?'],
    ['air','🛫','Missed my flight','飛行機に乗り遅れました。','Hikouki ni noriokuremashita.','I missed my flight.'],
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
  var ASKC=[['basics','Basics','👋'],['where','Where is&hellip;?','📍'],['shop','Shopping','🛍️'],['eat','Eating out','🍜'],['sights','Sights','🎡'],['go','Getting around','🚆'],['air','Airport','✈️'],['help','Help','🆘']];
  var askCat='basics'; try{ var sc=localStorage.getItem('ctsAskCat'); if(sc&&ASKC.some(function(c){return c[0]===sc;})) askCat=sc; }catch(e){}
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
    b.addEventListener('click',function(){ askCat=c[0]; try{localStorage.setItem('ctsAskCat',c[0]);}catch(e){} paintAsk(); });
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
    $('shareBtn').addEventListener('click',function(){ try{ navigator.share({title:'New Chitose Airport Pocket Guide',url:location.origin+location.pathname+'?src=share'}); }catch(e){} });
  }
  window.addEventListener('beforeinstallprompt',function(e){ e.preventDefault(); dp=e; });
  window.addEventListener('appinstalled',function(){ pgTrack('pg_installed',{via:'browser'}); markInstalled(); if(!inst.hidden) closeSheet(); });
  /*__PG_HOOKS__*/
  refresh();
  if(needed()&&!flag('ctsIntro')&&AUTO_INSTALL_SHEET){ flag('ctsIntro','1'); setTimeout(function(){ if(sheet.hidden&&inst.hidden){ instVia='auto'; openInst(); } },700); }
})();
</script>
</body>
</html>
"""
POCKET_HTML = (POCKET_HTML.replace("__CSS__", POCKET_CSS).replace("__FINDER_JSON__", json.dumps(FINDER_DATA, ensure_ascii=False)).replace("__KLP_JSON__", json.dumps({k: v for k, v in KLK.items() if v}))
               .replace("__PG_BOOT__", PG_BOOT).replace("/*__PG_HOOKS__*/", PG_HOOKS).replace("__SVG__", POCKET_SVG).replace("__GUIDE_URL__", URL))
if re.search(r"\b(India|Indian|INR|Rs\.?|rupee|lakh|Aadhaar|UPI|VFS|BLS)\b|₹", re.sub(r"<script[^>]*>.*?</script>", "", POCKET_HTML, flags=re.S)):
    die("neutral-rule violation in the pocket guide")
for _bad in ("ueno-pocket", "uenTerm", "uenInstalled", "Ueno", "Skyliner", "Keisei", "Panda", "Narita Line", "Yamanote",
             "station staff", "Tokyo Metro"):
    if _bad in POCKET_HTML or _bad in page:
        die("leftover Ueno text in the New Chitose pages: %r" % _bad)

POCKET_SW = """/* New Chitose Airport Pocket Guide service worker. Bump V when the page changes shape. */
var V='new-chitose-pocket-v1';
var PAGE='/new-chitose-pocket';
var SHELL=[PAGE,'/new-chitose-pocket.webmanifest','/favicon-32.png','/images/new-chitose-icon-192.png','/images/new-chitose-icon-512.png','/images/new-chitose-icon-maskable-512.png'];
self.addEventListener('install',function(e){
  e.waitUntil(caches.open(V).then(function(c){return c.addAll(SHELL);}).then(function(){return self.skipWaiting();}));
});
self.addEventListener('activate',function(e){
  e.waitUntil(caches.keys().then(function(ks){
    return Promise.all(ks.filter(function(k){return k.indexOf('new-chitose-pocket-')===0&&k!==V;}).map(function(k){return caches.delete(k);}));
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
    "name": "New Chitose Airport Pocket Guide",
    "short_name": "New Chitose",
    "description": "A simple New Chitose Airport helper that works offline.",
    "start_url": POCKET_PATH,
    "scope": POCKET_PATH,
    "display": "standalone",
    "background_color": THEME,
    "theme_color": "#1a1a3e",
    "lang": "en",
    "icons": [
        {"src": "/images/new-chitose-icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
        {"src": "/images/new-chitose-icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
        {"src": "/images/new-chitose-icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ],
}, indent=2) + "\n"
PUB = os.path.join(ROOT, "public")
for _ic in ("new-chitose-icon-192.png", "new-chitose-icon-512.png", "new-chitose-icon-maskable-512.png", "new-chitose-apple-touch-180.png"):
    if not os.path.isfile(os.path.join(PUB, "images", _ic)):
        die("pocket guide icon missing: public/images/" + _ic + " (the service worker would fail to install without it)")

# ---- anchors for the Japan guide link and the sitemap: check everything before writing anything
MARK = "new-chitose-airport-guide link"
jp = open(TEMPLATE, encoding="utf-8").read()
jp_new = jp
if MARK not in jp:
    anchor = re.search(r'(<!-- ueno-' + r'station-guide link -->\s*<p>.*?</p>)', jp, re.S)
    if not anchor:
        die("anchor for the Japan guide link (Ueno Station sentence) not found: run the Ueno Station generator (w68) first")
    add = ('\n\n<!-- %s -->\n<p>Flying into Hokkaido for skiing or the Snow Festival? Our <a href="/blog/%s">New Chitose Airport guide</a> explains the two terminals, '
           'the 2F corridor between them, the Airport Train and the buses to Sapporo, the ski buses, money, lockers and what to do when it snows.</p>') % (MARK, SLUG)
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
old = open(OUT, encoding="utf-8").read() if os.path.isfile(OUT) else None
if old != page:
    open(OUT, "w", encoding="utf-8").write(page)
    changed.append("new-chitose-airport-guide.html (%s bytes)" % len(page.encode("utf-8")))
for _name, _content in (("new-chitose-pocket.html", POCKET_HTML), ("new-chitose-sw.js", POCKET_SW), ("new-chitose-pocket.webmanifest", POCKET_MANIFEST)):
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
