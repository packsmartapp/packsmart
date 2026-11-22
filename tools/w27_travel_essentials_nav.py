#!/usr/bin/env python3
"""
w27: new top menu + Travel Essentials hub page.

Run from the repo root (after w25 and w26):  python3 tools/w27_travel_essentials_nav.py

  1. Top menu on every page: Destinations | Travel Essentials | Flights & Hotels | Plan My Trip
     (How It Works and Features are removed from the menu; they stay on the homepage).
     Footer: "Blog" becomes "Destinations" plus a "Travel Essentials" link.
  2. New page public/travel-essentials.html (URL /travel-essentials): 21 non-destination
     articles moved off the blog index, plus the Narita Airport guide, in four groups.
  3. public/blog.html becomes the Destinations index: non-destination cards removed,
     heading, title, meta and filters updated. The URL stays /blog.
  4. public/sitemap.xml gets /travel-essentials.
Idempotent. Aborts without writing anything if an expected anchor is missing.
"""
import os, re, sys, html, json

ROOT = os.getcwd()
PUB = os.path.join(ROOT, "public")
SITE = "https://www.packsmartapp.com"
TODAY = "2026-11-16"
LABEL = "Travel Essentials"
SLUG = "travel-essentials"


def die(m):
    print("ABORT: " + m)
    sys.exit(1)


def rd(p):
    return open(p, encoding="utf-8").read()


# ------------------------------------------------------------------ groups
GROUPS = [
    ("airports", "Airports",
     "Plain-English guides to getting through big airports, step by step.",
     ["narita-airport-guide"]),
    ("before-you-fly", "Before you fly",
     "Visas, insurance, staying connected and the checklists to run before you leave.",
     ["international-travel-checklist", "first-time-flying", "schengen-visa-guide-for-indians",
      "visa-free-countries-indian-passport", "travel-insurance-guide",
      "best-esim-international-travel-comparison", "travel-toiletries-checklist"]),
    ("your-way", "Travelling your way",
     "Tips for solo travellers, families, train journeys and cruises.",
     ["female-solo-travel-guide", "solo-travel-tips-beginners", "family-travel-tips-with-kids",
      "ship-cruise-travel-tips", "train-travel-tips-beginners"]),
    ("packing", "Packing lists",
     "Ready-made lists for any trip, whatever the destination.",
     ["winter-travel-packing-list", "summer-vacation-packing-list", "weekend-trip-packing-list",
      "carry-on-packing-list", "minimalist-packing-guide", "beach-vacation-packing-list",
      "honeymoon-packing-list", "road-trip-packing-checklist", "family-summer-vacation-packing-list"]),
]
MOVE = [s for g in GROUPS for s in g[3] if s != "narita-airport-guide"]
assert len(MOVE) == 21 and len(set(MOVE)) == 21

NARITA_CARD = """        <a href="/blog/narita-airport-guide" class="blog-card">
            <img class="blog-card-img" src="/images/airport-transfer-arrival-680.webp" alt="Narita Airport guide" loading="lazy">
            <div class="blog-card-body">
                <span class="tag">Airport Guide</span>
                <h2>Narita Airport Guide 2026: Terminals, Arrival Steps, SIM and Getting to Tokyo</h2>
                <p>Which terminal, what to do after landing, SIM and eSIM options, trains and buses to Tokyo, and where to find prayer rooms, baby rooms and quiet rooms.</p>
                <span class="meta">November 16, 2026 &middot; 8 min read</span>
                <br><span class="read-more">Read more &rarr;</span>
            </div>
        </a>"""

CARD_RX = re.compile(r'[ \t]*<a href="/blog/([^"]+)" class="blog-card"[^>]*>.*?</a>[ \t]*\n?', re.S)

# ------------------------------------------------------------------ blog.html (read first, write later)
BLOG = os.path.join(PUB, "blog.html")
blog = rd(BLOG)
blog_orig = blog

already_split = os.path.isfile(os.path.join(PUB, SLUG + ".html")) and "Destination Guides" in blog

cards_all = {m.group(1): m.group(0) for m in CARD_RX.finditer(blog)}
if not already_split:
    missing = [s for s in MOVE if s not in cards_all]
    if missing:
        die("cards not found in blog.html: %r" % missing)
    moved_cards = {s: cards_all[s].rstrip("\n").rstrip() for s in MOVE}
else:
    moved_cards = None

# ------------------------------------------------------------------ travel-essentials.html
ESS = os.path.join(PUB, SLUG + ".html")


