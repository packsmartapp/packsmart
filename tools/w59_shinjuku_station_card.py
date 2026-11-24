#!/usr/bin/env python3
"""w59: Travel Essentials hub: add the airport- and station-guide cards that are not built by an earlier script, each
after the last card of its section: Shinjuku (22 Nov 2026) and Ueno (23 Nov 2026) in Stations; New Chitose Airport
(24 Nov 2026) in Airports and Sapporo (24 Nov 2026) in Stations.
Run from the repo root:  python3 tools/w59_shinjuku_station_card.py   (after w58, w68, w70 and w71 have built the articles)
Idempotent: a card whose link is already on the page is skipped.
Needs public/images/shinjuku-station-card-680.webp (crop of the PAKUTASO photo of the Shinjuku Ogado bridge) and
public/images/ueno-station-card-680.webp (crop of the PAKUTASO photo of JR Ueno Station's main building, the article hero),
public/images/new-chitose-airport-card-680.webp (a plain dark title card: no airport photo exists, see docs/research/sapporo-sources.md)
and public/images/sapporo-odori-card-680.webp (crop of the PAKUTASO photo of Odori Park, the Sapporo article hero).
The read time typed here is replaced by w69 with the real one.
Only touches public/travel-essentials.html.
To add a guide: add an entry to CARDS (slug, image, alt, title, blurb, date and read time, pocket guide name, and
optionally the section id and tag; the default is the Stations section with the "Station Guide" tag).
"""
import os, sys
PAGE = "public/travel-essentials.html"
CARDS = [
    ("shinjuku-station-guide", "shinjuku-station-card-680.webp",
     "A green Yamanote Line train crossing the Shinjuku Ogado railway bridge",
     "Shinjuku Station Guide 2026: West vs East Exits, Platforms and Luggage",
     "West or East side, which exit for where, the last Narita Express, airport buses from Busta Shinjuku, ATMs, lockers and luggage, and help in English.",
     "November 22, 2026 &middot; 9 min read", "Shinjuku Station"),
    ("ueno-station-guide", "ueno-station-card-680.webp",
     "The main building of JR Ueno Station, with its Ueno Station sign",
     "Ueno Station Guide 2026: Exits, Skyliner to Narita, Ueno Park and Cherry Blossoms",
     "Which gate for Ueno Park, JR platforms by floor, the Skyliner to Narita (not JR&rsquo;s Narita Line), the Tokyo Metro, lockers and the cherry blossoms.",
     "November 23, 2026 &middot; 10 min read", "Ueno Station"),
    ("new-chitose-airport-guide", "new-chitose-airport-card-680.webp",
     "PackSmart title card: New Chitose Airport (CTS), the airport for Sapporo",
     "New Chitose Airport (CTS) Guide 2026: Terminals, Trains and Buses to Sapporo, and Winter Tips",
     "Which terminal, the 2F corridor while the 3F passage is closed, the Airport Train and buses to Sapporo, ski buses, money, lockers and what to do when it snows.",
     "November 24, 2026 &middot; 10 min read", "New Chitose Airport", "airports", "Airport Guide"),
    ("sapporo-station-guide", "sapporo-odori-card-680.webp",
     "Odori Park in Sapporo seen from above in summer, with mountains behind",
     "Sapporo Station Guide 2026: Gates, Subway to Odori, Lockers, the Snow Festival and the Airport Train",
     "West and East gates while the station is rebuilt for the Shinkansen, the subway to Odori and Susukino, lockers, the Snow Festival 2027 dates and the train to the airport.",
     "November 24, 2026 &middot; 10 min read", "Sapporo Station"),
]
if not os.path.exists(PAGE):
    sys.exit("run this from the repo root (cannot find " + PAGE + ")")
for c in CARDS:
    if not os.path.exists(os.path.join("public", "images", c[1])):
        sys.exit("missing public/images/" + c[1] + " (copy it into public/images first)")
s = open(PAGE, encoding="utf-8").read()
added = []
for c in CARDS:
    slug, img, alt, title, blurb, meta, pocket = c[:7]
    sec, tag = (c[7], c[8]) if len(c) > 7 else ("stations", "Station Guide")
    if 'href="/blog/%s" class="blog-card"' % slug in s:
        continue
    card = ('''        <a href="/blog/%s" class="blog-card">
            <img class="blog-card-img" src="/images/%s" alt="%s" width="680" height="340" loading="lazy">
            <div class="blog-card-body pg-body">
                <span class="tag">%s</span>
                <h2>%s</h2>
                <p>%s</p>
                <div class="pg-meta"><span class="meta">%s</span><span class="read-more">Read more &rarr;</span></div>
                <span class="pg-strip"><b>%s Pocket Guide Inside</b><i>Works offline</i></span>
            </div>
        </a>
''') % (slug, img, alt, tag, title, blurb, meta, pocket)
    a = s.index('id="%s"' % sec)
    end = '        </a>\n        </div>\n    </section>'
    j = s.find(end, a)
    if j < 0:
        sys.exit("cannot find the end of the %s section; page not changed" % sec)
    j += len('        </a>\n')
    s = s[:j] + card + s[j:]
    added.append(pocket)
if not added:
    print("nothing to do (already applied)")
    sys.exit(0)
open(PAGE, "w", encoding="utf-8").write(s)
print("changed:\n  - travel-essentials.html (%s card)" % ", ".join(added))
