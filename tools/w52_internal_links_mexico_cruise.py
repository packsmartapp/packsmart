#!/usr/bin/env python3
"""
w52: internal links to two more guides Google crawled but did not index (GSC "Crawled - currently not indexed",
20 Nov 2026): mexico-travel-packing-guide (3 inbound pages, last crawled 12 Apr) and ship-cruise-travel-tips (1 inbound).

Only pages where the topic really comes up get a callout (same teal look as the existing callouts):
  visa-free-countries-indian-passport -> Mexico guide  (its "Third-Country Visa Access" section lists Mexico)
  travel-insurance-guide              -> Ship & Cruise Travel Tips (its Cruise Travel subsection)
  greece-travel-packing-guide         -> Ship & Cruise Travel Tips (ferry and island-hopping logistics)
  vietnam-10-day-itinerary-mid-range  -> Ship & Cruise Travel Tips (Ha Long Bay cruise days)
Result: Mexico +1 inbound page, Ship & Cruise +3.

The travel-insurance-guide callout carries no insurance advice: it only points to the cruise guide.
No partner links, no new claims: the text names what the target guide's own sections cover.

Run from the repo root:   python3 -I tools/w52_internal_links_mexico_cruise.py [--dry-run]
Idempotent (marker <!-- W52 INTERNAL LINKS -->). Writes nothing at all if any page or target is missing or an
insertion point does not occur exactly once.
"""
import os
import sys

BLOG = os.path.join(os.getcwd(), "public", "blog")
MARK = "<!-- W52 INTERNAL LINKS -->"

BOX = ('background:#f0faf7;border-left:3px solid #00C9A7;padding:12px 16px;border-radius:0 8px 8px 0;'
       'font-size:0.92rem;margin:20px 0;')
LNK = 'style="color:#00C9A7;text-decoration:underline;"'

TITLES = {
    "mexico-travel-packing-guide": "Mexico Travel &amp; Packing Guide",
    "ship-cruise-travel-tips": "Ship &amp; Cruise Travel Tips",
}


def a(slug):
    return '<a href="/blog/%s" %s>%s</a>' % (slug, LNK, TITLES[slug])


MX = "mexico-travel-packing-guide"
SC = "ship-cruise-travel-tips"

# page slug: (anchor, callout text, target slugs that must exist)
PLAN = {
    "visa-free-countries-indian-passport": (
        "<!-- SECTION 9: TIPS -->",
        "Heading to Mexico? Our %s covers entry requirements, costs and a packing checklist." % a(MX), [MX]),
    "travel-insurance-guide": (
        "<h3>Solo Travel</h3>",
        "First cruise or ferry trip? Our %s covers cabins, seasickness and what to pack." % a(SC), [SC]),
    "greece-travel-packing-guide": (
        '<h2 id="faq"',
        "Island hopping by ferry? Our %s covers ferry travel, seasickness and what to pack." % a(SC), [SC]),
    "vietnam-10-day-itinerary-mid-range": (
        '<div class="faq-section"',
        "Booking a Ha Long Bay cruise? Our %s covers cabins, seasickness and what to pack for boat trips." % a(SC), [SC]),
}


def callout(text):
    return '%s\n<p style="%s">%s</p>\n' % (MARK, BOX, text)


def main():
    dry = "--dry-run" in sys.argv
    todo, problems, skipped = [], [], []
    for slug, (anchor, text, targets) in PLAN.items():
        path = os.path.join(BLOG, slug + ".html")
        if not os.path.exists(path):
            problems.append("missing page: " + slug)
            continue
        for t in targets:
            if not os.path.exists(os.path.join(BLOG, t + ".html")):
                problems.append("missing link target %s (for %s)" % (t, slug))
        html = open(path, encoding="utf-8").read()
        if MARK in html:
            skipped.append(slug)
            continue
        n = html.count(anchor)
        if n != 1:
            problems.append("%s: anchor %r occurs %d times (need 1)" % (slug, anchor, n))
            continue
        todo.append((path, slug, html.replace(anchor, callout(text) + anchor, 1)))
    if problems:
        print("ABORT, nothing written:")
        for p in problems:
            print("  -", p)
        sys.exit(1)
    for path, slug, new in todo:
        if not dry:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new)
        print(("would add" if dry else "added"), "callout:", slug)
    for s in skipped:
        print("already done:", s)
    print("%d page(s) %s, %d already done." % (len(todo), "to change" if dry else "changed", len(skipped)))


if __name__ == "__main__":
    main()
