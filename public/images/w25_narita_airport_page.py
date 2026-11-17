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


pickups = block("pickups-japan").replace("pickups-japan", "pickups-narita")
airalo = block("airalo-japan").replace("airalo-japan", "airalo-narita")

# DiscoverCars block for Narita (adapted from the Japan guide block; Narita pre-selected, no India framing)
cars = block("discovercars-japan-guide").replace("discovercars-japan-guide", "discovercars-narita")
cars = cars.replace('<div data-ps-placement="discovercars-narita"', '<div id="rent-a-car" data-ps-placement="discovercars-narita"', 1)
_h = "Rent a Car in Japan: Go Where Trains and Buses Don't"
if _h not in cars:
    die("cars heading not found")
cars = cars.replace(_h, "Rent a Car at Narita: Go Where Trains and Buses Don't")
_l = "Japan drives on the left, as in the UK, Australia and India."
if _l not in cars:
    die("cars left-hand line not found")
cars = cars.replace(_l, "Japan drives on the left.")
_on = 'class="ps-dc-chip on" data-country="japan" data-city="tokyo" data-place="hnd" aria-pressed="true"'
_off = 'class="ps-dc-chip" data-country="japan" data-city="tokyo" data-place="nrt" aria-pressed="false"'
if _on not in cars or _off not in cars:
    die("cars chips not found")
cars = cars.replace(_on, 'class="ps-dc-chip" data-country="japan" data-city="tokyo" data-place="hnd" aria-pressed="false"')
cars = cars.replace(_off, 'class="ps-dc-chip on" data-country="japan" data-city="tokyo" data-place="nrt" aria-pressed="true"')
if cars.count("&city=tokyo&place=hnd&locale=en") < 1:
    die("cars initial widget place not found")
cars = cars.replace("&city=tokyo&place=hnd&locale=en", "&city=tokyo&place=nrt&locale=en", 1)
if "India" in cars:
    die("India framing left in the Narita car block")

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
    "about": {"@type": "Airport", "name": "Narita International Airport", "iataCode": "NRT", "url": "https://www.narita-airport.jp/en/"},
}
ld_crumbs = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE},
        {"@type": "ListItem", "position": 2, "name": "Travel Essentials", "item": SITE + "/travel-essentials"},
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
    ("ic-card", "A train card (Suica or PASMO)"),
    ("to-tokyo", "Getting to Tokyo"),
    ("luggage", "Sending your suitcase to your hotel"),
    ("finder", "Find it fast: prayer room, baby room and more"),
    ("facilities", "Facilities by terminal"),
    ("help", "Help for older travellers and anyone who needs assistance"),
    ("leaving", "Leaving Narita"),
    ("layover", "A short stop or a long layover"),
    ("narita-or-haneda", "Narita or Haneda?"),
    ("faq", "FAQ"),
    ("about-this-guide", "About this guide and change log"),
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

DIAGRAM = """<figure class="ps-fig" id="at-a-glance">
<svg id="nrtDiagram" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 662" role="img" aria-labelledby="nrtT nrtD" font-family="Arial, Helvetica, sans-serif">
<title id="nrtT">Narita Airport at a glance</title>
<desc id="nrtD">Three terminals in a row along one line. Terminal 1 has its own train station, Narita Airport Station. Terminals 2 and 3 share one station, Airport Terminal 2\u00b73 Station, under Terminal 2. A free shuttle bus runs between Terminal 1 and Terminal 2, about 10 minutes. Between Terminals 2 and 3 it is about a 15 minute walk, or about 3 minutes by shuttle.</desc><rect width="480" height="662" fill="#fff"/><text x="240" y="38" font-size="26" font-weight="700" text-anchor="middle" fill="#0f0f23">Narita Airport at a glance</text><text x="240" y="64" font-size="17" text-anchor="middle" fill="#555">3 terminals, 2 train stations</text><line x1="44" y1="124" x2="44" y2="520" stroke="#00C9A7" stroke-width="6" stroke-linecap="round"/><circle cx="44" cy="124" r="22" fill="#00C9A7"/><text x="44" y="133" font-size="25" font-weight="700" text-anchor="middle" fill="#0f0f23">1</text><text x="90" y="132" font-size="26" font-weight="700" fill="#0f0f23">Terminal 1</text><text x="90" y="162" font-size="20" fill="#0f0f23">North Wing: SkyTeam airlines</text><text x="90" y="188" font-size="20" fill="#0f0f23">South Wing: Star Alliance, incl. ANA</text><rect x="90" y="206" width="370" height="34" rx="17" fill="#E7FAF5"/><g transform="translate(102,211)" fill="none" stroke="#0b6b59" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="1" width="16" height="18" rx="4"/><path d="M1 11h16"/><circle cx="5.5" cy="15" r="0.6" fill="#0b6b59"/><circle cx="12.5" cy="15" r="0.6" fill="#0b6b59"/><path d="M4 23l2-4M14 23l-2-4"/></g><text x="130" y="229" font-size="18" font-weight="700" fill="#0b6b59">Narita Airport Station</text><rect x="90" y="256" width="370" height="34" rx="17" fill="#FFF3E0" stroke="#F2C27B" stroke-width="1.5"/><text x="275.0" y="279" font-size="18" font-weight="600" text-anchor="middle" fill="#6b4a12">Free shuttle bus \u00b7 about 10 min</text><circle cx="44" cy="330" r="22" fill="#00C9A7"/><text x="44" y="339" font-size="25" font-weight="700" text-anchor="middle" fill="#0f0f23">2</text><text x="90" y="338" font-size="26" font-weight="700" fill="#0f0f23">Terminal 2</text><text x="90" y="368" font-size="20" fill="#0f0f23">oneworld airlines and others</text><rect x="90" y="386" width="370" height="34" rx="17" fill="#E7FAF5"/><g transform="translate(102,391)" fill="none" stroke="#0b6b59" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="1" width="16" height="18" rx="4"/><path d="M1 11h16"/><circle cx="5.5" cy="15" r="0.6" fill="#0b6b59"/><circle cx="12.5" cy="15" r="0.6" fill="#0b6b59"/><path d="M4 23l2-4M14 23l-2-4"/></g><text x="130" y="409" font-size="18" font-weight="700" fill="#0b6b59">Airport Terminal 2\u00b73 Station</text><rect x="90" y="436" width="200" height="34" rx="17" fill="#FFF3E0" stroke="#F2C27B" stroke-width="1.5"/><text x="190.0" y="459" font-size="18" font-weight="600" text-anchor="middle" fill="#6b4a12">Walk about 15 min</text><rect x="300" y="436" width="160" height="34" rx="17" fill="#FFF3E0" stroke="#F2C27B" stroke-width="1.5"/><text x="380.0" y="459" font-size="17" font-weight="600" text-anchor="middle" fill="#6b4a12">or shuttle 3 min</text><circle cx="44" cy="520" r="22" fill="#00C9A7"/><text x="44" y="529" font-size="25" font-weight="700" text-anchor="middle" fill="#0f0f23">3</text><text x="90" y="528" font-size="26" font-weight="700" fill="#0f0f23">Terminal 3</text><text x="90" y="558" font-size="20" fill="#0f0f23">Low-cost airlines</text><rect x="90" y="576" width="370" height="34" rx="17" fill="#FFF3E0"/><g transform="translate(102,581)" fill="none" stroke="#8a5a00" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="1" width="16" height="18" rx="4"/><path d="M1 11h16"/><circle cx="5.5" cy="15" r="0.6" fill="#8a5a00"/><circle cx="12.5" cy="15" r="0.6" fill="#8a5a00"/><path d="M4 23l2-4M14 23l-2-4"/></g><text x="130" y="599" font-size="18" font-weight="700" fill="#8a5a00">Uses the Terminal 2\u00b73 station</text><text x="240" y="648" font-size="14" text-anchor="middle" fill="#777">Simplified, not to scale. packsmartapp.com</text></svg>
<button type="button" class="ps-btn2" id="nrtDl">Download the diagram (PNG)</button>
</figure>
<script>
(function(){
  var b=document.getElementById('nrtDl'); if(!b) return;
  b.addEventListener('click',function(){
    try{
      var svg=document.getElementById('nrtDiagram');
      var xml=new XMLSerializer().serializeToString(svg);
      var img=new Image();
      img.onload=function(){
        var c=document.createElement('canvas'); c.width=960; c.height=1324;
        var x=c.getContext('2d'); x.fillStyle='#fff'; x.fillRect(0,0,c.width,c.height); x.drawImage(img,0,0,c.width,c.height);
        c.toBlob(function(bl){
          var a=document.createElement('a'); a.href=URL.createObjectURL(bl); a.download='narita-airport-at-a-glance.png';
          document.body.appendChild(a); a.click(); document.body.removeChild(a);
        },'image/png');
      };
      img.src='data:image/svg+xml;charset=utf-8,'+encodeURIComponent(xml);
    }catch(e){ window.print(); }
  });
})();
</script>"""

