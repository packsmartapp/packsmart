#!/usr/bin/env python3
"""w8: replace untracked generic Klook search links (aid=116473) with tracked
Travelpayouts klook.tpx.li "browse" links (Sub IDs klook-browse-<country>).

Usage: python3 w8_klook_browse.py [blog_dir]    (default: public/blog)
Idempotent: pages already swapped are left alone. A page whose tracked link is
not yet known (SRI_LANKA) is skipped and reported; run again once it is filled in.
Adds the 'klook.tpx.li': 'Klook' click-map label where the page lacks it.
"""
import re
import sys
import os

BLOG = sys.argv[1] if len(sys.argv) > 1 else "public/blog"

# page file -> tracked id (verified with curl 15 Nov: k_site = Klook search for the country/city, marker 711400)
SRI_LANKA = "5FGU4Pyh"  # klook-browse-sri-lanka (verified 15 Nov: k_site = search "Sri Lanka", marker 711400)
MAP = {
    "australia-travel-packing-guide-from-india.html": "zYuc61vt",      # Sydney
    "baku-azerbaijan-from-india.html": "EpvQekqu",                    # Baku
    "bali-travel-packing-guide-from-india.html": "deD2LEh0",          # Bali
    "bali-10-day-itinerary-mid-range.html": "deD2LEh0",               # Bali
    "canada-travel-packing-guide-from-india.html": "rqzk6cB8",        # Toronto
    "china-travel-packing-guide.html": "CfIPSEoP",                    # China
    "diwali-2026-international-trips-from-india.html": "FFtGAFj7",    # Bangkok
    "dubai-travel-packing-guide-from-india.html": "Ia5Lzvpc",         # Dubai
    "malaysia-travel-packing-guide-from-india.html": "7g3wF1iF",      # Kuala Lumpur
    "maldives-travel-packing-guide-from-india.html": "dp0C8ZU4",      # Maldives
    "nepal-travel-packing-guide-from-india.html": "2oONa9rJ",         # Nepal
    "new-zealand-travel-packing-guide-from-india.html": "APKeyiar",   # New Zealand
    "schengen-visa-guide-for-indians.html": "US4fjn1Z",               # Europe
    "south-korea-travel-packing-guide-from-india.html": "b0GFFpOX",   # Seoul
    "sri-lanka-travel-packing-guide-from-india.html": SRI_LANKA,      # Sri Lanka (pending)
    "usa-travel-packing-guide-from-india.html": "1bhz3sJw",           # New York
    "vietnam-travel-packing-guide-from-india.html": "5wbT3qkh",       # Vietnam
    "vietnam-10-day-itinerary-mid-range.html": "5wbT3qkh",            # Vietnam
}
EXPECTED = {  # generic anchors per page before the swap (from the 15 Nov scan)
    "australia-travel-packing-guide-from-india.html": 2,
    "baku-azerbaijan-from-india.html": 1,
    "bali-travel-packing-guide-from-india.html": 2,
    "bali-10-day-itinerary-mid-range.html": 1,
    "canada-travel-packing-guide-from-india.html": 1,
    "china-travel-packing-guide.html": 1,
    "diwali-2026-international-trips-from-india.html": 1,
    "dubai-travel-packing-guide-from-india.html": 1,
    "malaysia-travel-packing-guide-from-india.html": 3,
    "maldives-travel-packing-guide-from-india.html": 1,
    "nepal-travel-packing-guide-from-india.html": 1,
    "new-zealand-travel-packing-guide-from-india.html": 1,
    "schengen-visa-guide-for-indians.html": 1,
    "south-korea-travel-packing-guide-from-india.html": 3,
    "sri-lanka-travel-packing-guide-from-india.html": 2,
    "usa-travel-packing-guide-from-india.html": 1,
    "vietnam-travel-packing-guide-from-india.html": 1,
    "vietnam-10-day-itinerary-mid-range.html": 1,
}

ANCHOR = re.compile(
    r'<a\b[^>]*\bhref="https?://www\.klook\.com/en-US/search/result/\?query=[^"&]*&(?:amp;)?aid=116473"[^>]*>')
HREF = re.compile(r'href="[^"]*"')
REL = re.compile(r'rel="([^"]*)"')
LABEL = "'klook.tpx.li': 'Klook',"
TP_LINE = re.compile(r"^([ \t]*)'tpx\.li': 'Travelpayouts',[ \t]*$", re.M)


def fix_tag(tag, new_id):
    tag = HREF.sub('href="https://klook.tpx.li/%s"' % new_id, tag, count=1)
    m = REL.search(tag)
    if m:
        if "sponsored" not in m.group(1):
            tag = tag.replace(m.group(0), 'rel="nofollow noopener sponsored"', 1)
    else:
        tag = tag[:-1] + ' rel="nofollow noopener sponsored">'
    if 'target=' not in tag:
        tag = tag[:-1] + ' target="_blank">'
    return tag


def main():
    changed = skipped = 0
    problems = []
    plan = {}
    for fn, new_id in MAP.items():
        path = os.path.join(BLOG, fn)
        if not os.path.exists(path):
            problems.append("missing file " + fn)
            continue
        html = open(path, encoding="utf-8").read()
        tags = ANCHOR.findall(html)
        if not tags:
            print("skip (already swapped or none):", fn)
            skipped += 1
            continue
        if new_id is None:
            print("skip (tracked link not provided yet):", fn, "(%d generic anchors left)" % len(tags))
            skipped += 1
            continue
        if len(tags) != EXPECTED[fn]:
            problems.append("%s: expected %d generic anchors, found %d" % (fn, EXPECTED[fn], len(tags)))
            continue
        new = ANCHOR.sub(lambda m: fix_tag(m.group(0), new_id), html)
        if "aid=116473" in new and "klook.com/en-US/search" in new:
            left = [l for l in re.findall(r'klook\.com/en-US/search/result/\?query=[^"\s]*aid=116473', new)]
            if left:
                problems.append("%s: generic link left after swap: %s" % (fn, left[:2]))
                continue
        if LABEL not in new and "'klook.tpx.li'" not in new:
            ms = TP_LINE.findall(new)
            if len(ms) != 1:
                problems.append("%s: click-map anchor count %d (need exactly 1)" % (fn, len(ms)))
                continue
            new = TP_LINE.sub(lambda m: "%s%s\n%s'tpx.li': 'Travelpayouts'," % (m.group(1), LABEL, m.group(1)), new, count=1)
        plan[path] = (new, len(tags))
    if problems:
        print("ABORT, nothing written:")
        for p in problems:
            print("  -", p)
        sys.exit(1)
    for path, (new, n) in plan.items():
        open(path, "w", encoding="utf-8").write(new)
        print("swapped %d link(s): %s" % (n, os.path.basename(path)))
        changed += 1
    print("done: %d pages changed, %d skipped" % (changed, skipped))


main()
