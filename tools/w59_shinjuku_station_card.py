#!/usr/bin/env python3
"""w59: Travel Essentials hub: add the Shinjuku Station card to the Stations section (after the last station card).
Run from the repo root:  python3 tools/w59_shinjuku_station_card.py   (after w58 has built the article)
Idempotent. Needs public/images/shinjuku-station-card-680.webp (crop of the PAKUTASO photo of the Shinjuku Ogado bridge).
Only touches public/travel-essentials.html.
"""
import os, sys
PAGE = "public/travel-essentials.html"
IMG = "public/images/shinjuku-station-card-680.webp"
if not os.path.exists(IMG):
    sys.exit("missing " + IMG + " (copy it into public/images first)")
if not os.path.exists(PAGE):
    sys.exit("run this from the repo root (cannot find " + PAGE + ")")
s = open(PAGE, encoding="utf-8").read()
if 'href="/blog/shinjuku-station-guide" class="blog-card"' in s:
    print("nothing to do (already applied)")
    sys.exit(0)

CARD = '''        <a href="/blog/shinjuku-station-guide" class="blog-card">
            <img class="blog-card-img" src="/images/shinjuku-station-card-680.webp" alt="A green Yamanote Line train crossing the Shinjuku Ogado railway bridge" width="680" height="340" loading="lazy">
            <div class="blog-card-body pg-body">
                <span class="tag">Station Guide</span>
                <h2>Shinjuku Station Guide 2026: West vs East Exits, Platforms and Luggage</h2>
                <p>West or East side, which exit for where, the last Narita Express, airport buses from Busta Shinjuku, ATMs, lockers and luggage, and help in English.</p>
                <div class="pg-meta"><span class="meta">November 22, 2026 &middot; 8 min read</span><span class="read-more">Read more &rarr;</span></div>
                <span class="pg-strip"><b>Shinjuku Station Pocket Guide Inside</b><i>Works offline</i></span>
            </div>
        </a>
'''
a = s.index('id="stations"')
end = '        </a>\n        </div>\n    </section>'
j = s.find(end, a)
if j < 0:
    sys.exit("cannot find the end of the Stations section; page not changed")
j += len('        </a>\n')
s = s[:j] + CARD + s[j:]
open(PAGE, "w", encoding="utf-8").write(s)
print("changed:\n  - travel-essentials.html (Shinjuku Station card, Stations section)")
