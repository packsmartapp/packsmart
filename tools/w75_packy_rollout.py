#!/usr/bin/env python3
"""
w75: Packy, the pop-up travel helper, on the pages where its knowledge is solid (24 Nov 2026, D56).

One Packy, scoped by country: each page loads public/packy.js with its country and topic, e.g.
    <script src="/packy.js" data-country="japan" data-topic="sapporo" defer></script>
The topic picks Packy's example questions and the guide it points to (see packy.js and api/ask.js).

Stage 1 (this list): the Japan hub and the guides whose official-source knowledge is solid. Narita, Haneda and Kansai
follow once their research notes exist; Pocket Guides follow after real questions have been reviewed (they are
offline-first and Packy needs internet).

Run after w73 and before w72, and again after every edit to public/packy.js (the link's ?v= version comes from
the file, so browsers holding the 30-day cached copy fetch the new one):  python3 tools/w75_packy_rollout.py
Idempotent: removes any Packy line (the generators copy one from the Japan guide's footer), then adds the right one
to each listed page. Aborts without writing if a listed page or its </body> is missing.
"""
import os, sys

ROOT = os.getcwd()
PUB = os.path.join(ROOT, "public")
PAGES = {  # page: (country, topic, extra attributes)
    # no data-hide-when="#ask": hiding the button while the hub's Ask box was on screen looked like Packy vanishing (25 Nov)
    "japan.html": ("japan", "japan", ""),
    "blog/japan-travel-packing-guide.html": ("japan", "japan", ""),
    "blog/sapporo-station-guide.html": ("japan", "sapporo", ""),
    "blog/new-chitose-airport-guide.html": ("japan", "new-chitose", ""),
    "blog/ueno-station-guide.html": ("japan", "ueno", ""),
    "blog/shinjuku-station-guide.html": ("japan", "shinjuku", ""),
    "blog/tokyo-station-guide.html": ("japan", "tokyo", ""),
    "blog/kyoto-station-guide.html": ("japan", "kyoto", ""),
    "blog/osaka-station-guide.html": ("japan", "osaka", ""),
    # 25 Nov: the rest of the Japan pages (the owner found Packy missing on some): the three airports, the two city
    # guides (their own city's topic) and the two general articles (the Japan-wide topic)
    "blog/narita-airport-guide.html": ("japan", "narita", ""),
    "blog/haneda-airport-guide.html": ("japan", "haneda", ""),
    "blog/kansai-airport-guide.html": ("japan", "kansai", ""),
    "blog/kyoto-travel-guide.html": ("japan", "kyoto", ""),
    "blog/osaka-travel-guide.html": ("japan", "osaka", ""),
    "blog/japan-travel-packing-guide-from-india.html": ("japan", "japan", ""),
    "blog/japan-7-day-itinerary-budget.html": ("japan", "japan", ""),
    # 27 Nov: Fuku's Phrasebook (w81), for any Japan question next to the phrases (needs internet; the page works offline)
    "japan-phrasebook.html": ("japan", "japan", ""),
}

import glob, re
TAG_RX = re.compile(r'<script src="/packy\.js(?:\?v=[0-9a-f]+)?"[^>]*></script>\n?')
# The site caches .js files for 30 days as "immutable" (vercel.json), so the link carries a version made from
# packy.js itself: any change to Packy gets a new link and every browser fetches the new file at once.
import hashlib
VER = hashlib.md5(open(os.path.join(PUB, "packy.js"), "rb").read()).hexdigest()[:10]
# The page generators copy their footer from the Japan guide, so a Packy line can arrive on pages that are not on
# the list. Remove it everywhere first, then add the right one to each listed page.
plans, added = {}, 0
for path in sorted(glob.glob(os.path.join(PUB, "**", "*.html"), recursive=True)):
    rel = os.path.relpath(path, PUB).replace(os.sep, "/")
    s = open(path, encoding="utf-8").read()
    new = TAG_RX.sub("", s)
    if rel in PAGES:
        country, topic, extra = PAGES[rel]
        if new.count("</body>") != 1:
            sys.exit("w75 aborted, nothing written: </body> not found exactly once in " + rel)
        new = new.replace("</body>", '<script src="/packy.js?v=%s" data-country="%s" data-topic="%s"%s defer></script>\n</body>' % (VER, country, topic, extra), 1)
        added += 1
    if new != s:
        plans[path] = new
missing = [r for r in PAGES if not os.path.isfile(os.path.join(PUB, r))]
if missing:
    sys.exit("w75 aborted, nothing written: missing " + ", ".join(missing))

for path, s in plans.items():
    open(path, "w", encoding="utf-8").write(s)
print("w75 done. Packy on %d page(s); %d file(s) changed." % (added, len(plans)))
