#!/usr/bin/env python3
"""w9: (1) rename the click-tracker label 'tpwdg.com': 'Localrent' to 'Car_Rental_Widget'
on every HTML page under public/ (the tpwdg.com host serves DiscoverCars, EconomyBookings
and Kiwitaxi widgets now that Localrent is retired);
(2) update the partner list on public/affiliate-disclosure.html: Localrent out,
DiscoverCars, EconomyBookings, Airalo, Radical Storage, Kiwitaxi in.

Run from the repo root:  python3 tools/w9_click_label_disclosure.py
Idempotent. Part 2 aborts (without writing that file) if the list item is not found exactly once.
"""
import os
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "public"
OLD = "'tpwdg.com': 'Localrent'"
NEW = "'tpwdg.com': 'Car_Rental_Widget'"

# ---- part 1: click label -------------------------------------------------
files = changed = 0
for dp, dn, fn in os.walk(ROOT):
    dn[:] = [d for d in dn if d not in ("node_modules", ".git")]
    for f in fn:
        if not f.endswith(".html"):
            continue
        p = os.path.join(dp, f)
        files += 1
        s = open(p, encoding="utf-8").read()
        n = s.count(OLD)
        if n == 0:
            continue
        if n != 1:
            print("ABORT: %s has %d occurrences of the label (expected 1)" % (p, n))
            sys.exit(1)
        open(p, "w", encoding="utf-8").write(s.replace(OLD, NEW))
        changed += 1
print("label: %d of %d html files updated" % (changed, files))
left = 0
for dp, dn, fn in os.walk(ROOT):
    for f in fn:
        if f.endswith(".html") and OLD in open(os.path.join(dp, f), encoding="utf-8").read():
            left += 1
print("label left: %d" % left)

# ---- part 2: disclosure partner list ---------------------------------------
cands = [os.path.join(ROOT, "affiliate-disclosure.html"),
         os.path.join(ROOT, "affiliate-disclosure", "index.html")]
dp_path = next((c for c in cands if os.path.exists(c)), None)
if not dp_path:
    print("disclosure: file not found (skipped)")
    sys.exit(0)
s = open(dp_path, encoding="utf-8").read()
OLD_LI = "<li>Localrent (car rentals)</li>"
n = s.count(OLD_LI)
if n == 0:
    print("disclosure: already updated" if "DiscoverCars" in s else "disclosure: Localrent item not found (skipped)")
    sys.exit(0)
if n != 1:
    print("ABORT disclosure: Localrent item found %d times" % n)
    sys.exit(1)
items = [
    "DiscoverCars (car rentals)",
    "EconomyBookings (car rentals)",
    "Airalo (eSIM data plans)",
    "Radical Storage (luggage storage)",
    "Kiwitaxi (private transfers)",
]
open(dp_path, "w", encoding="utf-8").write(s.replace(OLD_LI, "".join("<li>%s</li>" % i for i in items)))
print("disclosure: partner list updated (%s)" % dp_path)
