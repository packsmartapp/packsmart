#!/usr/bin/env python3
"""
w25: new page /blog/narita-airport-guide (neutral, plain-English airport guide, pilot page #1).

Run from the repo root:  python3 public/images/w25_narita_airport_page.py

What it does (idempotent):
  1. Builds public/blog/narita-airport-guide.html from the site template taken from
     public/blog/japan-travel-packing-guide.html (head, CSS, nav, footer, tracking scripts)
     plus new body content, the Airalo eSIM block and the Welcome Pickups block
     (copied from the Japan guide, placement ids renamed to *-narita).
  2. Adds one sentence linking to the new page in the Japan guide (marker: narita-airport-guide link).
  3. Adds the page to public/sitemap.xml and bumps the Japan guide's lastmod.
It does NOT touch public/blog.html (no photo for the index card yet).
Aborts without writing anything if an expected anchor is missing.
"""
import os, re, sys, json, html
from urllib.parse import quote

ROOT = os.getcwd()
BLOG = os.path.join(ROOT, "public", "blog")
SITEMAP = os.path.join(ROOT, "public", "sitemap.xml")
TEMPLATE = os.path.join(BLOG, "japan-travel-packing-guide.html")
OUT = os.path.join(BLOG, "narita-airport-guide.html")
SITE = "https://www.packsmartapp.com"
SLUG = "narita-airport-guide"
URL = "%s/blog/%s" % (SITE, SLUG)
TODAY = "2026-11-16"

TITLE = "Narita Airport Guide 2026: Terminals, Arrival, SIM & Transport | PackSmart"
H1 = "Narita Airport Guide 2026: Terminals, Arrival Steps, SIM and Getting to Tokyo"
DESC = ("Plain-English Narita Airport (NRT) guide: which terminal, steps after landing, SIM and eSIM, "
        "trains and buses to Tokyo, plus prayer rooms, baby rooms and quiet rooms.")
KEYWORDS = ("Narita airport guide, Narita airport terminals, Narita airport arrival, Narita to Tokyo, "
            "Narita airport SIM card, Narita airport eSIM, Narita airport prayer room, Narita airport facilities")


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
    (465, '<nav class="nav" id="nav">'),
    (477, "</nav>"),
]
for n, needle in checks:
    if needle not in line(n):
        die("template line %d does not contain %r (template changed?)" % (n, needle))
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


pickups = block("pickups-japan").replace("pickups-japan", "pickups-narita")
airalo = block("airalo-japan").replace("airalo-japan", "airalo-narita")

# Narita-specific fare line for the transfer block
old_fare = re.search(r'(<p data-ps-anchor="pickups"[^>]*>)Typical fares, airport to city centre:[^<]*(</p>)', pickups)
if not old_fare:
    die("pickups fare line not found")
pickups = pickups.replace(
    old_fare.group(0),
    old_fare.group(1)
    + "Typical fares, airport to city centre: Narita about €139 · Tokyo Haneda about €45. Per car, not per person."
    + old_fare.group(2),
)
# widget heading: keep as is. Wording below the widget stays generic.

# Airalo heading wording for an airport page
airalo = airalo.replace("Install it before you fly, switch it on when you land. No airport SIM queue.",
                        "Install it before you fly, switch it on when you land at Narita. No counter queue.")

# ---------------------------------------------------------------- body content
def esc(s):
    return html.escape(s, quote=False)


