#!/usr/bin/env python3
"""
w71: new page /blog/sapporo-station-guide + offline /sapporo-pocket (neutral, plain-English station guide for JR Sapporo
Station and the subway station under it). Built from the Ueno Station generator (w68) and the New Chitose Airport
generator (w70): same template, partner-block helpers, Sources list and Pocket Guide shell.

Run from the repo root (after w70):  python3 tools/w71_sapporo_station_page.py
Then, as for the other guides: the rest of the page generators, w44-w49 (pocket chain, cross-links, hub, trip picker),
w55, w56, w59 (Travel Essentials card), w64, w65, w66, w67 and w69 (read times).

Facts: ONLY from docs/research/sapporo-sources.md (JR Hokkaido, the Sapporo City Transportation Bureau, the Sapporo
Snow Festival's Japanese site and the Sapporo Tourist Association; checked 24 November 2026). Anything not in that file
is left out, or written as "We did not find this on the official pages. Please ask station staff." (_NONE).
The station is being rebuilt for the Hokkaido Shinkansen: JR shows its map "as of 21 October 2026" and says it may
change. Left out on purpose: the platform for the Airport Train at Sapporo (only a 2022 press release names one), the
(first and last Airport Trains added 24 Nov 2026 from JR's station timetables), locker locations and prices, the length and hours of the underground
walkway to Odori, Snow Festival opening hours and the Premist Dome site's dates, and toilets. (ATMs added 24 Nov 2026 from Seven Bank's locator.)
JR Hokkaido group hotels (section hotels, Pocket Guide sheet hotelHTML; placements hotels-sapporo-station, hotel-jr-inn-asahikawa,
hotel-jr-inn-hakodate): tracked hotel links made by the owner (D52); descriptions only from JR's own hotel list.
Day trips and ski buses (section day-trips, Pocket Guide sheets dayHTML and skiHTML) come from docs/research/sapporo-daytrips-sources.md
(JR Hokkaido, Donan Bus, Asahiyama Zoo, Hokkaido Chuo Bus and Niseko Bus; checked 24 November 2026), with one tours link
(placement gyg-sapporo-daytrips, cmp ps-sapporo-station-daytrips).

Partner blocks (no new programmes, no Klook, no hotel links): the eSIM tiles copied from the Japan guide (placement
id airalo-sapporo-station) and a tours-and-tickets box with a search for Sapporo (gyg-sapporo-station,
cmp ps-sapporo-station-gyg). No luggage-storage callout (the existing tracked link is for Tokyo), no bullet-train box
(the Shinkansen does not reach Sapporo yet), no airport-transfer or car-rental block (no checked pick-up location for
Sapporo in those widgets yet). KLK stays empty.

What it does (idempotent):
  1. Builds public/blog/sapporo-station-guide.html from the site template taken from
     public/blog/japan-travel-packing-guide.html (head, CSS, nav, footer, tracking scripts) plus new body content.
  2. Builds public/sapporo-pocket.html (offline Pocket Guide), sapporo-sw.js and sapporo-pocket.webmanifest
     (cache sapporo-pocket-v1; later scripts bump it; storage prefix "spr", as w44 expects).
  3. Makes public/images/sapporo-odori-aerial-1600.jpg from sapporo-odori-aerial.jpg (PAKUTASO, checked by eye:
     Odori Park from above in summer, no identifiable people; sips on a Mac, Pillow elsewhere; an existing copy is kept).
  4. Adds one sentence linking to the new page in the Japan guide (marker: sapporo-station-guide link),
     right after the New Chitose Airport guide sentence that w70 adds.
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
OUT = os.path.join(BLOG, "sapporo-station-guide.html")
SITE = "https://www.packsmartapp.com"
SLUG = "sapporo-station-guide"
URL = "%s/blog/%s" % (SITE, SLUG)
TODAY = "2026-11-24"
READ_MIN = 10   # placeholder only: w69 sets the real read time from the words on the page

TITLE = "Sapporo Station Guide 2026: Gates, Subway to Odori, Lockers & Snow Festival | PackSmart Blog"
H1 = "Sapporo Station Guide 2026: Gates, Subway to Odori, Lockers, the Snow Festival and the Airport Train"
DESC = ("Plain-English Sapporo Station guide: West and East gates during the Shinkansen works, the subway to Odori, "
        "lockers, Snow Festival 2027 and the airport train.")
KEYWORDS = ("Sapporo Station guide, Sapporo Station map, Sapporo Station lockers, Sapporo subway Namboku Line, Sapporo to Odori, "
            "Sapporo Snow Festival 2027, Sapporo Station to New Chitose Airport, Sapporo Station construction, Hokkaido Shinkansen Sapporo")

# ---- official sources (docs/research/sapporo-sources.md), checked 24 November 2026
CHECKED = "Checked 24 November 2026."
_C = "https://www.city.sapporo.jp/"
SRC = {
    "jrconst": ("https://www.jrhokkaido.co.jp/construction/", "JR Hokkaido: Sapporo Station construction and station map (as of 21 October 2026)"),
    "jrstn": ("https://www.jrhokkaido.co.jp/network/station/station.html", "JR Hokkaido: station search (Sapporo)"),
    "jrinfo": ("https://www.jrhokkaido.co.jp/global/english/travel/info.html", "JR Hokkaido: JR Information Desk"),
    "jrlock": ("https://www.jrhokkaido.co.jp/network/locker/locker.pdf", "JR Hokkaido: coin locker list (PDF, July 2026)"),
    "jrfaq7": ("https://www.jrhokkaido.co.jp/global/english/faq/faq07.html", "JR Hokkaido: FAQ on coin lockers"),
    "jrhome": ("https://www.jrhokkaido.co.jp/global/index.html", "JR Hokkaido: English home page (notices)"),
    "jrops": ("https://www3.jrhokkaido.co.jp/webunkou/index_en.html", "JR Hokkaido: Train Operation Information (English)"),
    "jrttcts": ("https://www3.jrhokkaido.co.jp/webunkou/timetable_en.html?id=246", "JR Hokkaido: New Chitose Airport departures, 24 Nov 2026"),
    "jrttspk": ("https://www3.jrhokkaido.co.jp/webunkou/timetable_en.html?id=091", "JR Hokkaido: Sapporo departures, Chitose Line, 24 Nov 2026"),
    "jrwifi": ("https://www.jrhokkaido.co.jp/global/english/travel/wifi.html", "JR Hokkaido: Wi-Fi guide"),
    "jrair": ("https://www.jrhokkaido.co.jp/global/english/travel/airport.html", "JR Hokkaido: Airport Train (New Chitose Airport, Sapporo, Otaru)"),
    "jrdis": ("https://www.jrhokkaido.co.jp/global/english/travel/airport_disruption.html", "JR Hokkaido: when train services are disrupted"),
    "jrhak": ("https://www.jrhokkaido.co.jp/global/english/train/guide/hakodate.html", "JR Hokkaido: Sapporo to Hakodate (Limited Express Hokuto)"),
    "jrasa": ("https://www.jrhokkaido.co.jp/global/english/train/guide/asahikawa.html", "JR Hokkaido: Sapporo to Asahikawa"),
    "jrshin": ("https://www.jrhokkaido.co.jp/global/english/shinkansen/station.html", "JR Hokkaido: Hokkaido Shinkansen stations"),
    "stinfo": ("https://www.sapporo.travel/en/info/about/informationcenter/", "Sapporo Tourist Association: Hokkaido-Sapporo Tourist Information Center"),
    "sttrans": ("https://www.sapporo.travel/en/info/about/transportation/", "Sapporo Tourist Association: transportation"),
    "stlock": ("https://www.sapporo.travel/useful_information/how_to_use_coin-operated_lockers_in_japan/?lang=en", "Sapporo Tourist Association: how to use coin lockers"),
    "stvnews": ("https://www.sapporo.travel/en/news/important-information-for-travelers-to-sapporo/", "Sapporo Tourist Association: important information for travelers (17 December 2025)"),
    "submap": (_C + "documents/23641/sapporo.pdf", "Sapporo City Transportation Bureau: Sapporo subway station map (PDF, February 2026)"),
    "subtime": (_C + "st/s110/23601.html", "Sapporo City Transportation Bureau: journey times between stations"),
    "subtt": (_C + "documents/113189/06satsu.pdf", "Sapporo City Transportation Bureau: Sapporo subway station timetable (PDF, 28 February 2025)"),
    "subnum": (_C + "st/s110/113189.html", "Sapporo City Transportation Bureau: station timetables"),
    "subxfer": (_C + "st/s110/127449.html", "Sapporo City Transportation Bureau: changing lines at Sapporo Station"),
    "snow": ("https://www.snowfes.com/", "Sapporo Snow Festival (official site, Japanese)"),
    "ctsjr": ("https://www.hokkaido-airports.com/en/new-chitose/access/jr/", "New Chitose Airport: access by JR"),
    "sbintl": ("https://www.sevenbank.co.jp/intlcard/index2.html", "Seven Bank: cards issued outside Japan"),
    "sbjrspk": ("https://location.sevenbank.co.jp/sevenbank/spot/detail?code=0000038030", "Seven Bank ATM: JR Hokkaido Sapporo Station"),
    "sbnamboku": ("https://location.sevenbank.co.jp/sevenbank/spot/detail?code=0000029337", "Seven Bank ATM: subway Namboku Line, Sapporo"),
    "sbtoho": ("https://location.sevenbank.co.jp/sevenbank/spot/detail?code=0000027385", "Seven Bank ATM: subway Toho Line, Sapporo"),
    "sbapia": ("https://location.sevenbank.co.jp/sevenbank/spot/detail?code=0000009330", "Seven Bank ATM: JR Tower APIA"),
    "sbodori": ("https://location.sevenbank.co.jp/sevenbank/spot/detail?code=0000026672", "Seven Bank ATM: subway Odori station"),
    "jrpass": ("https://www.jrhokkaido.co.jp/global/english/ticket/railpass/index.html", "JR Hokkaido: rail passes for visitors"),
    "chuoair": ("https://www.chuo-bus.co.jp/feature/airport/", "Hokkaido Chuo Bus and Hokuto Kotsu: airport buses from 11 December 2026"),
    "jrhotels": ("https://www.jrhokkaido.co.jp/global/english/travel/link.html#lnk03", "JR Hokkaido: JR Hokkaido Group Hotels"),
    "jrallres": ("https://www.jrhokkaido.co.jp/CM/Info/notice_en/pdf/all_reserved_202602_en.pdf", "JR Hokkaido: all limited expresses reserved from 14 March 2026 (PDF)"),
    "jrusage": ("https://www.jrhokkaido.co.jp/global/english/ticket/usage/usage03.html", "JR Hokkaido: reserved seats with a rail pass"),
    "jrmanner": ("https://www.jrhokkaido.co.jp/global/pdf/e-cn-mannerguide.pdf", "JR Hokkaido: manner and user guide (PDF)"),
    "jracc": ("https://www.jrhokkaido.co.jp/global/pdf/e-accessibility2025.pdf", "JR Hokkaido: accessibility guide (PDF)"),
    "jretix": ("https://www.jrhokkaido.co.jp/CM/Info/news_en/pdf/ltdexp_eticket_202611_en.pdf", "JR Hokkaido: limited express e-tickets, Sapporo to Asahikawa (PDF)"),
    "jrmodnob": ("https://www.jrhokkaido.co.jp/global/english/travel/model/noboribetsu.html", "JR Hokkaido: Otaru, Noboribetsu and Upopoy routes"),
    "jrmodfur": ("https://www.jrhokkaido.co.jp/global/english/travel/model/furano.html", "JR Hokkaido: Asahikawa, Biei and Furano routes"),
    "jrfaq9": ("https://www.jrhokkaido.co.jp/global/english/faq/faq09.html", "JR Hokkaido: FAQ on Furano and Biei"),
    "jrfbtrain": ("https://www.jrhokkaido.co.jp/global/english/travel/furanobiei/train/index.html", "JR Hokkaido: Furano Lavender Express (June to September)"),
    "ttotaru": ("https://www3.jrhokkaido.co.jp/webunkou/timetable_en.html?id=076", "JR Hokkaido: Otaru departures, 24 Nov 2026"),
    "ttnob": ("https://www3.jrhokkaido.co.jp/webunkou/timetable_en.html?id=205", "JR Hokkaido: Noboribetsu departures, 24 Nov 2026"),
    "ttasa": ("https://www3.jrhokkaido.co.jp/webunkou/timetable_en.html?id=118", "JR Hokkaido: Asahikawa departures, 24 Nov 2026"),
    "ttbiei": ("https://www3.jrhokkaido.co.jp/webunkou/timetable_en.html?id=507", "JR Hokkaido: Biei departures, 24 Nov 2026"),
    "jtnob": ("https://www.japan.travel/en/destinations/hokkaido/hokkaido/noboribetsu-upopoy-and-around/", "Japan National Tourism Organization: Noboribetsu and Upopoy"),
    "donanstn": ("https://www.donanbus.co.jp/map/noboribetsu_ashiyu/?hp_lang=en", "Donan Bus: Noboribetsu Station to Noboribetsu Onsen"),
    "donanback": ("https://www.donanbus.co.jp/map/noboribetsu_ashiyu2/?hp_lang=en", "Donan Bus: Noboribetsu Onsen to Noboribetsu Station"),
    "zoowin": ("https://www.city.asahikawa.hokkaido.jp/asahiyamazoo/news-blog/osirase/d082799.html", "Asahiyama Zoo: winter opening 2026-27 (Japanese)"),
    "zooacc": ("https://www.city.asahikawa.hokkaido.jp/asahiyamazoo/generalinformation/d053767.html", "Asahiyama Zoo: access (Japanese)"),
    "skibus": ("https://teikan.chuo-bus.co.jp/en/course/18958", "Hokkaido Chuo Bus: Niseko ski bus (English)"),
    "skipdf": ("https://www.nisekobus.co.jp/uploads/2026冬-スキーバス.pdf", "Niseko Bus: ski bus timetable 2026-27 (PDF, Japanese)"),
    "skibook": ("https://teikan.chuo-bus.co.jp/multi/skibus.html?lang=en", "Hokkaido Chuo Bus: ski bus booking (English)"),
    "skikok": ("https://teikan.chuo-bus.co.jp/course/16756", "Hokkaido Chuo Bus: Sapporo Kokusai ski area bus (Japanese)"),
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


airalo = block("airalo-japan").replace("airalo-japan", "airalo-sapporo-station")
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
    ("How do I get from Sapporo Station to Odori Park?",
     "Take the subway Namboku Line from Sapporo (N06) one stop to Odori (N07): the city gives 2 minutes. "
     "The subway map also shows Exit 11 leading into the Sapporo Ekimae-dori underground walkway, which runs towards Odori; we did not find where it comes out, its length or its hours."),
    ("How do I get from Sapporo Station to Susukino?",
     "The Namboku Line from Sapporo (N06) to Susukino (N08) takes 3 minutes, according to the Sapporo City Transportation Bureau."),
    ("When is the Sapporo Snow Festival 2027?",
     "The festival's official Japanese site gives Thursday 4 February to Thursday 11 February 2027 (a national holiday) at all three main sites: "
     "Odori Park, Tsudome and Susukino. It also lists a Premist Dome site, with no 2027 dates yet. Opening and lighting times were not on the page."),
    ("Is Sapporo Station under construction?",
     "Yes. JR Hokkaido is rebuilding parts of the station for the Hokkaido Shinkansen extension to Sapporo. Its station map is dated 21 October 2026 "
     "and JR says it may change as work goes on. The map shows some areas under construction, and some lifts and escalators by the East gate out of use."),
    ("Does the Shinkansen go to Sapporo?",
     "Not yet. JR Hokkaido's Hokkaido Shinkansen stations are Shin-Hakodate-Hokuto, Kikonai and Okutsugaru-Imabetsu, and JR describes its work at Sapporo as towards the opening of the Sapporo station. "
     "From Sapporo, the Limited Express Hokuto goes to Hakodate and connects with the Shinkansen."),
    ("How do I get from Sapporo Station to New Chitose Airport?",
     "On JR Hokkaido's Airport Train. JR gives the fastest time between the airport and Sapporo as 33 minutes (Special Rapid), and IC cards such as Suica work. "
     "Check the departure boards for your platform: we did not find a current official platform list."),
    ("Where are the coin lockers at Sapporo Station?",
     "JR's locker list (July 2026) gives about 800 lockers at Sapporo, a number that changes with the construction, and 5 lockers for skis and snowboards. "
     "We did not find a locker map, so follow the signs or ask station staff. Lockers can be used for up to 3 days, counting the first day."),
    ("Can I change between the Namboku and Toho lines at Sapporo without leaving the gates?",
     "No. The city says you have to go out through the gates and come back in within 30 minutes. With a paper ticket, use the yellow transfer gates at the Namboku and Toho south gates."),
    ("Where is the tourist information at Sapporo Station?",
     "The Hokkaido-Sapporo Tourist Information Center is in the JR Sapporo West Concourse, open 8:30 to 20:00 all year, in Japanese, English, Chinese and Korean. "
     "JR's own Information Desk for visitors is at the West Exit."),
    ("Can I do a day trip from Sapporo by train?",
     "Yes. On JR Hokkaido's timetable for 24 November 2026, Otaru is 34 to 46 minutes by the Rapid Airport, Noboribetsu 70 to 82 minutes and Asahikawa 85 minutes by limited express. "
     "All seats on limited expresses are reserved, so book a seat, and JR says IC cards cannot be used to Noboribetsu, Biei or Furano. For Niseko, the booked ski bus from the North Exit takes about 3 hours."),
    ("Is the subway station called Sapporo too?",
     "Yes, but the subway writes it in hiragana, さっぽろ, while JR writes 札幌. Both are read Sapporo."),
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
    "about": {"@type": "TrainStation", "name": "Sapporo Station"},
}
ld_crumbs = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE},
        {"@type": "ListItem", "position": 2, "name": "Travel Essentials", "item": SITE + "/travel-essentials"},
        {"@type": "ListItem", "position": 3, "name": "Sapporo Station Guide", "item": URL},
    ],
}


def ld(obj):
    return '<script type="application/ld+json">\n%s\n</script>' % json.dumps(obj, ensure_ascii=False)


TOC = [
    ("one-page", "Sapporo Station on one page"),
    ("construction", "Under construction: what it means for you"),
    ("gates", "Gates and exits: West and East"),
    ("desks", "Information, tickets and tourist help"),
    ("subway", "Subway: Namboku and Toho lines, to Odori and Susukino"),
    ("snow-festival", "Sapporo Snow Festival 2027"),
    ("airport", "To New Chitose Airport: the Airport Train"),
    ("long-distance", "Hakodate, Asahikawa, Otaru and the Shinkansen"),
    ("day-trips", "Day trips by train, and ski buses"),
    ("connected", "Getting online: eSIM"),
    ("money", "Money and ATMs"),
    ("luggage", "Lockers and luggage"),
    ("finder", "Find it fast: by side"),
    ("hotels", "Staying by the station: JR Hokkaido's hotels"),
    ("leaving", "Leaving Sapporo: a checklist"),
    ("faq", "FAQ"),
    ("about-this-guide", "About this guide and change log"),
]
# ---- "What do you need first?" tiles + a quick-jump bar that appears once you scroll (as w42)
TOC_SHORT = {
    "one-page": "On one page", "construction": "Construction", "gates": "Gates", "desks": "Help desks", "subway": "Subway",
    "snow-festival": "Snow Festival", "airport": "To the airport", "long-distance": "Other trains", "day-trips": "Day trips", "connected": "Get online",
    "money": "ATMs", "luggage": "Lockers", "finder": "Find it fast", "hotels": "Hotels", "leaving": "Leaving", "faq": "FAQ", "about-this-guide": "About",
}
TOC_TILES = [
    ("subway", "&#128647;", "Subway to Odori", "Namboku N06, 2 min"),
    ("snow-festival", "&#10052;&#65039;", "Snow Festival", "4 to 11 Feb 2027"),
    ("airport", "&#9992;&#65039;", "To the airport", "33 min fastest"),
    ("gates", "&#128682;", "Which gate?", "West or East"),
    ("construction", "&#128679;", "Construction", "Lifts, map changes"),
    ("luggage", "&#129523;", "Lockers", "About 800, ski lockers"),
    ("desks", "&#8505;&#65039;", "Help desks", "JR and tourist info"),
    ("day-trips", "&#127956;&#65039;", "Day trips", "Otaru, onsen, ski bus"),
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
.ps-sources{font-size:0.9rem;line-height:1.6;}.ps-srcbox{margin:0 0 24px}.ps-srcbox summary{cursor:pointer;color:#0a8f78;font-weight:700;padding:8px 0;min-height:44px;display:flex;align-items:center}
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


DG_H = 772
_DG_SVG = (
    '<svg id="sprDiagram" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 %d" role="img" aria-labelledby="sprT sprD" font-family="Arial, Helvetica, sans-serif">' % DG_H
    + '<title id="sprT">Sapporo Station at a glance</title>'
    '<desc id="sprD">JR Sapporo Station, simplified from JR Hokkaido\'s map as of 21 October 2026. North: the North Exit plaza. '
    'Inside the ticket gates: stairs to platforms 2 to 11. Two ticket gates: the West gate (the JR Information Desk and the tourist information center are on the west side) '
    'and the East gate (some lifts and escalators there are out of use during construction). Indoor and outdoor passages run east to west along the south side. '
    'South: the South Exit plaza with taxis, Daimaru to the south-west and Sapporo Stellar Place to the south and south-east. '
    'Underground: the subway Namboku Line (N06) towards the west side and the Toho Line (H07) towards the east side. Odori is 2 minutes on the Namboku Line.</desc>'
    '<rect width="480" height="%d" fill="#fff"/>' % DG_H
    + '<text x="240" y="38" font-size="26" font-weight="700" text-anchor="middle" fill="#0f0f23">Sapporo Station at a glance</text>'
    '<text x="240" y="64" font-size="17" text-anchor="middle" fill="#555">North at the top. Under construction</text>'
    '<rect x="24" y="84" width="432" height="56" rx="18" fill="#EEF0FB" stroke="#34346e" stroke-width="2"/>'
    '<text x="240" y="119" font-size="20" font-weight="700" text-anchor="middle" fill="#0f0f23">North Exit plaza</text>'
    '<rect x="24" y="150" width="432" height="104" rx="18" fill="#E8F1FE" stroke="#2563EB" stroke-width="2"/>'
    '<text x="48" y="184" font-size="22" font-weight="700" fill="#0f0f23">JR platforms 2 to 11</text>'
    + _dg_pill(202, "Check the boards for your train", "#fff", "#2563EB", "#1e40af")
    + '<rect x="24" y="264" width="206" height="128" rx="18" fill="#E6FAF5" stroke="#0a8f78" stroke-width="2"/>'
    '<text x="127" y="300" font-size="21" font-weight="700" text-anchor="middle" fill="#0f0f23">West gate</text>'
    '<text x="127" y="328" font-size="15" text-anchor="middle" fill="#0a6b5a">JR Information Desk</text>'
    '<text x="127" y="350" font-size="15" text-anchor="middle" fill="#0a6b5a">Tourist information</text>'
    '<text x="127" y="372" font-size="15" text-anchor="middle" fill="#0a6b5a">&#8595; Namboku Line</text>'
    '<rect x="250" y="264" width="206" height="128" rx="18" fill="#FFF6E5" stroke="#b45309" stroke-width="2"/>'
    '<text x="353" y="300" font-size="21" font-weight="700" text-anchor="middle" fill="#0f0f23">East gate</text>'
    '<text x="353" y="328" font-size="15" text-anchor="middle" fill="#a3243b">Some lifts and</text>'
    '<text x="353" y="350" font-size="15" text-anchor="middle" fill="#a3243b">escalators closed</text>'
    '<text x="353" y="372" font-size="15" text-anchor="middle" fill="#7c4a03">&#8595; Toho Line</text>'
    '<rect x="24" y="402" width="432" height="56" rx="18" fill="#F5F5F5" stroke="#999" stroke-width="2"/>'
    '<text x="240" y="437" font-size="17" font-weight="600" text-anchor="middle" fill="#333">Indoor and outdoor passages, east to west</text>'
    '<rect x="24" y="468" width="432" height="112" rx="18" fill="#EEF0FB" stroke="#34346e" stroke-width="2"/>'
    '<text x="48" y="502" font-size="22" font-weight="700" fill="#0f0f23">South Exit plaza, taxis</text>'
    + _dg_pill(522, "Daimaru (SW), Stellar Place (S, SE)", "#fff", "#34346e", "#1a1a3e")
    + '<rect x="24" y="590" width="432" height="140" rx="18" fill="#E7FAF5" stroke="#00A98C" stroke-width="2"/>'
    '<text x="48" y="624" font-size="22" font-weight="700" fill="#0f0f23">Underground: subway</text>'
    + _dg_pill(640, "Namboku N06: Odori 2 min", "#fff", "#00A98C", "#0a6b5a", "700")
    + _dg_pill(684, "Toho H07 (east side)", "#fff", "#00A98C", "#0a6b5a")
    + '<text x="240" y="758" font-size="14" text-anchor="middle" fill="#777">Simplified, not to scale. packsmartapp.com</text></svg>'
)

DIAGRAM = '<figure class="ps-fig" id="at-a-glance">\n' + _DG_SVG + """
<button type="button" class="ps-btn2" id="sprDl">Download the diagram (PNG)</button>
</figure>
<script>
(function(){
  var b=document.getElementById('sprDl'); if(!b) return;
  b.addEventListener('click',function(){
    try{
      var svg=document.getElementById('sprDiagram');
      var xml=new XMLSerializer().serializeToString(svg);
      var img=new Image();
      img.onload=function(){
        var c=document.createElement('canvas'); c.width=960; c.height=""" + str(2 * DG_H) + """;
        var x=c.getContext('2d'); x.fillStyle='#fff'; x.fillRect(0,0,c.width,c.height); x.drawImage(img,0,0,c.width,c.height);
        c.toBlob(function(bl){
          var a=document.createElement('a'); a.href=URL.createObjectURL(bl); a.download='sapporo-station-at-a-glance.png';
          document.body.appendChild(a); a.click(); document.body.removeChild(a);
        },'image/png');
      };
      img.src='data:image/svg+xml;charset=utf-8,'+encodeURIComponent(xml);
    }catch(e){ window.print(); }
  });
})();
</script>"""
_NONE = "We did not find this on the official pages. Please ask station staff."
_BOTH = lambda s: {"T1": s, "T2": s}
FINDER_DATA = {
    "terms": [["T1", "West gate side"], ["T2", "East gate side"]],
    "items": [
        ["info", "Information", {
            "T1": "JR Information Desk for visitors, at the West Exit, outside the West gate towards the North Exit side: 8:30 to 19:00 (JR's map, undated), help in English, Chinese and Korean. Hokkaido-Sapporo Tourist Information Center, in the JR Sapporo West Concourse: 8:30 to 20:00, all year.",
            "T2": "The JR Information Desk and the Hokkaido-Sapporo Tourist Information Center are both on the west side (West Exit and West Concourse). Ask station staff at the East gate for the way."}],
        ["tickets", "Tickets and passes", _BOTH("JR ticket office: 5:40 to 22:00. Reserved-seat and talking ticket machines: 5:30 to 23:50 (operator help 6:00 to 23:00). The JR Information Desk at the West Exit sells rail passes and tickets and exchanges rail pass vouchers. We did not find where the ticket office is on JR's current map: follow the signs.")],
        ["lockers", "Lockers", _BOTH("About 800 coin lockers (JR says the number changes with the construction), including 5 for skis and snowboards. Up to 3 days, counting the first day. Key lockers take only 100-yen coins; touch-panel lockers work in English, simplified Chinese and Korean. Open 5:15 to midnight. We did not find a locker map: follow the signs.")],
        ["subway", "Subway", {
            "T1": "Namboku Line, Sapporo (N06): JR's map points to it from the west side. Odori (N07) 2 min, Susukino (N08) 3 min.",
            "T2": "Toho Line, Sapporo (H07): JR's map points to it from the east side. Changing to the Namboku Line means going out through the gates and back in within 30 minutes."}],
        ["help", "Lifts and help", {
            "T1": "Ask station staff for the step-free route: the station is under construction and the routes change. In an emergency, call 119.",
            "T2": "JR's map (21 October 2026) shows some lifts and escalators by the East gate out of use; the stairs can be used. Ask station staff for the step-free route. In an emergency, call 119."}],
        ["taxi", "Taxis", _BOTH("The taxi stand is at the South Exit plaza (JR's map).")],
        ["food", "Shops and food", {
            "T1": "Daimaru Sapporo, to the south-west, and Sapporo Stellar Place (Center), south of the gates (JR's map).",
            "T2": "Sapporo Stellar Place (East), to the south-east (JR's map)."}],
        ["money", "Money and ATMs", {
            "T1": "JR Sapporo Station has a Seven Bank ATM on the West gate side, 5:10 to 24:00. More in the Namboku Line subway concourse (N06), outside the gates, 6:00 to 24:00. Seven Bank ATMs take cards issued abroad.",
            "T2": "Toho Line subway (H07): a Seven Bank ATM on B1 near the South gate, 6:00 to 24:00. JR's own Seven Bank ATM is on the West gate side, 5:10 to 24:00. They take cards issued abroad."}],
        ["toilet", "Toilets", _BOTH("We did not find toilet locations in words on the official pages. Follow the signs, or ask station staff.")],
        ["unwell", "Feeling unwell", _BOTH("Tell station staff. In an emergency, call 119.")],
    ],
}
_ORDER = ["info", "tickets", "lockers", "subway", "help", "taxi", "food", "money", "toilet", "unwell"]
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
    if(!term||!what){ rEl.textContent=!term?'Now choose your side.':'Now choose what you need.'; return; }
    var tn=D.terms.filter(function(t){return t[0]===term;})[0][1];
    var it=D.items.filter(function(i){return i[0]===what;})[0];
    var txt=it[2][term];
    rEl.innerHTML='';
    var s=document.createElement('strong'); s.textContent=it[1]+': '+tn; rEl.appendChild(s);
    rEl.appendChild(document.createElement('br'));
    rEl.appendChild(document.createTextNode(txt?txt:'We did not find this on the official pages. Please ask station staff.'));
    var sm=document.createElement('small'); sm.textContent='From JR Hokkaido (station map as of 21 October 2026), the Sapporo City Transportation Bureau and the Sapporo Tourist Association, checked 24 November 2026. The station is under construction, so routes change. If you cannot find it, ask station staff.'; rEl.appendChild(sm);
  }
})();
</script>"""
FINDER = FINDER.replace("__FINDER_JSON__", json.dumps(FINDER_DATA, ensure_ascii=False))

