#!/usr/bin/env python3
"""
w73: the Japan hub page /japan, and a "Welcome to Japan" banner on /blog when the Japan chip is picked (24 Nov 2026).

Why: Japan is the lead topic (D48), but its guides were spread over /blog (country guides, itinerary) and
/travel-essentials (airport and station guides), and nothing showed them together with the Pocket Guides.
The owner's mock-up: pick Japan on /blog and see every Japan guide and Pocket Guide in one place.

What it does (idempotent; every run rebuilds public/japan.html from the current pages):
  1. Builds public/japan.html from public/travel-essentials.html (head, styles, nav, footer, filter script, and its
     Pocket Guide block with ?src=hub_japan), with three filterable sections of cards: Plan your trip (cards copied
     from /blog), Arriving and Stations (cards copied from /travel-essentials, so titles, photos and read times stay in
     step with w59 and w69). Below them, link lists for Hokkaido this winter and for the seasons.
     An empty slot (<!-- ask-japan-slot -->) is kept for the planned "Ask about Japan" assistant.
  2. Adds /japan to public/sitemap.xml (lastmod moves forward only when the page changed).
  3. Adds a banner to public/blog.html that shows while the Japan chip is selected (marker: id="jpHubBanner").

Run after w69 and before w72:  python3 tools/w73_japan_hub.py
Aborts without writing if an expected anchor or card is missing.
"""
import datetime, hashlib, os, re, sys

ROOT = os.getcwd()
PUB = os.path.join(ROOT, "public")
TE = os.path.join(PUB, "travel-essentials.html")
BLOG = os.path.join(PUB, "blog.html")
OUT = os.path.join(PUB, "japan.html")
SITEMAP = os.path.join(PUB, "sitemap.xml")
URL = "https://www.packsmartapp.com/japan"
TODAY = datetime.date.today().isoformat()

TITLE = "Japan Travel Guides: Airports, Stations, Pocket Guides &amp; Itineraries | PackSmart"
DESC = ("Every PackSmart guide for Japan in one place: trip planning, the Narita, Haneda, Kansai and New Chitose airports, "
        "Tokyo, Kyoto, Osaka and Sapporo stations, and free offline Pocket Guides.")

PLAN = ["japan-travel-packing-guide", "japan-7-day-itinerary-budget", "kyoto-travel-guide", "osaka-travel-guide"]
ARRIVE = ["narita-airport-guide", "haneda-airport-guide", "kansai-airport-guide", "new-chitose-airport-guide"]
STATIONS = ["tokyo-station-guide", "shinjuku-station-guide", "ueno-station-guide", "kyoto-station-guide",
            "osaka-station-guide", "sapporo-station-guide"]


def die(msg):
    sys.exit("w73 aborted, nothing written: " + msg)


def sub1(s, pattern, repl, what, flags=0):
    s2, n = re.subn(pattern, lambda m: repl, s, count=1, flags=flags)
    if n != 1:
        die("anchor not found: " + what)
    return s2


def card(src, slug, where):
    m = re.search(r'\n([ \t]*)<a href="/blog/%s" class="blog-card"[^>]*>.*?</a>' % re.escape(slug), src, re.S)
    if not m:
        die("card for %s not found on %s" % (slug, where))
    c = m.group(0).lstrip("\n")
    c = re.sub(r'(<a href="/blog/%s" class="blog-card")[^>]*>' % re.escape(slug), r"\1>", c, count=1)
    return "        " + c.strip()


te = open(TE, encoding="utf-8").read()
blog = open(BLOG, encoding="utf-8").read()

# ---- head: retitle the Travel Essentials head
head = te[:te.index("</head>")]
head = sub1(head, r"<title>.*?</title>", "<title>%s</title>" % TITLE, "title")
head = sub1(head, r'<meta name="description" content="[^"]*">', '<meta name="description" content="%s">' % DESC, "description")
head = sub1(head, r'<link rel="canonical" href="[^"]*">', '<link rel="canonical" href="%s">' % URL, "canonical")
for prop in ("og:title", "twitter:title"):
    attr = "property" if prop.startswith("og") else "name"
    head = sub1(head, r'<meta %s="%s" content="[^"]*">' % (attr, prop), '<meta %s="%s" content="%s">' % (attr, prop, TITLE), prop)
for prop in ("og:description", "twitter:description"):
    attr = "property" if prop.startswith("og") else "name"
    head = sub1(head, r'<meta %s="%s" content="[^"]*">' % (attr, prop), '<meta %s="%s" content="%s">' % (attr, prop, DESC), prop)
