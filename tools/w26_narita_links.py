#!/usr/bin/env python3
"""
w26: more internal links to /blog/narita-airport-guide from the Japan articles.

Run from the repo root:  python3 tools/w26_narita_links.py
(Run w25 first if it has not been run yet.)  Idempotent; aborts without writing if an anchor is missing.

  - japan-travel-packing-guide.html        : Visit Japan Web bullet + new "Related Guides" card
  - japan-travel-packing-guide-from-india  : pocket Wi-Fi bullet + new "Related Guides" card
  - japan-7-day-itinerary-budget.html      : arrival paragraph sentence + new "Related Guides" card
  - sitemap.xml                            : lastmod bumped for the three pages
"""
import os, re, sys

ROOT = os.getcwd()
BLOG = os.path.join(ROOT, "public", "blog")
SITEMAP = os.path.join(ROOT, "public", "sitemap.xml")
SITE = "https://www.packsmartapp.com"
TODAY = "2026-11-16"
HREF = "/blog/narita-airport-guide"
FULL = SITE + HREF

CARD = """        <div class="related-card">
            <div class="related-card-body">
                <h4>Narita Airport Guide 2026</h4>
                <p>Terminals, arrival steps, SIM and eSIM options, trains and buses to Tokyo, and airport facilities, in plain English.</p>
                <a href="%s">Read More <span class="related-arrow">&rarr;</span></a>
                <div class="related-tag">Airport Guide</div>
            </div>
        </div>
""" % FULL

def die(m):
    print("ABORT: " + m); sys.exit(1)

def rd(p):
    return open(p, encoding="utf-8").read()

# (file, [(anchor_regex_or_literal, replacement)], card?)
EDITS = {
    "japan-travel-packing-guide.html": [
        ("Receive QR codes for scanning at airport (speeds up airport processing).</li>",
         "Receive QR codes for scanning at airport (speeds up airport processing). The arrival steps are in our <a href=\"%s\">Narita Airport guide</a>.</li>" % HREF),
    ],
    "japan-travel-packing-guide-from-india.html": [
        ("Pocket WiFi rental: &#xA5;1,000-1,500/day from Narita/Kansai airport rental counters</li>",
         "Pocket WiFi rental: &#xA5;1,000-1,500/day from Narita/Kansai airport rental counters (counter locations at Narita are in our <a href=\"%s\">Narita Airport guide</a>)</li>" % HREF),
    ],
    "japan-7-day-itinerary-budget.html": [
        ("(the Shinkansen and some regional lines need a separate ticket).</p>",
         "(the Shinkansen and some regional lines need a separate ticket). For terminals, SIM options and the last trains, see our <a href=\"%s\">Narita Airport guide</a>.</p>" % HREF),
    ],
}

pending = {}
for fn, edits in EDITS.items():
    path = os.path.join(BLOG, fn)
    if not os.path.isfile(path):
        die("missing page: " + path)
    s = rd(path)
    orig = s
    # inline link
    for old, new in edits:
        if ("href=\"%s\"" % HREF) in new and new in s:
            continue
        if s.count(old) != 1:
            die("%s: inline anchor found %d times: %r" % (fn, s.count(old), old[:60]))
        s = s.replace(old, new, 1)
    # related card (first card in the Related Guides grid)
    grid = '<div class="related-grid">\n'
    if ('href="%s"' % FULL) not in s:
        if s.count(grid) != 1:
            die("%s: related-grid anchor found %d times" % (fn, s.count(grid)))
        s = s.replace(grid, grid + CARD, 1)
    if s != orig:
        pending[path] = s

sm = rd(SITEMAP)
sm0 = sm
for slug in ("japan-travel-packing-guide", "japan-travel-packing-guide-from-india", "japan-7-day-itinerary-budget"):
    rx = re.compile(r"(<loc>%s/blog/%s</loc>\s*<lastmod>)[^<]*(</lastmod>)" % (re.escape(SITE), re.escape(slug)))
    if not rx.search(sm):
        die("sitemap entry missing: " + slug)
    if any(slug + ".html" in os.path.basename(p) for p in pending):
        sm = rx.sub(lambda _m: _m.group(0) if re.search(r"<lastmod>([^<]*)", _m.group(0)).group(1) >= TODAY else _m.group(1) + TODAY + _m.group(2), sm, count=1)  # only move the date forward

for path, s in pending.items():
    open(path, "w", encoding="utf-8").write(s)
if sm != sm0:
    open(SITEMAP, "w", encoding="utf-8").write(sm)

if pending:
    print("changed:")
    for p in pending:
        print("  - " + os.path.relpath(p, ROOT))
    if sm != sm0:
        print("  - public/sitemap.xml")
else:
    print("nothing to do (already applied)")
