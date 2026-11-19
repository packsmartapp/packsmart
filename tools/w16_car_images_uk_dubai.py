#!/usr/bin/env python3
"""w16: add the road-trip image to the UK and Dubai DiscoverCars blocks (same layout as Germany/France/Italy/Japan/Spain).
Inserts, directly after the block's <h3>: the scoped .ps-trip-img style, a <picture> (webp 680/1360 + jpg fallback) and an
'Illustrative image' caption; the heading gets ': Go Where Trains and Buses Don't'.
Run from repo root:  python3 tools/w16_car_images_uk_dubai.py   (optional arg: blog dir)
Idempotent. Aborts without writing if the block structure is not as expected.
"""
import os, re, sys

BLOG = sys.argv[1] if len(sys.argv) > 1 else "public/blog"
IMG_DIR = os.path.join(os.getcwd(), "public", "images")  # run from the repo root

PAGES = [
    dict(
        file="uk-travel-packing-guide-from-india.html",
        placement="discovercars-uk",
        old_h3="Rent a Car for the Countryside",
        new_h3="Rent a Car for the Countryside: Go Where Trains and Buses Don't",
        img="car-trip-uk",
        w=1360, h=759,
        alt=("A family on a road trip in Britain: a picnic beside the car in the Scottish Highlands, a packed boot, "
             "a Cotswold village street and a car parked at a Highland viewpoint"),
    ),
    dict(
        file="dubai-travel-packing-guide-from-india.html",
        placement="discovercars-dubai",
        old_h3="Rent a Car in Dubai and the UAE",
        new_h3="Rent a Car in Dubai and the UAE: Go Where Trains and Buses Don't",
        img="car-trip-dubai",
        w=1360, h=759,
        alt=("A family on a road trip from Dubai to Hatta: a picnic beside the car in the Hajar Mountains, a packed boot, "
             "Hatta heritage village and a car parked above Hatta Dam"),
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