head = sub1(head, r'<meta property="og:url" content="[^"]*">', '<meta property="og:url" content="%s">' % URL, "og:url")
LD = ('{"@context": "https://schema.org", "@type": "CollectionPage", "name": "Japan travel guides", "url": "%s", '
      '"description": "%s", "publisher": {"@type": "Organization", "name": "PackSmart"}}' % (URL, DESC.replace('"', "'")))
head = re.sub(
    r'<script type="application/ld\+json">\s*\{"@context": "https://schema.org", "@type": "CollectionPage".*?</script>',
    lambda m: '<script type="application/ld+json">\n' + LD + '\n</script>', head, count=1, flags=re.S)
if LD not in head:
    die("JSON-LD not replaced")
HUB_CSS = """<style id="jp-hub-css">
.jp-links{background:#fff;border-radius:20px;padding:1.4rem 1.5rem;margin:0 0 1.6rem;box-shadow:0 2px 10px rgba(15,15,35,.05)}
.jp-links h2{font-size:1.35rem;margin:0 0 .3rem}
.jp-links p{margin:0 0 .8rem;color:#5a6378}
.jp-links ul{list-style:none;margin:0;padding:0;display:grid;gap:8px}
.jp-links li a{display:flex;align-items:center;gap:10px;min-height:44px;padding:8px 12px;border:1.5px solid #E3E8EC;border-radius:12px;color:#0f0f23;text-decoration:none;font-weight:600}
.jp-links li a:hover{border-color:#00C9A7}
.jp-links li small{display:block;font-weight:500;color:#5a6378}
.jp-two{display:grid;grid-template-columns:1fr 1fr;gap:1.2rem}
@media (max-width:760px){.jp-two{grid-template-columns:1fr}.jp-links{padding:1.1rem 1rem}}
</style>
"""
head = head + HUB_CSS

# ---- nav (as on Travel Essentials) and the Pocket Guide block
nav = te[te.index("</head>"):te.index('<div class="page-wrapper">')]
pm = re.search(r'<section class="pocket-hub" id="pocket-hub".*?</section>', te, re.S)
if not pm:
    die("Pocket Guide block not found on Travel Essentials")
pocket = pm.group(0).replace("?src=hub\"", "?src=hub_japan\"")
if "?src=hub_japan" not in pocket:
    die("Pocket Guide links not retagged")
foot = te[te.index('<footer class="footer">'):]

plan_cards = "\n".join(card(blog, s, "blog.html") for s in PLAN)
arrive_cards = "\n".join(card(te, s, "travel-essentials.html") for s in ARRIVE)
station_cards = "\n".join(card(te, s, "travel-essentials.html") for s in STATIONS)


def section(sid, title, lead, cards):
    return ('    <section class="te-section" id="%s">\n        <h2 class="te-h">%s</h2>\n        <p class="te-sub">%s</p>\n'
            '        <div class="blog-grid">\n%s\n        </div>\n    </section>\n') % (sid, title, lead, cards)


def links(title, lead, items):
    return ('<div class="jp-links"><h2>%s</h2><p>%s</p><ul>%s</ul></div>' % (
        title, lead, "".join('<li><a href="%s"><span aria-hidden="true">%s</span><span>%s<small>%s</small></span></a></li>' % i for i in items)))


HOKKAIDO = links("Hokkaido this winter", "Snow, ski buses and day trips from Sapporo.", [
    ("/blog/sapporo-station-guide#snow-festival", "&#10052;&#65039;", "Sapporo Snow Festival 2027", "4 to 11 February 2027: the sites and how to get there"),
    ("/blog/new-chitose-airport-guide#ski", "&#9975;&#65039;", "Ski buses from the airport", "Niseko ski bus times and how to book"),
    ("/blog/sapporo-station-guide#day-trips", "&#127956;&#65039;", "Day trips from Sapporo by train", "Otaru, Noboribetsu, Asahikawa, Biei and Furano"),
    ("/blog/sapporo-station-guide#hotels", "&#127976;", "Staying by Sapporo Station", "Hotels at or near the station"),
])
SEASONS = links("By season", "When you go changes what you pack and what you book.", [
    ("/blog/japan-travel-packing-guide#best-time", "&#128197;", "Best time to visit Japan", "Season by season"),
    ("/blog/ueno-station-guide#park", "&#127800;", "Cherry blossoms at Ueno Park", "One of Tokyo's best-known spots, next to the station"),
    ("/blog/japan-travel-packing-guide#packing-by-season", "&#129523;", "What to pack by season", "Winter layers to summer heat"),
    ("/blog/japan-travel-packing-guide#jr-pass", "&#128645;", "Is a JR Pass worth it?", "How to decide"),
])

