#!/usr/bin/env python3
"""
w75: Packy, the pop-up travel helper, on the pages where its knowledge is solid (24 Nov 2026, D56).

One Packy, scoped by country: each page loads public/packy.js with its country and topic, e.g.
    <script src="/packy.js" data-country="japan" data-topic="sapporo" defer></script>
The topic picks Packy's example questions and the guide it points to (see packy.js and api/ask.js).

Stage 1 (this list): the Japan hub and the guides whose official-source knowledge is solid. Narita, Haneda and Kansai
follow once their research notes exist; Pocket Guides follow after real questions have been reviewed (they are
offline-first and Packy needs internet).

Run after w73 and before w72:  python3 tools/w75_packy_rollout.py
Idempotent: removes any Packy line (the generators copy one from the Japan guide's footer), then adds the right one
to each listed page. Aborts without writing if a listed page or its </body> is missing.
"""
import os, sys

ROOT = os.getcwd()
PUB = os.path.join(ROOT, "public")
PAGES = {  # page: (country, topic, extra attributes)
    "japan.html": ("japan", "japan", ' data-hide-when="#ask"'),
    "blog/japan-travel-packing-guide.html": ("japan", "japan", ""),
    "blog/sapporo-station-guide.html": ("japan", "sapporo", ""),
    "blog/new-chitose-airport-guide.html": ("japan", "new-chitose", ""),
    "blog/ueno-station-guide.html": ("japan", "ueno", ""),
    "blog/shinjuku-station-guide.html": ("japan", "shinjuku", ""),
    "blog/tokyo-station-guide.html": ("japan", "tokyo", ""),
    "blog/kyoto-station-guide.html": ("japan", "kyoto", ""),
    "blog/osaka-station-guide.html": ("japan", "osaka", ""),
}

import glob, re
TAG_RX = re.compile(r'<script src="/packy\.js"[^>]*></script>\n?')
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
        new = new.replace("</body>", '<script src="/packy.js" data-country="%s" data-topic="%s"%s defer></script>\n</body>' % (country, topic, extra), 1)
        added += 1
    if new != s:
        plans[path] = new
missing = [r for r in PAGES if not os.path.isfile(os.path.join(PUB, r))]
if missing:
    sys.exit("w75 aborted, nothing written: missing " + ", ".join(missing))

for path, s in plans.items():
    open(path, "w", encoding="utf-8").write(s)
print("w75 done. Packy on %d page(s); %d file(s) changed." % (added, len(plans)))
