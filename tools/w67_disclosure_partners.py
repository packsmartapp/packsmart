#!/usr/bin/env python3
"""
w67: keep the Affiliate Disclosure page and the About page's partner pills in step with the partners we link to
(backlog B2; 23 Nov 2026).

An audit on 23 Nov found partners linked on the site but missing from /affiliate-disclosure: Sakura Mobile,
Japan Bullet Train, Trip.com, 12Go (book.packsmartapp.com is 12Go's booking page) and Saily; the About pills
also lacked EconomyBookings, Tiqets and Kiwitaxi.

What it does:
  1. Rewrites the partner list on public/affiliate-disclosure.html from PARTNERS below, and sets its
     "Last updated" line to the date this list last changed (LIST_DATE).
  2. Rewrites the "Trusted partners" pills on public/about.html from the same list (plus KEEP_PILLS).
  3. CHECK: every partner link domain found on any page under public/ must map to a partner in PARTNERS
     (DOMAIN_TO_PARTNER). A new partner domain with no entry fails the script, so the disclosure is updated
     before the new links go live.

Run from the repo root after adding a partner, and before pushing:  python3 tools/w67_disclosure_partners.py
Idempotent. Aborts without writing if a page's structure is not as expected.
"""
import glob, os, re, sys

ROOT = os.getcwd()
PUB = os.path.join(ROOT, "public")
LIST_DATE = "November 23, 2026"

# (name, what it is). Order: as readers meet them.
PARTNERS = [
    ("SafetyWing", "travel medical insurance"),
    ("GetYourGuide", "tours and activities"),
    ("Klook", "tours, tickets, transport and airport hotels in Asia"),
    ("Tiqets", "attraction tickets"),
    ("Airalo", "eSIM data plans"),
    ("GigSky", "eSIM data plans"),
    ("Yesim", "eSIM data plans"),
    ("Saily", "eSIM data plans"),
    ("Sakura Mobile", "Japan travel SIM cards and pocket Wi-Fi"),
    ("Welcome Pickups", "airport transfers"),
    ("Kiwitaxi", "private transfers"),
    ("DiscoverCars", "car rentals"),
    ("EconomyBookings", "car rentals"),
    ("Radical Storage", "luggage storage"),
    ("Japan Bullet Train", "Shinkansen tickets"),
    ("12Go", "trains, buses and ferries in Asia; our booking page book.packsmartapp.com is run by 12Go"),
    ("Trip.com", "hotels and flights"),
    ("Kiwi.com", "flights"),
    ("TourRadar", "guided multi-day tours"),
]
FOOT = "Plus flight and hotel price search powered by Travelpayouts"
KEEP_PILLS = []   # Tripadvisor pill removed 23 Nov 2026 (owner): nothing on the site links to Tripadvisor

DOMAIN_TO_PARTNER = {
    "safetywing.com": "SafetyWing", "getyourguide.com": "GetYourGuide", "klook.tpx.li": "Klook", "klook.tpo.lu": "Klook",
    "tiqets.tpx.li": "Tiqets", "airalo.tpx.li": "Airalo", "yesim.tpx.li": "Yesim", "saily.tpx.li": "Saily",
    "p.sakuramobile.jp": "Sakura Mobile", "radicalstorage.tpx.li": "Radical Storage", "economybookings.tpx.li": "EconomyBookings",
    "japan-bullettrain.com": "Japan Bullet Train", "trip.com": "Trip.com", "book.packsmartapp.com": "12Go",
    "airalo.tpo.lu": "Airalo", "gigsky.tpo.lu": "GigSky", "yesim.tpo.lu": "Yesim", "saily.tpo.lu": "Saily", "radicalstorage.tpo.lu": "Radical Storage", "tpo.lu": "Welcome Pickups",   # newer Travelpayouts short links (27 Nov: Packy's own, with Sub IDs)
    "tpx.li": "Welcome Pickups", "welcomepickups.com": "Welcome Pickups", "tourradar.com": "TourRadar",   # https://tpx.li/qYFLwgZ8 (Welcome Pickups); widgets load from tp.media/tpwdg.com (scripts, not links)
}
PARTNER_HOSTS = re.compile(r"tpx\.li|tpo\.lu|tp\.media|safetywing|getyourguide|klook|welcomepickups|discovercars|airalo|yesim|"
                           r"tiqets|gigsky|radicalstorage|sakuramobile|bullettrain|trip\.com|12go|book\.packsmartapp|economybookings|"
                           r"kiwitaxi|saily|aviasales|kiwi\.com|tripadvisor|tourradar")


