#!/usr/bin/env python3
"""
w60: GetYourGuide deep links (backlog B29, 23 Nov 2026).

Most GetYourGuide links on the articles went to the homepage
(https://www.getyourguide.com?partner_id=D7IXONS&cmp=share_to_earn), even next to a named activity.
This script points each one at a GetYourGuide search for what the link names, in the same format
the Baku guide already used (https://www.getyourguide.com/s/?q=...&partner_id=D7IXONS&cmp=...),
and gives every link its own cmp so clicks can be told apart in the GetYourGuide dashboard:
  cmp = "ps-<page slug>"            for the generic "Skip-the-line tours & activities" card
  cmp = "ps-<page slug>-<n>"        for in-text links (n = 1, 2, ... in page order)
Pages with no single destination (packing lists, tips, the homepage) keep the homepage link but
get their own cmp.

Run from the repo root:  python3 tools/w60_gyg_deep_links.py
Idempotent: only homepage links (getyourguide.com?partner_id=...) are rewritten; a second run
finds none. Aborts without writing if an in-text link has no mapping (a new link was added).
"""
import glob, html, os, re, sys
from urllib.parse import quote

ROOT = os.getcwd()
PUB = os.path.join(ROOT, "public")
PARTNER = "D7IXONS"

# page slug -> destination searched by the generic card (None = keep the homepage)
DEST = {
    "australia-travel-packing-guide": "Australia",
    "baku-azerbaijan-from-india": "Baku",
    "bali-10-day-itinerary-mid-range": "Bali",
    "bali-travel-packing-guide-from-india": "Bali",
    "canada-travel-packing-guide": "Canada",
    "china-travel-packing-guide": "China",
    "costa-rica-packing-list": "Costa Rica",
    "dubai-travel-packing-guide-from-india": "Dubai",
    "europe-travel-packing-list": "Europe",
    "greece-travel-packing-guide": "Greece",
    "italy-7-day-itinerary-mid-range": "Italy",
    "italy-travel-packing-guide": "Italy",
    "malaysia-travel-packing-guide-from-india": "Malaysia",
    "maldives-travel-packing-guide-from-india": "Maldives",
    "mexico-7-day-itinerary-mid-range": "Mexico",
    "mexico-travel-packing-guide": "Mexico",
    "nepal-travel-packing-guide-from-india": "Nepal",
    "new-zealand-travel-packing-guide": "New Zealand",
    "portugal-travel-packing-guide": "Portugal",
    "schengen-visa-guide-for-indians": "Europe",
    "singapore-travel-packing-guide-from-india": "Singapore",
    "south-korea-travel-packing-guide": "South Korea",
    "spain-10-day-itinerary-mid-range": "Spain",
    "spain-travel-packing-guide": "Spain",
    "sri-lanka-travel-packing-guide-from-india": "Sri Lanka",
    "switzerland-travel-packing-guide": "Switzerland",
    "thailand-7-day-itinerary-mid-range": "Thailand",
    "thailand-travel-packing-guide-from-india": "Thailand",
    "uk-travel-packing-guide": "United Kingdom",
    "usa-travel-packing-guide": "USA",
    "vietnam-10-day-itinerary-mid-range": "Vietnam",
    "vietnam-travel-packing-guide-from-india": "Vietnam",
}