def build_essentials(moved):
    s = blog_orig
    i_head_end = s.find("</head>")
    if i_head_end < 0 or '<div class="page-wrapper">' not in s:
        die("head/page-wrapper not found in blog.html")
    head = s[:i_head_end]
    # nav (new version), footer and script tail from the (already menu-updated) source later; here build raw
    i_foot = s.find('<footer class="footer">')
    if i_foot < 0:
        die("footer not found in blog.html")
    tail = s[i_foot:]

    title = "Travel Essentials | PackSmart: Airport Guides, Visas, eSIM, Insurance & Packing Lists"
    desc = ("Plain-English travel help that is not about one destination: airport guides, visas, "
            "eSIM and insurance, solo and family travel, and packing lists for any trip.")
    url = "%s/%s" % (SITE, SLUG)

    def sub(rx, rep, text, flags=0):
        new, n = re.subn(rx, rep, text, count=1, flags=flags)
        if n != 1:
            die("head pattern not found: " + rx)
        return new

    head = sub(r"<title>.*?</title>", "<title>%s</title>" % html.escape(title, quote=False), head, re.S)
    head = sub(r'(<meta name="description" content=")[^"]*(")', r"\g<1>%s\g<2>" % html.escape(desc), head)
    head = sub(r'(<link rel="canonical" href=")[^"]*(")', r"\g<1>%s\g<2>" % url, head)
    head = sub(r'(<meta property="og:title" content=")[^"]*(")', r"\g<1>%s\g<2>" % html.escape(title), head)
    head = sub(r'(<meta property="og:description" content=")[^"]*(")', r"\g<1>%s\g<2>" % html.escape(desc), head)
    head = sub(r'(<meta property="og:url" content=")[^"]*(")', r"\g<1>%s\g<2>" % url, head)
    head = sub(r'(<meta name="twitter:title" content=")[^"]*(")', r"\g<1>%s\g<2>" % html.escape(title), head)
    head = sub(r'(<meta name="twitter:description" content=")[^"]*(")', r"\g<1>%s\g<2>" % html.escape(desc), head)

    # drop the Blog JSON-LD from the copy, add a CollectionPage one
    head = re.sub(r'<script type="application/ld\+json">.*?</script>\s*', "", head, flags=re.S)
    ld = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "Travel Essentials",
        "url": url,
        "description": desc,
        "isPartOf": {"@type": "WebSite", "name": "PackSmart", "url": SITE},
    }
    extra_css = """
        .te-section { margin: 0 0 3rem; }
        .te-section h2.te-h { font-family: var(--font-display); font-size: 2rem; margin-bottom: 0.3rem; }
        .te-section p.te-sub { color: var(--text-secondary); font-size: 1.05rem; margin-bottom: 1.2rem; }
        .te-jump { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; margin: 0 0 2.5rem; }
        .te-jump a { padding: 10px 18px; border-radius: 24px; border: 1.5px solid var(--border); background: var(--bg-white); color: var(--text); font-size: 0.95rem; font-weight: 600; text-decoration: none; }
        .te-jump a:hover { background: var(--action); color: #fff; border-color: var(--action); }
        .te-back { text-align: center; margin-top: 1rem; color: var(--text-secondary); }
        .te-back a { color: var(--action); font-weight: 600; }
"""
    head = head.replace("</style>", extra_css + "    </style>\n<script type=\"application/ld+json\">\n%s\n</script>" % json.dumps(ld, ensure_ascii=False), 1)

    # body
    parts = []
    parts.append('<div class="page-wrapper">')
    parts.append('    <div class="page-header">')
    parts.append('        <h1>Travel <em style="font-family:var(--font-display);font-style:italic;">Essentials</em></h1>')
    parts.append("        <p>Plain-English help for the parts of a trip that are not about one destination.</p>")
    parts.append("    </div>")
    parts.append('    <div class="te-jump">')
    for gid, gname, _, _ in GROUPS:
        parts.append('        <a href="#%s">%s</a>' % (gid, html.escape(gname)))
    parts.append("    </div>")
    for gid, gname, gsub, slugs in GROUPS:
        parts.append('    <section class="te-section" id="%s">' % gid)
        parts.append('        <h2 class="te-h">%s</h2>' % html.escape(gname))
        parts.append('        <p class="te-sub">%s</p>' % html.escape(gsub))
        parts.append('        <div class="blog-grid">')
        for sl in slugs:
            parts.append(NARITA_CARD if sl == "narita-airport-guide" else moved[sl])
        parts.append("        </div>")
        parts.append("    </section>")
    parts.append('    <p class="te-back">Planning a trip to a specific country? See <a href="/blog">Destinations</a>.</p>')
    parts.append("</div>\n")
    body = "\n".join(parts)

    # tail: footer + nav script; remove search/filter script block (last <script> before </body>)
    tail = re.sub(r"<script>\s*\(function\(\) \{\s*const searchInput.*?\}\)\(\);\s*</script>\s*", "", tail, flags=re.S)
    if "searchInput" in tail:
        die("search script not removed from essentials tail")

    nb = re.search(r'<nav class="nav" id="nav">.*?</nav>', s, re.S)
    if not nb:
        die("nav block not found in blog.html")
    nav_block = nb.group(0)
    return head + "</head>\n<body>\n\n" + nav_block + "\n\n" + body + "\n" + tail