CARD = """<div class="ps-card" id="one-page">
<h2>Sapporo Station on one page</h2>
<ul>
<li><strong>Under construction:</strong> JR is rebuilding parts of the station for the Shinkansen. Its map is dated 21 October 2026 and may change. Some lifts and escalators by the East gate are out of use.</li>
<li><strong>Two ticket gates:</strong> the West gate and the East gate. North Exit plaza and South Exit plaza (taxis).</li>
<li><strong>Subway:</strong> Namboku Line N06 (west side) to Odori in 2 minutes and Susukino in 3. Toho Line H07 (east side).</li>
<li><strong>Help:</strong> JR Information Desk at the West Exit (8:30 to 19:00). Tourist Information Center in the West Concourse (8:30 to 20:00).</li>
<li><strong>Lockers:</strong> about 800, plus 5 for skis and snowboards. Up to 3 days.</li>
<li><strong>To New Chitose Airport:</strong> JR's Airport Train, fastest 33 minutes. Check the boards for your platform.</li>
<li><strong>Snow Festival 2027:</strong> 4 to 11 February at Odori Park, Tsudome and Susukino.</li>
<li><strong>Shinkansen:</strong> not in Sapporo yet. For Hakodate, take the Limited Express Hokuto.</li>
</ul>
<div class="ps-qr ps-qr-screen">__QR_SCREEN__<p><strong>Want it on your phone?</strong> Point your phone camera at this code. It opens the Sapporo Station Pocket Guide: no app to install, and it works without internet once opened.<span class="u">packsmartapp.com/sapporo-pocket</span></p></div>
<div class="ps-qr ps-qr-print">__QR_PRINT__<p><strong>Sapporo Station Pocket Guide. No app needed.</strong> Point your phone camera at this code. Open it once with signal and it works without internet.<span class="u">packsmartapp.com/sapporo-pocket</span></p></div>
<button type="button" class="ps-print-btn" onclick="window.print()">Print this card</button>
</div>"""