FAQ = [
    ("Is Narita Airport in Tokyo?",
     "No. Narita is in Chiba Prefecture, east of Tokyo. Plan on about an hour or more to reach central Tokyo."),
    ("Which terminal will my flight use?",
     "It depends on your airline, so check your ticket or airline app. As a general guide, Terminal 1 North Wing is used by SkyTeam airlines, "
     "Terminal 1 South Wing by Star Alliance airlines, Terminal 2 by oneworld airlines and others, and Terminal 3 by low-cost airlines."),
    ("Is there free Wi-Fi at Narita?",
     "Yes. Connect to FreeWiFi-NARITA. It works for quick messages, but it is not meant for a full day of maps and apps."),
    ("Do I need Visit Japan Web?",
     "It is not required, because you can still use paper forms. But registering on the free Visit Japan Web site before you fly lets you show QR codes "
     "for immigration and customs, which can speed up your arrival."),
    ("How do I get from Narita to central Tokyo?",
     "By train (Keisei Skyliner, JR Narita Express or the cheaper Keisei Access Express), by bus (the budget TYO-NRT bus or the Airport Limousine Bus), "
     "by taxi, or by a pre-booked private transfer. Trains are usually the quickest. Fares and times change, so check the operator before you go."),
    ("Is there a prayer room at Narita Airport?",
     "Yes, in every terminal. Narita's facility list shows one on the 3rd floor of Terminal 1, on the 1st and 3rd floors of the Terminal 2 main building, "
     "and on the 2nd floor of the Terminal 3 main building. If you cannot find it, ask at an information counter."),
    ("Where can I find a baby room or a quiet room?",
     "Baby rooms with a feeding booth, a nappy-changing counter, a sink and hot water are spread across the floors of the terminals. "
     "Narita also has small quiet rooms in each terminal. Ask at an information counter for the nearest one."),
    ("Can I walk between Terminal 2 and Terminal 3?",
     "Yes. It is about a 15-minute walk along a covered walkway, or a short shuttle bus ride of about 3 minutes. Terminal 3 has no train station of its own, "
     "so rail passengers use Terminal 2 station."),
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
}
ld_crumbs = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE},
        {"@type": "ListItem", "position": 2, "name": "Blog", "item": SITE + "/blog"},
        {"@type": "ListItem", "position": 3, "name": "Narita Airport Guide", "item": URL},
    ],
}


def ld(obj):
    return '<script type="application/ld+json">\n%s\n</script>' % json.dumps(obj, ensure_ascii=False)


TOC = [
    ("one-page", "Narita on one page"),
    ("terminals", "Which terminal?"),
    ("arrival", "Your first hour after landing"),
    ("connected", "Getting online: SIM, eSIM and Wi-Fi"),
    ("to-tokyo", "Getting to Tokyo"),
    ("facilities", "Facilities by terminal"),
    ("leaving", "Leaving Narita"),
    ("layover", "A short stop or a long layover"),
    ("faq", "FAQ"),
]
toc_html = ('<div class="toc">\n    <h3>Table of Contents</h3>\n    <ol>\n'
            + "\n".join('        <li><a href="#%s">%s</a></li>' % (i, esc(n)) for i, n in TOC)
            + "\n    </ol>\n</div>")

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
@media print{
  body *{visibility:hidden!important}
  .ps-card,.ps-card *{visibility:visible!important}
  .ps-card{position:absolute;left:0;top:0;width:100%;border:0;box-shadow:none}
  .ps-print-btn{display:none!important}
}
</style>"""

CARD = """<div class="ps-card" id="one-page">
<h2>Narita on one page</h2>
<ul>
<li><strong>Where:</strong> Narita is in Chiba, about an hour or more from central Tokyo.</li>
<li><strong>Terminals:</strong> there are 3. Terminals 1 and 2 each have a train station. Terminal 3 does not: walk to Terminal 2 (about 15 minutes) or take the free shuttle bus.</li>
<li><strong>Before you fly:</strong> register on Visit Japan Web (free) and keep the QR codes on your phone.</li>
<li><strong>After landing:</strong> immigration, then baggage, then customs, then the arrivals hall.</li>
<li><strong>In the arrivals hall:</strong> SIM and Wi-Fi counters, cash machines, convenience stores and train tickets.</li>
<li><strong>Free Wi-Fi:</strong> connect to FreeWiFi-NARITA for quick messages.</li>
<li><strong>Need help?</strong> Every terminal has information counters. Staff will help, so just ask.</li>
</ul>
<button type="button" class="ps-print-btn" onclick="window.print()">Print this card</button>
</div>"""

TERMINALS = """<h2 id="terminals">Which terminal?</h2>
<p>Narita has three terminals, and they are not next to each other. Check your ticket or airline app, because airlines can change terminals.</p>
<div class="ps-scroll">
<table class="checklist-table">
<thead><tr><th>Terminal</th><th>Who uses it</th><th>Train station</th></tr></thead>
<tbody>
<tr><td><strong>Terminal 1</strong></td><td>Most international airlines. North Wing: SkyTeam airlines. South Wing: Star Alliance airlines, including ANA.</td><td>Narita Airport Station (basement)</td></tr>
<tr><td><strong>Terminal 2</strong></td><td>oneworld airlines and others.</td><td>Airport Terminal 2 Station</td></tr>
<tr><td><strong>Terminal 3</strong></td><td>Low-cost airlines.</td><td>None. Use Terminal 2 station and walk or take the shuttle.</td></tr>
</tbody>
</table>
</div>
<div class="tip-box">
    <strong>Moving between terminals:</strong> a free shuttle bus links the terminals and takes about 10 minutes by road. Between Terminal 2 and Terminal 3 you can also take a 3-minute shuttle or walk for about 15 minutes.