# ------------------------------------------------------------------ blog.html -> Destinations index
def convert_blog(text):
    t = text
    # remove moved cards
    if not already_split:
        n_before = len(CARD_RX.findall(t))
        for sl in MOVE:
            t, n = re.subn(r'[ \t]*<a href="/blog/%s" class="blog-card"[^>]*>.*?</a>[ \t]*\n?' % re.escape(sl), "", t, count=1, flags=re.S)
            if n != 1:
                die("could not remove card: " + sl)
        if len(CARD_RX.findall(t)) != n_before - 21:
            die("card count after removal is wrong")

    def rep(old, new, cnt=1):
        nonlocal t
        if new in t and old not in t:
            return
        if t.count(old) < 1:
            die("blog.html anchor not found: " + old[:70])
        t = t.replace(old, new, cnt)

    rep("<title>Blog | PackSmart — Travel Tips, Packing Guides & More</title>",
        "<title>Destinations | PackSmart: Country Guides, Itineraries & Packing Lists</title>")
    old_d = "Travel tips, packing guides, destination prep, and smart travel advice from PackSmart. Everything you need to know before your next trip."
    new_d = "Country guides, itineraries and destination packing lists from PackSmart. Everything you need to know before you fly."
    t = t.replace(old_d, new_d)
    rep("PackSmart Blog — Travel Tips, Packing Guides & More", "PackSmart Destinations: Country Guides, Itineraries & Packing Lists", 2)
    rep('<h1>The PackSmart <em style="font-family:var(--font-display);font-style:italic;">Blog</em></h1>',
        '<h1>Destination <em style="font-family:var(--font-display);font-style:italic;">Guides</em></h1>')
    rep("<p>Travel tips, packing guides, and destination prep to help you travel smarter.</p>",
        '<p>Country guides, itineraries and what to pack, one destination at a time.</p>\n        <p style="font-size:0.95rem;margin-top:0.6rem;">Looking for airport guides, visas, insurance or packing lists? See <a href="/travel-essentials" style="color:var(--action);font-weight:600;">Travel Essentials</a>.</p>')
    rep('placeholder="Search guides... e.g. Japan, packing, visa"', 'placeholder="Search destinations... e.g. Japan, Thailand, itinerary"')
    rep('"name": "PackSmart Travel Blog"', '"name": "PackSmart Destination Guides"')

    # filters: keep only buttons that still match cards
    remaining_tags = re.findall(r'<span class="tag">([^<]*)</span>', t)
    has_summer = 'data-summer="true"' in t
    new_buttons = ['<button class="filter-btn active" data-filter="all">All Destinations</button>']
    if "Destination Guide" in remaining_tags:
        new_buttons.append('<button class="filter-btn" data-filter="Destination Guide">Country Guides</button>')
    if "Itinerary Guide" in remaining_tags:
        new_buttons.append('<button class="filter-btn" data-filter="Itinerary Guide">Itineraries</button>')
    if has_summer:
        new_buttons.append('<button class="filter-btn" data-filter="summer">Summer</button>')
    if any(x not in ("Destination Guide", "Packing Guide", "Travel Guide", "Itinerary Guide") for x in remaining_tags):
        new_buttons.append('<button class="filter-btn" data-filter="other">More</button>')
    fb = re.search(r'(<div class="filter-bar" id="filterBar">)(.*?)(</div>)', t, re.S)
    if not fb:
        die("filter bar not found")
    t = t[:fb.start(2)] + "\n        " + "\n        ".join(new_buttons) + "\n    " + t[fb.end(2):]
    return t


# ------------------------------------------------------------------ nav / footer on all pages
NAV_RX = re.compile(r'(<div class="nav-links" id="navLinks">)(.*?)(\n[ \t]*</div>)', re.S)