CONSTRUCTION = """<h2 id="construction">Under construction: what it means for you</h2>
<div class="ps-warn" role="note"><strong class="h">&#128679; Sapporo Station is being rebuilt for the Hokkaido Shinkansen</strong>
<p>JR Hokkaido is working on the station for the Hokkaido Shinkansen extension to Sapporo. Its station search page does not show a normal map of Sapporo: it sends you to the construction page, whose station map is dated <strong>21 October 2026</strong> and &ldquo;may change as work progresses&rdquo;.</p>
<p><strong>What the map shows:</strong> several areas under construction (some still passable), and some escalators and lifts by the East gate out of use, with the stairs usable.</p></div>
<ul>
<li><strong>Follow the signs on the day.</strong> Walkways move as the work goes on, so a route from an old map or video may be closed.</li>
<li><strong>Need step-free access?</strong> Ask station staff before you set off, especially on the East gate side.</li>
<li><strong>Allow extra time.</strong> We did not find official walking times inside the station, so add a buffer, especially with luggage or skis.</li>
</ul>
""" + sources(["jrconst", "jrstn"], "The map may change as the work goes on.")

GATES = """<h2 id="gates">Gates and exits: West and East</h2>
<p>JR's station map (as of 21 October 2026) shows two ticket gates and two exit plazas. Platform stairs 2 to 11 are inside the gates. The subway is underground, with the Namboku Line towards the west and the Toho Line towards the east.</p>
<div class="ps-scroll">
<table class="checklist-table">
<thead><tr><th>Going to</th><th>Use</th><th>Good to know</th></tr></thead>
<tbody>
<tr><td><strong>Subway Namboku Line</strong> (Odori, Susukino)</td><td>West side</td><td>JR's map points &ldquo;to Namboku Line&rdquo; near the west side.</td></tr>
<tr><td><strong>Subway Toho Line</strong></td><td>East side</td><td>JR's map points &ldquo;to Toho Line&rdquo; near the east side.</td></tr>
<tr><td><strong>JR Information Desk, tourist information</strong></td><td>West gate</td><td>The desk is outside the West gate, towards the North Exit side; the tourist information center is in the West Concourse.</td></tr>
<tr><td><strong>Taxis</strong></td><td>South Exit plaza</td><td>The map marks the taxi stand on the south side.</td></tr>
<tr><td><strong>Daimaru, Sapporo Stellar Place</strong></td><td>South side</td><td>Daimaru Sapporo is to the south-west; Stellar Place (Center) south of the gates, and Stellar Place (East) to the south-east.</td></tr>
<tr><td><strong>North side</strong></td><td>North Exit plaza</td><td>Named on JR's map. We did not find directions from it in words.</td></tr>
<tr><td><strong>East to west along the station</strong></td><td>Indoor or outdoor passage</td><td>Both run along the south side on JR's map.</td></tr>
</tbody>
</table>
</div>
""" + sources(["jrconst", "jrinfo", "stinfo"], "Routes change with the construction, so follow the signs.")

DESKS = """<h2 id="desks">Information, tickets and tourist help</h2>
<ul>
<li><strong>JR Information Desk (for visitors).</strong> At the JR Sapporo Station West Exit. JR says it helps in English, Chinese and Korean (not every language is always available), exchanges rail pass vouchers, and sells rail passes and train tickets. Hours on JR's map: 8:30 to 19:00 (the map is undated, so check).</li>
<li><strong>JR ticket office.</strong> 5:40 to 22:00. Reserved-seat and talking ticket machines 5:30 to 23:50 (with an operator 6:00 to 23:00).</li>
<li><strong>Hokkaido-Sapporo Tourist Information Center.</strong> In the Hokkaido-Sapporo &ldquo;Food and Tourism&rdquo; Information Building, JR Sapporo West Concourse (Kita 6-jo Nishi 4-chome). 8:30 to 20:00, open all year, in Japanese, English, Chinese and Korean.</li>
<li><strong>Station staff.</strong> Tell staff at a ticket gate if you need help or are not sure which way to go. In an emergency, call 119.</li>
<li><strong>Busy station.</strong> The Sapporo Tourist Association says about 90,000 people a day use JR Sapporo Station, JR Hokkaido's largest hub.</li>
</ul>
""" + sources(["jrinfo", "jrstn", "stinfo", "sttrans"], "Hours can change.")

SUBWAY = """<h2 id="subway">Subway: Namboku and Toho lines, to Odori and Susukino</h2>
<p>The subway station under JR Sapporo is called Sapporo too, but the city writes it in hiragana, <strong>さっぽろ</strong>, while JR writes 札幌. Two lines stop here: the <strong>Namboku Line (N06)</strong> and the <strong>Toho Line (H07)</strong>.</p>
<ul>
<li><strong>To Odori (Snow Festival main site).</strong> Namboku Line to Odori (N07): 2 minutes.</li>
<li><strong>To Susukino.</strong> Namboku Line to Susukino (N08): 3 minutes. The Toho Line has a station called Hosui-Susukino (H09).</li>
<li><strong>First and last trains towards Odori.</strong> On the timetable dated 28 February 2025, trains towards Makomanai (via Odori and Susukino) leave Sapporo from 6:09 to 0:09, on weekdays and at weekends. Towards Asabu: 6:18 to 0:18. Check the city's current timetable before a late night out.</li>
<li><strong>Changing between Namboku and Toho.</strong> You have to go out through the gates and come back in within 30 minutes. With a paper ticket, use the yellow transfer gates (three each at the Namboku and Toho south gates). Go in through the gate of the line you plan to ride: if you enter at the Namboku gates, you cannot leave towards the Toho Line.</li>
<li><strong>Exits.</strong> The city's map shows Exits 2 and 18 leading to JR Sapporo Station, and Exit 11 into the Sapporo Ekimae-dori underground walkway, which runs towards Odori. We did not find where the walkway comes out, its length or its hours. <strong>Exits 4 and 5 have been closed since 3 August 2024.</strong></li>
<li><strong>Odori has three stations:</strong> N07 on the Namboku Line, H08 on the Toho Line and T09 on the Tozai Line.</li>
</ul>
""" + sources(["submap", "subnum", "subtime", "subtt", "subxfer", "jrconst"], "Timetables change, so check the city's pages.")

SNOW = """<h2 id="snow-festival">Sapporo Snow Festival 2027</h2>
<p>The festival's official Japanese site gives the 2027 dates as <strong>Thursday 4 February to Thursday 11 February 2027</strong> (11 February is a national holiday) at all three main sites. Its English page still shows older years, so go by the Japanese page.</p>
<ul>
<li><strong>Odori Park site.</strong> Odori Park from Nishi 1-chome to Nishi 11-chome: the big snow sculptures and projection mapping. Subway Namboku Line from Sapporo to Odori, 2 minutes.</li>
<li><strong>Susukino site.</strong> Ice sculptures. Namboku Line from Sapporo to Susukino, 3 minutes.</li>
<li><strong>Tsudome site.</strong> Slides, snow rafts and indoor food booths. We did not find the way there on the pages we read, so check the festival's site.</li>
<li><strong>Premist Dome site.</strong> Listed on the festival's site, with no 2027 dates yet.</li>
<li><strong>Opening hours and lighting times.</strong> Not on the festival's top page yet. Check nearer the time.</li>
<li><strong>Dress for it.</strong> The Sapporo Tourist Association says it is very cold outside and recommends warm clothing and shoes with good grip for snowy roads.</li>
</ul>
""" + sources(["snow", "subtime", "stvnews"], "Dates and sites can change, so check the festival's site.")

AIRPORT = """<h2 id="airport">To New Chitose Airport: the Airport Train</h2>
<p>JR Hokkaido's Airport Train (the Rapid Airport) runs directly between Sapporo (01) and New Chitose Airport (AP15), and some trains start or end at Otaru.</p>
<ul>
<li><strong>How fast.</strong> JR gives the fastest times between the airport and Sapporo as 33 minutes (Special Rapid), 37 minutes (Rapid) and 43 minutes (Semi-Rapid). On the way, every type stops at Shin-Sapporo and Minami-Chitose.</li>
<li><strong>How often.</strong> JR's page gives six trains an hour between 9:00 and 16:00 from the airport to Sapporo. It does not give the times the other way, so check the timetable.</li>
<li><strong>Which platform?</strong> We did not find a current official platform list for the Airport Train at Sapporo, so check the departure boards.</li>
<li><strong>First and last trains.</strong> JR Hokkaido&rsquo;s timetable for 24 November 2026 (a weekday): from New Chitose Airport, the first train to Sapporo is the Rapid Airport at 6:38 (Sapporo 7:18), and the last is the Special Rapid Airport at 23:21 (Sapporo 23:59). From Sapporo to the airport, the first is the Rapid Airport at 5:50 (airport 6:28), and the last is a local train at 22:25, which stops everywhere and reaches the airport at 23:12. Timetables change, so check JR&rsquo;s departures the day before.</li>
<li><strong>Rail passes for visitors.</strong> JR Hokkaido&rsquo;s Sapporo&ndash;Noboribetsu Area Pass and Sapporo&ndash;Furano Area Pass (4 consecutive days each) include New Chitose Airport, and the Hokkaido Rail Pass (5, 7 or 10 days) covers all JR Hokkaido lines except the Hokkaido Shinkansen. JR says all non-Japanese passport holders can use them; show your passport itself when you buy or exchange one (a copy is not accepted). With a pass you can sit in the reserved car or the non-reserved cars. Put only the pass into the ticket gate and take it back: JR does not reissue a lost pass. The passes do not cover the subway.</li>
<li><strong>Seats.</strong> Cars 1 to 3 and 5 to 6 are non-reserved. Car 4 is the reserved &ldquo;U seat&rdquo; car: you need a reserved-seat ticket as well as the fare.</li>
<li><strong>IC cards work</strong> (Suica, Kitaca and others). Ticket machines take cash only; the reserved-seat machine and the ticket office take cash and credit cards.</li>
<li><strong>Luggage.</strong> Within 250 cm in total (2 m at most in length), up to 2 items, each up to 30 kg.</li>
<li><strong>Passport-reader ticket machines.</strong> JR has posted a notice (8 October 2026) with important notes on its ticket machines with passport readers at Sapporo and New Chitose Airport stations. We did not read it, so check it on JR&rsquo;s English home page.</li>
<li><strong>Live train information.</strong> Check JR Hokkaido&rsquo;s <a href="https://www3.jrhokkaido.co.jp/webunkou/index_en.html" target="_blank" rel="noopener noreferrer">Train Operation Information (English)</a>, or its <a href="https://www3.jrhokkaido.co.jp/webunkou/stationlist_en.html" target="_blank" rel="noopener noreferrer">information for each station</a>, which also shows that day&rsquo;s departures. JR&rsquo;s guide to it describes delays of 5 minutes or more by station (5:00 to 25:00), a map of cancellations and delays of 30 minutes or more by line, including the Chitose Line (Sapporo, New Chitose Airport, Tomakomai), 5:00 to 24:00, and train locations with delays of 1 minute or more (5:00 to 25:00).</li>
<li><strong>By bus instead.</strong> From 11 December 2026 the airport bus leaves the Sapporo Station stop (Sapporo Ekimae) from 5:25 to 18:15, 68 a day, and takes about 77 minutes. No booking needed. The bus companies show the stop on their route map. Until 10 December the summer timetable applies.</li>
<li><strong>At the airport.</strong> The train arrives at B1F under the Domestic Terminal. For an international flight, go up to 2F and walk the 2F corridor: the 3F passage is closed until about the end of June 2027.</li>
</ul>
<p>More detail: our <a href="/blog/new-chitose-airport-guide">New Chitose Airport guide</a> covers the terminals, the corridor, buses, money and what to do in snow.</p>
""" + sources(["jrair", "jrttspk", "jrttcts", "chuoair", "jrops", "jrpass", "jrdis", "ctsjr", "jrhome", "jrwifi"], "Times change, so check JR Hokkaido.")