</div>"""

ARRIVAL = """<h2 id="arrival">Your first hour after landing</h2>
<p>Most people follow the same four steps. Signs are in Japanese and English, and staff are nearby if you are unsure.</p>
<ol>
<li><strong>Before you fly (optional but helpful).</strong> Register on the free <a href="https://www.vjw.digital.go.jp/" target="_blank" rel="noopener noreferrer">Visit Japan Web</a> site. You enter your immigration and customs details once and get QR codes. Take a screenshot of them in case your signal is weak.</li>
<li><strong>Immigration.</strong> Have your passport ready. Narita's Terminals 1 and 2 have added self-service kiosks that handle immigration and customs together for foreign visitors (reported as fully running from 24 September 2026). Follow the signs and staff, and ask if you are unsure.</li>
<li><strong>Baggage claim.</strong> Find your flight on the screens and collect your bags.</li>
<li><strong>Customs.</strong> Show your Visit Japan Web QR code, or a paper declaration form (many flights hand these out).</li>
</ol>
<p>Then you arrive in the <strong>arrivals hall</strong>. At Terminals 1 and 2 you will find convenience stores, coffee shops, currency exchange, and SIM and pocket Wi-Fi counters. At Terminal 3 these services are on the 2nd floor. Train tickets are sold at the arrivals halls of Terminals 1 and 2.</p>
<div class="warning-box">
    <strong>Rules change.</strong> Immigration and customs procedures are updated often. If anything here differs from what the signs or officers tell you, follow the signs and officers.
</div>"""

CONNECTED = """<h2 id="connected">Getting online: SIM, eSIM and Wi-Fi</h2>
<p>You will want a connection soon after landing, for maps, messages and your hotel. Here are the usual choices.</p>
<div class="ps-scroll">
<table class="checklist-table">
<thead><tr><th>Option</th><th>How it works</th><th>Good to know</th></tr></thead>
<tbody>
<tr><td><strong>eSIM</strong></td><td>Install it on your phone before you fly. It works as soon as you land.</td><td>Needs an eSIM-ready, unlocked phone. No counter or queue.</td></tr>
<tr><td><strong>Tourist SIM card</strong></td><td>Buy or collect a SIM at a counter in the arrivals hall and swap it into your phone.</td><td>Keep your home SIM safe while you swap.</td></tr>
<tr><td><strong>Pocket Wi-Fi</strong></td><td>Pick up a small device that shares one connection with several phones.</td><td>You must return it. Return it before you reach the departures lobby, especially at Terminal 1.</td></tr>
<tr><td><strong>Airport free Wi-Fi</strong></td><td>Connect to FreeWiFi-NARITA.</td><td>Fine for a quick "I have landed" message, not for a full day of maps and apps.</td></tr>
</tbody>
</table>
</div>
<p>Narita's own facility list shows Wi-Fi rental counters on the 1st floor of Terminal 1, the basement 1st floor of the Terminal 2 main building, and the 1st and 2nd floors of the Terminal 3 main building. Counter hours and stock vary by company, so ordering ahead is safer.</p>"""