# in-text links: (page slug, link text) -> search
INTEXT = {
    ("australia-travel-packing-guide", "GetYourGuide offers reef tours"): "Great Barrier Reef",
    ("bali-10-day-itinerary-mid-range", "Book Ubud waterfall and temple tours"): "Ubud waterfall temple",
    ("bali-10-day-itinerary-mid-range", "Book Uluwatu temple & Kecak dance tours"): "Uluwatu Kecak dance",
    ("bali-10-day-itinerary-mid-range", "Book Nusa Penida day tours and snorkeling trips"): "Nusa Penida",
    ("italy-7-day-itinerary-mid-range", "Book skip-the-line Colosseum & Vatican tours"): "Colosseum Vatican",
    ("italy-7-day-itinerary-mid-range", "Book Uffizi & Duomo skip-the-line tours"): "Uffizi Duomo Florence",
    ("italy-7-day-itinerary-mid-range", "Book Venice walking tours & Burano day trips"): "Venice Burano",
    ("mexico-7-day-itinerary-mid-range", "Book Teotihuacán tours with transport"): "Teotihuacan",
    ("mexico-7-day-itinerary-mid-range", "Book Oaxaca food tours & mezcal experiences"): "Oaxaca food mezcal",
    ("mexico-7-day-itinerary-mid-range", "Book Tulum cenote tours & Sian Ka’an trips"): "Tulum cenote Sian Ka'an",
    ("new-zealand-travel-packing-guide", "Book activities through GetYourGuide"): "New Zealand",
    ("new-zealand-travel-packing-guide", "GetYourGuide for best prices"): "Milford Sound",
    ("south-korea-travel-packing-guide", "GetYourGuide"): "DMZ Seoul",
    ("spain-10-day-itinerary-mid-range", "Book skip-the-line Sagrada Familia & Park Güell tours"): "Sagrada Familia Park Guell",
    ("spain-10-day-itinerary-mid-range", "Book Madrid walking tours & Toledo day trips"): "Madrid Toledo",
    ("spain-10-day-itinerary-mid-range", "Book Alhambra skip-the-line tours & flamenco shows"): "Alhambra flamenco",
    ("thailand-7-day-itinerary-mid-range", "Book skip-the-line Bangkok temple tours"): "Bangkok temples",
    ("thailand-7-day-itinerary-mid-range", "Book Chiang Mai elephant sanctuary visits"): "Chiang Mai elephant sanctuary",
    ("thailand-7-day-itinerary-mid-range", "Book 4 Islands and Phi Phi tours from Krabi"): "Krabi 4 Islands Phi Phi",
    ("usa-travel-packing-guide", "GetYourGuide offers Grand Canyon tours →"): "Grand Canyon",
    ("vietnam-10-day-itinerary-mid-range", "Book Hanoi street food tours & Old Quarter walks"): "Hanoi street food",
    ("vietnam-10-day-itinerary-mid-range", "Book Ha Long Bay overnight cruises"): "Ha Long Bay cruise",
    ("vietnam-10-day-itinerary-mid-range", "Book Cu Chi Tunnels & Mekong Delta tours"): "Cu Chi Tunnels Mekong Delta",
}

GENERIC_TEXT = "Skip-the-line tours & activities"
HOME_RX = re.compile(r'href="https://www\.getyourguide\.com\?partner_id=%s(?:&amp;|&)cmp=share_to_earn"' % PARTNER)
A_RX = re.compile(r'<a\b[^>]*href="https://www\.getyourguide\.com\?partner_id=%s(?:&amp;|&)cmp=share_to_earn"[^>]*>(.*?)</a>' % PARTNER, re.S)


def search_url(q, cmp, amp):
    sep = "&amp;" if amp else "&"
    return "https://www.getyourguide.com/s/?q=%s%spartner_id=%s%scmp=%s" % (quote(q), sep, PARTNER, sep, cmp)


def home_url(cmp, amp):
    sep = "&amp;" if amp else "&"
    return "https://www.getyourguide.com/?partner_id=%s%scmp=%s" % (PARTNER, sep, cmp)


files = sorted(glob.glob(os.path.join(PUB, "blog", "*.html"))) + [os.path.join(PUB, "index.html")]
plans, missing = {}, []
for path in files:
    s = open(path, encoding="utf-8").read()
    if not HOME_RX.search(s):
        continue
    slug = os.path.basename(path)[:-5]
    slug = "home" if slug == "index" else slug
    out, last, n = [], 0, 0
    for m in A_RX.finditer(s):
        text = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(1)))).strip()
        amp = "&amp;cmp=" in m.group(0)
        if GENERIC_TEXT in text or slug == "home" or (slug, text) not in INTEXT and slug not in DEST:
            # generic card, homepage, or a general page: destination search if the page has one
            cmp = "ps-" + slug
            new = search_url(DEST[slug], cmp, amp) if slug in DEST else home_url(cmp, amp)
        else:
            n += 1
            key = (slug, text)
            if key not in INTEXT:
                missing.append("%s: %r" % (slug, text))
                continue
            new = search_url(INTEXT[key], "ps-%s-%d" % (slug, n), amp)
        old_href = HOME_RX.search(m.group(0)).group(0)
        out.append(s[last:m.start()] + m.group(0).replace(old_href, 'href="%s"' % new, 1))
        last = m.end()
    out.append(s[last:])
    plans[path] = "".join(out)

if missing:
    sys.exit("w60 aborted, nothing written. In-text links with no mapping:\n  " + "\n  ".join(missing))
for path, new in plans.items():
    open(path, "w", encoding="utf-8").write(new)
left = sum(len(HOME_RX.findall(open(p, encoding="utf-8").read())) for p in files)
print("w60 done. changed %d file(s); homepage-style links left: %d" % (len(plans), left))