LONG = """<h2 id="long-distance">Hakodate, Asahikawa, Otaru and the Shinkansen</h2>
<ul>
<li><strong>The Shinkansen does not reach Sapporo yet.</strong> JR Hokkaido's construction page describes its work as towards the opening of the Hokkaido Shinkansen's Sapporo station, and JR lists the Hokkaido Shinkansen stations as Shin-Hakodate-Hokuto, Kikonai and Okutsugaru-Imabetsu. We did not find an opening date on those pages.</li>
<li><strong>To Hakodate and the Shinkansen.</strong> JR: the Limited Express Hokuto connects Sapporo and Hakodate, and is used as a connecting train to and from the Hokkaido Shinkansen. The Sapporo Tourist Association gives about 3 hours 30 minutes to Hakodate. Staying there? JR says JR Inn Hakodate is right by JR Hakodate Station. <a href="https://klook.tpo.lu/NtExmdmD" target="_blank" rel="nofollow noopener sponsored" data-ps-placement="hotel-jr-inn-hakodate" style="color:#0a8f78;font-weight:700;">Rooms and prices</a> (partner link)</li>
<li><strong>Book a seat on limited expresses.</strong> JR Hokkaido: &ldquo;From March 14, 2026, all seats will be reserved on all limited express trains in Hokkaido.&rdquo; That includes the Hokuto, Kamui, Lilac and Ozora. The Airport Train is not a limited express: it keeps its non-reserved cars.</li>
<li><strong>To Asahikawa.</strong> The Limited Express Kamui and Lilac. The Sapporo Tourist Association gives 1 hour 25 minutes at the quickest, with over 20 round trips a day.</li>
<li><strong>To Kushiro.</strong> The Limited Express Ozora, about 4 hours 11 minutes (Sapporo Tourist Association).</li>
<li><strong>To Otaru.</strong> Some Airport Trains run on to Otaru. JR says trains bound for &ldquo;Teine&rdquo; or &ldquo;Hoshimi&rdquo; do not continue to Otaru.</li>
<li><strong>Going beyond Otaru</strong> to Yoichi, Kutchan or Niseko? JR says IC cards such as Suica cannot be used beyond Otaru: buy a ticket at the station before you board. JR&rsquo;s English home page also notes that IC cards work only at some stations.</li>
</ul>
""" + sources(["jrconst", "jrshin", "jrhak", "jrasa", "sttrans", "jrair", "jrhome", "jrhotels"], "Times change, so check JR Hokkaido.")

DAYTRIPS = """<h2 id="day-trips">Day trips by train, and ski buses</h2>
<p>Sapporo is a good base: Otaru, Noboribetsu and Asahikawa are all easy day trips by train. Train times below are from JR Hokkaido&rsquo;s timetables for Tuesday 24 November 2026 (a weekday). They change, so check JR&rsquo;s departures the day before.</p>
<h3>Before you go: four JR rules</h3>
<ul>
<li><strong>Limited expresses: book a seat.</strong> All seats on all limited expresses in Hokkaido are reserved: you need a reserved-seat ticket as well as the fare, and JR says passengers without a seat number may have to stand. With a rail pass, get your seat ticket before you board: seats cannot be given on the train.</li>
<li><strong>IC cards work only near Sapporo.</strong> Suica, Kitaca and the other IC cards work to Otaru and the airport. JR says they cannot be used to Noboribetsu, Biei, Furano or Toya, even if you board inside the IC area, nor beyond Otaru to Kutchan and Niseko. Buy a paper ticket. JR also says some IC cards, such as SAPICA, cannot be used on its trains.</li>
<li><strong>One-man trains</strong> (one or two cars, no conductor, as on the local lines to Biei and Furano): the doors do not open by themselves, so press the button. With no ticket, take a numbered ticket when you board and pay the driver in cash: no credit cards, no IC cards.</li>
<li><strong>Tickets and bags.</strong> Do not keep paper tickets in a phone case: JR warns they can stop working. Skis and snowboards must be fully in their bags. Each bag within 250 cm in total (2 m long at most), up to 30 kg, and up to 2 bags.</li>
</ul>
<div class="ps-scroll">
<table class="checklist-table">
<thead><tr><th>Day trip</th><th>Train from Sapporo</th><th>Time</th><th>Area pass</th></tr></thead>
<tbody>
<tr><td>Otaru</td><td>Rapid Airport (no seat ticket needed)</td><td>34 to 46 min</td><td>Either area pass</td></tr>
<tr><td>Upopoy (Shiraoi)</td><td>Limited Express Suzuran (some trains)</td><td>about 1 h</td><td>Sapporo-Noboribetsu</td></tr>
<tr><td>Noboribetsu</td><td>Limited Express Suzuran or Hokuto</td><td>70 to 82 min</td><td>Sapporo-Noboribetsu</td></tr>
<tr><td>Asahikawa</td><td>Limited Express Lilac or Kamui</td><td>85 min</td><td>Sapporo-Furano</td></tr>
<tr><td>Biei, Furano</td><td>Via Asahikawa, then local trains</td><td>2 h or more</td><td>Sapporo-Furano</td></tr>
<tr><td>Niseko</td><td>Ski bus (see below)</td><td>about 3 h</td><td>No</td></tr>
</tbody>
</table>
</div>
<p>The Hokkaido Rail Pass covers all the JR trains above. The area passes do not cover local buses.</p>
<h3>Otaru</h3>
<ul>
<li><strong>Train.</strong> The Rapid and Special Rapid Airport run through to Otaru about every 30 minutes in the daytime, 34 to 46 minutes. The last Rapid Airport leaves Sapporo at 22:53, and local trains run until 23:50. Back from Otaru, Rapid trains run until 19:56, then local trains.</li>
<li><strong>IC cards work</strong> to Otaru, and the Airport Train&rsquo;s non-reserved cars need no seat ticket.</li>
<li><strong>Winter.</strong> JR lists the Otaru Snow Light Path in early to mid February.</li>
<li><strong>If trains stop,</strong> JR lists a bus between Sapporo and Otaru, about 60 to 80 minutes.</li>
</ul>
<h3>Noboribetsu hot springs (and Upopoy on the way)</h3>
<ul>
<li><strong>Train.</strong> Limited Express Suzuran or Hokuto to Noboribetsu Station, 70 to 82 minutes. First 6:53, last 21:12. Back: the last limited express leaves Noboribetsu at 21:21. The 6:00 Hokuto does not stop at Noboribetsu.</li>
<li><strong>To the hot-spring town.</strong> Noboribetsu Onsen is about 8 km from the station (JNTO). Donan Bus runs a bus from the station, 27 minutes. IC cards cannot be used on it. On its weekday timetable the first bus leaves the station at 6:52 and the last at 20:04; back from Noboribetsu Onsen, first 6:40, last 20:35.</li>
<li><strong>Upopoy</strong> (National Ainu Museum and Park): get off at Shiraoi, about 1 hour from Sapporo; it is about a 10-minute walk from the North Exit. Not every limited express stops at Shiraoi.</li>
<li><strong>No IC cards</strong> to Noboribetsu: buy a paper ticket.</li>
</ul>
<h3>Asahikawa and Asahiyama Zoo</h3>
<ul>
<li><strong>Train.</strong> Limited Express Lilac or Kamui, 85 minutes. First 6:29, last 22:00; back, last 22:00 too. From 1 December 2026 JR sells e-tickets for these two trains: you tap your IC card at the gate.</li>
<li><strong>To the zoo.</strong> Asahikawa Denki Kido bus routes 41 and 47, from stop 6 in front of Asahikawa Station: about every 30 minutes, about 40 minutes.</li>
<li><strong>Winter opening.</strong> 11 November 2026 to 7 April 2027, 10:30 to 15:30 (last entry 15:00). Closed 30 December to 1 January.</li>
<li><strong>Penguin walk.</strong> In the snowy season, from about late December to mid-March, at 11:00 and 14:30 (March: 11:00 only). The zoo announces the first day on its social media, and the walk is called off in bad weather. The paths are steep: wear shoes that grip on snow.</li>
<li><strong>Staying the night?</strong> JR says JR Inn Asahikawa is directly connected to Asahikawa Station. <a href="https://klook.tpo.lu/lpyq58s7" target="_blank" rel="nofollow noopener sponsored" data-ps-placement="hotel-jr-inn-asahikawa" style="color:#0a8f78;font-weight:700;">Rooms and prices</a> (partner link)</li>
</ul>
<h3>Biei and Furano in winter</h3>
<ul>
<li><strong>No direct train in winter.</strong> The Furano Lavender Express runs June to September only. JR&rsquo;s winter route goes via Asahikawa, then local trains: about 35 minutes to Biei, and 66 to 83 minutes from Asahikawa to Furano.</li>
<li><strong>Few trains.</strong> On 24 November there were up to 2 hours between local trains in the morning (Biei to Furano: none between 10:14 and 12:09). Plan your way back before you go.</li>
<li><strong>Farm Tomita</strong> in winter: from Naka-Furano Station, about 25 minutes on foot (JR). JR marks its Blue Pond trip as one for the season without snow.</li>
<li><strong>No IC cards</strong> on these lines, and the trains are one-man: see the rules above.</li>
</ul>
<h3>Niseko: take the ski bus</h3>
<ul>
<li><strong>Why not the train?</strong> No direct daytime train: you change at Otaru, often at Kutchan too, and IC cards do not work.</li>
<li><strong>Ski bus</strong> (Hokkaido Chuo Bus with Niseko Bus), <strong>booking required</strong>, 12 December 2026 to 22 March 2027 (the first and last days depend on the snow). From the Sapporo Station North Exit at 7:50 and 9:20, at Niseko Hirafu (Welcome Center) at 10:56 and 12:26: about 3 hours. Back from Hirafu at 14:39 and 15:59, at Sapporo Station at 17:45 and 19:05.</li>
<li><strong>How to book.</strong> Online in English, or by phone at the Chuo Bus Sapporo Terminal, 0570-200-600 (7:30 to 18:00), by 18:00 the day before. Seats are not numbered. Online bookings are not paid online: buy the ticket at a counter on the day, or pay cash on the bus.</li>
<li><strong>Ski gear.</strong> No ski or snowboard boots on board. Put skis and snowboards in a case (sole guards are fine for snowboards).</li>
<li><strong>Closer slopes.</strong> A booked bus runs from the Sapporo Station North Exit (taxi-pool side) to the Sapporo Kokusai ski area, about 1 hour 37 minutes, from the ski area&rsquo;s opening (from 20 November 2026) to 5 May 2027. It does not take you if it is full. Check its winter times on the bus company&rsquo;s page.</li>
</ul>
<h3>If something goes wrong</h3>
<ul>
<li><strong>Lost something on a JR train?</strong> JR Hokkaido&rsquo;s &ldquo;find chat&rdquo; is an English and Chinese chat for items lost on its trains or in its stations; the QR code is in JR&rsquo;s manner guide.</li>
<li><strong>Need help with a wheelchair?</strong> Many stations have no staff or no lift, so JR recommends asking for help in advance with its inquiry form. Platforms are slippery with snow in winter.</li>
<li><strong>Snow.</strong> Check JR Hokkaido&rsquo;s <a href="https://www3.jrhokkaido.co.jp/webunkou/index_en.html" target="_blank" rel="noopener noreferrer">Train Operation Information (English)</a> before you set off, and keep a little cash for a bus or a taxi.</li>
</ul>
<p style="background:#f0faf7;border-left:3px solid #00C9A7;padding:12px 16px;border-radius:0 8px 8px 0;font-size:0.92rem;margin:20px 0;">Rather not plan the trains? <a href="https://www.getyourguide.com/s/?q=Sapporo%20day%20trip&amp;partner_id=D7IXONS&amp;cmp=ps-sapporo-station-daytrips" target="_blank" rel="nofollow noopener sponsored" data-ps-placement="gyg-sapporo-daytrips" style="color:#00C9A7;text-decoration:underline;">Compare guided day tours from Sapporo</a> (partner link). Check what is included, and the meeting point, before you book.</p>
""" + sources(["jrallres", "jrusage", "jrmanner", "jracc", "jretix", "jrpass", "jrttspk", "ttotaru", "ttnob", "ttasa", "ttbiei", "jrmodnob", "jrmodfur", "jrfaq9", "jrfbtrain", "jrdis", "jtnob", "donanstn", "donanback", "zoowin", "zooacc", "jrhotels", "skibus", "skibook", "skipdf", "skikok"], "Times change, so check the operator.")

CONNECTED = """<h2 id="connected">Getting online: eSIM</h2>
<p>You will want a connection for maps, messages and the festival pages.</p>
<ul>
<li><strong>JR Wi-Fi.</strong> JR Hokkaido says it provides Wi-Fi at its stations, on the Airport Train cars and on Hokkaido Shinkansen cars. We did not find SIM counters on the Sapporo station pages we read.</li>
<li><strong>eSIM:</strong> install it on your phone and switch it on when you need it. It needs an eSIM-ready, unlocked phone.</li>
</ul>
""" + sources(["jrwifi"])