FINDER_DATA = {
    "terms": [["T1", "Terminal 1"], ["T2", "Terminal 2"], ["T3", "Terminal 3"]],
    "items": [
        ["toilet", "Toilets", {
            "T1": "Free toilets are in the public areas and also after security. Look for the toilet signs, or ask at an information counter. Accessible (multipurpose) toilets are available too.",
            "T2": "Free toilets are in the public areas and also after security. Look for the toilet signs, or ask at an information counter. Accessible (multipurpose) toilets are available too.",
            "T3": "Free toilets are in the public areas and also after security. Look for the toilet signs, or ask at an information counter. Accessible (multipurpose) toilets are available too."}],
        ["food", "Food, drink and water", {
            "T1": "Restaurants: mostly 4F and 5F of the Central Building. Convenience stores: B1F and 1F, and one is open all night. Water: fountains and hot and cold water points are in every terminal. Ask at an information counter for the nearest. Many restaurants close by about 9 pm. Hours change, so check the shop door. Narita Airport's website has a restaurant search with vegetarian and halal filters.",
            "T2": "Mostly Japanese food. Look on 4F, with more on lower floors. Convenience stores: B1F, 1F and 2F (Main Building), and one is open all night. There is reportedly a 24-hour beef bowl restaurant. Water: fountains and hot and cold water points are in every terminal. Ask at an information counter for the nearest. Many restaurants close by about 9 pm. Hours change, so check the shop door. Narita Airport's website has a restaurant search with vegetarian and halal filters.",
            "T3": "A food court on 2F, with some counters opening very early, around 4 am. A 24-hour convenience store is on 2F. After security the choice is limited, so eat before you go through. Water: fountains and hot and cold water points are in every terminal. Ask at an information counter for the nearest. Many restaurants close by about 9 pm. Hours change, so check the shop door. Narita Airport's website has a restaurant search with vegetarian and halal filters."}],
        ["prayer", "Prayer room", {
            "T1": "3F (passport-control area)",
            "T2": "1F, Main Building; and 3F, Main Building (passport-control area)",
            "T3": "2F, Main Building"}],
        ["baby", "Baby room", {
            "T1": "Baby rooms are on several floors. Ask at an information counter for the nearest one.",
            "T2": "Baby rooms are on several floors. Ask at an information counter for the nearest one.",
            "T3": "Baby rooms are on several floors. Ask at an information counter for the nearest one."}],
        ["quiet", "Quiet room", {
            "T1": "2F, domestic departure area; and 2F, international departure area",
            "T2": "2F, domestic departure area; and 2F, international departure area",
            "T3": "3F, Main Building (public area); 3F domestic departure; 3F international departure"}],
        ["info", "Information counter", {
            "T1": "B1F, 1F, 2F, 3F and 4F",
            "T2": "B1F, 1F and 3F (Main Building)",
            "T3": "1F and 2F (Main Building)"}],
        ["help", "Wheelchair and help", {
            "T1": "Go to an information counter (marked with a ? sign). Wheelchair rental, accessible toilets and special assistance are arranged through the airport. Narita Airport Information: +81 476-34-8000, open 24 hours.",
            "T2": "Go to an information counter (marked with a ? sign). Wheelchair rental, accessible toilets and special assistance are arranged through the airport. Narita Airport Information: +81 476-34-8000, open 24 hours.",
            "T3": "Go to an information counter (marked with a ? sign). Wheelchair rental, accessible toilets and special assistance are arranged through the airport. Narita Airport Information: +81 476-34-8000, open 24 hours."}],
        ["lockers", "Luggage lockers and storage", {
            "T1": "Coin lockers: B1F, 1F and 4F. Delivery and storage counters: 1F and 4F.",
            "T2": "Coin lockers: B1F and 3F (Main Building). Delivery and storage counters: 1F and 3F (Main Building).",
            "T3": "Coin lockers: 2F (Main Building). Delivery and storage counter: 1F (Main Building)."}],
        ["wifi", "Wi-Fi rental counter", {
            "T1": "1F and 4F",
            "T2": "B1F, 1F and 3F (Main Building)",
            "T3": "1F and 2F (Main Building)"}],
        ["shower", "Showers and day rooms (paid)", {
            "T1": "2F; and 3F (passport-control area)",
            "T2": "3F, Main Building (passport-control area)",
            "T3": ""}],
        ["smoking", "Smoking area", {
            "T1": "14 designated smoking areas in the terminal. Look for the smoking-room signs, or ask at an information counter. Smoking is not allowed anywhere else at the airport, inside or outside the terminals.",
            "T2": "19 designated smoking areas in the terminal. Look for the smoking-room signs, or ask at an information counter. Smoking is not allowed anywhere else at the airport, inside or outside the terminals.",
            "T3": "Narita's service list shows a smoking area in Terminal 3 but gives no details. Ask at an information counter. Smoking is not allowed anywhere else at the airport, inside or outside the terminals."}],
        ["play", "Children's play area", {
            "T1": "3F (paid Kids Park, after passport control); Baby Play Space",
            "T2": "2F, domestic services area (after departure procedures)",
            "T3": ""}],
        ["pharmacy", "Pharmacy and medicine", {
            "T1": "Pharmacies and drugstores: B1F and 4F (before security), and 3F (after security, international flights). Some medicines are sold only when a pharmacist is on duty. Opening hours vary, so check the shop.",
            "T2": "Pharmacies and drugstores in the Main Building: 2F (before security) and 3F (after security, international flights). Some medicines are sold only when a pharmacist is on duty. Opening hours vary, so check the shop.",
            "T3": "A drugstore on 2F, before security. It sells cold, pain and stomach medicine, masks and travel goods. Opening hours vary, so check the shop."}],
        ["charge", "Phone charging", {
            "T1": "Free power outlets are in a number of places in every terminal. Ask at an information counter for the nearest. Paid power bank rental (ChargeSPOT) is before security in every terminal, open 24 hours.",
            "T2": "Free power outlets are in a number of places in every terminal. Ask at an information counter for the nearest. Paid power bank rental (ChargeSPOT) is before security in every terminal, open 24 hours.",
            "T3": "Free power outlets are in a number of places in every terminal. Ask at an information counter for the nearest. Paid power bank rental (ChargeSPOT) is before security in every terminal, open 24 hours."}],
        ["money", "Money and ATMs", {
            "T1": "ATMs: 1F, 3F and 4F. Currency exchange: B1F, 1F, 3F and 4F. Exchange rates differ from shop to shop, so check the rate before you exchange.",
            "T2": "ATMs: B1F, 1F, 2F and 3F (Main Building). Currency exchange: B1F, 1F and 3F (Main Building). Exchange rates differ from shop to shop, so check the rate before you exchange.",
            "T3": "ATMs: 1F and 2F (Main Building). Currency exchange: 2F (Main Building), and a self-service currency machine on 3F after passport control. Exchange rates differ from shop to shop, so check the rate before you exchange."}],
        ["unwell", "Feeling unwell", {
            "T1": "There is a clinic on B1F. Opening hours are not shown on the airport list, so ask at an information counter (? sign) first. Narita Airport Information: +81 476-34-8000, open 24 hours. In an emergency, call 119 for an ambulance.",
            "T2": "The airport list does not show a clinic in Terminal 2. Go to an information counter (? sign) and ask for help. Narita Airport Information: +81 476-34-8000, open 24 hours. In an emergency, call 119 for an ambulance.",
            "T3": "The airport list does not show a clinic in Terminal 3. Go to an information counter (? sign) and ask for help. Narita Airport Information: +81 476-34-8000, open 24 hours. In an emergency, call 119 for an ambulance."}],
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
    var sm=document.createElement('small'); sm.textContent='From Narita Airport pages, checked 16 November 2026. Floors can change. If you cannot find it, ask at an information counter (look for the ? sign).'; rEl.appendChild(sm);
  }
})();
</script>"""
FINDER = FINDER.replace("__FINDER_JSON__", json.dumps(FINDER_DATA, ensure_ascii=False))

CHOOSER = """<h3>Where are you staying?</h3>
<div class="ps-scroll">
<table class="checklist-table">
<thead><tr><th>You are going to</th><th>Easiest choice</th><th>Why</th></tr></thead>
<tbody>
<tr><td><strong>Ueno, Nippori or Asakusa</strong></td><td>Keisei Skyliner (fast) or Access Express (cheaper)</td><td>Both run straight to that side of Tokyo.</td></tr>
<tr><td><strong>Tokyo Station, Shinjuku, Shibuya or Yokohama</strong></td><td>JR Narita Express</td><td>Direct, no changing trains, and there is room for suitcases.</td></tr>
<tr><td><strong>A large hotel or Tokyo Disney Resort</strong></td><td>Airport Limousine Bus</td><td>Stops at many hotels, so you do not carry bags up and down station stairs.</td></tr>
<tr><td><strong>Tokyo Station area, lowest cost</strong></td><td>TYO-NRT bus or Access Express</td><td>The cheapest direct choices.</td></tr>
<tr><td><strong>Tired, lots of luggage, or not sure</strong></td><td>Limousine bus or a pre-booked private transfer</td><td>Least walking and the fewest decisions.</td></tr>
</tbody>
</table>
</div>
"""

IC_CARD = """<h2 id="ic-card">A train card (Suica or PASMO)</h2>
<p>A tap-on travel card saves you buying a ticket for every train, subway or bus ride, and it also pays in many shops and vending machines. Visitors usually buy a tourist version, called Welcome Suica. It has no deposit, it is valid for 28 days, and any money left on it cannot be refunded.</p>
<ul>
<li><strong>Where at Narita:</strong> JR East Travel Service Centers and dedicated Welcome Suica ticket machines at Narita Airport Station (Terminal 1) and Airport Terminal 2·3 Station.</li>
<li><strong>Queues:</strong> expect a line just after a busy arrival. If the machine queue is long, try the service counter.</li>
<li><strong>iPhone users:</strong> an app version, Welcome Suica Mobile, lets you set up before you land (iPhone only, as of April 2026).</li>
<li><strong>Staying longer than 28 days?</strong> A regular Suica or PASMO may suit you better. Ask at the counter.</li>
</ul>
<div class="warning-box">
    <strong>This changes often.</strong> Sales points and card types have changed several times in recent years. Check <a href="https://www.jreast.co.jp/multi/en/welcomeSUICA/welcomeSUICA.html" target="_blank" rel="noopener noreferrer">JR East's Welcome Suica page</a> before you travel.