def die(msg):
    sys.exit("w67 aborted, nothing written: " + msg)


# ---- check: every linked partner domain is disclosed
names = {n for n, _ in PARTNERS}
missing = set()
for f in glob.glob(os.path.join(PUB, "**", "*.html"), recursive=True):
    for href in re.findall(r'href="(https?://[^"]+)"', open(f, encoding="utf-8").read()):
        host = re.match(r"https?://([^/?#]+)", href).group(1).lower()
        if host == "tp.media":   # Travelpayouts redirect: the partner is in the u= parameter
            u = re.search(r"[?&]u=https?%3A%2F%2F([^%&]+)", href)
            host = u.group(1).lower() if u else host
        if host.startswith("widget.") or not PARTNER_HOSTS.search(host):
            continue
        key = host[4:] if host.startswith("www.") else host
        key = "safetywing.com" if key.endswith("safetywing.com") else key
        p = DOMAIN_TO_PARTNER.get(key)
        if not p or p not in names:
            missing.add("%s (%s)" % (host, os.path.relpath(f, ROOT)))
if missing:
    die("partner domains linked on the site but not mapped to a disclosed partner:\n  " + "\n  ".join(sorted(missing)))

# ---- disclosure page
dp = os.path.join(PUB, "affiliate-disclosure.html")
s = open(dp, encoding="utf-8").read()
m = re.search(r"(<h2>Our Affiliate Partners</h2>\s*<p>We currently partner with:</p>\s*)<ul>.*?</ul>", s, re.S)
if not m:
    die("disclosure: partner list not found")
items = "".join("\n        <li>%s (%s)</li>" % (n, w) for n, w in PARTNERS) + "\n        <li>%s</li>" % FOOT
new_ul = m.group(1) + "<ul>" + items + "\n    </ul>"
s2 = s[:m.start()] + new_ul + s[m.end():]
lu = re.search(r"<p>Last updated: [^<]*</p>", s2)
if not lu:
    die("disclosure: Last updated line not found")
if s2 != s:
    s2 = s2[:lu.start()] + "<p>Last updated: %s</p>" % LIST_DATE + s2[lu.end():]

# ---- about page pills
ap = os.path.join(PUB, "about.html")
a = open(ap, encoding="utf-8").read()
pm = re.search(r'(<h2>Trusted <em>partners</em></h2>.*?<div style="display: flex;[^"]*">)(.*?)(\n    </div>)', a, re.S)
if not pm:
    die("about: partner pills block not found")
tag = re.search(r'([ \t]*)(<span style="[^"]*">)[^<]*</span>', pm.group(2))
if not tag:
    die("about: pill markup not found")
indent, open_tag = tag.group(1), tag.group(2)
pills = [n for n, _ in PARTNERS] + KEEP_PILLS
a2 = a[:pm.start(2)] + "".join("\n%s%s%s</span>" % (indent, open_tag, n) for n in pills) + a[pm.end(2):]

changed = []
for path, old, new in ((dp, s, s2), (ap, a, a2)):
    if new != old:
        open(path, "w", encoding="utf-8").write(new)
        changed.append(os.path.basename(path))
print("w67 done. changed: %s. Every linked partner domain is disclosed." % (", ".join(changed) or "nothing"))