MONEY = """<h2 id="money">Money and ATMs</h2>
<p>Seven Bank ATMs take cards issued outside Japan with the Visa, Mastercard, UnionPay, American Express, JCB, Discover and Diners Club marks, though Seven Bank says some cards with these marks may not be accepted. These are the Seven Bank ATMs its locator lists at Sapporo Station:</p>
<ul>
<li><strong>JR Sapporo Station, West gate side:</strong> 1 ATM, 5:10 to 24:00.</li>
<li><strong>Subway, Namboku Line Sapporo (N06):</strong> 2 ATMs in the concourse outside the ticket gates, 6:00 to 24:00.</li>
<li><strong>Subway, Toho Line Sapporo (H07):</strong> 1 ATM on B1, in the gate concourse near the South gate, 6:00 to 24:00.</li>
<li><strong>JR Tower APIA:</strong> 1 ATM in the cash service corner (Floral Galleria), 8:00 to 21:00.</li>
<li><strong>At the Snow Festival:</strong> Odori subway station has 2 ATMs outside the ticket gates, 6:00 to 24:00: on B2 by the East gate (Toho Line) and on B1 by exit 4 (Tozai Line).</li>
<li><strong>Currency exchange:</strong> we did not find a counter at the station on the official pages we read.</li>
</ul>
<p>Seven Bank says the hours can differ on the day, so carry a little cash before a late train.</p>
""" + sources(["sbintl", "sbjrspk", "sbnamboku", "sbtoho", "sbapia", "sbodori"], "Hours can change.")

LUGGAGE = """<h2 id="luggage">Lockers and luggage</h2>
<p>Sort your bags out before you head to Odori or the ski slopes.</p>
<ul>
<li><strong>How many.</strong> JR's locker list (July 2026) gives about 800 lockers at Sapporo, in small, medium and large sizes. JR says the number goes up and down with the construction.</li>
<li><strong>Skis and snowboards.</strong> Sapporo has 5 coin lockers for skis and snowboards; JR says its other stations have none.</li>
<li><strong>How long.</strong> Up to 3 days, counting the day you start.</li>
<li><strong>Two kinds.</strong> The Sapporo Tourist Association describes key lockers, which take only 100-yen coins, and touch-panel lockers with English, simplified Chinese and Korean. It says the station lockers can be opened from 5:15 to midnight.</li>
<li><strong>Where and how much.</strong> We did not find a locker map or a current price list in English, so we give none. JR's English FAQ says locker information is in Japanese only. Follow the signs.</li>
<li><strong>Keep with you:</strong> medicines, valuables, chargers and your passport.</li>
</ul>
""" + sources(["jrlock", "stlock", "jrfaq7"], "Locker numbers change with the construction.")

HOTELS = """<div data-ps-placement="hotels-sapporo-station">
<h2 id="hotels">Staying by the station: JR Hokkaido&rsquo;s hotels</h2>
<p>Want to be close to the trains and the airport? JR Hokkaido lists these group hotels at or near Sapporo Station. This is what JR says about where each one is:</p>
<ul>
<li><strong>JR Tower Hotel Nikko Sapporo:</strong> next to Sapporo Station, a 36-storey hotel with natural hot springs. <a href="https://klook.tpo.lu/zjYrWP25" target="_blank" rel="nofollow noopener sponsored" style="color:#0a8f78;font-weight:700;">Rooms and prices</a> (partner link)</li>
<li><strong>JR Inn Sapporo:</strong> 4 minutes&rsquo; walk from the West Ticket Gate. <a href="https://klook.tpo.lu/DdKj1ncR" target="_blank" rel="nofollow noopener sponsored" style="color:#0a8f78;font-weight:700;">Rooms and prices</a> (partner link)</li>
<li><strong>JR Inn Sapporo N2:</strong> close to Sapporo Station, the Clock Tower and Odori Park. <a href="https://klook.tpo.lu/Qn866IDt" target="_blank" rel="nofollow noopener sponsored" style="color:#0a8f78;font-weight:700;">Rooms and prices</a> (partner link)</li>
<li><strong>JR Inn Sapporo South:</strong> close to the Former Hokkaido Government Office Building and Odori Park, with good access to Sapporo and Odori stations. <a href="https://klook.tpo.lu/vzyGqBYK" target="_blank" rel="nofollow noopener sponsored" style="color:#0a8f78;font-weight:700;">Rooms and prices</a> (partner link)</li>
</ul>
<p>Going further? JR also lists <strong>JR Inn Asahikawa</strong>, connected to Asahikawa Station, and <strong>JR Inn Hakodate</strong>, right by JR Hakodate Station: see <a href="#day-trips">day trips</a> and <a href="#long-distance">other trains</a>.</p>
<p>Check the room, the total price and the cancellation terms on the booking page before you book.</p>
""" + sources(["jrhotels"]) + "\n</div>"

LEAVING = """<h2 id="leaving">Leaving Sapporo: a checklist</h2>
<ul>
<li><strong>Flying from New Chitose?</strong> Take JR's Airport Train (fastest 33 minutes). The first leaves at 5:50 and the last at 22:25 (a local train, at the airport 23:12), on JR&rsquo;s timetable for 24 November 2026. Check the departure boards for the platform, and JR&rsquo;s departures the day before an early flight. See our <a href="/blog/new-chitose-airport-guide">New Chitose Airport guide</a>.</li>
<li><strong>International flight?</strong> At the airport, walk the 2F corridor from the Domestic Terminal; the 3F passage is closed until about the end of June 2027.</li>
<li><strong>Snow forecast?</strong> Leave earlier, and check JR Hokkaido&rsquo;s Train Operation Information (English). If trains stop, JR lists the airport bus and taxis as alternatives and warns they get very crowded.</li>
<li><strong>Heading to Hakodate or the Shinkansen?</strong> The Limited Express Hokuto. Since 14 March 2026 all seats on all limited expresses in Hokkaido are reserved (JR), so book a seat.</li>
<li><strong>Collect your bags.</strong> Lockers hold bags for up to 3 days, and the station is under construction, so leave time to find your locker again.</li>
<li><strong>Allow time for the station itself.</strong> Routes change with the works, and some lifts and escalators by the East gate are out of use.</li>
</ul>
""" + sources(["jrair", "jrdis", "ctsjr", "jrhak", "jrlock", "jrconst", "jrhome"], "Times change, so check the operator.")

ABOUT = """<div class="ps-about" id="about-this-guide">
<h2>About this guide</h2>
<p>Written by PackSmart. Station details were checked on 24 November 2026 against JR Hokkaido (including its construction map as of 21 October 2026), the Sapporo City Transportation Bureau, the Sapporo Snow Festival's Japanese site and the Sapporo Tourist Association. Where an official page did not tell us something, for example the Airport Train's platform at Sapporo, locker locations or the festival's opening hours, we say so instead of guessing. Spotted something out of date? <a href="/contact">Tell us</a> and we will fix it.</p>
<ul>
<li><strong>24 Nov 2026:</strong> first version, with the one-page card, the construction notice, the West and East gates, help desks, the subway to Odori and Susukino, the Snow Festival 2027 dates, the Airport Train, long-distance trains, lockers, the find-it tool and a leaving checklist.</li>
<li><strong>24 Nov 2026, update:</strong> ATMs, the first and last Airport Trains, rail passes, and a new section on day trips by train (Otaru, Noboribetsu, Asahikawa, Biei and Furano), JR&rsquo;s rules for trains beyond Sapporo and the Niseko ski bus.</li>
<li><strong>24 Nov 2026, update:</strong> JR Hokkaido&rsquo;s hotels by the station, Asahikawa and Hakodate.</li>
</ul>
</div>"""


def _card(title, text, slug, tag):
    return ('        <div class="related-card">\n            <div class="related-card-body">\n                <h4>%s</h4>\n                <p>%s</p>\n'
            '                <a href="https://www.packsmartapp.com%s">Read More <span class="related-arrow">&rarr;</span></a>\n                <div class="related-tag">%s</div>\n            </div>\n        </div>\n') % (title, text, slug, tag)


RELATED = ('<div class="related-posts">\n    <h3>Related Guides</h3>\n    <div class="related-grid">\n'
    + _card("New Chitose Airport Guide 2026", "Which terminal, the 2F corridor, the Airport Train and buses to Sapporo, ski buses, money and winter tips.", "/blog/new-chitose-airport-guide", "Airport Guide")
    + _card("Japan Travel and Packing Guide 2026", "What to pack, rail passes, etiquette and a budget breakdown for a first trip to Japan.", "/blog/japan-travel-packing-guide", "Destination Guide")
    + _card("Tokyo Station Guide 2026", "Going on to Tokyo? Which side to use, bullet train platforms, the Narita Express and luggage.", "/blog/tokyo-station-guide", "Station Guide")
    + '    </div>\n</div>')

# photo: public/images/sapporo-odori-aerial.jpg (PAKUTASO, checked by eye, see
# docs/research/sapporo-sources.md); optimised copies made here (as w58: sips on a Mac, Pillow elsewhere, an existing copy is kept)
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


IMAGES = {"hero": ("sapporo-odori-aerial", "sapporo-odori-aerial-1600.jpg", 1600)}
HERO_URL, HERO_NOTE = prepare_img(*IMAGES["hero"])
if not HERO_URL:
    die("hero photo not found: public/images/sapporo-odori-aerial.jpg")

WARN_CSS = """<style>
.ps-warn{background:#FDECEF;border:2px solid #E94560;border-radius:14px;padding:16px 18px;margin:20px 0;line-height:1.55}
.ps-warn strong.h{display:block;font-size:1.12rem;color:#a3243b;margin:0 0 6px}
.ps-warn p{margin:0 0 8px}
.ps-warn p:last-child{margin:0}
</style>"""