</div>"""

LUGGAGE = """<h2 id="luggage">Sending your suitcase to your hotel</h2>
<p>If you do not want to carry heavy bags on a crowded train, you can post them ahead. Two companies, JAL ABC and Yamato, run delivery counters at Narita. Ask which counter is in your terminal.</p>
<ul>
<li><strong>Usually next day.</strong> Most airport luggage delivery arrives the following day. Some same-day services exist, but they have cut-off times and can pause in busy seasons, so do not plan around same-day.</li>
<li><strong>Prices vary by size.</strong> A medium suitcase usually starts from about ¥1,950 (around 120 cm for length, width and height added together).</li>
<li><strong>Have these ready:</strong> your hotel name, address and phone number, written down.</li>
<li><strong>Keep with you:</strong> medicines, valuables, chargers and a change of clothes.</li>
</ul>
<p class="ps-note">Sources: <a href="https://tokyocheapo.com/travel/luggage-delivery-services" target="_blank" rel="noopener noreferrer">Tokyo Cheapo</a> and <a href="https://fun-japan.jp/en/articles/13685" target="_blank" rel="noopener noreferrer">Fun Japan</a>, checked 16 November 2026. Prices and cut-off times change, so confirm at the counter.</p>"""

HELP = """<h2 id="help">Help for older travellers and anyone who needs assistance</h2>
<p>You do not have to cope alone. Narita is set up to help, and asking early is easier than struggling.</p>
<ul>
<li><strong>Information counters.</strong> Look for the "?" sign. Staff can answer questions and solve problems.</li>
<li><strong>Phone help.</strong> Narita Airport Information is open 24 hours a day: +81 476-34-8000.</li>
<li><strong>Facilities.</strong> Narita lists accessible toilets, wheelchair rental, special-assistance and intercom services, and quiet rooms in all three terminals. Lifts have voice guidance, low buttons and Braille, and the terminal shuttle buses have low floors for wheelchairs.</li>
<li><strong>Trains.</strong> Reserved trains such as the Narita Express may have only one or two wheelchair spaces, so book early and tell station staff you need help.</li>
<li><strong>Before you fly.</strong> Ask your airline to arrange assistance at the airport when you book.</li>
</ul>
<p class="ps-note">Sources: <a href="https://www.narita-airport.jp/en/bf/" target="_blank" rel="noopener noreferrer">Narita Airport: customers requiring assistance</a>, <a href="https://www.narita-airport.jp/en/service/ud/" target="_blank" rel="noopener noreferrer">universal design facilities</a> and <a href="https://www.narita-airport.jp/en/service/ud/other-ud/" target="_blank" rel="noopener noreferrer">other facilities</a>; <a href="https://www.japan.travel/en/tokyo2020/barrier-free-for-everyone/" target="_blank" rel="noopener noreferrer">Japan National Tourism Organization</a>.</p>"""

LATE = """<h3>Landing late or leaving very early?</h3>
<p>The 9h nine hours Narita Airport capsule hotel sits inside the airport area next to Terminal 2·3 Station and has a 24-hour front desk. Its booking listing shows check-in from 2 pm to midnight and check-out by 10 am, and it asks you to tell them your arrival time in advance. From Terminal 1 or Terminal 3, use the terminal shuttle bus. The Japan National Tourism Organization lists it as the closest hotel for international flights.</p>"""

NRT_HND = """<h2 id="narita-or-haneda">Narita or Haneda?</h2>
<p>Many travellers cannot choose, because the airline decides. If you can choose, here is the short version.</p>
<div class="ps-scroll">
<table class="checklist-table">
<thead><tr><th></th><th>Narita (NRT)</th><th>Haneda (HND)</th></tr></thead>
<tbody>
<tr><td><strong>Where</strong></td><td>About 60 km east of Tokyo, in Chiba</td><td>Closer to central Tokyo</td></tr>
<tr><td><strong>Getting into the city</strong></td><td>About an hour or more</td><td>Usually quicker</td></tr>
<tr><td><strong>Flights</strong></td><td>Many international routes and low-cost airlines</td><td>Many domestic flights, plus international</td></tr>
<tr><td><strong>Good to know</strong></td><td>Three terminals; plan for the transfer</td><td>Often easier for a late arrival</td></tr>
</tbody>
</table>
</div>"""

ABOUT = """<div class="ps-about" id="about-this-guide">
<h2>About this guide</h2>
<p>Written by PackSmart. Our founder visited Narita in October 2026. Facility details were checked against Narita Airport's own pages on 16 November 2026, and transport fares and times are rounded ranges from several public sources. Spotted something out of date? <a href="/contact">Tell us</a> and we will fix it.</p>
<ul>
<li><strong>16 Nov 2026:</strong> first version.</li>
<li><strong>16 Nov 2026:</strong> added the find-it tool, the diagram, the train card, luggage, assistance, late arrival and Narita-or-Haneda sections.</li>
</ul>
</div>"""

def _card(title, text, slug, tag):
    return ('        <div class="related-card">\n            <div class="related-card-body">\n                <h4>%s</h4>\n                <p>%s</p>\n'
            '                <a href="https://www.packsmartapp.com%s">Read More <span class="related-arrow">&rarr;</span></a>\n                <div class="related-tag">%s</div>\n            </div>\n        </div>\n') % (title, text, slug, tag)

RELATED = ('<div class="related-posts">\n    <h3>Related Guides</h3>\n    <div class="related-grid">\n'
    + _card("Japan Travel and Packing Guide 2026", "What to pack, rail passes, etiquette and a budget breakdown for Tokyo, Kyoto and Osaka.", "/blog/japan-travel-packing-guide", "Destination Guide")
    + _card("Japan 7-Day Itinerary on a Budget", "A first week in Tokyo, Kyoto and Osaka, with costs.", "/blog/japan-7-day-itinerary-budget", "Itinerary")
    + _card("Best eSIM for International Travel", "Compare travel eSIMs before you fly.", "/blog/best-esim-international-travel-comparison", "Travel Essentials")
    + '    </div>\n</div>')

# hero image (optional): save the photo as public/images/narita-airport-hero.jpg (any of jpg/jpeg/png/webp), then run this script
def prepare_hero():
    imgdir = os.path.join(ROOT, "public", "images")
    src = None
    for ext in ("jpg", "jpeg", "png", "webp"):
        cand = os.path.join(imgdir, "narita-airport-hero." + ext)
        if os.path.isfile(cand):
            src = cand
            break
    if not src:
        return None, None
    dst = os.path.join(imgdir, "narita-airport-hero-1600.jpg")
    note = None
    if (not os.path.isfile(dst)) or os.path.getmtime(dst) < os.path.getmtime(src):
        import subprocess, shutil
        try:
            subprocess.run(["sips", "-Z", "1600", "-s", "format", "jpeg", "-s", "formatOptions", "72", src, "--out", dst],
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            note = "narita-airport-hero-1600.jpg (optimised from your photo)"
        except Exception:
            if src.lower().endswith(".jpg"):
                return "/images/" + os.path.basename(src), "using the original photo (could not optimise it here)"
            return None, None
    return "/images/narita-airport-hero-1600.jpg", note

HERO_URL, HERO_NOTE = prepare_hero()

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
<div class="ps-qr ps-qr-screen">__QR_SCREEN__<p><strong>Want it on your phone?</strong> Point your phone camera at this code. It opens the free Narita Pocket Guide, which works without internet once opened.<span class="u">packsmartapp.com/narita-pocket</span></p></div>
<div class="ps-qr ps-qr-print">__QR_PRINT__<p><strong>Free Narita Pocket Guide.</strong> Point your phone camera at this code. Open it once with signal and it works without internet.<span class="u">packsmartapp.com/narita-pocket</span></p></div>
<button type="button" class="ps-print-btn" onclick="window.print()">Print this card</button>
</div>"""
# QR codes are made once for each guide address (the Narita one has ?src=qr on screen, ?src=card on paper). For another airport ask Claude to make the two codes.
QR_SCREEN = '<svg shape-rendering="crispEdges" viewBox="0 0 41 41" class="segno"><title>QR code: open the Narita Pocket Guide</title><path fill="#fff" d="M0 0h41v41h-41z"/><path class="qrline" stroke="#000" d="M4 4.5h7m3 0h2m1 0h1m2 0h6m1 0h1m2 0h7m-33 1h1m5 0h1m3 0h1m1 0h6m6 0h1m1 0h1m5 0h1m-33 1h1m1 0h3m1 0h1m1 0h2m1 0h3m2 0h3m1 0h2m2 0h1m1 0h1m1 0h3m1 0h1m-33 1h1m1 0h3m1 0h1m1 0h2m1 0h1m2 0h1m1 0h1m3 0h1m1 0h1m3 0h1m1 0h3m1 0h1m-33 1h1m1 0h3m1 0h1m1 0h2m1 0h3m1 0h1m2 0h1m2 0h1m1 0h1m2 0h1m1 0h3m1 0h1m-33 1h1m5 0h1m1 0h1m1 0h7m1 0h1m1 0h2m4 0h1m5 0h1m-33 1h7m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h7m-25 1h2m5 0h1m5 0h4m-25 1h1m1 0h5m4 0h5m1 0h1m2 0h1m1 0h1m3 0h5m-29 1h2m1 0h1m2 0h4m7 0h3m1 0h1m2 0h2m1 0h4m-31 1h2m1 0h5m5 0h2m1 0h1m5 0h1m3 0h1m1 0h2m-32 1h1m8 0h2m3 0h3m2 0h1m1 0h3m1 0h2m1 0h4m-27 1h3m10 0h1m4 0h1m1 0h1m1 0h3m2 0h1m-32 1h1m1 0h3m2 0h3m1 0h5m3 0h4m2 0h1m2 0h4m-32 1h2m1 0h1m1 0h1m1 0h1m1 0h2m1 0h1m4 0h2m5 0h2m1 0h1m1 0h2m-30 1h1m6 0h1m1 0h1m1 0h1m2 0h1m1 0h6m1 0h2m1 0h3m-31 1h2m1 0h2m1 0h1m1 0h2m2 0h1m1 0h1m2 0h1m1 0h2m1 0h4m1 0h2m3 0h1m-31 1h1m1 0h2m1 0h1m2 0h1m3 0h1m1 0h2m1 0h2m2 0h5m1 0h2m1 0h1m-33 1h1m2 0h1m1 0h2m4 0h1m3 0h3m2 0h3m3 0h3m1 0h2m-30 1h2m1 0h1m1 0h8m1 0h3m2 0h3m1 0h6m1 0h1m-33 1h1m1 0h1m2 0h2m2 0h1m2 0h1m3 0h1m5 0h1m2 0h1m1 0h3m-30 1h1m1 0h4m1 0h2m4 0h3m2 0h1m3 0h3m1 0h1m3 0h1m1 0h1m-33 1h1m4 0h2m2 0h4m2 0h2m1 0h1m5 0h2m1 0h1m1 0h3m-32 1h1m2 0h1m1 0h1m3 0h1m5 0h1m2 0h1m2 0h2m2 0h3m2 0h2m-32 1h1m2 0h2m1 0h3m2 0h3m1 0h1m1 0h2m3 0h1m1 0h5m-21 1h4m1 0h1m2 0h1m1 0h7m3 0h1m1 0h3m-33 1h7m4 0h1m1 0h4m1 0h1m1 0h2m1 0h2m1 0h1m1 0h1m1 0h2m-32 1h1m5 0h1m1 0h1m3 0h1m1 0h1m5 0h5m3 0h4m-32 1h1m1 0h3m1 0h1m1 0h2m1 0h1m2 0h2m2 0h2m2 0h1m1 0h6m-30 1h1m1 0h3m1 0h1m1 0h4m2 0h4m3 0h3m1 0h1m2 0h2m1 0h2m-33 1h1m1 0h3m1 0h1m1 0h5m1 0h1m2 0h1m5 0h5m1 0h2m-31 1h1m5 0h1m2 0h2m5 0h1m1 0h2m1 0h3m1 0h1m2 0h3m-31 1h7m1 0h1m1 0h3m4 0h1m4 0h4m1 0h1m1 0h1m1 0h1"/></svg>'
QR_PRINT = '<svg shape-rendering="crispEdges" viewBox="0 0 41 41" class="segno"><title>QR code: open the Narita Pocket Guide</title><path fill="#fff" d="M0 0h41v41h-41z"/><path class="qrline" stroke="#000" d="M4 4.5h7m3 0h1m1 0h2m2 0h6m1 0h1m2 0h7m-33 1h1m5 0h1m2 0h1m2 0h6m6 0h1m1 0h1m5 0h1m-33 1h1m1 0h3m1 0h1m1 0h2m1 0h3m2 0h3m1 0h2m2 0h1m1 0h1m1 0h3m1 0h1m-33 1h1m1 0h3m1 0h1m1 0h1m2 0h1m2 0h1m1 0h1m5 0h1m3 0h1m1 0h3m1 0h1m-33 1h1m1 0h3m1 0h1m1 0h1m4 0h1m1 0h1m2 0h1m2 0h1m1 0h1m2 0h1m1 0h3m1 0h1m-33 1h1m5 0h1m1 0h1m4 0h4m1 0h1m2 0h1m4 0h1m5 0h1m-33 1h7m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h1m1 0h7m-25 1h5m2 0h1m5 0h4m-25 1h1m1 0h5m5 0h4m1 0h1m2 0h1m1 0h1m3 0h5m-31 1h1m1 0h1m4 0h1m1 0h1m1 0h2m6 0h3m1 0h1m2 0h2m1 0h4m-31 1h1m1 0h1m1 0h3m1 0h1m1 0h1m2 0h2m1 0h1m5 0h1m3 0h1m1 0h2m-31 1h1m2 0h2m1 0h1m1 0h2m3 0h3m2 0h1m1 0h3m1 0h2m1 0h4m-31 1h4m1 0h1m1 0h5m5 0h1m4 0h1m1 0h1m1 0h3m2 0h1m-32 1h1m2 0h1m5 0h3m1 0h3m4 0h3m2 0h1m2 0h4m-33 1h1m4 0h4m1 0h2m1 0h2m3 0h1m6 0h2m1 0h1m1 0h2m-32 1h2m5 0h2m1 0h5m1 0h1m1 0h1m1 0h4m1 0h2m1 0h3m-31 1h1m1 0h1m3 0h1m1 0h2m2 0h2m3 0h1m2 0h1m1 0h4m1 0h2m3 0h1m-33 1h1m2 0h1m3 0h2m3 0h2m2 0h2m1 0h2m2 0h5m1 0h2m1 0h1m-33 1h1m2 0h2m1 0h1m1 0h2m1 0h2m2 0h3m2 0h3m3 0h3m1 0h2m-28 1h2m4 0h1m2 0h1m2 0h3m2 0h3m1 0h6m1 0h1m-32 1h1m1 0h5m2 0h1m2 0h1m2 0h1m5 0h1m2 0h1m1 0h3m-30 1h2m5 0h1m1 0h1m1 0h3m1 0h1m2 0h3m2 0h2m1 0h1m3 0h1m1 0h1m-33 1h1m4 0h3m1 0h4m2 0h2m1 0h1m5 0h2m1 0h1m1 0h3m-32 1h1m2 0h3m1 0h3m1 0h1m2 0h2m2 0h2m1 0h2m2 0h3m2 0h3m-33 1h1m1 0h1m3 0h1m2 0h2m4 0h1m1 0h2m3 0h1m1 0h5m-21 1h1m1 0h1m1 0h1m3 0h1m1 0h7m3 0h1m1 0h3m-33 1h7m2 0h1m1 0h1m2 0h3m1 0h1m1 0h1m2 0h2m1 0h1m1 0h1m1 0h2m-32 1h1m5 0h1m1 0h1m1 0h3m7 0h5m3 0h4m-32 1h1m1 0h3m1 0h1m1 0h1m2 0h1m1 0h3m2 0h3m1 0h1m1 0h6m-30 1h1m1 0h3m1 0h1m1 0h1m1 0h1m2 0h1m1 0h3m1 0h3m1 0h1m1 0h1m2 0h2m1 0h2m-33 1h1m1 0h3m1 0h1m1 0h1m3 0h3m2 0h1m2 0h1m2 0h5m1 0h2m-31 1h1m5 0h1m3 0h1m3 0h1m1 0h1m1 0h1m2 0h3m1 0h1m2 0h3m-31 1h7m1 0h2m1 0h1m5 0h1m4 0h4m1 0h1m1 0h1m1 0h1"/></svg>'
CARD = CARD.replace("__QR_SCREEN__", QR_SCREEN).replace("__QR_PRINT__", QR_PRINT)

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
<p>Narita's own facility list shows Wi-Fi rental counters on the 1st and 4th floors of Terminal 1, the basement 1st, 1st and 3rd floors of the Terminal 2 main building, and the 1st and 2nd floors of the Terminal 3 main building. Counter hours and stock vary by company, so ordering ahead is safer.</p>"""


