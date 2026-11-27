#!/usr/bin/env python3
"""
w84: the departure tax and cherry blossoms 2027 on the three general Japan articles (27 Nov 2026, a tester).

Facts only from docs/research (official sources, checked 24 Nov 2026):
  - International Tourist Tax (departure tax): JNTO says visitors pay 3,000 yen (japan-prices-sources.md). The start
    date of the new rate could not be confirmed on an official page here, so no date is given.
  - Cherry blossoms: no 2027 forecast yet; the Japan Meteorological Agency's average first-bloom dates (also in JNTO's
    table) for Tokyo, Kyoto, Osaka and Sapporo (japan-basics-sources.md).
Japan travel guide: two cards in its "Japan in a minute" box. From-India guide: a box before "Japan Weather by Season".
7-day itinerary: a box before "Best Time to Visit Japan on a Budget".

Idempotent (marker "ps-jp2027"). Aborts without writing if an anchor is missing.
Run after the page generators and w77/w79, before w72:  python3 tools/w84_japan_2027_facts.py
"""
import os, sys

BLOG = os.path.join(os.getcwd(), "public", "blog")
MARK = "ps-jp2027"
TAX_URL = "https://www.japan.travel/en/plan/international-tourist-tax/"
SAKURA_URL = "https://www.japan.travel/en/see-and-do/cherry-blossom-forecast/"
JMA_URL = "https://www.data.jma.go.jp/sakura/data/sakura003_07.html"
A = ' target="_blank" rel="noopener"'

TAX = ("Japan charges an International Tourist Tax when you leave. Japan's tourism body (JNTO) says visitors pay "
       "3,000 yen. Check <a href=\"" + TAX_URL + "\"" + A + ">JNTO's page</a> for the current rules.")
SAKURA = ("The 2027 forecast isn't out yet. On average the first blossoms open around 24 March in Tokyo, 26 March in "
          "Kyoto, 27 March in Osaka and 1 May in Sapporo (<a href=\"" + JMA_URL + "\"" + A + ">Japan Meteorological "
          "Agency averages</a>). Watch <a href=\"" + SAKURA_URL + "\"" + A + ">JNTO's forecast page</a> in the new year.")

CARDS = ('<div class="jq-c ' + MARK + '"><b><span aria-hidden="true">🛫</span>Departure tax</b>' + TAX + '</div>'
         '<div class="jq-c ' + MARK + '"><b><span aria-hidden="true">🌸</span>Cherry blossoms 2027</b>' + SAKURA + '</div>')
BOX = ('<div class="' + MARK + '" style="background:#f0faf7;border-left:3px solid #00C9A7;border-radius:0 10px 10px 0;'
       'padding:14px 16px;margin:24px 0;font-size:0.93rem;line-height:1.55;">'
       '<p style="margin:0 0 8px;"><strong>🛫 Departure tax:</strong> ' + TAX + '</p>'
       '<p style="margin:0;"><strong>🌸 Cherry blossoms 2027:</strong> ' + SAKURA + '</p>'
       '<p style="margin:8px 0 0;font-size:0.8rem;color:#777;">Checked against official sources on 24 November 2026.</p></div>\n\n')

JOBS = [
    ("japan-travel-packing-guide.html", '</div></div><p class="jq-f">', CARDS + '</div></div><p class="jq-f">'),
    ("japan-travel-packing-guide-from-india.html", '<h2 id="weather">', BOX + '<h2 id="weather">'),
    ("japan-7-day-itinerary-budget.html", '<h2 id="best-time">', BOX + '<h2 id="best-time">'),
]
plans = {}
for name, anchor, new in JOBS:
    path = os.path.join(BLOG, name)
    s = open(path, encoding="utf-8").read()
    if MARK in s:
        continue
    if s.count(anchor) != 1:
        sys.exit("w84 aborted, nothing written: anchor found %d times in %s" % (s.count(anchor), name))
    plans[path] = s.replace(anchor, new, 1)
for path, s in plans.items():
    open(path, "w", encoding="utf-8").write(s)
print("w84 done. %d page(s) updated." % len(plans))