TO_TOKYO = """<h2 id="to-tokyo">Getting to Tokyo</h2>
<p>Narita is far from the city, so choose your route by where you are staying. Times and prices below are approximate: they differ a little between sources and change over time, so check the operator before you go.</p>
<div class="ps-scroll">
<table class="checklist-table">
<thead><tr><th>Option</th><th>Goes to</th><th>About how long</th><th>About how much</th><th>Good to know</th></tr></thead>
<tbody>
<tr><td><strong>Keisei Skyliner</strong></td><td>Nippori, Ueno</td><td>40 to 45 min</td><td>¥2,500 to ¥2,600</td><td>Fastest train. Seats are reserved.</td></tr>
<tr><td><strong>JR Narita Express (N'EX)</strong></td><td>Tokyo Station, Shinjuku, Shibuya, Yokohama</td><td>About 1 hour to Tokyo Station; longer to Shinjuku and Shibuya</td><td>¥3,100 to ¥3,300</td><td>Direct, with luggage racks. Seats are reserved.</td></tr>
<tr><td><strong>Keisei Access Express</strong></td><td>Asakusa, Ueno area</td><td>60 to 75 min</td><td>About ¥1,300</td><td>Cheapest train. A normal commuter train, so no seat reservation.</td></tr>
<tr><td><strong>TYO-NRT bus</strong></td><td>Tokyo Station (Yaesu South Exit)</td><td>65 to 90 min</td><td>About ¥1,500 (more late at night and early morning)</td><td>Cheapest direct option.</td></tr>
<tr><td><strong>Airport Limousine Bus</strong></td><td>Major hotels, Tokyo Disney Resort</td><td>75 to 90 min</td><td>¥3,200 or more</td><td>Hotel-direct; easy with heavy luggage.</td></tr>
<tr><td><strong>Taxi</strong></td><td>Door to door</td><td>60 to 90 min</td><td>Very expensive, often over ¥20,000</td><td>A fixed-price private transfer (below) is usually the better car option.</td></tr>
</tbody>
</table>
</div>
<div class="warning-box">
    <strong>Two trains look alike.</strong> The Skyliner and the Access Express can leave from the same platform. Check the train name and departure time on the display before you board.
</div>
<p><strong>Late arrival?</strong> The Narita Express and Skyliner are reported to stop around 11 pm, while buses run later. If you land late, check the last train before you book.</p>
<p><strong>Going on to Haneda?</strong> Keisei runs a direct train service to Haneda Airport (about 2 hours by Access Express), and a limousine bus takes about 85 minutes.</p>
<p>If you would rather have a driver waiting for you after a long flight, you can book a fixed-price private transfer in advance:</p>
""" + pickups

FACILITIES = """<h2 id="facilities">Facilities by terminal</h2>
<p>This table follows Narita Airport's own facility pages, checked on 16 November 2026. Floor labels use the airport's wording. "Passport-control area" appears to mean the departure side, beyond the outbound passport check. A dash means the airport's list does not show one.</p>
<div class="ps-scroll">
<table class="checklist-table">
<thead><tr><th>Facility</th><th>Terminal 1</th><th>Terminal 2</th><th>Terminal 3</th></tr></thead>
<tbody>
<tr><td><strong>Prayer room</strong></td><td>3F (passport-control area)</td><td>1F, Main Building; 3F, Main Building (passport-control area)</td><td>2F, Main Building</td></tr>
<tr><td><strong>Quiet room</strong> (a small private space with 1 or 2 chairs)</td><td>2F domestic departure area; 2F international departure area</td><td>2F domestic departure area; 2F international departure area</td><td>3F Main Building (public area); 3F domestic departure; 3F international departure</td></tr>
<tr><td><strong>Information counter</strong></td><td>B1F, 1F, 2F, 3F, 4F</td><td>B1F, 1F, 3F (Main Building)</td><td>1F, 2F (Main Building)</td></tr>
<tr><td><strong>Coin lockers</strong></td><td>B1F, 1F, 4F</td><td>B1F, 3F (Main Building)</td><td>2F (Main Building)</td></tr>
<tr><td><strong>Showers and day rooms</strong> (paid)</td><td>2F; 3F (passport-control area)</td><td>3F, Main Building (passport-control area)</td><td>-</td></tr>
<tr><td><strong>Wi-Fi rental counter</strong></td><td>1F</td><td>B1F, Main Building</td><td>1F, 2F (Main Building)</td></tr>
<tr><td><strong>Free internet point</strong></td><td>4F</td><td>1F, Main Building</td><td>-</td></tr>
<tr><td><strong>Children's play area</strong></td><td>3F (paid Kids Park, after passport control); Baby Play Space</td><td>2F, domestic services area (after departure procedures)</td><td>-</td></tr>
</tbody>
</table>
</div>
<h3>Baby and nursing rooms</h3>
<p>Baby rooms are spread across the floors of the terminals. They are described as having a breast-feeding booth, a nappy-changing counter, a wash basin and a hot water dispenser. The airport's pages we checked do not give a floor-by-floor list, so ask at an information counter for the nearest one.</p>
<h3>If you need help</h3>
<p>Every terminal has information counters, and staff there speak several languages. If you are tired, unsure or carrying a lot, go straight to a counter instead of searching on your own.</p>
<p class="ps-note">Sources: Narita Airport's own pages on <a href="https://www.narita-airport.jp/en/service/ud/guide/" target="_blank" rel="noopener noreferrer">facility layout</a>, <a href="https://www.narita-airport.jp/en/service/ud/cool-down/" target="_blank" rel="noopener noreferrer">quiet rooms</a> and <a href="https://www.narita-airport.jp/en/service/child/kid/" target="_blank" rel="noopener noreferrer">Kids Park</a>. Floors and opening hours can change, so confirm on the day. Found something out of date? <a href="/contact">Tell us</a>.</p>"""