SAKURA_LINK = "https://p.sakuramobile.jp/idevaffiliate.php?id=728"
SAKURA_SIM_LINK = SAKURA_LINK  # TODO: swap for a link to Sakura's travel SIM page if the programme gives one (this one opens Sakura's home page)
SAKURA = """<div style="max-width:800px;margin:24px auto;padding:22px 24px;background:#f0faf7;border:1px solid #cdeee5;border-left:4px solid #00C9A7;border-radius:12px;">
  <style>.ps-sk-tile{transition:border-color .15s,box-shadow .15s}.ps-sk-tile:hover,.ps-sk-tile:focus-visible{border-color:#00C9A7!important;box-shadow:0 2px 10px rgba(0,201,167,.25)}.ps-sk-ghost{transition:background .15s}.ps-sk-tile:hover .ps-sk-ghost,.ps-sk-tile:focus-visible .ps-sk-ghost{background:#E7FAF5}</style>
  <strong style="display:block;font-size:1.1rem;color:#0f0f23;margin:0 0 6px 0;">No eSIM? Two other ways to get online</strong>
  <p style="margin:0 0 18px 0;font-size:0.9rem;color:#555;line-height:1.5;">An eSIM needs a compatible phone. If yours is not, or you would rather hold something real, choose a travel SIM card or a pocket Wi-Fi. Both are from Sakura Mobile.</p>
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:18px 12px;margin:14px 0 16px 0;">
  <a class="ps-sk-tile" data-ps-placement="sakura-narita-sim" href="__SAKURA_SIM_LINK__" target="_blank" rel="sponsored nofollow noopener" style="position:relative;display:flex;flex-direction:column;background:#fff;border:1.5px solid #cdeee5;border-radius:12px;padding:22px 16px 16px;text-decoration:none;text-align:center;color:#0f0f23;"><span style="position:absolute;top:-10px;left:50%;transform:translateX(-50%);background:#00C9A7;color:#fff;font-size:0.68rem;font-weight:700;letter-spacing:.03em;padding:2px 10px;border-radius:999px;white-space:nowrap;">FOR ONE TRAVELLER</span><span style="display:block;max-width:340px;width:100%;margin:0 auto 12px;"><picture><source type="image/webp" srcset="/images/sakura-sim-banner.webp"><img src="/images/sakura-sim-banner.png" width="380" height="364" loading="lazy" alt="Sakura Mobile Japan travel SIM card" style="display:block;width:100%;height:auto;border-radius:12px;"></picture></span><span style="display:block;font-size:1.5rem;font-weight:700;line-height:1.15;">Travel SIM card</span><span style="display:block;font-size:0.85rem;color:#666;line-height:1.35;margin:4px 0 10px;">Data only, no phone number</span><span style="display:block;font-size:1.05rem;font-weight:700;color:#0a8f78;">From &yen;3,500 before tax</span><span style="display:block;font-size:0.78rem;color:#777;line-height:1.3;margin:6px 0 10px;">3 GB a day on docomo, or unlimited on au</span><span style="flex:1;min-height:2px;display:block;"></span><span class="ps-sk-ghost" style="display:block;box-sizing:border-box;border:1.5px solid #00C9A7;color:#0a8f78;font-weight:700;font-size:1rem;border-radius:12px;padding:10px 14px;margin-top:6px;">Get a travel SIM &rarr;</span><span style="display:block;font-size:0.76rem;color:#777;margin-top:6px;">Sakura Mobile &middot; partner link</span></a>
  <a class="ps-sk-tile" data-ps-placement="sakura-narita-wifi" href="__SAKURA_LINK__" target="_blank" rel="sponsored nofollow noopener" style="position:relative;display:flex;flex-direction:column;background:#fff;border:1.5px solid #cdeee5;border-radius:12px;padding:22px 16px 16px;text-decoration:none;text-align:center;color:#0f0f23;"><span style="position:absolute;top:-10px;left:50%;transform:translateX(-50%);background:#00C9A7;color:#fff;font-size:0.68rem;font-weight:700;letter-spacing:.03em;padding:2px 10px;border-radius:999px;white-space:nowrap;">FOR FAMILIES AND GROUPS</span><span style="display:block;max-width:340px;width:100%;margin:0 auto 12px;"><picture><source type="image/webp" srcset="/images/sakura-wifi-banner.webp"><img src="/images/sakura-wifi-banner.png" width="570" height="546" loading="lazy" alt="Sakura Mobile pocket Wi-Fi device" style="display:block;width:100%;height:auto;border-radius:12px;"></picture></span><span style="display:block;font-size:1.5rem;font-weight:700;line-height:1.15;">Pocket Wi-Fi</span><span style="display:block;font-size:0.85rem;color:#666;line-height:1.35;margin:4px 0 10px;">One device for every phone</span><span style="display:block;font-size:1.05rem;font-weight:700;color:#0a8f78;">The price depends on your dates</span><span style="display:block;font-size:0.78rem;color:#777;line-height:1.3;margin:6px 0 10px;">Docomo network, data described as unlimited</span><span style="flex:1;min-height:2px;display:block;"></span><span class="ps-sk-ghost" style="display:block;box-sizing:border-box;border:1.5px solid #00C9A7;color:#0a8f78;font-weight:700;font-size:1rem;border-radius:12px;padding:10px 14px;margin-top:6px;">Rent a pocket Wi-Fi &rarr;</span><span style="display:block;font-size:0.76rem;color:#777;margin-top:6px;">Sakura Mobile &middot; partner link</span></a>
  </div>
  <p style="margin:0 0 8px;font-size:0.82rem;color:#666;line-height:1.5;"><strong style="color:#0a8f78;">Pick up:</strong> at the Sakura Mobile counter at Terminal 1 (South Wing, 1st floor) or Terminal 2 (1st floor), or at a post office. The SIM needs no return: throw it away after your trip. Post the pocket Wi-Fi back in the envelope that comes with it. A fair use policy may apply to unlimited data.</p>
  <p style="margin:0;font-size:0.82rem;color:#666;line-height:1.5;">Order ahead: same-day orders are possible, but stock is limited. There is no counter at Terminal 3: take the free shuttle bus or the sky bridge to Terminal 2.</p>
</div>""".replace("__SAKURA_SIM_LINK__", SAKURA_SIM_LINK).replace("__SAKURA_LINK__", SAKURA_LINK)

JB_LINK = "https://www.japan-bullettrain.com/?via=packsmart"
JB_SHIN = '<svg style="display:block;width:100%;height:auto;" aria-hidden="true" focusable="false" viewBox="0 0 320 170" xmlns="http://www.w3.org/2000/svg"><rect width="320" height="170" fill="#E8F1FE"/><circle cx="64" cy="40" r="20" fill="#FFE3CC"/><path d="M120 120 L188 44 L204 60 L214 52 L282 120Z" fill="#b9cdf0"/><path d="M174 62 L188 44 L204 60 L196 64 L188 58 L181 66Z" fill="#fff"/><path d="M0 124 L60 96 L110 120 L150 104 L200 124Z" fill="#d3e0f7"/><g fill="#f7b9cf"><circle cx="262" cy="104" r="14"/><circle cx="276" cy="112" r="12"/><circle cx="250" cy="114" r="11"/></g><rect x="260" y="112" width="4" height="22" fill="#8b5a3c"/><rect y="132" width="320" height="38" fill="#d3e0f7"/><rect y="146" width="320" height="4" fill="#9db8e6"/><g><path d="M14 138 L14 110 C14 104 20 100 28 100 L214 100 C250 100 286 118 306 138 Z" fill="#fff" stroke="#0f0f23" stroke-width="2.5"/><path d="M14 124 L300 124 L304 130 L14 130Z" fill="#2563EB"/><g fill="#7fb4f5" stroke="#0f0f23" stroke-width="1.5"><rect x="34" y="106" width="20" height="11" rx="2"/><rect x="62" y="106" width="20" height="11" rx="2"/><rect x="90" y="106" width="20" height="11" rx="2"/><rect x="118" y="106" width="20" height="11" rx="2"/><rect x="146" y="106" width="20" height="11" rx="2"/><rect x="174" y="106" width="20" height="11" rx="2"/></g><path d="M214 101 C238 102 262 112 282 124 L214 124Z" fill="#0f0f23" opacity=".9"/><g fill="#0f0f23"><circle cx="60" cy="140" r="5"/><circle cx="104" cy="140" r="5"/><circle cx="200" cy="140" r="5"/><circle cx="244" cy="140" r="5"/></g></g><g stroke="#2563EB" stroke-width="3" stroke-linecap="round"><path d="M4 108h22"/><path d="M0 118h16"/><path d="M6 128h12"/></g></svg>'
JB_TRAIN = '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M5 16V8a5 5 0 0 1 5-5h4a5 5 0 0 1 5 5v8a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2z"/><path d="M5 11h14M9 15h.01M15 15h.01M8 18l-2 3M16 18l2 3"/></svg>'


def jb_node(text):
    return '<div class="jb-rn"><span class="jb-dot"></span><strong style="color:#0f0f23;font-size:1rem;">%s</strong></div>' % text


def jb_leg(text, icon="", blue=False):
    return '<div class="jb-lg%s"><span class="jb-ln"></span><span class="jb-lt">%s%s</span></div>' % (" jb-blue" if blue else "", icon, text)


