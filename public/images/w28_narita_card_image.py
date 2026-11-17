#!/usr/bin/env python3
"""w28: Travel Essentials hub, Narita card: use a real Narita photo instead of the stand-in transfer image.
Run from the repo root (~/packsmart):  python3 public/images/w28_narita_card_image.py
Idempotent. Needs public/images/narita-airport-card-680.webp (a crop of the licensed Pakutaso hero photo).
"""
import os, sys
PAGE = "public/travel-essentials.html"
IMG = "public/images/narita-airport-card-680.webp"
OLD = '<img class="blog-card-img" src="/images/airport-transfer-arrival-680.webp" alt="Narita Airport guide" loading="lazy">'
NEW = '<img class="blog-card-img" src="/images/narita-airport-card-680.webp" alt="A busy check-in hall at Narita Airport with travellers and luggage" width="680" height="340" loading="lazy">'
if not os.path.exists(IMG):
    sys.exit("missing " + IMG + " (copy it into public/images first)")
if not os.path.exists(PAGE):
    sys.exit("run this from the repo root (cannot find " + PAGE + ")")
s = open(PAGE, encoding="utf-8").read()
if NEW in s:
    print("nothing to do (already applied)")
    sys.exit(0)
if s.count(OLD) != 1:
    sys.exit("expected exactly one Narita card image, found %d; page not changed" % s.count(OLD))
open(PAGE, "w", encoding="utf-8").write(s.replace(OLD, NEW))
print("changed:\n  - travel-essentials.html (Narita card image)")