LEAVING = """<h2 id="leaving">Leaving Narita</h2>
<ul>
<li><strong>Know your terminal.</strong> The stations are different: Terminal 1 has its own, while Terminals 2 and 3 share one. Check before you set off.</li>
<li><strong>Terminal 3 takes longer.</strong> If you arrive by train, you get off at Terminal 2 and walk about 15 minutes or take the shuttle. Allow extra time.</li>
<li><strong>Return rented gear first.</strong> If you rented a pocket Wi-Fi, hand it back before you reach the departures lobby, especially at Terminal 1.</li>
<li><strong>Allow time.</strong> Check-in, security and passport control all take time, so arrive early.</li>
</ul>"""

LAYOVER = """<h2 id="layover">A short stop or a long layover</h2>
<p>If you have less than about 4 hours between flights, stay in the airport. Immigration, the train ride and the trip back eat up the time. With a longer wait you could visit Naritasan Shinjoji Temple, which is a short trip from the airport, or rest in a day room. Narita also has paid shower rooms and day rooms for a break between flights.</p>"""

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
    AFFILIATE_P,
    share,
    PRINT_CSS,
    '<p>Narita is the main airport for many visitors to Tokyo, but it is big, spread over three terminals, and far from the city. '
    'This guide is written in plain English so that a first-time visitor, a family or an older traveller can follow it step by step. '
    'You can print the one-page card below and carry it with you.</p>',
    toc_html,
    CARD,
    TERMINALS,
    ARRIVAL,
    CONNECTED,
    airalo,
    TO_TOKYO,
    FACILITIES,
    LEAVING,
    LAYOVER,
    '<div class="tip-box">\n    <strong>Planning more of Japan?</strong> Our <a href="/blog/japan-travel-packing-guide">Japan travel and packing guide</a> covers what to pack, rail passes, etiquette and a budget breakdown, and the <a href="/blog/japan-7-day-itinerary-budget">7-day Japan itinerary</a> shows how a first week can look.\n</div>',
    "<!-- FIRST-HAND NOTES: add notes and photos from a recent Narita visit here -->",
    faq_html(),
])

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
    '    <meta property="og:image" content="%s/og-default.png">' % SITE,
    '    <meta name="twitter:card" content="summary_large_image">',
    '    <meta name="twitter:title" content="%s">' % html.escape(TITLE),
    '    <meta name="twitter:description" content="%s">' % html.escape(DESC),
    '    <meta name="twitter:image" content="%s/og-default.png">' % SITE,
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
    "\n".join(t[464:477]),
    "",
    '    <div class="hero-blog" style="background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 100%);">',
    "        <h1>%s</h1>" % esc(H1),
    '        <div class="meta">November 16, 2026 · 8 min read</div>',
    '        <div class="meta">Airport Guide • Japan</div>',
    '        <div class="meta">Last updated: November 2026</div>',
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

changed = []
old = open(OUT, encoding="utf-8").read() if os.path.isfile(OUT) else None
if old != page:
    open(OUT, "w", encoding="utf-8").write(page)
    changed.append("narita-airport-guide.html (%s bytes)" % len(page.encode("utf-8")))

# ---- link from the Japan guide
MARK = "narita-airport-guide link"
jp = open(TEMPLATE, encoding="utf-8").read()
if MARK not in jp:
    anchor = re.search(r'(<div class="tip-box">\s*<strong>Pro Tip:</strong> Use the Visit Japan Web portal[^<]*</div>)', jp)
    if not anchor:
        die("anchor for the Japan guide link not found")
    add = ('\n\n<!-- %s -->\n<p>Landing at Narita? Our <a href="/blog/%s">Narita Airport guide</a> explains the terminals, the arrival steps, SIM and eSIM options, '
           'trains and buses to Tokyo, and airport facilities such as prayer rooms and baby rooms.</p>') % (MARK, SLUG)
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
