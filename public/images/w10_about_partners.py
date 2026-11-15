#!/usr/bin/env python3
"""w10: update the 'Trusted partners' pills on the About page.
Localrent pill -> DiscoverCars; add Airalo and Radical Storage pills after Welcome Pickups.
Run from repo root: python3 public/images/w10_about_partners.py   (optional arg: public dir)
Idempotent; aborts without writing if the page structure is not as expected.
"""
import os, re, sys
ROOT = sys.argv[1] if len(sys.argv) > 1 else "public"
cands = [os.path.join(ROOT, "about.html"), os.path.join(ROOT, "about", "index.html")]
p = next((c for c in cands if os.path.exists(c)), None)
if not p:
    print("ABORT: about page not found"); sys.exit(1)
s = open(p, encoding="utf-8").read()
if "<span" in s and ">Localrent</span>" not in s:
    print("about: already updated" if ">DiscoverCars</span>" in s else "about: Localrent pill not found (nothing to do)")
    sys.exit(0)
if s.count(">Localrent</span>") != 1:
    print("ABORT: Localrent pill count = %d" % s.count(">Localrent</span>")); sys.exit(1)
wp = re.search(r'([ \t]*)(<span\b[^>]*>)Welcome Pickups</span>', s)
if not wp or len(re.findall(r'>Welcome Pickups</span>', s)) != 1:
    print("ABORT: Welcome Pickups pill not found exactly once"); sys.exit(1)
indent, open_tag = wp.group(1), wp.group(2)
extra = "".join("\n%s%s%s</span>" % (indent, open_tag, n) for n in ("Airalo", "Radical Storage"))
s = s.replace(">Localrent</span>", ">DiscoverCars</span>")
s = s.replace(wp.group(0), wp.group(0) + extra, 1)
open(p, "w", encoding="utf-8").write(s)
print("about: updated (%s)" % p)
