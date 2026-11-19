#!/usr/bin/env python3
"""w37: Travel Essentials hub: add the Kansai Airport (KIX) card to Airports and a new Stations section with the Osaka station card.
Run from the repo root (~/packsmart):  python3 public/images/w37_travel_essentials_cards.py
Idempotent. Needs public/images/kansai-airport-card-680.webp and public/images/osaka-station-card-680.webp
(crops of the licensed Pakutaso photos). Only touches public/travel-essentials.html.
"""
import os, sys
PAGE = "public/travel-essentials.html"
for img in ("public/images/kansai-airport-card-680.webp", "public/images/osaka-station-card-680.webp"):
    if not os.path.exists(img):
        sys.exit("missing " + img + " (copy it into public/images first)")
if not os.path.exists(PAGE):
    sys.exit("run this from the repo root (cannot find " + PAGE + ")")
s = open(PAGE, encoding="utf-8").read()

KIX_CARD = '''        <a href="/blog/kansai-airport-guide" class="blog-card">
            <img class="blog-card-img" src="/images/kansai-airport-card-680.webp" alt="Aeroplanes parked at their gates beside the sea at Kansai Airport" width="680" height="340" loading="lazy">
            <div class="blog-card-body pg-body">
                <span class="tag">Airport Guide</span>
                <h2>Kansai Airport (KIX) Guide 2026: Arrival, SIM and Trains to Osaka and Kyoto</h2>
                <p>Which terminal, what to do after landing, SIM and eSIM options, Haruka, Nankai and the bus to Osaka and Kyoto, luggage delivery, and prayer rooms, showers and help.</p>
                <div class="pg-meta"><span class="meta">November 18, 2026 &middot; 8 min read</span><span class="read-more">Read more &rarr;</span></div>
                <span class="pg-strip"><b>Kansai Airport Pocket Guide Inside</b><i>Works offline</i></span>
            </div>
        </a>
'''
STATIONS = '''    <section class="te-section" id="stations">
        <h2 class="te-h">Stations</h2>
        <p class="te-sub">Plain-English guides to big train stations, step by step.</p>
        <div class="blog-grid">
        <a href="/blog/osaka-station-guide" class="blog-card">
            <img class="blog-card-img" src="/images/osaka-station-card-680.webp" alt="The golden four-sided clock at JR Osaka Station" width="680" height="340" loading="lazy">
            <div class="blog-card-body pg-body">
                <span class="tag">Station Guide</span>
                <h2>Osaka Station Guide 2026: Shin-Osaka, Umeda, Platforms and Luggage</h2>
                <p>Shin-Osaka for bullet trains or Osaka/Umeda for downtown, how to get between them, platforms, lockers and luggage delivery, ICOCA, and help for older travellers.</p>
                <div class="pg-meta"><span class="meta">November 19, 2026 &middot; 8 min read</span><span class="read-more">Read more &rarr;</span></div>
                <span class="pg-strip"><b>Osaka Station Pocket Guide Inside</b><i>Works offline</i></span>
            </div>
        </a>
        </div>
    </section>
'''
BTN_AFTER = '<a href="#airports" class="filter-btn" data-sec="airports" aria-pressed="false">Airports <i class="cnt"></i></a>\n'
BTN = '            <a href="#stations" class="filter-btn" data-sec="stations" aria-pressed="false">Stations <i class="cnt"></i></a>\n'
END_AIRPORTS = '        </div>\n    </section>\n    <section class="te-section" id="before-you-fly">'

changed = []
if 'href="/blog/kansai-airport-guide" class="blog-card"' not in s:
    if s.count(END_AIRPORTS) != 1:
        sys.exit("cannot find the end of the Airports section; page not changed")
    s = s.replace(END_AIRPORTS, KIX_CARD + END_AIRPORTS)
    changed.append("Kansai Airport card (Airports)")
if 'id="stations"' not in s:
    if s.count(END_AIRPORTS) != 1 and "</section>\n    <section class=\"te-section\" id=\"before-you-fly\">" not in s:
        sys.exit("cannot place the Stations section; page not changed")
    marker = '    <section class="te-section" id="before-you-fly">'
    if s.count(marker) != 1:
        sys.exit("cannot find the Before you fly section; page not changed")
    s = s.replace(marker, STATIONS + marker)
    if s.count(BTN_AFTER) != 1:
        sys.exit("cannot find the Airports filter button; page not changed")
    i = s.index(BTN_AFTER) + len(BTN_AFTER)
    s = s[:i] + BTN + s[i:]
    changed.append("Stations section, card and filter button")
if not changed:
    print("nothing to do (already applied)")
    sys.exit(0)
open(PAGE, "w", encoding="utf-8").write(s)
print("changed:\n  - travel-essentials.html (" + "; ".join(changed) + ")")