def new_nav_inner(old_inner):
    rel = 'href="flights.html"' in old_inner
    amp = "&amp;" in old_inner
    indent = re.match(r"\n([ \t]*)<a", old_inner)
    ind = indent.group(1) if indent else "        "
    fh = "flights.html" if rel else "/flights"
    bh = "blog.html" if rel else "/blog"
    eh = "travel-essentials.html" if rel else "/travel-essentials"
    ph = "#plan" if rel else "/#plan"
    fl = "Flights &amp; Hotels" if amp else "Flights & Hotels"
    return ("\n%s<a href=\"%s\">Destinations</a>\n%s<a href=\"%s\">%s</a>\n%s<a href=\"%s\">%s</a>\n%s<a href=\"%s\" class=\"nav-cta-btn\">Plan My Trip</a>"
            % (ind, bh, ind, eh, LABEL, ind, fh, fl, ind, ph))


FOOT_RX = re.compile(r'<a href="(/blog|blog\.html)">Blog</a>')


def convert_chrome(text):
    t = text
    m = NAV_RX.search(t)
    nav_changed = False
    if m and "Features" in m.group(2) and "Essentials" not in m.group(2):
        t = t[:m.start(2)] + new_nav_inner(m.group(2)) + t[m.end(2):]
        nav_changed = True

    def foot(m2):
        rel = m2.group(1) == "blog.html"
        return '<a href="%s">Destinations</a><a href="%s">%s</a>' % (m2.group(1), "travel-essentials.html" if rel else "/travel-essentials", LABEL)

    t2 = FOOT_RX.sub(foot, t)
    return t2, nav_changed, (t2 != t)


# ------------------------------------------------------------------ run
files = []
for dp, dn, fn in os.walk(PUB):
    for f in fn:
        if f.endswith(".html"):
            files.append(os.path.join(dp, f))
files.sort()

writes = {}
stats = {"nav": 0, "foot": 0}
leftover_nav = []

# essentials page text (built from the ORIGINAL blog.html, then chrome-converted below)
if os.path.isfile(ESS):
    ess_text = rd(ESS)
else:
    ess_text = build_essentials(moved_cards)

blog_new = convert_blog(blog_orig)

for path in files:
    if os.path.abspath(path) == os.path.abspath(BLOG):
        text = blog_new
    elif os.path.abspath(path) == os.path.abspath(ESS):
        continue
    else:
        text = rd(path)
    new, nav_ch, foot_ch = convert_chrome(text)
    if nav_ch:
        stats["nav"] += 1
    if foot_ch:
        stats["foot"] += 1
    mm = NAV_RX.search(new)
    if mm and "travel-essentials" not in mm.group(2):
        leftover_nav.append(os.path.relpath(path, ROOT))
    if new != rd(path):
        writes[path] = new

# essentials page chrome
ess_new, _, _ = convert_chrome(ess_text)
if (not os.path.isfile(ESS)) or ess_new != rd(ESS):
    writes[ESS] = ess_new

# sitemap
SM = os.path.join(PUB, "sitemap.xml")
sm = rd(SM)
sm0 = sm
if ("/%s</loc>" % SLUG) not in sm:
    entry = ("  <url>\n    <loc>%s/%s</loc>\n    <lastmod>%s</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>0.8</priority>\n  </url>\n") % (SITE, SLUG, TODAY)
    if "</urlset>" not in sm:
        die("sitemap has no </urlset>")
    sm = sm.replace("</urlset>", entry + "</urlset>", 1)
rx = re.compile(r"(<loc>%s/blog</loc>\s*<lastmod>)[^<]*(</lastmod>)" % re.escape(SITE))
if rx.search(sm):
    sm = rx.sub(lambda _m: _m.group(0) if re.search(r"<lastmod>([^<]*)", _m.group(0)).group(1) >= TODAY else _m.group(1) + TODAY + _m.group(2), sm, count=1)  # only move the date forward
if sm != sm0:
    writes[SM] = sm

if leftover_nav:
    print("NOTE: pages with a nav that was not converted:", leftover_nav)

for p, s in writes.items():
    open(p, "w", encoding="utf-8").write(s)

if writes:
    print("changed %d files (menu updated on %d pages, footer on %d)" % (len(writes), stats["nav"], stats["foot"]))
    for p in writes:
        if not p.endswith(".html") or os.path.dirname(p) == PUB:
            print("  - " + os.path.relpath(p, ROOT))
else:
    print("nothing to do (already applied)")
