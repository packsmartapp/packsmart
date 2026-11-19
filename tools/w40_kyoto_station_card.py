#!/usr/bin/env python3
"""w40: Travel Essentials hub: add the Kyoto Station card to the Stations section (after the Osaka station card).
Run from the repo root (~/packsmart):  python3 tools/w40_kyoto_station_card.py
Idempotent. Needs public/images/kyoto-station-card-680.webp (crop of the licensed Pakutaso photo). Only touches public/travel-essentials.html.
"""
import os, sys
PAGE = "public/travel-essentials.html"
IMG = "public/images/kyoto-station-card-680.webp"
if not os.path.exists(IMG):
    sys.exit("missing " + IMG + " (copy it into public/images first)")
if not os.path.exists(PAGE):
    sys.exit("run this from the repo root (cannot find " + PAGE + ")")
s = open(PAGE, encoding="utf-8").read()
if 'href="/blog/kyoto-station-guide" class="blog-card"' in s:
    print("nothing to do (already applied)")
    sys.exit(0)

CARD = '''        <a href="/blog/kyoto-station-guide" class="blog-card">
            <img class="blog-card-img" src="/images/kyoto-station-card-680.webp" alt="The glass walkway inside Kyoto Station" width="680" height="340" loading="lazy">
            <div class="blog-card-body pg-body">
                <span class="tag">Station Guide</span>
                <h2>Kyoto Station Guide 2026: Exits, Platforms, Buses and Luggage</h2>
                <p>Central or Hachijo side, bullet train and local platforms, city buses and the subway, lockers and luggage delivery, and help for older travellers.</p>
                <div class="pg-meta"><span class="meta">November 19, 2026 &middot; 8 min read</span><span class="read-more">Read more &rarr;</span></div>
                <span class="pg-strip"><b>Kyoto Station Pocket Guide Inside</b><i>Works offline</i></span>
            </div>
        </a>
'''
# the Stations section ends right after the last card: "        </a>\n        </div>\n    </section>"
a = s.index('id="stations"')
end = '        </a>\n        </div>\n    </section>'
j = s.find(end, a)
if j < 0:
    sys.exit("cannot find the end of the Stations section; page not changed")
j += len('        </a>\n')
s = s[:j] + CARD + s[j:]
open(PAGE, "w", encoding="utf-8").write(s)
print("changed:\n  - travel-essentials.html (Kyoto Station card, Stations section)")