JB_SHINKANSEN = (
    '<div data-ps-placement="jw-shinkansen-narita" style="max-width:800px;margin:20px auto;padding:20px;background:#f0faf7;border:1px solid #cdeee5;border-left:4px solid #00C9A7;border-radius:12px;">'
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
    + jb_node("Narita Airport") + jb_leg("Narita Express, about 1 hour") + jb_node("Tokyo Station")
    + jb_leg("Shinkansen (bullet train)", JB_TRAIN, True) + jb_node("Kyoto") + jb_node("Osaka") +
    '</div></div>'
    '<div class="jb-row"><div class="jb-tx">'
    '<p style="margin:0 0 8px;font-size:0.95rem;line-height:1.5;color:#333;">The Shinkansen leaves from Tokyo Station. If you want your tickets sorted before you fly, you can book them online. The company says its tickets cover the JR East, JR West, JR Central and JR Kyushu Shinkansen lines and are collected with a QR code.</p>'
    '</div><div class="jb-bt">'
    '<a class="ps-jb-btn" href="' + JB_LINK + '" target="_blank" rel="nofollow noopener sponsored" style="display:block;box-sizing:border-box;text-decoration:none;"><span class="ps-jb-ghost" style="display:block;border:1.5px solid #00C9A7;background:#fff;color:#0a8f78;text-align:center;font-weight:700;font-size:1rem;border-radius:12px;padding:11px 14px;min-height:46px;line-height:1.25;">Book Shinkansen tickets &rarr;</span><span style="display:block;text-align:center;font-size:0.76rem;color:#777;margin-top:6px;">Japan Bullet Train &middot; partner link</span></a>'
    '<p style="margin:10px 0 0;font-size:0.85rem;line-height:1.5;color:#555;">You can also buy at a station on the day, so check the price and the change and cancellation rules before you pay.</p>'
    '</div></div></div>'
)


KL_SKY = '<svg aria-hidden="true" focusable="false" style="display:block;width:100%;height:auto;" viewBox="0 0 320 150" xmlns="http://www.w3.org/2000/svg"><rect width="320" height="150" fill="#E7FAF5"/><circle cx="262" cy="38" r="20" fill="#FDE9C8"/><path d="M0 112 L40 86 L62 100 L96 70 L128 104 L160 112Z" fill="#cdeee5"/><path d="M150 112 L196 78 L226 98 L262 66 L320 112Z" fill="#bfe6dc"/><rect y="112" width="320" height="38" fill="#d6f1ea"/><rect y="124" width="320" height="4" fill="#9bd7c9"/><g><path d="M26 118 C26 96 40 86 62 86 L258 86 C276 86 292 100 298 118 Z" fill="#fff" stroke="#0f0f23" stroke-width="2.5"/><path d="M26 108 L298 108 L298 114 L26 114Z" fill="#00C9A7"/><g fill="#0f0f23"><path d="M262 92 C274 92 284 100 288 108 L262 108Z"/></g><g fill="#7fd9ea" stroke="#0f0f23" stroke-width="1.5"><rect x="70" y="93" width="26" height="12" rx="3"/><rect x="104" y="93" width="26" height="12" rx="3"/><rect x="138" y="93" width="26" height="12" rx="3"/><rect x="172" y="93" width="26" height="12" rx="3"/><rect x="206" y="93" width="26" height="12" rx="3"/></g><g fill="#0f0f23"><circle cx="70" cy="122" r="5"/><circle cx="110" cy="122" r="5"/><circle cx="214" cy="122" r="5"/><circle cx="254" cy="122" r="5"/></g></g><g stroke="#00C9A7" stroke-width="3" stroke-linecap="round"><path d="M6 96h22"/><path d="M2 106h18"/><path d="M8 116h14"/></g></svg>'
KL_NEX = '<svg aria-hidden="true" focusable="false" style="display:block;width:100%;height:auto;" viewBox="0 0 320 150" xmlns="http://www.w3.org/2000/svg"><rect width="320" height="150" fill="#FDECEC"/><g fill="#f6cfcf"><rect x="20" y="60" width="26" height="52"/><rect x="52" y="44" width="30" height="68"/><rect x="88" y="68" width="22" height="44"/><rect x="214" y="52" width="28" height="60"/><rect x="248" y="70" width="24" height="42"/><rect x="278" y="48" width="30" height="64"/></g><rect y="112" width="320" height="38" fill="#f3dcdc"/><rect y="124" width="320" height="4" fill="#e3b4b4"/><g><path d="M20 118 L20 92 C20 88 24 86 28 86 L252 86 C276 86 292 98 300 118 Z" fill="#fff" stroke="#0f0f23" stroke-width="2.5"/><path d="M20 106 L300 106 L300 112 L20 112Z" fill="#E5484D"/><g fill="#9ad8e8" stroke="#0f0f23" stroke-width="1.5"><rect x="34" y="93" width="22" height="11" rx="2"/><rect x="62" y="93" width="22" height="11" rx="2"/><rect x="90" y="93" width="22" height="11" rx="2"/><rect x="118" y="93" width="22" height="11" rx="2"/><rect x="146" y="93" width="22" height="11" rx="2"/><rect x="174" y="93" width="22" height="11" rx="2"/><rect x="202" y="93" width="22" height="11" rx="2"/></g><path d="M254 92 C270 92 284 100 290 106 L254 106Z" fill="#0f0f23"/><g fill="#0f0f23"><circle cx="60" cy="122" r="5"/><circle cx="100" cy="122" r="5"/><circle cx="210" cy="122" r="5"/><circle cx="250" cy="122" r="5"/></g></g></svg>'
KL_BUS = '<svg aria-hidden="true" focusable="false" style="display:block;width:100%;height:auto;" viewBox="0 0 320 150" xmlns="http://www.w3.org/2000/svg"><rect width="320" height="150" fill="#FFF1E2"/><g fill="#fbd9b6"><rect x="14" y="40" width="40" height="74"/><rect x="60" y="62" width="28" height="52"/><rect x="236" y="34" width="44" height="80"/><rect x="284" y="64" width="26" height="50"/></g><g fill="#fff3e6"><rect x="22" y="50" width="8" height="8"/><rect x="38" y="50" width="8" height="8"/><rect x="22" y="66" width="8" height="8"/><rect x="38" y="66" width="8" height="8"/><rect x="246" y="46" width="8" height="8"/><rect x="262" y="46" width="8" height="8"/><rect x="246" y="62" width="8" height="8"/><rect x="262" y="62" width="8" height="8"/></g><rect y="116" width="320" height="34" fill="#efd3b3"/><rect y="132" width="320" height="3" fill="#fff" opacity=".6"/><g><rect x="52" y="64" width="216" height="56" rx="10" fill="#fff" stroke="#0f0f23" stroke-width="2.5"/><rect x="52" y="104" width="216" height="8" fill="#F97316"/><g fill="#9ad8e8" stroke="#0f0f23" stroke-width="1.5"><rect x="64" y="72" width="26" height="22" rx="3"/><rect x="96" y="72" width="26" height="22" rx="3"/><rect x="128" y="72" width="26" height="22" rx="3"/><rect x="160" y="72" width="26" height="22" rx="3"/><rect x="192" y="72" width="26" height="22" rx="3"/><rect x="228" y="72" width="30" height="30" rx="3"/></g><circle cx="94" cy="122" r="11" fill="#0f0f23"/><circle cx="94" cy="122" r="4" fill="#bbb"/><circle cx="226" cy="122" r="11" fill="#0f0f23"/><circle cx="226" cy="122" r="4" fill="#bbb"/></g></svg>'
KL_LBL = "display:block;font-weight:700;color:#0a8f78;font-size:0.76rem;letter-spacing:.03em;text-transform:uppercase;"
KL_VAL = "display:block;font-size:0.92rem;line-height:1.35;color:#0f0f23;"
KL_ROWS = [
    ("skyliner", "Keisei Skyliner", "Ueno, Nippori", "40 to 45 min", "&yen;2,500 to &yen;2,600", "Fastest train. Seats are reserved.", "https://klook.tpx.li/gIYih1CY", "See Skyliner tickets", KL_SKY),
    ("nex", "JR Narita Express (N'EX)", "Tokyo Station, Shinjuku, Shibuya, Yokohama", "About 1 hour to Tokyo Station", "&yen;3,100 to &yen;3,300", "Direct, with luggage racks. Seats are reserved.", "https://klook.tpx.li/tX4jclRv", "See N'EX tickets", KL_NEX),
    ("limousine", "Airport Limousine Bus", "Major hotels, Tokyo Disney Resort", "75 to 90 min", "&yen;3,200 or more", "Hotel-direct; easy with heavy luggage.", "https://klook.tpx.li/SISnlOYP", "See Limousine tickets", KL_BUS),
]


def kl_row(label, text):
    return '<div style="margin:0 0 7px;"><span style="%s">%s</span><span style="%s">%s</span></div>' % (KL_LBL, label, KL_VAL, text)


def kl_tile(r):
    pid, name, to, mins, price, note, link, btn, svg = r
    return (
        '<a class="ps-kl-tile" data-ps-placement="klook-narita-transport-%s" href="%s" target="_blank" rel="nofollow noopener sponsored" style="display:flex;flex-direction:column;background:#fff;border:1.5px solid #cdeee5;border-radius:12px;padding:12px 12px 14px;text-decoration:none;color:#0f0f23;">' % (pid, link)
        + '<span style="display:block;margin:0 0 10px;border-radius:12px;overflow:hidden;">%s</span>' % svg
        + '<strong style="display:block;font-size:1.1rem;color:#0f0f23;margin:0 0 8px;">%s</strong>' % name
        + kl_row("Goes to", to) + kl_row("About how long", mins) + kl_row("About how much", price)
        + '<p style="margin:0 0 12px;font-size:0.88rem;color:#555;line-height:1.4;">%s</p><span style="flex:1;min-height:4px;display:block;"></span>' % note
        + '<span class="ps-kl-ghost" style="display:block;box-sizing:border-box;border:1.5px solid #00C9A7;color:#0a8f78;text-align:center;font-weight:700;font-size:0.98rem;border-radius:12px;padding:10px 12px;min-height:46px;line-height:1.25;display:flex;align-items:center;justify-content:center;">%s&nbsp;&rarr;</span><span style="display:block;text-align:center;font-size:0.76rem;color:#777;margin-top:6px;">Klook &middot; partner link</span></a>' % btn.replace(" ", "&nbsp;", btn.count(" ") - 1)
    )


KLOOK_TRANSPORT = (
    '<div data-ps-placement="klook-narita-transport" style="max-width:800px;margin:20px auto;padding:20px;background:#f0faf7;border:1px solid #cdeee5;border-left:4px solid #00C9A7;border-radius:12px;">'
    '<style>.ps-kl-tile{transition:border-color .15s,box-shadow .15s}.ps-kl-tile:hover,.ps-kl-tile:focus-visible{border-color:#00C9A7!important;box-shadow:0 2px 10px rgba(0,201,167,.25)}.ps-kl-ghost{transition:background .15s}.ps-kl-tile:hover .ps-kl-ghost,.ps-kl-tile:focus-visible .ps-kl-ghost{background:#E7FAF5}</style>'
    '<strong style="display:block;font-size:1.1rem;color:#0f0f23;margin:0 0 6px;">Want your train or bus ticket sorted before you fly?</strong>'
    '<p style="margin:0 0 14px;font-size:0.95rem;color:#333;line-height:1.5;">You can buy these as e-tickets on Klook. You can also buy at the station or bus counter when you arrive, so booking ahead is a convenience, not a must.</p>'
    '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin:0 0 12px;">'
    + "".join(kl_tile(r) for r in KL_ROWS) +
    '</div>'
    '<p style="margin:0;font-size:0.85rem;color:#555;line-height:1.5;">Before you pay, read each listing\'s change and cancellation rules. Some Skyliner options cannot be cancelled, and Limousine Bus bookings cannot be amended: you cancel and rebook. Buses can run late in traffic, so leave a buffer. We earn a small commission if you book through these links, at no extra cost to you.</p>'
    '</div>'
)