QR_SCREEN = '<svg shape-rendering="crispEdges" viewBox="0 0 41 41" class="segno"><title>QR code: open the Sapporo Station Pocket Guide</title><path fill="#fff" d="M0 0h41v41h-41z"/><path class="qrline" stroke="#000" d="M4 4.5h7m1 0h3m2 0h1m1 0h2m1 0h1m4 0h1m2 0h7m-33 1h1m5 0h1m2 0h1m2 0h3m1 0h1m1 0h4m2 0h1m1 0h1m5 0h1m-33 1h1m1 0h3m1 0h1m4 0h2m1 0h1m2 0h2m1 0h2m1 0h1m2 0h1m1 0h3m1 0h1m-33 1h1m1 0h3m1 0h1m1 0h1m2 0h2m3 0h2m5 0h2m1 0h1m1 0h3m1 0h1m-33 1h1m1 0h3m1 0h1m1 0h1m2 0h1m1 0h1m2 0h1m2 0h1m2 0h2m2 0h1m1 0h3m1 0h1m-33 1h1m5 0h1m1 0h1m1 0h3m1 0h2m2 0h1m1 0h1m5 0h1m5 0h1m-33 1h7m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h7m-25 1h5m1 0h1m2 0h5m2 0h1m-25 1h1m3 0h1m1 0h4m2 0h1m2 0h1m1 0h1m3 0h3m1 0h5m2 0h1m-33 1h2m1 0h1m1 0h1m3 0h4m1 0h2m1 0h1m5 0h1m1 0h1m3 0h3m-29 1h1m1 0h3m2 0h6m2 0h1m3 0h2m1 0h2m2 0h1m1 0h1m-32 1h1m2 0h1m1 0h1m2 0h1m2 0h3m1 0h1m3 0h1m1 0h2m1 0h3m-26 1h1m1 0h2m1 0h1m1 0h1m1 0h1m1 0h2m1 0h2m2 0h5m2 0h1m1 0h2m1 0h2m-29 1h1m2 0h2m3 0h3m3 0h3m2 0h3m1 0h1m1 0h1m-30 1h7m1 0h3m1 0h1m2 0h1m1 0h1m4 0h2m1 0h4m1 0h2m-31 1h5m2 0h1m1 0h2m3 0h3m3 0h1m1 0h6m-29 1h2m1 0h1m2 0h6m2 0h1m2 0h1m1 0h1m1 0h2m1 0h1m1 0h1m1 0h2m1 0h1m-32 1h1m2 0h2m3 0h1m1 0h2m2 0h3m6 0h2m4 0h2m-30 1h2m1 0h1m1 0h1m1 0h1m3 0h1m2 0h1m1 0h1m2 0h1m1 0h3m2 0h1m1 0h1m1 0h1m-27 1h1m3 0h1m4 0h1m2 0h2m2 0h1m2 0h4m-27 1h2m1 0h1m1 0h1m1 0h2m3 0h3m2 0h4m4 0h4m1 0h2m-33 1h1m1 0h2m8 0h3m1 0h1m2 0h5m1 0h1m1 0h1m2 0h2m-30 1h1m3 0h1m1 0h7m1 0h2m4 0h4m2 0h4m-29 1h3m1 0h1m2 0h1m1 0h1m4 0h1m1 0h1m1 0h1m1 0h4m5 0h1m-33 1h3m1 0h1m1 0h3m1 0h1m3 0h2m1 0h6m1 0h5m2 0h2m-25 1h2m2 0h1m2 0h4m2 0h4m3 0h1m1 0h1m-31 1h7m1 0h8m2 0h1m1 0h2m2 0h1m1 0h1m1 0h2m1 0h1m-32 1h1m5 0h1m3 0h2m4 0h1m3 0h2m2 0h1m3 0h1m2 0h1m-32 1h1m1 0h3m1 0h1m1 0h5m1 0h1m1 0h1m4 0h2m1 0h6m1 0h2m-33 1h1m1 0h3m1 0h1m2 0h1m2 0h2m3 0h2m3 0h2m2 0h4m-30 1h1m1 0h3m1 0h1m3 0h6m2 0h1m1 0h1m1 0h1m2 0h4m1 0h1m-31 1h1m5 0h1m2 0h1m2 0h6m3 0h1m1 0h2m1 0h1m2 0h1m-30 1h7m1 0h2m1 0h1m1 0h2m2 0h1m1 0h6m7 0h1"/></svg>'
QR_PRINT = '<svg shape-rendering="crispEdges" viewBox="0 0 41 41" class="segno"><title>QR code: open the Sapporo Station Pocket Guide</title><path fill="#fff" d="M0 0h41v41h-41z"/><path class="qrline" stroke="#000" d="M4 4.5h7m2 0h3m2 0h1m1 0h1m1 0h4m1 0h1m2 0h7m-33 1h1m5 0h1m4 0h2m2 0h2m1 0h1m5 0h1m1 0h1m5 0h1m-33 1h1m1 0h3m1 0h1m1 0h1m1 0h1m3 0h1m1 0h1m1 0h1m1 0h3m1 0h1m1 0h1m1 0h3m1 0h1m-33 1h1m1 0h3m1 0h1m1 0h2m2 0h1m5 0h1m3 0h1m3 0h1m1 0h3m1 0h1m-33 1h1m1 0h3m1 0h1m1 0h5m1 0h3m1 0h1m2 0h3m2 0h1m1 0h3m1 0h1m-33 1h1m5 0h1m1 0h1m3 0h2m4 0h1m2 0h1m4 0h1m5 0h1m-33 1h7m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h7m-25 1h1m2 0h1m2 0h1m1 0h1m3 0h4m-24 1h1m1 0h5m2 0h3m1 0h2m2 0h1m2 0h1m1 0h2m2 0h5m-31 1h3m2 0h1m1 0h1m1 0h5m3 0h1m1 0h3m1 0h1m2 0h2m1 0h2m1 0h1m-33 1h2m1 0h1m1 0h4m4 0h5m6 0h3m1 0h1m1 0h2m-32 1h6m1 0h1m3 0h1m1 0h1m1 0h5m1 0h1m1 0h1m1 0h2m1 0h3m-31 1h2m2 0h1m1 0h1m1 0h4m2 0h1m1 0h1m5 0h2m1 0h1m1 0h3m-30 1h1m1 0h1m7 0h1m4 0h1m2 0h4m1 0h2m1 0h1m2 0h1m1 0h2m-32 1h1m2 0h1m1 0h1m1 0h1m2 0h1m1 0h4m1 0h1m5 0h4m1 0h1m1 0h1m-32 1h2m1 0h1m3 0h2m1 0h1m1 0h1m2 0h1m2 0h2m1 0h2m2 0h3m1 0h2m-31 1h2m3 0h2m1 0h2m1 0h1m1 0h3m1 0h1m2 0h1m1 0h1m1 0h2m1 0h3m2 0h1m-33 1h4m1 0h1m1 0h1m1 0h5m2 0h1m2 0h3m1 0h5m1 0h4m-32 1h4m1 0h1m1 0h1m1 0h1m1 0h5m1 0h1m1 0h1m6 0h2m1 0h2m-30 1h1m2 0h1m3 0h5m2 0h1m4 0h3m1 0h6m-31 1h2m1 0h1m1 0h8m1 0h1m3 0h1m1 0h1m4 0h1m2 0h2m-30 1h5m2 0h2m2 0h1m3 0h2m2 0h2m1 0h2m2 0h1m3 0h1m1 0h1m-33 1h1m2 0h4m2 0h1m4 0h1m3 0h1m1 0h1m4 0h1m5 0h1m-32 1h1m6 0h1m2 0h1m3 0h1m1 0h1m1 0h1m2 0h2m2 0h2m1 0h3m-31 1h1m1 0h3m1 0h2m4 0h1m1 0h1m2 0h2m3 0h1m1 0h5m2 0h1m-24 1h1m1 0h1m1 0h1m1 0h1m1 0h5m1 0h3m3 0h1m1 0h3m-33 1h7m2 0h1m1 0h1m1 0h5m2 0h5m1 0h1m1 0h1m1 0h2m-32 1h1m5 0h1m1 0h4m1 0h2m2 0h2m1 0h5m3 0h4m-32 1h1m1 0h3m1 0h1m1 0h1m2 0h6m2 0h1m2 0h1m1 0h6m-30 1h1m1 0h3m1 0h1m1 0h1m2 0h5m1 0h5m1 0h1m1 0h1m2 0h2m1 0h2m-33 1h1m1 0h3m1 0h1m1 0h2m3 0h1m1 0h3m2 0h1m2 0h5m1 0h1m-30 1h1m5 0h1m3 0h3m1 0h2m2 0h2m1 0h2m3 0h1m1 0h1m1 0h1m-31 1h7m1 0h1m1 0h1m2 0h3m1 0h1m4 0h6m3 0h1"/></svg>'
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
<div id="psPocketBar" role="region" aria-label="Sapporo Station Pocket Guide">
<div class="t"><b>Get the Sapporo Station Pocket Guide</b><span>No app, no sign-up. Works offline at the station.</span></div>
<a class="go" href="/sapporo-pocket?src=bar">Get it</a>
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
<p>Open the Sapporo Station Pocket Guide once while you have signal, then add it to your home screen. At the station it opens like an app, even with no connection.</p>
<p><a class="ps-btn2" href="/sapporo-pocket?src=box" onclick="try{window.gtag&&gtag('event','pocket_prompt',{event_category:'engagement',action:'open_box',page_path:location.pathname});}catch(e){}" style="display:inline-block;text-decoration:none;">Open the Pocket Guide</a></p>
<ul>
<li><strong>iPhone:</strong> open it in Safari, tap the Share button, then "Add to Home Screen".</li>
<li><strong>Android:</strong> open it in Chrome, tap the menu (three dots), then "Add to Home screen" or "Install app".</li>
</ul>
</div>"""

# ---- GetYourGuide box: tours and tickets for a search on Sapporo (partner D7IXONS, its own cmp so clicks can be told apart).
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

GYG_Q = "Sapporo"
GYG_CMP = "ps-sapporo-station-gyg"
GYG_SEARCH = "https://www.getyourguide.com/s/?q=%s&partner_id=%s&cmp=ps-sapporo-station" % (quote(GYG_Q), GYG_PARTNER)
GYG_BOX = (GYGQ_TPL.replace("__PID__", "gyg-sapporo-station").replace("__HEAD__", "Tours and tickets around Sapporo")
           .replace("__BLURB__", "Popular tours and tickets for Sapporo, as listed by our partner. Check what is included, and the meeting point, before you book.")
           .replace("__MORE__", "See more tours and tickets around Sapporo")
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
    '<p>Sapporo Station is where most visitors to Hokkaido&rsquo;s biggest city arrive: the Airport Train from New Chitose stops here, the subway runs on to Odori Park and Susukino, '
    'and the limited expresses leave for Hakodate and Asahikawa. It is also a building site, being rebuilt for the Hokkaido Shinkansen, so routes inside it change. '
    'This guide is written in plain English so that a first-time visitor, a family or an older traveller can follow it step by step. '
    'You can print the one-page card below and carry it with you.</p>',
    toc_html,
    CARD,
    CONSTRUCTION,
    GATES,
    DIAGRAM,
    DESKS,
    SUBWAY,
    SNOW,
    GYG_BOX,
    AIRPORT,
    LONG,
    DAYTRIPS,
    CONNECTED,
    airalo,
    MONEY,
    LUGGAGE,
    FINDER,
    SAVE_BOX,
    HOTELS,
    LEAVING,
    '<div class="tip-box">\n    <strong>Planning more of Japan?</strong> Our <a href="/blog/japan-travel-packing-guide">Japan travel and packing guide</a> covers what to pack, rail passes, etiquette and a budget breakdown. '
    'Flying in or out? See our <a href="/blog/new-chitose-airport-guide">New Chitose Airport guide</a>.\n</div>',
    "<!-- FIRST-HAND NOTES: add notes and photos from a Sapporo Station visit here -->",
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
           'checked on 24 November 2026. Stations change, so follow the signs on the day.</p>\n'
           + '<details class="ps-srcbox"><summary>Show all %d official pages</summary>\n<ul class="ps-sources">\n' % len(_src_links)
           + "".join("<li>%s</li>\n" % a for a in _src_links) + "</ul></details>")
_faq = BODY.index('<h2 id="faq">')
BODY = BODY[:_faq] + SOURCES + "\n\n" + BODY[_faq:]
# hero button: a quiet way into the Pocket Guide from the top of the article (as w42)
HERO_CTA = ('        <div style="margin:48px 0 0;text-align:center;">'
            '<a href="/sapporo-pocket?src=hero" onclick="try{window.gtag&&gtag(\'event\',\'pocket_prompt\',{event_category:\'engagement\',action:\'open_hero\',page_path:location.pathname});}catch(e){}" '
            'style="display:inline-flex;align-items:center;gap:12px;background:#00C9A7;color:#0f0f23;text-align:left;padding:12px 14px 12px 20px;width:340px;max-width:100%;box-sizing:border-box;border-radius:12px;text-decoration:none;min-height:44px;box-shadow:0 6px 18px rgba(0,0,0,.28);line-height:1.2;">'
            '<span style="flex:1;min-width:0;text-align:left;">'
            '<span style="display:block;font-weight:700;font-size:0.8rem;opacity:0.8;">Save to your phone</span>'
            '<span style="display:block;font-weight:800;font-size:1.05rem;margin-top:2px;">Sapporo Station Pocket Guide</span>'
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
    '        <div class="meta">Station Guide • Japan · Published 24 Nov 2026 · __READ__ min read</div>',
    HERO_CTA,
    ('        <div style="position:absolute;left:12px;right:12px;bottom:8px;font-size:0.7rem;opacity:0.7;text-align:center;">Odori Park, the Snow Festival&rsquo;s main site, shown in summer. Photo: PAKUTASO.</div>' if HERO_URL else ''),
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



# ---- Sapporo Station Pocket Guide: standalone page + service worker + manifest (works offline once visited)
POCKET_PATH = "/sapporo-pocket"
THEME = "#0e7490"   # ice teal, one colour per guide
# ---- Pocket Guide analytics (v47): anonymous taps only, no accounts, honours Do Not Track / GPC
GUIDE_ID = "sapporo"
AIRPORT_CODE = "SPK-STN"
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

POCKET_SVG = re.search(r'<svg id="sprDiagram".*?</svg>', DIAGRAM, re.S).group(0).replace('id="sprDiagram"', 'id="pkDiagram"').replace('id="sprT"', 'id="pkT"').replace('id="sprD"', 'id="pkD"').replace('aria-labelledby="sprT sprD"', 'aria-labelledby="pkT pkD"')
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
<title>Sapporo Station Pocket Guide | PackSmart</title>
<meta name="description" content="A simple Sapporo Station helper that works offline: West and East gates during the Shinkansen works, the subway to Odori and Susukino, lockers, the Snow Festival and the train to the airport. By PackSmart.">
<meta name="robots" content="noindex,follow">
<link rel="canonical" href="__GUIDE_URL__">
<meta name="theme-color" content="#1a1a3e">
<link rel="manifest" href="/sapporo-pocket.webmanifest">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" href="/images/sapporo-apple-touch-180.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Sapporo">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<script>__PG_BOOT__</script>
<style>__CSS__</style>
</head>
<body>
<header class="top">
<div><strong>Sapporo Station Pocket Guide</strong><span class="by">by PackSmart &middot; 24 Nov 2026</span></div>
<div class="status" id="status" role="status">Checking...</div>
</header>
<button type="button" class="inst-strip" id="instStrip" hidden><span class="ico" aria-hidden="true">&#128242;</span><span><b>Add this to your home screen</b><br>so it works with no internet</span><span class="go">How</span></button>
<div class="panels" id="panels">
<section class="panel" id="p-find" role="tabpanel" aria-labelledby="t-find">
<p class="seg-h">Which side are you on?</p>
<div class="seg" id="seg"></div>
<p class="seg-h" style="margin-top:14px">What do you need? <span class="small">Tap one.</span></p>
<div class="pager" id="pager"><div class="track" id="track"><div class="tiles pane" id="tiles"></div><div class="tiles pane off" id="tiles2" aria-hidden="true"></div></div></div>
<p class="hint">The station is under construction. Ask station staff.</p>
<div id="sponsor" hidden></div>
<noscript><p class="card">This guide needs JavaScript. Please turn it on, or ask at any information counter.</p></noscript>
</section>
<section class="panel" id="p-map" role="tabpanel" aria-labelledby="t-map" hidden>
<p class="seg-h" style="margin-top:2px">Which side are you on?</p>
<div class="seg" id="mseg"></div>
<p class="lead2" id="mLead" style="margin-top:10px">Namboku Line (Odori): west side. Toho Line: east side. Taxis: South Exit.</p>
<div class="tmap" id="tmap">
<div class="tcard t2" data-t="N"><div class="badge">N</div><div class="tb"><h3>North Exit plaza</h3><p>North side of the station</p></div></div>
<div class="tlink"><span aria-hidden="true">&#128646;</span><span>JR platforms 2 to 11: stairs inside the gates. Check the boards</span></div>
<div class="tcard t1" data-t="T1"><div class="badge">W</div><div class="tb"><h3>West gate</h3><p>JR Information Desk (West Exit), Tourist Information Center (West Concourse)</p><p class="stn"><span aria-hidden="true">&#128647;</span> Namboku Line N06: Odori 2 min</p></div></div>
<div class="tcard t3" data-t="T2"><div class="badge">E</div><div class="tb"><h3>East gate</h3><p>Towards the Toho Line (H07)</p><p class="stn warn"><span aria-hidden="true">&#128679;</span> Some lifts and escalators out of use</p></div></div>
<div class="tlink"><span aria-hidden="true">&#8596;&#65039;</span><span>Indoor and outdoor passages, east to west</span></div>
<div class="tcard t2" data-t="S"><div class="badge">S</div><div class="tb"><h3>South Exit plaza</h3><p>Taxis. Daimaru to the south-west, Sapporo Stellar Place to the south and south-east</p></div></div>
</div>
<p class="small" style="text-align:center;margin-top:10px">Simplified, not to scale. From JR&rsquo;s map as of 21 October 2026, which may change. Follow the signs.</p>
</section>
<section class="panel" id="p-arrive" role="tabpanel" aria-labelledby="t-arrive" hidden>
<p class="lead2">Just arrived at Sapporo? Tap a step to tick it off.</p>
<ol class="steps" id="arrSteps"></ol>
<button type="button" class="reset" id="arrReset" hidden>Clear ticks</button>
<p class="sec-h">Then, once you are out</p>
<div class="tiles" id="arrTiles"></div>
</section>
<section class="panel" id="p-depart" role="tabpanel" aria-labelledby="t-depart" hidden>
<div class="heroline"><span class="big2">33&nbsp;min</span><span><b>Fastest Airport Train, Sapporo and New Chitose Airport.</b><br>JR&rsquo;s Special Rapid. Check the boards for the platform.</span></div>
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
<p class="small" style="margin-top:0">JR Information Desk at the West Exit, 8:30 to 19:00 (English, Chinese, Korean). Hokkaido-Sapporo Tourist Information Center, West Concourse, 8:30 to 20:00. Staff will help, so just ask.</p>
</div>
<div class="tiles hnav" id="hnav2"></div>
</div>
</div></div>
<div class="quiet"><div class="card slim" id="shareCard" hidden><div class="row"><div><h2>Helping someone travel?</h2><p>Send them this guide for offline use.</p></div><button type="button" class="big" id="shareBtn">Send it</button></div></div>
<div class="card slim install" id="install"><div class="row"><div><h2>Keep this on your phone</h2><p>Add it to your home screen. Works offline.</p><p class="small" id="instDesk">Open this page on your phone, then add it to your home screen.</p></div><div id="instHow" hidden><button type="button" class="big" id="instBtn">Show me</button></div></div></div>
<p class="small">Station details come from JR Hokkaido (station map as of 21 October 2026), the Sapporo City Transportation Bureau, the Sapporo Snow Festival site and the Sapporo Tourist Association, checked 24 November 2026. The station is under construction, so routes change. If you cannot find something, ask station staff. Found something out of date? <a href="/contact">Tell us</a> (needs internet). We count anonymous taps to improve this guide: no name, no account. <a href="/privacy-policy">Privacy</a> &middot; <a href="#" id="pgOpt">Turn off counting</a>. The full guide, with the subway, the Snow Festival and the Airport Train, is at <a href="__GUIDE_URL__">packsmartapp.com</a> (needs internet).</p></div>
</section>
</div>
<nav class="tabs" role="tablist" aria-label="Sections">
<button type="button" role="tab" id="t-find" data-tab="find" aria-selected="true"><span aria-hidden="true">&#128269;</span>Find</button>
<button type="button" role="tab" id="t-map" data-tab="map" aria-selected="false"><span aria-hidden="true">&#128506;&#65039;</span>Map</button>
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
  var ICON={prayer:'\\uD83D\\uDE4F',baby:'\\uD83C\\uDF7C',quiet:'\\uD83E\\uDD2B',info:'\\u2139\\uFE0F',help:'\\u267F',lockers:'\\uD83E\\uDDF3',wifi:'\\uD83D\\uDCF6',shower:'\\uD83D\\uDEBF',internet:'\\uD83D\\uDCBB',play:'\\uD83E\\uDDF8',smoking:'\\uD83D\\uDEAC',toilet:'\\uD83D\\uDEBB',food:'\\uD83C\\uDF5C',money:'\\uD83D\\uDCB4',unwell:'\\uD83C\\uDFE5',pharmacy:'\\uD83D\\uDC8A',trains:'\\uD83D\\uDE86',tickets:'\\uD83C\\uDFAB',phone:'\\uD83D\\uDCF6',charge:'\\uD83D\\uDD0B',exits:'\\uD83D\\uDEAA',park:'\\uD83C\\uDF38',lost:'\\uD83D\\uDCE6',bus:'\\uD83D\\uDE8C',bags:'\\uD83D\\uDEC4',rest:'\\u2668\\uFE0F',walk:'\\uD83D\\uDEB6',subway:'\\uD83D\\uDE87',snow:'\\u2744\\uFE0F',airport:'\\u2708\\uFE0F',taxi:'\\uD83D\\uDE95',more:'\\u2795'};
  var SHORT={prayer:'Prayer room',baby:'Nursing room',quiet:'Quiet space',info:'Information counter',help:'Wheelchair and help',lockers:'Lockers',wifi:'Wi-Fi rental',shower:'Showers',internet:'Free internet',play:'Kids play area',smoking:'Smoking room',toilet:'Toilets',food:'Shops and food',money:'Money and ATMs',unwell:'Feeling unwell',pharmacy:'Pharmacy',trains:'Trains and platforms',tickets:'Tickets and passes',phone:'Phone and Wi-Fi',charge:'Phone charging',exits:'Which exit?',park:'Park',lost:'Lost and found',bus:'Bus to Sapporo',bags:'Bag storage',rest:'Hotels and onsen',walk:'Between terminals',subway:'Subway to Odori',snow:'Snow Festival',airport:'To the airport',taxi:'Taxis',more:'More places'};
  var term='ALL', lastTile=null;
  try{ var s=localStorage.getItem('sprTerm'); if(s&&/^(ALL|T1|T2)$/.test(s)) term=s; }catch(e){}
  function $(id){return document.getElementById(id);}
  /* side selector */
  var seg=$('seg');
  function segBtn(id,html,cls){
    var b=document.createElement('button'); b.type='button'; b.setAttribute('data-t',id); if(cls) b.className=cls;
    b.innerHTML=html; b.addEventListener('click',function(){ term=id; try{localStorage.setItem('sprTerm',id);}catch(e){} paintSeg(); renderDep(); }); return b;
  }
  var CAP={T1:['West','gate'],T2:['East','gate']};
  D.terms.forEach(function(t){ seg.appendChild(segBtn(t[0],'<small>'+CAP[t[0]][0]+'</small><b>'+CAP[t[0]][1]+'</b>')); });
  seg.appendChild(segBtn('ALL','Not sure','txt'));
  var mseg=$('mseg');
  D.terms.forEach(function(t){ mseg.appendChild(segBtn(t[0],'<small>'+CAP[t[0]][0]+'</small><b>'+CAP[t[0]][1]+'</b>')); });
  mseg.appendChild(segBtn('ALL','Not sure','txt'));
  function paintSeg(){ [seg,mseg].forEach(function(g){ [].forEach.call(g.children,function(b){ b.setAttribute('aria-pressed',b.getAttribute('data-t')===term?'true':'false'); }); }); paintMap(); }
  /* Floors tab: marks the level the person chose */
  function paintMap(){
    var personal=(term==='T1'||term==='T2');
    $('mLead').textContent=personal?(term==='T1'?'You are on the West gate side: Namboku Line (Odori), JR Information Desk, tourist information.':'You are on the East gate side: Toho Line. Some lifts and escalators here are out of use.'):'Namboku Line (Odori): west side. Toho Line: east side. Taxis: South Exit.';
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
  var subwayIt=['subway','Subway to Odori',{}];
  var snowIt=['snow','Snow Festival',{}];
  var airIt=['airport','To the airport',{}];
  var LIST=[];
  ['subway','snow','airport','info','tickets','lockers','money','help','taxi','food','toilet','unwell'].forEach(function(id){
    LIST.push(id==='subway'?subwayIt:id==='snow'?snowIt:id==='airport'?airIt:item(id));
  });
  LIST.forEach(function(it,n){
    var b=document.createElement('button'); b.type='button'; b.className='tile c'+(n%3); b.setAttribute('data-id',it[0]);
    var ic=document.createElement('span'); ic.className='ic'; ic.setAttribute('aria-hidden','true'); ic.textContent=ICON[it[0]]||'\\u2022';
    var tx=document.createElement('span'); tx.className='tx'; tx.textContent=SHORT[it[0]]||it[1];
    b.appendChild(ic); b.appendChild(tx);
    b.addEventListener('click',function(){ if(it[0]==='subway'){ openInfo(ICON.subway,it[1],subwayHTML(),b); } else if(it[0]==='snow'){ openInfo(ICON.snow,it[1],snowHTML(),b); } else if(it[0]==='airport'){ openInfo(ICON.airport,it[1],airportHTML(),b); } else { openSheet(it,b); } });
    (n<MAIN?tiles:tiles2).appendChild(b);
    if(n===MAIN-1){ tiles.appendChild(pill('pgnext','\\u2192','More','Taxis, shops, toilets, feeling unwell',function(){ slideTo(1); })); }
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
  var NONE='We did not find this on the official pages. Please ask station staff.';
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
  var SRCL='<p class="sm">Source: JR Hokkaido station map (as of 21 October 2026), checked 24 November 2026. The station is under construction. Follow the signs.</p>';
  function subwayHTML(){
    return '<p class="n2">Subway <b>Namboku Line N06</b> (west side) and <b>Toho Line H07</b> (east side). The subway writes the name さっぽろ.</p>'
      +'<ul class="pl"><li><b>Odori</b> (N07): 2 min on the Namboku Line. <b>Susukino</b> (N08): 3 min.</li>'
      +'<li><b>Towards Odori</b> (for Makomanai): first 6:09, last 0:09 on the timetable dated 28 February 2025. Check for a newer one.</li>'
      +'<li><b>Changing lines:</b> go out through the gates and back in within 30 minutes. Paper ticket: use the yellow transfer gates.</li>'
      +'<li><b>Exit 11:</b> into the Ekimae-dori underground walkway, towards Odori. <b>Exits 4 and 5</b> are closed.</li></ul>'
      +'<p class="sm">Source: Sapporo City Transportation Bureau, checked 24 November 2026.</p>'+more('#subway');
  }
  function snowHTML(){
    return '<p class="n2">Sapporo Snow Festival 2027: <b>Thu 4 to Thu 11 February 2027</b>.</p>'
      +'<ul class="pl"><li><b>Odori Park</b> (Nishi 1 to 11-chome): big snow sculptures, projection mapping. Namboku Line to Odori, 2 min.</li>'
      +'<li><b>Susukino:</b> ice sculptures. Namboku Line to Susukino, 3 min.</li>'
      +'<li><b>Tsudome:</b> slides, snow rafts, indoor food booths. Check the festival site for the way.</li>'
      +'<li>Opening and lighting times were not published yet. Dress warmly, with shoes that grip on snow.</li></ul>'
      +'<p class="sm">Source: Sapporo Snow Festival official site (Japanese), checked 24 November 2026.</p>'+more('#snow-festival');
  }
  function airportHTML(){
    return '<p class="n2">JR <b>Airport Train</b> to New Chitose Airport: fastest <b>33 min</b> (Special Rapid), 37 min (Rapid), 43 min (Semi-Rapid).</p>'
      +'<ul class="pl"><li><b>Platform:</b> check the departure boards. We did not find a current official platform list.</li>'
      +'<li><b>Seats:</b> cars 1 to 3 and 5 to 6 non-reserved. Car 4 is the reserved &ldquo;U seat&rdquo; car.</li>'
      +'<li><b>IC cards</b> (Suica, Kitaca and others) work. Ticket machines: cash only.</li>'
      +'<li><b>Luggage:</b> within 250 cm in total, up to 2 items, each up to 30 kg.</li>'
      +'<li>To the airport: first 5:50, last 22:25 (a local train, at the airport 23:12). JR timetable, 24 Nov 2026.</li>'
      +'<li>Rail passes for visitors (Sapporo area passes, Hokkaido Rail Pass) cover the Airport Train. Show your passport to buy one; put only the pass in the gate and take it back.</li>'
      +'<li><b>Bus instead:</b> from 11 Dec, Sapporo Station stop 5:25 to 18:15, about 77 min, no booking.</li>'
      +'<li><b>At the airport:</b> you arrive at B1F under the Domestic Terminal. International flight: walk the 2F corridor (3F closed).</li></ul>'
      +'<p class="sm">Source: JR Hokkaido and New Chitose Airport, checked 24 November 2026.</p>'+more('#airport');
  }
  function gatesHTML(){
    return '<ul class="pl"><li><b>West gate:</b> towards the Namboku Line. JR Information Desk (West Exit) and the tourist information center (West Concourse).</li>'
      +'<li><b>East gate:</b> towards the Toho Line. Some lifts and escalators out of use during the works; stairs usable.</li>'
      +'<li><b>South Exit plaza:</b> taxis. Daimaru to the south-west, Stellar Place to the south and south-east.</li>'
      +'<li><b>North Exit plaza:</b> on the north side.</li>'
      +'<li>Platform stairs 2 to 11 are inside the gates. Check the boards for your train.</li></ul>'+SRCL;
  }
  function deskHTML(){
    return '<ul class="pl"><li><b>JR Information Desk</b> (West Exit): 8:30 to 19:00. English, Chinese, Korean. Rail passes and tickets.</li>'
      +'<li><b>JR ticket office:</b> 5:40 to 22:00. Ticket machines 5:30 to 23:50.</li>'
      +'<li><b>Hokkaido-Sapporo Tourist Information Center</b> (West Concourse): 8:30 to 20:00, all year.</li></ul>'
      +'<p class="sm">Source: JR Hokkaido and the Sapporo Tourist Association, checked 24 November 2026.</p>';
  }
  function bagsHTML(){
    return '<ul class="pl"><li><b>About 800 lockers</b>, plus <b>5 for skis and snowboards</b>. The number changes with the works.</li>'
      +'<li>Up to 3 days, counting the first day. Key lockers take only 100-yen coins.</li>'
      +'<li>We did not find a locker map. Follow the signs.</li>'
      +'<li>Keep medicines, valuables and your passport with you.</li></ul>'
      +'<p class="sm">Source: JR Hokkaido locker list (July 2026) and the Sapporo Tourist Association, checked 24 November 2026.</p>';
  }
  function simHTML(){
    return '<ul class="pl"><li><b>eSIM:</b> install it on your phone and switch it on when you need it. No counter, no queue.</li>'
      +'<li><b>JR Wi-Fi</b> at stations and on the Airport Train cars (JR Hokkaido).</li></ul>';
  }
  var NEXT=[['🚇','Subway to Odori',subwayHTML],['🚪','Gates and exits',gatesHTML],['❄️','Snow Festival',snowHTML],['ℹ️','Help desks',deskHTML],['🧳','Lockers',bagsHTML],['✈️','To the airport',airportHTML],['🏔️','Day trips',dayHTML],['🏨','Hotels by the station',hotelHTML],['📱','Phone data',simHTML]];
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
  var ARR=[['Came on the Airport Train?','Follow the signs to the West or East gate. The station is under construction, so routes change.'],
    ['Need help?','JR Information Desk at the West Exit (8:30 to 19:00). Tourist Information Center in the West Concourse (8:30 to 20:00).'],
    ['Subway to Odori or Susukino','Namboku Line N06 (west side): Odori 2 min, Susukino 3 min.'],
    ['Taxi','The taxi stand is at the South Exit plaza.'],
    ['Lockers','About 800 lockers, 5 for skis and snowboards. Up to 3 days.']];
  var DEP=[['Flying from New Chitose?','JR Airport Train, fastest 33 min. Check the departure boards for the platform.'],
    ['Early flight?','First Airport Train 5:50, at the airport 6:28 (JR timetable, 24 Nov 2026). Check JR the day before.'],
    ['Snow forecast?','Leave earlier. Check JR Hokkaido Train Operation Information (English). If trains stop, JR lists buses and taxis, which can get very crowded.'],
    ['Bags','Collect them from the locker. Remember which side you used.'],
    ['Go to your platform','Check the display for your train, and your ticket for your car and seat.']];
  function renderDep(){ renderSteps($('depSteps'),DEP,doneD); }
  renderSteps($('arrSteps'),ARR,doneA); renderDep();
  $('arrReset').addEventListener('click',function(){ doneA.length=0; renderSteps($('arrSteps'),ARR,doneA); syncReset(); });
  $('depReset').addEventListener('click',function(){ doneD.length=0; renderDep(); syncReset(); });
  /* departure: before you go */
  var GUIDE='__GUIDE_URL__';
  function more(a){ return '<p class="sm"><a href="'+GUIDE+a+'">More in the full guide</a> (needs internet)</p>'; }
  function longHTML(){
    return '<ul class="pl"><li><b>Shinkansen:</b> not in Sapporo yet. The Hokkaido Shinkansen stations are Shin-Hakodate-Hokuto, Kikonai and Okutsugaru-Imabetsu.</li>'
      +'<li><b>Limited expresses:</b> all seats reserved since 14 March 2026 (JR). Book a seat.</li>'
      +'<li><b>Hakodate:</b> Limited Express Hokuto, about 3 h 30 min. It connects with the Shinkansen.</li>'
      +'<li><b>Asahikawa:</b> Limited Express Kamui and Lilac, 1 h 25 min at the quickest.</li>'
      +'<li><b>Kushiro:</b> Limited Express Ozora, about 4 h 11 min.</li>'
      +'<li><b>Otaru:</b> some Airport Trains go on there. Not the trains for Teine or Hoshimi.</li>'
      +'<li><b>Beyond Otaru</b> (Yoichi, Kutchan, Niseko): no IC cards. Buy a ticket first.</li></ul>'
      +'<p class="sm">Source: JR Hokkaido and the Sapporo Tourist Association, checked 24 November 2026.</p>'+more('#long-distance');
  }
  function dayHTML(){
    return '<p class="n2">Day trips by train. JR timetable, 24 Nov 2026 (a weekday). Times change.</p>'
      +'<ul class="pl"><li><b>Otaru:</b> Rapid Airport, 34 to 46 min, about every 30 min. IC cards work.</li>'
      +'<li><b>Noboribetsu:</b> Ltd. Exp. Suzuran or Hokuto, 70 to 82 min. Last back 21:21. Then the bus to the hot springs, 27 min (no IC cards on it).</li>'
      +'<li><b>Upopoy:</b> Shiraoi Station, North Exit, about 10 min on foot. Not every train stops.</li>'
      +'<li><b>Asahikawa:</b> Ltd. Exp. Lilac or Kamui, 85 min. Zoo: bus 41 or 47 from stop 6, about 40 min. Zoo open 10:30 to 15:30 in winter (closed 30 Dec to 1 Jan).</li>'
      +'<li><b>Biei, Furano:</b> no direct train in winter. Go via Asahikawa; local trains are few.</li>'
      +'<li><b>Limited expresses:</b> all seats reserved. Book a seat.</li>'
      +'<li><b>No IC cards</b> to Noboribetsu, Biei, Furano, Toya or beyond Otaru. SAPICA does not work on JR. Buy a paper ticket.</li>'
      +'<li><b>One-man trains:</b> press the door button. No ticket? Take a numbered ticket and pay the driver in cash.</li>'
      +'<li>Keep paper tickets out of phone cases.</li></ul>'
      +'<p class="sm">Source: JR Hokkaido, Donan Bus and Asahiyama Zoo, checked 24 November 2026.</p>'+more('#day-trips');
  }
  function skiHTML(){
    return '<p class="n2">Niseko ski bus. <b>Booking required</b>, 12 Dec 2026 to 22 Mar 2027 (dates depend on snow).</p>'
      +'<ul class="pl"><li><b>From Sapporo Station North Exit:</b> 7:50 and 9:20. At Niseko Hirafu 10:56 and 12:26.</li>'
      +'<li><b>Back from Hirafu:</b> 14:39 and 15:59. At Sapporo Station 17:45 and 19:05.</li>'
      +'<li><b>Book</b> by 18:00 the day before: online, or Chuo Bus Sapporo Terminal <a href="tel:0570200600">0570-200-600</a> (7:30 to 18:00). Pay at a counter on the day, or cash on the bus.</li>'
      +'<li>No ski boots on board. Skis and boards in a case.</li>'
      +'<li><b>Sapporo Kokusai ski area:</b> booked bus from the North Exit (taxi-pool side), about 1 h 37 min.</li></ul>'
      +'<p class="sm">Source: Hokkaido Chuo Bus and Niseko Bus, checked 24 November 2026.</p>'+more('#day-trips');
  }
  function hotelHTML(){
    return '<p class="n2">JR Hokkaido&rsquo;s group hotels at or near Sapporo Station.</p>'
      +'<ul class="pl"><li><b>JR Tower Hotel Nikko Sapporo:</b> next to the station, natural hot springs. <a href="https://klook.tpo.lu/zjYrWP25" target="_blank" rel="nofollow noopener sponsored">Rooms and prices</a> (partner link, needs internet)</li>'
      +'<li><b>JR Inn Sapporo:</b> 4 min walk from the West Ticket Gate. <a href="https://klook.tpo.lu/DdKj1ncR" target="_blank" rel="nofollow noopener sponsored">Rooms and prices</a> (partner link, needs internet)</li>'
      +'<li><b>JR Inn Sapporo N2:</b> near the station, the Clock Tower and Odori Park. <a href="https://klook.tpo.lu/Qn866IDt" target="_blank" rel="nofollow noopener sponsored">Rooms and prices</a> (partner link, needs internet)</li>'
      +'<li><b>JR Inn Sapporo South:</b> near Odori Park, easy to reach from Sapporo and Odori stations. <a href="https://klook.tpo.lu/vzyGqBYK" target="_blank" rel="nofollow noopener sponsored">Rooms and prices</a> (partner link, needs internet)</li></ul>'
      +'<p class="sm">Source: JR Hokkaido, checked 24 November 2026.</p>'+more('#hotels');
  }
  function allowHTML(){
    return '<p class="n2">Sapporo Station is being rebuilt for the Shinkansen. Add a buffer for walking, gates and luggage.</p>'
      +'<ul class="pl"><li>JR&rsquo;s map (21 October 2026) may change as the work goes on.</li>'
      +'<li>Some lifts and escalators by the East gate are out of use. Ask station staff for the step-free route.</li>'
      +'<li>We did not find official walking times inside the station, so we give none.</li></ul>'
      +'<p class="sm">Times are approximate and change. Check the operator.</p>';
  }
  var BEFORE=[['✈️','To the airport',airportHTML],['🏔️','Day trips',dayHTML],['⛷️','Ski bus to Niseko',skiHTML],['🚆','Hakodate and beyond',longHTML],['🚇','Subway',subwayHTML],['⏱️','Allow time',allowHTML]];
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
  [].forEach.call(dseg.children,function(b){ b.addEventListener('click',function(){ var w=b.getAttribute('data-d'); try{localStorage.setItem('sprDepSeg',w);}catch(e){} paintDep(w); }); });
  var dsv='before'; try{ var q=localStorage.getItem('sprDepSeg'); if(q==='air'||q==='before') dsv=q; }catch(e){}
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
    navigator.serviceWorker.register('/sapporo-sw.js',{scope:'/sapporo-pocket',updateViaCache:'none'})
      .then(function(){ return navigator.serviceWorker.ready; })
      .then(function(){ return caches.has('sapporo-pocket-v1'); })
      .then(function(ok){ saved=!!ok; if(!saved){ setTimeout(function(){ caches.has('sapporo-pocket-v1').then(function(k){ saved=!!k; paint(); }); },2500);} paint(); })
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
  function needed(){ return mobile&&!standalone&&flag('sprInstalled')!=='1'; }
  function refresh(){
    var n=needed(); strip.hidden=!n;
    $('instHow').hidden=!n; $('instDesk').hidden=mobile;
    if(standalone||flag('sprInstalled')==='1'){ $('install').hidden=true; }
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
  function markInstalled(){ flag('sprInstalled','1'); refresh(); }
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
    ['air','✈️','Airport train','新千歳空港行きの電車はどのホームですか？','Shin-Chitose-kuukou-iki no densha wa dono hoomu desu ka?','Which platform is the train to New Chitose Airport?'],
    ['air','🚇','Subway','地下鉄の乗り場はどこですか？','Chikatetsu no noriba wa doko desu ka?','Where is the subway?'],
    ['air','❄️','Snow Festival','雪まつりの会場はどこですか？','Yuki matsuri no kaijou wa doko desu ka?','Where is the Snow Festival site?'],
    ['air','🚪','West gate','西改札口はどこですか？','Nishi kaisatsuguchi wa doko desu ka?','Where is the West ticket gate?'],
    ['air','🚪','East gate','東改札口はどこですか？','Higashi kaisatsuguchi wa doko desu ka?','Where is the East ticket gate?'],
    ['air','🛗','Step-free route','エレベーターで行ける道を教えてください。','Erebeetaa de ikeru michi o oshiete kudasai.','Please show me a route I can take by lift.'],
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
  var askCat='basics'; try{ var sc=localStorage.getItem('sprAskCat'); if(sc&&ASKC.some(function(c){return c[0]===sc;})) askCat=sc; }catch(e){}
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
    b.addEventListener('click',function(){ askCat=c[0]; try{localStorage.setItem('sprAskCat',c[0]);}catch(e){} paintAsk(); });
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
    $('shareBtn').addEventListener('click',function(){ try{ navigator.share({title:'Sapporo Station Pocket Guide',url:location.origin+location.pathname+'?src=share'}); }catch(e){} });
  }
  window.addEventListener('beforeinstallprompt',function(e){ e.preventDefault(); dp=e; });
  window.addEventListener('appinstalled',function(){ pgTrack('pg_installed',{via:'browser'}); markInstalled(); if(!inst.hidden) closeSheet(); });
  /*__PG_HOOKS__*/
  refresh();
  if(needed()&&!flag('sprIntro')&&AUTO_INSTALL_SHEET){ flag('sprIntro','1'); setTimeout(function(){ if(sheet.hidden&&inst.hidden){ instVia='auto'; openInst(); } },700); }
})();
</script>
</body>
</html>
"""
POCKET_HTML = (POCKET_HTML.replace("__CSS__", POCKET_CSS).replace("__FINDER_JSON__", json.dumps(FINDER_DATA, ensure_ascii=False)).replace("__KLP_JSON__", json.dumps({k: v for k, v in KLK.items() if v}))
               .replace("__PG_BOOT__", PG_BOOT).replace("/*__PG_HOOKS__*/", PG_HOOKS).replace("__SVG__", POCKET_SVG).replace("__GUIDE_URL__", URL))
