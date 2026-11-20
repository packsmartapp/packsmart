#!/usr/bin/env python3
"""
w51: internal links to four guides Google crawled but did not index (GSC "Crawled - currently not indexed", 20 Nov 2026):
new-zealand, canada, south-korea (merged "-from-india" targets, 3-5 inbound links each) and road-trip-packing-checklist (1).

One short callout (same look as the existing teal callouts) on ten pages where the topic really comes up:
  best-summer-travel-destinations-india-2026 -> New Zealand + Canada      female-solo-travel-guide -> New Zealand
  winter-travel-packing-list                 -> Canada                    road-trip-packing-checklist -> New Zealand
  japan-travel-packing-guide, japan-7-day-itinerary-budget, china-travel-packing-guide -> South Korea
  new-zealand, usa, australia travel packing guides -> Road Trip Packing Checklist
Result: New Zealand 3 -> 6, Canada 4 -> 6, South Korea 5 -> 8, Road Trip 1 -> 4 pages that link to it.

Callout sits just before the FAQ block (on the road-trip page, which has no FAQ, just before its closing "Need help figuring out" line).
No partner links, no new claims: the text only names what the target guide's own title says it covers.

Run from the repo root:   python3 -I tools/w51_internal_links.py [--dry-run]
Idempotent (marker <!-- W51 INTERNAL LINKS -->). Writes nothing at all if any page or target is missing or an
insertion point does not occur exactly once.
"""
import os
import sys

BLOG = os.path.join(os.getcwd(), "public", "blog")
MARK = "<!-- W51 INTERNAL LINKS -->"
FAQ = '<div class="faq-section"'
JAPAN_FAQ = '<h2 id="faq">Frequently Asked Questions</h2>'
RT_ANCHOR = '<p>Need help figuring out exactly what to pack for your specific trip?'

BOX = ('background:#f0faf7;border-left:3px solid #00C9A7;padding:12px 16px;border-radius:0 8px 8px 0;'
       'font-size:0.92rem;margin:20px 0;')
LNK = 'style="color:#00C9A7;text-decoration:underline;"'

TITLES = {
    "new-zealand-travel-packing-guide": "New Zealand Travel &amp; Packing Guide",
    "canada-travel-packing-guide": "Canada Travel &amp; Packing Guide",
    "south-korea-travel-packing-guide": "South Korea Travel &amp; Packing Guide",
    "road-trip-packing-checklist": "Road Trip Packing Checklist",
}


def a(slug):
    return '<a href="/blog/%s" %s>%s</a>' % (slug, LNK, TITLES[slug])


NZ = "new-zealand-travel-packing-guide"
CA = "canada-travel-packing-guide"
SK = "south-korea-travel-packing-guide"
RT = "road-trip-packing-checklist"

SK_TEXT = "Adding South Korea to your trip? Our %s covers entry rules, costs and a packing checklist." % a(SK)
RT_TEXT = "Planning to drive? Our %s covers what to pack for long drives." % a(RT)

# page slug: (anchor, callout text, target slugs that must exist)
PLAN = {
    "best-summer-travel-destinations-india-2026": (
        FAQ, "Want the full planning detail? See our %s and %s for visas, costs and packing checklists." % (a(NZ), a(CA)), [NZ, CA]),
    "female-solo-travel-guide": (
        FAQ, "Thinking about New Zealand for a solo trip? Our %s covers the visa, costs and a packing checklist." % a(NZ), [NZ]),
    "winter-travel-packing-list": (
        FAQ, "Heading to Canada for the cold months? Our %s covers the visa, costs and a packing checklist." % a(CA), [CA]),
    "japan-travel-packing-guide": (JAPAN_FAQ, SK_TEXT, [SK]),
    "japan-7-day-itinerary-budget": (FAQ, SK_TEXT, [SK]),
    "china-travel-packing-guide": (FAQ, SK_TEXT, [SK]),
    "new-zealand-travel-packing-guide": (FAQ, RT_TEXT, [RT]),
    "usa-travel-packing-guide": (FAQ, RT_TEXT, [RT]),
    "australia-travel-packing-guide": (FAQ, RT_TEXT, [RT]),
    "road-trip-packing-checklist": (
        RT_ANCHOR, "Planning a road trip in New Zealand? Our %s covers the visa, costs and a packing checklist." % a(NZ), [NZ]),
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