TO_TOKYO = """<h2 id="to-tokyo">Getting to Tokyo</h2>
<p>Narita is far from the city, so choose your route by where you are staying. Times and prices below are approximate: they differ a little between sources and change over time, so check the operator before you go.</p>
""" + CHOOSER + """
<h3>All the options</h3>
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
""" + JB_SHINKANSEN + """
""" + KLOOK_TRANSPORT + """
<p>If you would rather have a driver waiting for you after a long flight, you can book a fixed-price private transfer in advance:</p>
""" + pickups + """
<p>If you are leaving Tokyo by road, you can also collect a rental car at Narita:</p>
""" + cars


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
<div id="psPocketBar" role="region" aria-label="Narita Pocket Guide">
<div class="t"><b>Get the Narita Pocket Guide</b><span>Free. Works offline at the airport.</span></div>
<a class="go" href="/narita-pocket?src=bar">Get it</a>
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
<p>Open the Narita Pocket Guide once while you have signal, then add it to your home screen. At the airport it opens like an app, even with no connection.</p>
<p><a class="ps-btn2" href="/narita-pocket?src=box" onclick="try{window.gtag&&gtag('event','pocket_prompt',{event_category:'engagement',action:'open_box',page_path:location.pathname});}catch(e){}" style="display:inline-block;text-decoration:none;">Open the Pocket Guide</a></p>
<ul>
<li><strong>iPhone:</strong> open it in Safari, tap the Share button, then "Add to Home Screen".</li>
<li><strong>Android:</strong> open it in Chrome, tap the menu (three dots), then "Add to Home screen" or "Install app".</li>
</ul>
</div>"""

FACILITIES = """<h2 id="facilities">Facilities by terminal</h2>
<p>This table follows Narita Airport's own facility pages, checked on 16 November 2026. Floor labels use the airport's wording. "Passport-control area" appears to mean the departure side, beyond the outbound passport check. A dash means the airport's list does not show one.</p>
<div class="ps-scroll">
<table class="checklist-table">
<thead><tr><th>Facility</th><th>Terminal 1</th><th>Terminal 2</th><th>Terminal 3</th></tr></thead>
<tbody>
<tr><td><strong>Prayer room</strong></td><td>3F (passport-control area)</td><td>1F, Main Building; 3F, Main Building (passport-control area)</td><td>2F, Main Building</td></tr>
<tr><td><strong>Quiet room</strong> (a small private space with 1 or 2 chairs)</td><td>2F domestic departure area; 2F international departure area</td><td>2F domestic departure area; 2F international departure area</td><td>3F Main Building (public area); 3F domestic departure; 3F international departure</td></tr>
<tr><td><strong>Smoking area</strong></td><td>14 designated areas (floors not listed)</td><td>19 designated areas (floors not listed)</td><td>Listed, but no details given</td></tr>
<tr><td><strong>Information counter</strong></td><td>B1F, 1F, 2F, 3F, 4F</td><td>B1F, 1F, 3F (Main Building)</td><td>1F, 2F (Main Building)</td></tr>
<tr><td><strong>Coin lockers</strong></td><td>B1F, 1F, 4F</td><td>B1F, 3F (Main Building)</td><td>2F (Main Building)</td></tr>
<tr><td><strong>Showers and day rooms</strong> (paid)</td><td>2F; 3F (passport-control area)</td><td>3F, Main Building (passport-control area)</td><td>-</td></tr>
<tr><td><strong>Wi-Fi rental counter</strong></td><td>1F, 4F</td><td>B1F, 1F, 3F (Main Building)</td><td>1F, 2F (Main Building)</td></tr>
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
<li><strong>Shopped tax-free?</strong> Since 1 November 2026 you pay the tax at the shop and claim it back at the airport. Within 90 days of buying, scan your passport at a tax-free kiosk in the international departure lobby <em>before</em> you check in bags, with your receipts and the items with you. At Narita you can also start online with Visit Japan Web. Allow extra time, as queues are likely while the system is new. See the <a href="https://www.japan.travel/en/us/blog/everything-you-need-to-know-japans-new-tax-free-shopping-system/" target="_blank" rel="noopener">Japan National Tourism Organization guide</a> (checked 16 November 2026).</li>
</ul>
<p data-ps-placement="bags-narita-tokyo" style="background:#f0faf7;border-left:3px solid #00C9A7;padding:12px 16px;border-radius:0 8px 8px 0;font-size:0.92rem;margin:20px 0;">&#129523; Checked out of your Tokyo hotel with hours to spare before a Narita flight? <a href="https://radicalstorage.tpx.li/d0Eds67a" target="_blank" rel="nofollow noopener sponsored" style="color:#00C9A7;text-decoration:underline;">Store your bags in Tokyo with Radical Storage</a> and travel light until it is time to go.</p>"""

LAYOVER = """<h2 id="layover">A short stop or a long layover</h2>
<p>If you have less than about 4 hours between flights, stay in the airport. Immigration, the train ride and the trip back eat up the time. With a longer wait you could visit Naritasan Shinjoji Temple, which is a short trip from the airport, or rest in a day room. Narita also has paid shower rooms and day rooms for a break between flights.</p>
<p data-ps-placement="klook-narita-layover">If you would rather not plan it yourself, Klook lists a <a href="https://klook.tpx.li/lGwthXzC" target="_blank" rel="nofollow noopener sponsored" style="color:#00C9A7;text-decoration:underline;">private half-day Narita layover tour</a> that visits the Naritasan approach street and the temple, with free cancellation up to 24 hours before. It has very few reviews so far, so read the listing first. Leaving the airport means passing immigration, so check whether you need a visa, and leave plenty of time to get back. We earn a small commission if you book through this link, at no extra cost to you.</p>"""




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
    '<p style="font-size:0.85rem;color:#666;margin:0 0 0.6rem;">Published November 16, 2026 · Last updated November 2026 · Facts checked 16 Nov 2026</p>',
    AFFILIATE_P,
    share,
    PRINT_CSS,
    '<p>Narita is the main airport for many visitors to Tokyo, but it is big, spread over three terminals, and far from the city. '
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
    NRT_HND,
    '<div class="tip-box">\n    <strong>Planning more of Japan?</strong> Our <a href="/blog/japan-travel-packing-guide">Japan travel and packing guide</a> covers what to pack, rail passes, etiquette and a budget breakdown, and the <a href="/blog/japan-7-day-itinerary-budget">7-day Japan itinerary</a> shows how a first week can look.\n</div>',
    "<!-- FIRST-HAND NOTES: add notes and photos from a recent Narita visit here -->",
    faq_html(),
    ABOUT,
    RELATED,
    POCKET_BAR,
])