body = """<div class="page-wrapper">
    <div class="page-header">
        <h1>Welcome to <em style="font-family:var(--font-display);font-style:italic;">Japan</em></h1>
        <p>Every PackSmart guide for Japan in one place. Plan the trip, then save the free Pocket Guides for the airports and stations you will use: they work offline. Station and airport facts come from official sources, with the date we checked them.</p>
    </div>
""" + "    " + pocket + """
    <div class="filter-wrap te-filter" id="teFilter">
        <div class="filter-label" id="teFilterLabel">What do you need?</div>
        <div class="filter-bar" role="group" aria-labelledby="teFilterLabel">
            <a href="#all" class="filter-btn active" data-sec="all" aria-pressed="true">All <i class="cnt"></i></a>
            <a href="#plan" class="filter-btn" data-sec="plan" aria-pressed="false">Plan your trip <i class="cnt"></i></a>
            <a href="#arriving" class="filter-btn" data-sec="arriving" aria-pressed="false">Airports <i class="cnt"></i></a>
            <a href="#stations" class="filter-btn" data-sec="stations" aria-pressed="false">Stations <i class="cnt"></i></a>
        </div>
    </div>
""" + section("plan", "Plan your trip", "Visas, seasons, budget, packing and a 7-day route.", plan_cards) \
    + section("arriving", "Airports", "Landing in Japan: terminals, trains and buses into town, money and SIM cards. Each guide has a free Pocket Guide.", arrive_cards) \
    + section("stations", "Stations", "The big stations, side by side: exits, platforms, lockers and ATMs. Each guide has a free Pocket Guide.", station_cards) \
    + """    <div class="jp-two">
        """ + HOKKAIDO + """
        """ + SEASONS + """
    </div>
    <!-- ask-japan-slot -->
    <p class="te-back">Travelling from India? See our <a href="/blog/japan-travel-packing-guide-from-india">Japan guide for travellers from India</a>, with visa and cost details. Need help that is not about Japan? See <a href="/travel-essentials">Travel Essentials</a>.</p>
</div>

"""
page = head + nav + body + foot
for need in ('id="plan"', 'id="arriving"', 'id="stations"', "hub_japan", "</html>"):
    if need not in page:
        die("built page lacks " + need)

old = open(OUT, encoding="utf-8").read() if os.path.isfile(OUT) else ""
changed = old != page

# ---- sitemap
sm = open(SITEMAP, encoding="utf-8").read()
loc = "<loc>%s</loc>" % URL
if loc not in sm:
    entry = "  <url>\n    %s\n    <lastmod>%s</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>0.8</priority>\n  </url>\n" % (loc, TODAY)
    if sm.count("</urlset>") != 1:
        die("sitemap end not found")
    sm = sm.replace("</urlset>", entry + "</urlset>")
elif changed:
    sm = re.sub(r"(%s\s*<lastmod>)([0-9-]+)(</lastmod>)" % re.escape(loc),
                lambda m: m.group(1) + max(m.group(2), TODAY) + m.group(3), sm, count=1)

# ---- blog banner (shows while the Japan chip is selected)
BANNER = ('<div class="jp-hub-banner" id="jpHubBanner" hidden><b>Welcome to Japan.</b> Airports, stations, itineraries and free offline Pocket Guides, all together. '
          '<a href="/japan">See every Japan guide &rarr;</a></div>\n'
          '<style>.jp-hub-banner{max-width:860px;margin:10px auto 6px;padding:12px 16px;background:#f0faf7;border-left:3px solid #00C9A7;border-radius:0 12px 12px 0;font-size:.98rem;line-height:1.5}'
          '.jp-hub-banner a{color:#0a8f78;font-weight:700;white-space:nowrap}</style>\n'
          "<script>(function(){var bar=document.getElementById('countryBar'),b=document.getElementById('jpHubBanner');if(!bar||!b)return;"
          "function sync(){var on=!bar.hidden&&!!bar.querySelector('.cty-btn.active[data-country=\"japan\"]');b.hidden=!on;}"
          "new MutationObserver(sync).observe(bar,{attributes:true,subtree:true,attributeFilter:['class','hidden']});sync();})();</script>\n")
if 'id="jpHubBanner"' not in blog:
    m = re.search(r'<div class="country-bar" id="countryBar".*?</div>\n', blog, re.S)
    if not m:
        die("country bar not found on blog.html")
    blog = blog[:m.end()] + BANNER + blog[m.end():]
    open(BLOG, "w", encoding="utf-8").write(blog)
    print("w73: banner added to blog.html")

if changed:
    open(OUT, "w", encoding="utf-8").write(page)
open(SITEMAP, "w", encoding="utf-8").write(sm)
print("w73 done. japan.html %s (%d plan, %d airport, %d station cards)." % (
    "written" if changed else "unchanged", len(PLAN), len(ARRIVE), len(STATIONS)))
