#!/usr/bin/env python3
"""w12: USA guide: move the DiscoverCars block up so it no longer sits directly in front of the Klook block.
It now follows the 'Classic American highway landscape - perfect for a road trip adventure' figure
(end of section 6, just before '7. Complete Budget Guide').
Run from repo root:  python3 public/images/w12_usa_move_car_block.py   (optional arg: blog dir)
Idempotent. Aborts without writing if the page is not in the expected shape.
"""
import os, re, sys

BLOG = sys.argv[1] if len(sys.argv) > 1 else "public/blog"
path = os.path.join(BLOG, "usa-travel-packing-guide-from-india.html")
s = open(path, encoding="utf-8").read()

C_MARK = "<!-- DiscoverCars Car Rental Widget -->"
FIG_CAP = "Classic American highway landscape - perfect for a road trip adventure</figcaption>"
JS_MARK = "placement:'discovercars-usa'"

def abort(msg):
    print("ABORT: " + msg); sys.exit(1)

if s.count(C_MARK) != 1: abort("car block comment count != 1")
if s.count(FIG_CAP) != 1: abort("highway figure caption count != 1")
if s.count('<div data-ps-placement="discovercars-usa"') != 1: abort("car block div count != 1")

c = s.index(C_MARK)
cap = s.index(FIG_CAP)
sec7 = s.find("<!-- Section 7: Budget Guide -->")
if sec7 < 0: abort("Section 7 marker not found")
if cap < c < sec7:
    print("SKIP: car block is already right after the highway figure"); sys.exit(0)
if c < cap: abort("car block is above the highway figure in an unexpected spot")

# block extent: from the comment to the </div> that closes the block (right after its inline script)
js = s.index(JS_MARK, c)
tail = "</script>\n</div>"
e = s.index(tail, js)
if e - c > 12000: abort("block unexpectedly long")
end = e + len(tail)
block = s[c:end]
if block.count('<div data-ps-placement="discovercars-usa"') != 1: abort("extracted block malformed")
if block.count("<div") != block.count("</div>"): abort("div imbalance in extracted block")

# remove from its old place (with its 8-space indent and the blank line after it)
start = c
while start > 0 and s[start - 1] in " \t": start -= 1
rest = s[end:]
rm_end = end + (len(rest) - len(rest.lstrip("\n")))  # swallow blank lines after the block
s2 = s[:start] + s[rm_end:]

# insert after the figure that holds the caption
fig_close = s2.index("</figure>", s2.index(FIG_CAP))
ins = fig_close + len("</figure>")
s3 = s2[:ins] + "\n\n" + block + s2[ins:]

# sanity: block exactly once, above the Section 7 heading, and no widget directly in front of the Klook block
if s3.count(C_MARK) != 1: abort("block duplicated")
if s3.index(C_MARK) > s3.index("<!-- Section 7: Budget Guide -->"): abort("block not above Section 7")
kk = s3.index('data-ps-placement="klook-deals-usa-guide"')
if "discovercars-usa" in s3[kk - 400:kk]: abort("car block still next to Klook")

open(path, "w", encoding="utf-8").write(s3)
print("OK usa: car block moved after the highway figure (%d -> %d bytes)" % (len(s), len(s3)))