# hero button (v50): a quiet way into the Pocket Guide from the top of the article
HERO_CTA = ('        <div style="margin:48px 0 0;text-align:center;">'
            '<a href="/narita-pocket?src=hero" onclick="try{window.gtag&&gtag(\'event\',\'pocket_prompt\',{event_category:\'engagement\',action:\'open_hero\',page_path:location.pathname});}catch(e){}" '
            'style="display:inline-flex;align-items:center;gap:12px;background:#00C9A7;color:#0f0f23;text-align:left;padding:12px 14px 12px 20px;width:340px;max-width:100%;box-sizing:border-box;border-radius:12px;text-decoration:none;min-height:44px;box-shadow:0 6px 18px rgba(0,0,0,.28);line-height:1.2;">'
            '<span style="flex:1;min-width:0;text-align:left;">'
            '<span style="display:block;font-weight:700;font-size:0.8rem;opacity:0.8;">Download to your phone</span>'
            '<span style="display:block;font-weight:800;font-size:1.05rem;margin-top:2px;">Narita Pocket Guide</span>'
            '<span style="display:block;font-weight:600;font-size:0.8rem;margin-top:2px;opacity:0.8;">Works offline</span></span>'
            '<span aria-hidden="true" style="flex:none;width:40px;height:40px;border-radius:50%;background:#F97316;display:flex;align-items:center;justify-content:center;box-shadow:0 2px 6px rgba(0,0,0,.18);">'
            '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M12 4v11M7 11l5 5 5-5M5 20h14"/></svg></span>'
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
    ('        <div style="position:absolute;left:12px;right:12px;bottom:8px;font-size:0.7rem;opacity:0.7;text-align:center;">Photo: susi-paku / PAKUTASO. Illustrative image of a Narita terminal.</div>' if HERO_URL else ''),
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
for _dom, _nm in (("p.sakuramobile.jp", "Sakura_Mobile"), ("japan-bullettrain.com", "Japan_Bullet_Train")):
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
    changed.append("narita-airport-guide.html (%s bytes)" % len(page.encode("utf-8")))


# ---- Narita Pocket Guide: standalone page + service worker + manifest (works offline once visited)
POCKET_PATH = "/narita-pocket"
# ---- Pocket Guide analytics (v47): anonymous taps only, no accounts, honours Do Not Track / GPC
GUIDE_ID = "narita"
AIRPORT_CODE = "NRT"
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
    if(/^tel:/i.test(h)){ var d=h.replace(/^tel:/i,'').replace(/[^0-9+]/g,''); var nm={'119':'fire_ambulance','110':'police','+81476348000':'airport','+815038162787':'help_line'}; pgTrack('pg_call',{dest:nm[d]||d,where:whereNow()}); return; }
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

POCKET_SVG = re.search(r'<svg id="nrtDiagram".*?</svg>', DIAGRAM, re.S).group(0).replace('id="nrtDiagram"', 'id="pkDiagram"').replace('id="nrtT"', 'id="pkT"').replace('id="nrtD"', 'id="pkD"').replace('aria-labelledby="nrtT nrtD"', 'aria-labelledby="pkT pkD"')
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
<title>Narita Pocket Guide | PackSmart</title>
<meta name="description" content="A simple Narita Airport helper that works offline: terminals, prayer rooms, baby rooms, lockers and more. By PackSmart.">
<meta name="robots" content="noindex,follow">
<link rel="canonical" href="__GUIDE_URL__">
<meta name="theme-color" content="#1a1a3e">
<link rel="manifest" href="/narita-pocket.webmanifest">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" href="/favicon-192.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Narita">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<script>__PG_BOOT__</script>
<style>__CSS__</style>
</head>
<body>
<header class="top">
<div><strong>Narita Pocket Guide</strong><span class="by">by PackSmart &middot; 16 Nov 2026</span></div>
<div class="status" id="status" role="status">Checking...</div>
</header>
<button type="button" class="inst-strip" id="instStrip" hidden><span class="ico" aria-hidden="true">&#128242;</span><span><b>Add this to your home screen</b><br>so it works with no internet</span><span class="go">How</span></button>
<div class="panels" id="panels">
<section class="panel" id="p-find" role="tabpanel" aria-labelledby="t-find">
<p class="seg-h">Which terminal are you in?</p>
<div class="seg" id="seg"></div>
<p class="seg-h" style="margin-top:14px">What do you need? <span class="small">Tap one.</span></p>
<div class="pager" id="pager"><div class="track" id="track"><div class="tiles pane" id="tiles"></div><div class="tiles pane off" id="tiles2" aria-hidden="true"></div></div></div>
<p class="hint">Floors can change. Ask at an information counter (? sign).</p>
<div id="sponsor" hidden></div>
<noscript><p class="card">This guide needs JavaScript. Please turn it on, or ask at any information counter (look for the ? sign).</p></noscript>
</section>
<section class="panel" id="p-map" role="tabpanel" aria-labelledby="t-map" hidden>
<p class="seg-h" style="margin-top:2px">Which terminal are you in?</p>
<div class="seg" id="mseg"></div>
<p class="lead2" id="mLead" style="margin-top:10px">Your ticket or airline app shows which one is yours.</p>
<div class="tmap" id="tmap">
<div class="tcard t1" data-t="T1"><div class="badge">1</div><div class="tb"><h3>Terminal 1</h3><p><span class="wing">North Wing</span> SkyTeam airlines</p><p><span class="wing">South Wing</span> Star Alliance, incl. ANA</p><p class="stn"><span aria-hidden="true">&#128646;</span> Narita Airport Station</p></div></div>
<div class="tlink"><span aria-hidden="true">&#128652;</span><span>Free shuttle bus: about 10 min</span></div>
<div class="tcard t2" data-t="T2"><div class="badge">2</div><div class="tb"><h3>Terminal 2</h3><p>oneworld airlines and others</p><p class="stn"><span aria-hidden="true">&#128646;</span> Airport Terminal 2&middot;3 Station</p></div></div>
<div class="tlink"><span aria-hidden="true">&#128694;</span><span>Walk about 15 min<br>or shuttle bus 3 to 6 min</span></div>
<div class="tcard t3" data-t="T3"><div class="badge">3</div><div class="tb"><h3>Terminal 3</h3><p>Low-cost airlines</p><p class="stn warn"><span aria-hidden="true">&#9888;&#65039;</span> No station of its own: use the Terminal 2&middot;3 station</p></div></div>
</div>
<p class="small" style="text-align:center;margin-top:10px">Simplified, not to scale. Airlines can change terminals, so check before you go. Shuttle buses can run late in traffic. <a href="https://www.narita-airport.jp/en/access/shuttlebus" target="_blank" rel="noopener noreferrer">Official shuttle bus page</a> (needs internet).</p>
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
<div class="heroline"><span class="big2">2 h</span><span><b>Arrive at least 2 hours early.</b><br>Your airline sets when check-in opens.</span></div>
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
<p class="sec-h">At Narita Airport only</p>
<a class="num air" href="tel:+81476348000"><span class="ni" aria-hidden="true">&#8505;&#65039;</span><span class="nt"><b>Narita Airport Information</b><span>+81 476-34-8000</span><small>Open 24 hours</small></span></a>
<p class="small" style="margin-top:8px">Every terminal has information counters. Look for the <strong>?</strong> sign. Staff will help, so just ask.</p>
<p class="sec-h">Help or travel questions</p>
<a class="num hot" href="tel:+815038162787"><span class="ni" aria-hidden="true">&#128222;</span><span class="nt"><b>Japan Visitor Hotline</b><span>050-3816-2787</span><small>24 hours. English, Chinese, Korean</small></span></a>
</div>
<div class="tiles hnav" id="hnav2"></div>
</div>
</div></div>
<div class="quiet"><div class="card slim" id="shareCard" hidden><div class="row"><div><h2>Helping someone travel?</h2><p>Send them this guide for offline use.</p></div><button type="button" class="big" id="shareBtn">Send it</button></div></div>
<div class="card slim install" id="install"><div class="row"><div><h2>Keep this on your phone</h2><p>Add it to your home screen. Works offline.</p><p class="small" id="instDesk">Open this page on your phone, then add it to your home screen.</p></div><div id="instHow" hidden><button type="button" class="big" id="instBtn">Show me</button></div></div></div>
<p class="small">Facility details come from Narita Airport's own pages, checked 16 November 2026. Floors, opening hours and counters can change. If you cannot find something, ask at an information counter. Found something out of date? <a href="/contact">Tell us</a> (needs internet). We count anonymous taps to improve this guide: no name, no account. <a href="/privacy-policy">Privacy</a> &middot; <a href="#" id="pgOpt">Turn off counting</a>. The full guide, with trains, SIM and luggage, is at <a href="__GUIDE_URL__">packsmartapp.com</a> (needs internet).</p></div>
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
  var SHORT={prayer:'Prayer room',baby:'Baby room',quiet:'Quiet room',info:'Information counter',help:'Wheelchair and help',lockers:'Luggage',wifi:'Wi-Fi rental',shower:'Showers, day rooms',internet:'Free internet',play:'Kids play area',smoking:'Smoking room',toilet:'Toilets',food:'Food and drink',money:'Money and ATMs',unwell:'Feeling unwell',pharmacy:'Pharmacy',trains:'Train, bus, taxi',phone:'Phone and Wi-Fi',charge:'Phone charging',more:'More places'};
  var term='ALL', lastTile=null;
  try{ var s=localStorage.getItem('nrtTerm'); if(s&&/^(ALL|T1|T2|T3)$/.test(s)) term=s; }catch(e){}
  function $(id){return document.getElementById(id);}
  /* terminal selector */
  var seg=$('seg');
  function segBtn(id,html,cls){
    var b=document.createElement('button'); b.type='button'; b.setAttribute('data-t',id); if(cls) b.className=cls;
    b.innerHTML=html; b.addEventListener('click',function(){ term=id; try{localStorage.setItem('nrtTerm',id);}catch(e){} paintSeg(); renderDep(); }); return b;
  }
  D.terms.forEach(function(t){ seg.appendChild(segBtn(t[0],'<small>Terminal</small><b>'+t[0].charAt(1)+'</b>')); });
  seg.appendChild(segBtn('ALL','Not sure','txt'));
  var mseg=$('mseg');
  D.terms.forEach(function(t){ mseg.appendChild(segBtn(t[0],'<small>Terminal</small><b>'+t[0].charAt(1)+'</b>')); });
  mseg.appendChild(segBtn('ALL','Not sure','txt'));
  function paintSeg(){ [seg,mseg].forEach(function(g){ [].forEach.call(g.children,function(b){ b.setAttribute('aria-pressed',b.getAttribute('data-t')===term?'true':'false'); }); }); paintMap(); }
  /* Terminals tab: personal view for the terminal the person chose */
  function paintMap(){
    var R={T1:{T2:'Free shuttle bus, about 10 min',T3:'Free shuttle bus, about 14 min'},
           T2:{T1:'Free shuttle bus, about 10 min',T3:'Walk about 15 min, or shuttle bus about 6 min'},
           T3:{T1:'Free shuttle bus, about 14 min',T2:'Walk about 15 min, or shuttle bus about 3 min'}};
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
  var PH_TXT=' Phone charging: free power outlets are in many places in every terminal, and paid power bank rental (ChargeSPOT) is before security, open 24 hours.';
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
    var st={T1:'Terminal 1: <b>Narita Airport Station</b>.',T2:'Terminal 2: <b>Airport Terminal 2&middot;3 Station</b>.',T3:'Terminal 3: <b>Airport Terminal 2&middot;3 Station</b>. Walk about 15 minutes, or take the shuttle bus (about 3 minutes).'};
    var h='<p class="n2">'+(term==='ALL'?[st.T1,st.T2,st.T3].join('<br>'):st[term])+'</p>';
    h+='<ul class="pl"><li><b>Skyliner:</b> about 40 to 45 min to Nippori or Ueno, &yen;2,500 to &yen;2,600. Reserved seats.</li>'
      +'<li><b>Narita Express:</b> about 1 hour to Tokyo Station, &yen;3,100 to &yen;3,300. Reserved seats.</li>'
      +'<li><b>Access Express:</b> 60 to 75 min to the Asakusa and Ueno area, about &yen;1,300. No seat booking.</li>'
      +'<li><b>Bus to Tokyo Station:</b> 65 to 90 min, about &yen;1,500.</li>'
      +'<li><b>Limousine bus to hotels:</b> 75 to 90 min, from &yen;3,200.</li>'
       +'<li><b>Taxi or private car:</b> door to door, 60 to 90 min. A metered taxi is often over &yen;20,000. A fixed-price private car is about &euro;139 per car (figure from the company, Nov 2026).</li></ul>';
    h+='<div class="tipbox">The Skyliner and Access Express can leave from the same platform. Check the train name and time. Trains are reported to stop around 11 pm.</div>';
    h+='<p class="sm">Times and prices are approximate and change. Check the operator.</p>';
    h+='<p class="sm">You can book tickets here (partner links): <a href="https://klook.tpx.li/gIYih1CY" target="_blank" rel="sponsored nofollow noopener">Skyliner</a> &middot; <a href="https://klook.tpx.li/tX4jclRv" target="_blank" rel="sponsored nofollow noopener">Narita Express</a> &middot; <a href="https://klook.tpx.li/SISnlOYP" target="_blank" rel="sponsored nofollow noopener">Limousine bus</a> &middot; <a href="https://tpx.li/qYFLwgZ8" target="_blank" rel="sponsored nofollow noopener">Private car</a></p>';
    return h;
  }
  function simHTML(){
    var w=item('wifi')[2], f=term==='ALL'?D.terms.map(function(t){return t[1]+': '+w[t[0]];}).join('<br>'):w[term];
    return '<ul class="pl"><li><b>eSIM:</b> install it before you fly. It works as soon as you land.</li>'
      +'<li><b>SIM and pocket Wi-Fi counters</b> are in the public areas, before passport control. Floors:<br>'+f+'</li>'
      +'<li><b>Free airport Wi-Fi:</b> FreeWiFi-NARITA. Fine for a quick message, not for a day of maps.</li></ul>'
      +'<p class="sm">Counter hours and stock vary. Ordering ahead is safer.</p>'
      +'<p class="sm">You can book pocket Wi-Fi here (partner link): <a href="https://p.sakuramobile.jp/idevaffiliate.php?id=728" target="_blank" rel="sponsored nofollow noopener">Sakura Mobile</a></p>';
  }
  function cashHTML(){
    return '<ul class="pl"><li><b>Currency exchange</b> offices are in the arrivals area.</li>'
      +'<li><b>Welcome Suica</b> is a tourist train card. No deposit, valid 28 days, and money left on it cannot be refunded.</li>'
      +'<li>Buy it at a JR East Travel Service Center or Welcome Suica machine at Narita Airport Station (Terminal 1) or Airport Terminal 2&middot;3 Station. Expect a queue after a busy arrival.</li>'
      +'<li>iPhone users can set up Welcome Suica Mobile before landing.</li></ul>'
      +'<p class="sm">Card types and sales points change often. Check JR East before you travel.</p>';
  }
  function carHTML(){
    return '<p class="n2">Most visitors skip a car in Tokyo, because trains are quicker.</p>'
      +'<ul class="pl"><li>A car helps for trips out of the city, such as Mt Fuji or the countryside. Narita is an easy place to pick one up.</li>'
      +'<li>Bring your <b>passport</b>, your <b>home driving licence</b> and an <b>International Driving Permit</b> (1949 Geneva Convention type). Get it before you leave home. It cannot be issued in Japan.</li>'
      +'<li>Some countries, such as Germany and France, use an official Japanese translation of the licence instead. Check before you travel.</li>'
      +'<li>Japan drives on the left.</li>'
      +'<li>Book ahead in busy seasons.</li></ul>'
      +'<p class="sm"><a href="'+GUIDE+'#rent-a-car">Compare car prices in the full guide</a> (needs internet)</p>';
  }
  function bagsHTML(){
    return '<ul class="pl"><li><b>JAL ABC</b> and <b>Yamato</b> run luggage delivery counters at Narita. Ask which counter is in your terminal.</li>'
      +'<li>Usually arrives <b>the next day</b>. A medium suitcase starts from about &yen;1,950.</li>'
      +'<li>Write down your hotel name, address and phone number.</li>'
      +'<li>Keep medicines, valuables and chargers with you.</li></ul>'
      +'<p class="sm">Prices and cut-off times change. Confirm at the counter.</p>'
       +'<p class="sm">You can book it here (partner link): <a href="https://klook.tpo.lu/dc2ejBgY" target="_blank" rel="sponsored nofollow noopener">Luggage delivery between Tokyo hotels and Narita</a> (Terminals 1 and 2).</p>';
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
  var ARR=[['Health check',"Hand in the plane's health form. Feeling unwell? Tell an officer."],
    ['Immigration','Show your passport. Automatic gates give no stamp: ask staff if you want one.'],
    ['Baggage claim','Find your flight on the screen and go to its carousel. Carts are nearby.'],
    ['Customs','Show your Visit Japan Web QR code or paper form. Food or plants? Declare them first.'],
    ['Arrivals lobby','You are in. Follow the signs to trains, buses and taxis.']];
  function ckText(){
    var f={T1:'4F',T2:'3F',T3:'2F'};
    if(term==='ALL') return 'Airline counters: Terminal 1 on 4F, Terminal 2 on 3F, Terminal 3 on 2F. Or use a kiosk or self bag drop.';
    return 'Terminal '+term.charAt(1)+': your airline counter is on '+f[term]+'. Or use a kiosk or self bag drop.';
  }
  var DEP=[['Tax-free kiosk, if you shopped','Scan your passport at the kiosk in the departure lobby before you check in any bags.'],
    ['Check in',ckText],
    ['Before security','Change money, sort roaming or insurance, hand back rented Wi-Fi. Spend any Welcome Suica balance: no refunds.'],
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
    var st={T1:'Terminal 1: get off at <b>Narita Airport Station</b>.',T2:'Terminal 2: get off at <b>Airport Terminal 2&middot;3 Station</b>.',T3:'Terminal 3: get off at <b>Airport Terminal 2&middot;3 Station</b>, then walk about 15 minutes or take the shuttle bus (about 3 minutes).'};
    var h='<p class="n2">'+(term==='ALL'?[st.T1,st.T2,st.T3].join('<br>'):st[term])+'</p>';
    h+='<ul class="pl"><li><b>Skyliner:</b> about 40 to 45 min from Ueno, &yen;2,500 to &yen;2,600. Reserved seats.</li>'
      +'<li><b>Narita Express:</b> about 1 hour from Tokyo Station, &yen;3,100 to &yen;3,300. Reserved seats.</li>'
      +'<li><b>Access Express:</b> 60 to 75 min, about &yen;1,300. No seat booking.</li>'
      +'<li><b>Bus from Tokyo Station:</b> 65 to 90 min, about &yen;1,500.</li>'
      +'<li><b>Limousine bus from hotels:</b> 75 to 90 min, from &yen;3,200.</li>'
       +'<li><b>Taxi or private car:</b> door to door, 60 to 90 min. A metered taxi is often over &yen;20,000. A fixed-price private car is about &euro;139 per car (figure from the company, Nov 2026).</li></ul>';
    h+='<div class="tipbox"><b>Early flight?</b> The first Skyliner leaves Keisei-Ueno at about 5:40 and the first Tokyo Station bus at about 5:00. Check first-train times the day before. For a very early flight you may need a bus, a taxi, or a hotel near the airport the night before.</div>';
    h+='<p class="sm">Times and prices are approximate and change. Check the operator.</p>';
    h+='<p class="sm">You can book tickets here (partner links): <a href="https://klook.tpx.li/gIYih1CY" target="_blank" rel="sponsored nofollow noopener">Skyliner</a> &middot; <a href="https://klook.tpx.li/tX4jclRv" target="_blank" rel="sponsored nofollow noopener">Narita Express</a> &middot; <a href="https://klook.tpx.li/SISnlOYP" target="_blank" rel="sponsored nofollow noopener">Limousine bus</a> &middot; <a href="https://tpx.li/qYFLwgZ8" target="_blank" rel="sponsored nofollow noopener">Private car</a></p>';
    return h;
  }
  function sendOutHTML(){
    return '<ul class="pl"><li><b>JAL ABC</b> and <b>Yamato</b> can collect your suitcase from your hotel and leave it at a Narita counter for you.</li>'
      +'<li>Book ahead: ask your hotel front desk or book online, <b>2 to 3 days before</b> your flight. Bags usually need to reach the airport the day before, so ask when to hand yours over.</li>'
      +'<li>On departure day, show your receipt and ID at the counter, collect the bag, then go to check-in.</li>'
      +'<li>Counters are in Terminals 1 and 2. Ask which one and its opening hours, especially for an early or late flight.</li>'
      +'<li>Keep your passport, medicines and valuables with you.</li></ul>'
      +'<p class="sm">A medium suitcase starts from about &yen;1,950. Rules, prices and cut-off times change: confirm with the company.</p>'
       +'<p class="sm">You can book it here (partner link): <a href="https://klook.tpo.lu/dc2ejBgY" target="_blank" rel="sponsored nofollow noopener">Luggage delivery between Tokyo hotels and Narita</a> (Terminals 1 and 2).</p>';
  }
  function taxHTML(){
    return '<p class="n2">From <b>1 November 2026</b> you pay the full price, tax included, at the shop. You claim the tax back at the airport.</p>'
      +'<ul class="pl"><li>Applies when you spend <b>&yen;5,000 or more</b> (before tax) at one shop in one day.</li>'
      +'<li>Within <b>90 days</b> of buying, scan your passport at a <b>tax-free kiosk</b> in the international departure lobby, <b>before you check in bags</b>. Have your receipts and the items with you.</li>'
      +'<li>At Narita you can also start online with <b>Visit Japan Web</b>.</li>'
      +'<li><b>Green</b> result: you are done. <b>Red</b> result: take the items to the customs inspection area.</li></ul>'
      +'<div class="tipbox">Finish this before you board. If you miss your flight, neither customs nor the airline pays you back. Queues are likely while the system is new, so allow extra time.</div>'
      +'<p class="sm">How the refund is paid is not covered in the official summary: ask at the kiosk or check your shop receipt. Source: Japan National Tourism Organization, checked 16 November 2026.</p>';
  }
  function earlyHTML(){
    return '<p class="n2">Narita advises arriving at the airport <b>at least 2 hours</b> before your flight.</p>'
      +'<ul class="pl"><li>Add the journey from central Tokyo: about <b>1 to 1.5 hours</b> by train or bus.</li>'
      +'<li>Add time to reach the station, and a little extra.</li>'
      +'<li>Terminal 3: add about 15 minutes to walk or take the shuttle from the station.</li>'
      +'<li>Shopped tax-free? Add time for the kiosk.</li></ul>'
      +'<div class="tipbox"><b>Example:</b> flight at 12:00. Be at the airport by 10:00. Leave central Tokyo by about 8:30.</div>'
      +'<p class="sm">Your airline decides when check-in opens and closes. Check your ticket.</p>';
  }
  var BEFORE=[['🚆','Getting to Narita',gettingHTML],['📦','Luggage to the airport',sendOutHTML],['🧾','Tax refund',taxHTML],['⏰','How early to leave',earlyHTML]];
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
  [].forEach.call(dseg.children,function(b){ b.addEventListener('click',function(){ var w=b.getAttribute('data-d'); try{localStorage.setItem('nrtDepSeg',w);}catch(e){} paintDep(w); }); });
  var dsv='before'; try{ var q=localStorage.getItem('nrtDepSeg'); if(q==='air'||q==='before') dsv=q; }catch(e){}
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
    navigator.serviceWorker.register('/narita-sw.js',{scope:'/narita-pocket',updateViaCache:'none'})
      .then(function(){ return navigator.serviceWorker.ready; })
      .then(function(){ return caches.has('narita-pocket-v2'); })
      .then(function(ok){ saved=!!ok; if(!saved){ setTimeout(function(){ caches.has('narita-pocket-v2').then(function(k){ saved=!!k; paint(); }); },2500);} paint(); })
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
  function needed(){ return mobile&&!standalone&&flag('nrtInstalled')!=='1'; }
  function refresh(){
    var n=needed(); strip.hidden=!n;
    $('instHow').hidden=!n; $('instDesk').hidden=mobile;
    if(standalone||flag('nrtInstalled')==='1'){ $('install').hidden=true; }
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
  function markInstalled(){ flag('nrtInstalled','1'); refresh(); }
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
  var askCat='basics'; try{ var sc=localStorage.getItem('nrtAskCat'); if(sc&&ASKC.some(function(c){return c[0]===sc;})) askCat=sc; }catch(e){}
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
    b.addEventListener('click',function(){ askCat=c[0]; try{localStorage.setItem('nrtAskCat',c[0]);}catch(e){} paintAsk(); });
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
    $('shareBtn').addEventListener('click',function(){ try{ navigator.share({title:'Narita Pocket Guide',url:location.origin+location.pathname+'?src=share'}); }catch(e){} });
  }
  window.addEventListener('beforeinstallprompt',function(e){ e.preventDefault(); dp=e; });
  window.addEventListener('appinstalled',function(){ pgTrack('pg_installed',{via:'browser'}); markInstalled(); if(!inst.hidden) closeSheet(); });
  /*__PG_HOOKS__*/
  refresh();
  if(needed()&&!flag('nrtIntro')&&AUTO_INSTALL_SHEET){ flag('nrtIntro','1'); setTimeout(function(){ if(sheet.hidden&&inst.hidden){ instVia='auto'; openInst(); } },700); }
})();
</script>
</body>
</html>
"""
POCKET_HTML = (POCKET_HTML.replace("__CSS__", POCKET_CSS).replace("__FINDER_JSON__", json.dumps(FINDER_DATA, ensure_ascii=False))
               .replace("__PG_BOOT__", PG_BOOT).replace("/*__PG_HOOKS__*/", PG_HOOKS).replace("__SVG__", POCKET_SVG).replace("__GUIDE_URL__", URL))
if re.search(r"\b(India|Indian|INR|Rs\.?|rupee|lakh|Aadhaar|UPI|VFS|BLS)\b|₹", re.sub(r"<script[^>]*>.*?</script>", "", POCKET_HTML, flags=re.S)):
    die("neutral-rule violation in the pocket guide")

POCKET_SW = """/* Narita Pocket Guide service worker. Bump V when the page changes shape. */
var V='narita-pocket-v2';
var PAGE='/narita-pocket';
var SHELL=[PAGE,'/narita-pocket.webmanifest','/favicon-32.png','/favicon-192.png','/favicon-512.png'];
self.addEventListener('install',function(e){
  e.waitUntil(caches.open(V).then(function(c){return c.addAll(SHELL);}).then(function(){return self.skipWaiting();}));
});
self.addEventListener('activate',function(e){
  e.waitUntil(caches.keys().then(function(ks){
    return Promise.all(ks.filter(function(k){return k.indexOf('narita-pocket-')===0&&k!==V;}).map(function(k){return caches.delete(k);}));
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
    "name": "Narita Pocket Guide",
    "short_name": "Narita",
    "description": "A simple Narita Airport helper that works offline.",
    "start_url": POCKET_PATH,
    "scope": POCKET_PATH,
    "display": "standalone",
    "background_color": "#1a1a3e",
    "theme_color": "#1a1a3e",
    "lang": "en",
    "icons": [
        {"src": "/favicon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
        {"src": "/favicon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
    ],
}, indent=2) + "\n"
PUB = os.path.join(ROOT, "public")
for _name, _content in (("narita-pocket.html", POCKET_HTML), ("narita-sw.js", POCKET_SW), ("narita-pocket.webmanifest", POCKET_MANIFEST)):
    _p = os.path.join(PUB, _name)
    _old = open(_p, encoding="utf-8").read() if os.path.isfile(_p) else None
    if _old != _content:
        open(_p, "w", encoding="utf-8").write(_content)
        changed.append("%s (%s bytes)" % (_name, len(_content.encode("utf-8"))))

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
