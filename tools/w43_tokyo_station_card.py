#!/usr/bin/env python3
"""w43: Travel Essentials hub: add the Tokyo Station card to the Stations section (after the Kyoto Station card).
Run from the repo root (~/packsmart):  python3 tools/w43_tokyo_station_card.py
Idempotent. Needs public/images/tokyo-station-card-680.webp (crop of the licensed Pakutaso photo). Only touches public/travel-essentials.html.
"""
import os, sys
PAGE = "public/travel-essentials.html"
IMG = "public/images/tokyo-station-card-680.webp"
if not os.path.exists(IMG):
    sys.exit("missing " + IMG + " (copy it into public/images first)")
if not os.path.exists(PAGE):
    sys.exit("run this from the repo root (cannot find " + PAGE + ")")
s = open(PAGE, encoding="utf-8").read()
if 'href="/blog/tokyo-station-guide" class="blog-card"' in s:
    print("nothing to do (already applied)")
    sys.exit(0)

CARD = '''        <a href="/blog/tokyo-station-guide" class="blog-card">
            <img class="blog-card-img" src="/images/tokyo-station-card-680.webp" alt="The Tokyo Station Marunouchi building at night" width="680" height="340" loading="lazy">
            <div class="blog-card-body pg-body">
                <span class="tag">Station Guide</span>
                <h2>Tokyo Station Guide 2026: Marunouchi vs Yaesu, Platforms and Luggage</h2>
                <p>Marunouchi or Yaesu side, Shinkansen and Narita Express platforms, local trains and Metro, lockers and luggage, and help for older travellers.</p>
                <div class="pg-meta"><span class="meta">November 19, 2026 &middot; 8 min read</span><span class="read-more">Read more &rarr;</span></div>
                <span class="pg-strip"><b>Tokyo Station Pocket Guide Inside</b><i>Works offline</i></span>
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
print("changed:\n  - travel-essentials.html (Tokyo Station card, Stations section)")
