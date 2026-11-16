#!/usr/bin/env python3
"""w19: add the road-trip image to the South Korea guide, Mexico guide and Mexico 7-day itinerary DiscoverCars blocks (same layout as Germany/France/Italy/Japan/Spain).
Inserts, directly after the block's <h3>: the scoped .ps-trip-img style, a <picture> (webp 680/1360 + jpg fallback) and an
'Illustrative image' caption; the heading gets ': Go Where Trains and Buses Don't'.
Run from repo root:  python3 public/images/w19_car_images_south_korea_mexico.py   (optional arg: blog dir)
Idempotent. Aborts without writing if the block structure is not as expected.
"""
import os, re, sys

BLOG = sys.argv[1] if len(sys.argv) > 1 else "public/blog"
IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))  # public/images

PAGES = [
    dict(
        file="south-korea-travel-packing-guide-from-india.html",
        placement="discovercars-south-korea",
        old_h3="Rent a Car in South Korea",
        new_h3="Rent a Car in South Korea: Go Where Trains and Buses Don't",
        img="car-trip-south-korea",
        w=1360, h=759,
        alt=("A family on a road trip in South Korea: a picnic beside the car on the Jeju coast, a packed boot, a traditional hanok street in Jeonju and a car parked at a Jeju coastal overlook"),
    ),
    dict(
        file="mexico-travel-packing-guide.html",
        placement="discovercars-mexico",
        old_h3="Rent a Car in Mexico",
        new_h3="Rent a Car in Mexico: Go Where Trains and Buses Don't",
        img="car-trip-mexico",
        w=1360, h=759,
        alt=("A family on a road trip in Mexico's Yucatan: a picnic beside the car in the jungle, a packed boot, the pastel colonial streets of Valladolid and a car parked at a cenote overlook"),
    ),
    dict(
        file="mexico-7-day-itinerary-mid-range.html",
        placement="discovercars-mexico-itinerary",
        old_h3="Rent a Car in Mexico",
        new_h3="Rent a Car in Mexico: Go Where Trains and Buses Don't",
        img="car-trip-mexico",
        w=1360, h=759,
        alt=("A family on a road trip in Mexico's Yucatan: a picnic beside the car in the jungle, a packed boot, the pastel colonial streets of Valladolid and a car parked at a cenote overlook"),
    ),
]

def block(p):
    sel = '[data-ps-placement="%s"]' % p["placement"]
    return (
        '    <style>.ps-trip-img { display: block; width: 100%%; height: auto; border-radius: 10px; } '
        '@media (max-width: 600px) { %s .ps-trip-img { margin: 0 -28px; width: calc(100%% + 56px); max-width: none; border-radius: 0; } }</style>\n'
        '    <picture>\n'
        '        <source type="image/webp" srcset="/images/%s-680.webp 680w, /images/%s.webp 1360w" sizes="(max-width: 800px) 95vw, 676px">\n'
        '        <img class="ps-trip-img" src="/images/%s.jpg" width="%d" height="%d" loading="lazy" decoding="async" alt="%s">\n'
        '    </picture>\n'
        '    <p style="margin: 6px 0 18px 0; color: #999; font-size: 0.75rem; text-align: right;">Illustrative image</p>\n'
    ) % (sel, p["img"], p["img"], p["img"], p["w"], p["h"], p["alt"])

bad = 0
for p in PAGES:
    path = os.path.join(BLOG, p["file"])
    if not os.path.exists(path):
        print("ABORT: %s not found" % path); sys.exit(1)
    s = open(path, encoding="utf-8").read()
    if p["img"] in s:
        print("SKIP %s: already has %s" % (p["file"], p["img"])); continue
    if s.count('<div data-ps-placement="%s"' % p["placement"]) != 1:
        print("ABORT %s: block count != 1" % p["file"]); sys.exit(1)
    pat = re.compile(
        r'(<div data-ps-placement="%s"[^>]*>\s*)(<h3[^>]*>)%s(</h3>)\n' % (re.escape(p["placement"]), re.escape(p["old_h3"]))
    )
    m = pat.search(s)
    if not m:
        print("ABORT %s: block heading not as expected" % p["file"]); sys.exit(1)
    new = s[:m.start()] + m.group(1) + m.group(2) + p["new_h3"] + m.group(3) + "\n" + block(p) + s[m.end():]
    open(path, "w", encoding="utf-8").write(new)
    print("OK %s: image added (%d -> %d bytes)" % (p["file"], len(s), len(new)))

for p in PAGES:
    for suf in (".jpg", ".webp", "-680.webp"):
        f = os.path.join(IMG_DIR, p["img"] + suf)
        print(("   file ok: " if os.path.exists(f) else "   MISSING FILE: ") + os.path.basename(f))