if re.search(r"\b(India|Indian|INR|Rs\.?|rupee|lakh|Aadhaar|UPI|VFS|BLS)\b|₹", re.sub(r"<script[^>]*>.*?</script>", "", POCKET_HTML, flags=re.S)):
    die("neutral-rule violation in the pocket guide")
for _bad in ("ueno-pocket", "new-chitose-pocket", "ctsTerm", "ctsInstalled", "Ueno", "Skyliner", "Keisei", "Panda", "Yamanote",
             "Tokyo Metro", "Busta", "Arrival Gate", "Portom", "Baggage Port", "at an information center"):
    if _bad in POCKET_HTML or _bad in page:
        die("leftover Ueno or New Chitose text in the Sapporo pages: %r" % _bad)

POCKET_SW = """/* Sapporo Station Pocket Guide service worker. Bump V when the page changes shape. */
var V='sapporo-pocket-v1';
var PAGE='/sapporo-pocket';
var SHELL=[PAGE,'/sapporo-pocket.webmanifest','/favicon-32.png','/images/sapporo-icon-192.png','/images/sapporo-icon-512.png','/images/sapporo-icon-maskable-512.png'];
self.addEventListener('install',function(e){
  e.waitUntil(caches.open(V).then(function(c){return c.addAll(SHELL);}).then(function(){return self.skipWaiting();}));
});
self.addEventListener('activate',function(e){
  e.waitUntil(caches.keys().then(function(ks){
    return Promise.all(ks.filter(function(k){return k.indexOf('sapporo-pocket-')===0&&k!==V;}).map(function(k){return caches.delete(k);}));
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
    "name": "Sapporo Station Pocket Guide",
    "short_name": "Sapporo",
    "description": "A simple Sapporo Station helper that works offline.",
    "start_url": POCKET_PATH,
    "scope": POCKET_PATH,
    "display": "standalone",
    "background_color": THEME,
    "theme_color": "#1a1a3e",
    "lang": "en",
    "icons": [
        {"src": "/images/sapporo-icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
        {"src": "/images/sapporo-icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
        {"src": "/images/sapporo-icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ],
}, indent=2) + "\n"
PUB = os.path.join(ROOT, "public")
for _ic in ("sapporo-icon-192.png", "sapporo-icon-512.png", "sapporo-icon-maskable-512.png", "sapporo-apple-touch-180.png"):
    if not os.path.isfile(os.path.join(PUB, "images", _ic)):
        die("pocket guide icon missing: public/images/" + _ic + " (the service worker would fail to install without it)")

# ---- anchors for the Japan guide link and the sitemap: check everything before writing anything
MARK = "sapporo-station-guide link"
jp = open(TEMPLATE, encoding="utf-8").read()
jp_new = jp
if MARK not in jp:
    anchor = re.search(r'(<!-- new-chitose-' + r'airport-guide link -->\s*<p>.*?</p>)', jp, re.S)
    if not anchor:
        die("anchor for the Japan guide link (New Chitose Airport sentence) not found: run the New Chitose Airport generator (w70) first")
    add = ('\n\n<!-- %s -->\n<p>Staying in Sapporo? Our <a href="/blog/%s">Sapporo Station guide</a> explains the West and East gates while the station is rebuilt for the Shinkansen, '
           'the subway to Odori and Susukino, the lockers, the Snow Festival dates and the Airport Train.</p>') % (MARK, SLUG)
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
for _k, _want in (("hero", HERO_URL),):
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
    changed.append("sapporo-station-guide.html (%s bytes)" % len(page.encode("utf-8")))
for _name, _content in (("sapporo-pocket.html", POCKET_HTML), ("sapporo-sw.js", POCKET_SW), ("sapporo-pocket.webmanifest", POCKET_MANIFEST)):
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
